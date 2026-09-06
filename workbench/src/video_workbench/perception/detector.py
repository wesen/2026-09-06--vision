"""Pinned vendor adapter. PIL input is RGB; outputs are original-pixel boxes."""
from dataclasses import asdict
from pathlib import Path
import time
from video_workbench.embedding import digest
from video_workbench.registry import file_hash
from .contracts import Detection,box

DEFAULTS={'imgsz':640,'conf':.1,'iou':.7,'max_det':100,'rect':False,'augment':False,'verbose':False}


class Detector:
    def __init__(self,checkpoint,device='cpu'):
        import torch
        import ultralytics
        from ultralytics import YOLO
        if device not in {'cpu','mps'}:
            raise ValueError('explicit CPU or MPS device required')
        if device=='mps' and not torch.backends.mps.is_available():
            raise RuntimeError('MPS unavailable; no implicit CPU fallback')
        self.torch,self.device=torch,device
        self.model=YOLO(str(checkpoint))
        self.names=self.model.names
        self.spec={'checkpoint_sha256':file_hash(checkpoint),'checkpoint_name':Path(checkpoint).name,
                   'ultralytics':ultralytics.__version__,'torch':torch.__version__,'device':device,
                   'parameters':DEFAULTS,'class_map':self.names,'coordinates':'original-decoded-pixels-half-open','rgb_input':'PIL-RGB',
                   'adapter_sha256':file_hash(Path(__file__))}
        self.id=digest(self.spec)

    def predict(self,image,frame):
        if image.mode!='RGB' or image.size!=(frame.width,frame.height):
            raise ValueError('RGB/source-size mismatch')
        if self.device=='mps':self.torch.mps.synchronize()
        start=time.perf_counter()
        result=self.model.predict(source=image,device=self.device,**DEFAULTS)[0]
        if self.device=='mps':self.torch.mps.synchronize()
        seconds=time.perf_counter()-start
        output=[]
        if result.boxes is not None:
            for i,(xyxy,score,cls) in enumerate(zip(result.boxes.xyxy.cpu().numpy(),result.boxes.conf.cpu().numpy(),result.boxes.cls.cpu().numpy())):
                # Vendor promises source coordinates; clip numerical excursions and retain raw coordinates.
                raw=[float(x) for x in xyxy]
                clipped=(max(0,raw[0]),max(0,raw[1]),min(frame.width,raw[2]),min(frame.height,raw[3]))
                coords=box(clipped,frame.width,frame.height)
                record=Detection(digest([frame.id,self.id,i,coords])[:24],frame.id,self.id,int(cls),self.names[int(cls)],float(score),coords)
                record.validate(frame)
                output.append(dict(asdict(record),raw_xyxy=raw,coordinate_policy='clip-source-boundary'))
        return output,seconds,result
