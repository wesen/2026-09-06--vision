"""Render native-resolution detail for the explicitly unresolved source windows."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from video_workbench.media import decode_selected
from video_workbench.registry import file_hash
root=Path('output/action-benchmark-v1/dataset-v2')
out=Path('output/action-benchmark-v1/details-v2');out.mkdir(parents=True,exist_ok=True)
samples=json.loads((root/'samples.json').read_text())
for i in [0,1,12,13,17,20,28,29,35,41,42,43,53,54,56,57,58,59,66,69]:
    s=samples[i];assert file_hash(s['video'])==s['video_sha256']
    frames=decode_selected(s['video'],s['frame_indices'])
    sheet=Image.new('RGB',(1280,1020),'white');d=ImageDraw.Draw(sheet)
    for j,idx in enumerate(s['frame_indices']):
        x=j%2*640;y=j//2*510
        sheet.paste(frames[idx],(x,y));d.text((x+4,y+485),f"sample {i} / frame {idx} / {s['selected_pts_us'][j]/1e6:.2f}s",fill='black')
    sheet.save(out/f'sample-{i:02d}.jpg',quality=96)
