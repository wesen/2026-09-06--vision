import pytest
from video_workbench.actions.encoders import intervention
from video_workbench.actions.data import window,validate_samples


def test_interventions_reorder_pixels_not_source_clock():
    f,t,m=intervention(['a','b','c'],[10,20,30],'reverse')
    assert f==['c','b','a'] and t==[10,20,30] and m==[2,1,0]
    assert intervention(['a','b'],[10,20],'repeat_first')[0]==['a','a']
    with pytest.raises(ValueError):intervention(['a','b'],[20,10],'original')


def test_fixed_windows_and_lineage_leakage():
    from video_workbench.actions.data import action_center
    assert window(action_center('sit',2_400_000,8_500_000),11_000_000)==(6_750_000,8_750_000)
    assert action_center('open',2_000_000,4_000_000)==3_000_000
    assert window(200_000,5_000_000)==(0,2_000_000)
    assert window(4_900_000,5_000_000)==(3_000_000,5_000_000)
    assert window(1,1_000_000) is None
    s=dict(sample_id='a',lineage_id='l',video_sha256='h',split='train',start_us=0,end_us=100,available_us=100,selected_pts_us=[0,50],frame_indices=[0,1])
    validate_samples([s])
    with pytest.raises(ValueError,match='lineage'):validate_samples([s,dict(s,sample_id='b',split='test')])
    with pytest.raises(ValueError,match='future'):validate_samples([dict(s,available_us=49)])


def test_action_confusion_and_development_abstention():
    from video_workbench.actions.evaluate import classification_metrics,select_abstention
    m=classification_metrics([0,0,1,1],[0,1,1,1],2)
    assert m['confusion']==[[1,1],[0,2]] and m['accuracy']==.75
    assert m['balanced_accuracy']==.75
    p=select_abstention([.1,.3,.5],[-1,0,1],[0,0,0])
    assert p['gap_threshold']>.5 # no prefix of confidence-ranked answers is safe
    assert classification_metrics([],[],2)['accuracy'] is None
    with pytest.raises(ValueError,match='development'):select_abstention([],[],[])
    with pytest.raises(ValueError,match='development'):select_abstention([float('nan')],[0],[0])
