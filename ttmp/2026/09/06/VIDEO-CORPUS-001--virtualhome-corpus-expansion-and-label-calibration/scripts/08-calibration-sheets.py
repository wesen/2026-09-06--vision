"""Contact overviews of every appliance action frame; native sources remain linked."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
from virtualhome_corpus.core import frame_files
root=Path('output/virtualhome-corpus/diversity-v2');ticket=Path(__file__).resolve().parent.parent
rows=[]
for p in sorted((root/'episodes').glob('*/manifest.json')):
 m=json.loads(p.read_text())
 if m['status']!='complete' or m['condition']!='interaction' or m['scenario']['family']!='door':continue
 a=json.loads((root/m['annotations']).read_text());frames,_,_=frame_files(root/m['attempt']/'episode/0')
 indices=set()
 for event in a['actions']:
  if event['action'] in ('OPEN','CLOSE'):indices.update(range(max(0,event['raw_start']-3),min(len(frames),event['raw_end']+4)))
 indices=sorted(indices);sheet=Image.new('RGB',(1600,((len(indices)+4)//5)*264),'white');draw=ImageDraw.Draw(sheet)
 for j,i in enumerate(indices):
  with Image.open(frames[i]) as im:sheet.paste(im.resize((320,240)),((j%5)*320,(j//5)*264+24))
  draw.text(((j%5)*320+5,(j//5)*264+5),f'{i} / {i/10:.1f}s',fill='black')
 name=f"calibration-scene-{m['scene_index']}-{m['view']}.jpg";sheet.save(ticket/'various/screenshots'/name,quality=95)
 rows.append({'episode_id':m['episode_id'],'scene':m['scene_index'],'view':m['view'],'video_sha256':m['video_sha256'],'sheet':name,'frames':indices,'actions':[x for x in a['actions'] if x['action'] in ('OPEN','CLOSE')],'world_runs':json.loads((root/m['attempt']/'world-state-runs.json').read_text())})
(ticket/'various/calibration-source-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
