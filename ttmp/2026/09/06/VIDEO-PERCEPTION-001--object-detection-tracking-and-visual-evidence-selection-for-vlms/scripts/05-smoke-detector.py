"""CPU/MPS on identical training pixels; pin artifacts and save genuine overlays."""
from pathlib import Path
from dataclasses import asdict
import json,platform,importlib.metadata,time
import numpy as np
from PIL import Image,ImageDraw
from video_workbench.perception.detector import Detector
from video_workbench.perception.contracts import FrameRef
from video_workbench.perception.store import write_json
from video_workbench.registry import file_hash
S=Path(__file__).resolve().parents[1]
review=json.loads(Path('ttmp/2026/09/06/VIDEO-STATE-001--project-2-observable-state-recognition/various/samples-v2.json').read_text())
s=next(s for s in review if s['split']=='train' and s['entity_class']=='fridge' and s['ordinal']==3)
image=Image.open(s['image']).convert('RGB')
frame=FrameRef(s['episode_id'],s['video_sha256'],s['frame_index'],s['frame_index'],'1/10',s['sample_us'],640,480)
report={'frame':asdict(frame),'image_sha256':file_hash(s['image']),'platform':platform.platform(),'devices':{},'packages':{n:importlib.metadata.version(n) for n in ('ultralytics','torch','torchvision','numpy','av','pillow','lap')}}
for device in ('cpu','mps'):
 try:
  detector=Detector('output/models/yolo11/yolo11n.pt',device)
  detections,first,result=detector.predict(image,frame)
  timings=[]
  for _ in range(3):
   detections,seconds,result=detector.predict(image,frame);timings.append(seconds)
  report['devices'][device]={'status':'ok','first_seconds':first,'warm_seconds':timings,'spec':detector.spec,'detections':detections}
  overlay=image.copy();d=ImageDraw.Draw(overlay)
  for row in detections:
   d.rectangle(row['xyxy'],outline='lime',width=2);d.text((row['xyxy'][0],row['xyxy'][1]),f"{row['class_name']} {row['score']:.2f}",fill='red',stroke_width=1,stroke_fill='white')
  overlay.save(S/'various/screenshots'/f'd1-{device}-detector.png')
 except Exception as exc:
  report['devices'][device]={'status':'failed','error':repr(exc)}
write_json(S/'various/detector-smoke.json',report)
print(json.dumps({k:{x:y for x,y in v.items() if x not in {'spec','detections'}} for k,v in report['devices'].items()},indent=2))
import inspect
from ultralytics.trackers.byte_tracker import BYTETracker
from ultralytics.engine.results import Boxes
print('BYTETracker',inspect.signature(BYTETracker),inspect.signature(BYTETracker.update))
print(inspect.getsource(BYTETracker.update)[:4500])
