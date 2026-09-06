import pytest
from video_workbench.perception.contracts import box,expand,source_to_crop,crop_to_source,iou,FrameRef,crop_record,validate_packet,validate_response


def test_source_geometry_and_non_square_round_trip():
    assert expand((100,120,180,200),640,480)==(80,100,200,220)
    rect=expand((0,0,40,20),640,480)
    assert rect==(0,0,50,25)
    assert crop_to_source(source_to_crop((30,15),rect,(320,240)),rect,(320,240))==pytest.approx((30,15))
    assert iou((0,0,20,20),(10,0,30,20))==pytest.approx(1/3)
    for r in ((0,0,0,1),(0,0,float('nan'),2),(-1,0,2,2),(0,0,700,480)):
        with pytest.raises(ValueError):box(r,640,480)


def test_crop_cache_identity_changes_with_geometry_and_producer():
    f=FrameRef('ep','sha',0,0,'1/10',0,640,480)
    a=crop_record(f,(0,0,100,100),'p','target',('d',))
    b=crop_record(f,(0,0,101,100),'p','target',('d',))
    c=crop_record(f,(0,0,100,100),'q','target',('d',))
    assert len({r['evidence_id'] for r in (a,b,c)})==3


def test_packets_reject_future_source_budget_and_invented_citations():
    e=dict(episode_id='ep',video_sha256='sha',pts_us=10,width=320,height=240)
    packet=dict(episode_id='ep',video_sha256='sha',interval_us=(0,20),available_at_us=10,evidence_ids=['a'],budget=dict(max_images=1,max_pixels=76800))
    validate_packet(packet,{'a':e},10)
    for wrong in (dict(e,pts_us=30),dict(e,episode_id='other'),dict(e,width=640)):
        with pytest.raises(ValueError):validate_packet(packet,{'a':wrong},10)
    with pytest.raises(ValueError):validate_packet(packet,{'a':e},9)
    with pytest.raises(ValueError):validate_response(dict(value=True,evidence_ids=['invented'],explanation='x'),packet)
    validate_response(dict(value=None,evidence_ids=['a'],explanation='occluded'),packet)
