"""Freeze a six-point RGB grid; all old apartment-0 examples become training-only."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from video_workbench.media import probe,decode_selected
from video_workbench.registry import file_hash
from video_workbench.embedding import digest
out=Path('output/state-workbench/review-v2');out.mkdir(parents=True,exist_ok=True)
candidates=[]
for release in ('home-v1','diversity-v2'):
 root=Path('output/virtualhome-corpus')/release
 for row in map(json.loads,(root/'inputs.jsonl').read_text().splitlines()):
  m=json.loads((root/'episodes'/row['episode_id']/'manifest.json').read_text())
  entity=m.get('scenario',{}).get('target_class',m.get('family'))
  if release=='home-v1' and entity!='microwave':continue
  if release=='diversity-v2' and m['scenario']['family']!='door':continue
  candidates.append((release,root,row,m,entity))
rows=[];episodes=[]
for ordinal,(release,root,row,m,entity) in enumerate(sorted(candidates,key=lambda r:r[2]['episode_id'])):
 video=root/row['video'];assert file_hash(video)==row['video_sha256'];media=probe(video)
 indices=sorted({round((media['frames']-1)*f) for f in (0,.2,.4,.6,.8,1)})
 images=decode_selected(video,indices);episode=[];group='apartment-0' if release=='home-v1' else row['split_group'];split='train' if release=='home-v1' else row['split']
 for j,index in enumerate(indices):
  sid=digest([row['video_sha256'],media['pts_us'][index],m['bindings']['target']])[:20];path=out/(sid+'.png');images[index].save(path)
  sample={'sample_id':sid,'episode_id':row['episode_id'],'entity_id':row['episode_id']+':object-'+str(m['bindings']['target']),'entity_class':entity,'property':'door_open','sample_us':media['pts_us'][index],'frame_index':index,'video':str(video),'video_sha256':row['video_sha256'],'image':str(path),'image_sha256':file_hash(path),'split':split,'split_group':group,'source_release':release,'review_sheet':ordinal,'ordinal':j}
  rows.append(sample);episode.append(sample)
 sheet=Image.new('RGB',(1920,1020),'white');draw=ImageDraw.Draw(sheet)
 for j,s in enumerate(episode):
  x=j%3*640;y=j//3*510;sheet.paste(images[s['frame_index']],(x,y+30));draw.text((x+8,y+6),f"sheet {ordinal} / sample {j} / target {entity} / {s['sample_us']/1e6:.1f}s",fill='black')
 sheet.save(out/f'sheet-{ordinal:02d}.jpg',quality=95)
 episodes.append({'sheet':ordinal,'episode_id':row['episode_id'],'entity_class':entity,'split':split,'samples':[s['sample_id'] for s in episode]})
(out/'samples.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'sheets.json').write_text(json.dumps(episodes,indent=2)+'\n')
print(json.dumps({'samples':len(rows),'sheets':len(episodes),'policy':'six fixed relative times; old scene 0 entirely train; diversity apartment split preserved'}))
