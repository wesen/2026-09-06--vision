"""Probe household procedures on the owned simulator; preserve raw exports."""
from pathlib import Path
import json, uuid, argparse
from simulation.unity_simulator import UnityCommunication
p=argparse.ArgumentParser(); p.add_argument('--family',choices=['fridge','microwave','faucet','tv'],required=True); p.add_argument('--port',default='18081'); a=p.parse_args()
r=Path('output/virtualhome-corpus/pilots')/(a.family+'-'+uuid.uuid4().hex[:8]); r.mkdir(parents=True)
c=UnityCommunication(port=a.port,timeout_wait=180)
assert c.reset(0)
ok,g=c.environment_graph(); assert ok
room='livingroom' if a.family=='tv' else 'kitchen'
room_id=next(n['id'] for n in g['nodes'] if n['class_name']==room and n['category']=='Rooms')
ids={e['from_id'] for e in g['edges'] if e['relation_type']=='INSIDE' and e['to_id']==room_id}
target=min((n for n in g['nodes'] if n['class_name']==a.family and n['id'] in ids),key=lambda n:n['id'])
dest=next(n for n in g['nodes'] if n['class_name']==('kitchen' if room=='livingroom' else 'livingroom') and n['category']=='Rooms')
assert c.add_character('Chars/Male1',initial_room=room)
ok,initial=c.environment_graph(); assert ok
(r/'graph-initial.json').write_text(json.dumps(initial,indent=2))
def act(verb,node): return f"<char0> [{verb}] <{node['class_name']}> ({node['id']})"
program=[act('Walk',target),act('Open' if a.family in ['fridge','microwave'] else 'SwitchOn',target),act('Close' if a.family in ['fridge','microwave'] else 'SwitchOff',target),act('Walk',dest)]
(r/'actions.txt').write_text('\n'.join(program)+'\n')
ok,result=c.render_script(program,recording=True,randomize_execution=False,random_seed=7,output_folder=str(r.resolve()),file_name_prefix='episode',frame_rate=10,image_width=640,image_height=480,camera_mode=['AUTO'],save_pose_data=True,out_graph=True,per_frame=1)
(r/'result.json').write_text(json.dumps({'ok':ok,'result':result,'program':program,'target':target['id']},indent=2))
print(r,ok,result,flush=True)
print([str(x.relative_to(r)) for x in r.rglob('*') if x.is_file() and not x.name.startswith('Action_')],flush=True)
if not ok: raise SystemExit(1)
