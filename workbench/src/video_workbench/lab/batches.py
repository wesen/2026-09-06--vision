"""Bounded local batches reserve the existing supervisor and run children serially."""
import json,re,time,uuid
from threading import Thread,Event,Lock
from pydantic import BaseModel,ConfigDict,Field,model_validator
from .contracts import Experiment
from .catalog import MODELS
from .evidence import prepare
from .handoff import validate
from .presentation import reasoning_prompt
from .manager import write

class BatchEntry(BaseModel):
    model_config=ConfigDict(extra='forbid')
    label:str=Field(min_length=1,max_length=120)
    options:Experiment

class BatchPlan(BaseModel):
    model_config=ConfigDict(extra='forbid')
    name:str=Field(min_length=1,max_length=120)
    entries:list[BatchEntry]=Field(min_length=2,max_length=8)

    @model_validator(mode='after')
    def matched(self):
        if not self.name.strip():raise ValueError('batch name must not be blank')
        first=self.entries[0].options.model_dump()
        variable={'model','prompt','crop','handoff'}
        for entry in self.entries:
            if not entry.label.strip():raise ValueError('variant label must not be blank')
            if any(value!=first[key] for key,value in entry.options.model_dump().items() if key not in variable):
                raise ValueError('batch variants must share source, time, FPS, component, target and non-variant settings')
        if sum((e.options.end_us-e.options.start_us)*e.options.fps/1e6 for e in self.entries)>128:
            raise ValueError('batch exceeds 128 requested sample budget')
        return self

def evidence_identity(evidence):
    return (evidence['source'],[(f['pts_us'],f['sha256'],list(f['crop_xyxy'])) for f in evidence['frames']])

class Batches:
    def __init__(self,manager):
        self.manager=manager;self.directory=manager.output/'batches';self.directory.mkdir(exist_ok=True)
        self.lock=Lock();self.thread=None;self.stop=Event();self.active=None
        for path in self.directory.glob('batch-*/status.json'):
            status=json.loads(path.read_text())
            if status['status']=='running':
                status['status']='interrupted'
                for child in status['children']:
                    if child['status'] in ('running','pending'):child['status']='interrupted'
                write(path,status)

    def path(self,identifier):
        if not re.fullmatch(r'batch-[a-f0-9]{16}',identifier):raise ValueError('unknown batch')
        path=self.directory/identifier
        if not (path/'request.json').is_file():raise ValueError('unknown batch')
        return path

    def preview(self,plan):
        entries=[]
        for entry in plan.entries:
            options=entry.options
            validate(self.manager.output,options)
            _,python,checkpoint=MODELS[options.model]
            if not (self.manager.catalog.root/python).is_file() or not (self.manager.catalog.root/checkpoint).exists():
                raise ValueError('required runtime/checkpoint missing for '+entry.label)
            if options.component in ('reasoning','states'):
                options=options.model_copy(update={'prompt':reasoning_prompt(options)['prompt']})
            preview_id='preview-'+uuid.uuid4().hex[:16]
            evidence=prepare(self.manager.catalog,options,self.manager.output/preview_id)
            entries.append(dict(label=entry.label,options=options.model_dump(),evidence=evidence,preview_id=preview_id))
        identifier='batch-'+uuid.uuid4().hex[:16];path=self.directory/identifier;path.mkdir()
        request=dict(batch_id=identifier,name=plan.name,created_unix=time.time(),entries=entries,
                     maximum_worker_seconds=sum(e.options.deadline_seconds for e in plan.entries))
        write(path/'request.json',request)
        write(path/'status.json',dict(batch_id=identifier,status='draft',children=[dict(label=e['label'],status='pending',run_id=None) for e in entries]))
        return self.get(identifier)

    def get(self,identifier):
        path=self.path(identifier);value=json.loads((path/'status.json').read_text());value['request']=json.loads((path/'request.json').read_text())
        for child in value['children']:
            if child['run_id']:
                root=self.manager.output/child['run_id']
                status=json.loads((root/'status.json').read_text());child.update(status=status['status'],elapsed_seconds=status.get('elapsed_seconds'),error=status.get('error'))
                if (root/'result.json').is_file():
                    result=json.loads((root/'result.json').read_text())
                    child['outcomes']=[dict(pts_us=r['frame']['pts_us'],state=r.get('state'),validation=r.get('parsed',{}).get('status'),detections=len(r.get('detections',[]))) for r in result.get('records',[])]
                    child['action_predictions']=[w['prediction'] for w in result.get('action_windows',[])]
                    if result.get('windows'):child['top_window']=result['windows'][result['ranking'][0]]
        return value

    def list(self):
        values=[self.get(p.parent.name) for p in self.directory.glob('batch-*/status.json')]
        return sorted(values,key=lambda v:v['request']['created_unix'],reverse=True)

    def start(self,identifier):
        with self.lock:
            path=self.path(identifier);value=self.get(identifier)
            if value['status']!='draft':raise ValueError('only a draft batch can be started; preview a new batch to repeat')
            with self.manager.lock:
                if self.manager.owner is not None or (self.manager.thread and self.manager.thread.is_alive()):raise RuntimeError('an experiment or batch is already active')
                self.manager.owner=identifier
            self.active=identifier;self.stop=Event();stop=self.stop
            status=dict(batch_id=identifier,status='running',started_unix=time.time(),children=value['children'])
            write(path/'status.json',status)
            def work():
                try:
                    for child,entry in zip(status['children'],value['request']['entries']):
                        if stop.is_set():break
                        try:
                            run=self.manager.start(Experiment.model_validate(entry['options']),owner=identifier,expected_evidence=entry['evidence'])
                            child.update(run_id=run['run_id'],status='running');write(path/'status.json',status)
                            while self.manager.thread.is_alive():
                                if stop.is_set():self.manager.cancel.set()
                                self.manager.thread.join(.1)
                            child['status']=json.loads((self.manager.output/run['run_id']/'status.json').read_text())['status']
                        except Exception as exc:child.update(status='failed',error=str(exc))
                        write(path/'status.json',status)
                    for child in status['children']:
                        if child['status']=='pending':child['status']='skipped'
                    status['status']='cancelled' if stop.is_set() else ('completed' if all(c['status']=='completed' for c in status['children']) else 'completed_with_errors')
                except Exception as exc:status.update(status='failed',error=str(exc))
                finally:
                    status['finished_unix']=time.time();write(path/'status.json',status)
                    with self.manager.lock:self.manager.owner=None
            self.thread=Thread(target=work,daemon=True);self.thread.start()
        return self.get(identifier)

    def cancel(self,identifier):
        with self.lock:
            if self.active!=identifier or not self.thread or not self.thread.is_alive():raise ValueError('batch is not active')
            self.stop.set()
        return dict(batch_id=identifier,status='cancelling')

    def shutdown(self):
        self.stop.set()
        if self.thread:self.thread.join()
