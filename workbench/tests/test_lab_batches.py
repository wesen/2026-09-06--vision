"""Batch admission, evidence binding and process cancellation at feature boundary."""
import json,sys,time,subprocess
from types import SimpleNamespace
import pytest
from video_workbench.lab.contracts import Experiment
from video_workbench.lab.batches import BatchPlan,BatchEntry,Batches
from video_workbench.lab import manager as supervisor
from video_workbench.lab import batches as module

@pytest.fixture
def runtime(tmp_path,monkeypatch):
    (tmp_path/'checkpoint').write_text('model')
    evidence=dict(source={'video_sha256':'a'*64,'split':'test'},frames=[dict(pts_us=0,sha256='b'*64,crop_xyxy=(0,0,10,10))])
    monkeypatch.setattr(supervisor,'prepare',lambda *args:evidence)
    monkeypatch.setattr(module,'prepare',lambda *args:evidence)
    monkeypatch.setitem(supervisor.MODELS,'yolo11n',('perception',sys.executable,'checkpoint'))
    manager=supervisor.Manager(SimpleNamespace(root=tmp_path),tmp_path)
    batch=Batches(manager)
    options=Experiment(episode_id='x',end_us=1)
    plan=BatchPlan(name='test',entries=[BatchEntry(label='A',options=options),BatchEntry(label='B',options=options)])
    yield batch,manager,plan,evidence
    batch.shutdown();manager.shutdown()

def test_batch_continues_failure_and_reserves_worker(runtime,monkeypatch):
    batch,manager,plan,_=runtime
    original=subprocess.Popen;processes=[]
    def launch(command,**kwargs):
        script='import time; time.sleep(.3); raise SystemExit(3)' if not processes else 'import pathlib,sys; pathlib.Path(sys.argv[1],"result.json").write_text("{}")'
        process=original([sys.executable,'-c',script,command[-1]],**kwargs);processes.append(process);return process
    monkeypatch.setattr(supervisor.subprocess,'Popen',launch)
    draft=batch.preview(plan);batch.start(draft['batch_id'])
    with pytest.raises(RuntimeError,match='reserved'):manager.start(plan.entries[0].options)
    batch.thread.join(4);assert not batch.thread.is_alive()
    value=batch.get(draft['batch_id'])
    assert value['status']=='completed_with_errors'
    assert [c['status'] for c in value['children']]==['failed','completed']
    assert manager.owner is None and len(processes)==2
    with pytest.raises(ValueError,match='draft'):batch.start(draft['batch_id'])

def test_batch_cancel_skips_unstarted_children(runtime,monkeypatch):
    batch,manager,plan,_=runtime
    original=subprocess.Popen;processes=[]
    def launch(command,**kwargs):
        p=original([sys.executable,'-c','import time;time.sleep(30)'],**kwargs);processes.append(p);return p
    monkeypatch.setattr(supervisor.subprocess,'Popen',launch)
    draft=batch.preview(plan);batch.start(draft['batch_id'])
    deadline=time.monotonic()+3
    while not processes and time.monotonic()<deadline:time.sleep(.01)
    batch.cancel(draft['batch_id']);batch.thread.join(4)
    assert not batch.thread.is_alive()
    result=batch.get(draft['batch_id'])
    assert result['status']=='cancelled'
    assert [c['status'] for c in result['children']]==['cancelled','skipped']
    assert len(processes)==1 and processes[0].poll() is not None and manager.owner is None

def test_changed_preview_evidence_prevents_inference(runtime,monkeypatch):
    batch,manager,plan,evidence=runtime
    draft=batch.preview(plan)
    evidence['frames'][0]['sha256']='c'*64
    def forbidden(*args,**kwargs):raise AssertionError('must not launch')
    monkeypatch.setattr(supervisor.subprocess,'Popen',forbidden)
    batch.start(draft['batch_id']);batch.thread.join(3)
    value=batch.get(draft['batch_id'])
    assert value['status']=='completed_with_errors'
    assert all(c['run_id'] is None and 'evidence changed' in c['error'] for c in value['children'])

def test_batch_requires_matched_selection():
    options=Experiment(episode_id='x')
    with pytest.raises(ValueError,match='share source'):
        BatchPlan(name='bad',entries=[BatchEntry(label='a',options=options),BatchEntry(label='b',options=options.model_copy(update={'start_us':1}))])
