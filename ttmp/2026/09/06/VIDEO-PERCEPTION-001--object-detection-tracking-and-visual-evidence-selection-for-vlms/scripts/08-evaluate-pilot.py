"""Evaluate a source-first, single-reviewer target-box pilot, not full COCO AP."""
from pathlib import Path
from collections import Counter,defaultdict
import json
from PIL import Image,ImageDraw
from video_workbench.perception.contracts import iou
from video_workbench.perception.store import rows,write_json
S=Path(__file__).resolve().parents[1];source=Path('output/video-perception/detect-v1')
samples=json.loads((S/'various/pilot-samples.json').read_text());boxes=json.loads((S/'various/pilot-reviewed-boxes.json').read_text())
class_map={'fridge':'refrigerator','microwave':'microwave','sofa':'couch','bed':'bed','tv':'tv','book':'book','mug':'cup','plate':None,'tablelamp':None}
results=[]
for s in samples:
 rect=boxes[str(s['ordinal'])];mapped=class_map[s['target_class']]
 fs=rows(source/'episodes'/s['episode_id']/'frames.jsonl');frame=fs[s['frame_index']]
 detections=[d for d in rows(source/'episodes'/s['episode_id']/'detections.jsonl') if d['frame_id']==frame['frame_id'] and d['score']>=.25]
 matches=[d for d in detections if d['class_name']==mapped]
 best=max((iou(rect,d['xyxy']) for d in matches),default=0.) if rect else None
 status='unsupported_category' if mapped is None else 'unreviewable_target' if rect is None else 'localized' if best>=.5 else 'missed'
 row=dict(s,reviewed_xyxy=rect,reviewer='codex-assistant-rgb-box-review-v1',annotation_policy='Visible extent estimated from native source image; target class only, not exhaustive scene annotation.',mapped_class=mapped,status=status,best_iou=best,target_class_detections=len(matches),small_target=bool(rect and (rect[2]-rect[0])*(rect[3]-rect[1])<1024),rationale='Book hidden behind monitor' if s['ordinal']==2 else 'Several plates; target instance ambiguous' if s['ordinal'] in (11,23) else 'Visible target extent; partial image truncation/actor occlusion retained where present')
 results.append(row)
 im=Image.open(s['image']).convert('RGB');draw=ImageDraw.Draw(im)
 for d in detections:
  draw.rectangle(d['xyxy'],outline='#32b9ff',width=2);draw.text((d['xyxy'][0],d['xyxy'][1]),f"{d['class_name']} {d['score']:.2f}",fill='white',stroke_width=1,stroke_fill='black')
 if rect:draw.rectangle(rect,outline='#ffcb32',width=3)
 draw.rectangle((0,0,640,28),fill='black');draw.text((8,7),f"PILOT {s['ordinal']} / {s['target_class']} / {status} / gold yellow, YOLO blue",fill='white')
 im.save(S/'various/screenshots'/f'pilot-reviewed-{s["ordinal"]:02d}.jpg',quality=95)
summary={'protocol':'Fixed initial frames from 24 interaction episodes, one per apartment/family/view. Single assistant RGB review. Target-localization recall at score >=0.25 and IoU >=0.5; not AP or exhaustive-scene precision.',
 'class_map':class_map,'counts':dict(Counter(r['status'] for r in results)),
 'by_split':{split:dict(Counter(r['status'] for r in results if r['split']==split)) for split in ('train','development','test')},
 'small_targets':dict(Counter(r['status'] for r in results if r['small_target'])),
 'rows':results}
write_json(S/'various/detection-pilot-results.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))
