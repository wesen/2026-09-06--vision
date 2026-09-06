"""Decode registered videos in bounded memory and publish detector artifacts."""
from pathlib import Path
from dataclasses import asdict
import json,time
import av
from PIL import ImageDraw
from video_workbench.registry import Registry,file_hash
from video_workbench.embedding import digest
from .contracts import FrameRef
from .detector import Detector
from .store import write_json,publish_episode


def overlay(image,detections,tracks=()):
    im=image.copy();draw=ImageDraw.Draw(im)
    for d in detections:
        if d['score']<.25:continue
        xy=d['xyxy'];draw.rectangle(xy,outline='#00ff88',width=2)
        draw.text((xy[0],max(0,xy[1]-12)),f"{d['class_name']} {d['score']:.2f}",fill='black',stroke_width=1,stroke_fill='white')
    for t in tracks:
        draw.text((t['xyxy'][0],t['xyxy'][1]+12),t['track_id'].split(':')[-1]+' '+t['status'],fill='yellow',stroke_width=1,stroke_fill='black')
    return im


def detect(manifest,checkpoint,destination,device='mps'):
    dest=Path(destination)
    if dest.exists():raise ValueError('new run destination required')
    dest.mkdir(parents=True)
    registry=Registry(dest/'registry.sqlite')
    registry.ingest(manifest)
    detector=Detector(checkpoint,device)
    lock=Path('workbench/perception-env/requirements.lock')
    spec={'detector':detector.spec,'sources_sha256':file_hash(manifest),'lock_sha256':file_hash(lock),
          'sampling':'all-native-frames','code_sha256':{p.name:file_hash(p) for p in Path(__file__).parent.glob('*.py')}}
    run={'run_id':digest(spec),'spec':spec,'status':'running','episodes':[]}
    write_json(dest/'run.json',run)
    try:
        for episode in registry.episodes():
            folder=dest/'episodes'/episode['episode_id'];folder.mkdir(parents=True)
            if file_hash(episode['video'])!=episode['video_sha256']:raise ValueError('source changed')
            rows=0;total=0.;decode_total=0.;previous=None
            with (folder/'frames.jsonl').open('w') as frame_log,(folder/'detections.jsonl').open('w') as detection_log,av.open(episode['video']) as container:
                for i,decoded in enumerate(container.decode(video=0)):
                    started=time.perf_counter();image=decoded.to_image().convert('RGB');decode_total+=time.perf_counter()-started
                    pts=round(decoded.pts*decoded.time_base*1e6)-episode['media']['origin_us']
                    if pts!=episode['media']['pts_us'][i]:raise ValueError('source PTS changed')
                    frame=FrameRef(episode['episode_id'],episode['video_sha256'],i,decoded.pts,str(decoded.time_base),pts,image.width,image.height)
                    detections,seconds,_=detector.predict(image,frame)
                    # Full-frame appearance cue is independent of labels and target classes.
                    import numpy as np
                    small=np.asarray(image.resize((32,24)),dtype=float)/255
                    change=0. if previous is None else float(np.abs(small-previous).mean())
                    previous=small
                    frame_log.write(json.dumps(dict(asdict(frame),frame_id=frame.id,detector_seconds=seconds,full_frame_change=change))+'\n')
                    for d in detections:detection_log.write(json.dumps(d)+'\n')
                    if i%10==0 or i==episode['media']['frames']-1:
                        overlay(image,detections).save(folder/f'overlay-{i:05d}.jpg',quality=90)
                    rows+=len(detections);total+=seconds
            meta=publish_episode(folder,{'episode':episode,'run_id':run['run_id'],'producer_id':detector.id,'frames':episode['media']['frames'],'detections':rows,'detector_seconds':total,'image_conversion_seconds':decode_total})
            run['episodes'].append({'episode_id':episode['episode_id'],'manifest_sha256':file_hash(folder/'manifest.json')})
            write_json(dest/'run.json',run)
            print(f"detected {episode['episode_id']}: {meta['frames']} frames, {rows} boxes, {total:.1f}s",flush=True)
        run['status']='complete';write_json(dest/'run.json',run)
    except Exception as exc:
        run['status']='failed';run['error']=repr(exc);write_json(dest/'run.json',run);raise
    finally:registry.close()
    return run
