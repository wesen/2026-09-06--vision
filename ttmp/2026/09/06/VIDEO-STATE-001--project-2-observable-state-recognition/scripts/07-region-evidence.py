from pathlib import Path
import argparse,json
from video_workbench.predicates.regions import prepare,encode
S=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','encode']);a=p.parse_args()
samples=json.loads((S/'various/samples-v2.json').read_text())
manifest=S/'various/region-evidence-v1.json'
if a.action=='prepare':
 r=prepare(samples,'output/video-perception/derived-v1',manifest)
 from collections import Counter
 print(Counter(s['binding_status'] for s in r['samples']))
else:encode(samples,manifest,'output/state-workbench/features-v2','output/models/qwen3-vl-embedding-2b-4bit','output/state-workbench/region-features-v1')
