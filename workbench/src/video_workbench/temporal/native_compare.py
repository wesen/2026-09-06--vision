"""Train unchanged heads on native features and compare matched frozen results.

python -m video_workbench.temporal.native_compare DATASET NATIVE_ROOT POOLED_ROOT
"""

import argparse
import json
from pathlib import Path

from video_workbench.registry import file_hash
from video_workbench.perception.store import write_json
from . import benchmark, train


def paired(old, new):
    """Require identical supervised populations before counting changed outcomes."""
    if set(old["episodes"]) != set(new["episodes"]):
        raise ValueError("episode population mismatch")
    counts = dict(both_correct=0, native_corrected=0, native_worsened=0, both_wrong=0)
    changes = []
    for eid, a in old["episodes"].items():
        b = new["episodes"][eid]
        for field in ("targets", "label_mask", "end_us"):
            if a[field] != b[field]:
                raise ValueError(f"paired {field} mismatch: {eid}")
        av = a.get("valid", [True] * len(a["targets"]))
        bv = b.get("valid", [True] * len(b["targets"]))
        if av != bv or len(a["predictions"]) != len(b["predictions"]):
            raise ValueError("validity or prediction count mismatch")
        for i, (target, mask, valid) in enumerate(
            zip(a["targets"], a["label_mask"], av)
        ):
            if not mask or not valid:
                continue
            p, q = a["predictions"][i], b["predictions"][i]
            key = (
                ("both_correct" if q == target else "native_worsened")
                if p == target
                else ("native_corrected" if q == target else "both_wrong")
            )
            counts[key] += 1
            if p != q:
                changes.append(
                    dict(
                        episode_id=eid,
                        end_us=a["end_us"][i],
                        target=target,
                        pooled=p,
                        native=q,
                    )
                )
    if sum(counts.values()) != old["n"] or old["n"] != new["n"]:
        raise ValueError("paired supervision count mismatch")
    return dict(counts=counts, changed_predictions=changes)


def compact(metrics):
    return {k: v for k, v in metrics.items() if k != "episodes"}


def run(dataset, native_root, pooled_root):
    root, pooled = Path(native_root), Path(pooled_root)
    if any((root / name).exists() for name in ("ridge", "tcn", "comparison")):
        raise ValueError("fresh training and comparison destinations required")
    fm = json.loads((root / "features/manifest.json").read_text())
    if (
        fm["status"] != "complete"
        or fm["spec"]["mode"] != "dense-trailing-native-video-fp32"
    ):
        raise ValueError("complete native FP32 features required")
    sources = [
        pooled / "linear-v1/results.json",
        pooled / "tcn-v1/results.json",
        pooled / "pooled-features/manifest.json",
    ]
    hashes = {str(p): file_hash(p) for p in sources}
    old_ridge, old_tcn, old_fm = [json.loads(p.read_text()) for p in sources]
    if fm["sample_ids"] != old_fm["sample_ids"]:
        raise ValueError("native and pooled window identities differ")
    dm = json.loads((Path(dataset) / "manifest.json").read_text())
    if old_ridge["classes"] != dm["classes"]:
        raise ValueError("class-index mapping mismatch")
    for old in (old_ridge, old_tcn):
        for key in ("inputs_sha256", "labels_sha256"):
            if old[key] != dm[key]:
                raise ValueError(f"frozen {key} mismatch")
    ridge = benchmark.run(dataset, root / "features", root / "ridge")
    tcn = train.run(dataset, root / "features", root / "tcn")
    tcn["kind"] = "weak-label frozen native FP32 video-feature causal TCN"
    tcn["report_annotation"] = (
        "Representation description corrected by native_compare; training algorithm unchanged."
    )
    write_json(root / "tcn/results.json", tcn)
    for old, new in ((old_ridge, ridge), (old_tcn, tcn)):
        for key in ("inputs_sha256", "labels_sha256"):
            if old[key] != new[key]:
                raise ValueError(f"frozen {key} mismatch")
    old_by_seed = {r["seed"]: r for r in old_tcn["selected_seed_results"]}
    comparisons = []
    for r in tcn["selected_seed_results"]:
        old = old_by_seed[r["seed"]]
        comparisons.append(
            dict(
                seed=r["seed"],
                pooled=compact(old["metrics"]["test"]),
                native=compact(r["metrics"]["test"]),
                paired=paired(old["metrics"]["test"], r["metrics"]["test"]),
                chunk_max_abs_error=r["chunk_max_abs_error"],
                future_max_abs_error=r["future_max_abs_error"],
            )
        )
    if any(file_hash(p) != hashes[str(p)] for p in sources):
        raise ValueError("pooled source changed during comparison")
    report = dict(
        status="complete",
        classes=ridge["classes"],
        original_hashes=hashes,
        native_features_manifest_sha256=file_hash(root / "features/manifest.json"),
        native_results_sha256={
            name: file_hash(root / name / "results.json") for name in ("ridge", "tcn")
        },
        comparison_code_sha256=file_hash(Path(__file__)),
        extraction={
            k: fm[k]
            for k in (
                "wall_seconds",
                "load_seconds",
                "peak_mlx_bytes",
                "max_rss_bytes_macos",
                "pixel_probe",
            )
        },
        sample_count=len(fm["sample_ids"]),
        ridge=dict(
            pooled=compact(old_ridge["metrics"]["test"]),
            native=compact(ridge["metrics"]["test"]),
            paired=paired(old_ridge["metrics"]["test"], ridge["metrics"]["test"]),
            pooled_selected_ridge=old_ridge["selected_ridge"],
            native_selected_ridge=ridge["selected_ridge"],
        ),
        tcn=dict(
            pooled_mean=old_tcn["test_macro_recall_mean"],
            native_mean=tcn["test_macro_recall_mean"],
            pooled_std=old_tcn["test_macro_recall_std"],
            native_std=tcn["test_macro_recall_std"],
            pooled_layers=old_tcn["selected_layers"],
            native_layers=tcn["selected_layers"],
            seeds=comparisons,
        ),
        limitation="Native FP32 versus four-bit pooled changes precision and preprocessing as well as representation. Weak labels, overlapping windows, small within-scene corpus; no independent-window significance claim.",
    )
    destination = root / "comparison"
    destination.mkdir()
    write_json(destination / "results.json", report)
    bars = [
        ("Pooled ridge", report["ridge"]["pooled"]["macro_recall"]),
        ("Native FP32 ridge", report["ridge"]["native"]["macro_recall"]),
        ("Pooled TCN (3 seeds)", report["tcn"]["pooled_mean"]),
        ("Native FP32 TCN (3 seeds)", report["tcn"]["native_mean"]),
    ]
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="330" viewBox="0 0 900 330">',
        '<rect width="900" height="330" fill="white"/>',
        '<g font-family="sans-serif" fill="#171717"><text x="25" y="35" font-size="22">Frozen TEMPORAL: test macro recall</text>',
    ]
    for i, (label, value) in enumerate(bars):
        y = 65 + i * 49
        svg += [
            f'<text x="25" y="{y + 23}" font-size="16">{label}</text>',
            f'<rect x="280" y="{y}" width="{value * 520:.2f}" height="30" fill="{"#245b82" if "Native" in label else "#777"}"/>',
            f'<text x="{290 + value * 520:.2f}" y="{y + 22}" font-size="16">{100 * value:.2f}%</text>',
        ]
    svg += [
        '<text x="25" y="285" font-size="14">308 weak test labels; 249 WALK. Bar scale: 520 px = 100%.</text>',
        '<text x="25" y="310" font-size="14">System comparison: precision and preprocessing also differ. TCN bars show seed means.</text></g></svg>',
    ]
    (destination / "macro-recall.svg").write_text("\n".join(svg))
    print(json.dumps({k: report[k] for k in ("extraction", "sample_count")}, indent=2))
    print("ridge macro:", bars[:2], "TCN macro:", bars[2:])
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dataset")
    p.add_argument("native_root")
    p.add_argument("pooled_root")
    args = p.parse_args()
    run(args.dataset, args.native_root, args.pooled_root)
