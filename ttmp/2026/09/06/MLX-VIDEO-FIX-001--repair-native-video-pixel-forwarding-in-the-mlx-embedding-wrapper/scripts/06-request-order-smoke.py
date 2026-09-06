#!/usr/bin/env python3
"""Compare clean and reused model instances across text/image/video requests."""
import argparse,json,time
from pathlib import Path
import numpy as np
import mlx.core as mx
from PIL import Image
from transformers import AutoProcessor
from mlx_vlm.embedding_loader import load_embedding_model
from mlx_vlm.utils import prepare_inputs
import mlx_vlm.models.qwen3_vl_embedding  # Register the torch-free processor.
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('label');args=p.parse_args()
path=Path('output/models/qwen3-vl-embedding-2b-4bit').resolve()
frames=np.load('output/mlx-video-fix/probes/fixture.npz')['frames']
processor=AutoProcessor.from_pretrained(str(path),local_files_only=True)
def request(kind,n=4):
 content=[{'type':'text','text':'A person closing the fridge door.'}] if kind=='text' else [{'type':kind}]
 if kind=='mixed':content=[{'type':'image'},{'type':'video'}]
 prompt=processor.apply_chat_template([{'role':'system','content':[{'type':'text','text':"Represent the user's input."}]},{'role':'user','content':content}],add_generation_prompt=True,tokenize=False)
 kw={}
 if kind in ('video','mixed'):kw['videos']=[frames[:n]];kw['fps']=2.5
 if kind in ('image','mixed'):kw['images']=[Image.fromarray(frames[0])]
 return prepare_inputs(processor,prompts=prompt,**kw)
requests={}
errors={}
for name,kind,n in [('video4','video',4),('text','text',0),('image','image',0),('video2','video',2),('video1','video',1),('video3','video',3),('mixed','mixed',4)]:
 try:requests[name]=request(kind,n)
 except Exception as e:errors[name]=repr(e)
def load():return load_embedding_model(path,config_overrides={'model_type':'qwen3_vl_embedding'})
def run(model,inputs):
 out=model(**inputs).text_embeds;mx.eval(out);return np.array(out.astype(mx.float32))
# A fresh instance per reference case proves isolation independently of reset logic.
reference={}
for name,inputs in requests.items():
 try:
  m=load();reference[name]=run(m,inputs);del m;mx.clear_cache()
 except Exception as e:errors[name]=repr(e)
m=load();results=[]
for name in ['video4','text','video2','image','video4','text','video1','video3','mixed','text','video4']:
 if name not in reference:continue
 started=time.perf_counter()
 try:
  value=run(m,requests[name]);ref=reference[name]
  results.append({'case':name,'max_abs_vs_fresh':float(np.max(np.abs(value-ref))),
   'cosine_vs_fresh':float(np.sum(value*ref)/(np.linalg.norm(value)*np.linalg.norm(ref))),
   'seconds':time.perf_counter()-started,'shape':list(value.shape)})
 except Exception as e:results.append({'case':name,'error':repr(e)})
r={'label':args.label,'errors':errors,'cases':results,'all_exact':all(c.get('max_abs_vs_fresh')==0 for c in results) and not errors}
(root/'various'/('request-order-'+args.label+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
