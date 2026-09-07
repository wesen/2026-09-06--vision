"""Select prompt on development only; evaluate the frozen test set once."""
from pathlib import Path
import argparse
import json
from video_workbench.verifiers.adapter import verify
from video_workbench.verifiers.visibility import prompt
from video_workbench.registry import file_hash
root=Path(__file__).resolve().parents[1];protocol_path=root/'various/visibility-v2/protocol.json';protocol=json.loads(protocol_path.read_text())
p=argparse.ArgumentParser();p.add_argument('phase',choices=['development','test']);args=p.parse_args()
pins=json.loads((root/'various/qwen-8b-runtime-pins.json').read_text())+json.loads((root/'various/cosmos-8b-runtime-pins.json').read_text())
out=Path('output/verifier-visibility-v2');out.mkdir(exist_ok=True)
for variant,text in protocol['prompts'].items():assert text==prompt(protocol['cases'][0]['request'],variant),'frozen prompt changed'
if args.phase=='development':variants=['direct','visibility']
else:variants=[json.loads((out/'selection.json').read_text())['variant']]
records=[]
for pin in pins:
 for variant in variants:
  for c in protocol['cases']:
   if c['source']['split']!=args.phase:continue
   dest=out/args.phase/Path(pin['local_path']).name/variant/c['source']['id']
   result=verify(c['request'],pin['local_path'],dest,variant=variant)
   answer=result['answer']['answer'] if result['status']=='ok' else 'invalid'
   row=dict(model=pin['repo_id'],variant=variant,case_id=c['source']['id'],expected=c['expected'],answer=answer,status=result['status'],correct=answer==c['expected'],unsupported=c['expected']=='unknown' and answer in ('true','false'),result_path=str(dest/'result.json'))
   records.append(row);(out/(args.phase+'-results.json')).write_text(json.dumps(records,indent=2)+'\n')
   print(json.dumps(dict(model=pin['repo_id'],variant=variant,completed=len(records),status=result['status'])),flush=True)
if args.phase=='development':
 scores={v:sum(int(r['correct'])-int(r['unsupported']) for r in records if r['variant']==v) for v in variants}
 chosen='visibility' if scores['visibility']>scores['direct'] else 'direct'
 selection=dict(variant=chosen,scores=scores,protocol_sha256=file_hash(protocol_path),policy=protocol['selection'])
 (out/'selection.json').write_text(json.dumps(selection,indent=2)+'\n');print(json.dumps(selection),flush=True)
