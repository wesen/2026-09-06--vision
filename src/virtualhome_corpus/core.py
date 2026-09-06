"""Pure corpus contracts; no simulator import or model dependencies."""
from __future__ import annotations
import hashlib
import json
import math
import re
from pathlib import Path

VARIANTS = {'closed_before_leaving', 'closure_omitted', 'reopened_before_leaving'}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)


def validate_config(cfg):
    if cfg.get('schema_version') != 1:
        raise ValueError('Unsupported config schema')
    if not cfg['families'] or set(cfg['families']) - {'fridge', 'microwave'}:
        raise ValueError('Unsupported family')
    if not cfg['variants'] or set(cfg['variants']) - VARIANTS:
        raise ValueError('Unsupported variant')
    for key in ('families', 'variants'):
        if len(cfg[key]) != len(set(cfg[key])):
            raise ValueError(f'Duplicate {key}')
    for key in ('fps', 'width', 'height'):
        if type(cfg[key]) is not int or cfg[key] <= 0:
            raise ValueError(f'{key} must be a positive integer')
    if cfg['width'] % 2 or cfg['height'] % 2:
        raise ValueError('yuv420p dimensions must be even')
    if type(cfg['boundary_guard_frames']) is not int or cfg['boundary_guard_frames'] < 1:
        raise ValueError('A positive boundary guard is required')
    if not cfg['groups'] or len({g['id'] for g in cfg['groups']}) != len(cfg['groups']):
        raise ValueError('Duplicate or missing split groups')
    for g in cfg['groups']:
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', g['id']):
            raise ValueError('Unsafe group ID')
        if g['split'] not in {'train', 'development', 'test'}:
            raise ValueError('Invalid split')
    return cfg


def plan_episodes(cfg):
    validate_config(cfg)
    plan = []
    for group in cfg['groups']:
        for family in cfg['families']:
            for variant in cfg['variants']:
                identity = [cfg['name'], group['id'], family, variant]
                plan.append({'episode_id': 'ep-' + canonical_hash(identity)[:16],
                             'group': group, 'family': family, 'variant': variant})
    return plan


def select_objects(graph, family, initial_room, destination_room):
    nodes = graph['nodes']
    room = next(n for n in nodes if n.get('category') == 'Rooms' and n['class_name'] == initial_room)
    inside = {e['from_id'] for e in graph['edges']
              if e['relation_type'] == 'INSIDE' and e['to_id'] == room['id']}
    def appliance(name):
        matches = [n for n in nodes if n['class_name'] == name and n['id'] in inside
                   and 'CAN_OPEN' in n.get('properties', [])]
        if not matches:
            raise ValueError(f'No openable {name} in {initial_room}')
        return min(matches, key=lambda n: n['id'])
    target = appliance(family)
    neighbor = appliance('microwave' if family == 'fridge' else 'fridge')
    destination = next(n for n in nodes if n.get('category') == 'Rooms'
                       and n['class_name'] == destination_room)
    if 'CLOSED' not in target.get('states', []):
        raise ValueError('Target must start CLOSED')
    return target, neighbor, destination


def make_program(target, neighbor, destination, variant):
    if variant not in VARIANTS:
        raise ValueError('Unknown variant')
    def action(verb, node):
        return f"<char0> [{verb}] <{node['class_name']}> ({node['id']})"
    # The detour creates observable dwell while the target remains open.
    lines = [action('Walk', target), action('Open', target), action('Walk', neighbor)]
    if variant != 'closure_omitted':
        lines += [action('Walk', target), action('Close', target)]
    if variant == 'reopened_before_leaving':
        lines += [action('Open', target), action('Walk', neighbor)]
    lines += [action('Walk', destination)]
    return lines


def parse_action_export(text, program, frame_count, fps, guard):
    """Preserve raw endpoints; emit only explicitly weak interior intervals.

    Repeated program indices and inserted WALK rows are legitimate. No claim
    is made that the trimmed interiors resolve animation/capture alignment.
    """
    rows = []
    occupied = set()
    previous_start = -1
    for line in text.lstrip('\ufeff').splitlines():
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 4:
            raise ValueError(f'Invalid action export row: {line}')
        source_index, action, start, end = fields
        source_index, start, end = int(source_index), int(start), int(end)
        if not (0 <= source_index < len(program) and 0 <= start <= end <= frame_count):
            raise ValueError(f'Out-of-range action row: {line}')
        if start < previous_start:
            raise ValueError('Action rows must be chronologically ordered')
        previous_start = start
        lo, hi = start + guard, min(frame_count, end - guard)
        row = {'program_index': source_index, 'action': action.upper(),
               'raw_start': start, 'raw_end': end, 'raw_line': line,
               'endpoint_convention': 'unresolved', 'quality': 'weak_program_supervision',
               'program_line': program[source_index], 'interior': None}
        if hi > lo:
            indices = set(range(lo, hi))
            if occupied & indices:
                raise ValueError('Overlapping action interiors')
            occupied |= indices
            row['interior'] = {'start_frame': lo, 'end_frame_exclusive': hi,
                               'start_us': lo * 1_000_000 // fps,
                               'end_us': hi * 1_000_000 // fps}
        rows.append(row)
    if not rows:
        raise ValueError('Empty action export')
    return rows


def frame_files(directory):
    images, graphs, cameras = {}, {}, set()
    for path in Path(directory).glob('Action_*'):
        m = re.fullmatch(r'Action_(\d+)_(\d+)_(normal\.png|graph\.json)', path.name)
        if not m:
            continue
        index, camera, kind = int(m[1]), int(m[2]), m[3]
        cameras.add(camera)
        mapping = images if kind == 'normal.png' else graphs
        if index in mapping:
            raise ValueError('Duplicate frame index or multiple camera streams')
        mapping[index] = path
    if len(cameras) != 1 or not images or set(images) != set(graphs):
        raise ValueError('Missing or mismatched RGB/graph frame keys')
    if sorted(images) != list(range(len(images))):
        raise ValueError('RGB indices are not contiguous from zero')
    return images, graphs, next(iter(cameras))


def camera_rotation(position, look_at):
    dx, dy, dz = [look_at[i] - position[i] for i in range(3)]
    return [math.degrees(math.atan2(-dy, math.hypot(dx, dz))), math.degrees(math.atan2(dx, dz)), 0]


def endpoint_rule(graph, actor_id, target_id, destination_id, expected_closed):
    target = next(n for n in graph['nodes'] if n['id'] == target_id)
    states = set(target.get('states', []))
    arrived = any(e['from_id'] == actor_id and e['to_id'] == destination_id
                  and e['relation_type'] == 'INSIDE' for e in graph['edges'])
    if not arrived:
        raise ValueError('Actor did not reach destination room')
    if ('CLOSED' in states) == ('OPEN' in states):
        raise ValueError('Target has ambiguous door state')
    if ('CLOSED' in states) != expected_closed:
        raise ValueError('Executed endpoint contradicts intended variant')
    return {'rule': 'close_target_before_departure', 'verdict': 'PASS' if expected_closed else 'VIOLATION',
            'scope': 'episode_endpoint_world_truth', 'target_states': sorted(states),
            'destination_reached': True, 'exact_departure_time_verified': False,
            'pixel_observability': 'unverified'}
