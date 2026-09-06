"""Save exact numerical metrics and a prediction-trace figure for report review."""
from pathlib import Path
import json
import shutil
import numpy as np
from PIL import Image,ImageDraw
from video_workbench.temporal.metrics import segment_metrics
root=Path(__file__).resolve().parents[1]
out=root/'various/classical-comparison-v2';out.mkdir(exist_ok=True)
shutil.copy2('output/temporal-v1/classical-v2/results.json',out/'video-results.json')
oracle=json.loads((root/'various/classical-oracle-v1.json').read_text())
metrics={}
for name,episode in oracle['episodes'].items():
    ends=episode['end_us'];starts=[0]+ends[:-1]
    metrics[name]={method:{str(iou):segment_metrics(r['predictions'],episode['targets'],episode['valid'],starts,ends,iou) for iou in (.1,.25,.5)} for method,r in episode['results'].items()}
(out/'numerical-segment-metrics.json').write_text(json.dumps({'kind':'numerical exact intervals only; not weak video boundaries','episodes':metrics},indent=2)+'\n')
image=Image.new('RGB',(1100,670),'white');draw=ImageDraw.Draw(image)
draw.text((15,12),'Classical temporal oracle: expected order can fabricate missing actions',fill='black')
draw.text((15,32),'Numerical fixtures only. OPEN green / WALK gray / CLOSE red / unknown white. Horizontal axis: source seconds.',fill='black')
colors={-1:'#ffffff',0:'#28a66d',1:'#8c969b',2:'#d74736'}
y=70
for name in ('omission','repetition','gap'):
    ep=oracle['episodes'][name];end=ep['end_us'];start=[0]+end[:-1];duration=end[-1]
    draw.text((15,y),name.upper(),fill='black');y+=22
    rows={'truth':[t if v else -1 for t,v in zip(ep['targets'],ep['valid'])]}
    rows.update({method:ep['results'][method]['predictions'] for method in ('viterbi','procedure_viterbi','hysteresis')})
    for method,pred in rows.items():
        draw.text((15,y+4),method,fill='black')
        for a,b,k in zip(start,end,pred):
            left=180+int(890*a/duration);right=180+int(890*b/duration)
            draw.rectangle((left,y,right,y+20),fill=colors[k],outline='#dddddd')
        y+=28
    draw.text((180,y),'0s',fill='black');draw.text((1020,y),f'{duration/1e6:.1f}s',fill='black');y+=42
image.save(out/'oracle-traces.png')
r=json.loads((out/'video-results.json').read_text())
for method,m in r['methods'].items():
    t=m['metrics']['test'];print(method,t['weak_interior_accuracy'],t['macro_recall'],m['settings'])
