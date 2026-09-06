"""Native clip cache and immutable publication, independent of frame pooling."""

from dataclasses import asdict
from pathlib import Path
import time
import numpy as np
from .embedding import digest
from .index import FrameCache, Index, atomic_write, windows, writer_lock, write_json
from .media import selected_indices, decode_selected
from .registry import file_hash


def build_native(
    registry, embedder, root, seconds=5, fps=1, splits=("development",), progress=print
):
    seconds, fps = float(seconds), float(fps)
    if (
        not np.isfinite(fps)
        or not 0 < fps <= 30
        or not np.isfinite(seconds)
        or seconds <= 0
    ):
        raise ValueError("invalid native window or FPS")
    root = Path(root)
    with writer_lock(root):
        cache = FrameCache(root, embedder.space, namespace="clips")
        try:
            started = time.perf_counter()
            chunks = []
            vectors = []
            fresh = reused = 0
            episodes = [r for r in registry.episodes() if r["split"] in splits]
            if not episodes:
                raise ValueError("no episodes in requested splits")
            for ep in episodes:
                if file_hash(ep["video"]) != ep["video_sha256"]:
                    raise ValueError("source video changed")
                pts = ep["media"]["pts_us"]
                for start, end in windows(ep["media"]["duration_us"], seconds):
                    ids = selected_indices(pts, start, end, fps)
                    if not ids:
                        continue
                    chunk = {
                        "episode_id": ep["episode_id"],
                        "split": ep["split"],
                        "split_group": ep["split_group"],
                        "video_sha256": ep["video_sha256"],
                        "start_us": start,
                        "end_us": end,
                        "selected_pts_us": [pts[i] for i in ids],
                        "selected_raw_pts": [ep["media"]["raw_pts"][i] for i in ids],
                        "time_base": ep["media"]["time_base"],
                        "origin_us": ep["media"]["origin_us"],
                    }
                    chunk["chunk_id"] = digest({"space": embedder.space.id, **chunk})
                    vector = cache.get(chunk["chunk_id"])
                    if vector is None:
                        if len(ids) > embedder.space.max_frames:
                            raise ValueError(
                                "native clip exceeds frame limit; reduce FPS or window"
                            )
                        frames = decode_selected(ep["video"], ids)
                        # Never publish a cache entry until inference and validation succeed.
                        vector = cache.put(
                            chunk["chunk_id"],
                            embedder.video(
                                [frames[i] for i in ids],
                                chunk["selected_pts_us"],
                                start,
                            ),
                        )
                        fresh += 1
                    else:
                        reused += 1
                    chunks.append(chunk)
                    vectors.append(vector)
                progress(f"{ep['episode_id']}: native clips encoded", flush=True)
            if not vectors:
                raise ValueError("no native clips contain visual evidence")
            spec = {
                "schema": 1,
                "space": asdict(embedder.space),
                "space_id": embedder.space.id,
                "window_seconds": seconds,
                "fps": fps,
                "splits": sorted(splits),
                "producer_files": {
                    n: file_hash(Path(__file__).parent / n)
                    for n in (
                        "native_video.py",
                        "native_index.py",
                        "media.py",
                        "index.py",
                    )
                },
                "corpus": [
                    {
                        k: e[k]
                        for k in ("episode_id", "split", "split_group", "video_sha256")
                    }
                    for e in episodes
                ],
                "chunks": chunks,
            }
            identity = digest(spec)
            directory = root / "indices" / identity
            directory.mkdir(parents=True, exist_ok=True)
            array = np.stack(vectors).astype(np.float32)
            path = directory / "features.npy"
            manifest_path = directory / "manifest.json"
            if manifest_path.exists():
                if not np.array_equal(
                    Index(manifest_path, embedder.space.id).vectors, array
                ):
                    raise ValueError("immutable native index result changed")
            else:
                atomic_write(path, lambda f: np.save(f, array, allow_pickle=False))
                write_json(
                    manifest_path,
                    spec
                    | {
                        "index_id": identity,
                        "array_sha256": file_hash(path),
                        "shape": list(array.shape),
                    },
                )
            report = {
                "index_id": identity,
                "manifest": str(manifest_path),
                "chunks": len(chunks),
                "fresh_clips": fresh,
                "reused_clips": reused,
                "elapsed_seconds": time.perf_counter() - started,
                "feature_bytes": path.stat().st_size,
            }
            write_json(root / "last-build.json", report)
            return report
        finally:
            cache.close()
