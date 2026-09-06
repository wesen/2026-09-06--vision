import numpy as np
import pytest
from video_workbench.predicates.classify import margins, fit_head, head_scores, fit_calibration, probabilities, select_policy, evaluate
from video_workbench.predicates.contracts import StateLabel, StateObservation
from video_workbench.predicates.features import validate_cache, binding, CONDITIONS, CONTEXT_ONLY


def test_hand_computed_margin_and_head_binding():
    assert margins(np.array([[.6,.8]]),np.array([[1.,0.],[0.,1.]]))[0]==pytest.approx(.2)
    x=np.array([[1.,0.],[-1.,0.]])
    head=fit_head(x,[True,False],'space',{'fridge'})
    assert (head_scores(head,x,'space',{'fridge'})>0).tolist()==[True,False]
    with pytest.raises(ValueError,match='feature-space'):
        head_scores(head,x,'other',{'fridge'})
    with pytest.raises(ValueError,match='entity-class'):
        head_scores(head,x,'space',{'oven'})


def test_cached_entity_binding_is_not_interchangeable():
    sample=dict(sample_id='a',entity_id='ep:1',entity_class='fridge',property='door_open',sample_us=0,video_sha256='a',image_sha256='b')
    metadata=dict(feature_space_id='space',bindings=[binding(sample)],templates=CONDITIONS,context_only=CONTEXT_ONLY)
    validate_cache(metadata,[sample],'space')
    with pytest.raises(ValueError,match='entity/evidence'):
        validate_cache(metadata,[dict(sample,entity_id='ep:2')])
    with pytest.raises(ValueError,match='feature-space'):
        validate_cache(metadata,[sample],'wrong')


def test_calibration_and_unknown_false_certainty():
    cal=fit_calibration([-2,-1,1,2],[False,False,True,True])
    p=probabilities(cal,[-2,2])
    assert p[0]<.5<p[1]
    labels=[StateLabel('a','ep:1','door_open',False,'visible','r','v1','reviewed_rgb','closed'),StateLabel('b','ep:1','door_open',None,'occluded','r','v1','reviewed_rgb','actor')]
    counts=evaluate([.1,.9],labels,dict(threshold=.5,radius=0))
    assert counts['unknown_false_certainty']==1
    assert counts['oracle_visibility_answered']==1
    assert counts['known_answered_errors']==0
    empty=evaluate([.1,.9],labels,dict(threshold=.5,radius=1.01))
    assert empty['known_selective_risk'] is None
    assert empty['model_answered']==0


def test_constant_context_cannot_discriminate():
    cal=fit_calibration([1,1,1,1],[False,False,False,True])
    p=probabilities(cal,[1,1,1,1])
    assert len(set(p.tolist()))==1
    policy=select_policy(p,[False,False,False,True])
    assert policy['development_answered']==0  # 25% error exceeds 10% target


def test_observation_rejects_time_reversal_and_unexplained_unknown():
    kwargs=dict(sample_id='a',episode_id='ep',entity_id='ep:1',property='door_open',sample_us=10,available_us=11,availability_source='replay',value=None,raw_score=0.,calibrated_probability=.5,unknown_reason='band',evidence_ids=('a',),feature_space_id='s',producer_id='p')
    StateObservation(**kwargs)
    with pytest.raises(ValueError,match='time'):
        StateObservation(**dict(kwargs,available_us=9))
    with pytest.raises(ValueError,match='reason'):
        StateObservation(**dict(kwargs,unknown_reason=None))


def test_missing_evidence_can_export_unknown_without_fabricated_scores():
    kwargs=dict(sample_id='a',episode_id='ep',entity_id='ep:1',property='door_open',sample_us=0,available_us=0,availability_source='offline',value=None,raw_score=None,calibrated_probability=None,unknown_reason='missing_crop',evidence_ids=('a',),feature_space_id='s',producer_id='p')
    StateObservation(**kwargs)
    with pytest.raises(ValueError,match='paired null'):
        StateObservation(**dict(kwargs,value=False,unknown_reason=None))
