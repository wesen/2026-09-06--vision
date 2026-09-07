"""Save actual timestamped inputs before any model is run."""
from pathlib import Path
import math
from video_workbench.media import selected_indices, decode_selected
from video_workbench.registry import file_hash

MAX_SAMPLES=64

def prepare(catalog, selection, destination):
    source=catalog.get(selection.episode_id); media=source['media']
    if selection.end_us>media['duration_us']: raise ValueError('range exceeds recording duration')
    if (selection.end_us-selection.start_us)*selection.fps/1e6>MAX_SAMPLES:
        raise ValueError('selection exceeds 64 sample budget; reduce duration or FPS')
    indices=selected_indices(media['pts_us'],selection.start_us,selection.end_us,selection.fps)
    if not indices or len(indices)>MAX_SAMPLES: raise ValueError('selection must contain 1..64 frames')
    if getattr(selection,'component',None)=='reasoning' and len(indices)!=1:
        raise ValueError('reasoning accepts one sampled frame; use States for a sequence of independent image calls')
    images=decode_selected(source['video'],indices)
    destination=Path(destination); destination.mkdir(parents=True,exist_ok=True)
    records=[]
    for i in indices:
        image=images[i]; w,h=image.size; crop=(0,0,w,h)
        if selection.crop:
            a,b,c,d=selection.crop; crop=(math.floor(a*w),math.floor(b*h),math.ceil(c*w),math.ceil(d*h))
            image=image.crop(crop)
        name=f'input-{i:06d}.png'; path=destination/name; image.save(path)
        records.append(dict(id=f'frame-{i}',frame_index=i,pts_us=media['pts_us'][i],raw_pts=media['raw_pts'][i],
                            time_base=media['time_base'],origin_us=media['origin_us'],file=name,sha256=file_hash(path),
                            width=image.width,height=image.height,source_width=w,source_height=h,crop_xyxy=crop))
    return dict(source={k:v for k,v in source.items() if k not in ('media','video')},frames=records,
                duration_us=media['duration_us'],selection=selection.model_dump())
