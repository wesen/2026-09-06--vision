"""Freeze RGB labels and BOTH model protocols before development inference."""
from pathlib import Path
import json,collections,shutil
from video_workbench.verifiers.profiles import make_profile,profile_hash
from video_workbench.verifiers.visibility import experiment_prompt
from video_workbench.rules.evaluate import digest
from video_workbench.registry import file_hash
r=Path(__file__).resolve().parents[1];out=r/'various/reasoning-v3';sources=json.loads((out/'candidates.json').read_text())
labels={
'dv-31fd8bf573379ba5':['false']*5+['true']*3,
'dv-528d9a75133b1101':['false']*5,
'dv-c49ae32814f5899e':['unknown']*6,
'dv-503ac41c9f57746a':['false']*5,
'dv-dad43880b6994056':['false']*4+['true']*4,
'dv-50acf4cb570d5c06':['false']*5,
'dv-d065ae4a05eb0978':['false']*4+['unknown']*2,
'dv-d3ba7e1944d989fd':['false']*5}
counts=collections.Counter();cases=[]
for s in sources:
 i=counts[s['episode_id']];counts[s['episode_id']]+=1;label=labels[s['episode_id']][i];t=s['pts_us']
 reason={'false':'Visible door panel is seated against the appliance frame; inspectable surface and boundary.','true':'Visible door displacement or opening establishes open state.','unknown':'Door state is not distinguishable from the supplied image: small side-facing appliance or actor occlusion.'}[label]
 request=dict(episode_id=s['episode_id'],entity_id=s['entity_id'],entity_label=s['entity_class'],property='door_open',question='Is the target door visibly open?',event_us=t,allowed_start_us=t,allowed_end_us=t+1,as_of_us=t+250000,frames=[dict(id=s['id'],episode_id=s['episode_id'],entity_id=s['entity_id'],pts_us=t,available_us=t,path=str(Path(s['image']).resolve()),sha256=s['image_sha256'])],max_output_tokens=4096,deadline_ms=120000)
 request['request_id']=digest(request)
 cases.append(dict(source=s,request=request,expected=label,reviewer='codex-assistant-rgb-review',review_rationale=reason))
models={}
for family,name in [('qwen','qwen-8b-runtime-pins.json'),('cosmos','cosmos-8b-runtime-pins.json')]:
 pin=json.loads((r/'various'/name).read_text())[0]
 base=3407 if family=='qwen' else 1234;profiles=[]
 for reasoning,sampled in [(False,False),(True,False),(False,True),(True,True)]:
  for seed in range(base,base+(3 if sampled else 1)):
   p=make_profile(family,reasoning,sampled,seed);profiles.append(dict(profile=p,profile_sha256=profile_hash(p)))
 models[family]=dict(pin=pin,profiles=profiles)
code={}
for path in [*Path('workbench/src/video_workbench/verifiers').glob('*.py'),Path('workbench/src/video_workbench/rules/handoff.py')]:code[str(path)]=file_hash(path)
protocol=dict(version='reasoning-v3',cases=cases,models=models,code_sha256=code,
 prompts={family:{style:experiment_prompt(cases[0]['request'],make_profile(family,style=='reasoning')) for style in ['direct','reasoning']} for family in models},
 selection='Average correct-minus-unsupported indicator across seeds per case, then cases. Descending score; ties lower unsupported rate, lower median elapsed, direct then greedy. Choose control if no score gain over direct greedy.',
 test_policy='Both model selections must exist before any test run. Test each selected arm and direct greedy control; control only if selected is control. Sampled selections retain all three predefined seeds.',
 limitations='Assistant RGB review, not independent human ground truth. New episodes relative to prior verifier tests, same synthetic apartments and action families. Actual label imbalance; nearby open frames are correlated. Requested 8/8/8 mix unavailable in remaining episodes. Actor rendering artifacts present in a control episode.',
 label_counts={split:dict(collections.Counter(c['expected'] for c in cases if c['source']['split']==split)) for split in ['development','test']})
p=out/'protocol.json'
if p.exists():raise ValueError('refuse to overwrite frozen protocol')
p.write_text(json.dumps(protocol,indent=2)+'\n')
# Archive both pilot attempts, retaining failures as evidence.
for attempt in ['pilot','pilot-2']:
 dest=out/attempt;dest.mkdir(exist_ok=True)
 for path in Path('output/verifier-reasoning-v3',attempt).rglob('*.json'):
  target=dest/path.relative_to(Path('output/verifier-reasoning-v3',attempt));target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
print(json.dumps(dict(protocol_sha256=file_hash(p),counts=protocol['label_counts'])))
