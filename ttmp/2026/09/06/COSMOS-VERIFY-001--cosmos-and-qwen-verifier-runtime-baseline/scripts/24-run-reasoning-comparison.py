"""Sequential isolated calls; freeze both development selections before test."""
from pathlib import Path
import argparse,json,statistics,time
from video_workbench.verifiers.adapter import verify
from video_workbench.verifiers.profiles import profile_hash
from video_workbench.registry import file_hash
r=Path(__file__).resolve().parents[1];protocol_path=r/'various/reasoning-v3/protocol.json';protocol=json.loads(protocol_path.read_text());out=Path('output/verifier-reasoning-v3')
p=argparse.ArgumentParser();p.add_argument('phase',choices=['development','test']);args=p.parse_args()
for path,h in protocol['code_sha256'].items():assert file_hash(path)==h, 'frozen runtime changed: '+path
protocol_sha=file_hash(protocol_path)
def arm(profile):return ('R' if profile['prompt_style']=='reasoning' else 'D')+'-'+('S' if profile['temperature'] else 'G')
selections=None
if args.phase=='test':
 selections=json.loads((out/'selection.json').read_text());assert selections['protocol_sha256']==protocol_sha and set(selections['models'])==set(protocol['models'])
rows=[];started=time.monotonic()
for family,model in protocol['models'].items():
 entries=model['profiles']
 if selections:entries=[e for e in entries if arm(e['profile']) in {'D-G',selections['models'][family]['selected']}]
 for entry in entries:
  profile=entry['profile'];assert profile_hash(profile)==entry['profile_sha256']
  for c in protocol['cases']:
   if c['source']['split']!=args.phase:continue
   dest=out/args.phase/profile['id']/c['source']['id'];path=dest/'result.json'
   if path.exists():
    result=json.loads(path.read_text());assert result['profile_sha256']==entry['profile_sha256'] and result['request_id']==c['request']['request_id']
   else:result=verify(c['request'],model['pin']['local_path'],dest,profile=profile)
   answer=result.get('answer',{}).get('answer') if result['status']=='ok' else 'invalid'
   row=dict(family=family,arm=arm(profile),profile_id=profile['id'],seed=profile['seed'],case_id=c['source']['id'],episode_id=c['source']['episode_id'],expected=c['expected'],answer=answer,status=result['status'],reason=result.get('reason'),correct=answer==c['expected'],unsupported=c['expected']=='unknown' and answer in ('true','false'),elapsed_seconds=result['elapsed_seconds'],result_path=str(path))
   rows.append(row);(out/(args.phase+'-results.json')).write_text(json.dumps(dict(protocol_sha256=protocol_sha,rows=rows),indent=2)+'\n')
   print(json.dumps(dict(phase=args.phase,n=len(rows),family=family,arm=row['arm'],status=row['status'],seconds=round(time.monotonic()-started,1))),flush=True)
if args.phase=='development':
 selected={}
 for family in protocol['models']:
  scores={}
  for a in ['D-G','R-G','D-S','R-S']:
   group=[x for x in rows if x['family']==family and x['arm']==a];case_ids={x['case_id'] for x in group}
   score=statistics.mean(statistics.mean(int(x['correct'])-int(x['unsupported']) for x in group if x['case_id']==c) for c in case_ids)
   unsupported=statistics.mean(x['unsupported'] for x in group)
   scores[a]=dict(score=score,unsupported=unsupported,median_seconds=statistics.median(x['elapsed_seconds'] for x in group),calls=len(group),correct=sum(x['correct'] for x in group),invalid=sum(x['status']!='ok' for x in group))
  best=min(scores,key=lambda a:(-scores[a]['score'],scores[a]['unsupported'],scores[a]['median_seconds'],a.startswith('R'),a.endswith('S')))
  if scores[best]['score']<=scores['D-G']['score']+1e-12:best='D-G'
  selected[family]=dict(selected=best,scores=scores)
 record=dict(protocol_sha256=protocol_sha,models=selected)
 (out/'selection.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
