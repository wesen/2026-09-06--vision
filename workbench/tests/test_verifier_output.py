"""Output boundary smoke: normalize wrappers without relaxing semantic checks."""
import json
from pathlib import Path
import pytest
from video_workbench.verifiers.contracts import parse_answer


@pytest.fixture
def request_packet():
    root=Path(__file__).resolve().parents[2]
    p=next((root/'ttmp/2026/09/06').glob('COSMOS-VERIFY-001--*'))/'various/v1-image-gate/request.json'
    return json.loads(p.read_text())


def answer(request):
    return dict(request_id=request['request_id'],entity_id=request['entity_id'],answer='false',evidence_ids=[request['frames'][0]['id']],rationale='Door appears closed; literal ``` in text is preserved.')


@pytest.mark.parametrize('opening',['```json','```'])
def test_outer_fence_is_traced_and_raw_is_preserved(request_packet,opening):
    value=answer(request_packet);raw=' \r\n'+opening+'\r\n'+json.dumps(value)+'\r\n```\r\n '
    result=parse_answer(request_packet,raw)
    assert result['status']=='ok' and result['answer']==value
    assert result['raw']==raw and result['normalizations']==['markdown_fence_wrapper']
    assert parse_answer(request_packet,raw,allow_markdown_fence=False)['status']=='invalid'


@pytest.mark.parametrize('kind',['prose','two_blocks','truncated','duplicate_key','nonfinite','wrong_id','citation','language'])
def test_fence_does_not_make_invalid_payload_acceptable(request_packet,kind):
    value=answer(request_packet)
    if kind=='wrong_id':value['request_id']='wrong'
    if kind=='citation':value['evidence_ids']=['invented']
    body=json.dumps(value)
    if kind=='duplicate_key':body=body[:-1]+',"answer":"true"}'
    if kind=='nonfinite':body=body.replace('"false"','NaN')
    if kind=='truncated':body=body[:-1]
    raw='```json\n'+body+'\n```'
    if kind=='prose':raw='Here is the answer:\n'+raw
    if kind=='two_blocks':raw+='\n'+raw
    if kind=='language':raw=raw.replace('```json','```python',1)
    assert parse_answer(request_packet,raw)['status']=='invalid'


def test_plain_json_still_works(request_packet):
    result=parse_answer(request_packet,json.dumps(answer(request_packet)))
    assert result['status']=='ok' and result['normalizations']==[]
