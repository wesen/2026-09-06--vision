"""Measure trained CPU streaming latency and save the seed comparison figure."""
from pathlib import Path
import json
import shutil
import time
import numpy as np
import torch
from PIL import Image,ImageDraw
from video_workbench.temporal.benchmark import load_sequences
from video_workbench.temporal.tcn import CausalMultiStageTCN,ChunkPredictor
root=Path(__file__).resolve().parents[1];out=root/'various/tcn-v1';out.mkdir(exist_ok=True)
cache=Path('output/temporal-v1/tcn-v1');r=json.loads((cache/'results.json').read_text())
shutil.copy2(cache/'results.json',out/'results.json')
_,sequences,_,_=load_sequences('output/temporal-v1/dataset','output/temporal-v1/pooled-features')
torch.set_num_threads(2)
latency=[]
for selected in r['selected_seed_results']:
    ck=torch.load(cache/selected['checkpoint'],weights_only=True,map_location='cpu');m=CausalMultiStageTCN(**ck['config']);m.load_state_dict(ck['state_dict']);m.eval()
    times=[]
    for split,s in sequences:
        if split!='test':continue
        stream=ChunkPredictor(m)
        for i in range(len(s.features)):
            x=torch.tensor(s.features[i:i+1].T)[None];v=torch.tensor(s.valid[i:i+1])[None]
            start=time.perf_counter_ns();stream.push(x,v);times.append((time.perf_counter_ns()-start)/1e6)
    latency.append({'seed':selected['seed'],'samples':len(times),'median_ms':float(np.median(times)),'p95_ms':float(np.percentile(times,95)),'max_ms':float(max(times)),
                    'retained_raw_history_bytes':(m.receptive_field-1)*(m.input_dim*4+1),
                    'parameter_and_buffer_bytes':sum(x.numel()*x.element_size() for x in list(m.parameters())+list(m.buffers()))})
(out/'stream-latency.json').write_text(json.dumps({'scope':'CPU head-only push includes bounded-history recomputation; excludes video decode, embedding, transport, and tensor construction','torch':torch.__version__,'threads':2,'runs':latency},indent=2)+'\n')
img=Image.new('RGB',(1050,410),'white');d=ImageDraw.Draw(img)
d.text((20,15),'Frozen-feature TCN: development selection does not transfer to test macro recall',fill='black')
d.text((20,38),'Weak program-interior targets. 48 VirtualHome-AIST episodes. Bars: development blue / test orange.',fill='black')
labels=[('Linear',.3258469945355191,.21156626506024095)]+[(f'TCN seed {x["seed"]}',x['development_macro_recall'],x['metrics']['test']['macro_recall']) for x in r['selected_seed_results']]
for i,(label,dev,test) in enumerate(labels):
    y=85+i*65;d.text((20,y+12),label,fill='black')
    for delta,value,color in ((0,dev,'#3478b8'),(23,test,'#db7939')):
        right=180+int(value*1450);d.rectangle((180,y+delta,right,y+delta+17),fill=color);d.text((right+8,y+delta+2),f'{value:.1%}',fill='black')
d.text((20,365),'Selected architecture: 16 channels, 1 dilated layer per stage, 2 stages; receptive field 5 feature samples.',fill='black')
d.text((20,387),'Inference is causal; these measurements do not establish improved retrieval or reviewed dense action accuracy.',fill='black')
img.save(out/'seed-comparison.png')
print(json.dumps(latency,indent=2))
