"""Encode dense trailing pooled features without loading weak labels."""
from pathlib import Path
from dataclasses import asdict
import json
import numpy as np
from video_workbench.embedding import QwenEmbedder,normalize,digest
from video_workbench.registry import file_hash
from video_workbench.media import decode_selected,probe
from video_workbench.perception.store import write_json


def encode(dataset,model,destination):
    root=Path(dataset);dest=Path(destination)
    if dest.exists():raise ValueError('new temporal feature directory required')
    manifest=json.loads((root/'manifest.json').read_text())
    if file_hash(root/'inputs.json')!=manifest['inputs_sha256']:raise ValueError('model inputs changed')
    rows=json.loads((root/'inputs.json').read_text());encoder=QwenEmbedder(model)
    spec={'encoder':asdict(encoder.space),'mode':'dense-trailing-pooled-images','inputs_sha256':manifest['inputs_sha256'],
          'policy':manifest['policy'],'code_sha256':{str(p):file_hash(p) for p in [Path(__file__),Path(__file__).parents[1]/'embedding.py']}}
    groups={}
    for i,r in enumerate(rows):groups.setdefault(r['episode_id'],[]).append((i,r))
    vectors=np.zeros((len(rows),encoder.space.dimension),dtype=np.float32);valid=np.zeros(len(rows),dtype=bool)
    source_audit=[]
    for eid,items in groups.items():
        r=items[0][1]
        if file_hash(r['video'])!=r['video_sha256']:raise ValueError('temporal source changed')
        media=probe(r['video']);indices=sorted({j for _,w in items for j in w['frame_indices']})
        images=decode_selected(r['video'],indices);features={j:encoder.image(images[j]) for j in indices}
        for i,w in items:
            actual=[media['pts_us'][j] for j in w['frame_indices']]
            if actual!=w['pts_us'] or any(t<w['start_us'] or t>=w['end_us'] for t in actual):raise ValueError('temporal source-time mapping changed')
            if [media['raw_pts'][j] for j in w['frame_indices']]!=w['raw_pts'] or media['time_base']!=w['time_base'] or media['origin_us']!=w['origin_us']:raise ValueError('native timestamp provenance changed')
            if w['available_us']<w['end_us']:raise ValueError('future feature horizon')
            if w['frame_indices']:vectors[i]=normalize(np.mean([features[j] for j in w['frame_indices']],axis=0)[None])[0];valid[i]=True
        source_audit.append({'episode_id':eid,'video_sha256':r['video_sha256'],'encoded_frames':len(indices),'windows':len(items),'native_mapping_verified':True})
        print(f'temporal encoded {eid}: {len(items)} windows / {len(indices)} frames',flush=True)
    if not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors[valid],axis=1),1,atol=1e-4):raise ValueError('invalid pooled features')
    dest.mkdir(parents=True);np.savez_compressed(dest/'features.npz',features=vectors,valid=valid)
    result={'status':'complete','spec':spec,'space_id':digest(spec),'sample_ids':[r['sample_id'] for r in rows],
            'features_sha256':file_hash(dest/'features.npz'),'source_audit':source_audit,'timings':encoder.timings,
            'labels_read':False,'limitation':'Pooled-image temporal baseline; no native-video representation claim.'}
    write_json(dest/'manifest.json',result);return result
