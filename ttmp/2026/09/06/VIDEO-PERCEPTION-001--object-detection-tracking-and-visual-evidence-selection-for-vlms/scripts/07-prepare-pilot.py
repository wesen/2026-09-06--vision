"""Fixed source-first pilot: one interaction frame per apartment/family/view."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from video_workbench.media import probe,decode_selected
from video_workbench.registry import file_hash
S=Path(__file__).resolve().parents[1];root=Path('output/virtualhome-corpus/diversity-v2');out=Path('output/video-perception/review-v1');out.mkdir(parents=True,exist_ok=True)
records=[]
for p in sorted((root/'episodes').glob('*/manifest.json')):
 m=json.loads(p.read_text())
 if m['condition']!='interaction':continue
 video=root/m['video'];media=probe(video);im=decode_selected(video,[0])[0]
 i=len(records);path=out/f'pilot-{i:02d}.png';im.save(path)
 records.append({'ordinal':i,'episode_id':m['episode_id'],'image':str(path),'image_sha256':file_hash(path),'video_sha256':file_hash(video),'frame_index':0,'pts_us':0,'target_class':m['scenario']['target_class'],'family':m['scenario']['family'],'split':m['split'],'view':m['view']})
for start in range(0,len(records),4):
 sheet=Image.new('RGB',(1280,1020),'white');draw=ImageDraw.Draw(sheet)
 for j,r in enumerate(records[start:start+4]):
  x=j%2*640;y=j//2*510;sheet.paste(Image.open(r['image']),(x,y+30));draw.text((x+6,y+6),f"{r['ordinal']} / {r['target_class']} / source frame 0",fill='black')
 sheet.save(S/'various/screenshots'/f'pilot-source-{start//4:02d}.jpg',quality=95)
(S/'various/pilot-samples.json').write_text(json.dumps(records,indent=2)+'\n')
print(len(records),'source-first pilot frames')
