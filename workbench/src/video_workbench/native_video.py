"""Opt-in FP32 native video with the audited official processor contract."""

from dataclasses import dataclass
from hashlib import sha256
import importlib.metadata
import inspect
from pathlib import Path
import time
import numpy as np
from .embedding import FeatureSpace, INSTRUCTION, artifact_identity, normalize

REPAIR_COMMIT = "6452614f6de04694d1e34fd13abaca11f6ffb994"
WRAPPER_SHA256 = "f265fecc0c4de4d896e7ef14a9e51bfc43f2e20f344c7f6e0d2c3b30c0265a73"
OFFICIAL_MODEL = "Qwen/Qwen3-VL-Embedding-2B"
OFFICIAL_REVISION = "9f2f7e710d6d81056aa5c0a4f04764fec6bb7bda"
OFFICIAL_ARTIFACTS = "b54ff71dd970ab734fdd24dcbe4be01553bf8cb762b8acb1c195669678596e95"
DEFAULT_MODEL = "output/mlx-video-fix/models/official"
PINNED_RUNTIME = {
    "mlx": "0.32.2",
    "mlx-metal": "0.32.2",
    "transformers": "5.16.1",
    "av": "17.1.0",
    "torch": "2.14.0",
    "torchvision": "0.29.0",
    "numpy": "2.4.6",
    "pillow": "12.3.0",
}


@dataclass(frozen=True)
class NativeFeatureSpace(FeatureSpace):
    model_id: str = OFFICIAL_MODEL
    revision: str = OFFICIAL_REVISION
    mode: str = "native_video"
    adapter: str = "qwen3-vl-native-official-fp32-v1"
    quantization: str = "none-fp32"
    resize: str = "PIL-bicubic-320x240-then-official-torchvision-bicubic"
    pooling: str = "last-unmasked-token-then-fp32-l2"
    mlx_vlm: str = "git:" + REPAIR_COMMIT
    processor: str = "transformers.Qwen3VLProcessor-5.16.1-checkpoint-template"
    temporal: str = (
        "actual-selected-PTS-relative-to-clip-us-repeat-last-frame-and-PTS-v1"
    )
    max_frames: int = 32
    wrapper_sha256: str = WRAPPER_SHA256
    mlx_source: str = ""
    adapter_source: str = ""


def prepare_video(frames, pts_us, start_us, size=(320, 240), max_frames=32):
    """Map microsecond PTS to processor timestamp ticks without assuming CFR."""
    from PIL import Image

    if not frames or len(frames) > max_frames or len(frames) != len(pts_us):
        raise ValueError("native video requires 1..32 frames with matching PTS")
    pts = np.asarray(pts_us)
    if (
        pts.ndim != 1
        or pts.dtype.kind not in "iu"
        or np.any(pts < start_us)
        or np.any(np.diff(pts) <= 0)
    ):
        raise ValueError(
            "PTS must be strictly increasing integer microseconds within the clip"
        )
    arrays = [
        np.asarray(frame.convert("RGB").resize(size, Image.Resampling.BICUBIC))
        for frame in frames
    ]
    ticks = [int(p) - int(start_us) for p in pts]
    if len(arrays) % 2:
        arrays.append(arrays[-1])
        ticks.append(ticks[-1])
    # frames_indices are timestamp ticks here, not decode indices. Sampling is off.
    return np.stack(arrays), {
        "total_num_frames": len(arrays),
        "fps": 1_000_000.0,
        "frames_indices": ticks,
    }


class NativeVideoEmbedder:
    def __init__(self, path=DEFAULT_MODEL):
        for package, expected in PINNED_RUNTIME.items():
            try:
                actual_version = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                actual_version = None
            if actual_version != expected:
                raise RuntimeError(
                    f"native video requires {package}=={expected}; use the isolated native environment"
                )
        # Construct before MLX model registration can replace AutoProcessor mappings.
        from transformers import Qwen3VLProcessor

        self.path = Path(path)
        self.processor = Qwen3VLProcessor.from_pretrained(
            str(path), local_files_only=True
        )
        if any(
            not p.__class__.__module__.startswith("transformers.")
            for p in (self.processor.image_processor, self.processor.video_processor)
        ):
            raise RuntimeError(
                "native video requires official Transformers image/video processors"
            )
        import mlx.core as mx
        from mlx_vlm.models.qwen3_vl_embedding.qwen3_vl_embedding import Model
        from mlx_vlm.embedding_loader import load_embedding_model

        actual = sha256(Path(inspect.getfile(Model)).read_bytes()).hexdigest()
        if actual != WRAPPER_SHA256:
            raise RuntimeError(
                "native video requires the pinned repaired MLX wrapper; pooled-image environment is unsupported"
            )
        identity, self.artifacts = artifact_identity(path)
        if identity != OFFICIAL_ARTIFACTS:
            raise ValueError(
                "native video requires the audited official checkpoint and processor artifacts"
            )
        import json

        config = json.loads((self.path / "config.json").read_text())
        if config.get("quantization") or config.get("quantization_config"):
            raise ValueError(
                "quantized native video has not passed acceptance; use official weights"
            )
        import mlx_vlm
        from .embedding import digest

        package = Path(mlx_vlm.__file__).parent
        source = digest(
            {
                str(p.relative_to(package)): sha256(p.read_bytes()).hexdigest()
                for p in sorted(package.rglob("*.py"))
            }
        )
        self.space = NativeFeatureSpace(
            artifacts=identity,
            runtime=tuple(sorted(PINNED_RUNTIME.items())),
            mlx_source=source,
            adapter_source=sha256(Path(__file__).read_bytes()).hexdigest(),
        )
        self.mx = mx
        self.model = load_embedding_model(
            self.path, config_overrides={"model_type": "qwen3_vl_embedding"}
        )
        self.model.set_dtype(mx.float32)
        mx.eval(self.model.parameters())
        self.timings = []

    def _encode(self, content, **kwargs):
        started = time.perf_counter()
        prompt = self.processor.apply_chat_template(
            [
                {"role": "system", "content": [{"type": "text", "text": INSTRUCTION}]},
                {"role": "user", "content": content},
            ],
            add_generation_prompt=True,
            tokenize=False,
        )
        prepared = self.processor(
            text=[prompt],
            return_tensors="np",
            padding=True,
            add_special_tokens=False,
            **kwargs,
        )
        keys = (
            "input_ids",
            "attention_mask",
            "pixel_values",
            "pixel_values_videos",
            "image_grid_thw",
            "video_grid_thw",
        )
        inputs = {
            k: self.mx.array(np.asarray(prepared[k])) for k in keys if k in prepared
        }
        if (
            "videos" in kwargs
            and not {"pixel_values_videos", "video_grid_thw"} <= inputs.keys()
        ):
            raise ValueError("processor dropped native video pixels or grid")
        out = self.model(**inputs).text_embeds
        self.mx.eval(out)
        result = normalize(np.array(out.astype(self.mx.float32)))
        if result.shape != (1, self.space.dimension):
            raise ValueError(f"unexpected native embedding shape {result.shape}")
        self.timings.append(time.perf_counter() - started)
        return result[0]

    def text(self, text):
        if not text.strip():
            raise ValueError("empty query")
        return self._encode([{"type": "text", "text": text}])

    def video(self, frames, pts_us, start_us=0):
        video, metadata = prepare_video(
            frames, pts_us, start_us, self.space.image_size, self.space.max_frames
        )
        return self._encode(
            [{"type": "video"}],
            videos=[video],
            video_metadata=[metadata],
            do_sample_frames=False,
            cap_pixels_per_frame=False,
        )
