"""Read three actual simulator scenes and preserve v1 hashes without modifying it."""
from pathlib import Path
import json,time
from collections import Counter
from simulation.unity_simulator.comm_unity import UnityCommunication
import hashlib

OUT=Path('output/virtualhome-corpus/diversity-probes');OUT.mkdir(parents=True,exist_ok=True)
TICKET=Path(__file__).resolve().parent.parent
old=Path('output/virtualhome-corpus/home-v1');rows=[json.loads(l) for l in (old/'inputs.jsonl').read_text().splitlines()]
for r in rows:
 actual=hashlib.sha256((old/r['video']).read_bytes()).hexdigest()
 assert actual==r['video_sha256'],r['episode_id']
(TICKET/'various/v1-preservation.json').write_text(json.dumps({'videos':len(rows),'inputs_sha256':hashlib.sha256((old/'inputs.jsonl').read_bytes()).hexdigest(),'source_videos':{r['episode_id']:r['video_sha256'] for r in rows},'unchanged':True},indent=2)+'\n')
comm=UnityCommunication(port='18082',timeout_wait=120)
assert comm.post_command({'id':str(time.time()),'action':'idle'})['success']
summary=[]
for scene in (0,1,2):
 assert comm.reset(scene),scene
 ok,g=comm.environment_graph();assert ok
 (OUT/f'scene-{scene}.json').write_text(json.dumps(g,indent=2)+'\n')
 rooms={n['id']:n for n in g['nodes'] if n.get('category')=='Rooms'}
 inside={e['from_id']:e['to_id'] for e in g['edges'] if e['relation_type']=='INSIDE' and e['to_id'] in rooms}
 candidates=[]
 for n in g['nodes']:
  if any(p in n.get('properties',[]) for p in ('CAN_OPEN','GRABBABLE','SITTABLE','HAS_SWITCH')) and n['id'] in inside:
   candidates.append({'id':n['id'],'class':n['class_name'],'room':rooms[inside[n['id']]]['class_name'],'properties':n.get('properties',[]),'states':n.get('states',[]),'position':n.get('obj_transform',{}).get('position'),'bbox':n.get('bounding_box')})
 s={'scene':scene,'nodes':len(g['nodes']),'rooms':[{k:n.get(k) for k in ('id','class_name','obj_transform','bounding_box')} for n in rooms.values()],'candidates':candidates}
 summary.append(s);print(json.dumps(s),flush=True)
(TICKET/'various/scene-inventory.json').write_text(json.dumps(summary,indent=2)+'\n')
