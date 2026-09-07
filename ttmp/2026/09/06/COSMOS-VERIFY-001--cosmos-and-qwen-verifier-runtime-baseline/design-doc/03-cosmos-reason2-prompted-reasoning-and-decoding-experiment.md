---
Title: Cosmos Reason2 prompted reasoning and decoding experiment
Ticket: COSMOS-VERIFY-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/sources/cosmos-reason2/inference.py
      Note: Official reasoning sampling defaults
    - Path: repo://workbench/src/video_workbench/verifiers/visibility.py
      Note: Reasoning prompt and final answer validation
    - Path: repo://workbench/src/video_workbench/verifiers/worker.py
      Note: Shared generation profile integration
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T22:18:39.291542-04:00
WhatFor: ""
WhenToUse: ""
---


# Cosmos Reason2: explicit reasoning on the existing 8B checkpoint

## Objective and scope

Measure whether explicitly prompted reasoning improves visible door-state verification with the existing locally converted Cosmos-Reason2-8B weights. Use the accepted official source revision `a9fae2cf89dc64db96b12860417f0eb403013bb9` and existing MLX 8-bit group-64 conversion in `output/models/cosmos-reason2-8b-8bit-local`. Reuse its recorded conversion hashes. No new weights or inference engine are required for this experiment.

The previous short JSON run achieved seven correct labels out of twelve and zero correct abstentions among four unknown cases. This design tests a possible improvement; it does not assume that generated reasoning will recover hidden visual evidence.

Unlike the later Qwen Thinking comparison, the Cosmos direct and reasoning conditions use the same checkpoint. The archived NVIDIA guide enables explicit reasoning through a user instruction requesting a reasoning block followed by the final answer. See reference 06 for source details and the documented disagreement between examples about a separate answer tag.

## Controlled development experiment

Cross prompt style with decoding while holding the checkpoint, image, visibility definitions, and resource ceilings fixed:

| Arm | Prompt | Decoding |
|---|---|---|
| CD-G | Direct visibility JSON | Greedy |
| CR-G | Explicit reasoning followed by visibility JSON | Greedy |
| CD-S | Direct visibility JSON | NVIDIA reasoning sampling profile |
| CR-S | Explicit reasoning followed by visibility JSON | Same NVIDIA reasoning sampling profile |

Using the same sampled settings in CD-S and CR-S makes their difference a prompt comparison. CD-S is deliberately a control using the reasoning sampling profile; do not label it NVIDIA's default direct-answer configuration. NVIDIA's direct profile uses temperature 0.7, top-p 0.8, and presence penalty 1.5. Testing that profile is a later optional decoding comparison if development results justify it, not another mandatory arm here.

For both sampled arms set temperature 0.6, top-p 0.95, top-k 20, repetition penalty 1.0, and presence penalty 0.0. Use seeds 1234, 1235, and 1236, recording each result. For greedy arms explicitly use temperature 0, top-p 1, top-k 0, and neutral penalties. These choices follow the archived `sources/cosmos-reason2/inference.py:SamplingParams.get_defaults` for the reasoning condition and add explicit local controls.

Use the minimal helpful-assistant system message and media-first ordering in all four new arms. The historical experiment omitted a system turn; therefore CD-G is a new matched control, and differences from the old report cannot be attributed solely to reasoning. Record the actual formatted prompt to verify this change.

## Reasoning prompt and answer boundary

Keep the shared task text from `visibility.py`: identify the target, distinguish visible open from visible seated closed, and select unknown for occluded or indistinguishable state. Append the following only in reasoning arms:

```text
Examine the target appliance, which parts of its door are directly
visible, and the visible evidence for open or closed. Reason step by
step using only this image. Do not infer state from the person's
activity or from an assumed sequence of events.

Answer using this format:
<think>
Your reasoning about the visible evidence and its limitations.
</think>
Immediately after </think>, return one JSON object with the specified
visibility fields. No additional prose follows the final JSON.
```

This follows the cookbook's user-turn convention. Do not combine it with a competing system instruction requiring an additional answer tag. Preserve the complete response, but validate and score only the declared final object. An explanation is a model claim, not an independent observation or a calibrated confidence measure.

Reuse design 02's `think_then_json` parser: exactly one leading reasoning block, then exactly one final object; preserve the existing traced outer fence normalization for that object. Reject incomplete delimiters, multiple blocks or answers, trailing prose, and invalid visibility/citation content. Bind long request/entity identifiers on the host. Unknown remains a valid visual answer; malformed output, truncation, timeout, and execution failure remain distinct failures.

## Shared implementation and resource limits

Implement R1–R2 from design 02 once, then add Cosmos profiles and its prompt convention. There is no separate Cosmos supervisor, evidence store, or repair framework. The shared work covers explicit sampler settings, seeded generation, a versioned profile hash, final-answer extraction, and bounded raw-response handling.

The proposed common budget is 4096 generated tokens and a 120-second wall-clock deadline, including setup. The current request maximum is only 512 tokens, so the shared contract update is a prerequisite. Keep old callers' requested budgets unchanged. Apply the proposed one-MiB worker-result limit, 256-KiB raw UTF-8 limit, 16000-character final JSON limit, and 2000-character final rationale limit from design 02.

Run a small development-only pilot to verify template behavior, EOS handling, output extraction, and the budget. If generation does not complete within the declared deadline, revise and refreeze the protocol before the comparison. Do not extend timeouts case by case or reinterpret missing final answers as abstention.

Implementation touchpoints are `verifiers/worker.py`, `visibility.py`, `adapter.py`, `contracts.py`, and the small profile helper proposed in design 02. Add a numbered ticket experiment script or model-specific configuration to the shared runner; keep prior scripts and results unchanged.

## Data, evaluation, and visual trail

Reuse design 02's frozen development/test population only if both model protocols are frozen before any shared test output is examined. Run both development selections before opening the shared test comparison. If Qwen test results have already influenced Cosmos prompt or profile choices, those frames are development material for Cosmos and require a fresh untouched test population. This prevents cross-model test feedback from becoming hidden tuning.

Use the same frame bytes, reviewed labels, timestamps, and target identities across comparable runs. Preserve scene/episode membership and unknown cases. Average sampled results per case across the three fixed seeds; repeated generations are not independent images.

Select the Cosmos arm on development using the design 02 score: mean over all cases of correct-answer indicator minus unsupported-known-answer-on-unknown indicator. Break ties by lower unsupported certainty, then lower median end-to-end latency, then the simpler direct/greedy arm. Compare the selected arm with CD-G on untouched test cases. Keep the baseline if no development candidate improves the score.

Report final-state accuracy, visible-state accuracy, unknown recall, unsupported certainty, final-rationale factual support, invalid/truncated/timeout counts, generation tokens, end-to-end latency, and peak MLX allocation. Include original images with reviewed labels and model outcomes for changed decisions and persistent occlusion failures. Link full raw outputs from the gallery instead of treating the explanation as ground truth.

For a joint Qwen/Cosmos report, distinguish each model's within-checkpoint prompt effect from comparisons using different sampling profiles and quantization provenance. The recommended profiles do not provide numerical parity between models or engines.

## Acceptance and next action

At feature completion, run focused tests for profile validation, complete/incomplete reasoning envelopes, raw/final limits, future or changed evidence, timeout recovery, and unchanged baseline evidence. Then run one live Cosmos selected-style RULES handoff as separate evidence. Reliable abstention is accepted only if measured; a functioning parser alone does not satisfy it.

Start with the shared R1–R2 implementation, then Cosmos tasks C1–C4. Native video, multi-image crops, larger models, larger embeddings, autonomous investigation loops, and revision/supersession remain outside this experiment.

References: design 02 for shared contracts and detailed selection policy; reference 06 for NVIDIA guidance; `sources/cosmos-cookbook/reason_guide.md` and `sources/cosmos-reason2/inference.py` for the archived prompting and sampling source; reference 05 for the measured baseline.

## Pilot and freeze implementation note

P2 pilots completed before the comparison. Qwen Instruct omitted literal `<think>` delimiters in both initial reasoning pilots, producing prose followed by JSON; those outputs remain rejected and archived. A separate development pilot verified `<reasoning>...</reasoning>` for Qwen. Cosmos retains `<think>...</think>`. The declared model-family grammar is frozen before evaluation; no arbitrary-prose extraction was enabled.

Remaining unseen episodes did not yield the target balanced distribution. The frozen 48-case RGB set contains development 15 closed / 3 open / 6 unknown and test 18 closed / 4 open / 2 unknown, with eight new episodes and correlated apartment/action families. Frame sampling was refined through RGB review to include the visible opening interval before labels were frozen; no new-case model outputs informed selection. The few unknown test cases limit uncertainty conclusions.


## Completed implementation and measured decision — 2026-09-07

The shared experiment is complete: 384 development and 72 held-out calls, with both model selections frozen before test. Qwen selected direct greedy; Cosmos selected prompted reasoning with greedy decoding. On held-out frames, Qwen direct and Cosmos direct each scored 22/24, while Cosmos reasoning scored 20/24. None resolved either unknown test case. Keep direct greedy as the practical point-state reference; the reasoning profiles remain available explicitly. See [the measured report](../reference/08-measured-qwen-and-cosmos-prompted-reasoning-comparison.md) for seed variability, final-rationale support, visual panels, and resource costs.

After strict inference and live handoffs finished, commit `89c4313` enabled a conservative missing-close heuristic for practical profiled calls. It recovers a single omitted reasoning closing tag only when the entire final JSON passes unchanged validation, and records raw text and a recovery trace. `recover_missing_close=False` retains strict extraction. The separate saved-output replay recovered all 13 Qwen wrapper failures; it did not repair enum errors, execution failures, or visual mistakes. The original protocol and selections were not rewritten.
