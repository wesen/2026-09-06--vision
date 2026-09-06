"""Frozen region evidence ablations. Selection reads no state labels."""
from pathlib import Path
from dataclasses import asdict
import json
import numpy as np
from PIL import Image
from video_workbench.embedding import QwenEmbedder,digest,normalize
from video_workbench.registry import file_hash
from video_workbench.perception.store import rows,verify_episode,write_json
from .features import load_cache

CONDITIONS=('F','C','FC','FCH','FCW','H')
POLICY={'requested_class':{'fridge':'refrigerator','microwave':'microwave'},'binding':'exactly-one-accepted-requested-class-box-per-frame','crop_kind':'target','score_floor':.25,
 'fusion':'FC=unit(mean(unit-full,unit-crop)); FCH/FCW=joint-images-and-hint',
 'hints':'Predicted objects: {classes}. These are machine estimates.',
 'wrong_hints':'Predicted objects: bicycle, dog. These are machine estimates.',
 'missing_crop':'C unavailable; FC uses full frame; FCH/FCW keep full frame and explicit detector hint',
 'budgets':{'F':76800,'C':76800,'FC':153600,'FCH':153600,'FCW':153600,'H':0},
 'test_reuse':'Previously inspected test partition; exploratory follow-up, not a fresh untouched benchmark.'}


def prepare(samples,derived_path,destination):
    derived=Path(derived_path);run=json.loads((derived/'run.json').read_text())
    if run['status']!='complete':raise ValueError('complete perception run required')
    entries={e['episode_id']:e for e in run['episodes']};cached={};evidence=[]
    for sample in samples:
        eid=sample['episode_id']
        if eid not in entries:raise ValueError('missing perception episode')
        if eid not in cached:
            folder=derived/'episodes'/eid
            if file_hash(folder/'manifest.json')!=entries[eid]['manifest_sha256']:raise ValueError('perception manifest changed')
            m=verify_episode(folder)
            if m['episode']['video_sha256']!=sample['video_sha256']:raise ValueError('region source mismatch')
            cached[eid]=rows(folder/'crops.jsonl')
        candidates=[c for c in cached[eid] if c['frame_index']==sample['frame_index'] and c['kind']=='target' and c['class_name']==POLICY['requested_class'][sample['entity_class']] and c['status']=='usable']
        selected=candidates[0] if len(candidates)==1 else None
        if selected and file_hash(selected['image'])!=selected['image_sha256']:raise ValueError('crop changed')
        classes=sorted({c['class_name'] for c in cached[eid] if c['frame_index']==sample['frame_index'] and c['kind']=='target'})
        evidence.append({'sample_id':sample['sample_id'],'entity_id':sample['entity_id'],'video_sha256':sample['video_sha256'],'image_sha256':sample['image_sha256'],
            'crop':selected,'binding_status':'single_requested_class' if selected else 'ambiguous_class_instances' if len(candidates)>1 else 'no_accepted_requested_class',
            'hint':POLICY['hints'].format(classes=', '.join(classes) if classes else 'none accepted'),'wrong_hint':POLICY['wrong_hints']})
    manifest={'policy':POLICY,'source_run_id':run['run_id'],'source_manifest_sha256':file_hash(derived/'run.json'),'samples':evidence}
    manifest['id']=digest(manifest);write_json(destination,manifest);return manifest


def encode(samples,region_manifest,base_cache,model_path,destination):
    dest=Path(destination)
    if dest.exists():raise ValueError('new region feature directory required')
    manifest=json.loads(Path(region_manifest).read_text())
    if manifest['policy']!=POLICY:raise ValueError('region policy mismatch')
    if [r['sample_id'] for r in manifest['samples']]!=[s['sample_id'] for s in samples]:raise ValueError('region sample order mismatch')
    base,original=load_cache(base_cache,samples)
    encoder=QwenEmbedder(model_path)
    if encoder.space.artifacts!=base['space']['artifacts']:raise ValueError('model artifact mismatch')
    arrays={c:np.zeros_like(original['images']) for c in CONDITIONS};arrays['F']=original['images'].copy()
    available={c:np.ones(len(samples),dtype=bool) for c in CONDITIONS};timings=[]
    for i,(s,r) in enumerate(zip(samples,manifest['samples'])):
        if r['entity_id']!=s['entity_id'] or r['image_sha256']!=file_hash(s['image']):raise ValueError('region evidence/entity mismatch')
        with Image.open(s['image']) as im:full=im.convert('RGB').resize((320,240),Image.Resampling.BICUBIC)
        images=[full]
        crop=r['crop']
        if crop:
            if file_hash(crop['image'])!=crop['image_sha256']:raise ValueError('region crop changed')
            with Image.open(crop['image']) as im:cropped=im.convert('RGB')
            arrays['C'][i]=encoder.image(cropped)
            arrays['FC'][i]=normalize((arrays['F'][i]+arrays['C'][i])[None])[0]
            images.append(cropped)
        else:
            available['C'][i]=False;arrays['FC'][i]=arrays['F'][i]
        for condition,text in [('FCH',r['hint']),('FCW',r['wrong_hint'])]:
            content=[{'type':'image'} for _ in images]+[{'type':'text','text':text}]
            arrays[condition][i]=encoder._encode(content,images=images)
        arrays['H'][i]=encoder.text(r['hint'])
        if i%24==0:print(f'region features {i+1}/{len(samples)}',flush=True)
    dest.mkdir(parents=True)
    for c in CONDITIONS:arrays[c+'__available']=available[c]
    for entity in ('fridge','microwave'):arrays[entity+'__hypotheses']=original[entity+'__generic']
    np.savez_compressed(dest/'features.npz',**arrays)
    metadata={'manifest_id':manifest['id'],'manifest_sha256':file_hash(region_manifest),'policy':POLICY,'encoder_space':asdict(encoder.space),'base_space':base['feature_space_id'],'base_cache_sha256':base['features_sha256'],
        'spaces':{c:digest([base['feature_space_id'],manifest['id'],c,POLICY,file_hash(Path(__file__))]) for c in CONDITIONS},'features_sha256':file_hash(dest/'features.npz'),
        'encode_seconds':encoder.timings,'limitations':['FC uses up to twice F pixel budget; duplicate-full fusion equals F numerically and is the matched-count redundancy control.','FCH/FCW jointly encode images and hints; their difference measures wrong-hint sensitivity, not a pure crop effect.','No accepted crop does not imply the requested object is absent.']}
    write_json(dest/'metadata.json',metadata)
    return metadata
