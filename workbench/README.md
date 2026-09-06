# Timestamped video search

Local search over the 24-video VirtualHome household corpus. The implementation uses the 4-bit Qwen3-VL-Embedding model on MLX, explicitly in **pooled_images** mode. It encodes individual frames, averages their unit vectors, and normalizes again. This baseline discards frame order. Native-video encoding is rejected because the tested upstream embedding wrapper drops video pixels.

## Install and reproduce

Run commands from the repository root on Apple Silicon. This package has its own Python environment; it does not alter the simulator environment.

```sh
uv sync --project workbench --extra pooled-images --extra dev --locked
workbench/.venv/bin/python ttmp/2026/09/06/COSMOS-EMBED-001--embedding-runtime-baseline-on-mlx/scripts/03-download-pinned-model.py
workbench/.venv/bin/video-workbench ingest output/virtualhome-corpus/home-v1/inputs.jsonl
workbench/.venv/bin/video-workbench inspect
workbench/.venv/bin/pytest workbench/tests -q
```

The corpus must already exist. Follow [the corpus playbook](../docs/playbook/virtualhome-corpus.md) to generate it. Search uses recorded MP4 files and requires no running Unity simulator. Downloading the pinned checkpoint requires internet access; subsequent index and search operations use only local assets.

Build a chosen configuration and use the printed manifest path:

```sh
workbench/.venv/bin/video-workbench index --seconds 10 --fps 1
workbench/.venv/bin/video-workbench search 'A person opening the fridge door' --manifest output/video-workbench/indices/INDEX_ID/manifest.json --split train
workbench/.venv/bin/video-workbench serve --manifest output/video-workbench/indices/INDEX_ID/manifest.json
```

Open http://127.0.0.1:8767/. Click a ranked interval to seek to its beginning, then press Play. Playback pauses and clamps the displayed time at the interval end. Browser media timing is not a frame-accurate annotation tool. API documentation is at `/docs`; the server binds loopback and loads one immutable index. Stop it with Ctrl-C. Restart with another manifest to change indices.

`index` prints progress and then a JSON build summary; `output/video-workbench/last-build.json` holds the latest summary. Repeating an index build verifies and reuses cached frames. An interrupted feature write can leave unreferenced bytes; a subsequent build recomputes that uncommitted entry. A committed feature with a bad hash fails loudly. Preserve evidence and use a new `--root` if a cache is damaged; the implementation does not silently repair committed corruption.

## Evaluation

```sh
workbench/.venv/bin/video-workbench evaluate-retrieval
```

The committed protocol freezes six development settings, query text, weak relevance intervals, split groups, selection order, and random controls. It saves `selected.json` before ranking the test partition and writes a `test-started.json` marker. A second invocation against that same report directory refuses to overwrite the held-out run. To conduct a new experiment, version the protocol and use a new `--report-dir`; the original test partition is no longer pristine for exploratory retuning.

The serving manifest for the selected configuration is recorded in `output/video-workbench/evaluation-v1/serving-index.json`. Evaluation JSON contains per-query hit intervals and raw scores. `Success@K` asks whether any relevant interval was found. Interval Recall@K measures the fraction of distinct weak interiors covered. The relevance rule requires 50% interior coverage and favors long windows; a best-IoU diagnostic makes that tradeoff visible. Negative queries stay in the report with undefined positive-recall metrics and actual top scores. There is no calibrated abstention threshold.

## Read the implementation

- [registry.py](src/video_workbench/registry.py) validates a generic model-safe JSONL manifest and commits whole batches to schema-versioned SQLite.
- [media.py](src/video_workbench/media.py) decodes raw presentation timestamps and selects the first frame at or after each sampling-grid time inside a half-open interval.
- [embedding.py](src/video_workbench/embedding.py) pins preprocessing, prompt, model artifacts, runtime versions, normalization, and pooling in a feature-space hash.
- [index.py](src/video_workbench/index.py) owns frame caching, atomic publication, window pooling, immutable manifests, and exact cosine ranking.
- [api.py](src/video_workbench/api.py) validates requests, serializes model access, checks registry/index consistency, and serves registered videos with byte ranges.
- [viewer.html](src/video_workbench/viewer.html) renders results and source playback without a JavaScript build toolchain.
- [evaluation.py](src/video_workbench/evaluation.py) is the only application module that reads relevance labels. Inference modules never import it.

Model weights, source videos, caches, and local databases are ignored under `output/`. Code, locked dependencies, protocols, tickets, measured reports, and selected browser screenshots are committed. The ticket’s implementation report explains observed results and remaining limits.

## Observable-state experiment

The separate state CLI reuses frozen image embeddings and leaves native-video encoding independent:

```bash
python -m video_workbench.predicates encode --help
python -m video_workbench.predicates evaluate --help
python -m video_workbench.predicates serve --run output/state-workbench/run-v2 --port 8772
```

The first run is an exploratory negative result, with source-reviewed unknowns and apartment-separated data. See the [implementation and evidence report](../ttmp/2026/09/06/VIDEO-STATE-001--project-2-observable-state-recognition/reference/03-observable-state-baseline-implementation-and-evidence-report.md) for reproduction, exact metrics, screenshots, and the handoff to object detection/tracking/crops. Model predictions do not use reviewed visibility as an inference gate.


## Opt-in native video (MLX-VIDEO-FIX-001)

Native video uses the repaired fork at `6452614f6de04694d1e34fd13abaca11f6ffb994`, official Qwen weights at `9f2f7e710d6d81056aa5c0a4f04764fec6bb7bda`, FP32 inference, and pinned official Transformers preprocessing. It has a different feature space and clip cache. The community 4-bit checkpoint has not passed native-video acceptance.

Keep `workbench/.venv` for the existing pooled-image baseline. Install native requirements in a separate environment; never sync both runtime extras into one environment. The existing isolated repair environment is `output/mlx-video-fix/.venv`. For a fresh environment:

```sh
uv venv output/mlx-video-fix/.venv --python 3.11
uv pip install --python output/mlx-video-fix/.venv/bin/python -r workbench/native-video-requirements.txt -e 'workbench[native-video]'
```

The audited checkout may instead be installed editable with `uv pip install --python output/mlx-video-fix/.venv/bin/python --no-deps -e output/mlx-video-fix/mlx-vlm -e workbench` after installing the pinned runtime. Startup verifies the wrapper source hash and runtime versions; the feature identity includes the entire MLX Python source digest and model artifact hashes.

```sh
output/mlx-video-fix/.venv/bin/video-workbench index --mode native_video --splits development --seconds 2 --fps 2
output/mlx-video-fix/.venv/bin/video-workbench search --mode native_video 'A person closing the fridge door.' --manifest output/video-workbench-native/indices/INDEX_ID/manifest.json --split development
```

`--model` defaults to `output/mlx-video-fix/models/official` for native mode. Download exactly the official revision above if absent. Native defaults to `output/video-workbench-native`; pooled mode retains `output/video-workbench`. Actual selected PTS, relative to each clip, determine video timestamps. Single/odd inputs repeat the last frame and PTS; clips exceeding 32 selected frames fail clearly. Reduce FPS or window duration if needed.

Rollback is explicit: run `workbench/.venv/bin/video-workbench search --mode pooled_images ... --manifest OLD_POOLED_MANIFEST`. Existing indices and the baseline environment are retained. Loading a pooled index with the native query encoder, or vice versa, raises an incompatible-feature-space error. No native failure falls back to pooled images. The development smoke encoded nine clips from one episode and verified full cache reuse; this is not a corpus retrieval-quality acceptance.
