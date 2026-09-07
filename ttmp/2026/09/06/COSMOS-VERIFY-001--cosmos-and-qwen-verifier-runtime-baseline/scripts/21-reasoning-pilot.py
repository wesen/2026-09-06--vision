"""Development-only real model pilots before freezing both experiment protocols."""
from pathlib import Path
import json, argparse
from video_workbench.verifiers.profiles import make_profile
from video_workbench.verifiers.adapter import verify
from video_workbench.rules.evaluate import digest
r=Path(__file__).resolve().parents[1]
request=json.loads((r/'various/visibility-v2/protocol.json').read_text())['cases'][0]['request']
request.update(max_output_tokens=4096,deadline_ms=120000)
request['request_id']=digest({k:v for k,v in request.items() if k!='request_id'})
parser=argparse.ArgumentParser();parser.add_argument('--attempt',default='pilot');args=parser.parse_args()
out=Path('output/verifier-reasoning-v3')/args.attempt;out.mkdir(parents=True,exist_ok=True)
rows=[]
for family,model in [('qwen','output/models/qwen3-vl-instruct-8b-8bit'),('cosmos','output/models/cosmos-reason2-8b-8bit-local')]:
 for reasoning,sampled in [(False,False),(True,False),(False,True),(True,True)]:
  p=make_profile(family,reasoning,sampled)
  result=verify(request,model,out/p['id'],profile=p)
  row=dict(profile=p,status=result['status'],answer=result.get('answer',{}).get('answer'),reason=result.get('reason'),seconds=result['elapsed_seconds'],tokens=result.get('runtime',{}).get('generation_tokens'))
  rows.append(row);(out/'summary.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
