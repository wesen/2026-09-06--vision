import numpy as np
import pytest
from video_workbench.embedding import FeatureSpace, normalize


def test_normalize_and_reject_invalid_vectors():
    np.testing.assert_allclose(normalize([[3,4]]), [[.6,.8]])
    for v in ([[0,0]], [[float('nan'),1]], [1,2]):
        with pytest.raises(ValueError): normalize(v)


def test_space_identity_changes_for_processing_or_artifacts():
    base=FeatureSpace('a')
    assert base.id != FeatureSpace('b').id
    assert base.id != FeatureSpace('a',mode='native_video').id
    assert base.id != FeatureSpace('a',image_size=(640,480)).id
    assert base.id != FeatureSpace('a',instruction='Different.').id
