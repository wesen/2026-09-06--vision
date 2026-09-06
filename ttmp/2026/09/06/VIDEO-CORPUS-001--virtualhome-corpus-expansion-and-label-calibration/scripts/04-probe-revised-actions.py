"""Execute each planned interaction and save two actual fixed-camera previews."""
from pathlib import Path
import json
import cv2
from simulation.unity_simulator.comm_unity import UnityCommunication
from virtualhome_corpus.diversity import bind,camera_for,program_for

OUT=Path('output/virtualhome-corpus/diversity-probes-r2');OUT.mkdir(exist_ok=True);TICKET=Path(__file__).resolve().parent.parent
cfg=json.loads(Path('configs/virtualhome-diversity-v2.json').read_text())
comm=UnityCommunication(port='18082',timeout_wait=60)
results=[]
for scene in cfg['scenes']:
 for scenario in scene['scenarios']:
  item={'scene':scene['scene_index'],**scenario};directory=OUT/f"scene-{scene['scene_index']}-{scenario['family']}";directory.mkdir(exist_ok=True)
  try:
   assert comm.reset(scene['scene_index'])
   ok,graph=comm.environment_graph();assert ok
   target,room,support=bind(graph,scenario)
   assert comm.add_character(cfg['character'],initial_room=room['class_name'])
   ok,initial=comm.environment_graph();assert ok
   actor=next(n for n in initial['nodes'] if n['class_name']=='character')
   item['actor_position']=actor['obj_transform']['position'];item['room']=room['class_name'];item['room_id']=room['id'];item['cameras']={}
   for view in ('left','right'):
    camera=camera_for(target,room,view);ok,index=comm.camera_count();assert ok
    ok,result=comm.add_camera(position=camera['position'],rotation=camera['rotation']);assert ok
    ok,images=comm.camera_image([index],image_width=640,image_height=480);assert ok
    cv2.imwrite(str(directory/(view+'-before.png')),images[0]);item['cameras'][view]=dict(camera,id=index)
   script=program_for(scenario['family'],target,support,'interaction');item['program']=script
   ok,result=comm.render_script(script,recording=True,randomize_execution=False,random_seed=1000+scene['scene_index']*100,
     output_folder=str(directory.resolve()),file_name_prefix='probe',frame_rate=10,image_width=640,image_height=480,
     camera_mode=[str(item['cameras']['left']['id'])],out_graph=True,per_frame=1)
   item['success']=ok;item['result']=result
   for view,camera in item['cameras'].items():
    ok,images=comm.camera_image([camera['id']],image_width=640,image_height=480)
    if ok:cv2.imwrite(str(directory/(view+'-after.png')),images[0])
   ok,after=comm.environment_graph()
   if ok:(directory/'graph-after.json').write_text(json.dumps(after,indent=2)+'\n')
  except Exception as e:
   item.update(success=False,error=repr(e));results.append(item)
   (TICKET/'various/action-camera-probes-r2.json').write_text(json.dumps(results,indent=2)+'\n')
   raise # A timeout leaves Unity running: stop the sweep, never queue more requests.
  results.append(item);print(json.dumps(item),flush=True)
  (TICKET/'various/action-camera-probes-r2.json').write_text(json.dumps(results,indent=2)+'\n')
