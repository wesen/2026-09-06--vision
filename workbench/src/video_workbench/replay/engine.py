"""Connect released measured perception, sampled memory, rules, and bounded work."""
from dataclasses import asdict, dataclass
from pathlib import Path
from collections import Counter
import json
import math
import sqlite3
import sys
import time
import uuid
import psutil
from video_workbench.registry import file_hash
from video_workbench.rules.departure import DepartureDetector
from video_workbench.rules.evaluate import Event, digest, evaluate
from video_workbench.rules.handoff import plan_request, evaluate_answer
from video_workbench.temporal.store import Observation
from video_workbench.verifiers.profiles import make_profile, profile_hash
from video_workbench.verifiers.recovery import parse_with_recovery
from video_workbench.verifiers.adapter import check_packet
from .clock import ReplayClock
from .broker import EvidenceBroker
from .scheduler import Scheduler, Job
from .store import ReplayStore

DEFAULT_RECORDINGS = 'ttmp/2026/09/06/VIDEO-RULES-001--project-4-temporal-rules-and-bounded-investigation/various/r4-review/recordings.json'
MODELS = {'qwen':'output/models/qwen3-vl-instruct-8b-8bit','cosmos':'output/models/cosmos-reason2-8b-8bit-local'}


def write_json(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    temp.replace(path)


@dataclass(frozen=True)
class Options:
    episode_id: str
    mode: str = 'recorded'
    family: str = 'qwen'
    speed: float = 1.0
    repetitions: int = 1
    max_jobs: int = 16
    max_bytes: int = 16*1024*1024
    perception_deadline_seconds: float = 2.0
    verifier_deadline_seconds: float = 120.0
    service_multiplier: float = 1.0

    def validate(self):
        if self.mode not in ('recorded','live_verifier') or self.family not in MODELS:
            raise ValueError('unsupported execution mode/model family')
        for key, upper in [('repetitions',100),('max_jobs',128),('max_bytes',64*1024*1024)]:
            value = getattr(self,key)
            if type(value) is not int or not 1 <= value <= upper:
                raise ValueError('invalid bound '+key)
        for key, upper in [('speed',100),('perception_deadline_seconds',120),('verifier_deadline_seconds',120),('service_multiplier',100)]:
            value = getattr(self,key)
            if type(value) not in (int,float) or not math.isfinite(value) or not 0 < value <= upper:
                raise ValueError('invalid positive option '+key)
        return self


class Catalog:
    """Operator-selected registry. API clients select only IDs from these rows."""
    def __init__(self, recordings=DEFAULT_RECORDINGS, traces='output/rules-departure-v1', states='output/temporal-v1/replay-v1/observations.sqlite'):
        self.path, self.traces, self.states = Path(recordings).resolve(), Path(traces).resolve(), Path(states).resolve()
        rows = json.loads(self.path.read_text())
        self.sources = {r['episode_id']:r for r in rows}
        if len(rows) != len(self.sources):
            raise ValueError('duplicate registered source')
        run = json.loads((self.traces/'run.json').read_text())
        if run['recordings_sha256'] != file_hash(self.path):
            raise ValueError('perception/registry manifest mismatch')
        self.identity = dict(recordings_sha256=file_hash(self.path), trace_run_sha256=file_hash(self.traces/'run.json'), state_store_sha256=file_hash(self.states))

    def load(self, episode_id):
        if episode_id not in self.sources:
            raise ValueError('unregistered episode')
        source = self.sources[episode_id]
        root = self.traces/episode_id
        summary = json.loads((root/'complete.json').read_text())
        if file_hash(root/'frames.jsonl') != summary['frames_sha256']:
            raise ValueError('perception trace changed')
        rows = [json.loads(line) for line in (root/'frames.jsonl').read_text().splitlines()]
        if len(rows) != source['frames'] or len(rows) != len(source['pts_us']):
            raise ValueError('incomplete source trace')
        for index,row in enumerate(rows):
            f=row['frame']
            if f['frame_index'] != index or f['pts_us'] != source['pts_us'][index] or f['episode_id'] != episode_id or f['video_sha256'] != source['video_sha256']:
                raise ValueError('trace frame registration mismatch')
            if not math.isfinite(row['inference_seconds']) or row['inference_seconds'] < 0:
                raise ValueError('invalid recorded service time')
        con=sqlite3.connect(self.states.as_uri()+'?mode=ro',uri=True)
        try:
            states=[Observation(**json.loads(r[0])).validate() for r in con.execute("SELECT payload FROM observations WHERE run_id='temporal-replay-v1' AND episode_id=? AND stream_id='state/F__linear_head' ORDER BY committed_us",(episode_id,))]
        finally:
            con.close()
        return source, rows, states, summary


class DepartureStream:
    """Dropped/out-of-order frame coverage invalidates consecutive-frame state."""
    def __init__(self, episode_id):
        self.episode_id=episode_id
        self.last_index=-1
        self.cycle=None
        self.detector=None

    def observe(self, frame, frame_id, score, cycle):
        gap=self.cycle==cycle and frame['frame_index'] != self.last_index+1
        if self.cycle != cycle or gap:
            self.detector=DepartureDetector(self.episode_id)
        self.cycle=cycle;self.last_index=frame['frame_index']
        return self.detector.observe(frame_id,frame['pts_us'],score), gap


class ReplayEngine:
    def __init__(self, catalog, output, options, *, run_id=None):
        self.catalog,self.options=catalog,options.validate()
        self.source,self.trace,self.states,self.trace_summary=catalog.load(options.episode_id)
        self.run_id=run_id or 'replay-'+uuid.uuid4().hex[:16]
        self.root=Path(output).resolve()/self.run_id
        self.root.mkdir(parents=True,exist_ok=False)
        self.broker=EvidenceBroker(self.source,self.root/'evidence')
        self.store=ReplayStore(self.root/'replay.sqlite')
        self.scheduler=Scheduler(self.root/'jobs',max_jobs=options.max_jobs,max_bytes=options.max_bytes)
        self.clock=ReplayClock(options.speed)
        self.stream=DepartureStream(options.episode_id)
        self.contexts={}
        self.counts=Counter()
        self.latencies={'queue':[],'service':[],'total':[]}
        self.memory_high=0
        self.config=dict(run_id=self.run_id,options=asdict(options),source={k:v for k,v in self.source.items() if k not in ('video','pts_us')},identity=catalog.identity,
                         trace_mode='recorded_perception',verifier_mode=options.mode,
                         independent_accuracy_samples=1,capacity_repetitions=options.repetitions)
        write_json(self.root/'config.json',self.config)
        self.status='ready';self.error=None
        self._snapshot()

    def _append(self,kind,payload,event_us,cycle=0,case_id=None):
        return self.store.append(kind,payload,event_us=event_us,available_us=max(event_us,self.clock.now_us()),cycle=cycle,case_id=case_id)

    def _snapshot(self):
        process=psutil.Process()
        memory=process.memory_info().rss
        if self.scheduler.process is not None:
            try: memory += psutil.Process(self.scheduler.process.pid).memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError): pass
        self.memory_high=max(self.memory_high,memory)
        state=dict(run_id=self.run_id,status=self.status,horizon_us=self.clock.now_us(),source_end_us=self.options.repetitions*self.source['duration_us'],
                   wall_seconds=time.monotonic()-self.clock.started,options=asdict(self.options),scheduler=self.scheduler.snapshot(),counts=dict(self.counts),peak_host_and_worker_rss_bytes=self.memory_high,error=self.error)
        write_json(self.root/'status.json',state)
        return state

    def _submit(self,job,context):
        self.contexts[job.id]=context
        self.scheduler.submit(job)

    def _perception(self,row,cycle):
        frame=row['frame'];event_us=ReplayClock.source_time(frame['pts_us'],cycle,self.source['duration_us'])
        packet=self.broker.trace_packet(frame,dict(person_score=row['person_score'],detections=row['detections']),cycle=cycle,horizon_us=self.clock.now_us())
        payload=dict(mode='recorded',service_seconds=min(120.,row['inference_seconds']*self.options.service_multiplier),result=packet)
        job=Job(f'p-{cycle}-{frame["frame_index"]}','perception',payload,(sys.executable,'-m','video_workbench.replay.worker'),event_us,cycle=cycle,budget_seconds=self.options.perception_deadline_seconds)
        self._submit(job,dict(row=row))

    def _candidate(self,candidate,cycle):
        self.counts['candidates']+=1
        offset=cycle*self.source['duration_us']
        entity=self.options.episode_id+':object-'+self.source['entity_id']
        available_local=max(candidate['available_us'],self.clock.now_us()-offset)
        event=Event(candidate['event_id'],self.options.episode_id,entity,'yolo/camera-exit','camera_exit',candidate['event_us'],candidate['event_us'],available_local,available_local).validate()
        rule=dict(schema_version=1,rule_id='door-closed-at-camera-exit',op='state_at_event',event_stream=event.stream_id,event_id=event.id,state_stream='state/F__linear_head',property='door_open',expected=False)
        baseline=evaluate(rule,self.options.episode_id,entity,[event],self.states,as_of_us=available_local)
        case_id=digest([self.run_id,cycle,rule,entity])[:24]
        self._append('candidate',dict(candidate=candidate,event=asdict(event),rule=rule),offset+event.lo_us,cycle,case_id)
        self._append('decision',dict(condition='baseline',decision=baseline),offset+event.lo_us,cycle,case_id)
        self.counts['baseline_'+baseline['status']]+=1
        if baseline['status']!='UNKNOWN':return
        row=next(r for r in self.trace if r['frame_id']==candidate['frame_id'])
        approved=self.broker.image(row['frame'],entity_id=entity,cycle=cycle,horizon_us=self.clock.now_us())
        self._append('evidence',dict(frame={k:v for k,v in approved.items() if k!='path'},file=Path(approved['path']).name),offset+event.lo_us,cycle,case_id)
        plan=plan_request(rule,baseline,event,[approved],self.source['entity_label'])
        if plan['status']!='ready':
            self._append('gap',dict(reason=plan['reason'],kind='verifier'),offset+event.lo_us,cycle,case_id);return
        profile=make_profile(self.options.family)
        request=dict(plan['request'],max_output_tokens=profile['max_output_tokens'],deadline_ms=profile['deadline_ms'])
        request['request_id']=digest({k:v for k,v in request.items() if k!='request_id'})
        if self.options.mode=='recorded':
            original=next((e for e in self.trace_summary['candidates'] if e['event_us']==event.lo_us),None)
            if original is None:
                self._append('gap',dict(reason='no_recorded_verifier_for_exact_candidate',kind='verifier'),offset+event.lo_us,cycle,case_id);return
            path=self.catalog.traces/self.options.episode_id/(original['event_id']+'-'+self.options.family+'-handoff.json')
            saved=json.loads(path.read_text())['verifier']
            original_frame=json.loads((path.parent/(original['event_id']+'-packet.json')).read_text())['frame']
            if approved['sha256']!=original_frame['sha256']:
                raise ValueError('recorded verifier image bytes mismatch')
            if saved['profile_sha256']!=profile_hash(profile):
                raise ValueError('recorded verifier profile mismatch')
            payload=dict(mode='recorded',service_seconds=min(120.,saved['elapsed_seconds']*self.options.service_multiplier),result=saved['runtime'])
            command=(sys.executable,'-m','video_workbench.replay.worker')
        else:
            payload=dict(mode='live_verifier',request=request,profile=profile,model=str(Path(MODELS[self.options.family]).resolve()))
            command=(str(Path('workbench/verify-env/.venv/bin/python').absolute()),'-m','video_workbench.replay.worker')
        job=Job('v-'+case_id,'verifier',payload,command,offset+event.lo_us,cycle=cycle,mandatory=False,budget_seconds=self.options.verifier_deadline_seconds,case_id=case_id,
                input_bytes=len(json.dumps(payload).encode())+Path(approved['path']).stat().st_size+row['frame']['width']*row['frame']['height']*3)
        self._submit(job,dict(rule=rule,baseline=baseline,event=event,request=request,profile=profile))

    def _complete(self,completion):
        job=completion['job'];context=self.contexts.pop(job.id)
        self.counts[job.kind+'_'+completion['status']]+=1
        for key in self.latencies:self.latencies[key].append(completion[key+'_seconds'])
        payload=dict(job_id=job.id,job_kind=job.kind,mandatory=job.mandatory,status=completion['status'],reason=completion['reason'],
                     queue_seconds=completion['queue_seconds'],service_seconds=completion['service_seconds'],total_seconds=completion['total_seconds'])
        self._append('job',payload,job.event_us,job.cycle,job.case_id)
        if completion['status']!='completed':
            self._append('gap',payload,job.event_us,job.cycle,job.case_id)
            return
        result=completion['result']
        expected_mode='recorded' if job.kind=='perception' else self.options.mode
        if result.get('mode')!=expected_mode:
            self._append('gap',dict(reason='worker mode mismatch',job_id=job.id),job.event_us,job.cycle,job.case_id);return
        if job.kind=='perception':
            row=context['row'];packet=result['payload']
            if packet['frame']!=row['frame'] or packet['value']['person_score']!=row['person_score']:
                raise ValueError('recorded perception worker binding mismatch')
            candidate,gap=self.stream.observe(row['frame'],row['frame_id'],packet['value']['person_score'],job.cycle)
            if gap:self._append('gap',dict(reason='nonconsecutive_perception_prefix_reset',frame_index=row['frame']['frame_index']),job.event_us,job.cycle)
            # Keep actual detections available for overlays; do not import future rows.
            self._append('perception',packet,job.event_us,job.cycle)
            if candidate:self._candidate(candidate,job.cycle)
        else:
            raw=result['payload'];request=context['request'];profile=context['profile']
            check_packet(request)
            if raw.get('profile_sha256')!=profile_hash(profile) or raw.get('profile')!=profile:
                raise ValueError('verifier profile binding mismatch')
            if self.options.mode=='live_verifier' and raw.get('request_id')!=request['request_id']:
                raise ValueError('live verifier request binding mismatch')
            parsed=parse_with_recovery(request,raw['raw'],profile,raw.get('finish_reason'))
            if parsed['status']!='ok':
                self._append('gap',dict(reason='invalid_verifier_answer',validation=parsed),job.event_us,job.cycle,job.case_id);return
            completed_local=self.clock.now_us()-job.cycle*self.source['duration_us']
            conditioned=evaluate_answer(context['rule'],context['baseline'],context['event'],request,json.dumps(parsed['answer']),self.run_id,self.options.family,completed_local)
            decision=conditioned['decision']
            self.counts['verifier_'+decision['status']]+=1
            self._append('decision',dict(condition=self.options.family,mode=self.options.mode,decision=decision,answer=parsed['answer'],observation=asdict(conditioned['observation']),
                                         profile_sha256=profile_hash(profile),runtime={k:raw.get(k) for k in ('prompt_tokens','generation_tokens','peak_mlx_bytes','versions')},raw=raw['raw']),job.event_us,job.cycle,job.case_id)

    def run(self,cancel=None):
        self.status='running';cycle=index=state_index=0;last_snapshot=0.
        try:
            while cycle<self.options.repetitions or self.scheduler.has_work:
                if cancel is not None and cancel():
                    for done in self.scheduler.cancel():self._complete(done)
                    self.status='cancelled';break
                horizon=self.clock.now_us()
                while cycle<self.options.repetitions:
                    offset=cycle*self.source['duration_us']
                    # Publish only already-committed sampled observations.
                    while state_index<len(self.states) and offset+self.states[state_index].committed_us<=horizon:
                        observation=self.states[state_index]
                        self._append('state',asdict(observation),offset+observation.event_us,cycle)
                        state_index+=1
                    if index==len(self.trace):
                        if horizon<offset+self.source['duration_us']:break
                        cycle+=1;index=state_index=0
                        continue
                    if offset+self.trace[index]['frame']['pts_us']>horizon:break
                    self._perception(self.trace[index],cycle);index+=1
                    # Drain outcomes between admissions, bounding the terminal buffer.
                    for done in self.scheduler.poll():self._complete(done)
                    horizon=self.clock.now_us()
                for done in self.scheduler.poll():self._complete(done)
                if cycle==self.options.repetitions:self.status='draining'
                if time.monotonic()-last_snapshot>.2:
                    self._snapshot();last_snapshot=time.monotonic()
                time.sleep(.005)
            if self.status not in ('cancelled','failed'):self.status='complete'
        except Exception as exc:
            self.error=f'{type(exc).__name__}: {exc}';self.status='failed'
            for done in self.scheduler.cancel():
                job=done['job']
                self._append('gap',dict(job_id=job.id,reason='run_failed',error=self.error),job.event_us,job.cycle,job.case_id)
        finally:
            state=self._snapshot()
            state['latency_seconds']={key:dict(count=len(values),mean=sum(values)/len(values) if values else None,p50=sorted(values)[len(values)//2] if values else None,p95=sorted(values)[min(len(values)-1,int(.95*len(values)))] if values else None,max=max(values) if values else None) for key,values in self.latencies.items()}
            state['processed_frame_fraction']=self.counts['perception_completed']/(self.options.repetitions*len(self.trace))
            write_json(self.root/'summary.json',state)
            self.store.close()
        return state
