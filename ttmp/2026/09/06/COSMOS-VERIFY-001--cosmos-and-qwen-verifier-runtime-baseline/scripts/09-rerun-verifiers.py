"""Matched frozen evaluation; one resident model, fresh generation cache per request."""
from pathlib import Path
import argparse
import json
import os
import selectors
import signal
import subprocess
import sys
import time
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--worker',type=int);args=p.parse_args()
protocol=json.loads((root/'various/rerun/protocol.json').read_text())
pins=json.loads((root/'various/candidate-pins.json').read_text())+json.loads((root/'various/qwen-8b-runtime-pins.json').read_text())+json.loads((root/'various/cosmos-8b-runtime-pins.json').read_text())
out=Path('output/verifier-rerun-v1');out.mkdir(exist_ok=True)
if args.worker is not None:
 from video_workbench.verifiers.smoke_worker import run
 import mlx.core as mx
 pin=pins[args.worker];folder=out/Path(pin['local_path']).name;folder.mkdir(exist_ok=True);bundle=None
 for i,c in enumerate(protocol['cases']):
  result=folder/(c['sample_id']+'.json');request=folder/(c['sample_id']+'.request.json')
  if result.exists():raise ValueError('fresh result required')
  request.write_text(json.dumps(c['request'],indent=2)+'\n');mx.reset_peak_memory()
  print(json.dumps({'event':'start','case':i}),flush=True)
  bundle=run(pin['local_path'],request,result,model_bundle=bundle)
  mx.clear_cache()
  print(json.dumps({'event':'complete','case':i}),flush=True)
else:
 records=[]
 for i,pin in enumerate(pins):
  start=time.perf_counter();last=start;deadline=120
  env=dict(os.environ,PYTHONPATH=str(Path('workbench/src').absolute()),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',PYTHONUNBUFFERED='1')
  log=out/(Path(pin['local_path']).name+'.log')
  proc=subprocess.Popen([sys.executable,__file__,'--worker',str(i)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  sel=selectors.DefaultSelector();sel.register(proc.stdout,selectors.EVENT_READ);status='finished';completed=0
  with log.open('wb') as f:
   while True:
    if time.perf_counter()-last>deadline:
     os.killpg(proc.pid,signal.SIGKILL);status='timeout';proc.wait();break
    ready=sel.select(timeout=1)
    if ready:
     line=proc.stdout.readline()
     if not line:break
     f.write(line);f.flush()
     try:message=json.loads(line)
     except (ValueError,UnicodeDecodeError):continue
     if message.get('event')=='start':last=time.perf_counter();deadline=60
     elif message.get('event')=='complete':
      completed+=1;last=time.perf_counter();deadline=60
      print(json.dumps({'model':pin['repo_id'],'completed':completed,'total':len(protocol['cases'])}),flush=True)
   proc.wait();sel.close()
  if proc.returncode!=0 and status=='finished':status='runtime_error'
  records.append(dict(pin=pin,status=status,returncode=proc.returncode,completed=completed,wall_seconds=time.perf_counter()-start,log=str(log)))
  (out/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
  if status!='finished':raise RuntimeError(f'worker failed: {log}')
