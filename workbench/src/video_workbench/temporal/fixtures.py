"""Numerical oracle fixtures, explicitly not rendered-video measurements."""
import numpy as np
from .data import Sequence

CLASSES=('OPEN','WALK','CLOSE','OTHER')
PATTERNS={'normal':(0,1,2,0,1),'omission':(0,1,0,1),'repetition':(0,1,2,0,1,0,1),'gap':(0,1,2,0,1)}


def oracle_sequences(seed=0):
    rng=np.random.default_rng(seed);result={}
    for name,pattern in PATTERNS.items():
        target=np.repeat(pattern,4);n=len(target)
        x=np.eye(len(CLASSES))[target]+rng.normal(0,.08,(n,len(CLASSES)))
        valid=np.ones(n,dtype=bool)
        if name=='gap':valid[8:12]=False;x[~valid]=0
        # Deliberately irregular grid: index counts are not elapsed duration.
        ends=np.cumsum(np.resize([200_000,400_000,300_000],n)).astype(np.int64)
        starts=np.r_[0,ends[:-1]]
        result[name]=Sequence(f'oracle-{name}-{seed}','oracle-one-hot-noisy-v1',x,starts,ends,ends.copy(),valid,
                              np.ones(n,dtype=bool),target,[('oracle:'+str(i),) if valid[i] else () for i in range(n)]).validate(len(CLASSES))
    return result
