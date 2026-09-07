"""Convert the pinned official Cosmos weights locally; preserve provenance."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import time
from mlx_vlm.convert import convert
root=Path(__file__).resolve().parents[1]
source=json.loads((root/'various/candidate-pins-8b.json').read_text())[1]
out=Path('output/models/cosmos-reason2-8b-8bit-local')
if out.exists(): raise ValueError('fresh conversion directory required')
start=time.perf_counter()
convert(hf_path=source['local_path'],mlx_path=str(out),quantize=True,q_bits=8,q_group_size=64,q_mode='affine',trust_remote_code=False)
files=[]
for p in sorted(out.iterdir()):
 if p.is_file():
  h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(8*1024*1024),b''): h.update(chunk)
  files.append({'name':p.name,'size':p.stat().st_size,'sha256':h.hexdigest()})
record={'source_repo':source['repo_id'],'source_revision':source['revision'],'local_path':str(out),'conversion':{'engine':'mlx-vlm','version':importlib.metadata.version('mlx-vlm'),'bits':8,'group_size':64,'mode':'affine','trust_remote_code':False},'seconds':time.perf_counter()-start,'files':files,'claim':'Local quantized conversion; no full-precision numerical parity claim.'}
(root/'various/cosmos-8b-conversion.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='files'}))
