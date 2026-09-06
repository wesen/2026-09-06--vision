from itertools import product
import numpy as np
import pytest
from video_workbench.temporal.hmm import forward,filter,smooth,viterbi,logsumexp
from video_workbench.temporal.duration import hsmm_viterbi
from video_workbench.temporal.hysteresis import Hysteresis


def test_hmm_all_paths_marginals_and_prefix_causality():
    rng=np.random.default_rng(42)
    e=rng.normal(size=(4,2));a=rng.normal(size=(2,2));pi=rng.normal(size=2)
    paths=list(product(range(2),repeat=4))
    weights=np.array([np.exp(pi[p[0]]+sum(e[t,p[t]] for t in range(4))+sum(a[p[t-1],p[t]] for t in range(1,4))) for p in paths])
    alpha,z=forward(e,a,pi);marginal,_=smooth(e,a,pi);best,score=viterbi(e,a,pi)
    assert np.exp(z)==pytest.approx(weights.sum())
    assert tuple(best)==paths[weights.argmax()]
    assert np.exp(score)==pytest.approx(weights.max())
    for t in range(4):
        for k in range(2):assert marginal[t,k]==pytest.approx(sum(w for p,w in zip(paths,weights) if p[t]==k)/weights.sum())
    changed=e.copy();changed[2:]=99
    assert np.allclose(filter(e,a,pi)[:2],filter(changed,a,pi)[:2])
    assert np.allclose(filter(e,a,pi)[1],filter(e[:2],a,pi)[-1])
    assert logsumexp([-np.inf,-np.inf])==-np.inf
    with pytest.raises(ValueError,match='admissible'):viterbi(e,a,np.full(2,-np.inf))
    with pytest.raises(ValueError,match='admissible'):filter(e,a,np.full(2,-np.inf))


def runs(path):
    starts=[0]+[i for i in range(1,len(path)) if path[i]!=path[i-1]]
    return [(s,e,path[s]) for s,e in zip(starts,starts[1:]+[len(path)])]


def test_hsmm_matches_exhaustive_completed_segments():
    rng=np.random.default_rng(7)
    e=rng.normal(size=(5,2));a=rng.normal(size=(2,2));pi=rng.normal(size=2);d=rng.normal(size=(2,3))
    candidates=[]
    for path in product(range(2),repeat=5):
        segments=runs(path)
        if any(end-start>3 for start,end,k in segments):continue
        score=pi[path[0]]+sum(e[t,path[t]] for t in range(5))+sum(d[k,end-start-1] for start,end,k in segments)+sum(a[left[2],right[2]] for left,right in zip(segments,segments[1:]))
        candidates.append((score,segments))
    expected=max(candidates,key=lambda pair:pair[0]);segments,score=hsmm_viterbi(e,a,pi,d)
    assert segments==expected[1] and score==pytest.approx(expected[0])
    with pytest.raises(ValueError,match='admissible'):hsmm_viterbi(e,a,pi,np.full((2,3),-np.inf))


def test_hysteresis_uses_elapsed_time_resets_gaps_and_delays_short_events():
    h=Hysteresis(persistence_us=100,max_gap_us=200)
    assert [h.update(t,k) for t,k in [(0,0),(20,0),(99,0),(100,0),(120,1),(200,0)]]==[-1,-1,-1,0,0,0]
    assert h.update(210,None)==-1
    assert h.update(220,1)==-1
    assert h.update(500,1)==-1  # gap cancels the previous candidate
    assert h.update(600,1)==1
    with pytest.raises(ValueError,match='increase'):h.update(600,1)


def test_unconstrained_oracle_preserves_omission_and_repeated_open():
    from video_workbench.temporal.fixtures import oracle_sequences
    from video_workbench.temporal.linear import fit,predict
    model=fit(list(oracle_sequences(1).values()),3)
    for name in ('omission','repetition'):
        s=oracle_sequences(2)[name];score,_=predict(model,s)
        # Scored decoder: unrestricted transitions must not impose a procedure.
        p,_=viterbi(score,np.zeros((3,3)),np.zeros(3))
        assert np.array_equal(p,s.targets)
        if name=='omission':assert 2 not in p
        else:assert sum(k==0 for start,end,k in runs(p))==3
