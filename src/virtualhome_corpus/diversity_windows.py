"""Equal-duration, lineage-preserving windows for coarse target-interaction experiments."""
import argparse
import json
from pathlib import Path
import subprocess
from .core import canonical_hash, file_hash, save_json
from .runner import check_video, probe_video, corpus_lock
from .diversity import plan
from .diversity_runner import validate


def select_window(manifest, annotations, count=20):
    total=manifest['frame_count']
    if total<count:raise ValueError('Source too short; padding is not permitted')
    if manifest['condition']=='approach_only':
        return total-count, 'target_interaction_absent'
    family=manifest['scenario']['family']
    wanted={'door':{'OPEN'},'pickup':{'GRAB'},'posture':{'SIT'},'switch':{'SWITCHON','SWITCHOFF'}}[family]
    event=next(a for a in annotations['actions'] if a['action'] in wanted)
    if family=='posture':start=event['raw_end']-count
    else:start=(event['raw_start']+event['raw_end'])//2-count//2
    return max(0,min(total-count,start)),event['action']


def build(root, count=20):
    cfg=json.loads((root/'config.json').read_text())
    sources=[json.loads(line) for line in (root/'inputs.jsonl').read_text().splitlines()]
    if {s['episode_id'] for s in sources}!={m['episode_id'] for m in plan(cfg)}:raise ValueError('Complete parent release required')
    out=root/'windows-v1';out.mkdir(exist_ok=True)
    spec={'version':1,'frames':count,'fps':cfg['fps'],'source_inputs_sha256':file_hash(root/'inputs.jsonl'),
          'selection':'first target action midpoint; SIT terminal interval; controls terminal interval; clamp to source; no padding',
          'quality':'weak_program_conditioned_windows; not precise action boundaries'}
    spec_path=out/'spec.json'
    if spec_path.exists() and json.loads(spec_path.read_text())!=spec:raise ValueError('Window release spec changed')
    save_json(spec_path,spec)
    inputs=[];labels=[]
    for source in sources:
        m=json.loads((root/'episodes'/source['episode_id']/'manifest.json').read_text())
        validate(root,m,cfg)
        a=json.loads((root/m['annotations']).read_text());start,label=select_window(m,a,count)
        hashes=json.loads((root/m['attempt']/'raw-source-hashes.json').read_text())
        for row in hashes[start:start+count]:
            raw=root/m['attempt']/'episode/0'/f"Action_{row['frame']:04d}_{m['camera_stream']}_normal.png"
            if file_hash(raw)!=row['rgb_sha256']:raise ValueError('Selected raw frame hash mismatch')
        identity='win-'+canonical_hash([spec,m['episode_id'],start,count])[:16]
        video=out/(identity+'.mp4');meta=out/(identity+'.json')
        record={'episode_id':identity,'parent_episode_id':m['episode_id'],'parent_video_sha256':m['video_sha256'],
                'source_raw_hashes_sha256':m['source_hashes']['raw-source-hashes.json'],
                'split':m['split'],'split_group':m['split_group'],'lineage_id':m['lineage_id'],
                'start_frame':start,'end_frame_exclusive':start+count,'frames':count,'fps':cfg['fps'],
                'family':m['scenario']['family'],'condition':m['condition'],'view':m['view'],'target_action':label,
                'quality':spec['quality'],'precise_boundary_supervision_allowed':False,'dense_visual_state_supervision_allowed':False}
        if video.exists():
            old=json.loads(meta.read_text())
            if any(old.get(k)!=v for k,v in record.items()) or file_hash(video)!=old['video_sha256']:raise ValueError('Existing window provenance differs')
        else:
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-framerate',str(cfg['fps']),
                '-start_number',str(start),'-i',str(root/m['attempt']/'episode/0'/f"Action_%04d_{m['camera_stream']}_normal.png"),
                '-frames:v',str(count),'-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True,timeout=90)
        check_video(probe_video(video),count,cfg)
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True,timeout=30)
        record['video_sha256']=file_hash(video);save_json(meta,record)
        inputs.append({'episode_id':identity,'split':m['split'],'split_group':m['split_group'],'video':video.name,'video_sha256':record['video_sha256']})
        labels.append(record)
    for name,rows in [('inputs.jsonl',inputs),('labels.jsonl',labels)]:
        (out/name).write_text(''.join(json.dumps(r)+'\n' for r in rows))
    summary={'windows':len(inputs),'duration_s':count/cfg['fps'],'frames_each':count,'source_lineage_preserved':True,'padding':False,'quality':spec['quality']}
    save_json(out/'summary.json',summary);print(json.dumps(summary))


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('output/virtualhome-corpus/diversity-v2'));p.add_argument('--frames',type=int,default=20);a=p.parse_args()
    if a.frames<1:raise ValueError('Positive window length required')
    with corpus_lock(a.output):build(a.output,a.frames)

if __name__=='__main__':main()
