"""Run one heavy candidate at a time with a killable whole-process deadline."""
from pathlib import Path
import json
import argparse
import os
import signal
import subprocess
import time
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--pins',type=Path,default=root/'various/candidate-pins.json');parser.add_argument('--output',type=Path,default=Path('output/verifier-v1/image-gate'));args=parser.parse_args()
out=args.output;out.mkdir(parents=True,exist_ok=True)
request=json.loads(next(Path('ttmp/2026/09/06').glob('VIDEO-RULES-001--*')).joinpath('various/r3-handoff/requests.json').read_text())[0]
(out/'request.json').write_text(json.dumps(request,indent=2)+'\n')
python=str(Path('workbench/verify-env/.venv/bin/python').absolute());records=[]
for pin in json.loads(args.pins.read_text()):
    name=Path(pin['local_path']).name;result=out/(name+'.json');log=out/(name+'.log')
    if result.exists():raise ValueError('fresh smoke result required')
    env=dict(os.environ,PYTHONPATH=str(Path('workbench/src').resolve()),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    started=time.perf_counter()
    with log.open('w') as stream:
        process=subprocess.Popen([python,'-m','video_workbench.verifiers.smoke_worker',pin['local_path'],str(out/'request.json'),str(result)],stdout=stream,stderr=subprocess.STDOUT,env=env,start_new_session=True)
        try:code=process.wait(timeout=120);status='finished' if code==0 else 'runtime_error'
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL);process.wait();status='timeout';code=process.returncode
    records.append({'repo_id':pin['repo_id'],'revision':pin['revision'],'status':status,'returncode':code,'wall_seconds':time.perf_counter()-started,'deadline_seconds':120,'log':str(log),'result':str(result) if result.exists() else None})
    print(json.dumps(records[-1]),flush=True)
(out/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
