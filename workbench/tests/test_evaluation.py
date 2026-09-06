from video_workbench.evaluation import interval_metrics


def test_interval_coverage_is_not_query_success_or_iou():
    relevant = [
        dict(episode_id="a", start_us=10, end_us=20),
        dict(episode_id="b", start_us=10, end_us=20),
    ]
    hits = [
        dict(episode_id="a", start_us=15, end_us=25),
        dict(episode_id="a", start_us=10, end_us=20),
    ]
    first = interval_metrics(hits, relevant, 1)
    assert first["success"] == 1 and first["interval_recall"] == 0.5
    assert first["best_iou"] == 1 / 3
    both = interval_metrics(hits, relevant, 2)
    assert both["matched"] == 1 and both["interval_recall"] == 0.5
    assert interval_metrics([], [], 5)["success"] is None
    assert (
        interval_metrics([dict(episode_id="a", start_us=20, end_us=30)], relevant, 1)[
            "success"
        ]
        == 0
    )


def test_frozen_selection_precedes_test_and_prevents_retest(tmp_path, monkeypatch):
    import json
    import numpy as np
    import pytest
    from types import SimpleNamespace
    from video_workbench import evaluation as mod
    from video_workbench.registry import file_hash

    rows = [
        dict(
            episode_id="dev",
            split="development",
            split_group="g03",
            video_sha256="a",
            media={"duration_us": 100},
        ),
        dict(
            episode_id="test",
            split="test",
            split_group="g04",
            video_sha256="b",
            media={"duration_us": 100},
        ),
    ]
    registry = SimpleNamespace(
        episodes=lambda split=None: [
            r for r in rows if split is None or r["split"] == split
        ]
    )
    corpus = tmp_path / "inputs.jsonl"
    corpus.write_text("\n".join(json.dumps(r) for r in rows))
    queries = tmp_path / "queries.json"
    queries.write_text(
        json.dumps([dict(query="open", quality="weak", relevant_interiors=[])])
    )
    protocol = tmp_path / "protocol.json"
    protocol.write_text(
        json.dumps(
            dict(
                queries_sha256=file_hash(queries),
                corpus_manifest_sha256=file_hash(corpus),
                development_groups=["g03"],
                test_groups=["g04"],
                candidates=[dict(seconds=2, fps=1), dict(seconds=5, fps=1)],
                selection=["success"],
                limitations=["fixture"],
            )
        )
    )
    report = tmp_path / "report"
    calls = []
    monkeypatch.setattr(
        mod, "build", lambda *a, **k: dict(manifest="unused", index_id="id")
    )
    monkeypatch.setattr(mod, "Index", lambda *a: None)

    def evaluate(index, queries, vectors, split, protocol):
        calls.append(split)
        if split == "test":
            assert (report / "selected.json").exists()
        return {
            "metrics": {"5": {"success": 1, "interval_recall": 0.5, "best_iou": 0.2}}
        }

    monkeypatch.setattr(mod, "evaluate", evaluate)
    e = SimpleNamespace(
        text=lambda q: np.ones(3),
        space=SimpleNamespace(id="space"),
        mx=SimpleNamespace(get_peak_memory=lambda: 0),
    )
    mod.run(registry, e, tmp_path, protocol, queries, corpus, report)
    assert calls == ["development", "development", "test"]
    assert (
        json.loads((report / "selected.json").read_text())["configuration"]["seconds"]
        == 2
    )
    with pytest.raises(ValueError, match="already started"):
        mod.run(registry, e, tmp_path, protocol, queries, corpus, report)
