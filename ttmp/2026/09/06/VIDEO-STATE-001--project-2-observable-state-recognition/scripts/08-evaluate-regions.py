from pathlib import Path
from video_workbench.predicates.region_experiment import run
S=Path(__file__).resolve().parents[1]
run(S/'various/samples-v2.json',S/'various/labels-v2.json',S/'various/region-evidence-v1.json','output/state-workbench/region-features-v1','output/state-workbench/region-run-v1')
