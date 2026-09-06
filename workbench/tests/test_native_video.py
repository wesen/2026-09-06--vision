from dataclasses import replace
import numpy as np
import pytest
from PIL import Image
from video_workbench.embedding import FeatureSpace, normalize
from video_workbench.native_video import NativeFeatureSpace, prepare_video
from video_workbench.native_index import build_native
from video_workbench.index import FrameCache, Index, build
from video_workbench.registry import Registry
from test_registry import video, manifest, row
from test_index import FakeEmbedder


def test_pts_and_odd_padding_preserve_selected_time():
    frames = [Image.new("RGB", (10, 10), color=(i * 40, 0, 0)) for i in range(3)]
    pixels, meta = prepare_video(frames, [2_000_000, 2_350_000, 2_800_000], 2_000_000)
    assert pixels.shape == (4, 240, 320, 3)
    assert np.array_equal(pixels[-1], pixels[-2])
    assert meta["frames_indices"] == [0, 350_000, 800_000, 800_000]
    assert meta["fps"] == 1_000_000
    one, meta = prepare_video(frames[:1], [2_000_000], 2_000_000)
    assert len(one) == 2 and meta["frames_indices"] == [0, 0]
    with pytest.raises(ValueError, match="PTS"):
        prepare_video(frames[:2], [10, 10], 0)
    with pytest.raises(ValueError):
        prepare_video([], [], 0)


class NativeFake:
    space = NativeFeatureSpace("test", dimension=3)
    calls = 0

    def video(self, frames, pts_us, start_us):
        self.calls += 1
        return normalize(
            [[float(np.array(frames[0]).mean()) / 255, 1, len(frames) / 10]]
        )[0]


def test_native_cache_is_distinct_and_rejects_pooled_index(tmp_path, video):
    r = Registry(tmp_path / "r.sqlite")
    r.ingest(manifest(tmp_path, [row(video)]))
    root = tmp_path / "cache"
    e = NativeFake()
    pooled = build(r, FakeEmbedder(), root, 0.2, 5, progress=lambda *a, **k: None)
    a = build_native(r, e, root, 0.2, 5, ("train",), progress=lambda *a, **k: None)
    calls = e.calls
    b = build_native(r, e, root, 0.2, 5, ("train",), progress=lambda *a, **k: None)
    assert (
        calls > 0
        and e.calls == calls
        and b["fresh_clips"] == 0
        and b["reused_clips"] > 0
    )
    assert a["index_id"] == b["index_id"] and a["index_id"] != pooled["index_id"]
    assert (root / "frames").exists() and (root / "clips").exists()
    with pytest.raises(ValueError, match="incompatible"):
        Index(pooled["manifest"], e.space.id)
    with pytest.raises(ValueError, match="incompatible"):
        Index(a["manifest"], FakeEmbedder.space.id)
    assert replace(e.space, temporal="different").id != e.space.id
    assert replace(e.space, wrapper_sha256="different").id != e.space.id
    r.close()


def test_failed_native_inference_does_not_publish(tmp_path, video):
    r = Registry(tmp_path / "r.sqlite")
    r.ingest(manifest(tmp_path, [row(video)]))

    class Broken(NativeFake):
        def video(self, *args):
            raise RuntimeError("inference failed")

    root = tmp_path / "cache"
    with pytest.raises(RuntimeError, match="inference failed"):
        build_native(
            r, Broken(), root, 0.2, 5, ("train",), progress=lambda *a, **k: None
        )
    assert not list(root.glob("indices/*/manifest.json"))
    assert not (root / "last-build.json").exists()
    cache = FrameCache(root, Broken.space, namespace="clips")
    assert cache.db.execute("SELECT count(*) FROM features").fetchone()[0] == 0
    cache.close()
    r.close()
