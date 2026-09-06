"""Build model-safe manifest: all diversity families plus original state train sources."""
from pathlib import Path
import json
root=Path('output');records=[]
release=root/'virtualhome-corpus/diversity-v2'
for r in map(json.loads,(release/'inputs.jsonl').read_text().splitlines()):
 records.append(dict(r,video=str((release/r['video']).relative_to(root))))
state=Path('ttmp/2026/09/06/VIDEO-STATE-001--project-2-observable-state-recognition/various/samples-v2.json')
seen={r['episode_id'] for r in records}
for s in json.loads(state.read_text()):
 if s['episode_id'] in seen:continue
 seen.add(s['episode_id'])
 records.append({k:s[k] for k in ('episode_id','split','split_group','video_sha256')}|{'video':str(Path(s['video']).relative_to(root))})
(root/'perception-sources.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in sorted(records,key=lambda r:r['episode_id'])))
print(len(records),'model-safe source episodes')
