"""Encode audited native FP32 trailing windows without loading weak labels."""

from pathlib import Path
from dataclasses import asdict
import json
import time
import resource
import argparse
from PIL import Image
from video_workbench.native_video import NativeVideoEmbedder, DEFAULT_MODEL
import numpy as np
from video_workbench.embedding import digest
from video_workbench.registry import file_hash
from video_workbench.media import decode_selected, probe
from video_workbench.perception.store import write_json


def encode(dataset, destination, limit=None):
    started = time.perf_counter()
    if limit is not None and limit < 1:
        raise ValueError("limit must be positive")
    root = Path(dataset)
    dest = Path(destination)
    if dest.exists():
        raise ValueError("new temporal feature directory required")
    manifest = json.loads((root / "manifest.json").read_text())
    if file_hash(root / "inputs.json") != manifest["inputs_sha256"]:
        raise ValueError("model inputs changed")
    all_rows = json.loads((root / "inputs.json").read_text())
    rows = all_rows[:limit]
    encoder = NativeVideoEmbedder(DEFAULT_MODEL)
    loaded = time.perf_counter()
    pixel_probe = None
    spec = {
        "encoder": asdict(encoder.space),
        "mode": "dense-trailing-native-video-fp32",
        "inputs_sha256": manifest["inputs_sha256"],
        "policy": manifest["policy"],
        "code_sha256": {
            str(p): file_hash(p)
            for p in [
                Path(__file__),
                Path(__file__).parents[1] / "native_video.py",
                Path(__file__).parents[1] / "media.py",
            ]
        },
    }
    groups = {}
    for i, r in enumerate(rows):
        groups.setdefault(r["episode_id"], []).append((i, r))
    vectors = np.zeros((len(rows), encoder.space.dimension), dtype=np.float32)
    valid = np.zeros(len(rows), dtype=bool)
    source_audit = []
    for eid, items in groups.items():
        r = items[0][1]
        if file_hash(r["video"]) != r["video_sha256"]:
            raise ValueError("temporal source changed")
        media = probe(r["video"])
        indices = sorted({j for _, w in items for j in w["frame_indices"]})
        images = decode_selected(r["video"], indices)
        for i, w in items:
            actual = [media["pts_us"][j] for j in w["frame_indices"]]
            if actual != w["pts_us"] or any(
                t < w["start_us"] or t >= w["end_us"] for t in actual
            ):
                raise ValueError("temporal source-time mapping changed")
            if (
                [media["raw_pts"][j] for j in w["frame_indices"]] != w["raw_pts"]
                or media["time_base"] != w["time_base"]
                or media["origin_us"] != w["origin_us"]
            ):
                raise ValueError("native timestamp provenance changed")
            if w["available_us"] < w["end_us"]:
                raise ValueError("future feature horizon")
            if w["frame_indices"]:
                frames = [images[j] for j in w["frame_indices"]]
                vectors[i] = encoder.video(frames, w["pts_us"], w["start_us"])
                valid[i] = True
                if pixel_probe is None:
                    black = encoder.video(
                        [Image.new("RGB", f.size) for f in frames],
                        w["pts_us"],
                        w["start_us"],
                    )
                    delta = float(np.max(np.abs(vectors[i] - black)))
                    pixel_probe = {
                        "sample_id": w["sample_id"],
                        "black_cosine": float(vectors[i] @ black),
                        "max_abs_difference": delta,
                    }
                    if delta < 1e-5:
                        raise ValueError(
                            "native features insensitive to changed pixels"
                        )
        source_audit.append(
            {
                "episode_id": eid,
                "video_sha256": r["video_sha256"],
                "encoded_frames": len(indices),
                "windows": len(items),
                "native_mapping_verified": True,
            }
        )
        print(
            f"temporal encoded {eid}: {len(items)} windows / {len(indices)} frames",
            flush=True,
        )
    if not np.isfinite(vectors).all() or not np.allclose(
        np.linalg.norm(vectors[valid], axis=1), 1, atol=1e-4
    ):
        raise ValueError("invalid native features")
    dest.mkdir(parents=True)
    np.savez_compressed(dest / "features.npz", features=vectors, valid=valid)
    result = {
        "status": "pilot" if len(rows) != len(all_rows) else "complete",
        "spec": spec,
        "space_id": digest(spec),
        "sample_ids": [r["sample_id"] for r in rows],
        "features_sha256": file_hash(dest / "features.npz"),
        "source_audit": source_audit,
        "timings": encoder.timings,
        "labels_read": False,
        "pixel_probe": pixel_probe,
        "wall_seconds": time.perf_counter() - started,
        "load_seconds": loaded - started,
        "peak_mlx_bytes": encoder.mx.get_peak_memory(),
        "max_rss_bytes_macos": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "limitation": "Native FP32 versus existing four-bit pooled comparison changes both representation and precision; weak labels and offline source clocks.",
    }
    write_json(dest / "manifest.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    parser.add_argument("destination")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    encode(args.dataset, args.destination, args.limit)
