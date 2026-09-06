"""Verify every published sparse sequence against original source evidence."""
from pathlib import Path
import json
import numpy as np
from video_workbench.registry import file_hash
base=Path('output/action-benchmark-v1/temporal-handoff-v2')
m=json.loads((base/'manifest.json').read_text());count=0
for e in m['entries']:
 p=base/e['path'];assert file_hash(p)==e['sha256']
 with np.load(p,allow_pickle=False) as f:
  n=len(e['rows']);assert f['features'].shape==(n,2048) and np.isfinite(f['features']).all()
  assert np.allclose(np.linalg.norm(f['features'],axis=1),1,atol=1e-5)
  for i,s in enumerate(e['rows']):
   assert file_hash(s['video'])==s['video_sha256']
   assert f['event_us'][i]==s['end_us'] and f['available_us'][i]>=max(s['selected_pts_us'])
   assert f['valid'][i] and f['label_mask'][i]==(f['targets'][i]>=0)
  count+=n
out={'sequences':len(m['entries']),'feature_rows':count,'spaces':len({e['space_id'] for e in m['entries']}),'status':'all feature hashes, shapes, unit norms, source video hashes, clock mappings and masks verified'}
p=Path(__file__).resolve().parents[1]/'various/comparison-v2/handoff-audit.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
