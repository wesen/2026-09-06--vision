"""Changing held-out labels cannot alter learned parameters or decisions."""
from dataclasses import replace
import json
import numpy as np
from video_workbench.predicates import experiment
from video_workbench.predicates.contracts import StateLabel
from video_workbench.predicates.features import CONDITIONS


def test_test_labels_do_not_fit_any_parameters(tmp_path,monkeypatch):
    samples=[];labels=[]
    for i in range(12):
        split=('train','development','test')[i//4]
        samples.append(dict(sample_id=str(i),episode_id=str(i),entity_id=f'{i}:object-1',entity_class='fridge',property='door_open',sample_us=i*100,split=split))
        labels.append(StateLabel(str(i),f'{i}:object-1','door_open',bool(i%2),'visible','r','v1','reviewed_rgb','geometry'))
    vectors=np.array([[1.,0.] if i%2 else [0.,1.] for i in range(12)])
    arrays={'images':vectors,'fridge__context_only':np.array([.6,.8])}
    for name in CONDITIONS:arrays['fridge__'+name]=np.array([[0.,1.],[1.,0.]])
    metadata={'feature_space_id':'space','image_seconds':[.1]*12}
    monkeypatch.setattr(experiment,'load_cache',lambda *a:(metadata,arrays))
    monkeypatch.setattr(experiment,'load_dataset',lambda *a:(samples,labels))
    dummy=tmp_path/'input.json';dummy.write_text('{}')
    first=experiment.run(dummy,dummy,'unused',tmp_path/'first')
    labels[:]=[replace(l,value=not l.value) if i>=8 else l for i,l in enumerate(labels)]
    second=experiment.run(dummy,dummy,'unused',tmp_path/'second')
    assert first['head']==second['head']
    for name in first['conditions']:
        assert first['conditions'][name]['spec']==second['conditions'][name]['spec']
    a=(tmp_path/'first/observations.jsonl').read_text()
    b=(tmp_path/'second/observations.jsonl').read_text()
    assert a==b
