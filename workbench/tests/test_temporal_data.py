import numpy as np
import pytest
from video_workbench.temporal.data import Sequence,trailing_grid


def sequence():
    return Sequence('episode','space',np.array([[1.,0.],[0.,0.],[0.,1.]]),np.array([0,10,30]),np.array([10,20,40]),np.array([10,25,45]),np.array([True,False,True]),np.array([True,True,False]),np.array([0,1,-1]),[('a',),(),('c',)])


def test_missing_feature_is_not_background_or_supervised():
    s=sequence().validate(2)
    assert s.loss_mask.tolist()==[True,False,False]
    assert s.available_indices(40).tolist()==[0]
    assert s.available_indices(45).tolist()==[0,2]
    assert s.segment_time(0,3)=={'bounds_us':[0,40],'evidence_coverage_us':[[0,10],[30,40]],'contains_missing_features':True}


def test_future_horizon_and_nonfinite_are_rejected():
    s=sequence();s.available_us[-1]=39
    with pytest.raises(ValueError,match='horizon'):s.validate(2)
    s=sequence();s.features[0,0]=np.nan
    with pytest.raises(ValueError,match='finite'):s.validate(2)
    s=sequence();s.targets[0]=2
    with pytest.raises(ValueError,match='target'):s.validate(2)


def test_irregular_native_grid_and_half_open_end():
    grid=trailing_grid([0,100,400,900],1000,window_us=500,stride_us=300)
    assert [r['end_us'] for r in grid]==[300,600,900,1000]
    assert [r['source_indices'] for r in grid]==[[0,1],[1,2],[2],[3]]
    for row in grid:
        assert all([0,100,400,900][i]<row['available_us'] for i in row['source_indices'])


def test_oracle_omissions_and_gaps_survive_independent_baseline():
    from video_workbench.temporal.fixtures import oracle_sequences
    from video_workbench.temporal.linear import fit,predict
    # OTHER has no labels in this fixture: train the three observed event classes.
    train=list(oracle_sequences(1).values());model=fit(train,3)
    for name,s in oracle_sequences(2).items():
        score,pred=predict(model,s)
        assert np.array_equal(pred[s.valid],s.targets[s.valid])
        assert (pred[~s.valid]==-1).all() and np.isnan(score[~s.valid]).all()
        if name=='omission':assert 2 not in pred
        if name=='repetition':assert sum((pred==0)&np.r_[True,pred[:-1]!=0])==3


def test_linear_fit_ignores_unlabeled_targets_and_features():
    from copy import deepcopy
    from video_workbench.temporal.fixtures import oracle_sequences
    from video_workbench.temporal.linear import fit
    seq=oracle_sequences(1)['normal']
    seq.label_mask[1]=False
    changed=deepcopy(seq)
    changed.features[1]=12345
    changed.targets[1]=-1
    left=fit([seq],3);right=fit([changed],3)
    assert left==right
