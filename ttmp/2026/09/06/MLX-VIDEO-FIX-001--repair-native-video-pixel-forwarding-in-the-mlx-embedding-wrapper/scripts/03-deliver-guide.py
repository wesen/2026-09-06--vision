#!/usr/bin/env python3
"""Render, dry-run, or upload the ticket guide with review/hash gates."""
import argparse, hashlib, json, os, subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('mode',choices=['render','dry-run','upload']);args=p.parse_args()
guide=next((root/'design-doc').glob('01-*.md'))
out=Path('output/pdf/MLX-VIDEO-FIX-001').resolve();out.mkdir(parents=True,exist_ok=True)
source_hash=hashlib.sha256(guide.read_bytes()).hexdigest()
command=['remarquee','upload','md',str(guide),'--name','MLX-VIDEO-FIX-001 Intern Guide',
 '--remote-dir','/ai/2026/09/06/MLX-VIDEO-FIX-001',
 '--pandoc',str(root/'scripts/02-pdf-pandoc.sh'),
 '--pdf-engine','/Library/TeX/texbin/xelatex','--mainfont','Helvetica',
 '--monofont','Menlo','--geometry','margin=0.8in',
 '--latex-header-file',str(root/'scripts/01-pdf-header.tex'),'--non-interactive']
if args.mode=='render':command+=['--pdf-only','--output-dir',str(out)]
if args.mode=='dry-run':command+=['--dry-run']
if args.mode=='upload':
 review=json.loads((root/'various/pdf-validation.json').read_text())
 dry=json.loads((root/'various/upload-dry-run.json').read_text())
 assert review['source_sha256']==source_hash and review['visual_review']=='passed'
 assert dry['source_sha256']==source_hash and dry['returncode']==0
result=subprocess.run(command,env=dict(os.environ,PATH='/Library/TeX/texbin:'+os.environ['PATH']),capture_output=True,text=True,timeout=180)
receipt={'mode':args.mode,'returncode':result.returncode,'source_sha256':source_hash,
 'remote_dir':'/ai/2026/09/06/MLX-VIDEO-FIX-001','output':result.stdout+result.stderr}
name={'render':'render-receipt.json','dry-run':'upload-dry-run.json','upload':'remarkable-upload.json'}[args.mode]
(root/'various'/name).write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['output'],flush=True)
if result.returncode:raise SystemExit(result.returncode)
if args.mode=='upload':assert 'OK: uploaded' in receipt['output']
