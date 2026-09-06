"""Numerical decoder comparison; never interpreted as rendered-video accuracy."""
from pathlib import Path
import json
import numpy as np
from video_workbench.temporal.fixtures import oracle_sequences
from video_workbench.temporal.linear import fit,predict
from video_workbench.temporal.hmm import filter,smooth,viterbi
from video_workbench.temporal.duration import hsmm_viterbi
from video_workbench.temporal.hysteresis import Hysteresis

model=fit(list(oracle_sequences(1).values()),3)
a=np.zeros((3,3));pi=np.zeros(3)
constrained=np.full((3,3),-np.inf)
for k in range(3):constrained[k,k]=constrained[k,(k+1)%3]=0
report={'kind':'numerical oracle only','score_policy':'ridge discriminative scores; not calibrated emission probabilities','gap_policy':'split valid contiguous runs and restart decoders; gaps stay -1','methods':{'linear':'causal feature-local','filter':'causal prefix','smooth':'offline full valid run','viterbi':'offline full valid run','hsmm':'offline full valid run; flat durations up to 32 samples','procedure_viterbi':'offline OPEN-WALK-CLOSE cycle or dwell ablation','hysteresis':'causal; 300000us persistence; 500000us max gap'},'episodes':{}}
for name,s in oracle_sequences(2).items():
    score,independent=predict(model,s)
    predictions={key:np.full(len(score),-1,dtype=int) for key in report['methods']};predictions['linear']=independent
    padded=np.r_[False,s.valid,False];starts=np.flatnonzero(~padded[:-1]&padded[1:]);ends=np.flatnonzero(padded[:-1]&~padded[1:])
    for start,end in zip(starts,ends):
        e=score[start:end]
        predictions['filter'][start:end]=filter(e,a,pi).argmax(1)
        predictions['smooth'][start:end]=smooth(e,a,pi)[0].argmax(1)
        predictions['viterbi'][start:end]=viterbi(e,a,pi)[0]
        predictions['procedure_viterbi'][start:end]=viterbi(e,constrained,pi)[0]
        segments,_=hsmm_viterbi(e,a,pi,np.zeros((3,32)))
        for left,right,k in segments:predictions['hsmm'][start+left:start+right]=k
    gate=Hysteresis(300000,500000)
    predictions['hysteresis']=np.array([gate.update(int(t),int(k) if valid else None) for t,k,valid in zip(s.end_us,independent,s.valid)])
    records={}
    for method,p in predictions.items():
        opens=int(np.sum((p==0)&np.r_[True,p[:-1]!=0]))
        records[method]={'predictions':p.tolist(),'correct':int(np.sum(p[s.loss_mask]==s.targets[s.loss_mask])),'supervised':int(s.loss_mask.sum()),'open_runs':opens,'omission_preserved':bool(2 not in p) if name=='omission' else None,'repetition_preserved':opens==3 if name=='repetition' else None,'missing_unclassified':bool((p[~s.valid]==-1).all())}
    report['episodes'][name]={'targets':s.targets.tolist(),'valid':s.valid.tolist(),'end_us':s.end_us.tolist(),'results':records}
p=Path(__file__).resolve().parents[1]/'various/classical-oracle-v1.json';p.write_text(json.dumps(report,indent=2)+'\n')
for name,r in report['episodes'].items():print(name,{m:(x['correct'],x['supervised'],x['open_runs'],x['omission_preserved']) for m,x in r['results'].items()})
