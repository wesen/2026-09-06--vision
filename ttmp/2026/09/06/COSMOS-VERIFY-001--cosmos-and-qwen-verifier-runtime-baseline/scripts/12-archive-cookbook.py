"""Archive exact upstream recipe sources for review; never execute downloaded code."""
from pathlib import Path
import urllib.request
import hashlib
import json
root=Path(__file__).resolve().parents[1]/'sources/cosmos-cookbook';root.mkdir(parents=True,exist_ok=True)
revision='d0857364e8a727be41b181731e03f478213e4558'
prefix='docs/recipes/inference/reason2/worker_safety/'
paths=[prefix+x for x in ['SUMMARY.md','inference.md','setup.md','worker_safety.ipynb','worker_safety.py']]+['docs/getting_started/prompt_guide/reason_guide.md','LICENSE']
records=[]
for path in paths:
 url=f'https://raw.githubusercontent.com/nvidia-cosmos/cosmos-cookbook/{revision}/{path}'
 data=urllib.request.urlopen(url).read();local=root/Path(path).name;local.write_bytes(data)
 records.append(dict(source_url=url,repo_path=path,local_path=str(local),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
(root/'provenance.json').write_text(json.dumps(dict(revision=revision,files=records),indent=2)+'\n')
print('archived',len(records),'sources')
