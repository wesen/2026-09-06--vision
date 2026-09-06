from pathlib import Path
import json
from video_workbench.perception.evaluation import identity_counts
from video_workbench.perception.store import write_json
S=Path(__file__).resolve().parents[1]
spans=json.loads((S/'various/track-review-spans.json').read_text());review=json.loads((S/'various/track-reviewed-actor-ids.json').read_text());out=[]
for span in spans:
 tid=review[str(span['span'])];assignments=[];extras=0
 for sample in span['samples']:
  chosen=[t for t in sample['actor_tracks'] if tid is not None and t['track_id'].endswith(':c0:t'+str(tid)) and t['status']=='observed']
  assignments.append({'frame_id':sample['frame_id'],'visible':tid is not None,'observed_track_id':chosen[0]['track_id'] if chosen else None})
  if tid is not None:extras+=sum(t['status']=='observed' and t not in chosen for t in sample['actor_tracks'])
 out.append({'span':span['span'],'episode_id':span['episode_id'],'split':span['split'],'reviewer':'codex-assistant-RGB-and-overlay-correspondence-review-v1','entity':'visible-physical-actor','note':'Actor not visually observable in bed span; do not infer absence or location from simulator.' if tid is None else 'Same physical actor across six consecutive RGB frames; shadows/reflections/portraits are not additional actors.','assignments':assignments,'unmatched_observed_person_tracks':extras,'metrics':identity_counts(assignments)})
write_json(S/'various/identity-review-results.json',out)
print(json.dumps({'spans':len(out),'visible_rows':sum(r['metrics']['visible_rows'] for r in out),'matched_rows':sum(r['metrics']['matched_rows'] for r in out),'id_switches':sum(r['metrics']['id_switches'] for r in out),'extra_person_tracks':sum(r['unmatched_observed_person_tracks'] for r in out)}))
