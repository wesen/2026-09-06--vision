from fractions import Fraction
import json
import av
import numpy as np
import pytest
from video_workbench.registry import Registry, file_hash
from video_workbench.media import probe, selected_indices, decode_selected


@pytest.fixture
def video(tmp_path):
    p = tmp_path / "v.mp4"
    with av.open(str(p), "w") as c:
        s = c.add_stream("libx264", rate=10)
        s.width = 64
        s.height = 48
        s.pix_fmt = "yuv420p"
        s.time_base = Fraction(1, 1000)
        s.codec_context.time_base = Fraction(1, 1000)
        for i, pts in enumerate([0, 100, 350, 450]):
            f = av.VideoFrame.from_ndarray(
                np.full((48, 64, 3), i * 60, dtype=np.uint8), format="rgb24"
            )
            f.pts = pts
            f.time_base = Fraction(1, 1000)
            for packet in s.encode(f):
                c.mux(packet)
        for packet in s.encode():
            c.mux(packet)
    return p


def row(path, **kwargs):
    return (
        dict(
            episode_id="ep-one",
            split="train",
            split_group="g1",
            video=path.name,
            video_sha256=file_hash(path),
        )
        | kwargs
    )


def manifest(tmp_path, rows):
    p = tmp_path / "inputs.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows))
    return p


def test_vfr_uses_decoded_pts(video):
    m = probe(video)
    assert m["variable_rate"]
    assert m["frames"] == 4
    assert m["pts_us"][2] != 200000
    indices = selected_indices(m["pts_us"], 0, m["duration_us"], 5)
    assert indices == [0, 2, 3]
    assert len(decode_selected(video, indices)) == 3


def test_ingest_repeat_and_rollback(tmp_path, video):
    r = Registry(tmp_path / "r.sqlite")
    good = row(video)
    assert r.ingest(manifest(tmp_path, [good]))["registered"] == 1
    assert r.ingest(manifest(tmp_path, [good]))["registered"] == 1
    with pytest.raises(ValueError, match="hash mismatch"):
        r.ingest(
            manifest(
                tmp_path,
                [
                    row(video, episode_id="ep-two"),
                    row(video, episode_id="ep-bad", video_sha256="bad"),
                ],
            )
        )
    assert len(r.episodes()) == 1
    r.close()


@pytest.mark.parametrize(
    "change,error",
    [
        ({"split": "test"}, "group crosses"),
        ({"split": "test", "split_group": "g2"}, "identical video"),
        ({"video": "missing.mp4"}, "missing"),
        ({"label": "fridge"}, "model-safe"),
    ],
)
def test_manifest_rejections(tmp_path, video, change, error):
    r = Registry(tmp_path / "r.sqlite")
    r.ingest(manifest(tmp_path, [row(video)]))
    with pytest.raises((ValueError, FileNotFoundError)):
        r.ingest(manifest(tmp_path, [row(video, episode_id="ep-two", **change)]))
    assert len(r.episodes()) == 1
    r.close()


def test_duplicate_and_corrupt(tmp_path, video):
    r = Registry(tmp_path / "r.sqlite")
    with pytest.raises(ValueError, match="duplicate"):
        r.ingest(manifest(tmp_path, [row(video), row(video)]))
    video.write_bytes(b"not video")
    with pytest.raises(av.error.InvalidDataError):
        r.ingest(manifest(tmp_path, [row(video)]))
    assert r.episodes() == []
    r.close()
