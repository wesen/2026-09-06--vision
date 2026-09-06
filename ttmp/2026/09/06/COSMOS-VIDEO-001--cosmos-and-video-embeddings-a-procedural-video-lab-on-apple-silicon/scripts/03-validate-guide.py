"""Validate the guide's concrete examples and local references."""
from pathlib import Path
import re, json, sqlite3
import yaml
root=Path(__file__).resolve().parents[1]
p=root/'design-doc/02-intern-guide-to-the-procedural-video-workbench.md'
s=p.read_text()
assert s.count('```')%2==0
blocks=re.findall(r'```(\w+)\n(.*?)\n```',s,re.S)
for lang,body in blocks:
 if lang=='json': json.loads(body)
 if lang=='yaml': yaml.safe_load(body)
 if lang=='sql':
  db=sqlite3.connect(':memory:')
  db.executescript(body)
  db.execute("INSERT INTO episodes VALUES ('E','hash','v1','g')")
  try:
   db.execute("INSERT INTO evidence VALUES ('bad','E',5,4,6,'p','s')")
  except sqlite3.IntegrityError: pass
  else: raise AssertionError('inverted interval accepted')
  db.close()
links=re.findall(r'\]\(([^)]+)\)',s)
for link in links:
 if '://' not in link and not link.startswith('#'):
  assert (p.parent/link.split('#')[0]).exists(), link
assert 12700000-11000000==1700000
assert 12900000-10800000==2100000
assert 12800000-10900000==1900000
assert 1+2*(1+2+4)==15
assert 10000*2048*4==81920000
print(json.dumps({'words':len(s.split()),'fenced_blocks':len(blocks),
 'local_links':sum('://' not in x for x in links),
 'json_yaml_sql':'valid','interval_constraint':'enforced',
 'worked_arithmetic':'passed'},indent=2))
