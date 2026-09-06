"""Class-separated ByteTrack replay at explicit native cadence."""
from types import SimpleNamespace
from pathlib import Path
import numpy as np
from video_workbench.registry import file_hash
from video_workbench.embedding import digest
from .contracts import box

CONFIG={'tracker_type':'bytetrack','track_high_thresh':.25,'track_low_thresh':.1,'new_track_thresh':.25,'track_buffer':10,'match_thresh':.8,'fuse_score':True}


def new_tracker():
    from ultralytics.trackers.byte_tracker import BYTETracker,STrack
    # Vendor BaseTrack IDs are process-global. Give each session a private counter.
    counter=0
    class LocalTrack(STrack):
        @staticmethod
        def next_id():
            nonlocal counter
            counter+=1
            return counter
    class LocalTracker(BYTETracker):
        @staticmethod
        def reset_id():
            pass
    tracker=LocalTracker(SimpleNamespace(**CONFIG))
    tracker.track_class=LocalTrack
    return tracker


class TrackerSession:
    def __init__(self,run_id,episode_id,cadence_us=100_000):
        self.run_id,self.episode_id,self.cadence_us=run_id,episode_id,cadence_us
        self.shot=-1;self.previous=None;self.trackers={};self.resets=[]
        self.id=digest({'configuration':CONFIG,'cadence_us':cadence_us,'adapter_sha256':file_hash(Path(__file__))})
        self.reset('episode_start',0)

    def reset(self,reason,pts_us):
        self.shot+=1;self.trackers={};self.previous=None
        self.resets.append({'reason':reason,'pts_us':pts_us,'shot':self.shot})

    def update(self,frame,detections,shot_cut=False):
        from ultralytics.engine.results import Boxes
        if frame.episode_id!=self.episode_id:raise ValueError('tracker episode mismatch')
        if shot_cut:self.reset('explicit_shot_cut',frame.pts_us)
        if self.previous is not None:
            delta=frame.pts_us-self.previous
            if delta<=0:raise ValueError('non-increasing tracker time')
            if delta>self.cadence_us*1.5:self.reset('cadence_gap',frame.pts_us)
            elif abs(delta-self.cadence_us)>1:raise ValueError('unsupported variable cadence')
        self.previous=frame.pts_us
        classes=set(self.trackers)|{d['class_id'] for d in detections}
        output=[]
        for cls in sorted(classes):
            if cls not in self.trackers:self.trackers[cls]=new_tracker()
            tracker=self.trackers[cls]
            selected=[d for d in detections if d['class_id']==cls]
            data=np.array([[*d['xyxy'],d['score'],cls] for d in selected],dtype=np.float32).reshape(-1,6)
            tracked=tracker.update(Boxes(data,(frame.height,frame.width)))
            def emit(tid,xy,status,detection_id,score):
                clipped=(max(0,float(xy[0])),max(0,float(xy[1])),min(frame.width,float(xy[2])),min(frame.height,float(xy[3])))
                if clipped[2]<=clipped[0] or clipped[3]<=clipped[1]:return
                output.append({'track_id':f'{self.run_id[:12]}:{self.episode_id}:s{self.shot}:c{cls}:t{int(tid)}','frame_id':frame.id,'pts_us':frame.pts_us,'xyxy':box(clipped,frame.width,frame.height),'class_id':cls,'status':status,'detection_id':detection_id,'score':float(score),'producer_id':self.id})
            for row in tracked:
                index=int(row[-1]);d=selected[index]
                emit(row[4],row[:4],'observed',d['detection_id'],row[5])
            for lost in tracker.lost_stracks:
                if tracker.frame_id-lost.end_frame<=CONFIG['track_buffer']:
                    emit(lost.track_id,lost.xyxy,'predicted',None,lost.score)
        return output
