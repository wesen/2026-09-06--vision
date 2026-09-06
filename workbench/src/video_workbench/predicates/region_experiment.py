"""Fixed-source representation comparison; fit only train/development rows."""
from pathlib import Path
from dataclasses import asdict
import json
import numpy as np
from video_workbench.embedding import digest
from video_workbench.registry import file_hash
from video_workbench.perception.store import write_json
from .contracts import load_dataset,StateObservation
from .classify import fit_head,head_scores,margins,fit_calibration,probabilities,select_policy,evaluate,confusion,macro_f1
from .regions import CONDITIONS,POLICY


def score_predictions(probability,labels,available,policy):
    available=np.asarray(available,dtype=bool);known=np.array([l.value is not None for l in labels]);y=np.array([l.value is True for l in labels])
    answer=available&(np.abs(probability-policy['threshold'])>=policy['radius']);pred=probability>=policy['threshold']
    correct=int((answer&known&(pred==y)).sum());errors=int((answer&known&(pred!=y)).sum())
    counts=confusion(y[known&available],pred[known&available])
    return {'n':len(labels),'known':int(known.sum()),'unknown':int((~known).sum()),'evidence_available':int(available.sum()),'missing_evidence':int((~available).sum()),
        'answered':int(answer.sum()),'coverage':float(answer.mean()),'known_answered':int((answer&known).sum()),'known_errors':errors,'known_selective_risk':errors/int((answer&known).sum()) if (answer&known).any() else None,
        'known_correct_over_all_known':correct/int(known.sum()) if known.any() else None,'unknown_false_certainty':int((answer&~known).sum()),
        'available_visible_confusion_before_abstention':counts,'available_visible_macro_f1_before_abstention':macro_f1(counts) if (known&available).any() else None}


def run(samples_path,labels_path,manifest_path,features_path,destination):
    samples,labels=load_dataset(samples_path,labels_path)
    manifest=json.loads(Path(manifest_path).read_text());cache=Path(features_path);metadata=json.loads((cache/'metadata.json').read_text())
    if metadata['manifest_sha256']!=file_hash(manifest_path) or manifest['policy']!=POLICY or metadata['features_sha256']!=file_hash(cache/'features.npz'):
        raise ValueError('region cache/protocol mismatch')
    with np.load(cache/'features.npz',allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
    dest=Path(destination)
    if dest.exists():raise ValueError('new comparison destination required')
    result={'policy':POLICY,'feature_metadata':metadata,'manifest_id':manifest['id'],'label_sha256':file_hash(labels_path),'sample_sha256':file_hash(samples_path),
        'code_sha256':{p.name:file_hash(p) for p in Path(__file__).parent.glob('*.py')},'conditions':{},'limitations':['Same test scenes previously inspected; exploratory follow-up, not a new blind test.','One apartment per split and only two open development/test frames.','C-only coverage differs; compare correct/all-known and missing counts, not conditional F1 alone.','Correct detector hints contain false predictions as well as true objects.','No generative verifier quality claim; these are frozen embedding baselines.']}
    observations=[]
    common=np.asarray(arrays['C__available'],dtype=bool)
    for condition in CONDITIONS:
        x=arrays[condition];available=np.asarray(arrays[condition+'__available'],dtype=bool);space=metadata['spaces'][condition]
        if x.shape!=(len(samples),2048) or not np.isfinite(x).all():raise ValueError('invalid region features')
        if not np.allclose(np.linalg.norm(x[available],axis=1),1,atol=1e-4):raise ValueError('nonunit region features')
        train=[i for i,s in enumerate(samples) if s['split']=='train' and labels[i].value is not None and available[i]]
        dev=[i for i,s in enumerate(samples) if s['split']=='development' and labels[i].value is not None and available[i]]
        if {labels[i].value for i in train}!={True,False} or {labels[i].value for i in dev}!={True,False}:
            result['conditions'][condition]={'status':'insufficient_training_or_development_classes','train_rows':len(train),'development_rows':len(dev)};continue
        head=fit_head(x[train],[labels[i].value for i in train],space,{samples[i]['entity_class'] for i in train})
        raw_text=np.array([margins(x[i:i+1],arrays[s['entity_class']+'__hypotheses'])[0] for i,s in enumerate(samples)])
        raw_linear=head_scores(head,x,space,{s['entity_class'] for s in samples})
        for kind,raw in [('text_margin',raw_text),('linear_head',raw_linear)]:
            cal=fit_calibration(raw[dev],[labels[i].value for i in dev]);p=probabilities(cal,raw);policy=select_policy(p[dev],[labels[i].value for i in dev])
            name=condition+'__'+kind;spec={'condition':condition,'kind':kind,'space_id':space,'calibration':cal,'policy':policy,'train_ids':[samples[i]['sample_id'] for i in train],'development_ids':[samples[i]['sample_id'] for i in dev],'head':head if kind=='linear_head' else None,'manifest_id':manifest['id'],'label_sha256':result['label_sha256'],'code_sha256':result['code_sha256']}
            producer=digest(spec);metrics={};paired={}
            for split in ('train','development','test'):
                indices=[i for i,s in enumerate(samples) if s['split']==split]
                metrics[split]=score_predictions(p[indices],[labels[i] for i in indices],available[indices],policy)
                shared=[i for i in indices if common[i]]
                paired[split]=score_predictions(p[shared],[labels[i] for i in shared],available[shared],policy) if shared else None
            result['conditions'][name]={'status':'evaluated','producer_id':producer,'spec':spec,'metrics':metrics,'common_crop_subset':paired}
            for i,s in enumerate(samples):
                missing=not available[i];abstain=missing or abs(p[i]-policy['threshold'])<policy['radius']
                # Offline fixture availability: evidence PTS only, explicitly not measured live latency.
                observation=StateObservation(s['sample_id'],s['episode_id'],s['entity_id'],s['property'],s['sample_us'],s['sample_us'],'offline-source-horizon-only; processing latency not modeled',
                    None if abstain else bool(p[i]>=policy['threshold']),None if missing else float(raw[i]),None if missing else float(p[i]),'missing_or_ambiguous_detector_crop' if missing else 'development_abstention_band' if abstain else None,
                    (s['sample_id'],) if not manifest['samples'][i]['crop'] or condition in {'F','H'} else (s['sample_id'],manifest['samples'][i]['crop']['evidence_id']),space,producer)
                observations.append(dict(asdict(observation),condition=name,split=s['split']))
    result['run_id']=digest(result)
    dest.mkdir(parents=True);write_json(dest/'results.json',result)
    (dest/'observations.jsonl').write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in observations))
    print(json.dumps({n:r.get('metrics',{}).get('test',r) for n,r in result['conditions'].items()},indent=2))
    return result
