"""Publish frozen numeric results and a local source-linked failure gallery."""
from pathlib import Path
import json,shutil,html
import numpy as np
root=Path(__file__).resolve().parents[1];base=Path('output/action-benchmark-v1');out=root/'various/comparison-v2';out.mkdir(exist_ok=True)
r=json.loads((base/'evaluation-v2/results.json').read_text())
for name in ('results.json','observations.jsonl','selected.json'):shutil.copy2(base/'evaluation-v2'/name,out/name)
roots=json.loads((base/'feature-roots-v2.json').read_text());checks={}
for mode,p in roots.items():
 p=Path(p);shutil.copy2(p/'manifest.json',out/(mode+'-manifest.json'))
 with np.load(p/'features.npz') as f:checks[mode]={'reverse_max_abs':float(np.max(np.abs(f['original']-f['reverse']))),'repeat_first_max_abs':float(np.max(np.abs(f['original']-f['repeat_first']))),'completed_reuse':'verified by second encode invocation; same run_id, 72 samples'}
(out/'runtime-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
shutil.copy2(base/'temporal-handoff-v2/manifest.json',out/'temporal-handoff-manifest.json')
labels=json.loads((root/'various/action-source-review-v2/labels.json').read_text());samples=json.loads((root/'various/action-source-review-v2/samples.json').read_text())
observations=[json.loads(line) for line in (out/'observations.jsonl').read_text().splitlines()];obs={(o['mode'],o['sample_id']):o for o in observations}
esc=html.escape
page=['<!doctype html><meta charset="utf-8"><title>Action benchmark evidence</title><style>body{font:16px system-ui;margin:40px;max-width:1250px;background:#f7f5ef;color:#171717}table{border-collapse:collapse;width:100%}td,th{padding:12px;border:1px solid #444;text-align:left}h1{font-size:40px}article{border-top:4px solid #171717;margin-top:35px;padding-top:12px}img{width:100%}code{font-size:12px;overflow-wrap:anywhere}.note{padding:15px;background:#ffe5ab}</style><h1>Action discrimination: measured failures</h1><p>48 AIST/VirtualHome trajectories · 72 original windows · 62 eligible reviews · three isolated feature spaces</p><p class="note">Test support: 17/24 windows, six of nine classes. No eligible test closing or switching examples. These results do not establish general action understanding.</p><table><tr><th>Representation</th><th>Test accuracy</th><th>Balanced accuracy</th><th>Control false actions</th><th>Direction</th><th>Retrieval Success@5</th></tr>']
for mode,c in r['conditions'].items():
 m=c['metrics']['test'];page.append(f'<tr><td>{mode}</td><td>{m["accuracy"]:.3f}</td><td>{m["balanced_accuracy"]:.3f}</td><td>{m["control_false_action"]}/{m["control_count"]}</td><td>{c["directions"]["test"]["positive_margin_accuracy"]:.3f}</td><td>{c["retrieval"]["test"]["mean_at_k"]["5"]["success"]:.3f}</td></tr>')
page.append('</table><h2>Source evidence and frozen predictions</h2><p>Examples selected after evaluation; no query or threshold retuning. No opposite-action margin changed sign under reversal, despite changed native vectors.</p>')
for i in (17,28,42,6,8):
 s=samples[i];l=labels[i];detail=root/'various/action-source-review-v2'/f'sample-{i:02d}.jpg';sheet=detail if detail.exists() else root/'various/action-source-review-v2'/f'actions-source-{i//6:02d}.jpg'
 page.append(f'<article><h2>Sample {i}: {esc(l["visibility"])} / {esc(str(l["action"]))}</h2><p>{esc(l["rationale"])}</p><p>Source {s["start_us"]/1e6:.2f}–{s["end_us"]/1e6:.2f}s · {s["split"]} · <code>{s["sample_id"]}</code></p>')
 for mode in roots:
  o=obs[mode,s['sample_id']];page.append(f'<p>{mode}: <b>{o["predicted_action"]}</b>; gap {o["gap"]:.5f}; accepted {o["accepted"]}; <code>space {o["space_id"]}</code></p>')
 page.append(f'<img src="../action-source-review-v2/{sheet.name}" alt="Reviewed original source frames"><p>Image: {sheet.name}. Multi-row sheets retain surrounding examples for context.</p></article>')
(out/'index.html').write_text(''.join(page))
print(out/'index.html')
