"""Evaluator-only weak-label joins. Model/cache modules never import this module."""

from pathlib import Path
import json
import time
import numpy as np
from .embedding import digest
from .index import Index, build, write_json, atomic_write
from .registry import file_hash


def interval_metrics(hits, relevant, k, coverage=0.5):
    if not relevant:
        return {
            "success": None,
            "interval_recall": None,
            "best_iou": None,
            "matched": 0,
            "relevant": 0,
        }
    matched = set()
    best_iou = 0.0
    for hit in hits[:k]:
        for i, truth in enumerate(relevant):
            if hit["episode_id"] != truth["episode_id"]:
                continue
            overlap = max(
                0,
                min(hit["end_us"], truth["end_us"])
                - max(hit["start_us"], truth["start_us"]),
            )
            duration = truth["end_us"] - truth["start_us"]
            if duration <= 0:
                raise ValueError("invalid relevance interval")
            if overlap / duration >= coverage:
                matched.add(i)
            union = hit["end_us"] - hit["start_us"] + duration - overlap
            best_iou = max(best_iou, overlap / union)
    return {
        "success": int(bool(matched)),
        "interval_recall": len(matched) / len(relevant),
        "best_iou": best_iou,
        "matched": len(matched),
        "relevant": len(relevant),
    }


def evaluate(index, queries, vectors, split, protocol):
    rows = []
    rng = np.random.default_rng(protocol["random_seed"])
    eligible = [c for c in index.manifest["chunks"] if c["split"] == split]
    for query, vector in zip(queries, vectors, strict=True):
        relevant = [r for r in query["relevant_interiors"] if r["split"] == split]
        started = time.perf_counter()
        hits = index.search(
            vector, index.manifest["space_id"], max(protocol["k"]), split
        )
        ranking_seconds = time.perf_counter() - started
        metrics = {
            str(k): interval_metrics(hits, relevant, k, protocol["coverage_threshold"])
            for k in protocol["k"]
        }
        random_scores = []
        if relevant:
            for _ in range(protocol["random_repeats"]):
                shuffled = [eligible[int(i)] for i in rng.permutation(len(eligible))]
                random_scores.append(
                    interval_metrics(
                        shuffled, relevant, 5, protocol["coverage_threshold"]
                    )
                )
        rows.append(
            {
                "query": query["query"],
                "quality": query["quality"],
                "metrics": metrics,
                "top_score": hits[0]["score"] if hits else None,
                "returned_hits": len(hits),
                "ranking_seconds": ranking_seconds,
                "hits": hits,
                "random_success_at_5": float(
                    np.mean([m["success"] for m in random_scores])
                )
                if random_scores
                else None,
                "random_interval_recall_at_5": float(
                    np.mean([m["interval_recall"] for m in random_scores])
                )
                if random_scores
                else None,
            }
        )
    positive = [r for r in rows if r["metrics"]["5"]["relevant"]]
    aggregate = {
        str(k): {
            key: float(np.mean([r["metrics"][str(k)][key] for r in positive]))
            if positive
            else None
            for key in ("success", "interval_recall", "best_iou")
        }
        for k in protocol["k"]
    }
    return {
        "split": split,
        "index_id": index.manifest["index_id"],
        "positive_queries": len(positive),
        "unsupported_queries": len(rows) - len(positive),
        "metrics": aggregate,
        "queries": rows,
        "random_success_at_5": float(
            np.mean([r["random_success_at_5"] for r in positive])
        )
        if positive
        else None,
        "random_interval_recall_at_5": float(
            np.mean([r["random_interval_recall_at_5"] for r in positive])
        )
        if positive
        else None,
    }


def run(
    registry, embedder, root, protocol_path, query_path, corpus_manifest, report_dir
):
    protocol = json.loads(Path(protocol_path).read_text())
    queries = json.loads(Path(query_path).read_text())
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    if (report_dir / "test-started.json").exists():
        raise ValueError(
            "test run already started; preserve this frozen run and use a new explicitly versioned protocol for further experiments"
        )
    if file_hash(query_path) != protocol["queries_sha256"]:
        raise ValueError("queries changed after freeze")
    if file_hash(corpus_manifest) != protocol["corpus_manifest_sha256"]:
        raise ValueError("corpus changed after freeze")
    for split, key in [("development", "development_groups"), ("test", "test_groups")]:
        episodes = registry.episodes(split)
        if sorted({e["split_group"] for e in episodes}) != protocol[key]:
            raise ValueError("evaluation group mismatch")
    lookup = {e["episode_id"]: e for e in registry.episodes()}
    declared = [
        json.loads(line)
        for line in Path(corpus_manifest).read_text().splitlines()
        if line.strip()
    ]
    if {r["episode_id"] for r in declared} != set(lookup):
        raise ValueError("registry episodes differ from frozen manifest")
    for row in declared:
        if any(
            lookup[row["episode_id"]][k] != row[k]
            for k in ("split", "split_group", "video_sha256")
        ):
            raise ValueError("registry source metadata differs from frozen manifest")
    for query in queries:
        for interval in query["relevant_interiors"]:
            e = lookup[interval["episode_id"]]
            if (
                interval["split"] != e["split"]
                or not 0
                <= interval["start_us"]
                < interval["end_us"]
                <= e["media"]["duration_us"]
            ):
                raise ValueError("invalid evaluator relevance")
    query_vectors = []
    query_seconds = []
    for q in queries:
        started = time.perf_counter()
        query_vectors.append(embedder.text(q["query"]))
        query_seconds.append(time.perf_counter() - started)
    query_vectors = np.stack(query_vectors)
    atomic_write(
        report_dir / "query-vectors.npy",
        lambda f: np.save(f, query_vectors, allow_pickle=False),
    )
    candidates = []
    for cfg in protocol["candidates"]:
        result = build(
            registry, embedder, root, cfg["seconds"], cfg["fps"], ("development",)
        )
        metrics = evaluate(
            Index(result["manifest"], embedder.space.id),
            queries,
            query_vectors,
            "development",
            protocol,
        )
        candidates.append(
            {"configuration": cfg, "build": result, "evaluation": metrics}
        )
        write_json(
            report_dir / "development.json",
            {"candidates": candidates, "protocol_sha256": file_hash(protocol_path)},
        )

    def key(candidate):
        m = candidate["evaluation"]["metrics"]["5"]
        cfg = candidate["configuration"]
        return (
            m["success"],
            m["interval_recall"],
            m["best_iou"],
            -cfg["seconds"],
            -cfg["fps"],
        )

    winner = max(candidates, key=key)
    frozen = {
        "configuration": winner["configuration"],
        "space_id": embedder.space.id,
        "protocol_sha256": file_hash(protocol_path),
        "queries_sha256": file_hash(query_path),
        "development_index_id": winner["build"]["index_id"],
        "development_report_sha256": file_hash(report_dir / "development.json"),
        "query_vectors_sha256": file_hash(report_dir / "query-vectors.npy"),
        "selection_rule": protocol["selection"],
    }
    write_json(
        report_dir / "selected.json", frozen
    )  # durable choice BEFORE any test ranking
    cfg = winner["configuration"]
    # An exclusive marker prevents accidentally retuning/rerunning this held-out report.
    with (report_dir / "test-started.json").open("x") as f:
        json.dump({"selection_sha256": file_hash(report_dir / "selected.json")}, f)
        f.flush()
        import os

        os.fsync(f.fileno())
    result = build(registry, embedder, root, cfg["seconds"], cfg["fps"], ("test",))
    test = evaluate(
        Index(result["manifest"], embedder.space.id),
        queries,
        query_vectors,
        "test",
        protocol,
    )
    import psutil

    test_report = {
        "selection": frozen,
        "build": result,
        "evaluation": test,
        "query_encode_seconds": query_seconds,
        "query_vectors_sha256": frozen["query_vectors_sha256"],
        "mlx_peak_bytes": embedder.mx.get_peak_memory(),
        "rss_bytes": psutil.Process().memory_info().rss,
        "limitations": protocol["limitations"],
    }
    write_json(report_dir / "test-report.json", test_report)
    # Serving index uses the already-frozen configuration for all registered sources.
    all_build = build(registry, embedder, root, cfg["seconds"], cfg["fps"])
    write_json(report_dir / "serving-index.json", all_build)
    return {
        "configuration": cfg,
        "test_metrics": test["metrics"],
        "report_dir": str(report_dir),
        "serving_manifest": all_build["manifest"],
    }
