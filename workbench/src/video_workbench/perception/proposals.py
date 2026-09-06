"""Causal proposals: fixed bins and prefix-only cues, with periodic fallback."""
from math import hypot
from video_workbench.embedding import digest

POLICY={'bin_us':1_000_000,'periodic_bins':3,'proximity':1.5,'movement_per_second':.5,'change':.035,'max_extra_per_10s':3,'max_images':2,'max_pixels':2*640*480}


def cues(frame,observed,previous):
    people=[t for t in observed if t['class_id']==0]
    targets=[t for t in observed if t['class_id']!=0]
    center=lambda t:((t['xyxy'][0]+t['xyxy'][2])/2,(t['xyxy'][1]+t['xyxy'][3])/2)
    distance=float('inf');movement=0.
    for target in targets:
        x,y=center(target);extent=max(1.,hypot(target['xyxy'][2]-target['xyxy'][0],target['xyxy'][3]-target['xyxy'][1]))
        for person in people:
            px,py=center(person);distance=min(distance,hypot(x-px,y-py)/extent)
        old=previous.get(target['track_id'])
        if old and target['pts_us']>old['pts_us']:
            ox,oy=center(old);dt=(target['pts_us']-old['pts_us'])/1e6
            movement=max(movement,hypot(x-ox,y-oy)/extent/dt)
    return {'proximity':None if distance==float('inf') else distance,'movement_per_second':movement,'change':frame['full_frame_change']}


def select(frames,tracks_by_frame,policy=POLICY):
    """Outputs only completed one-second bins. No future frames rank past bins."""
    previous={};bins={};output=[];extras={}
    for frame in frames:
        observed=[t for t in tracks_by_frame.get(frame['frame_id'],[]) if t['status']=='observed']
        cue=cues(frame,observed,previous)
        previous.update({t['track_id']:t for t in observed})
        b=frame['pts_us']//policy['bin_us']
        record=bins.setdefault(b,{'frames':[],'reasons':set(),'max_movement':0.,'max_change':0.,'min_proximity':None})
        record['frames'].append(frame)
        for reason,active in [('proximity',cue['proximity'] is not None and cue['proximity']<=policy['proximity']),('movement',cue['movement_per_second']>=policy['movement_per_second']),('appearance_change',cue['change']>=policy['change'])]:
            if active:record['reasons'].add(reason)
        record['max_movement']=max(record['max_movement'],cue['movement_per_second']);record['max_change']=max(record['max_change'],cue['change'])
        if cue['proximity'] is not None:record['min_proximity']=min(record['min_proximity'] or float('inf'),cue['proximity'])
        for old_bin in sorted(k for k in bins if k<b):
            r=bins.pop(old_bin);periodic=old_bin%policy['periodic_bins']==0;window=old_bin//10
            candidate=bool(r['reasons']);accept=periodic or (candidate and extras.get(window,0)<policy['max_extra_per_10s'])
            if accept and not periodic:extras[window]=extras.get(window,0)+1
            reason='periodic_full_scene' if periodic else 'cue_budget' if accept else 'budget_exhausted' if candidate else 'no_cue'
            chosen=[r['frames'][0],r['frames'][-1]]
            chosen=list({f['frame_id']:f for f in chosen}.values())
            payload={'episode_id':frame['episode_id'],'video_sha256':frame['video_sha256'],'interval_us':[old_bin*policy['bin_us'],(old_bin+1)*policy['bin_us']],
                'available_at_us':max(frame['pts_us'],max(f.get('available_at_us',f['pts_us']) for f in r['frames'])),'evidence_ids':[f['frame_id'] for f in chosen],'selected':accept,'decision_reason':reason,'cues':sorted(r['reasons']),
                'max_movement':r['max_movement'],'max_change':r['max_change'],'min_proximity':r['min_proximity'],
                'budget':{'max_images':policy['max_images'],'max_pixels':policy['max_pixels']},'mode':'causal-completed-bin','policy_id':digest(policy)}
            output.append(dict(payload,packet_id=digest(payload)[:24]))
    # Final incomplete/unclosed bin is explicit, not retrospectively made causal.
    return output


def uniform(frames,policy=POLICY):
    rows=select(frames,{},dict(policy,periodic_bins=1))
    return rows
