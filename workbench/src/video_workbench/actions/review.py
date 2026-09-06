"""Source-first contact sheets; proposals are shown as requests, never gold labels."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from video_workbench.media import decode_selected
from video_workbench.registry import file_hash
from .data import validate_samples


def render(dataset,destination):
    data=Path(dataset);dest=Path(destination);dest.mkdir(parents=True,exist_ok=True)
    samples=validate_samples(json.loads((data/'samples.json').read_text()));reviews={r['sample_id']:r for r in json.loads((data/'review-proposals.json').read_text())}
    sheets=[]
    for start in range(0,len(samples),6):
        group=samples[start:start+6];im=Image.new('RGB',(1280,len(group)*290),'white');draw=ImageDraw.Draw(im)
        for j,s in enumerate(group):
            if file_hash(s['video'])!=s['video_sha256']:raise ValueError('source changed')
            r=reviews[s['sample_id']];frames=decode_selected(s['video'],s['frame_indices'])
            draw.text((8,j*290+5),f"{start+j:02d} {s['split']} {r['family']} {r['target_class']} {r['view']} REQUEST {r['requested_action']} / {s['sample_id']}",fill='black')
            for k,idx in enumerate(s['frame_indices']):
                image=frames[idx].resize((320,240));im.paste(image,(k*320,j*290+25));draw.text((k*320+5,j*290+269),f"frame {idx} / {s['selected_pts_us'][k]/1e6:.2f}s",fill='black')
        path=dest/f'actions-source-{start//6:02d}.jpg';im.save(path,quality=96);sheets.append(str(path))
    (dest/'review-index.json').write_text(json.dumps({'sample_ids':[s['sample_id'] for s in samples],'sheets':sheets},indent=2)+'\n')
    return sheets
