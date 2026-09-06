from pathlib import Path
import json
from collections import Counter,defaultdict
from PIL import Image,ImageDraw
from video_workbench.media import decode_selected
from video_workbench.perception.store import rows,write_json,verify_episode
from video_workbench.perception.pipeline import overlay
S=Path(__file__).resolve().parents[1];source=Path('output/video-perception/detect-v1');derived=Path('output/video-perception/derived-v1')
pilot=json.loads((S/'various/pilot-samples.json').read_text());spans=[]
for ordinal,pilot_index in enumerate((0,3,6,7,8,13,15,16)):
 s=pilot[pilot_index];eid=s['episode_id'];a=source/'episodes'/eid;b=derived/'episodes'/eid
 m=verify_episode(a);frames=rows(a/'frames.jsonl');tracks=rows(b/'tracks.jsonl');ds=rows(a/'detections.jsonl');mid=len(frames)//2;indices=list(range(max(0,mid-3),mid+3));images=decode_selected(m['episode']['video'],indices)
 sheet=Image.new('RGB',(1920,1020),'white');draw=ImageDraw.Draw(sheet);samples=[]
 for j,i in enumerate(indices):
  f=frames[i];ts=[t for t in tracks if t['frame_id']==f['frame_id']];detections=[d for d in ds if d['frame_id']==f['frame_id']]
  im=overlay(images[i],detections,ts);x=j%3*640;y=j//3*510;sheet.paste(im,(x,y+30));draw.text((x+8,y+8),f"span {ordinal} / frame {i} / {s['target_class']} / {(f['pts_us']/1e6):.1f}s",fill='black')
  samples.append({'frame_index':i,'frame_id':f['frame_id'],'pts_us':f['pts_us'],'actor_tracks':[t for t in ts if t['class_id']==0]})
 sheet.save(S/'various/screenshots'/f'track-span-{ordinal:02d}.jpg',quality=95)
 spans.append({'span':ordinal,'episode_id':eid,'split':s['split'],'target':s['target_class'],'samples':samples})
write_json(S/'various/track-review-spans.json',spans)
# Evaluator-only joins. No action metadata enters detector or proposal generation.
cal= json.loads(Path('ttmp/2026/09/06/VIDEO-CORPUS-001--virtualhome-corpus-expansion-and-label-calibration/various/calibration-assessment-v1.json').read_text())
events=[]
for r in cal:
 ps=rows(derived/'episodes'/r['episode_id']/'proposals.jsonl');us=rows(derived/'episodes'/r['episode_id']/'uniform.jsonl')
 for ev in r['events']:
  if ev['reviewed_seconds_bracket'] is None:continue
  lo,hi=[round(v*1e6) for v in ev['reviewed_seconds_bracket']]
  def assessment(packets):
   chosen=[p for p in packets if p['selected']];overlap=sum(max(0,min(hi,p['interval_us'][1])-max(lo,p['interval_us'][0])) for p in chosen)
   evidence=[f for p in chosen for f in p['evidence_ids']]
   fs=rows(source/'episodes'/r['episode_id']/'frames.jsonl');times={f['frame_id']:f['pts_us'] for f in fs}
   return {'bracket_overlap_us':overlap,'bracket_width_us':hi-lo,'complete_bracket_miss':overlap==0,'bracket_fully_covered':overlap>=hi-lo,'has_sample_inside_bracket':any(lo<=times[f]<=hi for f in evidence)}
  events.append({'episode_id':r['episode_id'],'action':ev['action'],'bracket_us':[lo,hi],'proposed':assessment(ps),'uniform':assessment(us)})
summary=[]
for entry in json.loads((source/'run.json').read_text())['episodes']:
 eid=entry['episode_id'];a=source/'episodes'/eid;b=derived/'episodes'/eid;m=verify_episode(a);d=verify_episode(b);p=rows(b/'proposals.jsonl');u=rows(b/'uniform.jsonl');frames=rows(a/'frames.jsonl');tracks=rows(b/'tracks.jsonl')
 labels={}
 if eid.startswith('dv-'):
  manifest=json.loads((Path('output/virtualhome-corpus/diversity-v2/episodes')/eid/'manifest.json').read_text());labels={k:manifest[k] for k in ('condition','lineage_id')};labels['family']=manifest['scenario']['family']
 summary.append(dict(episode_id=eid,split=m['episode']['split'],split_group=m['episode']['split_group'],frames=m['frames'],detections=m['detections'],detector_seconds=m['detector_seconds'],track_seconds=d['track_seconds'],tracks=len(tracks),predicted_tracks=sum(t['status']=='predicted' for t in tracks),crops=d['counts']['crops'],uniform_calls=len(u),selected_calls=sum(q['selected'] for q in p),selected_pixels=sum(len(q['evidence_ids'])*640*480 for q in p if q['selected']),uniform_pixels=sum(len(q['evidence_ids'])*640*480 for q in u),selected_seconds=sum((q['interval_us'][1]-q['interval_us'][0])/1e6 for q in p if q['selected']),total_seconds=m['episode']['media']['duration_us']/1e6,**labels))
write_json(S/'various/pipeline-evaluation.json',{'episodes':summary,'reviewed_transition_brackets':events,'limitations':['Target-only 24-frame initial-frame pilot, not exhaustive detection AP.','Bracket coverage is not action-time accuracy; no dense reviewed action spans for pickup/posture/switch.','Eight short identity spans require manual visual adjudication.','Final unclosed bins omitted in causal selector and included in total duration denominator.']})
print(json.dumps({'episodes':len(summary),'frames':sum(r['frames'] for r in summary),'detector_seconds':sum(r['detector_seconds'] for r in summary),'tracks':sum(r['tracks'] for r in summary),'crops':sum(r['crops'] for r in summary),'uniform_calls':sum(r['uniform_calls'] for r in summary),'selected_calls':sum(r['selected_calls'] for r in summary),'reviewed_brackets':len(events),'proposed_complete_misses':sum(e['proposed']['complete_bracket_miss'] for e in events)},indent=2))
