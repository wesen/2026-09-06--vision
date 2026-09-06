from pathlib import Path
import uvicorn
from video_workbench.predicates.region_app import create_app
S=Path(__file__).resolve().parents[1]
uvicorn.run(create_app('output/state-workbench/region-run-v1',S/'various/samples-v2.json',S/'various/labels-v2.json',S/'various/region-evidence-v1.json'),host='127.0.0.1',port=8774)
