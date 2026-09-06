import pytest
pytest.importorskip('ultralytics')
from video_workbench.perception.tracking import TrackerSession
from video_workbench.perception.contracts import FrameRef


def frame(i):return FrameRef('ep','sha',i,i,'1/10',i*100000,640,480)
def detection(i,x=20):return dict(class_id=0,xyxy=[x,20,x+40,120],score=.9,detection_id=f'd{i}')


def test_empty_frame_predicted_and_gap_shot_resets():
    t=TrackerSession('run','ep')
    first=t.update(frame(0),[detection(0)])
    assert first[0]['status']=='observed'
    missed=t.update(frame(1),[])
    assert missed[0]['status']=='predicted' and missed[0]['detection_id'] is None
    assert t.update(frame(2),[detection(2)])[0]['track_id']==first[0]['track_id']
    after=t.update(frame(10),[detection(10)])[0]
    assert after['track_id']!=first[0]['track_id'] and t.resets[-1]['reason']=='cadence_gap'
    shot=t.update(frame(11),[detection(11)],shot_cut=True)[0]
    assert shot['track_id']!=after['track_id']


def test_two_similar_objects_and_prefix_replay():
    def sequence():
        tracker=TrackerSession('run','ep');out=[]
        for i in range(6):
            out.append(tracker.update(frame(i),[detection(i,20+i),dict(detection(i,160-i),detection_id=f'b{i}')]))
        return out
    a=sequence();b=sequence()
    assert a==b
    assert len({r['track_id'] for r in a[0]})==2
    prefix=TrackerSession('run','ep')
    for i in range(3):prefix.update(frame(i),[detection(i,20+i),dict(detection(i,160-i),detection_id=f'b{i}')])
    assert prefix.update(frame(3),[detection(3,23),dict(detection(3,157),detection_id='b3')])==a[3]
