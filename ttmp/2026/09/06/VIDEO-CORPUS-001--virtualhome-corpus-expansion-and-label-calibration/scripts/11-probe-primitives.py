import json,sys,time
from pathlib import Path
from simulation.unity_simulator.comm_unity import UnityCommunication
from virtualhome_corpus.diversity import bind,program_for
cfg=json.loads(Path('configs/virtualhome-diversity-v2.json').read_text()); c=UnityCommunication(port='18082',timeout_wait=30)
scene=int(sys.argv[1]); family=sys.argv[2]; s=next(s for s in cfg['scenes'][scene]['scenarios'] if s['family']==family)
if len(sys.argv)>3:s.update(target_id=int(sys.argv[3]),target_class=sys.argv[4])
assert c.reset(scene);ok,g=c.environment_graph();assert ok
t,r,p=bind(g,s);assert c.add_character(cfg['character'],initial_room=r['class_name'])
for line in program_for(family,t,p,'interaction'):
 print('START',line,flush=True)
 try:
  ok,result=c.render_script([line],recording=False,skip_animation=False,time_scale=5,randomize_execution=False)
  print('RESULT',ok,result,flush=True)
  if not ok:break
 except Exception as e:print('ERROR',repr(e),flush=True);break
