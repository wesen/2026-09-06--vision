"""Probe real Sit/StandUp in all three scenes before rendering the full release."""
from pathlib import Path
import json,requests
from simulation.unity_simulator.comm_unity import UnityCommunication
from virtualhome_corpus import diversity_runner as runner
from virtualhome_corpus.core import save_json
cfg=json.loads(Path('configs/virtualhome-paired-actions-v1.json').read_text());root=Path('output/virtualhome-corpus/paired-actions-v1')
r=requests.post('http://127.0.0.1:18084',json={'id':'actions-ready','action':'idle'},timeout=5);r.raise_for_status();assert r.json()['success']
with runner.corpus_lock(root):
 path=root/'config.json'
 if path.exists():assert json.loads(path.read_text())==cfg
 else:save_json(path,cfg)
 comm=UnityCommunication(port='18084',timeout_wait=90);installation=json.loads(Path('output/virtualhome-install/installation.json').read_text())
 for item in runner.plan(cfg):
  if item['scenario']['family']!='posture' or item['condition']!='interaction' or item['view']!='left':continue
  dest=root/'episodes'/item['episode_id']/'manifest.json'
  if dest.exists() and json.loads(dest.read_text())['status']=='complete':continue
  print('PROBE',item['episode_id'],item['scene_index'],flush=True)
  result=runner.generate(comm,root,cfg,item,installation,runner.producer());print(json.dumps({'status':result['status'],'program':result['program'],'frames':result['frame_count']}),flush=True)
 print(json.dumps(runner.export(root,cfg)),flush=True)
