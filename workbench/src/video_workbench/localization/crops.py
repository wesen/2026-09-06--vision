"""Label-free F/D/O evidence with identical D/O raster geometry."""
import json
from pathlib import Path

from PIL import Image

from video_workbench.embedding import digest
from video_workbench.registry import file_hash
from video_workbench.perception.contracts import expand
from video_workbench.perception.store import write_json
from .annotations import CLASS_MAP, validate_review
from .detector_audit import load_detections

POLICY = {'confidence': .25, 'margin': .25, 'output_size': [320, 240],
          'interpolation': 'PIL-bicubic', 'minimum_expanded_extent': 12,
          'binding': 'exactly-one-usable-requested-class',
          'oracle': 'reviewed-visible-extent; diagnostic only',
          'fusion': 'unit(full+crop); full fallback when crop missing'}


def prepare(dataset, reviews_path, detector_root, destination):
    dest = Path(destination)
    if dest.exists():
        raise ValueError('new crop destination required')
    samples_path = Path(dataset) / 'samples.json'
    samples = json.loads(samples_path.read_text())
    reviews = json.loads(Path(reviews_path).read_text())
    by_id = {r['sample_id']: r for r in reviews}
    if len(by_id) != len(reviews) or set(by_id) != {s['sample_id'] for s in samples}:
        raise ValueError('review population mismatch')
    for s in samples:
        validate_review(s, by_id[s['sample_id']])
    detections, provenance = load_detections(samples, detector_root)
    producer = digest({'policy': POLICY, 'samples': file_hash(samples_path),
                       'reviews': file_hash(reviews_path), 'detector': provenance,
                       'code': file_hash(__file__)})
    dest.mkdir(parents=True)
    records = []
    for s in samples:
        review = by_id[s['sample_id']]
        def expanded(rect):
            return list(map(int, expand(rect, s['width'], s['height'], POLICY['margin'])))
        candidates = []
        for d in detections[s['sample_id']]:
            if d['class_name'] == CLASS_MAP[s['requested_class']] and d['score'] >= POLICY['confidence']:
                rect = expanded(d['xyxy'])
                if min(rect[2]-rect[0], rect[3]-rect[1]) >= POLICY['minimum_expanded_extent']:
                    candidates.append((d, rect))
        selected = candidates[0] if len(candidates) == 1 else None
        oracle = expanded(review['visible_xyxy']) if review['visible_xyxy'] is not None else None
        if oracle is not None and min(oracle[2]-oracle[0], oracle[3]-oracle[1]) < POLICY['minimum_expanded_extent']:
            oracle = None
        record = {'sample_id': s['sample_id'], 'aliases': s['aliases'],
                  'episode_id': s['episode_id'], 'entity_id': s['requested_entity'],
                  'image_sha256': s['image_sha256'], 'video_sha256': s['video_sha256'],
                  'frame_index': s['frame_index'], 'pts_us': s['pts_us'], 'split': s['split'],
                  'F': {'image': s['image'], 'image_sha256': s['image_sha256'], 'evidence_id': s['sample_id']},
                  'D': None, 'O': None, 'detector_usable_candidates': len(candidates),
                  'detector_status': 'unique' if selected else 'ambiguous' if candidates else 'unsupported' if CLASS_MAP[s['requested_class']] is None else 'missing',
                  'oracle_status': 'reviewed' if oracle else review['visibility'] if review['visible_xyxy'] is None else 'low_source_resolution'}
        with Image.open(s['image']) as source:
            for kind, rect in [('D', selected[1] if selected else None), ('O', oracle)]:
                if rect is None:
                    continue
                detection_ids = [selected[0]['detection_id']] if kind == 'D' else []
                evidence_id = digest([producer, s['sample_id'], kind, rect, detection_ids])[:24]
                path = dest / f'{evidence_id}.png'
                source.convert('RGB').crop(rect).resize(tuple(POLICY['output_size']), Image.Resampling.BICUBIC).save(path)
                record[kind] = {'evidence_id': evidence_id, 'image': str(path), 'image_sha256': file_hash(path),
                                'source_rect': rect, 'detection_ids': detection_ids, 'oracle_assisted': kind == 'O'}
        records.append(record)
    manifest = {'producer_id': producer, 'policy': POLICY, 'samples_sha256': file_hash(samples_path),
                'reviews_sha256': file_hash(reviews_path), 'detector': provenance, 'samples': records,
                'status': 'complete', 'labels_read': False}
    write_json(dest / 'manifest.json', manifest)
    return manifest
