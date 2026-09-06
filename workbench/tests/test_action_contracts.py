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


def test_retrieval_uses_union_duration_and_exposes_unsupported_queries():
    import numpy as np
    from video_workbench.actions.evaluate import interval_union_duration,retrieval_metrics
    samples=[dict(sample_id=str(i),episode_id='e',video_sha256='v',start_us=a,end_us=b) for i,(a,b) in enumerate([(0,20),(10,30),(40,60)])]
    assert interval_union_duration(samples,[0,1])==30
    scores=np.zeros((3,9));scores[:,0]=[.9,.8,.7]
    r=retrieval_metrics(samples,np.array([0,0,-1]),scores,[0,1,2])
    assert r['queries'][0]['at_k']['1']['interval_coverage']==20/30
    assert r['queries'][0]['at_k']['3']['interval_coverage']==1
    assert r['queries'][1]['at_k']['1']['success'] is None


def test_temporal_handoff_preserves_source_order_and_unknown_mask(tmp_path):
    import json
    import numpy as np
    from video_workbench.actions.handoff import export
    from video_workbench.registry import file_hash
    data=tmp_path/'data';data.mkdir();run=tmp_path/'run';run.mkdir()
    base=dict(episode_id='e',split='train',lineage_id='l',video_sha256='h',frame_indices=[0],selected_pts_us=[0],start_us=0,end_us=10,available_us=10)
    samples=[dict(base,sample_id='late',selected_pts_us=[20],start_us=20,end_us=30,available_us=30),dict(base,sample_id='early')]
    (data/'samples.json').write_text(json.dumps(samples))
    labels=tmp_path/'labels.json';labels.write_text(json.dumps([dict(sample_id='late',action=None),dict(sample_id='early',action='open')]))
    np.savez(run/'features.npz',original=np.array([[3.,4.],[1.,2.]]))
    (run/'manifest.json').write_text(json.dumps(dict(sample_ids=['late','early'],spec=dict(samples_sha256=file_hash(data/'samples.json'),space_id='s'),features_sha256=file_hash(run/'features.npz'),run_id='r')))
    out=tmp_path/'out';export(data,labels,{'m':run},out)
    with np.load(out/'m/e.npz') as f:
        assert f['features'].tolist()==[[1.,2.],[3.,4.]]
        assert f['event_us'].tolist()==[10,30]
        assert f['valid'].tolist()==[True,True]
        assert f['label_mask'].tolist()==[True,False]
        assert f['targets'].tolist()==[0,-1]
