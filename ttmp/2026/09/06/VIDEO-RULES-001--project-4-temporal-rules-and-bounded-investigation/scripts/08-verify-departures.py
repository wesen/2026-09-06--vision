"""Verify every detector candidate; reviewed labels are deliberately not loaded."""
from pathlib import Path
from dataclasses import asdict,is_dataclass
import json,sqlite3
import av
from video_workbench.registry import file_hash
from video_workbench.rules.evaluate import Event
from video_workbench.rules.stored import evaluate_stored
from video_workbench.rules.handoff import investigate
from video_workbench.verifiers.profiles import make_profile
root=Path(__file__).resolve().parents[1]
out=Path('output/rules-departure-v1')
store=Path('output/temporal-v1/replay-v1/observations.sqlite')
con=sqlite3.connect(store.resolve().as_uri()+'?mode=ro',uri=True)
runs=con.execute("SELECT DISTINCT run_id FROM observations WHERE stream_id='state/F__linear_head'").fetchall();con.close()
assert len(runs)==1,runs
run_id=runs[0][0]
models={'qwen':'output/models/qwen3-vl-instruct-8b-8bit','cosmos':'output/models/cosmos-reason2-8b-8bit-local'}
for row in json.loads((root/'various/r4-review/recordings.json').read_text()):
    dest=out/row['episode_id'];summary=json.loads((dest/'complete.json').read_text())
    assert file_hash(dest/'frames.jsonl')==summary['frames_sha256']
    assert file_hash(row['video'])==row['video_sha256']
    candidates=summary['candidates'];by_pts={e['event_us']:e for e in candidates}
    frames={}
    with av.open(row['video']) as c:
        for f in c.decode(video=0):
            pts=int(f.pts*f.time_base*1000000)
            if pts in by_pts:
                p=dest/(by_pts[pts]['frame_id']+'.png');f.to_image().save(p);frames[pts]=p
    for candidate in candidates:
        entity=row['episode_id']+':object-'+row['entity_id'];pts=candidate['event_us'];available=candidate['available_us']
        event=Event(candidate['event_id'],row['episode_id'],entity,'yolo/camera-exit','camera_exit',pts,pts,available,available).validate()
        rule=dict(schema_version=1,rule_id='door-closed-at-camera-exit',op='state_at_event',event_stream=event.stream_id,event_id=event.id,state_stream='state/F__linear_head',property='door_open',expected=False)
        baseline=evaluate_stored(store,run_id,rule,row['episode_id'],entity,[event],available)
        p=frames[pts]
        frame=dict(id=candidate['frame_id'],episode_id=row['episode_id'],entity_id=entity,pts_us=pts,available_us=pts,path=str(p.resolve()),sha256=file_hash(p))
        packet=dict(candidate=candidate,event=asdict(event),rule=rule,baseline=baseline,frame=frame,store_sha256=file_hash(store),state_run_id=run_id)
        (dest/(event.id+'-packet.json')).write_text(json.dumps(packet,indent=2)+'\n')
        for family,model in models.items():
            result=investigate(rule,baseline,event,[frame],row['entity_label'],model,dest/(event.id+'-'+family),'rules-camera-exit-v1',family,profile=make_profile(family))
            path=dest/(event.id+'-'+family+'-handoff.json')
            path.write_text(json.dumps(result,indent=2,default=lambda x:asdict(x) if is_dataclass(x) else str(x))+'\n')
            print(json.dumps(dict(episode_id=row['episode_id'],model=family,status=result['status'],decision=result.get('conditioned',{}).get('decision',{}).get('status'),elapsed=result.get('verifier',{}).get('elapsed_seconds'))),flush=True)
