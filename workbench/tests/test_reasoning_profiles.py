import copy
import json
from pathlib import Path
import pytest
from video_workbench.rules.evaluate import digest
from video_workbench.verifiers.profiles import make_profile, validate_profile, profile_hash
from video_workbench.verifiers.visibility import experiment_prompt, parse_experiment
from video_workbench.verifiers.contracts import validate_request
from video_workbench.verifiers.adapter import verify

@pytest.fixture
def packet():
    root=Path(__file__).resolve().parents[2]
    p=next((root/'ttmp/2026/09/06').glob('COSMOS-VERIFY-001--*'))/'various/visibility-v2/protocol.json'
    request=json.loads(p.read_text())['cases'][0]['request']
    request.update(max_output_tokens=4096,deadline_ms=120000)
    request['request_id']=digest({k:v for k,v in request.items() if k!='request_id'})
    return request


def payload():
    return json.dumps(dict(target_identified=True,door_observable=True,answer='false',evidence=['F1'],rationale='Door surface is visibly seated.'))


def test_profile_binding_and_limits(packet):
    p=make_profile('qwen',True,True)
    assert validate_profile(p,packet) is p
    q=copy.deepcopy(p);q['seed']+=1
    assert profile_hash(q)!=profile_hash(p)
    packet['max_output_tokens']=4097
    packet['request_id']=digest({k:v for k,v in packet.items() if k!='request_id'})
    with pytest.raises(ValueError,match='runtime limits'):validate_request(packet)

@pytest.mark.parametrize('key,value',[('seed',True),('temperature',float('nan')),('top_p',0),('top_k',-1),('prompt_style','auto'),('max_output_tokens',4097),('deadline_ms',120001),('system_prompt','arbitrary'),('penalty_context_size',0)])
def test_invalid_profiles(key,value):
    p=make_profile('cosmos');p[key]=value
    with pytest.raises(ValueError):validate_profile(p)


def test_prompt_replaces_direct_only_instruction(packet):
    text=experiment_prompt(packet,make_profile('qwen',True))
    assert 'no prose, with these exact fields' not in text
    assert 'step by step' in text and packet['request_id'] not in text


def test_reasoning_json_inside_body_is_not_answer(packet):
    raw='<think>{"answer":"true"} was a candidate, but visible door is seated.</think>\n```json\n'+payload()+'\n```'
    result=parse_experiment(packet,raw,make_profile('cosmos',True))
    assert result['status']=='ok' and result['answer']['answer']=='false'
    assert result['raw']==raw and result['normalizations']
    assert result['answer']['request_id']==packet['request_id']

@pytest.mark.parametrize('raw',[
    '<think>unfinished', '<think></think>'+payload(),
    '<think>reason</think>', 'prose <think>reason</think>'+payload(),
    '<think>one</think><think>two</think>'+payload(),
    '<think>one</think>'+payload()+' trailing',
    '<think>one</think>'+payload()+payload(),
    '<think>one</think>'+payload()[:-1]+',"answer":"true"}',
])
def test_bad_envelopes(packet,raw):
    assert parse_experiment(packet,raw,make_profile('qwen',True))['status']=='invalid'


def test_truncation_and_utf8_limit(packet):
    p=make_profile('qwen',True)
    assert 'truncated' in parse_experiment(packet,'<think>ok</think>'+payload(),p,'length')['reason']
    assert 'UTF-8' in parse_experiment(packet,'é'*(128*1024+1),p)['reason']
    assert parse_experiment(packet,payload(),make_profile('qwen'))['status']=='ok'


def test_host_rejects_worker_profile_substitution(packet,tmp_path,monkeypatch):
    model=tmp_path/'model';model.mkdir();(model/'config.json').write_text('{}')
    p=make_profile('qwen')
    def fake_supervise(command,*args):
        Path(command[5]).write_text(json.dumps(dict(request_id=packet['request_id'],raw=payload(),profile=p,profile_sha256='wrong')))
        return dict(status='ok')
    monkeypatch.setattr('video_workbench.verifiers.adapter.supervise',fake_supervise)
    result=verify(packet,model,tmp_path/'run',profile=p)
    assert result['status']=='runtime_error' and 'profile binding' in result['reason']


def test_qwen_literal_reasoning_envelope(packet):
    p=make_profile('qwen',True)
    raw='<reasoning>Door is visible and seated.</reasoning>'+payload()
    assert parse_experiment(packet,raw,p)['status']=='ok'
    assert '<reasoning>' in experiment_prompt(packet,p)
    assert parse_experiment(packet,raw.replace('</reasoning>',''),p)['status']=='invalid'
