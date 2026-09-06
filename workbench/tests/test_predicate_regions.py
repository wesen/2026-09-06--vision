import numpy as np
from video_workbench.predicates.region_experiment import score_predictions
from video_workbench.predicates.contracts import StateLabel


def test_missing_crop_counts_in_coverage_not_as_a_correct_unknown():
    labels=[StateLabel(str(i),'ep:1','door_open',v,'visible' if v is not None else 'occluded','r','v1','reviewed_rgb','pixels') for i,v in enumerate([False,True,None])]
    m=score_predictions(np.array([.1,.9,.9]),labels,[True,False,True],dict(threshold=.5,radius=0))
    assert m['missing_evidence']==1 and m['answered']==2
    assert m['known_correct_over_all_known']==.5
    assert m['known_errors']==0 and m['unknown_false_certainty']==1
