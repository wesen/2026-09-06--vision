"""One focused request; optional separate verifier-conditioned evaluation.

No autonomous retry, retrieval loop, observation replacement, or live model call.
"""
from dataclasses import replace
from video_workbench.temporal.store import Observation
from video_workbench.verifiers.contracts import validate_request,parse_answer
from .evaluate import digest,evaluate,integer


def plan_request(rule,decision,event,frames,entity_label):
    if decision['rule_sha256']!=digest(rule):raise ValueError('decision/rule mismatch')
    if decision['status']!='UNKNOWN':return {'status':'not_needed','reason':'decision_already_known'}
    if rule['op']!='state_at_event' or decision['reason'] not in ('source_unknown','no_exact_state_sample','disagreeing_samples'):
        return {'status':'unavailable','reason':'uncertainty_not_resolved_by_point_state_verifier'}
    if event is None:return {'status':'unavailable','reason':'trigger_missing'}
    event.validate()
    if event.id!=rule['event_id'] or event.episode_id!=decision['episode_id'] or event.entity_id!=decision['entity_id'] or event.stream_id!=rule['event_stream'] or event.lo_us!=event.hi_us or event.committed_us>decision['as_of_us']:raise ValueError('unusable bound trigger')
    if not frames:return {'status':'unavailable','reason':'no_approved_exact_frame'}
    request={'episode_id':decision['episode_id'],'entity_id':decision['entity_id'],'entity_label':entity_label,'property':rule['property'],
             'question':f'Is the {entity_label} door visibly open in the approved frame? Answer unknown if obscured or not identifiable.',
             'event_us':event.lo_us,'allowed_start_us':event.lo_us,'allowed_end_us':event.lo_us+1,'as_of_us':decision['as_of_us'],
             'frames':frames,'max_output_tokens':256,'deadline_ms':60000}
    request['request_id']=digest(request);validate_request(request)
    return {'status':'ready','request':request,'source_evaluation_id':decision['evaluation_id']}


def evaluate_answer(rule,baseline,event,request,raw,run_id,producer,completed_us):
    if not integer(completed_us) or completed_us<request['as_of_us']:raise ValueError('verifier result cannot be backdated')
    if request['episode_id']!=baseline['episode_id'] or request['entity_id']!=baseline['entity_id'] or request['event_us']!=event.lo_us or baseline['rule_sha256']!=digest(rule):raise ValueError('answer evaluation binding mismatch')
    result=parse_answer(request,raw)
    if result['status']!='ok':return dict(result,source_evaluation_id=baseline['evaluation_id'])
    answer=result['answer'];stream='verifier/'+producer
    # Independent comparison condition, not an instruction to discard baseline evidence.
    observation=Observation(digest({'request':request['request_id'],'producer':producer,'raw':raw,'completed_us':completed_us}),run_id,stream,baseline['episode_id'],baseline['entity_id'],rule['property'],
                            {'true':True,'false':False,'unknown':None}[answer['answer']],request['event_us'],completed_us,completed_us,
                            tuple(answer['evidence_ids'] or [f['id'] for f in request['frames']]),producer,'visual-verifier/'+producer,'causal','verifier_unknown' if answer['answer']=='unknown' else None).validate()
    conditioned_rule=dict(rule,state_stream=stream)
    decision=evaluate(conditioned_rule,baseline['episode_id'],baseline['entity_id'],[event],[observation],as_of_us=completed_us)
    return {'status':'ok','condition':'separate_verifier_evidence','source_evaluation_id':baseline['evaluation_id'],
            'request_id':request['request_id'],'observation':observation,'decision':decision,'model_citations':answer['evidence_ids'],'raw':raw}
