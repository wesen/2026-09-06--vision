"""Pin 8B verifier inputs; Cosmos is converted locally from official weights."""
from pathlib import Path
import json
from huggingface_hub import HfApi, snapshot_download
root=Path(__file__).resolve().parents[1];pin=root/'various/candidate-pins-8b.json'
if pin.exists(): records=json.loads(pin.read_text())
else:
 records=[]
 for repo,folder in [('mlx-community/Qwen3-VL-8B-Instruct-8bit','qwen3-vl-instruct-8b-8bit'),('nvidia/Cosmos-Reason2-8B','cosmos-reason2-8b-official')]:
  info=HfApi().model_info(repo,files_metadata=True)
  records.append({'repo_id':repo,'revision':info.sha,'local_path':'output/models/'+folder,'files':[{'name':s.rfilename,'size':s.size,'blob_id':s.blob_id} for s in info.siblings]})
 pin.write_text(json.dumps(records,indent=2)+'\n')
for r in records:
 print('downloading',r['repo_id'],r['revision'],flush=True)
 snapshot_download(r['repo_id'],revision=r['revision'],local_dir=r['local_path'],allow_patterns=['*.json','*.safetensors','*.txt','*.jinja','README.md'],max_workers=4)
 print('downloaded',r['local_path'],flush=True)
