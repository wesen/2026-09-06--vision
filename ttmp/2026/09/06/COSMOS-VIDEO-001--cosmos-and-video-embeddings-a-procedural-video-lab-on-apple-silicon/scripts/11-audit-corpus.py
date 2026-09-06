#!/usr/bin/env python3
"""Check corpus metadata against the plan and write a compact tracked inventory.

Run after `virtualhome_corpus validate --deep`. This audit adds plan membership,
index/label consistency, provenance, and per-frame world-state export checks.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from virtualhome_corpus.core import canonical_hash, endpoint_rule, file_hash, plan_episodes, save_json

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=Path('output/virtualhome-corpus/home-v1'))
parser.add_argument('--report', type=Path, default=Path(__file__).resolve().parents[1]/'various/corpus-result-inventory.json')
args = parser.parse_args()
root = args.root.resolve()
header = json.loads((root/'corpus.json').read_text())
plan = plan_episodes(header['config'])
assert json.loads((root/'plan.json').read_text()) == plan
inputs = [json.loads(x) for x in (root/'inputs.jsonl').read_text().splitlines()]
labels = [json.loads(x) for x in (root/'labels.jsonl').read_text().splitlines()]
assert len(inputs) == len(labels) == len(plan)
assert {p.parent.name for p in (root/'episodes').glob('*/manifest.json')} == {x['episode_id'] for x in plan}
records = []
for item, model_input, label in zip(plan, inputs, labels):
    m = json.loads((root/'episodes'/item['episode_id']/'manifest.json').read_text())
    assert m['status'] == 'complete'
    for key in ('episode_id', 'family', 'variant', 'group'):
        assert m[key] == item[key], (item['episode_id'], key)
    assert m['producer'] == header['producer'] and m['installation'] == header['installation']
    assert m['config_hash'] == header['config_hash'] == canonical_hash(header['config'])
    assert m['split'] == item['group']['split'] and m['split_group'] == item['group']['id']
    assert model_input == {k:m[k] for k in ('episode_id','split','split_group','video','video_sha256')}
    assert label == {k:m[k] for k in ('episode_id','family','variant','annotations','rule_truth')}
    attempt = root/m['attempt']
    b = m['bindings']
    truth = endpoint_rule(json.loads((attempt/'graph-after.json').read_text()), b['char0'],b['target'],b['destination'],m['variant']=='closed_before_leaving')
    assert m['rule_truth'] == truth
    annotations = json.loads((root/m['annotations']).read_text())
    assert annotations['precise_boundary_supervision_allowed'] is False
    assert annotations['dense_visual_state_supervision_allowed'] is False
    frames = [json.loads(line) for line in (attempt/'world-frames.jsonl').read_text().splitlines()]
    assert len(frames) == m['frame_count']
    for i, frame in enumerate(frames):
        assert frame['frame_index'] == i and frame['presentation_us'] == i*1_000_000//header['config']['fps']
        graph = json.loads((attempt/frame['source']).read_text(encoding='utf-8-sig'))
        target = next(n for n in graph['nodes'] if n['id']==b['target'])
        assert frame['target_states'] == sorted(target.get('states',[]))
    records.append({k:m[k] for k in ('episode_id','split','split_group','family','variant','frame_count','video','video_sha256','rule_truth','elapsed_s')})
report = {'root':str(root),'config_hash':header['config_hash'],'producer':header['producer'],
          'summary':json.loads((root/'summary.json').read_text()),
          'verdict_counts':dict(Counter(r['rule_truth']['verdict'] for r in records)),
          'render_seconds':sum(r['elapsed_s'] for r in records),
          'video_bytes':sum((root/r['video']).stat().st_size for r in records),
          'index_hashes':{name:file_hash(root/name) for name in ('inputs.jsonl','labels.jsonl','retrieval-queries.json')},
          'checks':['plan membership','provenance','model-input separation','label consistency','endpoint verdicts','world-frame alignment by export index'],
          'episodes':records}
save_json(args.report,report)
print(json.dumps({k:v for k,v in report.items() if k!='episodes'},indent=2))
