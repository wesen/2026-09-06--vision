"""Report strict answer outcomes against frozen reviewed RGB labels, by split."""
from pathlib import Path
import collections
import argparse
import json
import statistics
import shutil
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];out=root/'various/rerun';source=Path('output/verifier-rerun-v1')
parser=argparse.ArgumentParser();parser.add_argument('--normalize-fences',action='store_true');args=parser.parse_args()
protocol=json.loads((out/'protocol.json').read_text())
if args.normalize_fences:
 from video_workbench.verifiers.contracts import parse_answer
 out=out/'normalized';out.mkdir(exist_ok=True)
manifest=json.loads((source/'manifest.json').read_text());summary=[];raw=[]
assert len(manifest)==4 and all(m['completed']==48 and m['status']=='finished' for m in manifest)
for m in manifest:
 name=Path(m['pin']['local_path']).name
 for split in ['development','test']:
  rows=[]
  for c in protocol['cases']:
   if c['split']!=split:continue
   d=json.loads((source/name/(c['sample_id']+'.json')).read_text())
   assert d['request_id']==c['request']['request_id'] and d['image_sha256']==c['request']['frames'][0]['sha256']
   if args.normalize_fences:
    d['strict_parsed']=d['parsed'];d['parsed']=parse_answer(c['request'],d['raw'])
   predicted=d['parsed']['answer']['answer'] if d['parsed']['status']=='ok' else 'invalid'
   error_kind=None
   if predicted=='invalid':
    error_kind=d['parsed']['reason']
    text=d['raw'].strip()
    if not d['parsed'].get('normalizations') and text.startswith('```json\n') and text.endswith('\n```'):
     try:json.loads(text[8:-4]);error_kind='Markdown fence around syntactically valid JSON'
     except ValueError:pass
   row=dict(model=name,split=split,sample_id=c['sample_id'],expected=c['expected'],predicted=predicted,error_kind=error_kind,normalizations=d['parsed'].get('normalizations',[]),correct=predicted==c['expected'],result=d)
   rows.append(row);raw.append(row)
  known=[r for r in rows if r['expected']!='unknown'];unknown=[r for r in rows if r['expected']=='unknown'];valid=[r for r in rows if r['predicted']!='invalid']
  summary.append(dict(model=name,split=split,n=len(rows),schema_valid=len(valid),invalid=len(rows)-len(valid),correct=sum(r['correct'] for r in rows),known_n=len(known),known_correct=sum(r['correct'] for r in known),unknown_n=len(unknown),unknown_correct=sum(r['correct'] for r in unknown),abstained=sum(r['predicted']=='unknown' for r in rows),valid_answer_accuracy=sum(r['correct'] for r in valid)/len(valid) if valid else None,median_generation_seconds=statistics.median(r['result']['generation_seconds'] for r in rows),peak_mlx_gb=max(r['result']['peak_mlx_memory_bytes'] for r in rows)/1e9,normalized_count=sum(bool(r['normalizations']) for r in rows),errors=dict(collections.Counter(r['error_kind'] for r in rows if r['error_kind'])),confusion=dict(collections.Counter(r['expected']+' -> '+r['predicted'] for r in rows))))
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'raw-results.json').write_text(json.dumps(raw,indent=2)+'\n');shutil.copyfile(source/'manifest.json',out/'runtime-manifest.json')
native=json.loads(Path('output/temporal-native-fp32-rerun-v1/comparison/results.json').read_text());old=json.loads(Path('output/temporal-native-fp32-v1/comparison/results.json').read_text())
assert native['ridge']==old['ridge'] and native['tcn']==old['tcn'],'native rerun differs'
shutil.copyfile('output/temporal-native-fp32-rerun-v1/comparison/results.json',out/'native-temporal-results.json')
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',18)
canvas=Image.new('RGB',(1600,650),'white');draw=ImageDraw.Draw(canvas)
draw.text((25,20),'After JSON fence normalization | valid-answer correctness' if args.normalize_fences else 'Frozen reviewed frame evaluation | strict valid-answer correctness',font=font,fill='black')
for i,s in enumerate(summary):
 y=70+i*65
 draw.text((25,y),f"{s['model']:39} {s['split']:11}",font=font,fill='black')
 draw.rectangle((700,y,700+s['correct']/s['n']*500,y+28),fill='#245b82')
 draw.text((1220,y),f"{s['correct']}/{s['n']} | invalid {s['invalid']}",font=font,fill='black')
draw.text((25,605),'Development: fridge; test: microwave. Invalid outputs count as incorrect. No rationale-support score.',font=font,fill='black');canvas.save(out/'outcomes.png')
# Contact sheets retain all approved input pixels beside expected labels.
for split in ['development','test']:
 cases=[c for c in protocol['cases'] if c['split']==split];sheet=Image.new('RGB',(1600,1320),'white');d=ImageDraw.Draw(sheet)
 for i,c in enumerate(cases):
  x=(i%4)*400;y=(i//4)*220;im=Image.open(c['request']['frames'][0]['path']).convert('RGB');im.thumbnail((280,180));sheet.paste(im,(x,y))
  d.text((x,y+181),f"{i}: {c['expected']} {c['sample_id'][:8]}",font=font,fill='black')
 sheet.save(out/(split+'-reviewed-inputs.png'))
print(json.dumps(summary,indent=2))
