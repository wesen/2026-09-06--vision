"""Single expensive worker, immutable requests, cancellation and persisted status."""
from pathlib import Path
from threading import Lock,Thread,Event
import json,os,signal,subprocess,time,uuid
from .catalog import MODELS
from .evidence import prepare
from video_workbench.registry import file_hash

def write(path,value):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');tmp.replace(path)

class Manager:
    def __init__(self,catalog,output):
        self.catalog=catalog;self.output=Path(output);self.lock=Lock();self.thread=None;self.active=None;self.cancel=Event()
        for p in self.output.glob('run-*/status.json'):
            s=json.loads(p.read_text())
            if s['status'] in ('preparing','running'): write(p,dict(s,status='interrupted'))

    def start(self,request):
        with self.lock:
            if self.thread and self.thread.is_alive(): raise RuntimeError('one experiment is already running; cancel it or wait')
            run_id='run-'+uuid.uuid4().hex[:16];dest=self.output/run_id;dest.mkdir()
            # Validate and snapshot pixels before starting the worker. Preparation
            # is serialized with admission, so concurrent requests cannot overwrite.
            try: evidence=prepare(self.catalog,request,dest)
            except Exception:
                import shutil
                shutil.rmtree(dest);raise
            kind,python,checkpoint=MODELS[request.model]
            if not (self.catalog.root/python).is_file() or not (self.catalog.root/checkpoint).exists():
                import shutil
                shutil.rmtree(dest);raise ValueError('required local runtime/checkpoint missing')
            record=dict(schema_version=1,run_id=run_id,options=request.model_dump(),evidence=evidence,
                        checkpoint=checkpoint,worker_sha256=file_hash(Path(__file__).parent/'worker.py'),created_unix=time.time())
            write(dest/'request.json',record);write(dest/'status.json',dict(run_id=run_id,status='preparing'))
            self.active=run_id;self.cancel=Event();stop=self.cancel
            def work():
                started=time.monotonic();process=None
                status=dict(run_id=run_id,status='running',started_unix=time.time())
                write(dest/'status.json',status)
                try:
                    env=dict(os.environ,PYTHONPATH=str(self.catalog.root/'workbench/src'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
                    with (dest/'worker.log').open('wb') as log:
                        process=subprocess.Popen([str(self.catalog.root/python),'-m','video_workbench.lab.worker',str(dest)],cwd=self.catalog.root,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                        while process.poll() is None:
                            elapsed=time.monotonic()-started
                            if stop.is_set() or elapsed>request.deadline_seconds:
                                status['status']='cancelled' if stop.is_set() else 'timed_out'
                                os.killpg(process.pid,signal.SIGKILL);process.wait();break
                            if (dest/'worker.log').stat().st_size>2*1024*1024:
                                status.update(status='failed',error='worker log exceeded 2 MiB');os.killpg(process.pid,signal.SIGKILL);process.wait();break
                            stop.wait(.1)
                        if status['status']=='running':
                            if process.returncode==0 and (dest/'result.json').is_file(): status['status']='completed'
                            else: status.update(status='failed',error=(dest/'worker.log').read_text(errors='replace')[-4000:])
                except Exception as exc:
                    status.update(status='failed',error=f'{type(exc).__name__}: {exc}')
                finally:
                    if process and process.poll() is None:
                        os.killpg(process.pid,signal.SIGKILL);process.wait()
                    status['elapsed_seconds']=time.monotonic()-started;write(dest/'status.json',status)
            self.thread=Thread(target=work,daemon=True);self.thread.start()
        return dict(run_id=run_id,status='preparing')

    def shutdown(self):
        self.cancel.set()
        if self.thread:self.thread.join(5)
