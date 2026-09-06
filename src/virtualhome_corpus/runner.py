"""Own a corpus directory, invoke VirtualHome, and validate every artifact."""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import time

from .core import (canonical_hash, file_hash, save_json, validate_config, plan_episodes,
                   select_objects, make_program, parse_action_export, frame_files,
                   camera_rotation, endpoint_rule)


def now():
    return datetime.now(timezone.utc).isoformat()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def probe_video(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,nb_frames,r_frame_rate',
        '-show_entries', 'format=duration', '-of', 'json', str(path),
    ], text=True, timeout=30))


def encode_video(directory, camera, path, cfg):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error',
                    '-framerate', str(cfg['fps']), '-start_number', '0',
                    '-i', str(directory / f'Action_%04d_{camera}_normal.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    str(path)], check=True, timeout=180)
    return probe_video(path)


def check_video(metadata, count, cfg):
    stream = metadata['streams'][0]
    require(int(stream['nb_frames']) == count, 'Encoded frame count differs from PNGs')
    require((stream['width'], stream['height']) == (cfg['width'], cfg['height']), 'Encoded dimensions differ')
    require(Fraction(stream['r_frame_rate']) == cfg['fps'], 'Encoded FPS differs')
    require(abs(float(metadata['format']['duration']) - count / cfg['fps']) < 0.02, 'Encoded duration differs')


def export_annotations(attempt, cfg, program, target_id):
    from PIL import Image, ImageDraw, ImageStat
    directory = attempt / 'episode' / '0'
    images, graphs, camera = frame_files(directory)
    count = len(images)
    raw = (directory / 'ftaa_episode.txt').read_text(encoding='utf-8-sig')
    actions = parse_action_export(raw, program, count, cfg['fps'], cfg['boundary_guard_frames'])
    annotations = {'schema_version': 1, 'frame_count': count, 'fps': cfg['fps'],
                   'action_endpoint_convention': 'unresolved', 'graph_image_capture_phase': 'unverified',
                   'precise_boundary_supervision_allowed': False,
                   'dense_visual_state_supervision_allowed': False,
                   'action_quality': 'weak_program_supervision', 'actions': actions}
    save_json(attempt / 'annotations.json', annotations)
    state_runs = []
    with (attempt / 'world-frames.jsonl').open('w') as output:
        for index in range(count):
            with Image.open(images[index]) as image:
                require(image.size == (cfg['width'], cfg['height']), 'PNG dimensions differ')
                image.load()
                if index == 0:
                    require(max(ImageStat.Stat(image.convert('RGB')).stddev) > 1, 'Blank initial RGB image')
            graph = json.loads(graphs[index].read_text(encoding='utf-8-sig'))
            target = next(n for n in graph['nodes'] if n['id'] == target_id)
            states = sorted(target.get('states', []))
            frame = {'frame_index': index, 'presentation_us': index * 1_000_000 // cfg['fps'],
                     'target_states': states, 'source': str(graphs[index].relative_to(attempt)),
                     'quality': 'simulator_export_capture_phase_unverified'}
            output.write(json.dumps(frame) + '\n')
            if not state_runs or state_runs[-1]['states'] != states:
                state_runs.append({'start_frame': index, 'end_frame_exclusive': index + 1, 'states': states})
            else:
                state_runs[-1]['end_frame_exclusive'] = index + 1
    save_json(attempt / 'world-state-runs.json', state_runs)
    # Inspection sheets carry labels; the model video remains unchanged.
    picks = {0, count - 1}
    for row in actions:
        if row['interior']:
            picks.add((row['interior']['start_frame'] + row['interior']['end_frame_exclusive']) // 2)
    picks = sorted(picks)
    sheet = Image.new('RGB', (960, ((len(picks) + 2) // 3) * 264), 'white')
    draw = ImageDraw.Draw(sheet)
    for j, index in enumerate(picks):
        with Image.open(images[index]) as image:
            image = image.convert('RGB'); image.thumbnail((320, 240))
            x, y = (j % 3) * 320, (j // 3) * 264
            sheet.paste(image, (x, y + 24))
            labels = [a['action'] for a in actions if a['interior'] and
                      a['interior']['start_frame'] <= index < a['interior']['end_frame_exclusive']]
            draw.text((x + 5, y + 5), f'{index} / {index / cfg["fps"]:.1f}s / {",".join(labels) or "boundary"}', fill='black')
    sheet.save(attempt / 'contact-sheet.jpg', quality=90)
    metadata = encode_video(directory, camera, attempt / 'video.mp4', cfg)
    check_video(metadata, count, cfg)
    return count, metadata, camera


@contextmanager
def corpus_lock(root):
    root.mkdir(parents=True, exist_ok=True)
    with (root / '.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another generator owns this corpus directory') from None
        yield


def producer():
    from . import core
    return {'runner_sha256': file_hash(__file__), 'core_sha256': file_hash(core.__file__)}


def generate_episode(comm, root, cfg, item, installation, producer_spec):
    episode = root / 'episodes' / item['episode_id']
    episode.mkdir(parents=True, exist_ok=True)
    attempt_number = 1
    while (episode / f'attempt-{attempt_number:04d}').exists():
        attempt_number += 1
    attempt = episode / f'attempt-{attempt_number:04d}'
    attempt.mkdir()
    manifest = {'schema_version': 1, **item, 'split': item['group']['split'],
                'split_group': item['group']['id'], 'status': 'started', 'started_at': now(),
                'attempt': str(attempt.relative_to(root)), 'config_hash': canonical_hash(cfg),
                'producer': producer_spec, 'installation': installation,
                'determinism_verified': False, 'visual_review': 'pending',
                'recording': {'fps': cfg['fps'], 'width': cfg['width'], 'height': cfg['height']}}
    start = time.monotonic()
    def persist():
        save_json(attempt / 'manifest.json', manifest)
        save_json(episode / 'manifest.json', manifest)
    persist()
    try:
        require(comm.reset(cfg['scene_index']), 'Scene reset failed')
        ok, graph = comm.environment_graph(); require(ok, 'Initial graph fetch failed')
        save_json(attempt / 'graph-before.json', graph)
        target, neighbor, destination = select_objects(graph, item['family'], cfg['initial_room'], cfg['destination_room'])
        group_path = root / 'groups' / (item['group']['id'] + '.json')
        group_path.parent.mkdir(exist_ok=True)
        if group_path.exists():
            initialization = json.loads(group_path.read_text())
            require(comm.add_character(cfg['character'], position=initialization['position']), 'Fixed character insertion failed')
        else:
            require(comm.add_character(cfg['character'], initial_room=cfg['initial_room']), 'Character insertion failed')
        ok, initial = comm.environment_graph(); require(ok, 'Post-insertion graph fetch failed')
        actors = [n for n in initial['nodes'] if n['class_name'] == 'character']
        require(len(actors) == 1, 'Expected exactly one actor')
        actor = actors[0]
        if not group_path.exists():
            save_json(group_path, {'position': actor['obj_transform']['position'],
                                  'initial_transform': actor['obj_transform'],
                                  'split': item['group']['split'], 'seed': item['group']['seed'],
                                  'pose_determinism_verified': False})
        save_json(attempt / 'graph-initial.json', initial)
        position = list(cfg['camera']['position']); position[0] += item['group']['camera_dx']
        rotation = camera_rotation(position, cfg['camera']['look_at'])
        ok, camera_id = comm.camera_count(); require(ok, 'Camera count failed')
        ok, message = comm.add_camera(position=position, rotation=rotation); require(ok, 'Fixed camera insertion failed')
        program = make_program(target, neighbor, destination, item['variant'])
        manifest.update({'program': program,
                         'bindings': {'char0': actor['id'], 'target': target['id'], 'neighbor': neighbor['id'], 'destination': destination['id']},
                         'initial_actor_transform': actor['obj_transform'],
                         'camera': {'id': camera_id, 'position': position, 'rotation': rotation}})
        (attempt / 'actions.txt').write_text('\n'.join(program) + '\n')
        persist()
        ok, result = comm.render_script(program, recording=True, randomize_execution=False,
            random_seed=item['group']['seed'], output_folder=str(attempt.resolve()),
            file_name_prefix='episode', frame_rate=cfg['fps'], image_width=cfg['width'],
            image_height=cfg['height'], camera_mode=[str(camera_id)],
            save_pose_data=True, out_graph=True, per_frame=1)
        manifest['render_result'] = result; persist()
        require(ok, f'Action execution failed: {result}')
        ok, after = comm.environment_graph(); require(ok, 'Final graph fetch failed')
        save_json(attempt / 'graph-after.json', after)
        manifest['rule_truth'] = endpoint_rule(after, actor['id'], target['id'], destination['id'],
                                               item['variant'] == 'closed_before_leaving')
        count, metadata, camera_stream = export_annotations(attempt, cfg, program, target['id'])
        manifest.update({'status': 'complete', 'completed_at': now(), 'elapsed_s': round(time.monotonic()-start, 3),
                         'frame_count': count, 'graph_count': count, 'camera_stream': camera_stream,
                         'video': str((attempt / 'video.mp4').relative_to(root)),
                         'video_sha256': file_hash(attempt / 'video.mp4'), 'video_metadata': metadata,
                         'annotations': str((attempt / 'annotations.json').relative_to(root))})
        persist()
        return manifest
    except Exception as exc:
        manifest.update({'status': 'failed', 'error': f'{type(exc).__name__}: {exc}', 'failed_at': now()})
        persist()
        raise


def validate_episode(root, manifest, cfg, deep=False):
    require(manifest['status'] == 'complete', 'Episode is not complete')
    require(manifest['config_hash'] == canonical_hash(cfg), 'Episode config mismatch')
    video = root / manifest['video']
    require(file_hash(video) == manifest['video_sha256'], 'Video checksum mismatch')
    attempt = root / manifest['attempt']
    images, graphs, camera = frame_files(attempt / 'episode' / '0')
    require(len(images) == manifest['frame_count'] == manifest['graph_count'], 'Frame counts differ')
    check_video(probe_video(video), len(images), cfg)
    endpoint_rule(json.loads((attempt / 'graph-after.json').read_text()),
                  manifest['bindings']['char0'], manifest['bindings']['target'],
                  manifest['bindings']['destination'], manifest['variant'] == 'closed_before_leaving')
    expected = parse_action_export((attempt / 'episode/0/ftaa_episode.txt').read_text(encoding='utf-8-sig'),
                                   manifest['program'], len(images), cfg['fps'], cfg['boundary_guard_frames'])
    require(json.loads((root / manifest['annotations']).read_text())['actions'] == expected,
            'Annotation export differs from raw action rows')
    if deep:
        from PIL import Image
        for i in images:
            with Image.open(images[i]) as image:
                image.load(); require(image.size == (cfg['width'], cfg['height']), 'Image dimensions differ')
            g = json.loads(graphs[i].read_text(encoding='utf-8-sig'))
            require('nodes' in g and 'edges' in g, 'Malformed graph')
    return True


def export_index(root, cfg):
    complete, failures = [], []
    for item in plan_episodes(cfg):
        path = root / 'episodes' / item['episode_id'] / 'manifest.json'
        if path.exists():
            m = json.loads(path.read_text())
            (complete if m['status'] == 'complete' else failures).append(m)
    seen, group_splits = {}, {}
    for m in complete:
        previous = group_splits.setdefault(m['split_group'], m['split'])
        require(previous == m['split'], 'Split-group leakage')
        previous_split = seen.setdefault(m['video_sha256'], m['split'])
        require(previous_split == m['split'], 'Identical video crosses splits')
    with (root / 'inputs.jsonl').open('w') as inputs, (root / 'labels.jsonl').open('w') as labels:
        for m in complete:
            inputs.write(json.dumps({k: m[k] for k in ['episode_id', 'split', 'split_group', 'video', 'video_sha256']}) + '\n')
            labels.write(json.dumps({k: m[k] for k in ['episode_id', 'family', 'variant', 'annotations', 'rule_truth']}) + '\n')
    queries = []
    for family in cfg['families']:
        for action, verb in [('OPEN', 'opening'), ('CLOSE', 'closing')]:
            relevant = []
            for m in complete:
                if m['family'] != family:
                    continue
                annotations = json.loads((root / m['annotations']).read_text())
                for row in annotations['actions']:
                    if row['action'] == action and row['interior']:
                        relevant.append({'episode_id': m['episode_id'], 'split': m['split'], **row['interior']})
            queries.append({'query': f'A person {verb} the {family} door', 'relevant_interiors': relevant,
                            'quality': 'weak_program_supervision'})
    save_json(root / 'retrieval-queries.json', queries)
    summary = {'name': cfg['name'], 'planned': len(plan_episodes(cfg)), 'complete': len(complete),
               'failed': len(failures), 'frames': sum(m['frame_count'] for m in complete),
               'seconds': sum(m['frame_count']/cfg['fps'] for m in complete),
               'by_split': dict(Counter(m['split'] for m in complete)),
               'by_family': dict(Counter(m['family'] for m in complete)),
               'by_variant': dict(Counter(m['variant'] for m in complete)),
               'failure_ids': [m['episode_id'] for m in failures],
               'within_scene_split_only': True, 'precise_boundary_supervision_allowed': False,
               'dense_visual_state_supervision_allowed': False}
    save_json(root / 'summary.json', summary)
    return summary


def generate(args, cfg):
    from simulation.unity_simulator import UnityCommunication
    root = args.output.resolve()
    installation = json.loads((args.installation / 'installation.json').read_text())
    with corpus_lock(root):
        header = {'config': cfg, 'config_hash': canonical_hash(cfg), 'installation': installation,
                  'producer': producer(), 'schema_version': 1}
        header_path = root / 'corpus.json'
        if header_path.exists():
            require(json.loads(header_path.read_text()) == header, 'Corpus provenance changed; choose a fresh output directory')
        else:
            save_json(header_path, header); save_json(root / 'plan.json', plan_episodes(cfg))
        comm = UnityCommunication(port=str(args.port), timeout_wait=180)
        # Bounded request, unlike upstream check_connection's retry path.
        require(comm.post_command({'id': 'corpus-ready', 'action': 'idle'})['success'], 'Simulator not ready')
        attempted = 0
        for item in plan_episodes(cfg):
            path = root / 'episodes' / item['episode_id'] / 'manifest.json'
            if path.exists():
                m = json.loads(path.read_text())
                if m['status'] == 'complete':
                    validate_episode(root, m, cfg)
                    continue
            if args.limit and attempted >= args.limit:
                break
            attempted += 1
            print(json.dumps({'event': 'start', 'episode': item['episode_id'], 'family': item['family'],
                              'variant': item['variant'], 'split': item['group']['split']}), flush=True)
            try:
                m = generate_episode(comm, root, cfg, item, installation, header['producer'])
            except Exception:
                export_index(root, cfg)
                raise
            export_index(root, cfg)
            print(json.dumps({'event': 'complete', 'episode': item['episode_id'], 'frames': m['frame_count'],
                              'elapsed_s': m['elapsed_s']}), flush=True)
        print(json.dumps(export_index(root, cfg), indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'generate', 'validate'])
    parser.add_argument('--config', type=Path, default=Path('configs/virtualhome-household-v1.json'))
    parser.add_argument('--output', type=Path, default=Path('output/virtualhome-corpus/home-v1'))
    parser.add_argument('--installation', type=Path, default=Path('output/virtualhome-install'))
    parser.add_argument('--port', type=int)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--deep', action='store_true')
    args = parser.parse_args()
    cfg = validate_config(json.loads(args.config.read_text()))
    if args.command == 'plan':
        print(json.dumps(plan_episodes(cfg), indent=2)); return
    if args.command == 'generate':
        if args.port is None or not 1 <= args.port <= 65535:
            parser.error('generate requires --port for a simulator you own')
        if args.limit < 0:
            parser.error('--limit must be nonnegative')
        generate(args, cfg); return
    root = args.output.resolve()
    with corpus_lock(root):
        for path in sorted((root / 'episodes').glob('*/manifest.json')):
            m = json.loads(path.read_text())
            if m['status'] == 'complete':
                validate_episode(root, m, cfg, deep=args.deep)
        summary = export_index(root, cfg)
        require(summary['complete'] == summary['planned'] and summary['failed'] == 0, 'Corpus is incomplete')
        print(json.dumps(summary, indent=2))
