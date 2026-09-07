# Run the native FP32 TEMPORAL comparison

This playbook reproduces the VIDEO-TEMPORAL-001 native-feature experiment on this Mac: extract repaired native-video embeddings from the frozen VirtualHome-AIST windows, fit fresh ridge and causal TCN heads, and compare them with the preserved pooled results. Run commands from the repository root in the same terminal session.

The completed reference run is `output/temporal-native-fp32-v1`. The commands below use a **new** destination. They require existing local videos, dataset, model weights, and environments; cloning the repository alone does not restore ignored output artifacts.

## 1. Check prerequisites and choose a destination

Use the existing isolated environments:

| Operation | Interpreter | Hardware |
|---|---|---|
| Native extraction | `output/mlx-video-fix/.venv/bin/python` | Apple Silicon with accessible Metal GPU |
| Ridge, TCN, comparison | `workbench/perception-env/.venv/bin/python` | CPU |

The accepted adapter uses official FP32 weights at `output/mlx-video-fix/models/official`, official checkpoint revision `9f2f7e710d6d81056aa5c0a4f04764fec6bb7bda`, and repaired MLX-VLM commit `6452614f6de04694d1e34fd13abaca11f6ffb994`. Startup verifies runtime, processor, wrapper, and model identity. Do not replace these with the community four-bit checkpoint or mix native and pooled environments.

For environment restoration, see [native setup](../../workbench/README.md#opt-in-native-video-mlx-video-fix-001) and [CPU environment setup](../../workbench/perception-env/README.md). Those setup instructions are only needed if an environment is absent. Keep the existing pooled environment and artifacts intact.

```sh
export PYTHONPATH=workbench/src
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TEMPORAL_DATASET=output/temporal-v1/dataset
export TEMPORAL_POOLED=output/temporal-v1
export TEMPORAL_RUN=output/temporal-native-fp32-v2
```

Choose another unused run name if `v2` already exists. Run this preflight and **stop if it fails**:

```sh
python3 - <<'PY'
import hashlib
import json
import os
from pathlib import Path

root = Path(os.environ['TEMPORAL_DATASET'])
pooled = Path(os.environ['TEMPORAL_POOLED'])
run = Path(os.environ['TEMPORAL_RUN'])
assert not run.exists(), f'Choose a fresh run directory: {run}'
for name in (
    'output/mlx-video-fix/.venv/bin/python',
    'workbench/perception-env/.venv/bin/python',
    'output/mlx-video-fix/models/official/config.json',
):
    assert Path(name).is_file(), f'Missing prerequisite: {name}'
for name in ('linear-v1/results.json', 'tcn-v1/results.json',
             'pooled-features/manifest.json'):
    assert (pooled / name).is_file(), f'Missing pooled reference: {name}'
manifest = json.loads((root / 'manifest.json').read_text())
for name, key in [('inputs.json', 'inputs_sha256'),
                  ('weak-labels.json', 'labels_sha256')]:
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == manifest[key]
rows = json.loads((root / 'inputs.json').read_text())
assert len(rows) == 792, 'This playbook expects the frozen 792-window dataset'
assert len({r['episode_id'] for r in rows}) == 48
for video in {r['video'] for r in rows}:
    assert Path(video).is_file(), f'Missing source video: {video}'
print('Preflight passed: frozen dataset and local prerequisites available')
PY
```

This checks artifact presence and dataset integrity without loading the model. The producer additionally checks model/runtime identity and video hashes during extraction. Do not regenerate or relabel the dataset for this matched comparison.

## 2. Optional first-run pilot

Use the pilot when restoring the runtime or changing extraction code. It is unnecessary for every repeat of an already validated setup.

```sh
output/mlx-video-fix/.venv/bin/python \
  -m video_workbench.temporal.encode_native \
  "$TEMPORAL_DATASET" "$TEMPORAL_RUN/pilot" --limit 8
```

Expected: eight windows, covering one-, two-, three-, and four-frame inputs. The reference pilot took 8.7 seconds including loading. Inspect its manifest:

```sh
python3 - <<'PY'
import json, os
from pathlib import Path
m = json.loads((Path(os.environ['TEMPORAL_RUN']) / 'pilot/manifest.json').read_text())
assert m['status'] == 'pilot' and len(m['sample_ids']) == 8
assert m['pixel_probe']['max_abs_difference'] >= 1e-5
print(m['pixel_probe'])
print('seconds:', m['wall_seconds'])
PY
```

The black-pixel intervention checks that pixels affect the representation. It does not measure action recognition. The pilot cannot be used as the full training cache; the sequence loader rejects its incomplete sample population.

## 3. Extract all native FP32 windows

```sh
output/mlx-video-fix/.venv/bin/python \
  -m video_workbench.temporal.encode_native \
  "$TEMPORAL_DATASET" "$TEMPORAL_RUN/features"
```

The producer prints one progress line per episode. It audits actual selected frames and timestamps, then writes `features/features.npz` and `features/manifest.json` after extraction. A successful full manifest has `status: complete`, 792 sample IDs, and 48 source audits. Features are 2048-dimensional float32 unit vectors with a validity mask; the encoder never opens weak labels.

The reference extraction took **199 seconds**, including 5.9 seconds loading, with a peak MLX allocation of **9.61 GB**. These are measurements from one run on this shared Mac, not runtime guarantees. Avoid launching duplicate extraction jobs while waiting for progress.

## 4. Train fresh heads and compare

```sh
workbench/perception-env/.venv/bin/python \
  -m video_workbench.temporal.native_compare \
  "$TEMPORAL_DATASET" "$TEMPORAL_RUN" "$TEMPORAL_POOLED"
```

This fits ridge candidates and trains six TCN candidates: one/two layers crossed with seeds 7/17/27. It preserves the existing training policy, selects checkpoints and architecture on development data, and evaluates the selected models on the same test population as the pooled reference. The six reference training loops took about nine seconds; that excludes other orchestration work.

The runner requires complete native features and fresh `ridge`, `tcn`, and `comparison` subdirectories. It verifies paired episode/timestamp/target/mask identities and original artifact hashes. Actual trained TCN checkpoints must pass streaming-equivalence and future-perturbation checks. There is no fallback to pooled features and no reuse of pooled model weights.

## 5. Inspect and smoke-check the completed result

```sh
workbench/perception-env/.venv/bin/python - <<'PY'
import json, os
from pathlib import Path
from video_workbench.registry import file_hash
from video_workbench.temporal.benchmark import load_sequences

root = Path(os.environ['TEMPORAL_RUN'])
r = json.loads((root / 'comparison/results.json').read_text())
classes, sequences, _, fm = load_sequences(os.environ['TEMPORAL_DATASET'], root / 'features')
assert r['status'] == 'complete' and fm['status'] == 'complete'
assert len(sequences) == 48 and sum(len(s.features) for _, s in sequences) == 792
assert sum(int(s.loss_mask.sum()) for split, s in sequences if split == 'test') == 308
assert file_hash(root / 'features/manifest.json') == r['native_features_manifest_sha256']
for name, sha in r['native_results_sha256'].items():
    assert file_hash(root / name / 'results.json') == sha
for path, sha in r['original_hashes'].items():
    assert file_hash(path) == sha
training = json.loads((root / 'tcn/results.json').read_text())
assert len(training['candidates']) == 6
for candidate in training['candidates']:
    assert file_hash(root / 'tcn' / candidate['checkpoint']) == candidate['checkpoint_sha256']
for selected in training['selected_seed_results']:
    assert selected['chunk_max_abs_error'] <= 1e-4
    assert selected['future_max_abs_error'] <= 1e-6
print('Smoke passed: matched population, hashes, checkpoints, causal checks')
print('Ridge macro recall:', r['ridge']['pooled']['macro_recall'], '->', r['ridge']['native']['macro_recall'])
print('TCN mean macro recall:', r['tcn']['pooled_mean'], '->', r['tcn']['native_mean'])
print('TCN native seed standard deviation:', r['tcn']['native_std'])
print('Ridge corrected/worsened:', r['ridge']['paired']['counts'])
PY
```

| Artifact under the run directory | Contents |
|---|---|
| `features/manifest.json` | Runtime/model identity, source audits, timing, feature hash |
| `features/features.npz` | Native vectors and validity |
| `ridge/results.json` | Candidate selection, fitted weights, metrics and predictions |
| `tcn/results.json` | Six training traces, selected seeds, metrics and causal checks |
| `tcn/layers-*-seed-*.pt` | Six checkpoints tied to the native feature-space ID |
| `comparison/results.json` | Per-class and paired comparisons, source hashes |
| `comparison/macro-recall.svg` | Aggregate comparison figure; open in a browser |

The measured reference results are ridge macro recall **21.16% pooled → 24.55% native**, and TCN seed mean **18.63% → 24.31%**. Do not make these exact values acceptance assertions: inspect seed variability and per-class counts as well. Native TCN did not beat native ridge on mean macro recall. CLOSE, GRAB, PUTBACK, and TURNTO remained unresolved in the selected native heads.

This compares native FP32 with four-bit pooled features: preprocessing and precision change alongside representation. It does not isolate temporal ordering. Labels are weak program interiors; 249 of 308 test labels are WALK. Source-time availability also excludes actual extraction latency.

## Failure recovery

| Symptom | Action |
|---|---|
| `No Metal device available` | Run native extraction in a Mac session with GPU access; in Codex, request the authorized GPU execution outside the sandbox. Do not change model precision to work around this. |
| Runtime version, wrapper, processor, or artifact identity rejection | Restore the pinned isolated native environment and official model from the setup references. Keep acceptance checks enabled. |
| Missing videos or dataset files | Restore the original local experiment artifacts. Do not substitute a new corpus for a matched run. |
| Source hash, PTS, or row-identity mismatch | Stop and inspect the frozen artifacts and manifest references. Do not disable the audit or edit hashes to make it pass. |
| `new temporal feature directory required` | The feature destination exists. Inspect it or choose a fresh run name. |
| `fresh training and comparison destinations required` | One of the head/comparison outputs already exists, possibly from an interrupted run. There is no automatic resume. Preserve it and use a fresh run directory. |
| Training interrupted after successful extraction | To avoid re-extraction, create a new run directory and copy the completed `features/` directory unchanged into it; then run step 4 against that new root. Preserve the partial training output for inspection. |
| Native extraction interrupted | No per-window resumable cache is implemented. Preserve any partial output and rerun extraction to a fresh destination. |
| `complete native FP32 features required` or sample mismatch with eight rows | A pilot was supplied where the full feature cache is required. Complete step 3. |

For an existing successful run, set `TEMPORAL_RUN=output/temporal-native-fp32-v1` and run **only step 5** to inspect it. Do not execute the fresh-destination preflight or extraction/training steps against that completed run.

## Implementation and detailed findings

- [Native producer](../../workbench/src/video_workbench/temporal/encode_native.py)
- [Training and paired comparison runner](../../workbench/src/video_workbench/temporal/native_compare.py)
- [Accepted native adapter](../../workbench/src/video_workbench/native_video.py)
- [Measured report](../../ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/reference/06-native-fp32-temporal-benchmark-measured-findings.md)
- [Design](../../ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/design-doc/02-fp32-native-temporal-feature-comparison-design.md)

Native index/search is a separate retrieval workflow documented in the [workbench README](../../workbench/README.md#opt-in-native-video-mlx-video-fix-001); this playbook evaluates temporal heads on frozen windows.
