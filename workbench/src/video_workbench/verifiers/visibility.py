"""Visibility-aware model payload; request identity belongs to the host."""
import json
from .contracts import validate_request, parse_answer
from .normalization import unwrap_json_fence

SCHEMA_VERSION = 'visible-door-v2'


def prompt(request, variant='visibility'):
    validate_request(request)
    return prompt_text(request['entity_label'], variant)


def prompt_text(target, variant='visibility'):
    if variant not in ('direct', 'visibility'):
        raise ValueError('unsupported prompt variant')
    task = f"Inspect only the supplied image. Target appliance: {target}. Is its door open?"
    if variant == 'visibility':
        task += (' First establish whether you can identify the target and directly see enough of its door to determine its state.'
                 ' Closed means a visible door seated against its frame, not merely no visible opening.'
                 ' Open means a visible gap or displaced door exposing the opening.'
                 ' If a person blocks the door, the target is too small, outside the image, or its state cannot be distinguished, set door_observable=false and answer=unknown.'
                 ' Never infer closed just because you cannot see an open door. Do not infer state from what a person is doing.')
    return task + '\nImage reference: F1. Return one JSON object, no prose, with these exact fields: ' + json.dumps({
        'target_identified': True, 'door_observable': True, 'answer': 'true|false|unknown',
        'evidence': ['F1'], 'rationale': 'brief description of directly visible evidence'}) + '\nChoose one answer enum. No IDs or confidence scores are requested.'


def parse_visibility(request, raw):
    """Validate model content, then bind immutable host IDs and approved citations."""
    validate_request(request)
    changes=[]
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('duplicate JSON key')
            result[key]=value
        return result
    try:
        if not isinstance(raw,str) or len(raw)>16000:raise ValueError('response size invalid')
        payload,changes=unwrap_json_fence(raw)
        value=json.loads(payload,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
        if not isinstance(value,dict) or set(value)!={'target_identified','door_observable','answer','evidence','rationale'}:raise ValueError('visibility response schema')
        if type(value['target_identified']) is not bool or type(value['door_observable']) is not bool:raise ValueError('visibility flags must be booleans')
        if value['answer'] not in ('true','false','unknown'):raise ValueError('invalid answer')
        if not value['target_identified'] and value['door_observable']:raise ValueError('unidentified target cannot be observable')
        if value['answer']!='unknown' and not (value['target_identified'] and value['door_observable']):raise ValueError('known answer requires visible identified target')
        if not isinstance(value['evidence'],list) or any(e!='F1' for e in value['evidence']) or len(value['evidence'])>1:raise ValueError('unapproved image reference')
        if value['answer']!='unknown' and not value['evidence']:raise ValueError('known answer requires citation')
        if not isinstance(value['rationale'],str) or not value['rationale'].strip() or len(value['rationale'])>2000:raise ValueError('invalid rationale')
        bound=dict(request_id=request['request_id'],entity_id=request['entity_id'],answer=value['answer'],evidence_ids=[request['frames'][0]['id']] if value['evidence'] else [],rationale=value['rationale'])
        checked=parse_answer(request,json.dumps(bound))
        if checked['status']!='ok':raise ValueError(checked['reason'])
    except (ValueError,TypeError) as exc:
        return dict(status='invalid',reason=str(exc),raw=raw,normalizations=changes,schema_version=SCHEMA_VERSION)
    return dict(status='ok',answer=bound,visibility={k:value[k] for k in ('target_identified','door_observable')},raw=raw,normalizations=changes,schema_version=SCHEMA_VERSION)


REASONING_INSTRUCTION = """Reason step by step using only the supplied image. Identify the appliance and its door surface. Examine visible detail and occlusion. Compare direct evidence of an open door with direct evidence of a seated closed door. Choose unknown if neither is established. Do not infer state from the person's activity or an assumed history.
Write your reasoning inside <think> and </think>.
Immediately after </think>, return exactly one final JSON object with the specified visibility fields. Put no additional prose after the final JSON."""


def experiment_prompt(request, profile):
    from .profiles import validate_profile
    validate_profile(profile, request)
    validate_request(request)
    return experiment_prompt_text(request['entity_label'], profile)


def experiment_prompt_text(target, profile):
    from .profiles import validate_profile
    validate_profile(profile)
    text = prompt_text(target, 'visibility')
    if profile['prompt_style'] == 'reasoning':
        text = text.replace('Return one JSON object, no prose, with these exact fields:',
                            'Your final answer must be one JSON object with these exact fields:')
        instruction = REASONING_INSTRUCTION
        if profile['model_family'] == 'qwen':
            instruction = instruction.replace('<think>', '<reasoning>').replace('</think>', '</reasoning>')
        text += '\n' + instruction
    return text


def parse_experiment(request, raw, profile, finish_reason=None):
    from .profiles import validate_profile, CONTRACT_VERSION
    validate_profile(profile, request)
    final = None
    try:
        if not isinstance(raw, str) or len(raw.encode('utf-8')) > 256 * 1024:
            raise ValueError('raw response exceeds UTF-8 size limit')
        if finish_reason == 'length':
            raise ValueError('generation truncated at token limit')
        final = raw
        if profile['prompt_style'] == 'reasoning':
            value = raw.strip()
            opening, closing = ('<reasoning>', '</reasoning>') if profile['model_family']=='qwen' else ('<think>', '</think>')
            if not value.startswith(opening) or value.count(opening) != 1 or value.count(closing) != 1:
                raise ValueError('incomplete or repeated reasoning envelope')
            body, final = value[len(opening):].split(closing, 1)
            if not body.strip() or not final.strip():
                raise ValueError('empty reasoning or missing final answer')
        checked = parse_visibility(request, final)
        return dict(checked, raw=raw, final_text=final, schema_version=CONTRACT_VERSION,
                    output_style=profile['prompt_style'])
    except (ValueError, UnicodeError) as exc:
        return dict(status='invalid', reason=str(exc), raw=raw, final_text=final,
                    normalizations=[], schema_version=CONTRACT_VERSION, output_style=profile['prompt_style'])
