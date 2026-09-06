"""Source-bound target reviews with independent visibility and class support."""
from pathlib import Path
import math
from video_workbench.perception.contracts import box
from video_workbench.registry import file_hash

CLASS_MAP={'fridge':'refrigerator','microwave':'microwave','sofa':'couch','bed':'bed','tv':'tv','book':'book','mug':'cup','plate':None,'tablelamp':None}
VISIBILITY={'visible_unique','partially_visible_unique','ambiguous_instances','unobservable','absent'}


def validate_review(sample,review,check_source=True):
    if review['sample_id']!=sample['sample_id'] or review['image_sha256']!=sample['image_sha256']:raise ValueError('review/source identity mismatch')
    if check_source and file_hash(sample['image'])!=sample['image_sha256']:raise ValueError('source image changed')
    if review['visibility'] not in VISIBILITY:raise ValueError('unfinished visibility review')
    if review['detector_class_supported']!=(CLASS_MAP[sample['requested_class']] is not None):raise ValueError('class support differs from frozen vocabulary')
    if review['convention']!='visible-extent-half-open-v1' or not review['reviewer'] or not review['rationale']:raise ValueError('review provenance required')
    for name in ('occluded','truncated','temporal_context_used'):
        if type(review[name]) is not bool:raise ValueError('explicit review flags required')
    rect=review['visible_xyxy']
    if review['visibility'] in ('visible_unique','partially_visible_unique'):
        if rect is None:raise ValueError('visible target requires rectangle')
        box(rect,sample['width'],sample['height'])
    elif rect is not None:raise ValueError('nonunique or unobservable target must have null rectangle')
    return review
