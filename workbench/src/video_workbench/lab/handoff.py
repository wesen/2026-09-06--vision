"""Resolve detector evidence into a bounded, reproducible door-state request."""
import json
import math
from .contracts import Experiment
from video_workbench.registry import file_hash


def resolve(output, binding):
    parent = output / binding.run_id
    try:
        status = json.loads((parent / 'status.json').read_text())
        request = json.loads((parent / 'request.json').read_text())
        result = json.loads((parent / 'result.json').read_text())
    except (OSError, ValueError) as exc:
        raise ValueError('handoff parent is unavailable') from exc
    if status['status'] != 'completed' or request['options']['component'] not in ('detection', 'segmentation', 'tracking'):
        raise ValueError('handoff requires completed perception evidence')
    frame = next((f for f in request['evidence']['frames'] if f['id'] == binding.frame_id), None)
    row = next((r for r in result.get('records', []) if r['frame']['id'] == binding.frame_id), None)
    detection = next((d for d in (row or {}).get('detections', []) if d['detection_id'] == binding.detection_id), None)
    if frame is None or detection is None:
        raise ValueError('unknown handoff frame or detection')
    if detection['class_name'] not in ('refrigerator', 'microwave', 'oven'):
        raise ValueError('door-state handoff supports refrigerator, microwave and oven only')
    x0, y0, x1, y1 = detection['xyxy']
    if not all(math.isfinite(v) for v in (x0, y0, x1, y1)) or x1 <= x0 or y1 <= y0:
        raise ValueError('invalid detection box')
    dx, dy = (x1-x0)*binding.padding, (y1-y0)*binding.padding
    ox, oy = frame['crop_xyxy'][:2]
    w, h = frame['source_width'], frame['source_height']
    crop = (max(0, math.floor(ox+x0-dx)), max(0, math.floor(oy+y0-dy)),
            min(w, math.ceil(ox+x1+dx)), min(h, math.ceil(oy+y1+dy)))
    options = Experiment(episode_id=request['options']['episode_id'], start_us=frame['pts_us'],
                         end_us=frame['pts_us']+1, fps=1, crop=tuple(v/d for v,d in zip(crop,(w,h,w,h))),
                         component='reasoning', model='qwen', target=detection['class_name'], handoff=binding)
    provenance = dict(parent_run_id=binding.run_id, parent_request_sha256=file_hash(parent/'request.json'),
                      parent_result_sha256=file_hash(parent/'result.json'), source=request['evidence']['source'],
                      frame=frame, detection=detection, padding=binding.padding, source_crop_xyxy=crop)
    return options, provenance


def validate(output, request):
    if request.handoff is None:
        return None
    expected, provenance = resolve(output, request.handoff)
    for key in ('episode_id','start_us','end_us','fps','crop','target','component'):
        if getattr(request,key) != getattr(expected,key):
            raise ValueError(f'handoff {key} changed; detach the handoff before editing evidence')
    return provenance
