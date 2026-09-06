#!/usr/bin/env python3
"""Controlled real-model video probe. Run with the isolated repair Python.

PYTHONPATH=output/mlx-video-fix/mlx-vlm <python> SCRIPT before|after
The same selected development frames and metadata are used for both pixel cases.
"""
import argparse,hashlib,json,time,platform,importlib.metadata,subprocess
from pathlib import Path
from unittest.mock import patch
import av
import mlx.core as mx
import numpy as np
import psutil
from PIL import Image
from transformers import AutoProcessor
from mlx_vlm.embedding_loader import load_embedding_model
from mlx_vlm.utils import prepare_inputs

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('label');args=p.parse_args()
model_path=Path('output/models/qwen3-vl-embedding-2b-4bit').resolve()
corpus=Path('output/virtualhome-corpus/home-v1').resolve()
row=next(json.loads(line) for line in (corpus/'inputs.jsonl').read_text().splitlines() if json.loads(line)['split']=='development')
wanted={20,24,28,32};frames=[];pts=[]
with av.open(str(corpus/row['video'])) as c:
 for i,f in enumerate(c.decode(video=0)):
  if i in wanted:
   frames.append(np.array(f.to_image().resize((320,240),Image.Resampling.BICUBIC)));pts.append(round(float(f.pts*f.time_base)*1e6))
  if i>=max(wanted):break
assert len(frames)==4
frames=np.stack(frames)
work=Path('output/mlx-video-fix/probes');work.mkdir(parents=True,exist_ok=True)
np.savez(work/'fixture.npz',frames=frames,pts_us=np.array(pts))
started=time.perf_counter()
model=load_embedding_model(model_path,config_overrides={'model_type':'qwen3_vl_embedding'})
load_seconds=time.perf_counter()-started
processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
prompt=processor.apply_chat_template([
 {'role':'system','content':[{'type':'text','text':"Represent the user's input."}]},
 {'role':'user','content':[{'type':'video'}]}],add_generation_prompt=True,tokenize=False)
inputs=prepare_inputs(processor,videos=[frames],prompts=prompt,fps=2.5)
assert inputs.get('pixel_values_videos') is not None
black=prepare_inputs(processor,videos=[np.zeros_like(frames)],prompts=prompt,fps=2.5)
for key in ['input_ids','attention_mask','video_grid_thw']:
 np.testing.assert_array_equal(np.array(inputs[key]),np.array(black[key]))
assert inputs['pixel_values_videos'].shape==black['pixel_values_videos'].shape
original_vision=type(model.vision_tower).__call__
results={};vectors={}
for label,request in [('original',inputs),('black',black),('original_repeat',inputs)]:
 calls=[]
 def observe(vision,*a,**kw):
  calls.append({'pixels_shape':list(a[0].shape),'grid':np.array(a[1]).tolist() if len(a)>1 else None})
  return original_vision(vision,*a,**kw)
 begin=time.perf_counter()
 try:
  with patch.object(type(model.vision_tower),'__call__',observe):
   emb=model(**request).text_embeds;mx.eval(emb);vector=np.array(emb.astype(mx.float32))
  vectors[label]=vector
  results[label]={'ok':True,'shape':list(vector.shape),'norms':np.linalg.norm(vector,axis=-1).tolist(),'finite':bool(np.isfinite(vector).all())}
 except Exception as e:
  results[label]={'ok':False,'error_type':type(e).__name__,'error':str(e)}
 results[label].update(seconds=time.perf_counter()-begin,vision_calls=calls)
report={'label':args.label,'upstream_commit':subprocess.check_output(['git','-C','output/mlx-video-fix/mlx-vlm','rev-parse','HEAD'],text=True).strip(),
 'platform':platform.platform(),'packages':{k:importlib.metadata.version(k) for k in ['mlx','mlx-vlm','transformers','av','numpy']},
 'fixture':{'episode_id':row['episode_id'],'split':row['split'],'video_sha256':row['video_sha256'],'pts_us':pts,'frames_sha256':hashlib.sha256(frames.tobytes()).hexdigest()},
 'input_shapes':{k:list(v.shape) for k,v in inputs.items() if hasattr(v,'shape')},'input_ids':np.array(inputs['input_ids']).tolist(),
 'grid':np.array(inputs['video_grid_thw']).tolist(),'load_seconds':load_seconds,'results':results,
 'rss_bytes':psutil.Process().memory_info().rss,'mlx_peak_bytes':mx.get_peak_memory()}
if 'original' in vectors and 'black' in vectors:
 report['pixel_intervention_cosine']=float(np.sum(vectors['original']*vectors['black']) / (np.linalg.norm(vectors['original']) * np.linalg.norm(vectors['black'])))
 report['pixel_intervention_max_abs']=float(np.max(np.abs(vectors['original']-vectors['black'])))
if 'original_repeat' in vectors and 'original' in vectors:
 report['repeat_max_abs']=float(np.max(np.abs(vectors['original']-vectors['original_repeat'])))
np.savez(work/(args.label+'-vectors.npz'),**vectors)
(root/'various'/('video-smoke-'+args.label+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
