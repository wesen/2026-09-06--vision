from pathlib import Path
import json,shutil,statistics
r=Path(__file__).resolve().parents[1];out=Path('output/verifier-visibility-v2');dest=r/'various/visibility-v2/results';dest.mkdir(exist_ok=True)
summary=[]
for phase in ['development','test']:
 rows=json.loads((out/(phase+'-results.json')).read_text());shutil.copyfile(out/(phase+'-results.json'),dest/(phase+'-results.json'))
 for row in rows:
  p=Path(row['result_path']);local=dest/p.parent.relative_to(out);local.mkdir(parents=True,exist_ok=True)
  for name in ['request.json','result.json','worker-result.json']:
   shutil.copyfile(p.parent/name,local/name)
 for model,variant in sorted(set((x['model'],x['variant']) for x in rows)):
  group=[x for x in rows if (x['model'],x['variant'])==(model,variant)];workers=[json.loads((Path(x['result_path']).parent/'worker-result.json').read_text()) for x in group]
  summary.append(dict(phase=phase,model=model,variant=variant,total=len(group),correct=sum(x['correct'] for x in group),invalid=sum(x['status']!='ok' for x in group),unsupported=sum(x['unsupported'] for x in group),unknown_correct=sum(x['answer']=='unknown' and x['expected']=='unknown' for x in group),generation_seconds_median=statistics.median(x['generation_seconds'] for x in workers),peak_mlx_bytes=max(x['peak_mlx_bytes'] for x in workers),truncated=sum(x.get('finish_reason')=='length' for x in workers)))
shutil.copyfile(out/'selection.json',dest/'selection.json');(dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
