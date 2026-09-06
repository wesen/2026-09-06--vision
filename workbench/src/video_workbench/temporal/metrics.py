"""Exact metrics for numerical or reviewed dense labels, never weak interiors."""
import numpy as np


def segments(labels,valid,starts,ends):
    labels=np.asarray(labels);valid=np.asarray(valid);starts=np.asarray(starts);ends=np.asarray(ends)
    if labels.ndim!=1 or valid.shape!=labels.shape or starts.shape!=labels.shape or ends.shape!=labels.shape:raise ValueError('metric shapes differ')
    if np.any(ends<=starts) or np.any(starts[1:]<ends[:-1]):raise ValueError('positive nonoverlapping output cells required')
    result=[]
    for k,ok,a,b in zip(labels,valid,starts,ends):
        if not ok or k<0:continue
        if result and result[-1][2]==k and result[-1][1]==a:result[-1]=(result[-1][0],int(b),int(k))
        else:result.append((int(a),int(b),int(k)))
    return result


def segment_metrics(prediction,truth,valid,starts,ends,threshold=.5,short_us=1500000):
    if not 0<threshold<=1:raise ValueError('IoU threshold must be in (0,1]')
    p=segments(prediction,valid,starts,ends);g=segments(truth,valid,starts,ends)
    # Standard temporal-order greedy matching, one truth match per prediction.
    matched=set();tp=0
    for a,b,k in p:
        options=[]
        for j,(c,d,label) in enumerate(g):
            if label!=k or j in matched:continue
            intersection=max(0,min(b,d)-max(a,c));iou=intersection/((b-a)+(d-c)-intersection)
            options.append((iou,-j,j))
        if options:
            iou,_,j=max(options)
            if iou>=threshold:matched.add(j);tp+=1
    fp=len(p)-tp;fn=len(g)-tp;den=2*tp+fp+fn
    previous=list(range(len(g)+1))
    for i,(_,_,label) in enumerate(p,1):
        current=[i]
        for j,(_,_,target) in enumerate(g,1):current.append(min(current[-1]+1,previous[j]+1,previous[j-1]+int(label!=target)))
        previous=current
    short=[i for i,(a,b,k) in enumerate(g) if b-a<=short_us]
    return {'iou_threshold':threshold,'tp':tp,'fp':fp,'fn':fn,'segment_f1':2*tp/den if den else 1.,
            'normalized_edit_score':1-previous[-1]/max(len(p),len(g),1),
            'short_action_max_us':short_us,'short_action_count':len(short),
            'short_action_recall':sum(i in matched for i in short)/len(short) if short else None,
            'truth_segments':g,'prediction_segments':p,'matching':'temporal-order greedy maximum IoU; one-to-one; negative labels excluded; validity gaps retained'}
