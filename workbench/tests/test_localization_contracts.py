import pytest
from video_workbench.localization.annotations import validate_review
from video_workbench.localization.evaluate import match,summarize


def fixture(cls='microwave'):
    s=dict(sample_id='s',image_sha256='h',width=100,height=100,requested_class=cls,split='train',apartment='a',view='left')
    r=dict(sample_id='s',image_sha256='h',visibility='visible_unique',visible_xyxy=[0,0,20,20],detector_class_supported=cls!='plate',convention='visible-extent-half-open-v1',reviewer='reviewer',rationale='visible front',occluded=False,truncated=False,temporal_context_used=False)
    return s,r


def test_geometry_and_source_review_contract():
    s,r=fixture();validate_review(s,r,False)
    with pytest.raises(ValueError,match='identity'):validate_review(s,dict(r,image_sha256='changed'),False)
    with pytest.raises(ValueError,match='source-coordinate'):validate_review(s,dict(r,visible_xyxy=[0,0,101,20]),False)
    with pytest.raises(ValueError,match='null'):validate_review(s,dict(r,visibility='unobservable'),False)
    validate_review(s,dict(r,visibility='unobservable',visible_xyxy=None),False)


def test_best_match_does_not_claim_unique_binding():
    s,r=fixture();d=[dict(detection_id='a',class_name='microwave',score=.8,xyxy=[0,0,20,20]),dict(detection_id='b',class_name='microwave',score=.3,xyxy=[50,50,80,80])]
    x=match(s,r,d);assert x['localized'] and not x['unique_correct'] and x['binding']=='ambiguous_instances'
    x=match(s,r,d,.5);assert x['unique_correct']
    half=match(s,r,[dict(d[0],xyxy=[0,0,10,20])]);assert half['best_iou']==.5 and half['localized']


def test_wrong_class_unsupported_and_empty_denominators():
    s,r=fixture();d=[dict(detection_id='wrong',class_name='oven',score=.9,xyxy=[0,0,20,20])]
    x=match(s,r,d);assert x['binding']=='missing_class' and x['wrong_class_overlap_ids']==['wrong'] and not x['localized']
    s,r=fixture('plate');x=match(s,r,d);assert x['binding']=='unsupported_category' and x['localized'] is None
    assert summarize([x])['recall'] is None
    assert summarize([])['binding_coverage'] is None


def test_overlay_requires_exact_population_and_unchanged_source(tmp_path):
    import json
    from PIL import Image
    from video_workbench.registry import file_hash
    from video_workbench.localization.review import render_overlays
    image = tmp_path / 'source.png'
    Image.new('RGB', (100, 100)).save(image)
    s, r = fixture()
    s.update(image=str(image), image_sha256=file_hash(image), episode_id='episode', frame_index=0)
    r['image_sha256'] = s['image_sha256']
    (tmp_path / 'samples.json').write_text(json.dumps([s]))
    reviews = tmp_path / 'reviews.json'
    reviews.write_text(json.dumps([r]))
    result = render_overlays(tmp_path, reviews, tmp_path / 'valid')
    assert result['targets'] == 1 and len(result['sheets']) == 1
    reviews.write_text(json.dumps([r, r]))
    with pytest.raises(ValueError, match='duplicate'):
        render_overlays(tmp_path, reviews, tmp_path / 'duplicate')
    reviews.write_text('[]')
    with pytest.raises(ValueError, match='exactly'):
        render_overlays(tmp_path, reviews, tmp_path / 'missing')
    reviews.write_text(json.dumps([r]))
    Image.new('RGB', (100, 100), 'red').save(image)
    with pytest.raises(ValueError, match='source image changed'):
        render_overlays(tmp_path, reviews, tmp_path / 'changed')


def test_detector_join_checks_artifacts_and_distinguishes_missing_frame(tmp_path):
    import json
    from dataclasses import asdict
    from video_workbench.embedding import digest
    from video_workbench.registry import file_hash
    from video_workbench.perception.contracts import FrameRef
    from video_workbench.perception.store import publish_episode
    from video_workbench.localization.detector_audit import load_detections
    video = tmp_path / 'video.mp4'
    video.write_bytes(b'synthetic source identity fixture')
    frame = FrameRef('episode', file_hash(video), 0, 0, '1/10', 0, 100, 100)
    detector = {'parameters': {'conf': .1}, 'class_map': {2: 'cup', 10: 'microwave'}}
    spec = {'detector': detector}
    run_id = digest(spec)
    folder = tmp_path / 'episodes' / 'episode'
    folder.mkdir(parents=True)
    frame_file = folder / 'frames.jsonl'
    frame_file.write_text(json.dumps(dict(asdict(frame), frame_id=frame.id))+'\n')
    (folder / 'detections.jsonl').write_text('')
    publish_episode(folder, {'episode': {'episode_id': 'episode', 'video': str(video), 'video_sha256': file_hash(video), 'media': {'width': 100, 'height': 100, 'pts_us': [0], 'raw_pts': [0], 'time_base': '1/10'}}, 'run_id': run_id, 'producer_id': digest(detector), 'frames': 1, 'detections': 0})
    run = {'run_id': run_id, 'spec': spec, 'status': 'complete', 'episodes': [{'episode_id': 'episode', 'manifest_sha256': file_hash(folder / 'manifest.json')}]}
    (tmp_path / 'run.json').write_text(json.dumps(run))
    sample = dict(asdict(frame), sample_id='sample')
    found, _ = load_detections([sample], tmp_path)
    assert found == {'sample': []}  # A processed frame with no boxes is valid.
    with pytest.raises(ValueError, match='absent'):
        load_detections([dict(sample, frame_index=1)], tmp_path)
    with pytest.raises(ValueError, match='differs'):
        load_detections([dict(sample, pts_us=100)], tmp_path)
    frame_file.write_text(frame_file.read_text()+'\n')
    with pytest.raises(ValueError, match='artifact changed'):
        load_detections([sample], tmp_path)


def test_crop_policy_keeps_ambiguity_and_matches_oracle_raster(tmp_path, monkeypatch):
    import json
    from PIL import Image
    from video_workbench.registry import file_hash
    from video_workbench.localization import crops
    s, r = fixture()
    path = tmp_path / 'source.png'
    image = Image.new('RGB', (100, 100), 'blue')
    image.paste('red', (0, 0, 20, 20))
    image.save(path)
    s.update(image=str(path), image_sha256=file_hash(path), aliases=[{'kind': 'state', 'id': 'state'}], episode_id='episode', requested_entity='entity', video_sha256='video', frame_index=0, pts_us=0)
    r['image_sha256'] = s['image_sha256']
    (tmp_path/'samples.json').write_text(json.dumps([s]))
    reviews = tmp_path/'reviews.json'
    reviews.write_text(json.dumps([r]))
    detections = [dict(detection_id='d', class_name='microwave', score=.8, xyxy=[0, 0, 20, 20])]
    monkeypatch.setattr(crops, 'load_detections', lambda *args: ({'s': detections}, {}))
    result = crops.prepare(tmp_path, reviews, 'unused', tmp_path/'one')['samples'][0]
    assert result['D']['source_rect'] == result['O']['source_rect'] == [0, 0, 25, 25]
    assert result['D']['image_sha256'] == result['O']['image_sha256']
    assert Image.open(result['D']['image']).size == (320, 240)
    detections.append(dict(detections[0], detection_id='other', xyxy=[50, 50, 80, 80]))
    ambiguous = crops.prepare(tmp_path, reviews, 'unused', tmp_path/'two')['samples'][0]
    assert ambiguous['D'] is None and ambiguous['detector_status'] == 'ambiguous'
    assert ambiguous['O'] is not None
