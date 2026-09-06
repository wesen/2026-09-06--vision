import pytest
from video_workbench.perception.store import publish_episode,verify_episode


def test_successful_episode_is_immutable_and_corruption_is_rejected(tmp_path):
    artifact=tmp_path/'detections.jsonl';artifact.write_text('{}\n')
    publish_episode(tmp_path,{'run_id':'run'})
    assert verify_episode(tmp_path)['run_id']=='run'
    with pytest.raises(ValueError,match='already published'):
        publish_episode(tmp_path,{'run_id':'other'})
    artifact.write_text('changed\n')
    with pytest.raises(ValueError,match='artifact changed'):
        verify_episode(tmp_path)
