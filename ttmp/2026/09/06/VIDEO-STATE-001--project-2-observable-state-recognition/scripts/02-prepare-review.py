"""Select a label-independent relative-time grid and emit blind RGB review sheets."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
from video_workbench.registry import Registry,file_hash
from video_workbench.media import decode_selected
from video_workbench.embedding import digest

ROOT=Path('output/state-workbench/review-v1');ROOT.mkdir(parents=True,exist_ok=True)
r=Registry('output/video-workbench/registry.sqlite')
rows=[]
for e in r.episodes():
    source=Path(e['video']).parent.parent/'manifest.json'
    metadata=json.loads(source.read_text())
    # Entity metadata only: never transfer intended action variants or graph labels.
    binding={'entity_id':f"{e['episode_id']}:object-{metadata['bindings']['target']}",'entity_class':metadata['family']}
    indices=sorted({round((e['media']['frames']-1)*f) for f in (0,.2,.4,.6,.8,1)})
    images=decode_selected(e['video'],indices)
    for ordinal,i in enumerate(indices):
        sid=digest({'video':e['video_sha256'],'pts':e['media']['pts_us'][i],'entity':binding['entity_id']})[:20]
        path=ROOT/(sid+'.png');images[i].save(path)
        rows.append({'sample_id':sid,'episode_id':e['episode_id'],**binding,'property':'door_open',
            'sample_us':e['media']['pts_us'][i],'frame_index':i,'video_sha256':e['video_sha256'],
            'image_sha256':file_hash(path),'image':str(path),'split':e['split'],'split_group':e['split_group'],'ordinal':ordinal})
r.close()
(ROOT/'samples.json').write_text(json.dumps(rows,indent=2)+'\n')
# One episode per sheet, 3x2 native-resolution frames, opaque sample numbers.
for e in sorted({r['episode_id'] for r in rows}):
    episode=[r for r in rows if r['episode_id']==e]
    sheet=Image.new('RGB',(1920,1020),'white');draw=ImageDraw.Draw(sheet)
    for n,row in enumerate(episode):
        x=(n%3)*640;y=(n//3)*510
        draw.text((x+8,y+5),f"{n}: {row['entity_class']} / {row['sample_us']/1e6:.1f}s / {row['sample_id']}",fill='black')
        sheet.paste(Image.open(row['image']),(x,y+30))
    sheet.save(ROOT/(e+'-sheet.jpg'),quality=94)
print(json.dumps({'samples':len(rows),'episodes':len({r['episode_id'] for r in rows}),'root':str(ROOT)}))
