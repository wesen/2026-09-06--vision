"""Archive complete experiment records, aggregate by case, and render review panels."""
from pathlib import Path
import collections,json,statistics,math,textwrap
from PIL import Image,ImageDraw,ImageFont
from video_workbench.registry import file_hash
r=Path(__file__).resolve().parents[1];p=r/'various/reasoning-v3/protocol.json';protocol=json.loads(p.read_text());out=Path('output/verifier-reasoning-v3');dest=r/'various/reasoning-v3/results';dest.mkdir(exist_ok=True)
cases={c['source']['id']:c for c in protocol['cases']}
summary=[]
def mean(xs):return statistics.mean(xs) if xs else None
def quantile(xs,q):return sorted(xs)[max(0,math.ceil(q*len(xs))-1)] if xs else None
for phase in ['development','test']:
 source=out/(phase+'-results.json')
 if not source.exists():continue
 record=json.loads(source.read_text());assert record['protocol_sha256']==file_hash(p);rows=record['rows']
 archive=[]
 for row in rows:
  result=json.loads(Path(row['result_path']).read_text());assert result['request_id']==cases[row['case_id']]['request']['request_id']
  archive.append(dict(row=row,result=result))
 with (dest/(phase+'-records.jsonl')).open('w') as f:
  for x in archive:f.write(json.dumps(x)+'\n')
 for family,arm in sorted({(x['family'],x['arm']) for x in rows}):
  group=[x for x in rows if (x['family'],x['arm'])==(family,arm)];bycase=collections.defaultdict(list)
  for x in group:bycase[x['case_id']].append(x)
  accuracy=mean([mean([x['correct'] for x in g]) for g in bycase.values()])
  known=[g for g in bycase.values() if g[0]['expected']!='unknown'];unknown=[g for g in bycase.values() if g[0]['expected']=='unknown']
  runtime=[x['result'].get('runtime',{}) for x in archive if (x['row']['family'],x['row']['arm'])==(family,arm)]
  tokens=[x['generation_tokens'] for x in runtime if 'generation_tokens' in x]
  peaks=[x['peak_mlx_bytes'] for x in runtime if 'peak_mlx_bytes' in x]
  seed_scores={str(s):mean([x['correct'] for x in group if x['seed']==s]) for s in sorted({x['seed'] for x in group})}
  episodes={eid:mean([mean([x['correct'] for x in g]) for g in bycase.values() if g[0]['episode_id']==eid]) for eid in sorted({x['episode_id'] for x in group})}
  summary.append(dict(phase=phase,family=family,arm=arm,cases=len(bycase),calls=len(group),correct_calls=sum(x['correct'] for x in group),case_accuracy=accuracy,
    known_case_accuracy=mean([mean([x['correct'] for x in g]) for g in known]),unknown_cases=len(unknown),unknown_recall=mean([mean([x['correct'] for x in g]) for g in unknown]),
    unsupported_calls=sum(x['unsupported'] for x in group),unsupported_rate_on_unknown=mean([mean([x['unsupported'] for x in g]) for g in unknown]),
    statuses=dict(collections.Counter(x['status'] for x in group)),failure_reasons=dict(collections.Counter(x['reason'] for x in group if x['reason'])),
    median_seconds=statistics.median(x['elapsed_seconds'] for x in group),p95_seconds=quantile([x['elapsed_seconds'] for x in group],.95),
    median_generation_tokens=statistics.median(tokens) if tokens else None,max_generation_tokens=max(tokens) if tokens else None,peak_mlx_bytes=max(peaks) if peaks else None,
    seed_accuracy=seed_scores,episode_accuracy=episodes))
 if phase=='test':
  panel_dir=dest/'panels';panel_dir.mkdir(exist_ok=True)
  font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',17)
  for cid,c in cases.items():
   if c['source']['split']!='test':continue
   groups=collections.defaultdict(list)
   for x in archive:
    if x['row']['case_id']==cid:groups[(x['row']['family'],x['row']['arm'])].append(x)
   canvas=Image.new('RGB',(1280,610+len(groups)*160),'white');draw=ImageDraw.Draw(canvas)
   draw.text((20,15),f'{cid} | reviewed: {c["expected"]} | {c["source"]["entity_class"]}',font=font,fill='black')
   original=Image.open(c['request']['frames'][0]['path']);canvas.paste(original,(20,55))
   draw.multiline_text((700,65),'\n'.join(textwrap.wrap(c['review_rationale'],49)),font=font,fill='black',spacing=6)
   y=555
   for (family,arm),items in sorted(groups.items()):
    votes=dict(collections.Counter(x['row']['answer'] for x in items));draw.text((20,y),f'{family} {arm} | answers across seeds: {votes}',font=font,fill='black')
    first=items[0];rationale=first['result'].get('answer',{}).get('rationale',first['result'].get('reason','Unavailable'))
    draw.multiline_text((20,y+30),'\n'.join(textwrap.wrap('First-seed rationale (model claim): '+rationale,115)[:5]),font=font,fill='black',spacing=4)
    y+=160
   canvas.save(panel_dir/(cid+'.png'))
  # A fixed, explicitly limited rationale-review set: one visible closed, one open,
  # and every unknown test case, for every evaluated arm and seed.
  chosen=[]
  for label in ['false','true']:
   chosen.append(next(c['source']['id'] for c in protocol['cases'] if c['source']['split']=='test' and c['expected']==label))
  chosen += [c['source']['id'] for c in protocol['cases'] if c['source']['split']=='test' and c['expected']=='unknown']
  review=[dict(case_id=x['row']['case_id'],profile_id=x['row']['profile_id'],seed=x['row']['seed'],expected=x['row']['expected'],answer=x['row']['answer'],rationale=x['result'].get('answer',{}).get('rationale'),status=x['row']['status']) for x in archive if x['row']['case_id'] in chosen]
  (dest/'rationale-review-input.json').write_text(json.dumps(review,indent=2)+'\n')
(dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
if (out/'selection.json').exists():(dest/'selection.json').write_text((out/'selection.json').read_text())
print(json.dumps(summary,indent=2))
