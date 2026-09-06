"""Materialize the assistant's RGB review, never derive truth from simulator actions."""
from pathlib import Path
from dataclasses import asdict
from collections import Counter
import json
import shutil
from video_workbench.predicates.contracts import StateLabel, load_dataset
S = Path(__file__).resolve().parents[1]
R = Path('output/state-workbench/review-v2')
codes = json.loads((S/'various/review-codes-v2.json').read_text())
samples = json.loads((R/'samples.json').read_text())
meanings = {
 'C': (False, 'visible', 'Door panel appears seated against the appliance; no visible opening.'),
 'O': (True, 'visible', 'Door projects away from appliance and/or interior opening is visible; ajar counts open.'),
 'A': (None, 'ambiguous', 'Visible hand/edge and partial motion do not establish the door angle reliably.'),
 'U': (None, 'occluded', 'Actor hides the door area needed to discriminate open from closed.'),
}
labels=[]
for s in samples:
 value, visibility, reason = meanings[codes[str(s['review_sheet'])][s['ordinal']]]
 labels.append(asdict(StateLabel(s['sample_id'],s['entity_id'],'door_open',value,visibility,'codex-assistant-single-rgb-review','rgb-v2-r1','reviewed_rgb',reason)))
for name, rows in [('samples-v2.json',samples),('labels-v2.json',labels)]:
 (S/'various'/name).write_text(json.dumps(rows,indent=2)+'\n')
load_dataset(S/'various/samples-v2.json',S/'various/labels-v2.json')
counts=Counter((s['split'],s['entity_class'],str(l['value']),l['observability']) for s,l in zip(samples,labels))
summary={'reviewer_limit':'Single assistant RGB review, not independent human gold; ambiguous frames retained as null.',
 'sampling':'Six fixed relative positions per episode; full frame; no score-driven selection.',
 'split_policy':'All home-v1 apartment-0 examples reassigned train; diversity-v2 apartment groups preserved.',
 'counts':[dict(zip(('split','entity_class','value','observability'),k),count=v) for k,v in sorted(counts.items())],
 'episodes':len({s['episode_id'] for s in samples}), 'samples':len(samples),
 'limitations':['Only one apartment per split; appliance confounded with evaluation split.', 'Development has two open fridge frames; class support is insufficient for a reliable calibration claim.', 'No out-of-frame examples; occlusion examples occur only in test.', 'Frame counts are correlated within episodes, not independent trials.']}
(S/'various/label-summary-v2.json').write_text(json.dumps(summary,indent=2)+'\n')
for p in R.glob('sheet-*.jpg'):
 shutil.copy2(p,S/'various/screenshots'/p.name)
print(json.dumps(summary,indent=2))
