"""Compare immutable evidence, inspect frozen action outputs, and evaluate point rules."""
from pathlib import Path
import json
from pydantic import BaseModel,ConfigDict,Field
from typing import Literal
from video_workbench.registry import file_hash
from video_workbench.rules.evaluate import Event,evaluate,digest
from video_workbench.temporal.store import Observation

class Review(BaseModel):
    model_config=ConfigDict(extra='forbid')
    verdict: Literal['correct','incorrect','unjudgeable']
    note: str=Field(min_length=1,max_length=4000)

class RuleRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    event_us: int=Field(ge=0)
    expected_open: bool=False

def compare(a,b):
    differences=[]
    for key in ('episode_id','start_us','end_us','fps','crop','component','model','target','reasoning','max_tokens','query','window_seconds','stride_seconds','confidence','iou','image_size','classes'):
        av=a['request']['options'][key];bv=b['request']['options'][key]
        if av!=bv:differences.append(dict(field=key,a=av,b=bv))
    def inputs(run):
        e=run['request']['evidence']
        return dict(source_sha256=e['source']['video_sha256'],split=e['source']['split'],frames=[(f['pts_us'],f['sha256'],f['crop_xyxy']) for f in e['frames']])
    same=inputs(a)==inputs(b)
    fa=a.get('result',{}).get('feature_space_id');fb=b.get('result',{}).get('feature_space_id')
    return dict(a=a['run_id'],b=b['run_id'],same_evidence=same,differences=differences,
                same_feature_space=bool(fa and fb and fa==fb),
                interpretation='Matched pixels and timestamps; configuration differences are listed.' if same else 'Inputs differ. Treat this as an input intervention, not a controlled model-only comparison.',
                feature_note='Compare rankings separately; do not combine or subtract vectors from different feature spaces.' if fa and fb and fa!=fb else None)

def point_rule(run,request):
    result=run.get('result',{})
    if result.get('kind') not in ('reasoning','states'):raise ValueError('select a completed reasoning/state run')
    o=run['request']['options'];eid=o['episode_id'];entity=o['target'];horizon=max(o['end_us'],request.event_us)
    event=Event('user-point',eid,entity,'manual','selected_time',request.event_us,request.event_us,horizon,horizon)
    rule=dict(schema_version=1,rule_id='lab-door-state-at-point',op='state_at_event',event_stream='manual',event_id=event.id,state_stream='lab-state',property='door_open',expected=request.expected_open)
    observations=[]
    for i,r in enumerate(result['records']):
        value={'open':True,'closed':False,'unknown':None}[r['state']]
        observations.append(Observation(f'lab-{i}',run['run_id'],'lab-state',eid,entity,'door_open',value,r['pts_us'],horizon,horizon,
                                        (r['frame']['id'],),o['model'],'verifier/'+o['model'],'offline', 'verifier_unknown' if value is None else None))
    # Observation mode is an existing closed enum; offline lab computation still
    # uses causal-form clocks with all inputs explicitly available at this horizon.
    from dataclasses import replace
    observations=[replace(o,mode='causal') for o in observations]
    return dict(rule=rule,decision=evaluate(rule,eid,entity,[event],observations,as_of_us=horizon),
                scope='Offline exact-point experiment; user-selected trigger, not a detected event or streaming latency measurement.')

def action_artifacts(root,source,start_us,end_us):
    root=Path(root);dataset=root/'output/temporal-v1/dataset';inputs=json.loads((dataset/'inputs.json').read_text())
    windows=[r for r in inputs if r['episode_id']==source['original_episode_id'] and r['video_sha256']==source['video_sha256'] and start_us<=r['start_us'] and r['end_us']<=end_us]
    if not windows:return dict(mode='saved_results_only',records=[],reason='No frozen action windows fully contained in this selection with the same source hash. Select a paired-actions-v4 recording and a wider range.')
    results=[]
    for mode,path,fm_path in [('native FP32 ridge','output/temporal-native-fp32-v1/ridge/results.json','output/temporal-native-fp32-v1/features/manifest.json'),('pooled 4-bit ridge','output/temporal-v1/linear-v1/results.json','output/temporal-v1/pooled-features/manifest.json')]:
        p=root/path;model=json.loads(p.read_text());fm=root/fm_path
        if file_hash(fm)!=model['features_manifest_sha256']:raise ValueError('action feature manifest changed')
        if file_hash(dataset/'inputs.json')!=model['inputs_sha256']:raise ValueError('frozen action inputs changed')
        row=model['metrics'][source['split']]['episodes'].get(source['original_episode_id'])
        if row is None:continue
        by_end=dict(zip(row['end_us'],row['predictions']))
        for w in windows:
            label=by_end.get(w['end_us'],-1)
            results.append(dict(model=mode,start_us=w['start_us'],end_us=w['end_us'],pts_us=w['pts_us'],prediction=model['classes'][label] if label>=0 else 'UNKNOWN',sample_id=w['sample_id'],feature_space_id=model['model']['space'],checkpoint_sha256=file_hash(p)))
    return dict(mode='saved_results_only',records=results,scope='Frozen ridge action predictions, not newly executed inference. Window inputs and source hashes are matched; weak labels are not included in this response.')
