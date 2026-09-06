#!/usr/bin/env python3
"""Prepare identical tensors; compare repaired MLX and official Torch FP32.

Modes run separately so MLX processor registration cannot affect Torch's processor.
"""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
work=Path('output/mlx-video-fix/parity');work.mkdir(parents=True,exist_ok=True)
path=Path('output/mlx-video-fix/models/official').resolve()
p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','mlx','mlx4bit','torch','compare']);args=p.parse_args()

def unit(x):return x/np.linalg.norm(x,axis=-1,keepdims=True)
def compare(a,b):
 return {'shape_equal':a.shape==b.shape,'cosine':float(np.sum(unit(a)*unit(b))),
         'max_abs':float(np.max(np.abs(a-b))),'mean_abs':float(np.mean(np.abs(a-b)))}

if args.mode=='prepare':
 from PIL import Image
 from transformers import AutoProcessor
 import mlx_vlm.models.qwen3_vl_embedding
 from mlx_vlm.utils import prepare_inputs
 frames=np.load('output/mlx-video-fix/probes/fixture.npz')['frames']
 processor=AutoProcessor.from_pretrained(str(path),local_files_only=True)
 records=[]
 for name in ['text','image','video','black','reverse','mixed']:
  content=[{'type':'text','text':'A person closing the fridge door.'}] if name=='text' else [{'type':'image'}] if name=='image' else [{'type':'video'}]
  if name=='mixed':content=[{'type':'image'},{'type':'video'}]
  prompt=processor.apply_chat_template([{'role':'system','content':[{'type':'text','text':"Represent the user's input."}]},{'role':'user','content':content}],add_generation_prompt=True,tokenize=False)
  kw={}
  if name in ['video','black','reverse','mixed']:
   video=np.zeros_like(frames) if name=='black' else frames[::-1].copy() if name=='reverse' else frames
   kw={'videos':[video],'fps':2.5}
  if name in ['image','mixed']:kw['images']=[Image.fromarray(frames[0])]
  inputs=prepare_inputs(processor,prompts=prompt,**kw)
  arrays={k:np.array(v) for k,v in inputs.items() if hasattr(v,'shape')}
  np.savez(work/(name+'-inputs.npz'),**arrays)
  records.append({'case':name,'shapes':{k:list(v.shape) for k,v in arrays.items()},
   'tensor_hashes':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in arrays.items()},
   'prompt':prompt,'decoded_tokens':processor.tokenizer.decode(arrays['input_ids'][0].tolist())})
 (root/'various/parity-inputs.json').write_text(json.dumps(records,indent=2)+'\n')
 print('prepared',len(records),'matched-input fixtures',flush=True)

elif args.mode in ('mlx','mlx4bit'):
 import mlx.core as mx
 from mlx_vlm.embedding_loader import load_embedding_model
 started=time.perf_counter()
 model_path = path if args.mode=='mlx' else Path('output/models/qwen3-vl-embedding-2b-4bit')
 model=load_embedding_model(model_path,config_overrides={'model_type':'qwen3_vl_embedding'})
 if args.mode=='mlx':model.set_dtype(mx.float32)
 mx.eval(model.parameters())
 report={'backend':'MLX','dtype':'float32' if args.mode=='mlx' else 'checkpoint-native','conversion':'official FP32' if args.mode=='mlx' else 'pinned community 4-bit artifact','load_seconds':time.perf_counter()-started,'cases':[]}
 for file in sorted(work.glob('*-inputs.npz')):
  name=file.name.removesuffix('-inputs.npz');a=dict(np.load(file));inputs={k:mx.array(v) for k,v in a.items()}
  started=time.perf_counter();out=model(**inputs);mx.eval(out.text_embeds)
  pos,_=model.language_model.get_rope_index(inputs['input_ids'],image_grid_thw=inputs.get('image_grid_thw'),video_grid_thw=inputs.get('video_grid_thw'),attention_mask=inputs.get('attention_mask'))
  arrays={'embedding':np.array(out.text_embeds.astype(mx.float32)),'positions':np.array(pos),'last_hidden':np.array(out.last_hidden_state[:,-1].astype(mx.float32))}
  for kind,key in [('image','pixel_values'),('video','pixel_values_videos')]:
   if key in inputs:
    visual,deep=model.vision_tower(inputs[key],inputs[kind+'_grid_thw']);mx.eval(visual,deep)
    arrays[kind+'_features']=np.array(visual.astype(mx.float32))
    for i,v in enumerate(deep):arrays[f'{kind}_deep_{i}']=np.array(v.astype(mx.float32))
  np.savez(work/(name+'-'+args.mode+'.npz'),**arrays)
  record={'case':name,'seconds':time.perf_counter()-started,'norm':float(np.linalg.norm(arrays['embedding']))}
  report['cases'].append(record);print(record,flush=True)
 report['peak_bytes']=mx.get_peak_memory()
 (root/'various'/('parity-'+args.mode+'.json')).write_text(json.dumps(report,indent=2)+'\n')

elif args.mode=='torch':
 import torch
 from transformers import Qwen3VLModel
 torch.set_num_threads(8)
 started=time.perf_counter()
 model,loading=Qwen3VLModel.from_pretrained(str(path),dtype=torch.float32,attn_implementation='eager',output_loading_info=True,local_files_only=True)
 model.eval()
 report={'backend':'PyTorch CPU','dtype':'float32','load_seconds':time.perf_counter()-started,'loading':loading,'cases':[]}
 assert not loading.get('missing_keys'),loading
 with torch.inference_mode():
  for file in sorted(work.glob('*-inputs.npz')):
   name=file.name.removesuffix('-inputs.npz');a=dict(np.load(file));inputs={k:torch.from_numpy(v.copy()) for k,v in a.items()}
   for key in ['input_ids','attention_mask','image_grid_thw','video_grid_thw']:
    if key in inputs:inputs[key]=inputs[key].long()
   types=torch.zeros_like(inputs['input_ids']);types[inputs['input_ids']==model.config.image_token_id]=1;types[inputs['input_ids']==model.config.video_token_id]=2
   inputs['mm_token_type_ids']=types
   started=time.perf_counter()
   pos,_=model.get_rope_index(inputs['input_ids'],mm_token_type_ids=types,image_grid_thw=inputs.get('image_grid_thw'),video_grid_thw=inputs.get('video_grid_thw'),attention_mask=inputs['attention_mask'])
   out=model(**inputs,use_cache=False)
   mask=inputs['attention_mask'];last=mask.shape[1]-1-mask.flip(-1).argmax(-1)
   pooled=out.last_hidden_state[torch.arange(len(last)),last]
   arrays={'embedding':torch.nn.functional.normalize(pooled,dim=-1).numpy(),'positions':pos.numpy(),'last_hidden':pooled.numpy()}
   for kind,key in [('image','pixel_values'),('video','pixel_values_videos')]:
    if key in inputs:
     features=getattr(model,'get_'+kind+'_features')(inputs[key],inputs[kind+'_grid_thw'],return_dict=True)
     arrays[kind+'_features']=torch.cat(features.pooler_output,dim=0).numpy()
     for i,v in enumerate(features.deepstack_features):arrays[f'{kind}_deep_{i}']=v.numpy()
   np.savez(work/(name+'-torch.npz'),**arrays)
   record={'case':name,'seconds':time.perf_counter()-started,'norm':float(np.linalg.norm(arrays['embedding']))}
   report['cases'].append(record);print(record,flush=True)
 (root/'various/parity-torch.json').write_text(json.dumps(report,indent=2,default=str)+'\n')

else:
 results=[]
 for file in sorted(work.glob('*-mlx.npz')):
  name=file.name.removesuffix('-mlx.npz');a=np.load(file);b=np.load(work/(name+'-torch.npz'))
  record={'case':name,'embedding':compare(a['embedding'],b['embedding']),
          'positions_equal':bool(np.array_equal(np.broadcast_to(a['positions'],b['positions'].shape),b['positions'])), 'position_shapes':{'mlx':list(a['positions'].shape),'torch':list(b['positions'].shape)},'intermediates':{}}
  for k in a.files:
   if k in ['embedding','positions']:continue
   record['intermediates'][k]={'shape':list(a[k].shape),'max_abs':float(np.max(np.abs(a[k]-b[k]))),'mean_abs':float(np.mean(np.abs(a[k]-b[k])))}
  results.append(record)
 report={'scope':'Same official source weights, FP32, identical packed processor tensors; processor end-to-end alignment is separate',
  'tolerance':{'min_embedding_cosine':0.999,'max_embedding_abs':0.001,'positions_exact_after_text_axis_broadcast':True},'cases':results,
  'passed':len(results)==6 and all(r['embedding']['cosine']>=.999 and r['embedding']['max_abs']<=.001 and r['positions_equal'] for r in results)}
 (root/'various/reference-parity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
