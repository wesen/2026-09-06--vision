"""Explicit train -> development -> frozen test evaluation and observation export."""
from dataclasses import asdict
from pathlib import Path
import json
import numpy as np
from video_workbench.embedding import digest
from video_workbench.registry import file_hash
from .contracts import StateObservation, load_dataset
from .features import CONDITIONS, extract, load_cache
from .classify import margins, fit_head, head_scores, fit_calibration, probabilities, select_policy, evaluate


def run(samples_path, labels_path, cache_path, destination):
    samples, labels = load_dataset(samples_path, labels_path)
    metadata, arrays = load_cache(cache_path, samples)
    space = metadata['feature_space_id']
    train = [i for i,s in enumerate(samples) if s['split']=='train' and labels[i].value is not None]
    dev = [i for i,s in enumerate(samples) if s['split']=='development' and labels[i].value is not None]
    head = fit_head(arrays['images'][train], [labels[i].value for i in train], space, {samples[i]['entity_class'] for i in train})
    scores = {name:np.zeros(len(samples)) for name in (*CONDITIONS, 'context_only')}
    for i, sample in enumerate(samples):
        entity=sample['entity_class']
        for name in CONDITIONS:
            scores[name][i]=margins(arrays['images'][i:i+1],arrays[entity+'__'+name])[0]
        scores['context_only'][i]=margins(arrays[entity+'__context_only'][None],arrays[entity+'__generic'])[0]
    scores['linear_head']=head_scores(head, arrays['images'], space, {s['entity_class'] for s in samples})
    code={p.name:file_hash(p) for p in Path(__file__).parent.glob('*.py')}
    result={'feature_space_id':space,'feature_metadata':metadata,'labels_sha256':file_hash(Path(labels_path)),
            'samples_sha256':file_hash(Path(samples_path)), 'code_sha256':code, 'head':head,
            'train_ids':[samples[i]['sample_id'] for i in train], 'development_ids':[samples[i]['sample_id'] for i in dev],
            'limitations':['Single assistant RGB review.', 'One apartment per split, correlated frames and only two positive development/test frames.', 'Development calibration and policy selection reuse 24 fridge frames; no calibration guarantee on microwave test.', 'Context variants change text hypotheses only; this is not multimodal context conditioning.', 'Oracle visibility is a labeled diagnostic, not a deployed visibility detector.', 'Availability is a service-time replay estimate, excludes decoding and queueing.', 'Sparse fixed-grid observations do not support precise transition-time metrics.'], 'conditions':{}}
    observations=[]
    for name, raw in scores.items():
        calibration=fit_calibration(raw[dev],[labels[i].value for i in dev])
        p=probabilities(calibration,raw)
        policy=select_policy(p[dev],[labels[i].value for i in dev])
        spec={'condition':name,'calibration':calibration,'policy':policy,'feature_space_id':space,'head_digest':digest(head) if name=='linear_head' else None,'code_sha256':code,'labels_sha256':result['labels_sha256'],'train_ids':result['train_ids'],'development_ids':result['development_ids']}
        producer=digest(spec)
        metrics={}
        for split in ('train','development','test'):
            indices=[i for i,s in enumerate(samples) if s['split']==split]
            metrics[split]=evaluate(p[indices],[labels[i] for i in indices],policy)
        result['conditions'][name]={'producer_id':producer,'spec':spec,'metrics':metrics}
        for i,s in enumerate(samples):
            abstain=abs(float(p[i])-policy['threshold'])<policy['radius']
            latency=0 if name=='context_only' else round(metadata['image_seconds'][i]*1e6)
            observation=StateObservation(s['sample_id'],s['episode_id'],s['entity_id'],s['property'],s['sample_us'],s['sample_us']+latency,
                'sample-plus-image-service-time-replay; excludes decode/queue/head; context-only text precomputed',
                None if abstain else bool(p[i]>=policy['threshold']),float(raw[i]),float(p[i]),'development_abstention_band' if abstain else None,
                (s['sample_id'],),space,producer)
            observations.append(dict(asdict(observation),condition=name,split=s['split']))
    destination=Path(destination)
    if destination.exists():
        raise ValueError('run destination exists; preserve prior runs')
    destination.mkdir(parents=True)
    result['run_id']=digest({k:v for k,v in result.items() if k!='feature_metadata'})
    (destination/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (destination/'observations.jsonl').write_text(''.join(json.dumps(o,allow_nan=False)+'\n' for o in observations))
    (destination/'samples.json').write_text(json.dumps(samples,indent=2)+'\n')
    (destination/'labels.json').write_text(json.dumps([asdict(l) for l in labels],indent=2)+'\n')
    print(json.dumps({n:r['metrics']['test'] for n,r in result['conditions'].items()},indent=2))
    return result
