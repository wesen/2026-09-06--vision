"""New episode/frame extraction for RGB review, before inference."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
from video_workbench.media import probe,decode_selected
from video_workbench.registry import file_hash
root=Path(__file__).resolve().parents[1];out=root/'various/reasoning-v3';out.mkdir(exist_ok=True)
old=set();hashes=set()
for path in [root/'various/rerun/protocol.json',root/'various/visibility-v2/protocol.json']:
 for c in json.loads(path.read_text())['cases']:
  old.add(c['request']['episode_id']);hashes.add(c['request']['frames'][0]['sha256'])
chosen=[('dv-31fd8bf573379ba5','development'),('dv-528d9a75133b1101','development'),('dv-c49ae32814f5899e','development'),('dv-dad43880b6994056','test'),('dv-503ac41c9f57746a','development'),('dv-50acf4cb570d5c06','test'),('dv-d065ae4a05eb0978','test'),('dv-d3ba7e1944d989fd','test')]
rows=[];font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',17)
for eid,split in chosen:
 assert eid not in old
 base=Path('output/virtualhome-corpus/paired-actions-v4');m=json.loads((base/'episodes'/eid/'manifest.json').read_text());video=base/m['attempt']/'video.mp4';meta=probe(video)
 indices=sorted({round((meta['frames']-1)*f) for f in [0,.2,.4,.55,.75,.95]});
 if eid=='dv-31fd8bf573379ba5':indices=[0,17,33,46,55,59,63,67]
 elif eid=='dv-dad43880b6994056':indices=[0,14,28,38,46,49,52,55]
 elif m['scenario']['target_class']=='fridge':indices=indices[1:]
 images=decode_selected(video,indices)
 canvas=Image.new('RGB',(1280,1400),'white');draw=ImageDraw.Draw(canvas)
 for k,i in enumerate(indices):
  identifier=f'{eid}-{i}';path=out/(identifier+'.png');images[i].save(path);h=file_hash(path);assert h not in hashes
  rows.append(dict(id=identifier,episode_id=eid,entity_id=f"{eid}:object-{m['scenario']['target_id']}",entity_class=m['scenario']['target_class'],split=split,view=m['view'],scene=m['scene_index'],frame_index=i,pts_us=meta['pts_us'][i],image=str(path),image_sha256=h,video=str(video),video_sha256=file_hash(video)))
  x=k%2*640;y=k//2*350;im=images[i].copy();im.thumbnail((420,315));canvas.paste(im,(x,y));draw.text((x,y+317),f'{k}: frame {i} {split} {m["scenario"]["target_class"]}',font=font,fill='black')
 canvas.save(out/(eid+'-review.png'))
(out/'candidates.json').write_text(json.dumps(rows,indent=2)+'\n');print('Extracted',len(rows),'fresh frames in eight new episodes')
