"""One encoder process per frozen representation, with resumable source caches."""
from dataclasses import asdict
from pathlib import Path
import json,time
import numpy as np
from PIL import Image
from video_workbench.embedding import digest,normalize
from video_workbench.index import FrameCache,writer_lock,atomic_write,write_json
from video_workbench.registry import file_hash
from video_workbench.media import decode_selected
from .data import validate_samples,ACTIONS
from .encoders import intervention,OfficialImagePool


def run(dataset, destination, mode):
    data=Path(dataset);dest=Path(destination)
    protocol=json.loads((data/'protocol.json').read_text())
    if file_hash(data/'samples.json')!=protocol['samples_sha256']:raise ValueError('sample freeze changed')
    samples=validate_samples(json.loads((data/'samples.json').read_text()))
    if mode not in protocol['representations']:raise ValueError('unknown representation')
    if mode=='native_fp32':
        from video_workbench.native_video import NativeVideoEmbedder
        encoder=NativeVideoEmbedder()
    elif mode=='pooled_fp32':encoder=OfficialImagePool()
    else:
        from video_workbench.embedding import QwenEmbedder
        encoder=QwenEmbedder('output/models/qwen3-vl-embedding-2b-4bit')
    spec={'mode':mode,'space':asdict(encoder.space),'space_id':encoder.space.id,
          'protocol_sha256':file_hash(data/'protocol.json'),'samples_sha256':file_hash(data/'samples.json'),
          'producer':{n:file_hash(Path(__file__).parent/n) for n in ('encode.py','encoders.py','data.py')}}
    # JSON manifests store tuple-valued encoder metadata as lists.
    spec=json.loads(json.dumps(spec))
    with writer_lock(dest):
        existing=dest/'manifest.json'
        if existing.exists():
            m=json.loads(existing.read_text())
            if m['spec']!=spec or file_hash(dest/'features.npz')!=m['features_sha256']:raise ValueError('immutable action run changed')
            result={'status':'reused','run_id':m['run_id'],'samples':len(samples)};print(json.dumps(result),flush=True);return result
        cache=FrameCache(dest,encoder.space,namespace='source-evidence');fresh=reused=0;arrays={k:[] for k in protocol['interventions']};mapping=[];started=time.perf_counter()
        def cached(key,compute):
            nonlocal fresh,reused
            key=digest([encoder.space.id,key]);v=cache.get(key)
            if v is None:v=cache.put(key,compute());fresh+=1
            else:reused+=1
            return v
        try:
            for row,s in enumerate(samples):
                if file_hash(s['video'])!=s['video_sha256']:raise ValueError('source changed')
                decoded=decode_selected(s['video'],s['frame_indices']);frames=[decoded[i] for i in s['frame_indices']]
                if mode!='native_fp32':
                    frame_vectors=[cached(['image',s['video_sha256'],idx],lambda im=im:encoder.image(im)) for idx,im in zip(s['frame_indices'],frames)]
                transforms={}
                for transform in protocol['interventions']:
                    images,slots,indices=intervention(frames,s['selected_pts_us'],transform)
                    if mode=='native_fp32':v=cached(['video',s['sample_id'],transform,spec['producer']],lambda:encoder.video(images,slots,s['start_us']))
                    else:v=normalize(np.mean([frame_vectors[i] for i in indices],axis=0)[None])[0]
                    arrays[transform].append(v);transforms[transform]={'slot_pts_us':slots,'source_indices':[s['frame_indices'][i] for i in indices]}
                mapping.append({'sample_id':s['sample_id'],'transforms':transforms})
                if row==0 and mode=='native_fp32':
                    black=[Image.new('RGB',im.size) for im in frames]
                    black_vector=encoder.video(black,s['selected_pts_us'],s['start_us'])
                    pixel_probe={'sample_id':s['sample_id'],'original_black_cosine':float(arrays['original'][0]@black_vector),'max_abs_difference':float(np.max(np.abs(arrays['original'][0]-black_vector)))}
                    if pixel_probe['max_abs_difference']<1e-6:raise ValueError('native output insensitive to changed pixels')
                if row%12==0:print(f'{mode} {row+1}/{len(samples)}',flush=True)
            for key in arrays:arrays[key]=np.stack(arrays[key]).astype(np.float32)
            arrays['queries']=np.stack([cached(['query',protocol['queries'][a]],lambda a=a:encoder.text(protocol['queries'][a])) for a in ACTIONS])
            if mode!='native_fp32' and not np.allclose(arrays['original'],arrays['reverse'],atol=1e-6):raise ValueError('pooled permutation invariant failed')
            atomic_write(dest/'features.npz',lambda f:np.savez_compressed(f,**arrays))
            manifest={'spec':spec,'features_sha256':file_hash(dest/'features.npz'),'sample_ids':[s['sample_id'] for s in samples],
                      'source_mapping':mapping,'actions':ACTIONS,'fresh':fresh,'reused':reused,'elapsed_seconds':time.perf_counter()-started,
                      'pixel_probe':pixel_probe if mode=='native_fp32' else None}
            manifest['run_id']=digest(manifest);write_json(existing,manifest)
            print(json.dumps({k:manifest[k] for k in ('run_id','fresh','reused','elapsed_seconds','pixel_probe')}),flush=True);return manifest
        finally:cache.close()
