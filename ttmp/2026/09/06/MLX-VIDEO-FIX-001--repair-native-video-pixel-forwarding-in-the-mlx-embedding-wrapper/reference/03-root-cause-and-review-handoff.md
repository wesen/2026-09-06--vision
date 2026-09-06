---
Title: Native video root cause and review handoff
Ticket: MLX-VIDEO-FIX-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://output/mlx-video-fix/mlx-vlm/mlx_vlm/models/qwen3_vl_embedding/qwen3_vl_embedding.py
      Note: Repaired pixel forwarding and request-local positions at 6452614
    - Path: repo://output/mlx-video-fix/mlx-vlm/mlx_vlm/tests/test_qwen3_vl_embedding_video.py
      Note: Synthetic regression coverage
    - Path: repo://workbench/src/video_workbench/native_video.py
      Note: Accepted application contract
ExternalSources:
    - https://github.com/wesen/mlx-vlm/tree/fix/qwen3-vl-video-embeddings
Summary: Two repaired wrapper defects, controlled reference evidence, and opt-in workbench delivery.
LastUpdated: 2026-09-06T16:29:00-04:00
WhatFor: Human review of the repair and integration
WhenToUse: Before adopting or proposing the repair upstream
---


# Review handoff

The repair is on [wesen/mlx-vlm, fix/qwen3-vl-video-embeddings](https://github.com/wesen/mlx-vlm/tree/fix/qwen3-vl-video-embeddings) at `6452614f6de04694d1e34fd13abaca11f6ffb994`. The fork branch has been pushed. No issue or pull request has been created; the user requested personal review before any upstream submission.

The workbench integration and investigation artifacts are separate commits in this workspace: `ade0f2b` preserves the ticket and fresh audit, `1effb65` establishes P3 reference acceptance, and `127921a` integrates the accepted native path. They are not part of the MLX-VLM fork patch series.

## Root cause 1: Video pixels were silently omitted

`Model.__call__` accepted arbitrary keyword arguments, so the caller could supply `pixel_values_videos` without a signature error. The wrapper called `_last_hidden_state` without that argument, and the helper did not expose it. Consequently `get_input_embeddings` received video grid/token metadata but no video pixels and did not select its video vision branch. The language model could still produce a finite vector from token and timestamp content.

The original four-frame intervention held token IDs, masks and grids constant while replacing all video pixels with black. Both calls returned the same vector and invoked the vision tower zero times. This is a demonstrated silent-data-loss defect for that fixture, not a universal assertion about all possible malformed video calls.

Commit `05432ac` adds failing public-call-to-helper and helper-to-backbone sentinel regressions. Commit `d26804d` adds an explicit optional video-pixel parameter at both boundaries, forwards it through the video argument, and requires matching pixels/grids for each modality. Existing positional argument order is preserved. Image pixels remain in the image argument, and mixed visual features retain deepstack information.

After forwarding, that same historical community-checkpoint fixture invoked the vision tower and original/black cosine changed from approximately 1 to 0.518210. This proves restored visual computation. It does not establish official numerical parity or semantic action accuracy by itself.

## Root cause 2: Cached positions leaked between embedding requests

The helper independently managed generation-related cached position state despite the backbone already producing current-request positions. A text query after video could reuse an incompatible positional prefix. The forwarding-only real request-order probe showed text drift as large as 0.35791016 per coordinate, with cosine 0.615845 after mixed media.

Commit `6452614` uses `InputEmbeddingsFeatures.position_ids` from the current backbone result. The embedding call retains `cache=None`, existing causal/padding masks and deepstack inputs. It no longer derives positions from the preceding request's generation state. This removes duplicated positional logic without changing shared generation behavior.

The same commit checks pooling mask shape and rejects all-padding requests. Tiny-model tests cover left/right padding, text batch/individual agreement, video pixel dependence, and text after video. Historical eleven-case mixed-order measurements exactly match fresh-instance references after the repair. Fresh resume tests reconfirm the structural suite, and P3/P4 additionally compare official-reference and long-lived-adapter outputs.

## What the numerical evidence accepts

Eight official-source FP32 cases pass exact positions, every visual/deepstack/pooled intermediate, and unit-vector tolerances. Observed maximum embedding difference is 2.83123e-6; maximum intermediate difference is 8.60214e-4. The accepted processor is pinned Transformers 5.16.1 with official checkpoint artifacts. See [the complete parity findings](02-parity-findings.md), [policy](../various/audit-policy.json), and [gate results](../various/audit-gates.json).

Independent MLX preprocessing is not interchangeable with that contract: it removes outer video delimiters, and its timestamp handling differs for repeated final frames. Token-only interventions explain most vector drift; resizing contributes much less. This discrepancy is documented separately and is not hidden behind a relaxed wrapper tolerance.

Controlled all-eligible-layer affine four-bit quantization and the community four-bit checkpoint both show substantial vector and ranking drift. The latter also has distinct tokenizer/config artifacts. Neither is accepted for native rollout. FP32 implementation parity is a different claim from approximate quantized retrieval quality.

## Workbench integration

`--mode native_video` selects official FP32 weights and the repaired wrapper in the separate native environment. Default mode remains `pooled_images`. Runtime dependencies use mutually exclusive extras because the repaired checkout reports `0.7.0rc0`, while the baseline remains pinned to `0.6.17`.

Native feature identity includes model/config/tokenizer artifact hashes, repaired wrapper hash, all MLX Python source hashes, native adapter source hash, runtime versions, official processor identity, last-token pooling, normalization and PTS policy. Native caches complete clip embeddings under `clips/SPACE_ID`; pooled frame caches remain under `frames/SPACE_ID`. Index/query space mismatch fails explicitly.

Actual sampled PTS relative to the clip determine timestamps. Single/odd clips repeat the last frame and its PTS before processing. More than 32 selected frames fails clearly. Inference must return a valid unit vector before cache publication, and index manifests/latest-build pointers are published only after the full build succeeds.

Nine clips from development episode `ep-368d6331fc690a2c` were encoded into `output/mlx-video-fix/workbench-native-smoke`, then all nine were reused. Final native space: `2610572d944abb10b0366c2b00aaf87e701b6f6bb6656b022eca66dd230edecd`. Final manifest and measurements are in [native-integration.json](../various/native-integration.json). The parent registry was read-only; corpus/perception work was excluded from these changes.

Rollback: use `workbench/.venv/bin/video-workbench ... --mode pooled_images` with an existing pooled manifest. The original `embedding.py`, baseline environment, and cached frame/index artifacts are retained. See [workbench instructions](../../../../../../workbench/README.md) for installation and native invocation.

## Performance and limits

Materialized FP32 model inference on the fixed four-frame case was about 0.201 s warm, with a 9.545 GB MLX process peak including diagnostic passes. Full adapter fresh-process runs varied: 0.324–2.578 s for first inference including preprocessing and 0.207–0.371 s warm. Model loading took 5.435–6.562 s in those adapter runs. Filesystem caches were warm and the machine was shared with concurrent work; these are observations, not isolated latency guarantees. MLX allocation and process RSS are different metrics and both are recorded.

The test corpus is deliberately small and development-only. Order sensitivity does not establish correct temporal action classification; the contact sheet shows an opening sequence despite the diagnostic query saying closing. No claim is made that native retrieval outperforms the existing pooled baseline, and no held-out corpus results were used to choose tolerances. Image/text batching is tested at the wrapper level; the workbench adapter intentionally handles one request at a time.

## Human review order

1. Review fork commits `05432ac`, `d26804d`, and `6452614` in sequence. Only the embedding wrapper and synthetic test file change.
2. Read parity findings and inspect token/pixel interventions, exact-position checks, precision tables and ranking drift.
3. Review `native_video.py`, `native_index.py`, the CLI switch, dependency extras/lockfile, and native contract tests in workspace commit `127921a`.
4. Use the portable patches and local review notes under `various/upstream-package/`. They apply to the recorded current upstream base `d5064772dcd1e31704604f93a873323505ae70d5` and reproduce the repaired tree.
5. Decide personally whether and how to propose this upstream. No submission is pending or automatically scheduled.
