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
