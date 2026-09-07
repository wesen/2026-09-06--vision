"""One selected-profile live RULES handoff per model after test completion."""
from pathlib import Path
import json,copy
from dataclasses import asdict,is_dataclass
from video_workbench.rules.evaluate import Event,evaluate
from video_workbench.rules.handoff import investigate
from video_workbench.registry import file_hash
r=Path(__file__).resolve().parents[1];out=Path('output/verifier-reasoning-v3');protocol_path=r/'various/reasoning-v3/protocol.json';protocol=json.loads(protocol_path.read_text())
selection=json.loads((out/'selection.json').read_text());test=json.loads((out/'test-results.json').read_text())
assert selection['protocol_sha256']==test['protocol_sha256']==file_hash(protocol_path)
case=next(c for c in protocol['cases'] if c['source']['split']=='development' and c['expected']=='false');p=case['request'];records=[]
for family,model in protocol['models'].items():
 chosen=selection['models'][family]['selected']
 expected={(e['profile']['id'],c['source']['id']) for e in model['profiles'] for c in protocol['cases'] if c['source']['split']=='test' and (('R' if e['profile']['prompt_style']=='reasoning' else 'D')+'-'+('S' if e['profile']['temperature'] else 'G')) in {'D-G',chosen}}
 actual={(x['profile_id'],x['case_id']) for x in test['rows'] if x['family']==family};assert actual==expected, 'incomplete test comparison'
 profile=next(e['profile'] for e in model['profiles'] if (('R' if e['profile']['prompt_style']=='reasoning' else 'D')+'-'+('S' if e['profile']['temperature'] else 'G'))==chosen)
 rule=dict(schema_version=1,rule_id='closed-at-sample',op='state_at_event',event_id='sample',event_stream='sample-events',state_stream='state',property='door_open',expected=False)
 event=Event('sample',p['episode_id'],p['entity_id'],'sample-events','sample',p['event_us'],p['event_us'],p['event_us'],p['event_us'])
 baseline=evaluate(rule,p['episode_id'],p['entity_id'],events=[event],as_of_us=p['as_of_us']);before=copy.deepcopy(baseline)
 result=investigate(rule,baseline,event,p['frames'],p['entity_label'],model['pin']['local_path'],out/'live-rules'/family,'reasoning-v3-live',family+'-8b',profile=profile)
 assert baseline==before and baseline['status']=='UNKNOWN'
 record=dict(family=family,profile=profile,fixture='Controlled frame-sample event, not measured departure detection',baseline=baseline,baseline_unchanged=True,result=result)
 records.append(record)
 print(json.dumps(dict(family=family,status=result['status'],conditioned=result.get('conditioned',{}).get('decision',{}).get('status'))),flush=True)
(r/'various/reasoning-v3/live-rules.json').write_text(json.dumps(records,indent=2,default=lambda o:asdict(o) if is_dataclass(o) else str(o))+'\n')
