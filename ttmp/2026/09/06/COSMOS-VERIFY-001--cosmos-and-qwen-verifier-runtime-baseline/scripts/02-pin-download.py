"""Pin public conversion revisions before downloading local verifier candidates."""
from pathlib import Path
import json
from huggingface_hub import HfApi,snapshot_download
root=Path(__file__).resolve().parents[1];pin=root/'various/candidate-pins.json'
if pin.exists():records=json.loads(pin.read_text())
else:
    records=[]
    for repo,folder in [('mlx-community/Qwen3-VL-2B-Instruct-8bit','qwen3-vl-instruct-2b-8bit'),('hzang/Cosmos-Reason2-2B-8bit','cosmos-reason2-2b-8bit')]:
        info=HfApi().model_info(repo,files_metadata=True)
        records.append({'repo_id':repo,'revision':info.sha,'local_path':'output/models/'+folder,'files':[{'name':s.rfilename,'size':s.size,'blob_id':s.blob_id} for s in info.siblings]})
    pin.write_text(json.dumps(records,indent=2)+'\n')
for record in records:
    print('downloading',record['repo_id'],record['revision'],flush=True)
    snapshot_download(record['repo_id'],revision=record['revision'],local_dir=record['local_path'],allow_patterns=['*.json','*.safetensors','*.txt','*.jinja','README.md'],max_workers=4)
    print('downloaded',record['local_path'],flush=True)
