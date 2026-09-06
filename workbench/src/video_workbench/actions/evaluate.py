"""Coverage-aware zero-shot action comparison with development-only abstention."""
from pathlib import Path
import json
import numpy as np
from video_workbench.embedding import digest
from video_workbench.registry import file_hash
from video_workbench.index import write_json
from .data import ACTIONS,OPPOSITES,validate_samples


def classification_metrics(truth,predicted,n_classes=len(ACTIONS)):
    truth=np.asarray(truth,dtype=int);predicted=np.asarray(predicted,dtype=int)
    if truth.shape!=predicted.shape or truth.ndim!=1:raise ValueError('aligned class vectors required')
    if np.any((truth<0)|(truth>=n_classes)|(predicted<0)|(predicted>=n_classes)):raise ValueError('invalid class id')
    c=np.zeros((n_classes,n_classes),dtype=int)
    for a,b in zip(truth,predicted):c[a,b]+=1
    support=c.sum(1);tp=np.diag(c);denom=c.sum(0)+support
    f1=np.divide(2*tp,denom,out=np.zeros(n_classes,dtype=float),where=denom>0)
    recall=np.divide(tp,support,out=np.zeros(n_classes,dtype=float),where=support>0)
    return {'n':len(truth),'confusion':c.tolist(),'support':support.tolist(),
            'accuracy':float(tp.sum()/len(truth)) if len(truth) else None,
            'macro_f1_all_declared':float(f1.mean()) if len(truth) else None,
            'macro_f1_supported':float(f1[support>0].mean()) if np.any(support) else None,
            'balanced_accuracy':float(recall[support>0].mean()) if np.any(support) else None,
            'per_class_f1':f1.tolist()}


def select_abstention(gaps,truth,predicted):
    """Choose maximal coverage under <=20% known risk and zero unknown answers."""
    gaps=np.asarray(gaps);truth=np.asarray(truth);predicted=np.asarray(predicted)
    if gaps.ndim!=1 or gaps.shape!=truth.shape or gaps.shape!=predicted.shape or not len(gaps) or not np.isfinite(gaps).all():raise ValueError('nonempty aligned development vectors required')
    candidates=sorted(set([0.,*map(float,gaps),float(gaps.max()+1e-6)]))
    valid=[]
    for t in candidates:
        answered=gaps>=t;known=truth>=0;count=int((answered&known).sum())
        risk=float((answered&known&(predicted!=truth)).sum()/count) if count else 0.
        if risk<=.2 and not np.any(answered&~known):valid.append((int(answered.sum()),-t,t))
    return {'gap_threshold':max(valid)[2],'selection':'development maximum coverage, <=0.2 known risk, zero unknown answers'}


def interval_union_duration(samples,indices):
    groups={}
    for i in indices:
        s=samples[i];groups.setdefault(s['video_sha256'],[]).append((s['start_us'],s['end_us']))
    total=0
    for intervals in groups.values():
        end=-1
        for a,b in sorted(intervals):
            total+=max(0,b-max(a,end));end=max(end,b)
    return total


def retrieval_metrics(samples,truth,scores,indices):
    """Original-only gallery; reviewed action equality defines relevance."""
    rows=[]
    for c,action in enumerate(ACTIONS):
        relevant=[i for i in indices if truth[i]==c]
        duration=interval_union_duration(samples,relevant)
        ranking=sorted(indices,key=lambda i:(-float(scores[i,c]),samples[i]['sample_id']))
        row={'action':action,'relevant_windows':len(relevant),'relevant_duration_us':duration,
             'ranking':[{'sample_id':samples[i]['sample_id'],'score':float(scores[i,c]),'relevant':bool(truth[i]==c),'episode_id':samples[i]['episode_id']} for i in ranking], 'at_k':{}}
        for k in (1,3,5):
            hits=[i for i in ranking[:k] if truth[i]==c]
            row['at_k'][str(k)]={'success':bool(hits) if relevant else None,'interval_coverage':interval_union_duration(samples,hits)/duration if duration else None}
        rows.append(row)
    return {'relevance':'reviewed action equality; unknown windows remain in original gallery; unsupported queries have undefined metrics','queries':rows,
            'supported_queries':sum(r['relevant_windows']>0 for r in rows),
            'mean_at_k':{str(k):{name:float(np.mean([r['at_k'][str(k)][name] for r in rows if r['relevant_windows']])) if any(r['relevant_windows'] for r in rows) else None for name in ('success','interval_coverage')} for k in (1,3,5)}}


def run(dataset,labels_path,feature_roots,destination):
    data=Path(dataset);dest=Path(destination)
    if dest.exists():raise ValueError('new evaluation destination required')
    protocol=json.loads((data/'protocol.json').read_text());samples=validate_samples(json.loads((data/'samples.json').read_text()))
    if set(feature_roots)!=set(protocol['representations']):raise ValueError('all frozen representations required')
    if file_hash(data/'samples.json')!=protocol['samples_sha256']:raise ValueError('source protocol changed')
    labels=json.loads(Path(labels_path).read_text());byid={l['sample_id']:l for l in labels}
    if len(byid)!=len(labels) or set(byid)!={s['sample_id'] for s in samples}:raise ValueError('review sample mismatch')
    for s in samples:
        l=byid[s['sample_id']]
        if l['visibility'] not in ('visible','partial','ambiguous','unobservable') or not l['rationale'] or not l['reviewer'] or l['source_sha256']!=s['video_sha256']:raise ValueError('review incomplete or source changed')
        if l['action'] is not None and l['action'] not in ACTIONS:raise ValueError('unknown reviewed action')
        if l['visibility'] in ('ambiguous','unobservable') and l['action'] is not None:raise ValueError('uncertain review must remain unknown')
        if l['visibility'] in ('visible','partial') and l['action'] is None:raise ValueError('eligible review requires an action')
    truth=np.array([ACTIONS.index(byid[s['sample_id']]['action']) if byid[s['sample_id']]['action'] is not None else -1 for s in samples])
    loaded={};policies={};dev=np.array([s['split']=='development' for s in samples]);
    for mode,root in feature_roots.items():
        root=Path(root);m=json.loads((root/'manifest.json').read_text())
        if m['spec']['mode']!=mode or m['spec']['samples_sha256']!=file_hash(data/'samples.json') or m['spec']['protocol_sha256']!=file_hash(data/'protocol.json') or m['sample_ids']!=[s['sample_id'] for s in samples] or m['features_sha256']!=file_hash(root/'features.npz'):raise ValueError('feature identity mismatch')
        with np.load(root/'features.npz',allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
        if set(arrays)!={*protocol['interventions'],'queries'}:raise ValueError('feature conditions mismatch')
        if m['actions']!=list(ACTIONS):raise ValueError('query class order mismatch')
        if any(v.shape!=(len(ACTIONS) if k=='queries' else len(samples),2048) for k,v in arrays.items()):raise ValueError('feature row counts mismatch')
        for v in arrays.values():
            if v.ndim!=2 or v.shape[1]!=2048 or not np.isfinite(v).all() or not np.allclose(np.linalg.norm(v,axis=1),1,atol=1e-5):raise ValueError('invalid normalized feature array')
        score=arrays['original']@arrays['queries'].T;rank=np.argsort(-score,axis=1,kind='stable');pred=rank[:,0];gaps=np.take_along_axis(score,rank[:,:1],1)[:,0]-np.take_along_axis(score,rank[:,1:2],1)[:,0]
        policies[mode]=select_abstention(gaps[dev],truth[dev],pred[dev]);loaded[mode]=(m,arrays,score,pred,gaps)
    dest.mkdir(parents=True);write_json(dest/'selected.json',{'protocol_sha256':file_hash(data/'protocol.json'),'labels_sha256':file_hash(labels_path),'policies':policies})
    result={'protocol':protocol,'label_sha256':file_hash(labels_path),'sample_sha256':file_hash(data/'samples.json'),'conditions':{},'limitations':['Candidate requested verbs are weak proposals; primary labels use RGB review.','One apartment per split; source families and target classes are partly confounded.','FP32 native versus FP32 image pooling still differs in token structure; 4-bit is an additional system baseline.','Reversed and static clips are interventions, not newly labeled physical actions.']}
    observations=[]
    for mode,(manifest,arrays,scores,pred,gaps) in loaded.items():
        rows={};interventions={};retrieval={};directions={}
        for split in ('train','development','test'):
            indices=np.array([i for i,s in enumerate(samples) if s['split']==split]);known=indices[truth[indices]>=0];unknown=indices[truth[indices]<0];answered=gaps>=policies[mode]['gap_threshold']
            metric=classification_metrics(truth[known],pred[known]);controls=known[truth[known]==ACTIONS.index('none')]
            metric.update(total=len(indices),eligible=len(known),unknown=len(unknown),review_coverage=len(known)/len(indices),control_count=len(controls),control_false_action=int((pred[controls]!=ACTIONS.index('none')).sum()),
                answered=int(answered[indices].sum()),unknown_answered=int(answered[unknown].sum()),known_answered=int(answered[known].sum()),known_errors=int((answered[known]&(pred[known]!=truth[known])).sum()))
            rows[split]=metric
            retrieval[split]=retrieval_metrics(samples,truth,scores,indices)
            pair_rows=[]
            for i in known:
                action=ACTIONS[truth[i]]
                if action in OPPOSITES:
                    margin=float(scores[i,truth[i]]-scores[i,ACTIONS.index(OPPOSITES[action])])
                    pair_rows.append({'sample_id':samples[i]['sample_id'],'action':action,'margin':margin})
            directions[split]={'rows':pair_rows,'n':len(pair_rows),'positive_margin_accuracy':float(np.mean([r['margin']>0 for r in pair_rows])) if pair_rows else None,'conditioning':'compares reviewed action with its opposite; easier than generic nine-way classification'}
            for transform in ('reverse','repeat_first'):
                changed=arrays[transform]@arrays['queries'].T;details=[]
                for i in known:
                    action=ACTIONS[truth[i]]
                    if action not in OPPOSITES:continue
                    c=truth[i];o=ACTIONS.index(OPPOSITES[action]);orig=float(scores[i,c]-scores[i,o]);other=float(changed[i,c]-changed[i,o]);details.append({'sample_id':samples[i]['sample_id'],'original_margin':orig,'intervened_margin':other,'sign_changed':bool((orig>0)!=(other>0))})
                interventions[split+'__'+transform]={'rows':details,'n':len(details),'sign_changes':sum(r['sign_changed'] for r in details),'mean_abs_margin_change':float(np.mean([abs(r['original_margin']-r['intervened_margin']) for r in details])) if details else None}
        result['conditions'][mode]={'run_id':manifest['run_id'],'space_id':manifest['spec']['space_id'],'metrics':rows,'interventions':interventions,'directions':directions,'retrieval':retrieval,'policy':policies[mode]}
        for i,s in enumerate(samples):observations.append({'sample_id':s['sample_id'],'episode_id':s['episode_id'],'split':s['split'],'mode':mode,'predicted_action':ACTIONS[pred[i]],'accepted':bool(gaps[i]>=policies[mode]['gap_threshold']),'gap':float(gaps[i]),'scores':dict(zip(ACTIONS,map(float,scores[i]))),'available_us':s['available_us'],'source_interval_us':[s['start_us'],s['end_us']],'space_id':manifest['spec']['space_id'],'producer_id':manifest['run_id']})
    result['run_id']=digest(result);write_json(dest/'results.json',result);(dest/'observations.jsonl').write_text(''.join(json.dumps(o)+'\n' for o in observations));return result
