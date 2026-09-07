"""One real frame-sample handoff, not a measured departure-event detector."""
from pathlib import Path
import json, copy
from dataclasses import asdict,is_dataclass
from video_workbench.rules.evaluate import Event,evaluate
from video_workbench.rules.handoff import investigate
r=Path(__file__).resolve().parents[1]
p=json.loads((r/'various/visibility-v2/protocol.json').read_text())['cases'][0]['request']
rule=dict(schema_version=1,rule_id='closed-at-sample',op='state_at_event',event_id='sample',event_stream='sample-events',state_stream='state',property='door_open',expected=False)
event=Event('sample',p['episode_id'],p['entity_id'],'sample-events','sample',p['event_us'],p['event_us'],p['event_us'],p['event_us'])
baseline=evaluate(rule,p['episode_id'],p['entity_id'],events=[event],as_of_us=p['as_of_us']);before=copy.deepcopy(baseline)
variant=json.loads(Path('output/verifier-visibility-v2/selection.json').read_text())['variant']
result=investigate(rule,baseline,event,p['frames'],p['entity_label'],'output/models/cosmos-reason2-8b-8bit-local','output/verifier-visibility-v2/live-rules','visibility-v2-live','cosmos-8b',variant=variant)
assert baseline==before and baseline['status']=='UNKNOWN'
assert result['status']=='ok'
record=dict(fixture='Controlled frame-sample trigger, not real departure detection',rule=rule,baseline=baseline,baseline_unchanged=baseline==before,result=result)
(r/'various/visibility-v2/live-rules.json').write_text(json.dumps(record,indent=2,default=lambda o:asdict(o) if is_dataclass(o) else str(o))+'\n')
print(json.dumps(dict(status=result['status'],baseline=baseline['status'],conditioned=result['conditioned']['decision']['status'])))
