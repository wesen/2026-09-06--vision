"""Single subprocess worker, queue-inclusive deadlines, count and byte admission.

The trusted host supplies commands; API input never becomes an executable. All
terminal outcomes are returned to the host for durable logging, including drops.
"""
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
import json
import math
import os
import signal
import subprocess
import time


@dataclass
class Job:
    id: str
    kind: str
    payload: dict
    command: tuple[str, ...]
    event_us: int
    cycle: int = 0
    mandatory: bool = True
    budget_seconds: float = 10.0
    case_id: str | None = None
    input_bytes: int = 0
    enqueued: float = 0.0
    deadline: float = 0.0
    started: float | None = None
    directory: Path | None = None


class Scheduler:
    def __init__(self, directory, *, max_jobs=16, max_bytes=16*1024*1024, max_output_bytes=1024*1024, monotonic=time.monotonic):
        if any(type(v) is not int or v < 1 for v in (max_jobs,max_bytes,max_output_bytes)):
            raise ValueError('positive integer scheduler bounds required')
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.max_jobs, self.max_bytes, self.max_output_bytes = max_jobs, max_bytes, max_output_bytes
        self.monotonic = monotonic
        self.queue = []
        self.running = None
        self.process = None
        self.completed = []
        self.seen = set()
        self.counts = Counter()
        self.high_jobs = self.high_bytes = 0
        self.closed = False

    @property
    def jobs(self):
        return self.queue + ([self.running] if self.running else [])

    @property
    def has_work(self):
        return bool(self.queue or self.running or self.completed)

    def snapshot(self):
        return dict(queued=len(self.queue), running=self.running.id if self.running else None,
                    admitted_jobs=len(self.jobs), admitted_bytes=sum(j.input_bytes for j in self.jobs),
                    max_jobs=self.max_jobs, max_bytes=self.max_bytes,
                    high_jobs=self.high_jobs, high_bytes=self.high_bytes, counts=dict(self.counts))

    def _terminal(self, job, status, reason=None, result=None):
        now = self.monotonic()
        self.counts[status] += 1
        self.completed.append(dict(job=job, status=status, reason=reason, result=result,
                                   queue_seconds=(job.started if job.started is not None else now)-job.enqueued,
                                   service_seconds=now-job.started if job.started is not None else 0.,
                                   total_seconds=now-job.enqueued))

    def _fits(self, job):
        return len(self.jobs) < self.max_jobs and sum(j.input_bytes for j in self.jobs)+job.input_bytes <= self.max_bytes

    def submit(self, job):
        if self.closed:
            raise ValueError('scheduler closed')
        if not job.id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in job.id):
            raise ValueError('invalid job identity')
        if job.id in self.seen:
            raise ValueError('duplicate job identity')
        if not math.isfinite(job.budget_seconds) or not 0 < job.budget_seconds <= 120:
            raise ValueError('invalid wall deadline budget')
        if not job.command or type(job.event_us) is not int or job.event_us < 0:
            raise ValueError('invalid job command or source time')
        encoded = json.dumps(job.payload, allow_nan=False).encode()
        if len(encoded) > self.max_bytes:
            job.input_bytes = max(job.input_bytes, len(encoded))
        elif job.input_bytes < len(encoded):
            job.input_bytes = len(encoded)
        if type(job.input_bytes) is not int or job.input_bytes < 1:
            raise ValueError('positive job input bytes required')
        job.payload = json.loads(encoded)
        self.seen.add(job.id)
        job.enqueued = self.monotonic()
        job.deadline = job.enqueued + job.budget_seconds
        self.counts['submitted'] += 1
        if job.mandatory and job.input_bytes <= self.max_bytes:
            for optional in list(reversed(self.queue)):
                if self._fits(job):
                    break
                if not optional.mandatory:
                    self.queue.remove(optional)
                    self._terminal(optional, 'dropped', 'evicted_for_mandatory')
        if not self._fits(job):
            self._terminal(job, 'dropped', 'admission_bound')
            return False
        job.directory = self.directory / job.id
        job.directory.mkdir(exist_ok=False)
        (job.directory/'input.json').write_bytes(encoded)
        self.queue.append(job)
        self.high_jobs = max(self.high_jobs, len(self.jobs))
        self.high_bytes = max(self.high_bytes, sum(j.input_bytes for j in self.jobs))
        return True

    def _kill(self):
        if self.process is not None:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            self.process.wait()

    def poll(self):
        now = self.monotonic()
        if self.running:
            job = self.running
            code = self.process.poll()
            if now >= job.deadline:
                self._kill()
                self._terminal(job, 'timeout', 'wall_deadline')
                self.running = self.process = None
            elif code is not None:
                try:
                    if code != 0:
                        raise ValueError(f'worker exit {code}')
                    output = job.directory/'result.json'
                    if output.stat().st_size > self.max_output_bytes:
                        raise ValueError('worker output exceeds bound')
                    result = json.loads(output.read_text())
                    if not isinstance(result, dict):
                        raise ValueError('worker output must be an object')
                    self._terminal(job, 'completed', result=result)
                except (OSError, ValueError) as exc:
                    self._terminal(job, 'failed', str(exc))
                self.running = self.process = None
        for job in list(self.queue):
            if now >= job.deadline:
                self.queue.remove(job)
                self._terminal(job, 'expired', 'queue_deadline')
        if not self.running and self.queue:
            index = next((i for i,j in enumerate(self.queue) if j.mandatory), 0)
            job = self.queue.pop(index)
            job.started = self.monotonic()
            env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2]),
                       HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
            try:
                self.process = subprocess.Popen([*job.command, str(job.directory/'input.json'), str(job.directory/'result.json')],
                                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                                env=env, start_new_session=True)
                self.running = job
                self.counts['started'] += 1
            except OSError as exc:
                self._terminal(job, 'failed', str(exc))
        results, self.completed = self.completed, []
        return results

    def cancel(self):
        self.closed = True
        if self.running:
            self._kill()
            self._terminal(self.running, 'cancelled', 'run_cancelled')
            self.running = self.process = None
        for job in self.queue:
            self._terminal(job, 'cancelled', 'run_cancelled')
        self.queue = []
        results, self.completed = self.completed, []
        return results
