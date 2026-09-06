from dataclasses import replace
import json
import numpy as np
import pytest
from video_workbench.embedding import FeatureSpace, normalize
from video_workbench.index import FrameCache, Index, build, windows, writer_lock
from video_workbench.registry import Registry
from test_registry import video, manifest, row


class FakeEmbedder:
    space = FeatureSpace("test", dimension=3)

    def image(self, image):
        return normalize([[float(np.array(image).mean()) / 255, 1, 0.2]])[0]


def test_orphan_recovery_and_corruption(tmp_path):
    cache = FrameCache(tmp_path, FakeEmbedder.space)

    def crash():
        raise RuntimeError("simulated crash after rename before transaction")

    with pytest.raises(RuntimeError):
        cache.put("frame", [1, 2, 3], after_publish=crash)
    assert cache.get("frame") is None
    cache.put("frame", [1, 2, 3])
    assert cache.get("frame") is not None
    (cache.root / "frame.npy").write_bytes(b"bad")
    with pytest.raises(ValueError, match="corrupt"):
        cache.get("frame")
    cache.close()


def test_build_reuse_integrity_and_space(tmp_path, video):
    r = Registry(tmp_path / "r.sqlite")
    r.ingest(manifest(tmp_path, [row(video)]))
    e = FakeEmbedder()
    root = tmp_path / "cache"
    a = build(r, e, root, 0.2, 5, progress=lambda *a, **k: None)
    b = build(r, e, root, 0.2, 5, progress=lambda *a, **k: None)
    assert a["index_id"] == b["index_id"]
    assert a["fresh_frames"] > 0 and b["fresh_frames"] == 0 and b["reused_frames"] > 0
    idx = Index(a["manifest"], e.space.id)
    hits = idx.search([1, 1, 0], e.space.id, split="train")
    assert hits and idx.search([1, 1, 0], e.space.id, split="test") == []
    assert hits[0]["score"] >= hits[-1]["score"]
    with pytest.raises(ValueError, match="incompatible"):
        Index(a["manifest"], "different")
    with pytest.raises(ValueError, match="incompatible"):
        idx.search([1, 1, 0], "different")
    # Stable order even with exactly tied vectors.
    idx.vectors = np.ones_like(idx.vectors) / np.sqrt(3)
    tied = idx.search([1, 1, 1], e.space.id)
    assert [h["chunk_id"] for h in tied] == sorted(h["chunk_id"] for h in tied)
    p = idx.path.parent / "features.npy"
    p.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="hash"):
        Index(a["manifest"])
    r.close()


def test_writer_lock_and_window_boundaries(tmp_path):
    assert windows(5500000, 2) == [(0, 2000000), (2000000, 4000000), (4000000, 5500000)]
    with writer_lock(tmp_path):
        with pytest.raises(RuntimeError, match="writer"):
            with writer_lock(tmp_path):
                pass
