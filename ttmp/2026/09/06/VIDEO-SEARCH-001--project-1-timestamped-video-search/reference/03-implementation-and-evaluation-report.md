---
Title: Implementation and evaluation report
Ticket: VIDEO-SEARCH-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://configs/retrieval/home-v1-protocol.json
      Note: Precommitted experiment protocol
    - Path: repo://workbench/README.md
      Note: Reproduction and operation commands
    - Path: repo://workbench/src/video_workbench/api.py
      Note: Typed search and registered media API
    - Path: repo://workbench/src/video_workbench/evaluation.py
      Note: Frozen selection and held-out measurement
    - Path: repo://workbench/src/video_workbench/index.py
      Note: Durable feature cache and exact ranking
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T14:00:49.686472-04:00
WhatFor: ""
WhenToUse: ""
---
# Implementation and evaluation report

## Outcome and scope

Project 1 now has a working local ingest/index/search application, typed HTTP API, browser video player, and a frozen retrieval evaluation. It runs on this Apple Silicon Mac using the existing 24-video VirtualHome corpus. Unity is not needed during search. The implementation resides in `workbench/`; the working simulator and corpus generator remain separate.

The measured model baseline is **pooled_images**, not native video. The tested MLX-VLM 0.6.17 Qwen embedding wrapper accepts arbitrary keyword arguments but does not forward `pixel_values_videos` into its visual encoder. The adapter therefore rejects native video explicitly. It encodes actual frames independently, averages their normalized vectors, and normalizes the result. This provides a truthful appearance-based search baseline while native-video repair remains separate work.

Engineering acceptance is complete for VIDEO-SEARCH-001: verified ingest, deterministic timestamps, recoverable features, exact ranking, typed API, real browser seeking, and held-out reporting. Model quality is limited. The final setting is 10-second windows at 1 FPS; held-out Success@5 is 75%, but random ranking achieves 74% on this tiny candidate pool. Low temporal overlap and failure on microwave closing mean this should be used to inspect coarse candidate evidence, not to decide procedural correctness.

## Start the application

From the repository root, use the exact frozen serving index:

```sh
workbench/.venv/bin/video-workbench serve \
  --manifest output/video-workbench/indices/e9ba74dabd6c07eafc1df2ee28c2b77a6f0235b87a7e7b3e0fff2e3df893bbce/manifest.json
```

Open http://127.0.0.1:8767/. The process binds loopback. Enter a query, choose a partition, and click a result to seek to its beginning. Press Play to inspect the source. The player pauses and clamps its displayed time at the interval end. This is browser playback, not a frame-accurate annotation instrument.

For installation, pinned model download, fresh indexing, CLI search, and evaluation commands, follow [workbench/README.md](../../../../../../workbench/README.md). The final serving manifest is also recorded in [serving-index.json](../various/evaluation/serving-index.json). Source videos, model weights, SQLite files, and caches live under ignored `output/`; the code, protocol, reports, and screenshots are tracked.

## How the implemented system fits together

```text
inputs.jsonl + MP4 bytes
          |
     Registry.ingest   -> SQLite episodes, source hashes, decoded PTS
          |
    deterministic half-open windows
          |
    select PTS grid -> decode selected RGB frames
          |
    QwenEmbedder.image -> unit 2048-dimensional vectors
          |
    FrameCache: atomic NPY publication -> committed SQLite metadata
          |
    mean(frame vectors) -> normalize -> immutable index matrix + manifest
                                                 |
query text -> same-space QwenEmbedder.text -> exact matrix @ query
                                                 |
                                  stable ranking + partition filter
                                                 |
                               typed hit -> browser source interval

frozen weak relevance -----------------> evaluator only
```

An intern should first read `registry.py` and `media.py`, then `embedding.py` and `index.py`. The HTTP layer is small because it delegates all ranking and integrity checks. `evaluation.py` is deliberately separate: inference modules never import it or read `labels.jsonl`, weak intervals, intended variants, or graph state.

The original guide proposed several separate modules and a SQL clip table. The implemented small-system layout consolidates sampling in `media.py`, and cache/ranking in `index.py`. Episode and frame-cache metadata use SQLite; complete clip metadata lives in immutable JSON index manifests alongside the matrix. This avoids another mutable clip-table publication boundary at the current scale. `PRAGMA user_version=1` versions the registry schema. Future schema changes must introduce a new migration rather than silently reinterpreting rows.

### Registry and time contract

A generic manifest row must contain exactly `episode_id`, `split`, `split_group`, `video`, and `video_sha256`. IDs are restricted to letters, numbers, underscore, and hyphen. Paths resolve under the manifest directory; escaping that root is rejected. Ingest checks duplicate IDs, source hashes, group ownership, identical videos crossing partitions, and every decoded timestamp. The incoming batch is all-or-nothing. A SQLite immediate transaction serializes validation and insertion so concurrent writers cannot validate against stale split ownership.

The registry stores the source path and checksum plus decoded media JSON: raw PTS values, stream time base, normalized microsecond timestamps, origin, duration, frame count, dimensions, variable-rate detection, and the final-frame duration source. Video access uses the registered ID and verifies the bytes again. An index cannot be served against a registry with different source or split metadata.

All requested clips use half-open integer-microsecond intervals. Sampling chooses the first frame at or after each requested grid time, deduplicates repeated selections, and excludes frames outside the interval. Generic variable-rate gaps can yield no frame; such windows are omitted. Last-frame duration prefers encoded duration and explicitly labels an estimate when needed. This prevents nominal-FPS arithmetic from silently shifting evidence.

```python
# Conceptual sampling and pooling, matching the implementation.
for start, end in windows(duration_us, seconds):
    ids = first_pts_at_or_after_grid(pts_us, start, end, fps)
    if not ids:
        continue
    frame_vectors = [cache_or_encode(video_hash, raw_pts[i], frame[i]) for i in ids]
    clip_vector = l2_normalize(mean(frame_vectors))
    store_clip(start, end, actual_selected_pts=pts_us[ids], vector=clip_vector)
```

### Model and feature-space contract

The checkpoint is `arthurcollet/Qwen3-VL-Embedding-2B-mlx-4bit`, revision `99b57b385f543a94c46d9f8e85a354de4c836b37`. Weight, tokenizer, chat-template, and processor bytes are hashed. The community model card has conflicting base-model lineage metadata; this report records the exact artifact rather than asserting independently verified conversion provenance.

`QwenEmbedder` loads the embedding model class through an in-memory `config_overrides={"model_type": "qwen3_vl_embedding"}`. It does not edit downloaded configuration files. The prompt uses the checkpoint chat template, the system instruction “Represent the user's input.”, and an assistant generation prefix. Image inputs are RGB, resized to 320×240 with Pillow bicubic, then passed through the hashed model processor. The encoder pools the last nonpadding token. It resets cached rotary-position state between independent samples and materializes MLX output before timing or conversion to NumPy.

`FeatureSpace.id` hashes weights/config identities, model revision, explicit mode, adapter version, prompt, resize, pooling, dimensions, dtype, normalization, sampling policy, and installed runtime versions. Final versions include MLX 0.32.2, MLX-VLM 0.6.17, Transformers 5.16.1, NumPy 2.4.6, Pillow 12.3.0, and PyAV 17.1.0. The complete environment is locked in `workbench/uv.lock`. Search rejects a query whose space ID differs from the index even when both vectors have 2048 dimensions.

The final runtime smoke produced finite unit vectors, exact same-image repetition, adjacent-frame cosine 0.9634, and black-frame cosine 0.3662. These controls establish pixel sensitivity and repeatability for this fixture. They do not establish semantic accuracy or native-video support. See [runtime-final-smoke.json](../../COSMOS-EMBED-001--embedding-runtime-baseline-on-mlx/various/runtime-final-smoke.json).

### Durable cache and exact ranking

Frame keys identify the feature space, source hash, raw PTS, time base, origin, and normalized PTS. A cache write creates a temporary NPY, flushes and fsyncs it, atomically renames it, then commits its checksum row. A crash before row commit leaves an orphan that is recomputed on resume. Committed corrupt bytes are rejected. A filesystem lock enforces one index writer.

Each completed index freezes ordered chunks, source/split identities, selected PTS, producer source-file hashes, sampling parameters, feature-space ID, matrix shape, and matrix checksum. The matrix is float32 and row-normalized. Rebuilding an already published identity verifies the existing matrix and refuses to change its contents. The API opens it read-only through NumPy memory mapping.

Ranking is exact cosine similarity: `scores = X @ q`. Results sort by descending score and then chunk ID, providing deterministic ties. Partition filtering occurs before selecting top K. There is no approximate search, reranking, learned score calibration, or overlap suppression. The small corpus does not require a vector database.

## API reference and browser evidence

| Route | Contract |
|---|---|
| `POST /v1/search` | JSON `query`, optional loaded `index_id`, optional `split`, `top_k` in 1–100. Unknown fields rejected. |
| `GET /v1/index` | Loaded immutable index identity, feature space, window/FPS parameters, matrix shape, partitions. |
| `GET /v1/episodes/{episode_id}/video` | Registered, checksum-verified MP4 only; supports HTTP byte ranges. |
| `/docs`, `/openapi.json` | Generated API schema and interactive reference. |

A hit contains episode/chunk IDs, rank, split/group, requested start/end microseconds, actual selected PTS, raw cosine score, feature-space ID, and registered video URL. Search calls serialize model access because the underlying model carries cached state. Empty valid partitions return an empty hit list; malformed requests are errors.

[The initial search screenshot](../various/screenshots/02-first-search-and-seek.png) shows a training query with source playback at 5.0 seconds and timestamp evidence. The browser reported readyState 4 and decoded 640×480 video. The first coarse `timeupdate` stop overshot 10 seconds by 245ms; animation-frame checks and clamping corrected the observed displayed endpoint to exactly 10.0 seconds.

[The final selected-index screenshot](../various/screenshots/03-selected-index-test-playback.png) shows the held-out query after the frozen evaluation had already completed. The top interval is 10–20 seconds in `ep-d9e2a612fb2342e2`, sought to exactly 10 seconds; the source duration is 24 seconds. The response took 0.09 seconds in this browser observation. This later UI inspection did not change parameters or rerun the held-out aggregate evaluation.

## Frozen development selection

Protocol and evaluator were committed as `aeeaa30` before the sweep. Development is g03; test is g04. Training groups were used for engineering smoke checks. The test partition had not been ranked during configuration selection. The evaluator saves and hashes the selected configuration before writing an exclusive test-start marker and computing test metrics.

A hit is relevant when it belongs to the correct episode and covers at least half of a weak action interior. `Success@K` means any relevant interval is found. Interval Recall@K counts distinct matched interiors divided by the query's relevant interiors; repeated hits do not count twice. Reported aggregates are macro means across four positive query families. The IoU diagnostic is the mean of each query's best hit–truth temporal IoU within top K. Negative controls remain in the report with undefined positive-recall metrics.

| Window / FPS | Dev Success@5 | Dev interval Recall@5 | Dev best IoU@5 |
|---|---:|---:|---:|
| 2s / 1 | 25% | 6.25% | 0.098 |
| 2s / 2 | 50% | 25% | 0.300 |
| 5s / 1 | 50% | 25% | 0.120 |
| 5s / 2 | 50% | 31.25% | 0.120 |
| 10s / 1 | 75% | 50% | 0.090 |
| 10s / 2 | 75% | 50% | 0.090 |

The fixed selection order was Success@5, interval Recall@5, best IoU@5, then smaller window and FPS. The two ten-second settings tied on metrics, so 1 FPS won. Shorter windows had better localization in one condition, but the precommitted primary metric selected the long windows. This is a reported tradeoff, not grounds for retuning on test.

## Held-out result and interpretation

| K | Success@K | Macro interval Recall@K | Mean best IoU@K |
|---|---:|---:|---:|
| 1 | 25% | 6.25% | 0.030 |
| 5 | 75% | 68.75% | 0.095 |
| 10 | 100% | 100% | 0.114 |

At K=5 the fridge opening/closing queries covered all their weak interiors, microwave opening covered three of four, and microwave closing covered none. Across queries that is nine of twelve interiors; the micro average would be 75%, distinct from the reported 68.75% macro average.

Random ranking over 14 held-out windows, using seed 42 and 100 permutations per positive query, achieved 74% Success@5 and 34.81% macro interval Recall@5. The model retrieves more relevant intervals on this fixture, but its success rate is essentially the random baseline. Looking at ten of fourteen windows makes Success@10 a particularly weak quality claim. Low IoU confirms that long-window coverage does not establish precise localization.

The negative queries “A dog running outside in a garden” and “A person watering houseplants” scored 0.0618 and 0.1523 at the top, respectively. They still returned candidates: this system has no fitted abstention threshold. Two low-scoring negatives are insufficient to calibrate one. All six queries and top-ten hits are preserved in [test-report.json](../various/evaluation/test-report.json).

The full within-scene corpus is only 426.1 seconds, one apartment, one character, and four action query families. Weak program interiors are not reviewed dense visual labels. Mean pooling erases ordering, so an opening and closing sequence can have similar appearance. The appropriate next work is better temporal visual evidence and reviewed labels, not claiming production-quality procedural recognition from these scores.

## Runtime and artifact sizes

- Initial engineering build: 861 frames at 2 FPS, 95 five-second windows, 134.37 seconds excluding model loading, 778,368-byte matrix. This is about 0.315× corpus duration.
- Verified reuse build: zero new encodes, all 861 frames reused, 0.124 seconds excluding model loading.
- Selected serving index: 55 windows across 24 videos, 434 sampled frames at 1 FPS, 450,688-byte matrix. The final all-partition build reused 217 frames and encoded 217 training frames in 36.84 seconds.
- Held-out index: 14 windows, 110 new frames, 18.43 seconds. These cache-aware build times are not independent cold benchmarks of each configuration.
- Evaluation query encodes: first call 0.746 seconds; subsequent calls about 0.027–0.036 seconds. MLX output was materialized before stopping the timer.
- Measured peak MLX allocation: 2.152 GB; evaluator RSS: 2.226 GB. The separate final smoke loaded the model in 2.52 seconds. Timings are local observations, not a controlled machine-wide performance study.

## Validation and handoff to the next project

Fifteen automated tests pass. They cover vector invariants, feature identity, VFR decode/sampling, corruption and missing files, idempotent/atomic ingest, split leakage, interrupted cache publication, immutable index compatibility, stable ranking, typed API validation, byte ranges, source tampering, weak-interval metrics, selection-before-test ordering, and repeat-test rejection. Two upstream Starlette TestClient deprecation warnings remain. Browser evidence independently confirms actual decoding, seeking, and endpoint behavior.

Project 2 can reuse `Registry`, `media.probe`, `selected_indices`, `decode_selected`, `FeatureSpace`, `FrameCache`, and the explicit pooled-image adapter. Preserve raw PTS and source identities when producing new state features. Do not reinterpret these weak retrieval interiors as dense state supervision. Any future native-video adapter must have a distinct feature-space identity and fresh capability controls.

The embedding prerequisite has been implemented only as far as required for this baseline. Broader cold/warm profiling, detailed preprocessing/inference separation, reversed-video controls, and native-video support remain open in COSMOS-EMBED-001 or its native-video repair follow-up. VIDEO-SEARCH-001 is complete within its explicitly documented pooled-image scope.

### Evidence and review order

1. [Frozen protocol](../../../../../../configs/retrieval/home-v1-protocol.json), [development selection](../various/evaluation/selected.json), and [held-out measurements](../various/evaluation/test-report.json).
2. [Evaluation screenshot](../various/screenshots/04-frozen-evaluation-report.png) and [final playback screenshot](../various/screenshots/03-selected-index-test-playback.png).
3. [Implementation diary](02-implementation-diary.md) for commands, failures, and milestone commits.
4. [Workbench source and reproduction instructions](../../../../../../workbench/README.md).

Primary runtime references inspected during implementation: the [official Qwen embedding script](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B/raw/main/scripts/qwen3_vl_embedding.py), the [pinned community checkpoint](https://huggingface.co/arthurcollet/Qwen3-VL-Embedding-2B-mlx-4bit/tree/99b57b385f543a94c46d9f8e85a354de4c836b37), and installed MLX-VLM 0.6.17 `encoder_loader.py`, `models/qwen3_vl_embedding/qwen3_vl_embedding.py`, and `models/qwen3_vl/qwen3_vl.py`. Runtime signatures in this report describe the installed source, not inferred support from a model name.
