from pathlib import Path
import json,math
from PIL import Image
from simulation.unity_simulator import UnityCommunication
c=UnityCommunication(port='18081',timeout_wait=180); assert c.reset(0)
r=Path('output/virtualhome-corpus/cameras'); r.mkdir(exist_ok=True)
for family,pos,look in [('fridge',[-0.3,1.65,-4.8],[-3.0,1.0,-2.0]),('tv',[3.6,2.2,-5.8],[6.1,1.0,-8.6])]:
 dx,dy,dz=[look[i]-pos[i] for i in range(3)]
 rot=[math.degrees(math.atan2(-dy,math.hypot(dx,dz))),math.degrees(math.atan2(dx,dz)),0]
 ok,count=c.camera_count(); assert ok
 ok,msg=c.add_camera(position=pos,rotation=rot); assert ok
 ok,images=c.camera_image([count],image_width=640,image_height=480); assert ok
 # camera_image returns arrays from OpenCV (BGR).
 Image.fromarray(images[0][:,:,::-1]).save(r/(family+'.png'))
 (r/(family+'.json')).write_text(json.dumps({'position':pos,'rotation':rot,'camera_index':count,'message':msg},indent=2))
 print(family,count,msg,flush=True)
