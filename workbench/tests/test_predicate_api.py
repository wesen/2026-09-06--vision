from pathlib import Path
from dataclasses import asdict
import json
from fastapi.testclient import TestClient
from video_workbench.registry import file_hash
from video_workbench.predicates.app import create_app
from video_workbench.predicates.contracts import StateLabel,StateObservation


def test_evidence_allowlist_range_and_hash_change(tmp_path):
    image=tmp_path/'frame.png';image.write_bytes(b'image-fixture')
    video=tmp_path/'source.mp4';video.write_bytes(b'0123456789')
    sample=dict(sample_id='sample',episode_id='ep',entity_id='ep:object-1',entity_class='fridge',property='door_open',sample_us=0,frame_index=0,split='test',split_group='apartment',image='frame.png',image_sha256=file_hash(image),video='source.mp4',video_sha256=file_hash(video))
    label=StateLabel('sample','ep:object-1','door_open',None,'occluded','r','r1','reviewed_rgb','actor')
    obs=StateObservation('sample','ep','ep:object-1','door_open',0,1,'replay',False,0.,.1,None,('sample',),'space','producer')
    run=tmp_path/'run';run.mkdir()
    for name,value in [('samples.json',[sample]),('labels.json',[asdict(label)]),('results.json',dict(run_id='run',feature_space_id='space',conditions={'generic':{'producer_id':'producer'}},limitations=[]))]:
        (run/name).write_text(json.dumps(value))
    (run/'observations.jsonl').write_text(json.dumps(dict(asdict(obs),condition='generic',split='test'))+'\n')
    client=TestClient(create_app(run,tmp_path))
    assert client.get('/v1/state/run').json()['observations'][0]['value'] is False
    assert client.get('/v1/state/evidence/unknown/image').status_code==404
    assert client.get('/v1/state/evidence/sample/labels').status_code==404
    response=client.get('/v1/state/evidence/sample/video',headers={'Range':'bytes=2-5'})
    assert response.status_code==206 and response.content==b'2345'
    image.write_bytes(b'changed')
    assert client.get('/v1/state/evidence/sample/image').status_code==409
