"""Materialize RGB review sheets; never infer event/state truth from programs."""
from pathlib import Path
import json
import av
from PIL import Image,ImageDraw,ImageFont
from video_workbench.registry import file_hash
root=Path(__file__).resolve().parents[1];out=root/'various/r4-review';out.mkdir(exist_ok=True)
records=[];font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',14)
for path in sorted(Path('output/virtualhome-corpus/home-v1/episodes').glob('*/attempt-0001/manifest.json')):
    meta=json.loads(path.read_text())
    if meta['split'] not in ('development','test'):continue
    video=path.with_name('video.mp4');assert file_hash(video)==meta['video_sha256']
    with av.open(str(video)) as container:
        frames=[(int(f.pts*f.time_base*1000000),f.to_image()) for f in container.decode(video=0)]
    indices=sorted({round(i*(len(frames)-1)/19) for i in range(20)})
    canvas=Image.new('RGB',(1280,1150),'white');draw=ImageDraw.Draw(canvas)
    draw.text((8,5),f"{meta['episode_id']} {meta['split']} target={meta['family']}",font=font,fill='black')
    for i,index in enumerate(indices):
        pts,image=frames[index];x=(i%4)*320;y=30+(i//4)*224
        canvas.paste(image.resize((300,200)),(x,y));draw.text((x,y+201),f'frame {index} | {pts/1e6:.1f}s',font=font,fill='black')
    canvas.save(out/(meta['episode_id']+'.png'))
    records.append(dict(episode_id=meta['episode_id'],split=meta['split'],entity_id=str(meta['bindings']['target']),entity_label=meta['family'],video=str(video.resolve()),video_sha256=meta['video_sha256'],frames=len(frames),pts_us=[p for p,_ in frames],duration_us=frames[-1][0]+100000))
(out/'recordings.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps([dict(episode_id=r['episode_id'],split=r['split'],target=r['entity_label']) for r in records]))
