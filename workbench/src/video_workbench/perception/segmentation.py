"""Bounded, separately identified YOLO instance-mask probe."""
from pathlib import Path
from dataclasses import asdict
import json
import numpy as np
from PIL import Image,ImageDraw
from .detector import Detector
from .contracts import FrameRef
from .store import write_json
from video_workbench.registry import file_hash


def probe_masks(samples,checkpoint,destination,device='mps'):
    dest=Path(destination)
    if dest.exists():raise ValueError('new mask-probe directory required')
    dest.mkdir(parents=True)
    detector=Detector(checkpoint,device);records=[]
    for s in samples:
        if file_hash(s['image'])!=s['image_sha256']:raise ValueError('mask source changed')
        image=Image.open(s['image']).convert('RGB')
        frame=FrameRef(s['episode_id'],s['video_sha256'],s['frame_index'],0,'1/10',s['pts_us'],image.width,image.height)
        detections,seconds,result=detector.predict(image,frame)
        masks=[];paint=image.convert('RGBA');layer=Image.new('RGBA',image.size);draw=ImageDraw.Draw(layer)
        if result.masks is not None:
            for i,polygon in enumerate(result.masks.xy):
                points=np.asarray(polygon,dtype=float).tolist()
                if not points:continue
                cls=int(result.boxes.cls[i]);score=float(result.boxes.conf[i]);name=detector.names[cls]
                masks.append({'class_id':cls,'class_name':name,'score':score,'polygon_source_xy':points})
                color=((i*67+40)%255,(i*97+160)%255,(i*43+90)%255,100)
                if score>=.25:draw.polygon([tuple(p) for p in points],fill=color,outline=(255,255,255,220))
        paint=Image.alpha_composite(paint,layer).convert('RGB');draw=ImageDraw.Draw(paint)
        draw.rectangle((0,0,640,28),fill='black');draw.text((8,7),f'YOLO11n-seg / pilot {s["ordinal"]} / {len(masks)} masks / separate model',fill='white')
        path=dest/f'masks-{s["ordinal"]:02d}.jpg';paint.save(path,quality=95)
        records.append({'sample':s,'frame':asdict(frame),'producer_id':detector.id,'seconds':seconds,'masks':masks,'overlay':str(path),'overlay_sha256':file_hash(path)})
    output={'spec':detector.spec,'producer_id':detector.id,'scope':'24 fixed initial-frame pilot samples; no temporal masks or segmentation accuracy claim','records':records}
    write_json(dest/'masks.json',output)
    return output
