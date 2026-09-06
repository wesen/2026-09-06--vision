"""Validate the actual handoff and reject oracle citations in production rows."""
from pathlib import Path
import json,shutil,tempfile
from video_workbench.localization.handoff import export
from video_workbench.registry import file_hash
root=Path(__file__).resolve().parents[1]
source=Path('output/localization-v1/state-comparison-v1')
crop=Path('output/localization-v1/crops-v1/manifest.json')
features=Path('output/localization-v1/features-v1/metadata.json')
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp)
 result=export(source,crop,features,tmp/'valid')
 altered=tmp/'altered';shutil.copytree(source,altered)
 rows=[json.loads(l) for l in (altered/'observations.jsonl').read_text().splitlines()]
 samples=json.loads(crop.read_text())['samples'];by_id={a['id']:s for s in samples for a in s['aliases'] if a['kind']=='state'}
 victim=next(r for r in rows if r['condition']=='F__linear_head')
 victim['evidence_ids']=[by_id[victim['sample_id']]['O']['evidence_id']]
 (altered/'observations.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
 manifest=json.loads((altered/'manifest.json').read_text());manifest['artifacts']['observations.jsonl']=file_hash(altered/'observations.jsonl');(altered/'manifest.json').write_text(json.dumps(manifest))
 try:export(altered,crop,features,tmp/'invalid')
 except ValueError as e:
  assert str(e)=='condition evidence citation mismatch';rejection=str(e)
 else:raise AssertionError('oracle citation accepted as production')
 report={'actual_streams':result['streams'],'production_oracle_citation_rejected':rejection,'invalid_output_published':(tmp/'invalid').exists()}
 (root/'various/temporal-handoff-v2/validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(report)
