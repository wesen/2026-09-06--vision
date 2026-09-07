"""Freeze all existing development/test reviewed point-state cases, without prompt tuning."""
from pathlib import Path
import json
from video_workbench.registry import file_hash
from video_workbench.rules.evaluate import digest
from video_workbench.verifiers.contracts import validate_request
root=Path(__file__).resolve().parents[1];out=root/'various/rerun';out.mkdir(exist_ok=True)
src=Path('output/state-workbench/review-v2/samples.json');lab=Path('output/state-workbench/run-v2/labels.json')
labels={x['sample_id']:x for x in json.loads(lab.read_text())};cases=[]
for s in json.loads(src.read_text()):
 if s['split'] not in ['development','test']:continue
 l=labels[s['sample_id']];t=s['sample_us']
 assert file_hash(s['image'])==s['image_sha256']
 r=dict(episode_id=s['episode_id'],entity_id=s['entity_id'],entity_label=s['entity_class'],property='door_open',question=f"Is the {s['entity_class']} door visibly open in the approved frame? Answer unknown if obscured or not identifiable.",event_us=t,allowed_start_us=t,allowed_end_us=t+1,as_of_us=t+250000,frames=[dict(id=s['sample_id'],episode_id=s['episode_id'],entity_id=s['entity_id'],pts_us=t,available_us=t,path=str(Path(s['image']).absolute()),sha256=s['image_sha256'])],max_output_tokens=256,deadline_ms=60000)
 r['request_id']=digest(r);validate_request(r)
 cases.append(dict(sample_id=s['sample_id'],split=s['split'],expected='unknown' if l['value'] is None else str(l['value']).lower(),label=l,request=r))
protocol=dict(samples_sha256=file_hash(src),labels_sha256=file_hash(lab),cases=cases,selection='All existing development/test reviewed RGB point-state frames; no prompt tuning; splits reported separately',limitation='Previously reviewed small within-scene corpus, repeated frames per episode, appliance and split confounded; no independent-frame significance claim.')
p=out/'protocol.json'
if p.exists():assert json.loads(p.read_text())==protocol
else:p.write_text(json.dumps(protocol,indent=2)+'\n')
print('frozen cases',len(cases))
