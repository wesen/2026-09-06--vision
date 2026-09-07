"""Record source-level runtime evidence without importing or loading MLX."""
from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parents[1];base=Path('workbench/verify-env/.venv/lib/python3.11/site-packages/mlx_vlm')
records=[]
for p in [base/'generate/common.py',base/'generate/ar.py',base/'sample_utils.py',Path('workbench/src/video_workbench/verifiers/worker.py'),Path('output/models/qwen3-vl-instruct-8b-8bit/generation_config.json')]:
 data=p.read_bytes();lines=data.decode().splitlines();matches=[dict(line=i+1,text=line) for i,line in enumerate(lines) if any(s in line for s in ['DEFAULT_TOP','DEFAULT_TEMPERATURE','presence_context_size','presence_penalty','temperature=','max_tokens=','top_p','top_k'])]
 records.append(dict(path=str(p.resolve()),sha256=hashlib.sha256(data).hexdigest(),excerpts=matches))
(r/'sources/qwen3-vl/local-runtime-audit.json').write_text(json.dumps(records,indent=2)+'\n')
manifest=json.loads((r/'sources/qwen3-vl/provenance.json').read_text())
for item in manifest['files']:
 p=r/'sources/qwen3-vl'/item['local'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
print('Verified',len(manifest['files']),'source hashes; recorded five local files')
