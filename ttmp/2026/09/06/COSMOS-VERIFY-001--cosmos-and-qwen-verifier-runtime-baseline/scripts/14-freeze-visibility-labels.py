"""Record assistant RGB review before prompt selection or model inference."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
from video_workbench.rules.evaluate import digest
from video_workbench.verifiers.visibility import prompt
root=Path(__file__).resolve().parents[1];out=root/'various/visibility-v2';rows=json.loads((out/'candidates.json').read_text())
labels={
'dv-0a0732aef26f3d73':['false','false','false','false','true','true'],
'dv-554891a30ac02c19':['unknown','unknown','unknown','unknown','true','true'],
'dv-0d6f76e6e85792a3':['false','false','false','false','true','true'],
'dv-ab93c9c80442cb4a':['false','false','unknown','unknown','unknown','unknown']}
counts={};cases=[]
for s in rows:
 eid=s['episode_id'];i=counts.get(eid,0);counts[eid]=i+1;label=labels[eid][i]
 rationale={'false':'Visible door panel is seated against the appliance frame; its surface and boundary can be inspected.','true':'Door is visibly displaced from its closed position, exposing an opening or the interior.','unknown':'Door cannot be reliably inspected: narrow side-view at small pixel extent or person covering its state-bearing surface.'}[label]
 t=s['pts_us'];r=dict(episode_id=eid,entity_id=s['entity_id'],entity_label=s['entity_class'],property='door_open',question=f"Is the {s['entity_class']} door visibly open?",event_us=t,allowed_start_us=t,allowed_end_us=t+1,as_of_us=t+250000,frames=[dict(id=s['id'],episode_id=eid,entity_id=s['entity_id'],pts_us=t,available_us=t,path=str(Path(s['image']).absolute()),sha256=s['image_sha256'])],max_output_tokens=384,deadline_ms=60000);r['request_id']=digest(r)
 cases.append(dict(source=s,request=r,expected=label,reviewer='codex-assistant-rgb-review',rationale=rationale))
protocol=dict(cases=cases,prompts={v:prompt(cases[0]['request'],v) for v in ['direct','visibility']},selection='Choose one shared variant on development using correct_count minus unsupported_known_on_unknown; ties prefer direct. No test output inspected before selection.',limitations='Fresh source frames/episodes relative to prior verifier sweep, not a new independent world. Microwave development/test share apartment and action family with different views. Conservative fresh side-view visibility rubric. Assistant review, not human ground truth.')
p=out/'protocol.json'
if p.exists():raise ValueError('do not overwrite frozen labels')
p.write_text(json.dumps(protocol,indent=2)+'\n')
# Annotated report panels are separate from model input images; no markings are sent.
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',20)
examples=[cases[0],cases[4],cases[18+2],cases[6]]
for k,c in enumerate(examples):
 canvas=Image.new('RGB',(960,660),'white');canvas.paste(Image.open(c['request']['frames'][0]['path']),(0,50));d=ImageDraw.Draw(canvas)
 d.text((20,15),c['expected'].upper()+' | '+c['source']['entity_class'],font=font,fill='black')
 import textwrap
 d.multiline_text((20,550),'\n'.join(textwrap.wrap(c['rationale'],72)),font=font,fill='black',spacing=6)
 d.text((20,630),c['source']['id'],font=font,fill='black');canvas.save(out/f'example-{k}-{c["expected"]}.png')
print('frozen',len(cases),'reviewed cases')
