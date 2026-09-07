"""Shared RULES/VERIFY boundary. Valid citations do not prove factual support."""
import json
from video_workbench.rules.evaluate import digest,integer
from .normalization import unwrap_json_fence


def validate_request(request):
    fields={'request_id','episode_id','entity_id','entity_label','property','question','event_us','allowed_start_us','allowed_end_us','as_of_us','frames','max_output_tokens','deadline_ms'}
    if not isinstance(request,dict) or set(request)!=fields:raise ValueError('invalid request fields')
    for k in ('request_id','episode_id','entity_id','entity_label','property','question'):
        if not isinstance(request[k],str) or not request[k]:raise ValueError('request identity required')
    if request['property']!='door_open':raise ValueError('initial verifier supports door_open only')
    if not all(integer(request[k]) for k in ('event_us','allowed_start_us','allowed_end_us','as_of_us','max_output_tokens','deadline_ms')):raise ValueError('integer request clocks/limits required')
    if not request['allowed_start_us']<=request['event_us']<request['allowed_end_us'] or request['event_us']>request['as_of_us']:raise ValueError('request event outside horizon')
    if not 1<=request['max_output_tokens']<=512 or not 1<=request['deadline_ms']<=120000:raise ValueError('request exceeds runtime limits')
    frames=request['frames']
    if not isinstance(frames,list) or not 1<=len(frames)<=4:raise ValueError('one to four approved frames required')
    ids=[]
    for f in frames:
        if set(f)!={'id','episode_id','entity_id','pts_us','available_us','path','sha256'}:raise ValueError('invalid frame fields')
        if any(not isinstance(f[k],str) or not f[k] for k in ('id','episode_id','entity_id','path','sha256')):raise ValueError('invalid frame identity')
        if f['episode_id']!=request['episode_id'] or f['entity_id']!=request['entity_id']:raise ValueError('frame entity/episode mismatch')
        if not integer(f['pts_us']) or not integer(f['available_us']) or not request['allowed_start_us']<=f['pts_us']<request['allowed_end_us'] or not f['pts_us']<=f['available_us']<=request['as_of_us']:raise ValueError('frame outside evidence horizon')
        # Current point-state contract cannot infer the target from nearby frames.
        if f['pts_us']!=request['event_us']:raise ValueError('exact-time state evidence required')
        if len(f['sha256'])!=64 or any(c not in '0123456789abcdef' for c in f['sha256']):raise ValueError('invalid frame hash')
        ids.append(f['id'])
    if len(set(ids))!=len(ids):raise ValueError('duplicate packet frame ID')
    if request['request_id']!=digest({k:v for k,v in request.items() if k!='request_id'}):raise ValueError('request identity mismatch')
    return request


def parse_answer(request,raw,*,allow_markdown_fence=True):
    validate_request(request)
    def pairs(values):
        result={}
        for k,v in values:
            if k in result:raise ValueError('duplicate JSON key')
            result[k]=v
        return result
    normalizations=[]
    try:
        if not isinstance(raw,str) or len(raw)>16000:raise ValueError('response size invalid')
        payload,normalizations=unwrap_json_fence(raw) if allow_markdown_fence else (raw,[])
        value=json.loads(payload,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
        if not isinstance(value,dict) or set(value)!={'request_id','entity_id','answer','evidence_ids','rationale'}:raise ValueError('response schema')
        if value['request_id']!=request['request_id'] or value['entity_id']!=request['entity_id']:raise ValueError('response binding mismatch')
        if value['answer'] not in ('true','false','unknown'):raise ValueError('invalid answer')
        ids=value['evidence_ids'];approved={f['id'] for f in request['frames']}
        if not isinstance(ids,list) or any(not isinstance(i,str) or i not in approved for i in ids) or len(set(ids))!=len(ids):raise ValueError('invalid evidence citation')
        if value['answer']!='unknown' and not ids:raise ValueError('known answer requires citation')
        if not isinstance(value['rationale'],str) or len(value['rationale'])>2000:raise ValueError('invalid rationale')
    except (ValueError,TypeError) as exc:return {'status':'invalid','reason':str(exc),'raw':raw,'normalizations':normalizations}
    return {'status':'ok','answer':value,'raw':raw,'normalizations':normalizations}
