"""Fixed image encoder; no state labels enter feature extraction."""
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np
from PIL import Image

from video_workbench.embedding import QwenEmbedder, digest, normalize
from video_workbench.registry import file_hash
from video_workbench.perception.store import write_json
from .crops import POLICY

CONDITIONS = ('F', 'D', 'O', 'FD', 'FO')


def encode(manifest_path, model_path, destination):
    dest = Path(destination)
    if dest.exists():
        raise ValueError('new localization feature destination required')
    manifest = json.loads(Path(manifest_path).read_text())
    if manifest['status'] != 'complete' or manifest['policy'] != POLICY:
        raise ValueError('crop protocol mismatch')
    samples = [s for s in manifest['samples'] if any(a['kind'] == 'state' for a in s['aliases'])]
    encoder = QwenEmbedder(model_path)
    arrays = {c: np.zeros((len(samples), encoder.space.dimension), dtype=np.float32) for c in CONDITIONS}
    available = {c: np.ones(len(samples), dtype=bool) for c in CONDITIONS}
    for i, sample in enumerate(samples):
        for condition in ('F', 'D', 'O'):
            evidence = sample[condition]
            if evidence is None:
                available[condition][i] = False
                continue
            if file_hash(evidence['image']) != evidence['image_sha256']:
                raise ValueError('crop or full-frame image changed')
            with Image.open(evidence['image']) as image:
                arrays[condition][i] = encoder.image(image)
        for crop, fusion in [('D', 'FD'), ('O', 'FO')]:
            arrays[fusion][i] = normalize((arrays['F'][i] + arrays[crop][i])[None])[0] if available[crop][i] else arrays['F'][i]
        if i % 24 == 0:
            print(f'localization features {i+1}/{len(samples)}', flush=True)
    for c in CONDITIONS:
        if not np.isfinite(arrays[c]).all() or not np.allclose(np.linalg.norm(arrays[c][available[c]], axis=1), 1, atol=1e-4):
            raise ValueError('invalid localization features')
        arrays[c+'__available'] = available[c]
    for entity in ('fridge', 'microwave'):
        arrays[entity+'__hypotheses'] = np.stack([encoder.text(f'The {entity} door is {state}.') for state in ('closed', 'open')])
    space = asdict(encoder.space)
    producer = {'encoder': space, 'manifest_sha256': file_hash(manifest_path), 'policy': POLICY,
                'code_sha256': {p.name: file_hash(p) for p in (Path(__file__), Path(__file__).parents[1]/'embedding.py')},
                'samples': [s['sample_id'] for s in samples]}
    dest.mkdir(parents=True)
    np.savez_compressed(dest/'features.npz', **arrays)
    metadata = {'producer': producer, 'producer_id': digest(producer),
                'spaces': {c: digest([producer, c]) for c in CONDITIONS},
                'features_sha256': file_hash(dest/'features.npz'), 'timings': encoder.timings,
                'conditions': list(CONDITIONS), 'status': 'complete', 'labels_read': False,
                'missing_storage': 'zero vector with availability=false; prediction scores must be null',
                'oracle_conditions': ['O', 'FO'], 'fusion_fallback': 'full frame'}
    write_json(dest/'metadata.json', metadata)
    return metadata
