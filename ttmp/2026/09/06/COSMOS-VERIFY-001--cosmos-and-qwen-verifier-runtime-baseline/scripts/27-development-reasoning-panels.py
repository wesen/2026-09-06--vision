"""Render completed greedy development pairs; never used as model input."""
from pathlib import Path
import json,textwrap
from PIL import Image,ImageDraw,ImageFont
r=Path(__file__).resolve().parents[1];protocol=json.loads((r/'various/reasoning-v3/protocol.json').read_text());out=Path('output/verifier-reasoning-v3/development');dest=r/'various/reasoning-v3/development-panels';dest.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',17)
for family,seed in [('qwen',3407),('cosmos',1234)]:
 for label in ['false','true','unknown']:
  c=next(c for c in protocol['cases'] if c['source']['split']=='development' and c['expected']==label);cid=c['source']['id']
  paths=[out/f'{family}-{style}-G-{seed}'/cid/'result.json' for style in ['D','R']]
  if not all(p.exists() for p in paths):continue
  results=[json.loads(p.read_text()) for p in paths]
  canvas=Image.new('RGB',(1280,940),'white');draw=ImageDraw.Draw(canvas)
  draw.text((20,15),f'DEVELOPMENT ONLY | {family} | reviewed {label} | {cid}',font=font,fill='black')
  canvas.paste(Image.open(c['request']['frames'][0]['path']),(20,55))
  draw.multiline_text((700,70),'\n'.join(textwrap.wrap(c['review_rationale'],49)),font=font,fill='black',spacing=6)
  for i,result in enumerate(results):
   y=560+i*170;title='Direct greedy' if i==0 else 'Prompted reasoning, greedy';answer=result.get('answer',{}).get('answer',result['status'])
   draw.text((20,y),f'{title}: {answer} | {result["elapsed_seconds"]:.2f}s',font=font,fill='black')
   rationale=result.get('answer',{}).get('rationale',result.get('reason',''))
   draw.multiline_text((20,y+30),'\n'.join(textwrap.wrap('Model rationale: '+rationale,115)[:5]),font=font,fill='black',spacing=5)
  draw.text((20,915),'Same source image; explanations are model claims. Full raw outputs archived separately.',font=font,fill='black')
  canvas.save(dest/f'{family}-{label}.png')
print('Saved',len(list(dest.glob('*.png'))),'development comparison panels')
