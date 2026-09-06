"""Join frozen detector outputs to exact reviewed sources and report coverage."""
import json
from dataclasses import fields
from pathlib import Path

from video_workbench.embedding import digest
from video_workbench.index import write_json
from video_workbench.registry import file_hash
from video_workbench.perception.contracts import FrameRef, Detection
from video_workbench.perception.store import rows, verify_episode
from .annotations import validate_review
from .evaluate import match, summarize


def load_detections(samples, detector_root):
    root = Path(detector_root)
    run = json.loads((root / 'run.json').read_text())
    # Detector.spec uses Ultralytics' integer-keyed names dictionary. JSON
    # stringifies those keys; restore their original type before hash checks.
    run['spec']['detector']['class_map'] = {int(k): v for k, v in run['spec']['detector']['class_map'].items()}
    if run['status'] != 'complete' or digest(run['spec']) != run['run_id']:
        raise ValueError('incomplete or changed detector run')
    detector = run['spec']['detector']
    if detector['parameters']['conf'] > .10:
        raise ValueError('detector floor prevents frozen confidence sweep')
    manifest_refs = {e['episode_id']: e['manifest_sha256'] for e in run['episodes']}
    if len(manifest_refs) != len(run['episodes']):
        raise ValueError('duplicate detector episode')
    groups = {}
    for sample in samples:
        groups.setdefault(sample['episode_id'], []).append(sample)
    result, provenance = {}, []
    for episode_id, targets in groups.items():
        folder = root / 'episodes' / episode_id
        if episode_id not in manifest_refs or file_hash(folder / 'manifest.json') != manifest_refs[episode_id]:
            raise ValueError('missing or changed detector episode manifest')
        manifest = verify_episode(folder)
        if manifest['run_id'] != run['run_id'] or manifest['producer_id'] != digest(detector):
            raise ValueError('detector producer mismatch')
        if not {'frames.jsonl', 'detections.jsonl'} <= set(manifest['artifacts']):
            raise ValueError('unhashed detector artifacts')
        episode = manifest['episode']
        if episode['episode_id'] != episode_id or file_hash(episode['video']) != episode['video_sha256']:
            raise ValueError('detector video source changed')
        frame_rows = rows(folder / 'frames.jsonl')
        detections = rows(folder / 'detections.jsonl')
        if len(frame_rows) != manifest['frames'] or len(detections) != manifest['detections']:
            raise ValueError('detector row counts changed')
        frames, by_index, by_frame = {}, {}, {}
        for row in frame_rows:
            frame = FrameRef(**{f.name: row[f.name] for f in fields(FrameRef)})
            media = episode['media']
            if (frame.id != row['frame_id'] or frame.id in frames or frame.frame_index in by_index
                    or frame.episode_id != episode_id or frame.video_sha256 != episode['video_sha256']
                    or frame.width != media['width'] or frame.height != media['height']
                    or frame.pts_us != media['pts_us'][frame.frame_index]
                    or frame.raw_pts != media['raw_pts'][frame.frame_index]
                    or frame.time_base != media['time_base']):
                raise ValueError('detector frame identity mismatch')
            frames[frame.id] = frame
            by_index[frame.frame_index] = frame
            by_frame[frame.id] = []
        seen = set()
        for row in detections:
            if row['frame_id'] not in frames or row['detection_id'] in seen:
                raise ValueError('unknown detection frame or duplicate detection')
            detection = Detection(**{f.name: row[f.name] for f in fields(Detection)})
            detection.validate(frames[row['frame_id']])
            if row['producer_id'] != manifest['producer_id'] or detector['class_map'][row['class_id']] != row['class_name']:
                raise ValueError('detection producer or vocabulary mismatch')
            seen.add(row['detection_id'])
            by_frame[row['frame_id']].append(row)
        for sample in targets:
            frame = by_index.get(sample['frame_index'])
            if frame is None:
                raise ValueError('requested source frame absent from detector run')
            for name in ('episode_id', 'video_sha256', 'frame_index', 'pts_us', 'width', 'height'):
                if getattr(frame, name) != sample[name]:
                    raise ValueError('requested source differs from detector frame')
            result[sample['sample_id']] = by_frame[frame.id]
        provenance.append({'episode_id': episode_id, 'manifest_sha256': manifest_refs[episode_id], 'artifacts': manifest['artifacts']})
    return result, {'run_id': run['run_id'], 'run_sha256': file_hash(root / 'run.json'), 'episodes': provenance}


def audit(dataset, reviews_path, detector_root, destination):
    dest = Path(destination)
    if dest.exists():
        raise ValueError('new audit directory required')
    samples_path = Path(dataset) / 'samples.json'
    samples = json.loads(samples_path.read_text())
    reviews = json.loads(Path(reviews_path).read_text())
    by_id = {r['sample_id']: r for r in reviews}
    if len(by_id) != len(reviews) or len({s['sample_id'] for s in samples}) != len(samples) or set(by_id) != {s['sample_id'] for s in samples}:
        raise ValueError('review population mismatch')
    for sample in samples:
        validate_review(sample, by_id[sample['sample_id']])
    detections, provenance = load_detections(samples, detector_root)
    results = [match(s, by_id[s['sample_id']], detections[s['sample_id']], confidence)
               for confidence in (.10, .25, .50) for s in samples]
    summary = {}
    for confidence in (.10, .25, .50):
        subset = [r for r in results if r['confidence'] == confidence]
        strata = {}
        for field in ('split', 'requested_class', 'apartment', 'view', 'size', 'occluded', 'visibility'):
            strata[field] = {str(value): summarize([r for r in subset if r[field] == value])
                             for value in sorted({r[field] for r in subset}, key=str)}
        summary[str(confidence)] = {'overall': summarize(subset), 'strata': strata}
    dest.mkdir(parents=True)
    write_json(dest / 'rows.json', results)
    write_json(dest / 'summary.json', summary)
    write_json(dest / 'manifest.json', {'samples_sha256': file_hash(samples_path), 'reviews_sha256': file_hash(reviews_path), 'detector': provenance, 'iou_threshold': .5, 'confidence_policies': [.10, .25, .50], 'artifacts': {n: file_hash(dest / n) for n in ('rows.json', 'summary.json')}})
    return summary
