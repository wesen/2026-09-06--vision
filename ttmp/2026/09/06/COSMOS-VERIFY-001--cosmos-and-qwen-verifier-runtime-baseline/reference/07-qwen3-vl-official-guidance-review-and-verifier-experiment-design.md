---
Title: Qwen3-VL official guidance review and verifier experiment design
Ticket: COSMOS-VERIFY-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/sources/qwen3-vl/local-runtime-audit.json
      Note: Installed MLX default evidence
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/sources/qwen3-vl/provenance.json
      Note: Immutable primary-source identities
    - Path: repo://workbench/src/video_workbench/verifiers/worker.py
      Note: Actual verifier generation settings
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T22:07:27.797595-04:00
WhatFor: ""
WhenToUse: ""
---


# Qwen3-VL guidance: what to change and what to measure

Qwen3-VL is relevant to this system in two separate roles. Our generative verifier uses an MLX conversion of Qwen3-VL-8B-Instruct. The temporal pipeline uses the separately trained Qwen3-VL-Embedding-2B model through the accepted native FP32 adapter. Sharing an architectural family does not make their output spaces or evaluation protocols interchangeable. This review concerns the generative verifier; the larger embedding experiment remains deferred.

The most consequential finding is that Qwen3-VL has separate Instruct and Thinking checkpoints. Testing a longer explanation from our current Instruct checkpoint would not test Qwen3-VL-8B-Thinking. This differs from the Cosmos prompt experiment described in reference 06: a Qwen Thinking comparison introduces a new checkpoint as well as potentially different generation settings.

## Primary sources and archive

The `sources/qwen3-vl/` archive contains 16 original files: the official repository README and license, utility documentation and video preprocessing source, four relevant notebooks, two evaluation guides, and model cards plus generation configurations for official 8B Instruct, official 8B Thinking, and our pinned community MLX Instruct conversion. The repository revision is `96588727e44c78b25ba03ea03b8e12f7e64fd0da`. Model revisions and every source hash appear in `provenance.json`.

Script 19 archives the originals and produces readable notebook cell extracts. Those extracts omit saved outputs; the original notebooks retain them. Script 20 verifies all original hashes and records source excerpts and hashes from the installed MLX runtime without importing MLX or allocating GPU memory. No upstream notebook was executed, package upgraded, or model weight downloaded during this review.

Useful entry points:

- [Qwen3-VL README](https://github.com/QwenLM/Qwen3-VL): processor API, model family, serving examples, evaluation settings.
- [8B Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct) and [8B Thinking](https://huggingface.co/Qwen/Qwen3-VL-8B-Thinking): separate official checkpoints.
- [Video understanding cookbook](https://github.com/QwenLM/Qwen3-VL/blob/main/cookbooks/video_understanding.ipynb): temporal localization and timestamped input.
- [2D grounding cookbook](https://github.com/QwenLM/Qwen3-VL/blob/main/cookbooks/2d_grounding.ipynb) and [spatial understanding cookbook](https://github.com/QwenLM/Qwen3-VL/blob/main/cookbooks/spatial_understanding.ipynb): visual queries and coordinate conventions.
- [Thinking with images](https://github.com/QwenLM/Qwen3-VL/blob/main/cookbooks/think_with_images.ipynb): an agent using image zoom and search tools.

## Generation settings: three different sources of defaults

The repository's evaluation section describes the following settings. They are benchmark reproduction settings, not a requirement that every short state question consume the entire output allowance.

| Parameter | Published Instruct evaluation | Published Thinking evaluation | Current worker path |
|---|---:|---:|---:|
| Temperature | 0.7 | 0.6 | 0.0 explicitly |
| top-p | 0.8 | 0.95 | 1.0 runtime default |
| top-k | 20 | 20 | 0 runtime default |
| Repetition penalty | 1.0 | 1.0 | Unset |
| Presence penalty | 1.5 | 0.0 | Unset |
| Seed | 3407 | 1234 | Not explicitly set |
| Output allowance | 32768 | 40960 | 384 comparison / 256 RULES |

The current worker calls `mlx_vlm.generate` with temperature zero and a request token limit. In installed MLX-VLM 0.6.17, `generate/ar.py:generate_step` supplies sampling defaults from `generate/common.py`; top-p is 1.0 and top-k is 0. At temperature zero the sampler is greedy, so those sampling filters do not provide the published stochastic profile. The saved model `generation_config.json` is not evidence that our explicit Python call uses every field from that file.

There is also a documented configuration discrepancy worth preserving: the archived official Thinking generation file specifies temperature 1.0, while the repository evaluation recipe specifies 0.6. The Instruct generation file lists temperature 0.7, top-p 0.8, and top-k 20, but does not supply the evaluation recipe's presence penalty. Consequently, a run must identify whether it follows the checkpoint config, published evaluation settings, or a task-specific profile. Silently relying on defaults cannot reproduce all three.

The installed MLX implementation supports presence penalties, but also has a penalty-context setting that defaults to a limited recent-token window. Verify its intended scope against the comparison engine before claiming matching penalty semantics. Matching parameter names is not sufficient for numerical or behavioral parity.

## A bounded experiment for this ticket

Keep the current deterministic Instruct results as an immutable baseline. First compare the same checkpoint and image packet under explicitly configured sampling on development. This isolates a decoding change from a checkpoint change. The small test set already inspected in reference 05 is now diagnostic material; use new reviewed test episodes for subsequent model selection claims.

Then evaluate a pinned 8B Thinking checkpoint as a distinct candidate, subject to a load/template smoke and conversion provenance. Record the actual template prefix and how the worker exposes reasoning and final-answer boundaries. Do not assume that a Cosmos-specific prompt wrapper or a text-only Qwen reasoning toggle is appropriate for this multimodal checkpoint.

```text
for candidate in frozen_development_candidates:
    load candidate.checkpoint_and_processor
    configure every sampling parameter explicitly
    for approved_case in development_cases:
        run with candidate.token_budget and measured_deadline
        preserve complete raw response and finish reason
        parse the final answer using candidate.output_contract
        validate identity, citations, visibility, and enum
        score answer correctness, unsupported certainty, and abstention
select one protocol using development only
freeze new test cases before evaluating the selected protocol
```

A first bounded reasoning trial could allow 4096 output tokens, with a deadline established by measurement. That would be our engineering choice, substantially below the published Thinking evaluation allowance. Label it accordingly and report truncation. A missing final answer after budget exhaustion is a runtime/output failure, not an unknown visual state and not a false answer. Repeat a small development subset with fixed, recorded seeds if sampling variability affects selection.

Keep two comparisons distinct: equal packet and resource budget for deployment utility, and separately documented recommended settings for each model. Otherwise, changes in checkpoint, quantization, decoding, and runtime become impossible to distinguish.

## Resolution, crops, and grounding

The Qwen README describes image processor size values as pixel-area budgets despite their `shortest_edge` and `longest_edge` names. For video, the official processor budget applies across frames. The utility path also exposes per-frame and total budgets. Read the exact processor version and path rather than copying numerical settings between APIs.

Qwen3-VL uses 32-fold spatial compression for the visual-token budgeting examples and twofold temporal compression for video. The utility example calls `process_vision_info` with `image_patch_size=16`, requests video metadata, and sets `do_resize=False` in the processor after utility resizing. This avoids resizing the same media twice. Our adapter's input pixel cap bounds file acceptance; it does not establish the exact tensor resolution seen by the model. Log the processed shape and visual grid when extending the experiment.

The zoom cookbook suggests a useful bounded experiment for a tiny but visible appliance: provide full-frame context and one approved crop. Keep the source frame ID, crop rectangle, resize transform, and distinct image alias. Both views derive from the same observation and must not be counted as independent evidence. Our current adapter accepts only one image, so this would require an explicit contract extension. The notebook's search tool is unnecessary for a point-state question; external images cannot establish the state in our approved frame.

Grounding uses coordinates normalized independently to 0–1000 along width and height. Convert proposed boxes to pixel coordinates, validate ordering and bounds, and overlay them for review before comparing them with YOLO detections. A valid box and a fluent label do not establish correct localization. Cropping can improve access to visible detail but cannot recover a door surface hidden behind an actor.

## Video and temporal evidence

The video cookbook demonstrates event start/end localization, frame-list inputs, and timestamp-image pairs. Its frame-list sampling rate describes the temporal spacing of supplied frames; it must not be confused with the source movie's original frame rate. The helper documentation distinguishes handling of file paths from handling of a pre-sampled list. Preserve actual presentation timestamps, selected frame indices, and clip offsets in either representation.

The utility path returns video metadata that is passed into the official processor. Treat metadata loss, double sampling, and incorrect clip-relative timestamp conversion as implementation failures to diagnose before attributing weak temporal answers to the model. Native video and several separately labeled images should remain distinct modes.

This is related to the earlier native embedding repair as an engineering lesson, not as a shared fix. Successful forwarding of video pixels in the embedding adapter does not prove that the generative MLX video path preserves timestamps, frame ordering, or preprocessing. The single-image verifier smoke establishes none of those capabilities.

## Runtime, quantization, and evaluation cautions

Our pinned community model card says its MLX conversion was made using MLX-VLM 0.3.4; we currently execute it with 0.6.17. That is useful provenance, not automatically an incompatibility. Keep the exact checkpoint and installed runtime identities in every result. The community's short temperature-zero example is a usage smoke, not the official Qwen evaluation configuration.

The Qwen repository advertises FP8 checkpoints and CUDA-oriented serving examples. FP8 and our MLX affine 8-bit weights are different representations; a shared bit count does not imply interchangeable files, operators, or quality. This review does not establish a vetted MLX Thinking conversion. Check available conversion provenance or convert from official weights only when starting that experiment. No new engine or package installation is needed for this research or the accepted single-image path.

The archived evaluation guides are helpful but contain older examples, including Qwen2.5 model names and 28-based pixel calculations. They should not be treated as uniformly current Qwen3 preprocessing specifications. Their answer-extraction workflows also differ from our strict evidence contract. Use reviewed labels and explicit final-answer validation here; do not let an auxiliary model rewrite malformed answers into apparently correct results.

Our measured Qwen result remains 8/12 on the fresh test split, including 0/4 correct abstentions. None of the upstream guidance demonstrates that Thinking, stochastic decoding, or crops will fix that failure. Those are hypotheses to measure with explicit unknown cases, not accepted improvements.

## Recommended order

1. Add an explicit generation-profile record and inspect processed image dimensions; compare deterministic and published Instruct decoding settings on development.
2. Pin and smoke-test an 8B Thinking candidate, then evaluate its separately versioned output contract and budget.
3. Run a full-frame-plus-crop experiment for small visible targets if those remain a major error class.
4. Extend to short timestamped video only for questions requiring temporal evidence.
5. Continue to defer larger embedding models and fine-tuning until the verifier experiments establish a concrete need.

Local implementation references: `workbench/src/video_workbench/verifiers/worker.py`, `adapter.py`, `visibility.py`, and `rules/handoff.py`. Runtime evidence is in `sources/qwen3-vl/local-runtime-audit.json`; prior measured evidence and visual cases remain in reference 05 and `various/visibility-v2/`.
