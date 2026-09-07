---
Title: Cosmos Reason2 official guidance review and experiment recommendations
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
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/sources/cosmos-reason2/provenance.json
      Note: Pinned primary source archive
    - Path: repo://workbench/src/video_workbench/verifiers/worker.py
      Note: Comparison with official inference guidance
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T21:56:28.759315-04:00
WhatFor: ""
WhenToUse: ""
---


# Cosmos Reason2: official guidance and implications for our verifier

The main finding is a configuration distinction. We have measured Cosmos Reason2 8B as a short, deterministic image classifier with structured answers. We have not yet measured its explicitly prompted reasoning mode under NVIDIA's recommended generation settings. Those results answer different questions. The existing comparison remains useful, but it does not establish the best reasoning performance available from this checkpoint.

## Sources and reproducibility

The adjacent `sources/cosmos-reason2/` directory contains the official repository README, minimal Transformers inference example, configurable inference utility, troubleshooting guide, quantization guide, license, and the model card from our downloaded official checkpoint. `provenance.json` records URLs, byte lengths, and SHA-256 hashes. Repository files are pinned to `a3b4a1db4065fe13c4b1f4d2fb8605bad647f4b9`; the model card is pinned to checkpoint revision `a9fae2cf89dc64db96b12860417f0eb403013bb9`. Script `16-archive-reason2-guidance.py` reproduces this collection. Downloaded Python is reference material, not executed code.

The cookbook archive is separately pinned to `d0857364e8a727be41b181731e03f478213e4558`. Its prompt guide is particularly useful because it describes message ordering, generation controls, temporal output, grounding coordinates, and task examples in one place. The warehouse recipe supplies a concrete evaluation workflow with visual inspection and saved failures.

## Reasoning and direct answering

The cookbook and official inference utility distinguish two sampling profiles:

| Setting | Direct profile | Reasoning profile | Current verifier |
|---|---:|---:|---:|
| Temperature | 0.7 | 0.6 | 0.0 |
| top-p | 0.8 | 0.95 | Not explicitly overridden |
| top-k | 20 | 20 | Not explicitly overridden |
| Repetition penalty | 1.0 | 1.0 | Not explicitly overridden |
| Presence penalty | 1.5 | 0.0 | Not explicitly overridden |
| Maximum generated tokens | Official utility defaults to 4096 | Official utility defaults to 4096 | 384 in frozen image evaluation; 256 in RULES request |

The guide enables reasoning through an explicit user instruction requesting a `think` section followed by a final answer. Our worker requests only the small JSON object. A larger model alone does not change that protocol. Increasing the token limit without changing the prompt would not constitute the recommended reasoning experiment either.

There is a real documentation inconsistency: the model card's introductory usage section suggests a system instruction with both `think` and `answer` tags, while its later working example and the cookbook use a user instruction with the final answer immediately after the closing reasoning tag. A new experiment should select and freeze one convention. Prefer the cookbook convention shared by the later example, with a minimal helpful-assistant system message. Do not make the parser heuristically search arbitrary prose for any plausible JSON object.

For the reasoning experiment, retain the full raw model output as a diagnostic artifact, parse only the explicitly delimited final answer, and validate that answer through the existing visibility contract. Missing closing delimiters, truncation, duplicate JSON keys, or invalid citations remain failures. Generated reasoning and rationale are model claims; they are not independent evidence of what appears in the frame.

## Message structure and runtime identity

The official example places media before user text and uses a minimal helpful-assistant system message. Inspection of our saved `worker-result.json` confirms that MLX-VLM places the image token before our task text. Our current formatted prompt has no system turn. Record that difference explicitly and introduce any system-message change only in a new protocol version.

The official example instantiates `Qwen3VLForConditionalGeneration` and `Qwen3VLProcessor`, which explains why the Qwen3-VL family infrastructure is relevant to Cosmos Reason2. This is architectural compatibility, not evidence that our MLX conversion reproduces every CUDA/Transformers numerical result. Our local 8B weights are converted from the accepted official source into MLX affine 8-bit group-64 weights. NVIDIA's quantization document describes its own supported workflow; its existence does not validate our conversion or make CUDA-oriented compressed checkpoints interchangeable with MLX weights.

No additional inference engine is required for the current image experiment. Installing vLLM or NVIDIA CUDA dependencies on this Mac would not resolve a prompting or visibility failure. Keep the working MLX environment and record its exact package versions, conversion provenance, formatted input, and generation settings with each run.

## Video sampling and preprocessing

The official minimal example samples video at 4 fps and permits 4096 generated tokens. These are useful starting points for a later bounded video experiment, not proof that every task requires that sampling rate. A door transition can be missed if sampling excludes the relevant interval; a single image cannot establish temporal order regardless of the model's reasoning ability.

The example budgets visual tokens through processor size settings and a 32-by-32 pixels-per-token factor. The troubleshooting guide warns that Reason1 preprocessing arguments cannot simply be renamed with unchanged numbers for Reason2. This matters when introducing video or crops: record the actual selected frame timestamps, resize policy, image dimensions, processor identity, and resulting token count. Our current file-size and pixel limits bound the input packet; they do not by themselves document every internal processor transformation.

Reason2 incorporates video timestamps through its input representation; the migration guidance says not to paint timestamp text onto the frames. Human review panels may carry labels, but model input must remain the original image. Our annotated closed/open/unknown panels are separate files and are not submitted for inference.

## What the examples teach—and what they do not prove

The warehouse notebook defines concrete visual classes, restricts irrelevant subjects, and saves predictions for visual review. We can adopt those practices by defining visible closed-door evidence, naming occlusion conditions, and keeping per-case images and raw answers. We should not copy its fixed warehouse labels or force our unknown cases into a closed class.

Some cookbook examples infer package authorization or estimated load weight from visual context. Such outputs illustrate model behavior; they do not establish the hidden facts. Our verifier must separate visible state from authorization, intent, ownership, and unobserved history. This distinction is especially important for a closed case: failure to see an opening is insufficient when the door is obscured.

Grounding examples use independently normalized image coordinates on a 0–1000 scale. If we ask Cosmos for a box to compare against YOLO, convert x by image width and y by image height, validate bounds, and render the proposed box for inspection. A model-generated box should not silently replace the detector track or become a correct localization merely because it is valid JSON.

## Recommended sequence

1. Finish and preserve the current frozen image comparison, including abstention errors. This establishes the behavior of the implemented bounded adapter.
2. Run a separately versioned development experiment comparing the existing direct configuration with an explicitly prompted reasoning configuration. Include the minimal system message, explicit sampling settings, larger output budget, truncation reporting, and a corresponding measured deadline. Select settings without looking at fresh test outputs.
3. Inspect difficult cases with an approved target crop plus full-frame context, if the packet contract is deliberately extended to multiple images. Keep occluded cases unknown: cropping cannot recover missing pixels. This is a proposed experiment, not implemented capability.
4. Evaluate a short, timestamp-preserving video packet for questions that require change or order. Keep this separate from point-state inference and from the native embedding benchmark.
5. Consider fine-tuning only after the above separates prompt, visibility, temporal coverage, and inference failures. Our small correlated VirtualHome sample is insufficient to justify a training program by itself.

The repository now also documents a 32B Reason2 model and states that ongoing development has moved toward Cosmos 3. That is useful planning information, not a reason to change this ticket's pinned 8B baseline mid-evaluation. A model-family migration should have its own resource and acceptance comparison.

## References

- [Official Cosmos Reason2 repository](https://github.com/nvidia-cosmos/cosmos-reason2)
- [Cosmos Reason2 8B model card](https://huggingface.co/nvidia/Cosmos-Reason2-8B)
- [NVIDIA prompting guide](https://nvidia-cosmos.github.io/cosmos-cookbook/getting_started/prompt_guide/reason_guide.html)
- [Worker safety recipe](https://nvidia-cosmos.github.io/cosmos-cookbook/recipes/inference/reason2/worker_safety/inference.html)
- Local implementation: `workbench/src/video_workbench/verifiers/worker.py`, `visibility.py`, `adapter.py`; `workbench/src/video_workbench/rules/handoff.py`.
