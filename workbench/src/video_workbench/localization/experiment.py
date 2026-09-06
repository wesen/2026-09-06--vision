"""State diagnostic on frozen localization features; no held-out fitting."""
from dataclasses import asdict
import json
from pathlib import Path
import numpy as np
from video_workbench.embedding import digest
from video_workbench.registry import file_hash
from video_workbench.perception.store import write_json
from video_workbench.predicates.contracts import load_dataset, StateObservation
from video_workbench.predicates.classify import fit_head, head_scores, margins, fit_calibration, probabilities, select_policy
from video_workbench.predicates.region_experiment import score_predictions
from .features import CONDITIONS
from .crops import POLICY


def run(samples_path, labels_path, manifest_path, features_path, destination):
    dest = Path(destination)
    if dest.exists():
        raise ValueError('new state comparison directory required')
    samples, labels = load_dataset(samples_path, labels_path)
    manifest = json.loads(Path(manifest_path).read_text())
    cache = Path(features_path)
    metadata = json.loads((cache/'metadata.json').read_text())
    producer = metadata['producer']
    if (manifest['policy'] != POLICY or metadata['status'] != 'complete'
            or digest(producer) != metadata['producer_id']
            or producer['manifest_sha256'] != file_hash(manifest_path)
            or metadata['features_sha256'] != file_hash(cache/'features.npz')):
        raise ValueError('feature protocol or artifact mismatch')
    evidence = [s for s in manifest['samples'] if any(a['kind']=='state' for a in s['aliases'])]
    if producer['samples'] != [s['sample_id'] for s in evidence]:
        raise ValueError('feature row order mismatch')
    state_by_id = {s['sample_id']: (s,l) for s,l in zip(samples,labels)}
    ordered = []
    for e in evidence:
        aliases = [a['id'] for a in e['aliases'] if a['kind']=='state']
        if len(aliases)!=1 or aliases[0] not in state_by_id:
            raise ValueError('state alias mismatch')
        s,l = state_by_id[aliases[0]]
        for key in ('episode_id','entity_id','image_sha256','video_sha256','frame_index','split'):
            if s[key]!=e[key]: raise ValueError('state evidence identity mismatch')
        if s['sample_us']!=e['pts_us']: raise ValueError('state evidence clock mismatch')
        ordered.append((s,l))
    if len(ordered)!=len(samples) or len({s['sample_id'] for s,l in ordered})!=len(samples):
        raise ValueError('state population mismatch')
    samples,labels = map(list,zip(*ordered))
    with np.load(cache/'features.npz',allow_pickle=False) as archive:
        arrays = {k:archive[k] for k in archive.files}
    for c in CONDITIONS:
        x,mask=arrays[c],arrays[c+'__available']
        if (x.shape!=(len(samples),producer['encoder']['dimension']) or mask.shape!=(len(samples),)
                or mask.dtype!=np.bool_ or not np.isfinite(x).all()
                or not np.allclose(np.linalg.norm(x[mask],axis=1),1,atol=1e-4)
                or not (x[~mask]==0).all()):
            raise ValueError('invalid feature shape, mask, or normalization')
        if metadata['spaces'][c]!=digest([producer,c]):raise ValueError('condition space mismatch')
    results={'conditions':{},'labels_sha256':file_hash(labels_path),'features_sha256':metadata['features_sha256'],
             'feature_metadata_sha256':file_hash(cache/'metadata.json'),'policy':POLICY,
             'limitations':['Previously inspected test partition: exploratory, not fresh generalization.','Oracle O/FO use reviewed locations.','Offline availability excludes processing latency.','One reviewer; apartment and class confounds remain.']}
    observations=[]
    common=arrays['D__available'] & arrays['O__available']
    for c in CONDITIONS:
        x=arrays[c];available=arrays[c+'__available'];space=metadata['spaces'][c]
        train=[i for i,s in enumerate(samples) if s['split']=='train' and available[i] and labels[i].value is not None]
        dev=[i for i,s in enumerate(samples) if s['split']=='development' and available[i] and labels[i].value is not None]
        if {labels[i].value for i in train}!={True,False} or {labels[i].value for i in dev}!={True,False}:
            raise ValueError(f'insufficient train/development classes for {c}')
        head=fit_head(x[train],[labels[i].value for i in train],space,{samples[i]['entity_class'] for i in train})
        scores={'linear_head':head_scores(head,x,space,{s['entity_class'] for s in samples}),
                'text_margin':np.array([margins(x[i:i+1],arrays[s['entity_class']+'__hypotheses'])[0] for i,s in enumerate(samples)])}
        for method,raw in scores.items():
            calibration=fit_calibration(raw[dev],[labels[i].value for i in dev])
            p=probabilities(calibration,raw);policy=select_policy(p[dev],[labels[i].value for i in dev])
            spec={'condition':c,'method':method,'space':space,'head':head if method=='linear_head' else None,
                  'calibration':calibration,'policy':policy,'train_ids':[samples[i]['sample_id'] for i in train],
                  'development_ids':[samples[i]['sample_id'] for i in dev],'labels_sha256':results['labels_sha256'],
                  'feature_metadata_sha256':results['feature_metadata_sha256'],
                  'code_sha256':{str(path):file_hash(path) for path in [Path(__file__),Path(__file__).parents[1]/'predicates/classify.py',Path(__file__).parents[1]/'predicates/region_experiment.py']}}
            pid=digest(spec);name=c+'__'+method;metrics={};paired={}
            for split in ('train','development','test'):
                indices=[i for i,s in enumerate(samples) if s['split']==split]
                metrics[split]=score_predictions(p[indices],[labels[i] for i in indices],available[indices],policy)
                shared=[i for i in indices if common[i]]
                paired[split]={'n':len(shared),'metrics':score_predictions(p[shared],[labels[i] for i in shared],available[shared],policy) if shared else None}
            results['conditions'][name]={'spec':spec,'producer_id':pid,'metrics':metrics,'paired_F_D_O':paired}
            for i,(s,e) in enumerate(zip(samples,evidence)):
                missing=not available[i];abstain=missing or abs(p[i]-policy['threshold'])<policy['radius']
                used=['F'] if c=='F' else [c] if c in ('D','O') else ['F',c[1]]
                ids=tuple(e[k]['evidence_id'] for k in used if e[k] is not None)
                # Missing inference cites the requested source for traceability only.
                if not ids:ids=(e['sample_id'],)
                obs=StateObservation(s['sample_id'],s['episode_id'],s['entity_id'],s['property'],s['sample_us'],s['sample_us'],
                    'offline-source-horizon-only; processing latency not modeled',None if abstain else bool(p[i]>=policy['threshold']),
                    None if missing else float(raw[i]),None if missing else float(p[i]),
                    'missing_crop' if missing else 'development_abstention_band' if abstain else None,ids,space,pid)
                observations.append(dict(asdict(obs),condition=name,split=s['split'],oracle_assisted=c in ('O','FO'),evidence_available=bool(available[i])))
    dest.mkdir(parents=True);write_json(dest/'results.json',results)
    (dest/'observations.jsonl').write_text(''.join(json.dumps(o,allow_nan=False)+'\n' for o in observations))
    write_json(dest/'manifest.json',{'status':'complete','artifacts':{n:file_hash(dest/n) for n in ('results.json','observations.jsonl')}})
    return results
