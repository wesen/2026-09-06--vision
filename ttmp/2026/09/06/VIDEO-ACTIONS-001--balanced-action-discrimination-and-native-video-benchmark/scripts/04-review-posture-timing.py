"""Inspect the end of exported Sit spans before freezing source windows."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from video_workbench.media import decode_selected
from video_workbench.registry import file_hash

root=Path('output/action-benchmark-v1/dataset')
out=Path('output/action-benchmark-v1/posture-timing');out.mkdir(parents=True,exist_ok=True)
samples=json.loads((root/'samples.json').read_text())
reviews=json.loads((root/'review-proposals.json').read_text())
for i,(s,r) in enumerate(zip(samples,reviews)):
    if r['requested_action']!='sit':continue
    assert file_hash(s['video'])==s['video_sha256']
    end=r['weak_interval_us'][1]//100000
    indices=list(range(max(0,end-25),end+1,2))
    frames=decode_selected(s['video'],indices)
    sheet=Image.new('RGB',(1280,((len(indices)+3)//4)*270),'white');d=ImageDraw.Draw(sheet)
    for j,idx in enumerate(indices):
        x=j%4*320;y=j//4*270
        sheet.paste(frames[idx].resize((320,240)),(x,y));d.text((x+4,y+245),f"sample {i} / frame {idx} / {idx/10:.1f}s",fill='black')
    sheet.save(out/f'sit-{i:02d}.jpg',quality=96)
    print(i,r['weak_interval_us'],flush=True)
