"""Development-selected real-feature comparison; weak labels are evaluators only."""
from pathlib import Path
import json
import time
import numpy as np
from video_workbench.registry import file_hash
from video_workbench.perception.store import write_json
from .benchmark import load_sequences
from .linear import predict
from .classical import MODES,training_prior,decode


def run(dataset,features,linear_result,destination):
    dest=Path(destination)
    if dest.exists():raise ValueError('fresh classical destination required')
    classes,sequences,manifest,fm=load_sequences(dataset,features)
    baseline=json.loads(Path(linear_result).read_text())
    if baseline['inputs_sha256']!=manifest['inputs_sha256'] or baseline['labels_sha256']!=manifest['labels_sha256'] or baseline['features_manifest_sha256']!=file_hash(Path(features)/'manifest.json'):raise ValueError('baseline provenance mismatch')
    model=baseline['model'];train=[s for split,s in sequences if split=='train']
    if set(model['training_episodes'])!={s.episode_id for s in train}:raise ValueError('baseline training partition mismatch')
    a,pi=training_prior(train,len(classes))
    scores={s.episode_id:predict(model,s)[0] for _,s in sequences}
    def evaluate(method,settings,split):
        episodes={};pairs=[];start=time.perf_counter()
        for part,s in sequences:
            if part!=split:continue
            record=decode(s,scores[s.episode_id],method,a,pi,**settings)
            pred=np.array(record['predictions']);mask=s.loss_mask
            pairs.extend(zip(s.targets[mask].tolist(),pred[mask].tolist()))
            record.update(targets=s.targets.tolist(),label_mask=s.label_mask.tolist())
            episodes[s.episode_id]=record
        per={name:{'n':sum(y==k for y,p in pairs),'correct':sum(y==k and p==k for y,p in pairs)} for k,name in enumerate(classes)}
        recalls=[r['correct']/r['n'] for r in per.values() if r['n']]
        return {'weak_interior_accuracy':sum(y==p for y,p in pairs)/len(pairs),
                'macro_recall':float(np.mean(recalls)),'n':len(pairs),'per_class':per,
                'unknown_predictions':sum(p<0 for y,p in pairs),'episodes':episodes,
                'wall_seconds':time.perf_counter()-start}
    results={}
    for method in MODES:
        candidates=[{}] if method=='linear' else ([{'persistence_us':x} for x in (0,500000,1000000)] if method=='hysteresis' else ([{'strength':x,'duration_mean':d} for x in (0.,.25,1.) for d in (2,4,8)] if method=='hsmm' else [{'strength':x} for x in (0.,.25,1.)]))
        selected=[]
        for settings in candidates:
            dev=evaluate(method,settings,'development');selected.append((dev['macro_recall'],settings))
        best=max(range(len(selected)),key=lambda i:selected[i][0]);settings=selected[best][1]
        results[method]={'mode':MODES[method],'settings':settings,
                         'development_candidates':[{'settings':s,'macro_recall':r} for r,s in selected],
                         'metrics':{split:evaluate(method,settings,split) for split in ('train','development','test')}}
        print(method,settings,results[method]['metrics']['test']['macro_recall'],flush=True)
    result={'kind':'weak program-interior classical comparison; no exact boundary metrics',
            'selection':'development macro recall; first candidate wins ties',
            'code_sha256':{name:file_hash(Path(__file__).parent/name) for name in ('classical_benchmark.py','classical.py','hmm.py','duration.py','hysteresis.py','benchmark.py')},
            'classes':classes,'linear_result_sha256':file_hash(linear_result),
            'features_manifest_sha256':file_hash(Path(features)/'manifest.json'),
            'transition_prior':{'fit_episodes':[s.episode_id for s in train],'log_a':a.tolist(),'log_pi':pi.tolist(),'policy':'Laplace-smoothed adjacent known train labels; no bridges through masked cells'},
            'methods':results,'limitations':['Weak overlapping labels, small within-scene corpus.','Discriminative scores and duration preferences are not calibrated probabilities.','Temporal outputs use source-horizon availability, excluding compute latency.']}
    dest.mkdir(parents=True);write_json(dest/'results.json',result);return result
