from dataclasses import replace
import pytest
from video_workbench.predicates.contracts import StateLabel, validate_samples


def test_unknown_is_not_false():
    label=StateLabel('a','ep:object-1','door_open',None,'occluded','reviewer','r1','reviewed_rgb','actor hides door')
    with pytest.raises(ValueError,match='disagree'):
        replace(label,value=False)
    with pytest.raises(ValueError,match='bool'):
        replace(label,value=0)


def test_entity_and_group_rejection():
    sample=dict(sample_id='a',sample_us=0,frame_index=0,split='train',split_group='room',entity_class='fridge',property='door_open',episode_id='ep',entity_id='ep:object-1',image='a.png',image_sha256='a'*64,video='a.mp4',video_sha256='b'*64)
    validate_samples([sample],verify_files=False)
    with pytest.raises(ValueError,match='entity mismatch'):
        validate_samples([dict(sample,entity_id='other:object-1')],verify_files=False)
    with pytest.raises(ValueError,match='cross-split'):
        validate_samples([sample,dict(sample,sample_id='b',split='test')],verify_files=False)
