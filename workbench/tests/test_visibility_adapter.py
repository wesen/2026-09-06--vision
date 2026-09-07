import copy
import json
import sys
from pathlib import Path
import pytest
from video_workbench.verifiers.visibility import parse_visibility,prompt
from video_workbench.verifiers.adapter import check_packet,supervise
from video_workbench.rules.evaluate import digest,Event,evaluate
from video_workbench.rules.handoff import investigate

@pytest.fixture
def packet():
 root=Path(__file__).resolve().parents[2]
 p=next((root/'ttmp/2026/09/06').glob('COSMOS-VERIFY-001--*'))/'various/visibility-v2/protocol.json'
 return json.loads(p.read_text())['cases'][0]['request']

def payload(**kw):
 d=dict(target_identified=True,door_observable=True,answer='false',evidence=['F1'],rationale='Visible door is seated against the frame.');d.update(kw);return json.dumps(d)

def test_host_binds_ids_and_short_citation(packet):
 r=parse_visibility(packet,'```json\n'+payload()+'\n```')
 assert r['status']=='ok' and r['answer']['request_id']==packet['request_id']
 assert r['answer']['evidence_ids']==[packet['frames'][0]['id']]
 assert packet['request_id'] not in prompt(packet) and packet['entity_id'] not in prompt(packet)

@pytest.mark.parametrize('kw',[dict(door_observable=False),dict(target_identified=False),dict(evidence=['F2']),dict(evidence=[]),dict(target_identified='yes'),dict(request_id='invented'),dict(rationale='')])
def test_invalid_visibility_payloads(packet,kw):
 assert parse_visibility(packet,payload(**kw))['status']=='invalid'

def test_unknown_is_not_closed(packet):
 r=parse_visibility(packet,payload(target_identified=False,door_observable=False,answer='unknown',evidence=[]))
 assert r['status']=='ok' and r['answer']['answer']=='unknown'

def test_duplicate_keys_rejected(packet):
 raw=payload()[:-1]+',"answer":"true"}'
 assert parse_visibility(packet,raw)['status']=='invalid'

def test_changed_image_rejected(packet,tmp_path):
 p=tmp_path/'changed.png';p.write_bytes(b'changed');packet['frames'][0]['path']=str(p);packet['request_id']=digest({k:v for k,v in packet.items() if k!='request_id'})
 with pytest.raises(ValueError,match='bytes changed'):check_packet(packet)

def test_future_evidence_rejected(packet):
 packet['frames'][0]['available_us']=packet['as_of_us']+1;packet['request_id']=digest({k:v for k,v in packet.items() if k!='request_id'})
 with pytest.raises(ValueError,match='horizon'):check_packet(packet)

def test_timeout_then_next_worker_recovers(tmp_path):
 r=supervise([sys.executable,'-c','import time; time.sleep(30)'],.1,tmp_path/'timeout.log')
 assert r['status']=='timeout' and r['returncode']<0 and r['elapsed_seconds']<5
 r=supervise([sys.executable,'-c','print("next")'],5,tmp_path/'next.log')
 assert r['status']=='ok' and (tmp_path/'next.log').read_text().strip()=='next'

def test_runtime_error_is_not_false(tmp_path):
 assert supervise([sys.executable,'-c','raise RuntimeError("fixture")'],5,tmp_path/'error.log')['status']=='runtime_error'

def test_rules_keep_baseline_and_bind_host_answer(packet,tmp_path,monkeypatch):
 rule=dict(schema_version=1,rule_id='closed-at-sample',op='state_at_event',event_id='sample',event_stream='sample-events',state_stream='state',property='door_open',expected=False)
 event=Event('sample',packet['episode_id'],packet['entity_id'],'sample-events','sample',packet['event_us'],packet['event_us'],packet['event_us'],packet['event_us'])
 baseline=evaluate(rule,packet['episode_id'],packet['entity_id'],events=[event],as_of_us=packet['as_of_us']);before=copy.deepcopy(baseline)
 def fake_verify(request,*a,**kw):return dict(parse_visibility(request,payload()),completed_us=request['as_of_us']+100)
 monkeypatch.setattr('video_workbench.verifiers.adapter.verify',fake_verify)
 result=investigate(rule,baseline,event,packet['frames'],packet['entity_label'],'fixture',tmp_path/'run','run','fixture')
 assert baseline==before and baseline['status']=='UNKNOWN'
 assert result['conditioned']['decision']['status']=='PASS'
 assert result['conditioned']['source_evaluation_id']==baseline['evaluation_id']
