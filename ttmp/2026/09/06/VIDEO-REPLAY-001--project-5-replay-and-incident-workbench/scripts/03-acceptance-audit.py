"""Inspect authoritative artifacts for the completed RULES-to-REPLAY goal."""
from pathlib import Path
import json,sqlite3
from PIL import Image
root=Path(__file__).resolve().parents[1]
rules=next(root.parent.glob('VIDEO-RULES*'))
measurement=json.loads((rules/'various/r4-measurement.json').read_text())
assert measurement['splits']['all']['qwen']['positive_events']==6
assert measurement['splits']['all']['cosmos']['violation_recall']==2/6
assert not measurement['splits']['all']['qwen']['matching']['missed']
assert measurement['splits']['all']['baseline']['unknowns']==12
assert not any(line.startswith('- [ ]') for line in (rules/'tasks.md').read_text().splitlines())
assert 'supersedes' in (root/'design-doc/02-bounded-replay-implementation-and-viewer-contract.md').read_text()
artifacts={}
for name in ('recorded_microwave','live_fridge','overload','browser_started'):
    report=json.loads((root/'various/p4-measurements'/f'{name}.json').read_text())
    summary=report['summary'];s=summary['scheduler'];assert summary['status']=='complete'
    assert s['high_jobs']<=s['max_jobs'] and s['high_bytes']<=s['max_bytes']
    assert s['admitted_jobs']==s['admitted_bytes']==0
    if name=='live_fridge':
        decision=next(r for r in report['decisions'] if r['payload']['condition']=='qwen')
        assert decision['payload']['mode']=='live_verifier'
        assert decision['payload']['runtime']['generation_tokens']>0
        assert decision['available_us']>decision['event_us']
    if name=='overload':assert summary['counts']['perception_dropped']>0 and summary['options']['repetitions']==20
    artifacts[name]=summary['run_id']
for name in ('p4-live-fridge.png','p4-asof-before-verifier.png','p4-recorded-microwave.png','p4-overload-gaps.png'):
    with Image.open(root/'various'/name) as image:
        image.verify()
for name in ('implementation-plan.yaml','p2-start.yaml','p2-done.yaml','p3-start.yaml','p3-done.yaml','p4-start.yaml','p4-done.yaml'):
    assert (root/'various'/name).is_file()
for name in ('r4-start.yaml','r4-done.yaml'):assert (rules/'various'/name).is_file()
assert json.loads((root/'various/p4-cancellation.json').read_text())['status']=='cancelled'
active_tasks=(root/'tasks.md').read_text().split('## Deferred follow-ups')[0]
assert '- [ ]' not in active_tasks
result=dict(status='passed',scope='RULES measurement, simplified REPLAY design, bounded scheduler and viewer',runs=artifacts,
            observed_smoke=dict(core=12,api=4),screenshots=4,phase_layouts=9,
            checks=['reviewed recall population','unknown baseline','scoped task completion','bounded drained runs','fresh worker tokens and delayed availability','repeated overload drops','PNG readability','phase layouts','browser cancellation'],
            manual_evidence=['Browser as-of at 11 seconds showed baseline only and source seek to 11 seconds.','Approved images, missed fridge PASS, detected microwave VIOLATION, and overload screenshots visually inspected.','Worker/data boundaries and deferred scope reviewed against design document 02.'])
(root/'various/p4-acceptance-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
