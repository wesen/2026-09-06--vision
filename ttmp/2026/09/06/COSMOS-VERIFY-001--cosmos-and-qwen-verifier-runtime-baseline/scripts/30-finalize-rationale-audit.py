"""Validate completeness and aggregate manually authored final-rationale reviews."""
from pathlib import Path
import collections, json
from video_workbench.registry import file_hash
root=Path(__file__).resolve().parents[1]/'various/reasoning-v3'
audit_path=root/'test-rationale-audit.json'
audit=json.loads(audit_path.read_text())
records=[json.loads(line) for line in (root/'results/test-records.jsonl').read_text().splitlines()]
expected={(r['row']['profile_id'],r['row']['case_id']):r for r in records}
actual={(r['profile_id'],r['case_id']):r for r in audit['rows']}
assert len(actual)==len(audit['rows'])==len(records) and set(actual)==set(expected)
for key,review in actual.items():
    record=expected[key]
    assert review['result_sha256']==file_hash(Path(record['row']['result_path']))
    assert review['rationale']==record['result'].get('answer',{}).get('rationale')
    assert review['rating'] in ('supported','mixed','unsupported','invalid')
    assert (review['rating']=='invalid')==(record['row']['status']!='ok')
    assert review['note'].strip()
audit['complete']=True
audit['protocol_sha256']=file_hash(root/'protocol.json')
audit['summary']={p:dict(collections.Counter(r['rating'] for r in audit['rows'] if r['profile_id']==p)) for p in sorted({r['profile_id'] for r in audit['rows']})}
audit_path.write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit['summary'],indent=2))
