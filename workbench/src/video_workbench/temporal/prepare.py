"""Freeze dense model-safe windows separately from weak program targets."""
from pathlib import Path
import json
from video_workbench.registry import Registry,file_hash
from video_workbench.embedding import digest
from video_workbench.media import selected_indices
from video_workbench.perception.store import write_json
from .data import trailing_grid


def prepare(release,destination):
    root=Path(release).resolve();dest=Path(destination)
    if dest.exists():raise ValueError('new temporal dataset required')
    dest.mkdir(parents=True)
    registry=Registry(dest/'registry.sqlite')
    try:registry.ingest(root/'inputs.jsonl');episodes=registry.episodes()
    finally:registry.close()
    inputs=[];labels=[];classes=set();lineages={}
    for episode in episodes:
        manifest_path=root/'episodes'/episode['episode_id']/'manifest.json'
        manifest=json.loads(manifest_path.read_text());annotation_path=root/manifest['annotations'];annotation=json.loads(annotation_path.read_text())
        lineage=manifest['lineage_id']
        if lineages.setdefault(lineage,episode['split'])!=episode['split']:raise ValueError('lineage split leakage')
        intervals=[r for r in annotation['actions'] if r['interior'] is not None]
        for w in trailing_grid(episode['media']['pts_us'],episode['media']['duration_us']):
            indices=selected_indices(episode['media']['pts_us'],w['start_us'],w['end_us'],2)
            row={k:episode[k] for k in ('episode_id','split','video','video_sha256')}
            row.update(lineage_id=lineage,start_us=w['start_us'],end_us=w['end_us'],available_us=w['end_us'],
                       frame_indices=indices,pts_us=[episode['media']['pts_us'][i] for i in indices],
                       raw_pts=[episode['media']['raw_pts'][i] for i in indices],time_base=episode['media']['time_base'],origin_us=episode['media']['origin_us'])
            row['sample_id']=digest(row)[:24];inputs.append(row)
            # Target the latest actual source frame, never an unobserved nominal boundary.
            event= row['pts_us'][-1] if indices else None
            matches=[r for r in intervals if event is not None and r['interior']['start_us']<=event<r['interior']['end_us']]
            actions={r['action'] for r in matches}
            label=next(iter(actions)) if len(actions)==1 else None
            if label is not None:classes.add(label)
            labels.append({'sample_id':row['sample_id'],'action':label,'label_mask':label is not None,
                           'target_source_us':event,'quality':'weak_program_interior' if label else 'unlabeled_boundary_or_gap',
                           'annotation_sha256':file_hash(annotation_path),'precise_boundary_supervision':False})
    write_json(dest/'inputs.json',inputs);write_json(dest/'weak-labels.json',labels)
    result={'status':'complete','episodes':len(episodes),'windows':len(inputs),'classes':sorted(classes),
            'inputs_sha256':file_hash(dest/'inputs.json'),'labels_sha256':file_hash(dest/'weak-labels.json'),
            'policy':{'window_us':2_000_000,'stride_us':500_000,'fps':2,'feature_availability':'trailing end; offline latency excluded','target':'latest sampled frame inside weak interior','boundaries':'unlabeled; exact-boundary metrics prohibited'},
            'release_inputs_sha256':file_hash(root/'inputs.jsonl'),'code_sha256':file_hash(__file__)}
    write_json(dest/'manifest.json',result);return result
