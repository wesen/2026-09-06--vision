"""Post-observation recovery replay; never overwrites strict results/selection."""
from pathlib import Path
import json,collections
from video_workbench.verifiers.recovery import parse_with_recovery
from video_workbench.registry import file_hash
r=Path(__file__).resolve().parents[1];protocol_path=r/'various/reasoning-v3/protocol.json';protocol=json.loads(protocol_path.read_text());cases={c['source']['id']:c for c in protocol['cases']};out=Path('output/verifier-reasoning-v3');dest=r/'various/reasoning-v3/recovery-replay';dest.mkdir(exist_ok=True)
summary=[]
for phase in ['development','test']:
 source=out/(phase+'-results.json')
 if not source.exists():continue
 original=json.loads(source.read_text());assert original['protocol_sha256']==file_hash(protocol_path)
 replay=[]
 for row in original['rows']:
  result=json.loads(Path(row['result_path']).read_text())
  if result['status'] not in ('ok','invalid') or 'runtime' not in result:
   checked=dict(status=result['status'],reason=result.get('reason'))
  else:
   checked=parse_with_recovery(cases[row['case_id']]['request'],result['runtime']['raw'],result['profile'],result['runtime'].get('finish_reason'))
  answer=checked.get('answer',{}).get('answer') if checked['status']=='ok' else 'invalid'
  replay.append(dict(original=row,replayed=checked,answer=answer,correct=answer==row['expected'],unsupported=row['expected']=='unknown' and answer in ('true','false')))
 with (dest/(phase+'-records.jsonl')).open('w') as f:
  for x in replay:f.write(json.dumps(x)+'\n')
 for family,arm in sorted({(x['original']['family'],x['original']['arm']) for x in replay}):
  group=[x for x in replay if (x['original']['family'],x['original']['arm'])==(family,arm)]
  summary.append(dict(phase=phase,family=family,arm=arm,calls=len(group),strict_invalid=sum(x['original']['status']!='ok' for x in group),replayed_invalid=sum(x['replayed']['status']!='ok' for x in group),recovered=sum('recovery' in x['replayed'] for x in group),strict_correct=sum(x['original']['correct'] for x in group),replayed_correct=sum(x['correct'] for x in group),strict_unsupported=sum(x['original']['unsupported'] for x in group),replayed_unsupported=sum(x['unsupported'] for x in group)))
record=dict(protocol_sha256=file_hash(protocol_path),recovery_sha256=file_hash(Path('workbench/src/video_workbench/verifiers/recovery.py')),interpretation='Post-observation parsing replay. Strict generation records and development selection are unchanged. Counts may be partial until the complete run is archived.',groups=summary)
(dest/'summary.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
