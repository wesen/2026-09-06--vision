"""Archive frozen predictions and derive diagnostics without selecting new policies."""
from pathlib import Path
import json,shutil
import numpy as np
from video_workbench.predicates.contracts import StateLabel
from video_workbench.predicates.classify import evaluate,confusion,macro_f1,head_scores
from video_workbench.predicates.features import load_cache
S=Path(__file__).resolve().parents[1]
run=Path('output/state-workbench/run-v2')
archive=S/'various/run-v2';archive.mkdir(exist_ok=True)
for name in ('results.json','observations.jsonl'):
 shutil.copy2(run/name,archive/name)
r=json.loads((run/'results.json').read_text());samples=json.loads((run/'samples.json').read_text());labels=[StateLabel(**l) for l in json.loads((run/'labels.json').read_text())]
obs=[json.loads(l) for l in (run/'observations.jsonl').read_text().splitlines()]
curves={}
for condition,c in r['conditions'].items():
 rows=[o for o in obs if o['condition']==condition]
 curves[condition]={}
 for split in ('train','development','test'):
  indices=[i for i,s in enumerate(samples) if s['split']==split]
  curves[condition][split]=[dict(radius=radius,**evaluate([rows[i]['calibrated_probability'] for i in indices],[labels[i] for i in indices],dict(c['spec']['policy'],radius=radius))) for radius in (0.,.05,.1,.2,.3,.4,.5,1.01)]
metadata,arrays=load_cache('output/state-workbench/features-v2',samples)
raw=head_scores(r['head'],arrays['images'],r['feature_space_id'],{s['entity_class'] for s in samples})
raw_head={}
for split in ('train','development','test'):
 indices=[i for i,s in enumerate(samples) if s['split']==split and labels[i].value is not None]
 counts=confusion([labels[i].value for i in indices],raw[indices]>=0)
 raw_head[split]={'confusion':counts,'macro_f1':macro_f1(counts)}
summary={'note':'Post-run diagnostic sweep only; deployed policies and original predictions remain unchanged. Raw head uses its predeclared regression zero threshold, no test fitting.',
 'raw_head_before_development_calibration':raw_head,
 'image_encoding_seconds':{'sum':sum(metadata['image_seconds']),'median':float(np.median(metadata['image_seconds']))},
 'risk_coverage_sweeps':curves}
(archive/'diagnostics.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='risk_coverage_sweeps'},indent=2))
