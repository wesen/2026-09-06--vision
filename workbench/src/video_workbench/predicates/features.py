"""Cache individual frozen image features without reading evaluator labels."""
from dataclasses import asdict
from pathlib import Path
import json
import numpy as np
from PIL import Image
from video_workbench.embedding import QwenEmbedder, digest
from video_workbench.registry import file_hash
from .contracts import validate_samples

CONDITIONS = {
    'generic': 'The {entity} door is {state}.',
    'correct_context': 'In a kitchen, the {entity} door is {state}.',
    'misleading_context': 'In a bathroom, the {entity} door is {state}.',
}
CONTEXT_ONLY = 'A {entity} in a kitchen.'


def binding(sample):
    return {k: sample[k] for k in ('sample_id', 'entity_id', 'entity_class', 'property', 'sample_us', 'video_sha256', 'image_sha256')}


def validate_cache(metadata, samples, expected_space=None):
    if expected_space is not None and metadata['feature_space_id'] != expected_space:
        raise ValueError('feature-space mismatch')
    if metadata['bindings'] != [binding(s) for s in samples]:
        raise ValueError('cached entity/evidence mismatch')
    if metadata['templates'] != CONDITIONS or metadata['context_only'] != CONTEXT_ONLY:
        raise ValueError('cached text-template mismatch')


def load_cache(path, samples, expected_space=None):
    path = Path(path)
    metadata = json.loads((path/'metadata.json').read_text())
    validate_cache(metadata, samples, expected_space)
    if file_hash(path/'features.npz') != metadata['features_sha256']:
        raise ValueError('feature archive hash mismatch')
    with np.load(path/'features.npz', allow_pickle=False) as archive:
        arrays = {key: archive[key] for key in archive.files}
    images = arrays['images']
    if images.shape != (len(samples), metadata['space']['dimension']) or not np.isfinite(images).all():
        raise ValueError('invalid image features')
    if not np.allclose(np.linalg.norm(images, axis=1), 1, atol=1e-4):
        raise ValueError('features must be unit normalized')
    return metadata, arrays


def extract(samples, model_path, destination):
    validate_samples(samples)
    destination = Path(destination)
    if (destination/'metadata.json').exists():
        raise ValueError('cache already exists; use a new destination to re-encode')
    destination.mkdir(parents=True, exist_ok=True)
    encoder = QwenEmbedder(model_path)
    space = dict(asdict(encoder.space), mode='single_image_state', pooling='none', sampling='fixed-relative-six-reviewed-v2')
    metadata = {'space': space, 'feature_space_id': digest(space), 'bindings': [binding(s) for s in samples],
                'templates': CONDITIONS, 'context_only': CONTEXT_ONLY, 'image_seconds': [],
                'adapter_sha256': file_hash(Path(__file__).parents[1]/'embedding.py'),
                'extractor_sha256': file_hash(Path(__file__))}
    vectors = []
    for i, sample in enumerate(samples):
        with Image.open(sample['image']) as im:
            vectors.append(encoder.image(im))
        metadata['image_seconds'].append(encoder.timings[-1])
        if i % 12 == 0:
            print(f'Encoded {i+1}/{len(samples)} images', flush=True)
    arrays = {'images': np.stack(vectors)}
    for entity in sorted({s['entity_class'] for s in samples}):
        for condition, template in CONDITIONS.items():
            arrays[entity+'__'+condition] = np.stack([encoder.text(template.format(entity=entity,state=state)) for state in ('closed','open')])
        arrays[entity+'__context_only'] = encoder.text(CONTEXT_ONLY.format(entity=entity))
    np.savez_compressed(destination/'features.npz', **arrays)
    metadata['features_sha256'] = file_hash(destination/'features.npz')
    metadata['text_seconds'] = encoder.timings[len(samples):]
    (destination/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    return load_cache(destination, samples)
