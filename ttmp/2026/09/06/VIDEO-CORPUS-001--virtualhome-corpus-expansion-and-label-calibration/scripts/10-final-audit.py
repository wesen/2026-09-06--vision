"""Freeze release audit: provenance, duration-only baseline, derivatives, and v1 preservation."""
from pathlib import Path
from collections import Counter
import json
from virtualhome_corpus.core import file_hash,save_json
root=Path('output/virtualhome-corpus/diversity-v2');ticket=Path(__file__).resolve().parent.parent
ms=[json.loads(p.read_text()) for p in sorted((root/'episodes').glob('*/manifest.json'))]
assert len(ms)==48 and all(m['status']=='complete' for m in ms)
inputs=[json.loads(s) for s in (root/'inputs.jsonl').read_text().splitlines()];windows=[json.loads(s) for s in (root/'windows-v1/inputs.jsonl').read_text().splitlines()];labels=[json.loads(s) for s in (root/'windows-v1/labels.jsonl').read_text().splitlines()]
assert len(windows)==len(labels)==48
keys={'episode_id','split','split_group','video','video_sha256'}
assert all(set(r)==keys for r in inputs+windows)
parents={m['episode_id']:m for m in ms};seen={}
for row in labels:
 p=parents[row['parent_episode_id']]
 assert row['split']==p['split'] and row['split_group']==p['split_group'] and row['lineage_id']==p['lineage_id']
 assert row['frames']==20 and row['fps']==10 and row['end_frame_exclusive']-row['start_frame']==20
 assert file_hash(root/'windows-v1'/(row['episode_id']+'.mp4'))==row['video_sha256']
 assert seen.setdefault(row['video_sha256'],row['split'])==row['split']
train=[(m['frame_count']/10,m['condition']=='interaction') for m in ms if m['split']=='train'];values=sorted(set(x for x,y in train));candidates=[values[0]-1]+[(a+b)/2 for a,b in zip(values,values[1:])]+[values[-1]+1]
threshold=min(candidates,key=lambda t:(-sum((x>=t)==y for x,y in train),t))
baseline={}
for split in ('train','development','test'):
 subset=[m for m in ms if m['split']==split];correct=sum(((m['frame_count']/10)>=threshold)==(m['condition']=='interaction') for m in subset)
 baseline[split]={'correct':correct,'total':len(subset),'accuracy':correct/len(subset)}
old=Path('output/virtualhome-corpus/home-v1');preserved=json.loads((ticket/'various/v1-preservation.json').read_text())
assert file_hash(old/'inputs.jsonl')==preserved['inputs_sha256']
for line in (old/'inputs.jsonl').read_text().splitlines():
 row=json.loads(line);assert file_hash(old/row['video'])==preserved['source_videos'][row['episode_id']]
failed=[]
for p in (root/'episodes').glob('*/attempt-*/manifest.json'):
 m=json.loads(p.read_text())
 if m['status']=='failed':failed.append({'attempt':m['attempt'],'error':m['error']})
result={'source_episodes':48,'source_frames':sum(m['frame_count'] for m in ms),'source_duration_s':sum(m['frame_count'] for m in ms)/10,
 'windows':48,'window_duration_s':2.0,'window_total_duration_s':96.0,'split_counts':dict(Counter(m['split'] for m in ms)),
 'duration_only_baseline':{'fitted_on':'train only; maximize accuracy; lowest threshold breaks ties','threshold_seconds':threshold,'predict_interaction_if':'duration >= threshold','results':baseline},
 'equal_duration_majority_baseline_accuracy':0.5,'all_window_durations_identical':True,
 'producer_runner_sha256_counts':dict(Counter(m['producer']['diversity_runner.py'] for m in ms)),
 'config_hashes':sorted({m['config_hash'] for m in ms}),'installation_variants':len({json.dumps(m['installation'],sort_keys=True) for m in ms}),
 'failed_attempts':failed,'v1_videos_unchanged':24,'v1_inputs_unchanged':True,
 'model_input_keys':sorted(keys),'parent_window_split_violations':0,'window_cross_split_exact_duplicates':0,
 'release_files_sha256':{n:file_hash(root/n) for n in ('config.json','inputs.jsonl','labels.jsonl','audit.json','calibration-assessment-v1.json','windows-v1/inputs.jsonl','windows-v1/labels.jsonl','windows-v1/spec.json','windows-v1/visual-assessment-v1.json')},
 'combined_release_warning':'Do not combine v1 evaluation with v2 training as an unseen-apartment test: v1 is entirely scene 0.'}
save_json(root/'release-audit.json',result);save_json(ticket/'various/release-audit.json',result)
print(json.dumps(result,indent=2))
