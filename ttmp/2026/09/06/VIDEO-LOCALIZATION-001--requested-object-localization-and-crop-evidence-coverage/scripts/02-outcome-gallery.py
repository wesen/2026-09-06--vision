"""Render unique measured source/D/O examples, including detector overlays."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from video_workbench.localization.detector_audit import load_detections
root=Path(__file__).resolve().parents[1]
samples=json.load(open('output/localization-v1/dataset/samples.json'))
detections,_=load_detections(samples,'output/video-perception/detect-v1')
crops=json.load(open('output/localization-v1/crops-v1/manifest.json'))['samples']
labels=json.load(open(next(Path('ttmp').glob('**/VIDEO-STATE-001*/various/labels-v2.json'))))
by_label={r['sample_id']:r for r in labels}
obs=[json.loads(l) for l in Path('output/localization-v1/state-comparison-v1/observations.jsonl').read_text().splitlines()]
by_obs={(r['sample_id'],r['condition']):r for r in obs}
rows=[r for r in crops if any(a['kind']=='state' for a in r['aliases'])]
def sid(r):return next(a['id'] for a in r['aliases'] if a['kind']=='state')
criteria=[('Train accepted detector',lambda r:r['split']=='train' and r['D']),('Development accepted detector',lambda r:r['split']=='development' and r['D']),('Test known open',lambda r:r['split']=='test' and by_label[sid(r)]['value'] is True),('Test unknown',lambda r:r['split']=='test' and by_label[sid(r)]['value'] is None),('Oracle head error',lambda r:r['split']=='test' and by_label[sid(r)]['value'] is not None and by_obs[sid(r),'O__linear_head']['value']!=by_label[sid(r)]['value'])]
selected=[];seen=set()
for title,accept in criteria:
 r=next(r for r in rows if r['sample_id'] not in seen and accept(r));seen.add(r['sample_id']);selected.append((title,r))
dest=root/'various/outcome-gallery-v1';dest.mkdir(exist_ok=True)
index=[]
for n,(title,r) in enumerate(selected):
 canvas=Image.new('RGB',(1280,580),'white');draw=ImageDraw.Draw(canvas)
 with Image.open(r['F']['image']) as source:
  canvas.paste(source,(0,0))
 for d in detections[r['sample_id']]:
  if d['score']>=.25:
   draw.rectangle(d['xyxy'],outline='lime',width=2);draw.text((d['xyxy'][0],d['xyxy'][1]),d['class_name'],fill='lime')
 for j,c in enumerate(('D','O')):
  if r[c]:
   with Image.open(r[c]['image']) as im:canvas.paste(im,(640+j*320,0))
  else:draw.text((660+j*320,100),'MISSING',fill='red')
  draw.text((640+j*320,245),c+' crop',fill='black')
 state_id=sid(r);label=by_label[state_id]['value']
 draw.text((5,485),title+' / '+state_id,fill='black')
 draw.text((5,505),f'Reviewed state: {label}; split: {r["split"]}; frame: {r["frame_index"]}',fill='black')
 for j,c in enumerate(('F','D','O','FD','FO')):
  o=by_obs[state_id,c+'__linear_head'];draw.text((5+j*250,535),f'{c}: {o["value"]} / {o["unknown_reason"] or "answered"}',fill='black')
 path=dest/f'outcome-{n:02d}.jpg';canvas.save(path,quality=95);index.append({'title':title,'source':r,'state_label':by_label[state_id],'sheet':path.name})
(dest/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print(dest)
