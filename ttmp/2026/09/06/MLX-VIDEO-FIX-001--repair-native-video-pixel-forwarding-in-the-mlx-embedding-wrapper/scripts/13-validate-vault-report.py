#!/usr/bin/env python3
"""Validate report structure, local assets and vault wikilinks without Obsidian."""
import argparse,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
import yaml
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--report',type=Path);p.add_argument('--vault',type=Path,default=Path('/Users/manuel/code/wesen/go-go-golems/go-go-parc'));args=p.parse_args()
report=args.report or next((root/'various/vault-report').glob('*.md'))
s=report.read_text();front=s.split('---',2);assert len(front)==3
metadata=yaml.safe_load(front[1]);assert all(k in metadata for k in ['title','aliases','tags','status','type','created','repo','ticket'])
assert metadata['repair_revision']=='6452614f6de04694d1e34fd13abaca11f6ffb994'
assert s.count('```')%2==0
assert s.count('```mermaid')==4
assert not re.search(r'think of|like a kitchen|imagine that|traffic cop|delve|in the ever.evolving',s,re.I)
assets=[]
for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',s):
 if target.startswith(('https://','http://','#')):continue
 path=report.parent/target;assert path.is_file(),path
 assets.append({'path':target,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
links=re.findall(r'\[\[([^\]|#]+)',s)
for name in links:assert list(args.vault.rglob(name+'.md')),name
for asset in assets:
 if asset['path'].endswith('.json'):json.loads((report.parent/asset['path']).read_text())
result={'created_at':datetime.now(timezone.utc).isoformat(),'report':str(report),'sha256':hashlib.sha256(report.read_bytes()).hexdigest(),'words':len(s.split()),'mermaid_diagrams':4,'figures':s.count('![]('),'vault_links':links,'assets':assets,'validation':'Frontmatter, fences, local assets, JSON parsing, wikilink resolution, direct technical style scan; plots visually inspected. No Obsidian validation requested.'}
(root/'various/vault-report-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='assets'},indent=2))
