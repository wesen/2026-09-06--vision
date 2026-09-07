"""Archive pinned official guidance for inspection, never execute it."""
from pathlib import Path
import urllib.request, hashlib, json
root=Path(__file__).resolve().parents[1]/'sources/cosmos-reason2'
root.mkdir(parents=True,exist_ok=True)
revision='a3b4a1db4065fe13c4b1f4d2fb8605bad647f4b9'
paths=['README.md','LICENSE','docs/troubleshooting.md','docs/llmcompressor.md','scripts/inference_sample.py','cosmos_reason2_utils/cosmos_reason2_utils/script/inference.py']
records=[]
for path in paths:
 url=f'https://raw.githubusercontent.com/nvidia-cosmos/cosmos-reason2/{revision}/{path}'
 data=urllib.request.urlopen(url,timeout=30).read();local=root/Path(path).name;local.write_bytes(data)
 records.append(dict(url=url,path=path,local=local.name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
model=Path('output/models/cosmos-reason2-8b-official/README.md')
if model.exists():
 data=model.read_bytes();(root/'model-card-8b.md').write_bytes(data)
 records.append(dict(url='https://huggingface.co/nvidia/Cosmos-Reason2-8B/blob/a9fae2cf89dc64db96b12860417f0eb403013bb9/README.md',local='model-card-8b.md',sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
(root/'provenance.json').write_text(json.dumps(dict(revision=revision,files=records),indent=2)+'\n')
print('Archived',len(records),'files')
