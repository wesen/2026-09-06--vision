#!/usr/bin/env python3
"""Render or deliver each ticket's guide with the same reviewed PDF settings.

Usage: python3 SCRIPT render|dry-run|upload [--ticket ID]
Upload authorization is supplied by the user's request; dry-run precedes upload.
"""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['render','dry-run','upload']);parser.add_argument('--ticket')
args=parser.parse_args()
records=json.loads((ROOT/'various/project-tickets.json').read_text())
env=dict(os.environ);env['PATH']='/Library/TeX/texbin:'+env['PATH']
for r in records:
    if args.ticket and r['ticket']!=args.ticket:continue
    ticket=Path(r['path']);guide=Path(r['guide']).resolve()
    out=Path('output/pdf/project-guides')/r['ticket'];out.mkdir(parents=True,exist_ok=True)
    header=ticket/'scripts/01-pdf-header.tex';header.parent.mkdir(exist_ok=True)
    if args.mode=='render':
        header.write_text((ROOT/'scripts/04-pdf-header.tex').read_text().replace('COSMOS-VIDEO-001',r['ticket']))
    name=r['ticket']+' Intern Guide'
    command=['remarquee','upload','md',str(guide),'--name',name,
        '--remote-dir','/ai/2026/09/06/'+r['ticket'],
        '--pandoc',str((ROOT/'scripts/05-pdf-pandoc.sh').resolve()),
        '--pdf-engine','/Library/TeX/texbin/xelatex','--mainfont','Helvetica',
        '--monofont','Menlo','--geometry','margin=0.8in',
        '--latex-header-file',str(header.resolve()),'--non-interactive']
    if args.mode=='render':command+=['--pdf-only','--output-dir',str(out.resolve())]
    elif args.mode=='dry-run':command+=['--dry-run']
    elif args.mode=='upload':
        validation=json.loads((ticket/'various/pdf-validation.json').read_text())
        assert validation['source_sha256']==hashlib.sha256(guide.read_bytes()).hexdigest(), 'Source changed after review'
        assert validation['visual_review']=='passed', 'PDF visual review incomplete'
        dry=json.loads((ticket/'various/upload-dry-run.json').read_text())
        assert dry['returncode']==0 and dry['source_sha256']==validation['source_sha256']
    print(args.mode,r['ticket'],flush=True)
    result=subprocess.run(command,env=env,text=True,capture_output=True,timeout=180)
    (out/(args.mode+'.log')).write_text(result.stdout+result.stderr)
    if result.returncode:
        print(result.stdout+result.stderr,flush=True)
        raise SystemExit(result.returncode)
    if args.mode in ('dry-run','upload'):
        receipt={'ticket':r['ticket'],'mode':args.mode,'returncode':result.returncode,
                 'source_sha256':hashlib.sha256(guide.read_bytes()).hexdigest(),
                 'remote_dir':'/ai/2026/09/06/'+r['ticket'],
                 'output':result.stdout+result.stderr}
        if args.mode=='upload':assert 'OK: uploaded' in receipt['output'], 'Missing positive upload receipt'
        (ticket/'various'/('upload-dry-run.json' if args.mode=='dry-run' else 'remarkable-upload.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print((result.stdout+result.stderr).strip()[-600:],flush=True)
