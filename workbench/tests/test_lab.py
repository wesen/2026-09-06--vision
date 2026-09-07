"""Feature-boundary checks for the laboratory's evidence and option contracts."""
from pathlib import Path
import pytest
from video_workbench.lab.contracts import Selection,Experiment
from video_workbench.lab.catalog import Catalog,ROOT
from video_workbench.lab.evidence import prepare

def test_ranges_and_model_combinations():
    for kwargs in ({'end_us':0},{'start_us':2,'end_us':1},{'fps':float('nan')},{'crop':[.8,0,.2,1]}):
        with pytest.raises(ValueError): Selection(episode_id='x',**kwargs)
    with pytest.raises(ValueError): Experiment(episode_id='x',component='embeddings',model='qwen')

def test_corpus_identity_and_exact_preview(tmp_path):
    catalog=Catalog(); eid='home-v1--ep-7d3106fb1cac9776'
    if eid not in catalog.sources: pytest.skip('local corpus absent')
    source=catalog.get(eid)
    assert source['original_episode_id']=='ep-7d3106fb1cac9776'
    result=prepare(catalog,Selection(episode_id=eid,start_us=9500000,end_us=10500000,fps=2,crop=(.25,0,.75,1)),tmp_path)
    assert [f['pts_us'] for f in result['frames']]==[9500000,10000000]
    assert result['frames'][0]['width']==source['media']['width']//2
    with pytest.raises(ValueError,match='64 sample'):
        prepare(catalog,Selection(episode_id=eid,end_us=14000000,fps=10),tmp_path/'too-many')

def test_project_reader_and_resource_boundaries():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from video_workbench.lab.resources import Resources
    resources=Resources(ROOT);app=FastAPI();resources.attach(app)
    with TestClient(app) as client:
        assert client.get('/resources').status_code==200
        entries=client.get('/v1/lab/resources?component=embeddings').json()
        source=next(e for e in entries['local'] if e['path'].endswith('/native_video.py'))
        response=client.get(source['url'])
        assert 'id="L42"' in response.text
        assert 'class="highlight"' in response.text
        assert "default-src 'none'" in response.headers['content-security-policy']
        markdown=next(e for e in entries['local'] if e['kind']=='markdown')
        rendered=client.get(markdown['url'])
        assert '<h1' in rendered.text and '<summary>Contents</summary>' in rendered.text
        assert client.get('/resources/../../.git/config').status_code==404
        assert client.get('/resources/not-indexed/raw').status_code==404
        assert client.get(source['raw_url']).headers['content-type'].startswith('text/plain')
        assert all('http' in e['url'] for e in entries['external'])

def test_transition_unknown_and_interval_policy():
    from video_workbench.lab.worker import transitions
    def sample(t,state):return dict(pts_us=t,state=state,frame={'id':str(t)})
    assert transitions([sample(0,'closed'),sample(1,'unknown'),sample(2,'open')],3)==[]
    assert transitions([sample(0,'closed'),sample(4,'open')],3)==[]
    assert transitions([sample(0,'closed'),sample(2,'open')],3)==[dict(kind='OPEN',start_us=0,end_us=2,interval='(start, end]',evidence_ids=['0','2'])]


def test_manager_cancels_real_process_group(tmp_path,monkeypatch):
    import subprocess,sys,time
    from video_workbench.lab import manager as module
    from types import SimpleNamespace
    root=tmp_path; (root/'checkpoint').write_text('model')
    monkeypatch.setattr(module,'prepare',lambda *args: {'frames':[]})
    monkeypatch.setitem(module.MODELS,'yolo11n',('perception',sys.executable,'checkpoint'))
    original=subprocess.Popen
    processes=[]
    def launch(command,**kwargs):
        p=original([sys.executable,'-c','import time; time.sleep(30)'],**kwargs);processes.append(p);return p
    monkeypatch.setattr(module.subprocess,'Popen',launch)
    m=module.Manager(SimpleNamespace(root=root),root)
    r=m.start(Experiment(episode_id='x'))
    end=time.monotonic()+3
    while not processes and time.monotonic()<end:time.sleep(.01)
    with pytest.raises(RuntimeError):m.start(Experiment(episode_id='x'))
    m.shutdown()
    import json
    assert json.loads((root/r['run_id']/'status.json').read_text())['status']=='cancelled'
    assert processes[0].poll() is not None

def test_comparison_and_exact_point_rules():
    from video_workbench.lab.analysis import compare,point_rule,RuleRequest
    from copy import deepcopy
    o=Experiment(episode_id='test',component='states',model='qwen').model_dump()
    run=dict(run_id='a',request=dict(options=o,evidence=dict(source=dict(video_sha256='a'*64,split='test'),frames=[dict(pts_us=0,sha256='b'*64,crop_xyxy=[0,0,10,10])])),result=dict(kind='states',records=[dict(pts_us=0,state='closed',frame={'id':'frame-0'})]))
    other=deepcopy(run);other['run_id']='b';other['request']['options']['model']='cosmos'
    assert compare(run,other)['same_evidence']
    other['request']['evidence']['frames'][0]['sha256']='c'*64
    assert not compare(run,other)['same_evidence']
    assert point_rule(run,RuleRequest(event_us=0))['decision']['status']=='PASS'
    assert point_rule(run,RuleRequest(event_us=1))['decision']['status']=='UNKNOWN'
    assert point_rule(run,RuleRequest(event_us=0,expected_open=True))['decision']['status']=='VIOLATION'
