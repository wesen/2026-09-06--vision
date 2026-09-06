"""Generate a separately versioned household corpus; never mutate the v1 release."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
import time

from . import core, diversity, runner
from .core import canonical_hash, file_hash, save_json, frame_files, parse_action_export
from .diversity import bind, camera_for, plan, program_for
from .runner import require, now, corpus_lock, export_annotations, check_video, probe_video


def producer():
    return {Path(m.__file__).name: file_hash(m.__file__) for m in (core, diversity, runner)} | {'diversity_runner.py': file_hash(__file__)}


def placement_room(initial, actor, requested):
    room_ids={n['id'] for n in initial['nodes'] if n.get('category')=='Rooms'}
    initial_rooms=sorted({e['to_id'] for e in initial['edges'] if e['from_id']==actor['id'] and e['relation_type']=='INSIDE' and e['to_id'] in room_ids})
    require(len(initial_rooms)==1, 'Actor initial room is ambiguous')
    actual=actor['obj_transform']['position']
    require(math.hypot(actual[0]-requested[0],actual[2]-requested[2])<0.25, 'Actor placement differs from requested coordinates')
    return initial_rooms[0]


def generate(comm, root, cfg, item, installation, code):
    episode = root / 'episodes' / item['episode_id']
    episode.mkdir(parents=True, exist_ok=True)
    number = 1
    while (episode / f'attempt-{number:04d}').exists():
        number += 1
    attempt = episode / f'attempt-{number:04d}'
    attempt.mkdir()
    manifest = dict(item, schema_version=2, status='started', started_at=now(),
                    attempt=str(attempt.relative_to(root)), config_hash=canonical_hash(cfg),
                    producer=code, installation=installation, visual_review='pending',
                    determinism_verified=False, recording={k: cfg[k] for k in ('fps', 'width', 'height')})
    def persist():
        save_json(attempt / 'manifest.json', manifest)
        save_json(episode / 'manifest.json', manifest)
    persist()
    started = time.monotonic()
    try:
        require(comm.reset(item['scene_index']), 'Reset failed')
        ok, graph = comm.environment_graph(); require(ok, 'Initial graph failed')
        save_json(attempt / 'graph-before.json', graph)
        target, room, support = bind(graph, item['scenario'])
        initialization = root / 'initializations' / (item['lineage_id'] + '.json')
        if initialization.exists():
            position = json.loads(initialization.read_text())['position']
            require(comm.add_character(cfg['character'], position=position), 'Character placement failed')
        else:
            require(comm.add_character(cfg['character'], position=item['scenario']['initial_position']), 'Character insertion failed')
        ok, initial = comm.environment_graph(); require(ok, 'Actor graph failed')
        actors = [n for n in initial['nodes'] if n['class_name'] == 'character']
        require(len(actors) == 1, 'Expected one actor')
        actor = actors[0]
        save_json(attempt / 'graph-initial.json', initial)
        initial_room=placement_room(initial,actor,item['scenario']['initial_position'])
        manifest['initial_room_id']=initial_room
        manifest['target_room_id']=room['id']
        if not initialization.exists():
            initialization.parent.mkdir(exist_ok=True)
            save_json(initialization, {'position': actor['obj_transform']['position'], 'transform': actor['obj_transform'], 'room_id': initial_room, 'target_room_id': room['id'], 'seed': item['seed'], 'pose_determinism_verified': False})
        save_json(attempt / 'graph-initial.json', initial)
        camera = camera_for(target, room, item['view'])
        ok, camera_id = comm.camera_count(); require(ok, 'Camera count failed')
        ok, result = comm.add_camera(position=camera['position'], rotation=camera['rotation']); require(ok, 'Camera insertion failed')
        program = program_for(item['scenario']['family'], target, support, item['condition'])
        manifest.update(program=program, camera=dict(camera, id=camera_id), initial_actor_transform=actor['obj_transform'],
                        bindings={'char0': actor['id'], 'target': target['id'], 'room': room['id'], 'support': support['id'] if support else None})
        (attempt / 'actions.txt').write_text('\n'.join(program) + '\n')
        persist()
        ok, result = comm.render_script(program, recording=True, randomize_execution=False, random_seed=item['seed'],
            output_folder=str(attempt.resolve()), file_name_prefix='episode', frame_rate=cfg['fps'],
            image_width=cfg['width'], image_height=cfg['height'], camera_mode=[str(camera_id)],
            save_pose_data=True, out_graph=True, per_frame=1)
        manifest['render_result'] = result; persist()
        require(ok, f'Execution failed: {result}')
        ok, after = comm.environment_graph(); require(ok, 'Final graph failed')
        save_json(attempt / 'graph-after.json', after)
        count, metadata, stream = export_annotations(attempt, cfg, program, target['id'])
        images, graphs, _ = frame_files(attempt/'episode/0')
        save_json(attempt/'raw-source-hashes.json', [{'frame':i, 'rgb_sha256':file_hash(images[i]), 'graph_sha256':file_hash(graphs[i])} for i in images])
        manifest.update(status='complete', completed_at=now(), elapsed_s=round(time.monotonic()-started, 3),
            frame_count=count, graph_count=count, camera_stream=stream,
            video=str((attempt/'video.mp4').relative_to(root)), video_sha256=file_hash(attempt/'video.mp4'),
            video_metadata=metadata, annotations=str((attempt/'annotations.json').relative_to(root)),
            source_hashes={name: file_hash(attempt/name) for name in ('graph-before.json','graph-initial.json','graph-after.json','actions.txt','annotations.json','world-frames.jsonl','world-state-runs.json','episode/0/ftaa_episode.txt','raw-source-hashes.json')})
        persist()
        return manifest
    except Exception as exc:
        manifest.update(status='failed', error=f'{type(exc).__name__}: {exc}', failed_at=now())
        persist()
        raise  # Stop: a request timeout does not cancel a running simulator action.


def validate(root, manifest, cfg, deep=False):
    require(manifest['status'] == 'complete', 'Incomplete episode')
    require(manifest['config_hash'] == canonical_hash(cfg), 'Config mismatch')
    attempt = root / manifest['attempt']
    require(file_hash(root / manifest['video']) == manifest['video_sha256'], 'Video hash mismatch')
    for name, expected in manifest['source_hashes'].items():
        require(file_hash(attempt/name) == expected, f'Source hash mismatch: {name}')
    images, graphs, camera = frame_files(attempt/'episode/0')
    require(len(images) == manifest['frame_count'] == manifest['graph_count'], 'Frame count mismatch')
    check_video(probe_video(root/manifest['video']), len(images), cfg)
    expected = parse_action_export((attempt/'episode/0/ftaa_episode.txt').read_text(encoding='utf-8-sig'), manifest['program'], len(images), cfg['fps'], cfg['boundary_guard_frames'])
    require(expected == json.loads((root/manifest['annotations']).read_text())['actions'], 'Action export mismatch')
    if deep:
        for row in json.loads((attempt/'raw-source-hashes.json').read_text()):
            i=row['frame']
            require(file_hash(images[i])==row['rgb_sha256'] and file_hash(graphs[i])==row['graph_sha256'], f'Raw frame hash mismatch: {i}')
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(root/manifest['video']),'-f','null','-'], check=True, timeout=120)
    return True


def export(root, cfg):
    complete=[]
    for item in plan(cfg):
        path=root/'episodes'/item['episode_id']/'manifest.json'
        if path.exists():
            m=json.loads(path.read_text())
            if m['status']=='complete':complete.append(m)
    with (root/'inputs.jsonl').open('w') as inputs, (root/'labels.jsonl').open('w') as labels:
        for m in complete:
            inputs.write(json.dumps({k:m[k] for k in ('episode_id','split','split_group','video','video_sha256')})+'\n')
            labels.write(json.dumps({k:m[k] for k in ('episode_id','scenario','condition','view','lineage_id','annotations')})+'\n')
    summary={'name':cfg['name'],'planned':len(plan(cfg)),'complete':len(complete),'frames':sum(m['frame_count'] for m in complete),
             'splits':dict(Counter(m['split'] for m in complete)), 'families':dict(Counter(m['scenario']['family'] for m in complete)),
             'conditions':dict(Counter(m['condition'] for m in complete)), 'visual_review':'pending','precise_visual_labels':False}
    save_json(root/'summary.json',summary)
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['plan','generate','validate'])
    p.add_argument('--config',type=Path,default=Path('configs/virtualhome-diversity-v2.json'))
    p.add_argument('--output',type=Path,default=Path('output/virtualhome-corpus/diversity-v2'))
    p.add_argument('--port',default='18082');p.add_argument('--limit',type=int)
    a=p.parse_args();cfg=json.loads(a.config.read_text());items=plan(cfg);root=a.output
    if a.command=='plan':print(json.dumps(items,indent=2));return
    with corpus_lock(root):
        config_path=root/'config.json'
        if config_path.exists():require(json.loads(config_path.read_text())==cfg,'Existing release config differs; use a new output directory')
        else:save_json(config_path,cfg)
        if a.command=='generate':
            from simulation.unity_simulator.comm_unity import UnityCommunication
            comm=UnityCommunication(port=a.port,timeout_wait=90)
            installation=json.loads(Path('output/virtualhome-install/installation.json').read_text())
            code=producer();done=0
            for item in items:
                path=root/'episodes'/item['episode_id']/'manifest.json'
                if path.exists():
                    old=json.loads(path.read_text())
                    if old['status']=='complete':validate(root,old,cfg);continue
                if a.limit is not None and done>=a.limit:break
                print('GENERATE',item['episode_id'],item['scenario']['family'],item['condition'],item['view'],flush=True)
                generate(comm,root,cfg,item,installation,code);done+=1
                print(json.dumps(export(root,cfg)),flush=True)
        else:
            for item in items:
                m=json.loads((root/'episodes'/item['episode_id']/'manifest.json').read_text())
                validate(root,m,cfg,deep=True)
            print(json.dumps(export(root,cfg)),flush=True)

if __name__=='__main__':main()
