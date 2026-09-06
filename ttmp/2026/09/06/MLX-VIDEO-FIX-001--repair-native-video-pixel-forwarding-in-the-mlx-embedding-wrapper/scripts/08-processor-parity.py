#!/usr/bin/env python3
"""Compare the official processor with the MLX-prepared fixture tensors."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from transformers import Qwen3VLProcessor
root=Path(__file__).resolve().parents[1]
path=Path('output/mlx-video-fix/models/official').resolve()
work=Path('output/mlx-video-fix/parity')
frames=np.load('output/mlx-video-fix/probes/fixture.npz')['frames']
processor=Qwen3VLProcessor.from_pretrained(str(path),local_files_only=True)
results=[]
for record in json.loads((root/'various/parity-inputs.json').read_text()):
 name=record['case'];kw={}
 if name in ['video','black','reverse','mixed']:
  video=np.zeros_like(frames) if name=='black' else frames[::-1].copy() if name=='reverse' else frames
  kw={'videos':[video],'do_sample_frames':False,'video_metadata':[{'total_num_frames':4,'fps':2.5,'frames_indices':[0,1,2,3]}]}
 if name in ['image','mixed']:kw['images']=[Image.fromarray(frames[0])]
 try:
  hf=processor(text=[record['prompt']],return_tensors='np',padding=True,add_special_tokens=False,**kw)
  mlx=dict(np.load(work/(name+'-inputs.npz')))
  comparisons={}
  for key,a in mlx.items():
   b=np.asarray(hf[key]);same=a.shape==b.shape
   comparisons[key]={'mlx_shape':list(a.shape),'hf_shape':list(b.shape),'exact':same and bool(np.array_equal(a,b)),
    'max_abs':float(np.max(np.abs(a.astype(float)-b.astype(float)))) if same else None}
  np.savez(work/(name+'-hf-inputs.npz'),**{k:np.asarray(v) for k,v in hf.items() if hasattr(v,'shape')})
  results.append({'case':name,'comparisons':comparisons,'hf_decoded_tokens':processor.tokenizer.decode(hf['input_ids'][0].tolist())})
 except Exception as e:results.append({'case':name,'error':repr(e)})
report={'sampling_fps':2.5,'frames':4,'results':results,'scope':'Independent processors on identical resized frames and prompt; no runtime model calls'}
(root/'various/processor-parity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
