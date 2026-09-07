"""Render every native frame in manually selected exit neighborhoods."""
from pathlib import Path
import json
import av
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parents[1]/'various/r4-review'
bounds=[(78,87),(138,147),(180,193),(132,142),(164,176),(96,105),(80,88),(86,94),(128,138),(190,202),(124,134),(166,179)]
rows=json.loads((root/'recordings.json').read_text())
for row,(lo,hi) in zip(rows,bounds):
    with av.open(row['video']) as c:
        frames=[f.to_image() for f in c.decode(video=0)]
    indices=list(range(lo,hi+1))
    canvas=Image.new('RGB',(1280,((len(indices)+3)//4)*260),'white');d=ImageDraw.Draw(canvas)
    for k,i in enumerate(indices):
        x=k%4*320;y=k//4*260
        canvas.paste(frames[i].resize((320,240)),(x,y));d.text((x,y+242),f'{row["episode_id"]} frame {i}',fill='black')
    canvas.save(root/(row['episode_id']+'-exit.png'))
