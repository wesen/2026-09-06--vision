"""Capability-tagged classical inference on frozen features.

Missing observations split runs. Filtering and hysteresis are causal; full-run
smoothing and joint decoding become available only after the run's last input.
Event cells [previous feature end, feature end) describe output-grid support,
not reviewed action boundaries or continuous visual evidence.
"""
import numpy as np
from .hmm import filter,smooth,viterbi
from .duration import hsmm_viterbi
from .hysteresis import Hysteresis

MODES={'linear':'causal','hysteresis':'causal','filter':'causal',
       'smooth':'offline','viterbi':'offline','hsmm':'offline'}


def valid_runs(valid):
    padded=np.r_[False,valid,False]
    return list(zip(np.flatnonzero(~padded[:-1]&padded[1:]),
                    np.flatnonzero(padded[:-1]&~padded[1:])))


def training_prior(sequences,classes):
    """Laplace-smoothed adjacent known-label counts; never bridge masked cells."""
    transitions=np.ones((classes,classes));initial=np.ones(classes)
    for s in sequences:
        s.validate(classes)
        for start,end in valid_runs(s.loss_mask):
            initial[s.targets[start]]+=1
            for t in range(start+1,end):transitions[s.targets[t-1],s.targets[t]]+=1
    return np.log(transitions/transitions.sum(1,keepdims=True)),np.log(initial/initial.sum())


def decode(sequence,scores,method,log_a,log_pi,strength=0.,duration_mean=4,persistence_us=500000):
    if method not in MODES:raise ValueError('unknown temporal method')
    sequence.validate(len(log_pi))
    scores=np.asarray(scores)
    if scores.shape!=(len(sequence.features),len(log_pi)) or not np.isfinite(scores[sequence.valid]).all():raise ValueError('invalid temporal scores')
    if strength<0 or duration_mean<=0:raise ValueError('invalid decoder parameter')
    pred=np.full(len(scores),-1,dtype=int)
    availability=sequence.available_us.copy()
    if method=='hysteresis':
        gate=Hysteresis(persistence_us,750000)
        for i in range(len(scores)):
            pred[i]=gate.update(int(sequence.end_us[i]),int(scores[i].argmax()) if sequence.valid[i] else None)
            # Prefix state may depend on any earlier delayed input.
        availability=np.maximum.accumulate(availability)
    else:
        for start,end in valid_runs(sequence.valid):
            e=scores[start:end];a=log_a*strength;pi=log_pi*strength
            if method=='linear':p=e.argmax(1)
            elif method=='filter':p=filter(e,a,pi).argmax(1)
            elif method=='smooth':p=smooth(e,a,pi)[0].argmax(1)
            elif method=='viterbi':p=viterbi(e,a,pi)[0]
            else:
                # Explicit scored duration preference; not fitted action duration truth.
                durations=np.arange(1,len(e)+1)
                d=np.tile(-.1*((durations-duration_mean)/duration_mean)**2,(e.shape[1],1))
                segments,_=hsmm_viterbi(e,a,pi,d);p=np.full(len(e),-1,dtype=int)
                for left,right,k in segments:p[left:right]=k
            pred[start:end]=p
            if MODES[method]=='offline':availability[start:end]=int(sequence.available_us[start:end].max())
            elif method=='filter':availability[start:end]=np.maximum.accumulate(sequence.available_us[start:end])
    dependencies=[[] for _ in scores]
    for start,end in valid_runs(sequence.valid):
        for i in range(start,end):
            left,right=(start,end) if MODES[method]=='offline' else ((i,i+1) if method=='linear' else (start,i+1))
            dependencies[i]=sorted({e for ids in sequence.evidence_ids[left:right] for e in ids})
    cells=np.r_[0,sequence.end_us[:-1]]
    return {'mode':MODES[method],'predictions':pred.tolist(),'available_us':availability.tolist(),
            'cell_start_us':cells.tolist(),'cell_end_us':sequence.end_us.tolist(),
            'valid':sequence.valid.tolist(),'evidence_ids':[list(x) for x in sequence.evidence_ids],
            'feature_space_id':sequence.feature_space_id,'dependency_evidence_ids':dependencies,
            'clock_policy':'source-horizon availability; excludes compute latency',
            'boundary_policy':'output grid cells only; no reviewed boundary claim'}
