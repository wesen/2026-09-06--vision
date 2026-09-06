---
Title: Reference parity and native video acceptance
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
    - Path: repo://ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/scripts/09-parity-audit.py
      Note: Enumerated process-isolated parity measurements
    - Path: repo://ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/scripts/10-parity-gates.py
      Note: Explicit gate evaluation
ExternalSources:
    - https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B
Summary: FP32 correctness accepted for pinned official preprocessing; quantized rollout rejected.
LastUpdated: 2026-09-06T16:16:00-04:00
WhatFor: Explain measured acceptance and limits
WhenToUse: Before native video integration or precision changes
---


# P3 findings

The repaired wrapper passes eight controlled FP32 comparisons against the official Qwen3VLModel on the same source weights and packed inputs. This accepts the wrapper implementation under the pinned official processor contract. It does not accept the existing MLX processor as interchangeable, any quantized native-video path, or corpus retrieval quality.

The official checkpoint is Qwen/Qwen3-VL-Embedding-2B at `9f2f7e710d6d81056aa5c0a4f04764fec6bb7bda`. The strict MLX loader sanitizes the official weight layout and casts the model to FP32; this is a controlled materialized in-memory conversion, with no independently downloaded unquantized MLX checkpoint. Source weight/config hashes are in `various/audit-provenance.json`. The official model's [published usage and modality scope](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B) are background; acceptance here comes from local measurements.

## Reproduction

Run from the workspace root with the isolated environment and Mac GPU access:

```sh
for mode in prepare-hf prepare-mlx torch mlx bf16 quant community compare; do
  PYTHONPATH=output/mlx-video-fix/mlx-vlm output/mlx-video-fix/.venv/bin/python \
    ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/scripts/09-parity-audit.py "$mode" || break
done
output/mlx-video-fix/.venv/bin/python \
  ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/scripts/10-parity-gates.py
```

Script 09 supersedes scripts 07/08 for acceptance, preserving their historical results. Fixtures are explicitly enumerated; saved HF arrays cannot contaminate a later glob. Processor families run in separate processes. Diagnostic visual passes occur outside inference timers. Reports record timestamp, commit, versions, tensor hashes, intermediate comparisons, and measurement boundaries.

## Separate causes

- **Preprocessing:** Transformers 5.16.1 with Torch 2.14.0/Torchvision 0.29.0 retains outer video vision delimiters from the checkpoint template, while MLX removes them. Direct MLX processor video has 195 tokens versus HF 197; historical script 07 had 196 because its utility path also treated sampling differently. These are distinct contracts. Token-only swaps produce cosine 0.8754–0.9637, while pixel-only swaps stay above 0.9999989. Pixel differences are approximately one 8-bit resampling step after normalization (0.0078433), consistent with PIL versus Torchvision bicubic kernels.
- **Single/odd frames:** Official processing rejects one frame before its implicit temporal padding. Explicitly repeat the last frame and timestamp first. The one-frame timestamp remains 0.0; three frames at 2.5 FPS give final group timestamp 0.8. MLX's regular-grid timestamp formula instead advances the duplicate to a new time. Native integration must use actual selected PTS relative to the clip and repeat the final PTS without advancing time.
- **Positions:** All eight FP32 cases match official positions exactly, allowing only broadcasting text's redundant modality axis. P2's independent-request and padding regressions remain green.
- **Visual/deepstack features and pooled hidden state:** Every exported intermediate passes the 0.01 absolute gate; observed global maximum is 0.000860214. The embedding wrapper retains all three deepstack features.
- **Pooling:** Official reference gathers the final unmasked token and normalizes in FP32. All eight normalized embeddings have cosine at least 0.999999999741 and maximum coordinate difference 0.00000283123. P2 tests separately cover padded batches and all-padding rejection.
- **Quantization:** BF16 minimum cosine is 0.998436, maximum coordinate error 0.017016. Controlled affine 4-bit group64 quantization of the same FP32 model has minimum cosine 0.443686; the community checkpoint minimum is 0.689270. The controlled policy quantizes all eligible model layers; it is not claimed to reproduce the community conversion policy. Community artifact identity is independently hashed, and its differences are not all attributed to quantization.

The one-query, seven-candidate ranking is identical for Torch FP32, MLX FP32, and BF16. Controlled 4-bit ranks reversed video first; the community checkpoint ranks the three-frame clip first and reverses the original/reversed order. No 4-bit native rollout is accepted. This tiny ranking probe is diagnostic, not a calibrated retrieval benchmark.

## Pixel and temporal interventions

Original/black inputs hold tokens and grids constant. FP32 original-versus-black cosine is 0.429234 and original-versus-reverse is 0.969836. These differ from P1's 0.518 because P1 used the community checkpoint and MLX preparation. Do not compare those values as a repair regression.

The reviewed contact sheet `various/parity-fixture-contact.jpg` shows an asymmetric door-opening sequence and its reversal. The query deliberately says closing; query similarity is not a ground-truth temporal label. The accepted claim is sensitivity to pixels/order and reference parity, not correct action classification.

## Tolerances and performance

`various/audit-policy.json` specifies rationale and bounds. FP32 requires cosine >= 0.99999, normalized coordinate error <= 0.0001, exact positions, and all unnormalized intermediate errors <= 0.01. These are implementation regression tolerances. BF16 bounds are exploratory; production initially uses FP32. Quantization is measurement-only.

| Runtime | Materialized load, s | First video call, s | Warm video median, s | MLX peak, GB | RSS high-water, GB |
|---|---:|---:|---:|---:|---:|
| Torch CPU FP32 | 5.435 | 1.175 | 1.185 | — | 13.153 |
| MLX FP32 | 4.197 | 0.356 | 0.201 | 9.545 | 5.019 |
| MLX BF16 | 2.996 | 0.196 | 0.196 | 5.655 | 4.799 |
| MLX controlled 4-bit | 2.894 | 0.217 | 0.215 | 2.397 | 4.810 |
| MLX community 4-bit | 2.478 | 0.219 | 0.215 | 3.182 | 2.350 |

Units above are decimal GB. Each warm median uses three materialized calls. Load includes process imports and conversion; first video call follows text/image, so it is first for the video shape, not first model inference. No filesystem-cache eviction is claimed. Process-wide memory peaks include untimed intermediate diagnostics and should not be interpreted as per-request increments. A fresh-process adapter benchmark will supplement these with cold first inference and preprocessing-inclusive timings during P4.

## Accepted integration boundary

Use official FP32 weights and the exact pinned official processor, explicitly materialize MLX outputs, preserve last-token pooling, and normalize stored output as FP32. Give native video its own adapter/runtime/temporal-policy identity and clip cache. Preserve the pooled-image baseline and its environment. Quantized native mode requires a future separate acceptance decision.


## P4 fresh-process measurement supplement

The completed native adapter exactly matches the accepted video/single/odd vectors; text differs only by 2.98e-8 after the workbench's final FP32 normalization. Two fresh-process runs are retained: `native-integration-first.json` and `native-integration.json`. The first measured cold inference including preprocessing at 0.324 s and warm at 0.207–0.209 s; the final source-gated run measured 2.578 s cold and 0.318–0.371 s warm. Both use warm filesystem caches on a machine with concurrent work. No load-isolated performance guarantee or causal explanation of variance is asserted. The final run has 9.539 GB MLX allocator peak and 4.842 GB RSS high-water, including the nine-clip development build.
