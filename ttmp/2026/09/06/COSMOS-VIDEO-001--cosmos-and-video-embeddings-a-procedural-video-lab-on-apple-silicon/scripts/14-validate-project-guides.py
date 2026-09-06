#!/usr/bin/env python3
"""Validate guide structure, links, JSON/Python syntax, and task inventory."""
import ast,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'various/project-tickets.json').read_text())
report=[]
for r in records:
    p=Path(r['guide']);s=p.read_text()
    assert '<!--' not in s, (r['ticket'],'unfilled template')
    assert s.count('```')%2==0
    assert len(s.split())>=1400
    for phrase in ('## Implementation phases','### Decision:','## Shared system contract','### Existing file references'):
        assert phrase in s,(r['ticket'],phrase)
    blocks=re.findall(r'```([^\n]*)\n(.*?)\n```',s,re.S)
    for lang,code in blocks:
        if lang=='json':json.loads(code)
        elif lang=='python':ast.parse(code)
        elif lang=='sql':
            con=sqlite3.connect(':memory:');con.executescript(code);con.close()
    checked=[]
    for target in re.findall(r'\]\(([^)]+)\)',s):
        if target.startswith(('https://','http://','#')):continue
        target=target.split('#')[0]
        assert (p.parent/target).exists(),(r['ticket'],target)
        checked.append(target)
    tasks=(Path(r['path'])/'tasks.md').read_text()
    count=tasks.count('- [ ]')
    assert count>=12
    report.append({'ticket':r['ticket'],'words':len(s.split()),'code_blocks':len(blocks),'local_links_checked':len(checked),'unchecked_tasks_including_delivery':count,'syntax_only_not_application_tests':True})
(ROOT/'various/project-guide-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
