from pathlib import Path
import json,shutil
from video_workbench.perception.segmentation import probe_masks
S=Path(__file__).resolve().parents[1]
r=probe_masks(json.loads((S/'various/pilot-samples.json').read_text()),'output/models/yolo11/yolo11n-seg.pt','output/video-perception/masks-v1')
for record in r['records']:shutil.copy2(record['overlay'],S/'various/screenshots'/Path(record['overlay']).name)
shutil.copy2('output/video-perception/masks-v1/masks.json',S/'various/mask-probe.json')
print('Saved',len(r['records']),'mask overlays;',sum(len(r['masks']) for r in r['records']),'raw instance masks')
