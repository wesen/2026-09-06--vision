import json
from pathlib import Path
import pytest
from video_workbench.rules.evaluate import digest
from video_workbench.verifiers.profiles import make_profile
from video_workbench.verifiers.recovery import parse_with_recovery

@pytest.fixture
def request_packet():
    root=Path(__file__).resolve().parents[2]
    path=next((root/'ttmp/2026/09/06').glob('COSMOS-VERIFY-001--*'))/'various/reasoning-v3/protocol.json'
    return json.loads(path.read_text())['cases'][0]['request']


def payload(**kw):
    obj=dict(target_identified=True,door_observable=True,answer='false',evidence=['F1'],rationale='The visible door is seated.')
    obj.update(kw);return json.dumps(obj)

@pytest.mark.parametrize('family,opening',[('qwen','<reasoning>'),('cosmos','<think>')])
@pytest.mark.parametrize('fenced',[False,True])
def test_missing_close_only(request_packet,family,opening,fenced):
    final='```json\n'+payload()+'\n```' if fenced else payload()
    raw=' \n'+opening+'\nVisible door is seated.\n\n'+final+'\n'
    result=parse_with_recovery(request_packet,raw,make_profile(family,True))
    assert result['status']=='ok' and result['raw']==raw
    assert result['answer']['request_id']==request_packet['request_id']
    assert result['normalizations'][0]=='missing_reasoning_close_before_final_json'
    assert raw[result['recovery']['final_start_character']:].strip()==final

@pytest.mark.parametrize('raw',[
    'Prose\n'+payload(),
    '<reasoning>\n'+payload(),
    '<reasoning>reason\n'+payload()+' trailing',
    '<reasoning>reason\n'+payload()+'\n'+payload(),
    '<reasoning>reason {"answer":"true"}\n'+payload(),
    '<reasoning><reasoning>reason\n'+payload(),
    '<reasoning>reason</think>\n'+payload(),
    '<reasoning>reason\n'+payload(evidence=['F2']),
    '<reasoning>reason\n'+payload(door_observable=False),
    '<reasoning>reason\n'+payload()[:-1]+',"answer":"true"}',
    '<reasoning>reason\n```python\n'+payload()+'\n```',
    '<reasoning>reason\n{"answer":',
])
def test_ambiguous_or_invalid_is_not_repaired(request_packet,raw):
    assert parse_with_recovery(request_packet,raw,make_profile('qwen',True))['status']=='invalid'


def test_no_recovery_of_truncation_or_direct_prose(request_packet):
    raw='<reasoning>reason\n'+payload()
    assert parse_with_recovery(request_packet,raw,make_profile('qwen',True),'length')['status']=='invalid'
    assert parse_with_recovery(request_packet,raw,make_profile('qwen'))['status']=='invalid'


def test_complete_envelope_stays_strict(request_packet):
    raw='<reasoning>reason</reasoning>'+payload()
    result=parse_with_recovery(request_packet,raw,make_profile('qwen',True))
    assert result['status']=='ok' and 'recovery' not in result and result['raw']==raw

@pytest.mark.parametrize('family,opening',[('qwen','<reasoning>'),('cosmos','<think>')])
@pytest.mark.parametrize('recover',[False,True])
def test_host_recovery_policy_and_persisted_trace(request_packet,tmp_path,monkeypatch,family,opening,recover):
    from video_workbench.verifiers.adapter import verify
    from video_workbench.verifiers.profiles import profile_hash
    from video_workbench.verifiers.recovery import RECOVERY_VERSION
    model=tmp_path/'model';model.mkdir();(model/'config.json').write_text('{}')
    profile=make_profile(family,True)
    raw=opening+'Visible door is seated.\n'+payload()
    def fake_supervise(command,*args):
        record=dict(request_id=request_packet['request_id'],raw=raw,profile=profile,
                    profile_sha256=profile_hash(profile),finish_reason='stop')
        Path(command[5]).write_text(json.dumps(record))
        return dict(status='ok')
    monkeypatch.setattr('video_workbench.verifiers.adapter.supervise',fake_supervise)
    result=verify(request_packet,model,tmp_path/'run',profile=profile,**({} if recover else {'recover_missing_close':False}))
    assert result['status']==('ok' if recover else 'invalid')
    assert result['validation_policy']==(RECOVERY_VERSION if recover else 'strict-reasoning-envelope-v1')
    assert result['raw']==result['runtime']['raw']==raw
    assert json.loads((tmp_path/'run/result.json').read_text())==result
    if recover:
        assert result['answer']['request_id']==request_packet['request_id']
        assert result['recovery']['missing_token']==('</reasoning>' if family=='qwen' else '</think>')
    else:
        assert 'recovery' not in result
