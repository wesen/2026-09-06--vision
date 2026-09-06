#!/usr/bin/env python3
"""Append-only copy of the reviewed report and assets; no Git/network actions."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
source=root/'various/vault-report'
vault=Path('/Users/manuel/code/wesen/go-go-golems/go-go-parc')
target=vault/'Projects/2026/09/06'
files=[p for p in source.rglob('*') if p.is_file()]
for p in files:
 out=target/p.relative_to(source)
 if out.exists():assert out.read_bytes()==p.read_bytes(),f'refusing to overwrite {out}'
for p in files:
 out=target/p.relative_to(source);out.parent.mkdir(parents=True,exist_ok=True)
 if not out.exists():
  with out.open('xb') as f:f.write(p.read_bytes())
 assert hashlib.sha256(out.read_bytes()).digest()==hashlib.sha256(p.read_bytes()).digest()
receipt={'vault':str(vault),'files':[str((target/p.relative_to(source)).relative_to(vault)) for p in files]}
(root/'various/vault-copy.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
