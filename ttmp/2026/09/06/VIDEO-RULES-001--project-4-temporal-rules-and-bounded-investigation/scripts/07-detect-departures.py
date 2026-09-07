"""Run the frozen candidate policy on complete recordings without reading labels."""
from pathlib import Path
from dataclasses import asdict
import json,time
import av
from video_workbench.registry import file_hash
from video_workbench.perception.contracts import FrameRef
from video_workbench.perception.detector import Detector
from video_workbench.rules.departure import DepartureDetector, DeparturePolicy
root=Path(__file__).resolve().parents[1]
out=Path('output/rules-departure-v1');out.mkdir(exist_ok=True)
manifest=root/'various/r4-review/recordings.json'
policy_path=root/'various/r4-review/protocol.json'
protocol=json.loads(policy_path.read_text())
policy=DeparturePolicy(**protocol['candidate_policy'])
model=Detector(Path('output/models/yolo11/yolo11n.pt'),device='mps')
(out/'run.json').write_text(json.dumps(dict(detector=model.spec,policy=asdict(policy),recordings_sha256=file_hash(manifest),protocol_sha256=file_hash(policy_path)),indent=2)+'\n')
for row in json.loads(manifest.read_text()):
    dest=out/row['episode_id'];dest.mkdir(exist_ok=True)
    if (dest/'complete.json').exists():
        raise RuntimeError('refusing to overwrite an existing completed experiment')
    assert file_hash(row['video'])==row['video_sha256']
    detector=DepartureDetector(row['episode_id'],policy);candidates=[];start=time.perf_counter();count=0
    with (dest/'frames.jsonl').open('w') as log, av.open(row['video']) as c:
        for i,f in enumerate(c.decode(video=0)):
            frame=FrameRef(row['episode_id'],row['video_sha256'],i,f.pts,str(f.time_base),int(f.pts*f.time_base*1000000),f.width,f.height)
            detections,seconds,_=model.predict(f.to_image(),frame)
            score=max((d['score'] for d in detections if d['class_id']==0),default=0.)
            event=detector.observe(frame.id,frame.pts_us,score)
            log.write(json.dumps(dict(frame=asdict(frame),frame_id=frame.id,person_score=score,detections=detections,inference_seconds=seconds,candidate=event))+'\n');log.flush()
            if event:candidates.append(event)
            count+=1
    assert count==row['frames']
    summary=dict(episode_id=row['episode_id'],frames=count,candidates=candidates,wall_seconds=time.perf_counter()-start,frames_sha256=file_hash(dest/'frames.jsonl'))
    (dest/'complete.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)
