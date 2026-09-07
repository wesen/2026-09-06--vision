"""Archive compact measured run identities without committing model outputs."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
repo=next(p for p in root.parents if (p/'workbench').is_dir())
rows=[]
for p in sorted((repo/'output/video-lab').glob('run-*/request.json')):
    r=json.loads(p.read_text());status=json.loads((p.parent/'status.json').read_text())
    result=json.loads((p.parent/'result.json').read_text()) if (p.parent/'result.json').exists() else {}
    rows.append(dict(run_id=r['run_id'],options=r['options'],source=r['evidence']['source'],frames=r['evidence']['frames'],status=status,
                     result_summary={k:result[k] for k in ('kind','mode','feature_space_id','encoder_space_id','checkpoint_identity','checkpoint_sha256','seconds') if k in result},
                     states=[dict(pts_us=x['pts_us'],state=x['state'],validation=x['parsed']['status']) for x in result.get('records',[]) if 'state' in x],
                     windows=result.get('windows',result.get('action_windows',[]))))
(root/'various/measured-runs.json').write_text(json.dumps(rows,indent=2)+'\n')
print(f'Archived {len(rows)} measured run identities')
