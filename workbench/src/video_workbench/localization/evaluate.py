"""Requested-class recall differs from production unique-binding coverage."""
import math
from video_workbench.perception.contracts import box,iou
from .annotations import CLASS_MAP,validate_review


def match(sample,review,detections,confidence=.25):
    validate_review(sample,review,check_source=False)
    if confidence not in (.10,.25,.50):raise ValueError('use a frozen confidence policy')
    mapped=CLASS_MAP[sample['requested_class']]
    for d in detections:
        box(d['xyxy'],sample['width'],sample['height'])
        if not math.isfinite(d['score']) or not 0<=d['score']<=1:raise ValueError('invalid confidence')
    kept=[d for d in detections if d['score']>=confidence]
    candidates=[d for d in kept if d['class_name']==mapped] if mapped is not None else []
    rect=review['visible_xyxy'];eligible=mapped is not None and rect is not None
    overlaps=[iou(d['xyxy'],rect) for d in candidates] if rect is not None else []
    wrong=[d for d in kept if mapped is not None and d['class_name']!=mapped and rect is not None and iou(d['xyxy'],rect)>=.5]
    binding='unsupported_category' if mapped is None else 'missing_class' if not candidates else 'unique_class' if len(candidates)==1 else 'ambiguous_instances'
    area=(rect[2]-rect[0])*(rect[3]-rect[1]) if rect is not None else None
    return {'sample_id':sample['sample_id'],'confidence':confidence,'split':sample['split'],'requested_class':sample['requested_class'],'apartment':sample['apartment'],'view':sample['view'],'visibility':review['visibility'],'occluded':review['occluded'],'supported':mapped is not None,'eligible':eligible,'area_px':area,'size':'unreviewable' if area is None else 'small' if area<1024 else 'larger','candidate_count':len(candidates),'binding':binding,'selected_detection_id':candidates[0]['detection_id'] if len(candidates)==1 else None,'best_iou':max(overlaps,default=0.) if rect is not None else None,'localized':bool(max(overlaps,default=0)>=.5) if eligible else None,'unique_correct':bool(len(candidates)==1 and overlaps[0]>=.5) if eligible else None,'wrong_class_overlap_ids':[d['detection_id'] for d in wrong]}


def summarize(rows):
    eligible=[r for r in rows if r['eligible']];n=len(eligible)
    return {'total':len(rows),'eligible':n,'localized':sum(r['localized'] for r in eligible),'recall':sum(r['localized'] for r in eligible)/n if n else None,'unique_correct':sum(r['unique_correct'] for r in eligible),'unique_correct_rate':sum(r['unique_correct'] for r in eligible)/n if n else None,'unique_class_bindings':sum(r['binding']=='unique_class' for r in rows),'binding_coverage':sum(r['binding']=='unique_class' for r in rows)/len(rows) if rows else None,'unsupported':sum(not r['supported'] for r in rows),'unreviewable_supported':sum(r['supported'] and not r['eligible'] for r in rows),'wrong_class_overlap':sum(bool(r['wrong_class_overlap_ids']) for r in eligible),'ambiguous_bindings':sum(r['binding']=='ambiguous_instances' for r in rows),'missing_class':sum(r['binding']=='missing_class' for r in rows)}
