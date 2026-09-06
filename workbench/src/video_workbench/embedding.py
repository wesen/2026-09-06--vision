"""Explicit pooled-image baseline; no implicit native-video fallback."""
from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
import importlib.metadata
import json
import time
import numpy as np

MODEL_ID = 'arthurcollet/Qwen3-VL-Embedding-2B-mlx-4bit'
REVISION = '99b57b385f543a94c46d9f8e85a354de4c836b37'
INSTRUCTION = "Represent the user's input."


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def normalize(values):
    a = np.asarray(values, dtype=np.float32)
    if a.ndim != 2 or not np.isfinite(a).all():
        raise ValueError('embeddings must be finite [batch, dimension]')
    norms = np.linalg.norm(a, axis=1, keepdims=True)
    if np.any(norms < 1e-12):
        raise ValueError('zero embedding')
    return a / norms


@dataclass(frozen=True)
class FeatureSpace:
    artifacts: str
    model_id: str = MODEL_ID
    revision: str = REVISION
    mode: str = 'pooled_images'
    adapter: str = 'qwen3-vl-embedding-last-token-v1'
    quantization: str = 'affine-4bit-group64'
    instruction: str = INSTRUCTION
    image_size: tuple = (320, 240)
    resize: str = 'PIL-bicubic'
    pooling: str = 'mean-of-unit-frame-vectors-then-l2'
    dimension: int = 2048
    dtype: str = 'float32'
    normalization: str = 'l2'
    sampling: str = 'first-PTS-at-or-after-grid-v1'
    mlx_vlm: str = '0.6.17'
    transformers: str = '5.16.1'

    @property
    def id(self):
        return digest(asdict(self))


def artifact_identity(path):
    records = {}
    for p in sorted(Path(path).iterdir()):
        if p.suffix in {'.json', '.jinja', '.safetensors', '.txt'}:
            h = sha256()
            with p.open('rb') as f:
                for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
                    h.update(block)
            records[p.name] = h.hexdigest()
    if not any(n.endswith('.safetensors') for n in records):
        raise ValueError('model weights missing')
    return digest(records), records


class QwenEmbedder:
    def __init__(self, path):
        import mlx.core as mx
        from mlx_vlm.embedding_loader import load_embedding_model
        from transformers import AutoProcessor
        self.mx = mx
        self.path = Path(path)
        identity, self.artifacts = artifact_identity(path)
        self.space = FeatureSpace(artifacts=identity,
            mlx_vlm=importlib.metadata.version('mlx-vlm'),
            transformers=importlib.metadata.version('transformers'))
        self.model = load_embedding_model(self.path,
            config_overrides={'model_type': 'qwen3_vl_embedding'})
        self.processor = AutoProcessor.from_pretrained(str(path), local_files_only=True)
        self.timings = []

    def _encode(self, content, images=None):
        from mlx_vlm.utils import prepare_inputs
        conversation = [
            {'role': 'system', 'content': [{'type': 'text', 'text': INSTRUCTION}]},
            {'role': 'user', 'content': content}]
        prompt = self.processor.apply_chat_template(conversation,
            add_generation_prompt=True, tokenize=False)
        started = time.perf_counter()
        inputs = prepare_inputs(self.processor, prompts=prompt, images=images)
        if images and inputs.get('pixel_values') is None:
            raise ValueError('processor dropped image pixels')
        # The upstream encoder caches position IDs. Each independent sample must reset them.
        self.model.language_model._position_ids = None
        self.model.language_model._rope_deltas = None
        out = self.model(**inputs).text_embeds
        self.mx.eval(out)
        result = normalize(np.array(out.astype(self.mx.float32)))
        if result.shape != (1, self.space.dimension):
            raise ValueError(f'unexpected shape {result.shape}')
        self.timings.append(time.perf_counter() - started)
        return result[0]

    def text(self, text):
        if not text.strip():
            raise ValueError('empty query')
        return self._encode([{'type': 'text', 'text': text}])

    def image(self, image):
        from PIL import Image
        image = image.convert('RGB').resize(self.space.image_size, Image.Resampling.BICUBIC)
        return self._encode([{'type': 'image'}], images=[image])

    def video(self, *_args, **_kwargs):
        raise NotImplementedError('mlx-vlm 0.6.17 qwen3_vl_embedding drops pixel_values_videos; use explicit pooled_images')

    def pool(self, frames):
        if not frames:
            raise ValueError('no frames')
        return normalize(np.mean(np.stack([self.image(f) for f in frames]), axis=0)[None])[0]
