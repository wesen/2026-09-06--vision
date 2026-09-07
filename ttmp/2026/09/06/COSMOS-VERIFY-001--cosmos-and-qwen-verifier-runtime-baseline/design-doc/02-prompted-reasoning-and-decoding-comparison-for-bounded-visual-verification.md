---
Title: Prompted reasoning and decoding comparison for bounded visual verification
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
    - Path: repo://workbench/src/video_workbench/verifiers/adapter.py
      Note: Worker supervision and raw record size
    - Path: repo://workbench/src/video_workbench/verifiers/contracts.py
      Note: Current output and deadline caps
    - Path: repo://workbench/src/video_workbench/verifiers/visibility.py
      Note: Prompt and final answer validation
    - Path: repo://workbench/src/video_workbench/verifiers/worker.py
      Note: Explicit sampling profile implementation target
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T22:14:14.604626-04:00
WhatFor: ""
WhenToUse: ""
---


# Prompted reasoning and decoding comparison

## Purpose and current evidence

Test whether explicitly asking the existing Qwen3-VL-8B-Instruct checkpoint to reason through visible evidence improves its final state answers, particularly abstention. This experiment does not require a Thinking checkpoint. Prompted reasoning is a valid candidate behavior for an instruction model; its benefit remains an empirical question. A later Qwen3-VL-8B-Thinking run measures a different checkpoint and must be reported separately.

The accepted implementation executes one approved image per request, binds identities on the host, and returns separate verifier-conditioned RULES evidence. In the latest comparison, Qwen answered eight of twelve labels correctly but gave definite answers on all four unknown cases. Cosmos answered seven of twelve and also failed all four abstentions. These results motivate a focused experiment rather than a claim that more reasoning will fix the problem.

This document specifies follow-up work. No prompts, limits, parser behavior, weights, or measured results change merely by accepting the design.

## First experiment: hold the Qwen checkpoint fixed

Use the already pinned MLX 8-bit Qwen Instruct model and existing single-image preprocessing. Cross two prompt styles with two decoding profiles:

| Arm | Prompt | Decoding | Question answered |
|---|---|---|---|
| QD-G | Direct visibility answer | Greedy | Repeated control under the new common budget |
| QR-G | Step-by-step visible-evidence reasoning, then answer | Greedy | Does prompted reasoning help with decoding held fixed? |
| QD-S | Direct visibility answer | Explicit sampled Instruct profile | Does decoding help with prompt held fixed? |
| QR-S | Same reasoning prompt as QR-G | Same sampled profile as QD-S | Does the combination help? |

All four arms use the same model hash, processor, image bytes, target description, system-message policy, final-answer schema, and maximum output budget. Retain the historical 384-token evaluation unchanged; QD-G is a fresh control, not a relabeling of that historical result. Preserve the current absence of a system turn in this first factorial experiment so that it does not become another confound.

The greedy profile explicitly records temperature 0, top-p 1, top-k 0, and neutral penalties. The sampled profile records temperature 0.7, top-p 0.8, top-k 20, repetition penalty 1.0, and presence penalty 1.5. These sampled values follow the archived Qwen evaluation recipe, but our resource budget is task-specific. Inspect and explicitly record MLX penalty context scope; if semantics differ from the reference engine, label the run a local approximation instead of claiming exact reproduction.

Use one deterministic run per greedy arm. Use fixed seeds 3407, 3408, and 3409 for sampled arms on development. Report their mean and range, and preserve individual results. Do not count repeated answers to one frame as independent cases.

## Prompt and output contracts

Both prompts retain the existing definitions of open, closed, and unknown. The direct arm requests only the current five-field visibility JSON object. The reasoning arm adds an explicit step-by-step instruction after the shared task definitions:

```text
Reason step by step using only the supplied image:
1. Identify the requested appliance and the door surface.
2. Examine which parts are visible and which are obscured or too small.
3. Compare direct evidence for an open door with direct evidence for a
   closed door. If neither is established, choose unknown.
Do not infer door state from the person's activity or an assumed history.

Write your reasoning inside <think> and </think>.
Immediately after </think>, return exactly one final JSON object using
 the specified visibility schema. Put no additional prose after it.
```

The resulting text is model-generated explanation. It may be incomplete, unfaithful, or visually incorrect. Preserve it for diagnosis but do not treat its fluency or length as evidence of correctness. Score the final answer against the reviewed image label. The existing final `rationale` field remains a brief statement of visible support, separate from the preceding explanation.

The new parser must select a declared output style, not auto-detect arbitrary answer formats:

- `direct_json`: retain the existing strict visibility parser and narrow outer-fence normalization.
- `think_then_json`: require exactly one leading reasoning block and its closing delimiter; parse the entire remaining suffix as one final JSON object. Permit only the existing traced outer JSON fence on that suffix.
- Reject missing or repeated delimiters, extra trailing prose, multiple answer objects, invalid JSON, duplicate keys, fabricated image aliases, and inconsistent visibility flags.
- A response cut off before a final answer is `invalid` with an explicit truncation/incomplete-output reason when supported by the worker finish record. It is never converted to a visual `unknown` answer.

The parser retains the untouched raw response, extracted final text, normalization trace, declared style, and error category. Existing host ID and F1 citation binding remain unchanged. No repair pass asks another model to invent or correct the final answer.

## Budget and implementation changes

`verifiers/contracts.py:validate_request` currently limits output to 512 tokens and deadlines to 120000 ms. `visibility.parse_visibility` limits final text to 16000 characters, and `adapter.verify` caps the serialized worker result at 100000 bytes. These limits must be addressed deliberately: merely passing 4096 to generation would fail the request contract.

For this experiment, raise the maximum accepted request output budget to 4096 while keeping existing callers' requested budgets unchanged. Record the contract revision in the run manifest and add boundary cases for the revised maximum. Keep the 120-second maximum deadline. A small development-only pilot checks whether the chosen 4096-token allowance and 120-second deadline are usable. If not, stop and revise the protocol before freezing the experiment; do not silently extend timed-out runs.

Use the same 4096-token maximum and 120-second deadline for all four new arms. This compares behavior under equal resource ceilings, not equal realized computation: reasoning will usually generate more text. Report actual tokens and wall time. Increase the bounded worker-result file allowance to one MiB and allow at most 256 KiB of raw UTF-8 response before extraction. Keep the final JSON limit at 16000 characters and the final rationale limit at 2000 characters. The larger raw limit supports explanations without weakening the final contract.

Add a small immutable experiment profile rather than a general provider/configuration framework:

```text
GenerationProfile:
    id, prompt_style, output_style
    temperature, top_p, top_k
    repetition_penalty, presence_penalty, penalty_context_scope
    seed, max_output_tokens, deadline_ms
```

Host validation checks the profile and ensures its limits equal those in the request. Write a canonical profile JSON and hash it into the result manifest. The worker reads that exact profile, sets the MLX seed, passes supported decoding parameters explicitly, and records resolved values, formatted prompt, actual processed image dimensions/grid, generation tokens, finish reason, and memory. If a requested parameter cannot be applied, fail that profile before evaluation rather than ignore it.

Proposed file responsibilities:

- `verifiers/visibility.py`: preserve shared task definitions; add explicit reasoning prompt and final-answer extraction.
- `verifiers/worker.py`: apply the validated profile and record resolved runtime settings.
- `verifiers/adapter.py`: pass the profile, enforce raw/file limits, and preserve execution versus output failure categories.
- `verifiers/contracts.py`: revise and test the explicit output-budget maximum.
- New `verifiers/profiles.py`: a small validation/serialization helper only if it keeps worker and host validation in one place.
- A new numbered ticket script: freeze cases/profiles, run sequentially, and produce comparison artifacts. Keep the existing scripts and results reproducible.

```mermaid
flowchart LR
    C[Reviewed frame and target] --> P[Frozen arm and generation profile]
    P --> W[Bounded MLX worker]
    W --> R[Preserved raw response]
    R --> E[Declared final-answer extractor]
    E --> V[Existing visibility and citation validation]
    V --> S[Label scores and separate RULES evidence]
```

## Dataset, selection, and acceptance

Use already reviewed cases only as development/diagnostic material. Before inference, freeze at least 24 new development frames and 24 untouched test frames from disjoint episodes, with a target of eight visible closed, eight visible open, and eight unknown cases per partition. If the available episodes cannot provide that distribution, record the actual counts before running rather than duplicating frames. Label solely from RGB, preserve original hashes, and document camera/apartment overlap. Request independent review of ambiguous labels when available; do not call assistant review a human benchmark.

Freeze all four prompts/profiles and the following selection rule before development inference. Compute exact final-answer accuracy and the rate of known answers on unknown cases, with invalid outputs counted as incorrect and reported separately. Rank profiles by `mean_over_all_cases(correct_indicator - unsupported_known_on_unknown_indicator)`, averaging each sampled case across seeds first. Both terms use the complete case population as their denominator, matching the earlier count-based selection convention after normalization. Break ties by lower unsupported-certainty rate, then lower median end-to-end latency, then the simpler direct/greedy arm. For stochastic arms average each case over the three predefined seeds first.

If no candidate improves the development score over QD-G, retain the direct control. On the untouched test partition, compare the chosen candidate with QD-G, using the same seed policy and no further tuning. Report known-state accuracy, unknown recall, unsupported certainty, invalid/truncated/timeout counts, tokens, median and tail latency, and memory. Show per-case paired changes and summarize by episode as well as frame; this small correlated set does not justify broad statistical claims.

Report final-rationale factual support separately: review whether each short rationale describes actually visible evidence, especially when it asserts an unobstructed door. Do not use agreement between explanation and answer as a correctness metric. Keep galleries showing the original frame, reviewed label, arm, final answer, and a brief failure annotation; store full raw explanations in linked artifacts.

Successful execution establishes an experimental adapter capability. Improved abstention requires measured evidence. Any model promotion to RULES remains separate from the unchanged baseline stream. A bounded live handoff smoke verifies the selected output style at feature completion, not after every small edit.

## Subsequent comparisons

After this fixed-checkpoint experiment, run the analogous direct-versus-prompted-reasoning comparison for the pinned Cosmos 8B model using its documented prompting convention. Keep model-specific decoding profiles explicit. A cross-model comparison must distinguish equal-budget deployment utility from model-specific recommended configurations.

Qwen3-VL-8B-Thinking remains a later distinct checkpoint candidate. Pin its weights/conversion, inspect the actual template and output boundaries, and smoke-test loading before a new frozen comparison. No Thinking download is required to run QR-G or QR-S.

Crops, multi-image input, native generative video, fine-tuning, and larger embeddings remain separate follow-ups. This design adds neither an autonomous tool loop nor revision/supersession machinery.

## References

- Reference 05: measured visibility comparison and visual case guide.
- Reference 06: Cosmos guidance and configuration differences.
- Reference 07: Qwen source review and installed runtime audit.
- `sources/qwen3-vl/README.md`, `provenance.json`, and `local-runtime-audit.json`: archived settings and implementation evidence.

## Pilot and freeze implementation note

P2 pilots completed before the comparison. Qwen Instruct omitted literal `<think>` delimiters in both initial reasoning pilots, producing prose followed by JSON; those outputs remain rejected and archived. A separate development pilot verified `<reasoning>...</reasoning>` for Qwen. Cosmos retains `<think>...</think>`. The declared model-family grammar is frozen before evaluation; no arbitrary-prose extraction was enabled.

Remaining unseen episodes did not yield the target balanced distribution. The frozen 48-case RGB set contains development 15 closed / 3 open / 6 unknown and test 18 closed / 4 open / 2 unknown, with eight new episodes and correlated apartment/action families. Frame sampling was refined through RGB review to include the visible opening interval before labels were frozen; no new-case model outputs informed selection. The few unknown test cases limit uncertainty conclusions.


## Completed implementation and measured decision — 2026-09-07

The shared experiment is complete: 384 development and 72 held-out calls, with both model selections frozen before test. Qwen selected direct greedy; Cosmos selected prompted reasoning with greedy decoding. On held-out frames, Qwen direct and Cosmos direct each scored 22/24, while Cosmos reasoning scored 20/24. None resolved either unknown test case. Keep direct greedy as the practical point-state reference; the reasoning profiles remain available explicitly. See [the measured report](../reference/08-measured-qwen-and-cosmos-prompted-reasoning-comparison.md) for seed variability, final-rationale support, visual panels, and resource costs.

After strict inference and live handoffs finished, commit `89c4313` enabled a conservative missing-close heuristic for practical profiled calls. It recovers a single omitted reasoning closing tag only when the entire final JSON passes unchanged validation, and records raw text and a recovery trace. `recover_missing_close=False` retains strict extraction. The separate saved-output replay recovered all 13 Qwen wrapper failures; it did not repair enum errors, execution failures, or visual mistakes. The original protocol and selections were not rewritten.
