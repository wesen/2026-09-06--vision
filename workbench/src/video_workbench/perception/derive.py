"""Replay stored detections into tracks, source crops, and bounded packets."""
from pathlib import Path
from dataclasses import fields
from collections import defaultdict
import json,time
from video_workbench.embedding import digest
from video_workbench.registry import file_hash
from video_workbench.media import decode_selected
from .contracts import FrameRef,expand,union,crop_record,validate_packet
from .tracking import TrackerSession,CONFIG
from .proposals import select,uniform,POLICY
from .pipeline import overlay
from .store import rows,write_json,publish_episode,verify_episode

CROP_POLICY={'margin':.25,'minimum_extent':12,'output_size':[320,240],'accepted_score':.25,'person_union':True}


def derive(run_path,destination):
    source=Path(run_path);dest=Path(destination)
    run=json.loads((source/'run.json').read_text())
    if run['status']!='complete':raise ValueError('complete detector run required')
    if dest.exists():raise ValueError('new derived run destination required')
    dest.mkdir(parents=True)
    spec={'source_run':run['run_id'],'source_manifest_sha256':file_hash(source/'run.json'),'tracker':CONFIG,'crops':CROP_POLICY,'proposals':POLICY,'code_sha256':{p.name:file_hash(p) for p in Path(__file__).parent.glob('*.py')}}
    derived={'run_id':digest(spec),'spec':spec,'status':'running','episodes':[]}
    write_json(dest/'run.json',derived)
    for entry in run['episodes']:
        eid=entry['episode_id'];folder=source/'episodes'/eid;target=dest/'episodes'/eid;target.mkdir(parents=True)
        if file_hash(folder/'manifest.json')!=entry['manifest_sha256']:raise ValueError('source manifest changed')
        manifest=verify_episode(folder);episode=manifest['episode'];frames=rows(folder/'frames.jsonl');detections=rows(folder/'detections.jsonl')
        if file_hash(episode['video'])!=episode['video_sha256']:raise ValueError('video changed')
        by_frame=defaultdict(list)
        for d in detections:by_frame[d['frame_id']].append(d)
        tracker=TrackerSession(derived['run_id'],eid);tracks=[];track_map={};crop_rows=[];elapsed=0.
        sample_indices={round((len(frames)-1)*f) for f in (0,.2,.4,.6,.8,1)}
        sample_indices.update(range(0,len(frames),10))
        images=decode_selected(episode['video'],sample_indices)
        for frame in frames:
            ref=FrameRef(**{f.name:frame[f.name] for f in fields(FrameRef)})
            start=time.perf_counter();tracked=tracker.update(ref,by_frame[ref.id]);seconds=time.perf_counter()-start;elapsed+=seconds
            for t in tracked:t['available_at_us']=frame['pts_us']+round((frame['detector_seconds']+seconds)*1e6)
            tracks.extend(tracked);track_map[ref.id]=tracked
            frame['available_at_us']=frame['pts_us']+round((frame['detector_seconds']+seconds)*1e6)
            if ref.frame_index not in images:continue
            im=images[ref.frame_index]
            accepted=[d for d in by_frame[ref.id] if d['score']>=CROP_POLICY['accepted_score']]
            people=[d for d in accepted if d['class_id']==0]
            for d in accepted:
                rect=expand(d['xyxy'],ref.width,ref.height,CROP_POLICY['margin'])
                variants=[('target',rect,[d['detection_id']])]
                if d['class_id']!=0 and people:
                    def distance(person):return sum(((d['xyxy'][i]+d['xyxy'][i+2])-(person['xyxy'][i]+person['xyxy'][i+2]))**2 for i in (0,1))
                    person=min(people,key=distance)
                    variants.append(('person_target',expand(union(d['xyxy'],person['xyxy']),ref.width,ref.height,.1),[d['detection_id'],person['detection_id']]))
                for kind,rect,ids in variants:
                    record=crop_record(ref,rect,derived['run_id'],kind,ids)
                    record.update(episode_id=eid,pts_us=ref.pts_us,frame_index=ref.frame_index,class_id=d['class_id'],class_name=d['class_name'],score=d['score'],status='usable' if record['source_min_extent']>=CROP_POLICY['minimum_extent'] else 'low_source_resolution')
                    path=target/(record['evidence_id']+'.png')
                    from PIL import Image
                    im.crop(tuple(map(int,rect))).resize((320,240),Image.Resampling.BICUBIC).save(path)
                    record.update(image=str(path),image_sha256=file_hash(path));crop_rows.append(record)
            overlay(im,by_frame[ref.id],tracked).save(target/f'tracks-{ref.frame_index:05d}.jpg',quality=90)
        packets=select(frames,track_map);uniform_packets=uniform(frames)
        known={f['frame_id']:f for f in frames}
        for packet in packets+uniform_packets:validate_packet(packet,known,packet['available_at_us'])
        for name,content in [('tracks.jsonl',tracks),('crops.jsonl',crop_rows),('proposals.jsonl',packets),('uniform.jsonl',uniform_packets)]:
            (target/name).write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in content))
        publish_episode(target,{'episode':episode,'run_id':derived['run_id'],'source_manifest_sha256':entry['manifest_sha256'],'resets':tracker.resets,'track_seconds':elapsed,'tail_policy':'last bin remains unclosed without a later source clock tick','counts':{'tracks':len(tracks),'crops':len(crop_rows),'proposals':len(packets),'selected':sum(p['selected'] for p in packets)}})
        derived['episodes'].append({'episode_id':eid,'manifest_sha256':file_hash(target/'manifest.json')});write_json(dest/'run.json',derived)
        print(f'derived {eid}: {len(tracks)} track rows, {len(crop_rows)} crops',flush=True)
    derived['status']='complete';write_json(dest/'run.json',derived)
    return derived
