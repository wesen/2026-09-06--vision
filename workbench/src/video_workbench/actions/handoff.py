"""Export original source windows as sparse per-episode temporal sequences."""
from pathlib import Path
import json
import numpy as np
from video_workbench.index import write_json,atomic_write
from video_workbench.registry import file_hash
from .data import ACTIONS,validate_samples


def export(dataset,labels_path,feature_roots,destination):
    data=Path(dataset);dest=Path(destination)
    if dest.exists():raise ValueError('new handoff destination required')
    samples=validate_samples(json.loads((data/'samples.json').read_text()))
    labels={r['sample_id']:r for r in json.loads(Path(labels_path).read_text())}
    if set(labels)!={s['sample_id'] for s in samples}:raise ValueError('labels mismatch')
    groups={}
    for i,s in enumerate(samples):groups.setdefault(s['episode_id'],[]).append(i)
    entries=[]
    for mode,root in feature_roots.items():
        root=Path(root);m=json.loads((root/'manifest.json').read_text())
        if m['sample_ids']!=[s['sample_id'] for s in samples] or m['spec']['samples_sha256']!=file_hash(data/'samples.json') or m['features_sha256']!=file_hash(root/'features.npz'):raise ValueError('feature identity mismatch')
        with np.load(root/'features.npz',allow_pickle=False) as f:features=f['original']
        for episode,indices in sorted(groups.items()):
            indices=sorted(indices,key=lambda i:samples[i]['available_us']);rows=[samples[i] for i in indices]
            if any(b['available_us']<=a['available_us'] for a,b in zip(rows,rows[1:])):raise ValueError('ambiguous sequence ordering')
            target=np.array([ACTIONS.index(labels[s['sample_id']]['action']) if labels[s['sample_id']]['action'] is not None else -1 for s in rows])
            rel=Path(mode)/(episode+'.npz')
            atomic_write(dest/rel,lambda f:np.savez_compressed(f,features=features[indices],valid=np.ones(len(rows),dtype=bool),label_mask=target>=0,targets=target,event_us=np.array([s['end_us'] for s in rows],dtype=np.int64),available_us=np.array([s['available_us'] for s in rows],dtype=np.int64)))
            entries.append({'episode_id':episode,'split':rows[0]['split'],'mode':mode,'space_id':m['spec']['space_id'],'producer_id':m['run_id'],'path':str(rel),'sha256':file_hash(dest/rel),'rows':rows})
    manifest={'schema':'sparse-action-sequences-v1','actions':ACTIONS,'label_sha256':file_hash(labels_path),'entries':entries,'semantics':'Original windows only. Each row is valid source evidence; label_mask separately excludes unknown action reviews. Event and availability equal window end in source time, excluding wall-clock model latency. Unrepresented time has no evidence. These 1–2-row episodes are a sparse handoff, not dense segmentation ground truth.'}
    write_json(dest/'manifest.json',manifest)
    return {'sequences':len(entries),'episodes':len(groups),'source_windows':len(samples)}
