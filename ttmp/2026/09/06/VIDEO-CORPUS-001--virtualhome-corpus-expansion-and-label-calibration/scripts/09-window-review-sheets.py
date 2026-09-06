"""Sample every fixed-duration window at start/middle/end for the report."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path('output/virtualhome-corpus/diversity-v2');ticket=Path(__file__).resolve().parent.parent
rows=[json.loads(s) for s in (root/'windows-v1/labels.jsonl').read_text().splitlines()]
for scene,split in enumerate(('train','development','test')):
 for family in ('door','pickup','posture','switch'):
  group=sorted([r for r in rows if r['split']==split and r['family']==family],key=lambda r:(r['condition'],r['view']))
  sheet=Image.new('RGB',(960,1056),'white');draw=ImageDraw.Draw(sheet)
  for j,row in enumerate(group):
   m=json.loads((root/'episodes'/row['parent_episode_id']/'manifest.json').read_text())
   for k,i in enumerate((row['start_frame'],row['start_frame']+10,row['end_frame_exclusive']-1)):
    with Image.open(root/m['attempt']/'episode/0'/f"Action_{i:04d}_{m['camera_stream']}_normal.png") as im:sheet.paste(im.resize((320,240)),(k*320,j*264+24))
    draw.text((k*320+4,j*264+4),f"{row['condition']} {row['view']} f{i}",fill='black')
  sheet.save(ticket/f'various/screenshots/windows-scene-{scene}-{family}.jpg',quality=95)
