"""Integration smoke against an actual completed replay plus bounded API inputs."""
from pathlib import Path
from threading import Event
import json
import pytest
from fastapi.testclient import TestClient
from video_workbench.replay.app import create_app,Manager,StartRequest
from video_workbench.replay.engine import Catalog

RUN='replay-0adb49ee32254188'


@pytest.fixture
def client():
    if not Path('output/replay-workbench',RUN,'summary.json').exists():pytest.skip('local measured replay fixture unavailable')
    with TestClient(create_app(Catalog(),'output/replay-workbench')) as client:yield client


def test_actual_asof_citation_media_and_pagination(client):
    state=client.get('/v1/replays/'+RUN).json();end=state['horizon_us']
    rows=[];after=0
    while True:
        page=client.get(f'/v1/replays/{RUN}/events',params={'as_of_us':end,'after':after,'limit':23}).json()
        rows.extend(page['events']);after=page['next_after']
        if len(page['events'])<23:break
    assert len({r['seq'] for r in rows})==len(rows)
    decisions=[r for r in rows if r['kind']=='decision']
    baseline=next(r for r in decisions if r['payload']['condition']=='baseline')
    verified=next(r for r in decisions if r['payload']['condition']=='qwen')
    assert baseline['payload']['decision']['status']=='UNKNOWN'
    assert verified['payload']['mode']=='live_verifier'
    old=client.get(f'/v1/replays/{RUN}/events',params={'as_of_us':verified['available_us']-1,'limit':500}).json()['events']
    assert baseline['seq'] in {r['seq'] for r in old}
    assert verified['seq'] not in {r['seq'] for r in old}
    evidence=next(r for r in rows if r['kind']=='evidence');eid=evidence['payload']['frame']['id']
    url=f'/v1/replays/{RUN}/evidence/{eid}'
    assert client.get(url,params={'as_of_us':evidence['available_us']-1}).status_code==404
    response=client.get(url,params={'as_of_us':end})
    assert response.status_code==200 and response.headers['content-type']=='image/png'
    response=client.get('/v1/episodes/ep-7d3106fb1cac9776/video',headers={'Range':'bytes=0-99'})
    assert response.status_code==206 and len(response.content)==100
    assert client.get(f'/v1/replays/{RUN}/events',params={'as_of_us':end+1}).status_code==422


def test_unregistered_and_unbounded_inputs(client):
    assert client.get('/v1/episodes/nope/video').status_code==404
    assert client.get('/v1/replays/not-a-run').status_code==404
    assert client.get(f'/v1/replays/{RUN}/events',params={'limit':501}).status_code==422
    assert client.post('/v1/replays',json={'episode_id':'nope'}).status_code==404
    assert client.post('/v1/replays',json={'episode_id':'ep-7d3106fb1cac9776','model':'/tmp/arbitrary'}).status_code==422
    assert client.post('/v1/replays',json={'episode_id':'ep-7d3106fb1cac9776','repetitions':101}).status_code==422


def test_one_active_run_and_cancellation(tmp_path,monkeypatch):
    entered=Event()
    class FakeEngine:
        def __init__(self,*args,**kwargs):pass
        def run(self,cancel):
            import time
            entered.set()
            while not cancel():time.sleep(.001)
    monkeypatch.setattr('video_workbench.replay.app.ReplayEngine',FakeEngine)
    catalog=type('Catalog',(),{'sources':{'ep':{}}})()
    manager=Manager(catalog,tmp_path)
    first=manager.start(StartRequest(episode_id='ep'));assert entered.wait(1)
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as caught:manager.start(StartRequest(episode_id='ep'))
    assert caught.value.status_code==409
    manager.shutdown();assert not manager.thread.is_alive()
