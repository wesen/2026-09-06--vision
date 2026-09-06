#!/usr/bin/env python3
"""Isolated-process parity audit. Preserve scripts 07/08 and their historical reports.

Run prepare-hf, prepare-mlx, torch, mlx, bf16, quant, community, compare in order.
All inputs are explicitly enumerated; latency excludes intermediate diagnostics.
"""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import resource
import subprocess
import time
from datetime import datetime, timezone
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WORK = Path('output/mlx-video-fix/audit')
MODEL = Path('output/mlx-video-fix/models/official').resolve()
WORK.mkdir(parents=True, exist_ok=True)
CASES = ['text', 'image', 'video', 'black', 'reverse', 'video1', 'video3', 'mixed']
KEYS = ['input_ids', 'attention_mask', 'pixel_values', 'pixel_values_videos', 'image_grid_thw', 'video_grid_thw']
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('mode', choices=['prepare-hf','prepare-mlx','torch','mlx','bf16','quant','community','compare'])
args = parser.parse_args()

def write(name, data):
    (ROOT/'various'/name).write_text(json.dumps(data, indent=2)+'\n')

def metadata():
    return {'created_at':datetime.now(timezone.utc).isoformat(),
            'commit':subprocess.check_output(['git','-C','output/mlx-video-fix/mlx-vlm','rev-parse','HEAD'],text=True).strip(),
            'versions':{p:importlib.metadata.version(p) for p in ['mlx','mlx-metal','mlx-vlm','transformers','torch','torchvision','numpy','pillow']}}

def compare(a,b):
    if a.shape != b.shape:
        return {'shape_equal':False}
    a,b=a.astype(np.float64),b.astype(np.float64)
    d=np.abs(a-b)
    return {'shape_equal':True,'max_abs':float(d.max()),'mean_abs':float(d.mean()),
            'cosine':float(np.dot(a.ravel(),b.ravel())/(np.linalg.norm(a)*np.linalg.norm(b)))}

if args.mode.startswith('prepare'):
    from PIL import Image, ImageDraw
    from transformers import Qwen3VLProcessor
    frames=np.load('output/mlx-video-fix/probes/fixture.npz')['frames']
    hf=args.mode=='prepare-hf'
    if hf:
        processor=Qwen3VLProcessor.from_pretrained(str(MODEL),local_files_only=True)
    else:
        from mlx_vlm.models.qwen3_vl.processing_qwen3_vl import Qwen3VLProcessor as MLXProcessor
        processor=MLXProcessor.from_pretrained(str(MODEL),local_files_only=True)
    report=metadata();report['cases']=[]
    for name in CASES:
        video=frames[:1] if name=='video1' else frames[:3] if name=='video3' else frames[::-1].copy() if name=='reverse' else np.zeros_like(frames) if name=='black' else frames
        content=[{'type':'text','text':'A person closing the fridge door.'}] if name=='text' else [{'type':'image'}] if name=='image' else [{'type':'image'},{'type':'video'}] if name=='mixed' else [{'type':'video'}]
        prompt=processor.apply_chat_template([{'role':'system','content':[{'type':'text','text':"Represent the user's input."}]},{'role':'user','content':content}],add_generation_prompt=True,tokenize=False)
        kw={}
        if name not in ('text','image'):
            indices=list(range(len(video)))
            if len(video)%2:
                video=np.concatenate([video,video[-1:]],axis=0)
                indices.append(indices[-1])
            kw['videos']=[video]
            if hf:
                kw.update(do_sample_frames=False,video_metadata=[{'total_num_frames':len(video),'fps':2.5,'frames_indices':indices}])
            else:kw['fps']=2.5
        if name in ('image','mixed'):kw['images']=[Image.fromarray(frames[0])]
        started=time.perf_counter()
        inputs=processor(text=[prompt],return_tensors='np',padding=True,add_special_tokens=False,**kw)
        arrays={k:np.asarray(inputs[k]) for k in KEYS if k in inputs}
        np.savez(WORK/f'{name}-{ "hf" if hf else "mlx" }-inputs.npz',**arrays)
        report['cases'].append({'case':name,'seconds':time.perf_counter()-started,'prompt':prompt,
            'decoded':processor.tokenizer.decode(arrays['input_ids'][0].tolist()),
            'shapes':{k:list(v.shape) for k,v in arrays.items()},'hashes':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in arrays.items()}})
    if hf:
        sheet=Image.new('RGB',(4*320,2*270),'white');draw=ImageDraw.Draw(sheet)
        for row,seq in enumerate([frames,frames[::-1]]):
            for i,frame in enumerate(seq):
                sheet.paste(Image.fromarray(frame).resize((320,240)),(i*320,row*270))
                draw.text((i*320+5,row*270+244),f'{"original" if row==0 else "reversed"} frame {i}',fill='black')
        sheet.save(ROOT/'various/parity-fixture-contact.jpg')
    write('audit-'+args.mode+'.json',report)
    if not hf:
        # Pixel-only intervention: retain HF tokens, masks and grids, replace pixels.
        # Token-only intervention: retain MLX tokens/masks with official pixels.
        for name in CASES:
            a=dict(np.load(WORK/f'{name}-hf-inputs.npz'));b=dict(np.load(WORK/f'{name}-mlx-inputs.npz'))
            for label,base,pixels in [('pixels',a,b),('tokens',b,a)]:
                c=dict(base)
                for k in ('pixel_values','pixel_values_videos'):
                    if k in pixels:
                        assert a[k].shape==b[k].shape
                        c[k]=pixels[k]
                np.savez(WORK/f'{name}-{label}-inputs.npz',**c)
    print('prepared',args.mode,flush=True)

elif args.mode!='compare':
    torch_mode=args.mode=='torch'
    started=time.perf_counter()
    if torch_mode:
        import torch
        from transformers import Qwen3VLModel
        torch.set_num_threads(8)
        model,loading=Qwen3VLModel.from_pretrained(str(MODEL),dtype=torch.float32,attn_implementation='eager',output_loading_info=True,local_files_only=True)
        assert not any(loading.values()),loading
        model.eval();torch.set_grad_enabled(False)
    else:
        import mlx.core as mx
        import mlx.nn as nn
        from mlx_vlm.embedding_loader import load_embedding_model
        model=load_embedding_model(Path('output/models/qwen3-vl-embedding-2b-4bit') if args.mode=='community' else MODEL,config_overrides={'model_type':'qwen3_vl_embedding'})
        if args.mode in ('mlx','quant'):model.set_dtype(mx.float32)
        if args.mode=='bf16':model.set_dtype(mx.bfloat16)
        if args.mode=='quant':nn.quantize(model,group_size=64,bits=4)
        mx.eval(model.parameters())
        mx.reset_peak_memory()
    report=metadata();report.update(mode=args.mode,load_materialized_seconds=time.perf_counter()-started,cases=[])
    families=['hf','mlx','pixels','tokens'] if args.mode=='mlx' else ['hf']
    for family in families:
        for name in CASES:
            a=dict(np.load(WORK/f'{name}-{family}-inputs.npz'))
            if torch_mode:
                inputs={k:torch.from_numpy(v.copy()) for k,v in a.items()}
                for k in ['input_ids','attention_mask','image_grid_thw','video_grid_thw']:
                    if k in inputs:inputs[k]=inputs[k].long()
                types=torch.zeros_like(inputs['input_ids']);types[inputs['input_ids']==model.config.image_token_id]=1;types[inputs['input_ids']==model.config.video_token_id]=2
                inputs['mm_token_type_ids']=types
                def run():
                    out=model(**inputs,use_cache=False)
                    mask=inputs['attention_mask'];last=mask.shape[1]-1-mask.flip(-1).argmax(-1)
                    pooled=out.last_hidden_state[torch.arange(len(last)),last]
                    return torch.nn.functional.normalize(pooled,dim=-1).numpy(),pooled.numpy()
            else:
                inputs={k:mx.array(v) for k,v in a.items()}
                def run():
                    out=model(**inputs);mx.eval(out.text_embeds,out.last_hidden_state)
                    return np.array(out.text_embeds.astype(mx.float32)),np.array(out.last_hidden_state[:,-1].astype(mx.float32))
            times=[]
            for repeat in range(4):
                started=time.perf_counter();embedding,pooled=run();times.append(time.perf_counter()-started)
            if torch_mode:pos,_=model.get_rope_index(**{k:v for k,v in inputs.items() if k not in ('pixel_values','pixel_values_videos')});pos=pos.numpy()
            else:pos,_=model.language_model.get_rope_index(inputs['input_ids'],image_grid_thw=inputs.get('image_grid_thw'),video_grid_thw=inputs.get('video_grid_thw'),attention_mask=inputs['attention_mask']);pos=np.array(pos)
            arrays={'embedding':embedding,'last_hidden':pooled,'positions':pos}
            # Diagnostics are deliberately outside timed embedding calls.
            for kind,key in [('image','pixel_values'),('video','pixel_values_videos')]:
                if key not in inputs:continue
                if torch_mode:
                    features=getattr(model,'get_'+kind+'_features')(inputs[key],inputs[kind+'_grid_thw'],return_dict=True)
                    visual=torch.cat(features.pooler_output,dim=0).numpy();deep=[x.numpy() for x in features.deepstack_features]
                else:
                    visual,deep=model.vision_tower(inputs[key],inputs[kind+'_grid_thw']);mx.eval(visual,deep)
                    visual=np.array(visual.astype(mx.float32));deep=[np.array(x.astype(mx.float32)) for x in deep]
                arrays[kind+'_features']=visual
                for i,v in enumerate(deep):arrays[f'{kind}_deep_{i}']=v
            np.savez(WORK/f'{name}-{family}-{args.mode}.npz',**arrays)
            record={'case':name,'family':family,'first_seconds':times[0],'warm_seconds':times[1:],'norm':float(np.linalg.norm(embedding)),
                'rss_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            if not torch_mode:record['mlx_peak_bytes']=mx.get_peak_memory()
            report['cases'].append(record);print(args.mode,name,family,round(times[-1],3),flush=True)
    write('audit-'+args.mode+'.json',report)

else:
    report=metadata();report['comparisons']=[]
    for name in CASES:
        ref=np.load(WORK/f'{name}-hf-torch.npz')
        for mode in ['mlx','bf16','quant','community']:
            candidate=np.load(WORK/f'{name}-hf-{mode}.npz')
            row={'case':name,'mode':mode,'positions_equal':bool(np.array_equal(np.broadcast_to(candidate['positions'],ref['positions'].shape),ref['positions'])),
                'layers':{k:compare(candidate[k],ref[k]) for k in ref.files if k!='positions'}}
            report['comparisons'].append(row)
    report['preprocessing']=[]
    for name in CASES:
        ref=np.load(WORK/f'{name}-hf-mlx.npz')['embedding']
        a=np.load(WORK/f'{name}-hf-inputs.npz');b=np.load(WORK/f'{name}-mlx-inputs.npz')
        report['preprocessing'].append({'case':name,'tensors':{k:compare(a[k],b[k]) for k in a.files},
            'embedding_effect':{f:compare(ref,np.load(WORK/f'{name}-{f}-mlx.npz')['embedding']) for f in ['mlx','tokens','pixels']}})
    write('audit-comparison.json',report)
    print(json.dumps({'fp32':[(r['case'],r['layers']['embedding']) for r in report['comparisons'] if r['mode']=='mlx']},indent=2))
