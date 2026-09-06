"""Visualize actual feature end times and weak labels for every episode."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
rows=json.load(open('output/temporal-v1/dataset/inputs.json'));labels={l['sample_id']:l for l in json.load(open('output/temporal-v1/dataset/weak-labels.json'))}
classes=json.load(open('output/temporal-v1/dataset/manifest.json'))['classes'];colors=['#c0392b','#8e44ad','#27ae60','#d35400','#2980b9','#16a085','#f39c12','#34495e','#e84393','#7f8c8d']
groups={}
for r in rows:groups.setdefault((r['split'],r['episode_id']),[]).append(r)
canvas=Image.new('RGB',(1200,120+len(groups)*23),'white');d=ImageDraw.Draw(canvas);maximum=max(r['end_us'] for r in rows)
d.text((10,8),'Dense trailing feature grid: weak program labels, not reviewed boundaries',fill='black')
for i,c in enumerate(classes):d.rectangle((10+i*115,30,20+i*115,40),fill=colors[i]);d.text((24+i*115,29),c,fill='black')
d.text((10,53),'Gray ticks = unlabeled boundary/gap. Tick position = feature end / offline availability.',fill='black')
for i,((split,eid),rr) in enumerate(sorted(groups.items())):
 y=85+i*23;d.text((5,y),split[:3]+' '+eid,fill='black');d.line((230,y+6,1180,y+6),fill='#dddddd')
 for r in rr:
  x=230+int(r['end_us']/maximum*950);l=labels[r['sample_id']];color=colors[classes.index(l['action'])] if l['label_mask'] else '#bbbbbb';d.rectangle((x-2,y,x+2,y+13),fill=color)
d.text((230,90+len(groups)*23),'0 seconds',fill='black');d.text((1080,90+len(groups)*23),f'{maximum/1e6:.1f} seconds',fill='black')
canvas.save(root/'various/dense-plan-v1/weak-grid.png')
