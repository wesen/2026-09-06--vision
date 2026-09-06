"""Join weak labels after encoding and evaluate a development-selected baseline."""
from pathlib import Path
import json
import numpy as np
from video_workbench.registry import file_hash
from video_workbench.perception.store import write_json
from .data import Sequence
from .linear import fit,predict


def load_sequences(dataset,features):
    root=Path(dataset);cache=Path(features)
    manifest=json.loads((root/'manifest.json').read_text());fm=json.loads((cache/'manifest.json').read_text())
    if file_hash(root/'inputs.json')!=manifest['inputs_sha256'] or file_hash(root/'weak-labels.json')!=manifest['labels_sha256'] or fm['spec']['inputs_sha256']!=manifest['inputs_sha256'] or file_hash(cache/'features.npz')!=fm['features_sha256']:raise ValueError('sequence artifact mismatch')
    rows=json.loads((root/'inputs.json').read_text());labels=json.loads((root/'weak-labels.json').read_text());by_label={l['sample_id']:l for l in labels}
    if fm['sample_ids']!=[r['sample_id'] for r in rows] or set(by_label)!=set(fm['sample_ids']):raise ValueError('sequence row identity mismatch')
    if len(by_label)!=len(labels) or len(set(fm['sample_ids']))!=len(rows):raise ValueError('duplicate sample identity')
    classes=manifest['classes']
    with np.load(cache/'features.npz') as archive:
        feature_values=archive['features'];valid_values=archive['valid']
    groups={}
    for i,r in enumerate(rows):groups.setdefault((r['episode_id'],r['split']),[]).append(i)
    sequences=[]
    for (eid,split),indices in groups.items():
        rr=[rows[i] for i in indices];ll=[by_label[r['sample_id']] for r in rr]
        s=Sequence(eid,fm['space_id'],feature_values[indices],np.array([r['start_us'] for r in rr]),np.array([r['end_us'] for r in rr]),np.array([r['available_us'] for r in rr]),valid_values[indices],np.array([l['label_mask'] for l in ll]),np.array([classes.index(l['action']) if l['label_mask'] else -1 for l in ll]),[(r['sample_id'],) for r in rr]).validate(len(classes));sequences.append((split,s))
    return classes,sequences,manifest,fm


def run(dataset,features,destination):
    dest=Path(destination);cache=Path(features)
    if dest.exists():raise ValueError('new baseline destination required')
    classes,sequences,manifest,fm=load_sequences(dataset,features)
    def evaluate(model,split):
        pairs=[];episodes={}
        for part,s in sequences:
            if part!=split:continue
            _,p=predict(model,s);mask=s.loss_mask;pairs.extend(zip(s.targets[mask].tolist(),p[mask].tolist()));episodes[s.episode_id]={'predictions':p.tolist(),'targets':s.targets.tolist(),'label_mask':mask.tolist(),'end_us':s.end_us.tolist()}
        per={name:{'n':sum(y==i for y,p in pairs),'correct':sum(y==i and p==i for y,p in pairs)} for i,name in enumerate(classes)}
        recalls=[r['correct']/r['n'] for r in per.values() if r['n']]
        return {'weak_interior_accuracy':sum(y==p for y,p in pairs)/len(pairs),'macro_recall':sum(recalls)/len(recalls),'n':len(pairs),'per_class':per,'episodes':episodes}
    train=[s for split,s in sequences if split=='train'];candidates=[]
    for ridge in (.01,.1,1.):
        model=fit(train,len(classes),ridge);dev=evaluate(model,'development');candidates.append((dev['macro_recall'],ridge,model))
    _,ridge,model=max(candidates,key=lambda r:(r[0],-r[1]))
    result={'kind':'weak program-interior video baseline; not reviewed dense action accuracy','classes':classes,'selected_ridge':ridge,'selection':'development macro recall','candidates':[{'ridge':r,'development_macro_recall':score} for score,r,m in candidates],'model':model,'metrics':{s:evaluate(model,s) for s in ('train','development','test')},'inputs_sha256':manifest['inputs_sha256'],'labels_sha256':manifest['labels_sha256'],'features_manifest_sha256':file_hash(cache/'manifest.json')}
    dest.mkdir(parents=True);write_json(dest/'results.json',result);return result
