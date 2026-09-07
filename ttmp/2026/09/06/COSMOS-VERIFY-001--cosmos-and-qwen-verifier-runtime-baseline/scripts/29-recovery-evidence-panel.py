"""Visualize an actual strict failure and its traced recovery; not model input."""
from pathlib import Path
import json,textwrap
from PIL import Image,ImageDraw,ImageFont
r=Path(__file__).resolve().parents[1];root=r/'various/reasoning-v3';protocol=json.loads((root/'protocol.json').read_text());cases={c['source']['id']:c for c in protocol['cases']}
rows=[json.loads(line) for line in (root/'recovery-replay/development-records.jsonl').read_text().splitlines()]
x=next(x for x in rows if 'recovery' in x['replayed'] and x['correct']);c=cases[x['original']['case_id']]
canvas=Image.new('RGB',(1280,1080),'white');d=ImageDraw.Draw(canvas);font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',17)
d.text((20,15),'ACTUAL DEVELOPMENT RESPONSE | missing closing tag recovery',font=font,fill='black')
canvas.paste(Image.open(c['request']['frames'][0]['path']),(20,55))
lines=['Reviewed state: '+c['expected'],'Strict status: '+x['original']['status'],'Strict reason:',x['original']['reason'],'Recovered answer: '+x['answer'],'Trace:',x['replayed']['normalizations'][0],'JSON values and raw response unchanged.']
y=65
for line in lines:
 for wrapped in textwrap.wrap(line,49):d.text((700,y),wrapped,font=font,fill='black');y+=27
 y+=10
d.text((20,565),'Original raw output (excerpt, including the missing close):',font=font,fill='black')
y=600
for line in x['replayed']['raw'].splitlines():
 for wrapped in textwrap.wrap(line,116) or ['']:
  if y>1030:break
  d.text((20,y),wrapped,font=font,fill='black');y+=24
canvas.save(root/'missing-close-recovery.png')
print('Rendered actual response',x['original']['profile_id'],x['original']['case_id'])
