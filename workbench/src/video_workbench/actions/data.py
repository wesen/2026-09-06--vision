"""Prepare source windows and separate evaluator proposals; never infer RGB labels."""
from pathlib import Path
import json,re
from video_workbench.embedding import digest
from video_workbench.registry import Registry,file_hash
from video_workbench.media import selected_indices
from video_workbench.perception.store import write_json

ACTIONS=('open','close','pickup','putdown','sit','stand','switch_on','switch_off','none')
VERBS={'open':'open','close':'close','grab':'pickup','putobjback':'putdown','sit':'sit','stand':'stand','standup':'stand','switchon':'switch_on','switchoff':'switch_off'}
QUERIES={
 'open':'A person opening a door.', 'close':'A person closing a door.',
 'pickup':'A person picking up an object.', 'putdown':'A person putting an object down.',
 'sit':'A person sitting down.', 'stand':'A person standing up from a seat.',
 'switch_on':'A person switching an appliance on.', 'switch_off':'A person switching an appliance off.',
 'none':'A person approaching or looking at an object without manipulating it.',
}
OPPOSITES={'open':'close','close':'open','pickup':'putdown','putdown':'pickup','sit':'stand','stand':'sit','switch_on':'switch_off','switch_off':'switch_on'}


def window(center_us,duration_us,width_us=2_000_000):
    if duration_us<width_us:return None
    start=max(0,min(int(center_us)-width_us//2,duration_us-width_us))
    return start,start+width_us


def action_center(action,start_us,end_us):
    # AIST Sit exports include a long positioning/wait period. Source review
    # shows the actual descent at the end; preserve a seated final sample.
    return end_us-750_000 if action=='sit' else (start_us+end_us)//2


def validate_samples(samples):
    ids=set();lineages={};hashes={}
    for s in samples:
        if s['sample_id'] in ids:raise ValueError('duplicate sample')
        ids.add(s['sample_id'])
        if s['split'] not in ('train','development','test'):raise ValueError('invalid split')
        if lineages.setdefault(s['lineage_id'],s['split'])!=s['split']:raise ValueError('lineage crosses splits')
        if hashes.setdefault(s['video_sha256'],s['split'])!=s['split']:raise ValueError('source crosses splits')
        pts=s['selected_pts_us'];indices=s['frame_indices']
        if not pts or len(pts)!=len(indices) or any(type(t)!=int for t in pts):raise ValueError('invalid PTS')
        if any(t<s['start_us'] or t>=s['end_us'] for t in pts) or any(b<=a for a,b in zip(pts,pts[1:])):raise ValueError('PTS outside source window')
        if s['available_us']<max(pts):raise ValueError('future evidence')
    return samples


def prepare(release, destination):
    root=Path(release).resolve();dest=Path(destination)
    if dest.exists():raise ValueError('use a new action protocol directory')
    summary=json.loads((root/'summary.json').read_text())
    if summary['complete']!=48:raise ValueError('complete paired release required')
    dest.mkdir(parents=True)
    registry=Registry(dest/'registry.sqlite')
    try:
        registry.ingest(root/'inputs.jsonl');episodes=registry.episodes()
    finally:registry.close()
    samples=[];reviews=[];excluded=[]
    for ep in episodes:
        m=json.loads((root/'episodes'/ep['episode_id']/'manifest.json').read_text())
        annotations=json.loads((root/m['annotations']).read_text())
        candidates=[]
        if m['condition']=='approach_only':candidates=[('none',ep['media']['duration_us']-1_000_000,None)]
        else:
            for i,line in enumerate(m['program']):
                verb=re.search(r'\[([^]]+)\]',line).group(1).lower()
                if verb not in VERBS:continue
                rows=[r for r in annotations['actions'] if r['program_index']==i and r['action'] not in ('WALK','TURNTO','WATCH')]
                if not rows:raise ValueError(f'missing inverse action export: {ep["episode_id"]} {verb}')
                lo=min(r['raw_start'] for r in rows)*1_000_000//annotations['fps'];hi=max(r['raw_end'] for r in rows)*1_000_000//annotations['fps']
                candidates.append((VERBS[verb],action_center(VERBS[verb],lo,hi),[lo,hi]))
            if len(candidates)!=2:raise ValueError('paired interaction must expose two directions')
        for action,center,weak in candidates:
            interval=window(center,ep['media']['duration_us'])
            if interval is None:excluded.append({'episode_id':ep['episode_id'],'requested_action':action,'reason':'video_shorter_than_fixed_window'});continue
            start,end=interval;indices=selected_indices(ep['media']['pts_us'],start,end,2)
            s={k:ep[k] for k in ('episode_id','split','split_group','video','video_sha256')}
            s.update(lineage_id=m['lineage_id'],start_us=start,end_us=end,available_us=end,
                     selected_pts_us=[ep['media']['pts_us'][i] for i in indices],frame_indices=indices,
                     selected_raw_pts=[ep['media']['raw_pts'][i] for i in indices],time_base=ep['media']['time_base'],origin_us=ep['media']['origin_us'])
            s['sample_id']=digest(s)[:24]
            samples.append(s)
            reviews.append({'sample_id':s['sample_id'],'requested_action':action,'weak_interval_us':weak,
                            'action':None,'visibility':'pending','rationale':'','reviewer':None,
                            'family':m['scenario']['family'],'target_class':m['scenario']['target_class'],
                            'view':m['view'],'condition':m['condition'],'source_sha256':ep['video_sha256']})
    validate_samples(samples)
    write_json(dest/'samples.json',samples);write_json(dest/'review-proposals.json',reviews)
    write_json(dest/'protocol.json',{'version':'actions-v2','seconds':2,'fps':2,'actions':ACTIONS,'queries':QUERIES,
        'window_policy':'Sit center = exported end minus 750 ms; other actions use exported midpoint; controls use trajectory end minus 1 s. Source-review correction before model inference.',
        'representations':['native_fp32','pooled_fp32','pooled_4bit'],'interventions':['original','reverse','repeat_first'],
        'samples_sha256':file_hash(dest/'samples.json'),'release_config_sha256':file_hash(root/'config.json'),
        'excluded':excluded,'labels':'Source RGB review required before primary scoring; weak requested actions are not truth.'})
    return {'samples':len(samples),'excluded':len(excluded),'episodes':len(episodes)}
