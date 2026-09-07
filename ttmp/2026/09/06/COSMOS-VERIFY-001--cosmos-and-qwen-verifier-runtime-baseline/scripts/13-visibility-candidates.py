"""Decode new source-frame candidates for RGB review before inference."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
from video_workbench.media import probe,decode_selected
from video_workbench.registry import file_hash
root=Path(__file__).resolve().parents[1];out=root/'various/visibility-v2';out.mkdir(exist_ok=True)
old=json.loads((root/'various/rerun/protocol.json').read_text());old_hashes={c['request']['frames'][0]['sha256'] for c in old['cases']}
chosen=[('dv-0a0732aef26f3d73','development'),('dv-554891a30ac02c19','development'),('dv-0d6f76e6e85792a3','test'),('dv-ab93c9c80442cb4a','test')]
records=[];font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',17)
for eid,split in chosen:
 base=Path('output/virtualhome-corpus/paired-actions-v4');m=json.loads((base/'episodes'/eid/'manifest.json').read_text());video=base/m['attempt']/'video.mp4';meta=probe(video)
 indices=sorted({round((meta['frames']-1)*fraction) for fraction in [0,.3,.45,.6,.75,.95]});images=decode_selected(video,indices)
 canvas=Image.new('RGB',(1280,1050),'white');draw=ImageDraw.Draw(canvas)
 for k,i in enumerate(indices):
  identifier=f'{eid}-{i}';path=out/(identifier+'.png');images[i].save(path);h=file_hash(path)
  if h in old_hashes:raise ValueError('candidate repeats previously evaluated pixels')
  record=dict(id=identifier,episode_id=eid,entity_id=f"{eid}:object-{m['scenario']['target_id']}",entity_class=m['scenario']['target_class'],split=split,view=m['view'],scene=m['scene_index'],frame_index=i,pts_us=meta['pts_us'][i],image=str(path),image_sha256=h,video=str(video),video_sha256=file_hash(video))
  records.append(record);x=(k%2)*640;y=(k//2)*350;im=images[i].copy();im.thumbnail((420,315));canvas.paste(im,(x,y));draw.text((x,y+317),f'{k}: {i} @ {meta["pts_us"][i]/1e6:.1f}s {split}',font=font,fill='black')
 canvas.save(out/(eid+'-candidates.png'))
(out/'candidates.json').write_text(json.dumps(records,indent=2)+'\n');print('fresh candidates',len(records))
