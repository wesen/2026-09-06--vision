"""Feature-boundary checks for real subprocess behavior and evidence visibility."""
import json
import os
from pathlib import Path
import signal
import sqlite3
import sys
import time
import pytest
from video_workbench.replay.clock import ReplayClock
from video_workbench.replay.broker import EvidenceBroker
from video_workbench.replay.scheduler import Scheduler, Job
from video_workbench.replay.store import ReplayStore
from video_workbench.registry import file_hash


def job(name, *, mandatory=True, seconds=0., budget=2., size=300):
    return Job(name,'test',dict(mode='recorded',service_seconds=seconds,result={'value':name}),
               (sys.executable,'-m','video_workbench.replay.worker'),0,
               mandatory=mandatory,budget_seconds=budget,input_bytes=size)


def drain(s):
    results=[];until=time.monotonic()+5
    while s.has_work:
        results.extend(s.poll())
        assert time.monotonic()<until
        time.sleep(.005)
    return results


def test_clock_mapping_and_backward_time():
    now=[2.0];c=ReplayClock(2,monotonic=lambda:now[0]);now[0]=3
    assert c.now_us()==2000000
    assert c.source_time(100,2,1000)==2100
    now[0]=2.5
    with pytest.raises(ValueError):c.now_us()
    for speed in [0,-1,float('nan'),float('inf')]:
        with pytest.raises(ValueError):ReplayClock(speed)


def test_broker_gates_cached_dependencies_and_paths(tmp_path):
    video=tmp_path/'source.mp4';video.write_bytes(b'fixture')
    source=dict(video=str(video),video_sha256=file_hash(video),episode_id='a',duration_us=1000,pts_us=[0,100])
    b=EvidenceBroker(source,tmp_path/'images')
    f=dict(episode_id='a',video_sha256=source['video_sha256'],frame_index=1,raw_pts=1,time_base='1/10',pts_us=100,width=640,height=480)
    with pytest.raises(ValueError):b.trace_packet(f,{},cycle=0,horizon_us=99)
    with pytest.raises(ValueError):b.trace_packet(f,{'features':[1,2]},cycle=0,horizon_us=199,available_us=200,dependency_end_us=180)
    p=b.trace_packet(f,{'features':[1,2]},cycle=2,horizon_us=2200,available_us=200,dependency_end_us=180)
    assert p['value']['features']==[1,2]
    with pytest.raises(ValueError):b.trace_packet(f,{'nested':{'video':str(video)}},cycle=0,horizon_us=1000)
    with pytest.raises(ValueError):b.image(f,entity_id='target',cycle=1,horizon_us=1099)


def test_queue_bounds_include_running_priority_and_eviction(tmp_path):
    s=Scheduler(tmp_path,max_jobs=2,max_bytes=600)
    first=job('first',seconds=.05)
    assert s.submit(first);s.poll()
    assert s.submit(job('optional',mandatory=False))
    assert s.submit(job('mandatory'))
    assert not s.submit(job('too_many'))
    assert s.snapshot()['high_jobs']==2 and s.snapshot()['high_bytes']==600
    results=drain(s)
    reasons={r['job'].id:r['reason'] for r in results}
    assert reasons['optional']=='evicted_for_mandatory'
    assert reasons['too_many']=='admission_bound'
    assert [r['job'].id for r in results if r['status']=='completed']==['first','mandatory']


def test_byte_bound_and_mandatory_priority(tmp_path):
    s=Scheduler(tmp_path,max_jobs=5,max_bytes=500)
    assert not s.submit(job('oversize',size=501))
    assert s.submit(job('optional',mandatory=False,size=200))
    assert s.submit(job('mandatory',size=200))
    results=drain(s)
    assert [r['job'].id for r in results if r['status']=='completed']==['mandatory','optional']
    assert s.high_bytes==400


def test_queue_deadline_running_timeout_and_reaping(tmp_path):
    s=Scheduler(tmp_path,max_jobs=3)
    s.submit(job('slow',seconds=2,budget=.1));s.poll();pid=s.process.pid
    s.submit(job('expires',budget=.02))
    results=drain(s)
    assert {r['job'].id:r['status'] for r in results}=={'slow':'timeout','expires':'expired'}
    with pytest.raises(ProcessLookupError):os.kill(pid,0)


def test_cancellation_reaps_worker(tmp_path):
    s=Scheduler(tmp_path);s.submit(job('slow',seconds=2));s.poll();pid=s.process.pid
    s.submit(job('waiting'))
    results=s.cancel()
    assert len(results)==2 and all(r['status']=='cancelled' for r in results)
    assert not s.has_work
    with pytest.raises(ProcessLookupError):os.kill(pid,0)


@pytest.mark.parametrize('code,reason', [
    ("import sys;sys.exit(4)",'worker exit 4'),
    ("import sys;open(sys.argv[-1],'w').write('bad')",'Expecting value'),
    ("import sys;open(sys.argv[-1],'w').write('x'*2000)",'worker output exceeds bound')])
def test_worker_failures_are_terminal(tmp_path,code,reason):
    s=Scheduler(tmp_path,max_output_bytes=1000)
    j=job('bad');j.command=(sys.executable,'-c',code);s.submit(j)
    result=drain(s)[0]
    assert result['status']=='failed' and reason in result['reason']


def test_store_asof_pagination_and_immutable_identity(tmp_path):
    path=tmp_path/'replay.sqlite';s=ReplayStore(path)
    s.append('baseline',{'status':'UNKNOWN'},event_us=100,available_us=200,case_id='c',record_id='a')
    s.append('verifier',{'status':'PASS'},event_us=100,available_us=400,case_id='c',record_id='b')
    assert len(s.events(as_of_us=399)['events'])==1
    assert s.events(as_of_us=400,limit=1)['next_after']==1
    assert s.events(as_of_us=400,after=1)['events'][0]['kind']=='verifier'
    assert s.append('baseline',{'status':'UNKNOWN'},event_us=100,available_us=200,case_id='c',record_id='a')==1
    with pytest.raises(ValueError):s.append('baseline',{'status':'PASS'},event_us=100,available_us=200,case_id='c',record_id='a')
    with pytest.raises(sqlite3.IntegrityError):s.con.execute("UPDATE records SET kind='changed'")
    s.close();reader=ReplayStore(path,readonly=True)
    assert len(reader.events(as_of_us=400)['events'])==2
    reader.close()
