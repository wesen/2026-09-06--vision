#!/usr/bin/env python3
"""Render, dry-run, or upload only this ticket's guide; preserve receipts."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
T=Path(__file__).resolve().parent.parent
G=T/'design-doc/01-intern-analysis-design-and-implementation-guide.md'
mode=sys.argv[1]
assert mode in ('render','dry-run','upload')
source_hash=hashlib.sha256(G.read_bytes()).hexdigest()
if mode=='upload':
 qa=json.loads((T/'various/pdf-validation.json').read_text())
 assert qa['source_sha256']==source_hash and qa['visual_review']=='passed'
 dry=json.loads((T/'various/upload-dry-run.json').read_text())
 assert dry['source_sha256']==source_hash and dry['returncode']==0
cmd=['remarquee','upload','md',str(G),'--name','VIDEO-PERCEPTION-001 Intern Guide','--remote-dir','/ai/2026/09/06/VIDEO-PERCEPTION-001','--pandoc',str(T/'scripts/03-pandoc.sh'),'--pdf-engine','/Library/TeX/texbin/xelatex','--mainfont','Helvetica','--monofont','Menlo','--geometry','margin=0.8in','--latex-header-file',str(T/'scripts/04-pdf-header.tex'),'--non-interactive']
if mode=='render':cmd+=['--pdf-only','--output-dir',str(T/'various/pdf')]
if mode=='dry-run':cmd+=['--dry-run']
env=dict(os.environ);env['PATH']='/Library/TeX/texbin:'+env['PATH']
r=subprocess.run(cmd,text=True,capture_output=True,env=env,timeout=180)
receipt={'mode':mode,'returncode':r.returncode,'source_sha256':source_hash,'remote_dir':'/ai/2026/09/06/VIDEO-PERCEPTION-001','output':r.stdout+r.stderr}
name={'render':'render-receipt.json','dry-run':'upload-dry-run.json','upload':'remarkable-upload.json'}[mode]
(T/'various'/name).write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['output']);assert r.returncode==0
if mode=='upload':assert 'OK: uploaded' in receipt['output']
