---
Title: Intern analysis design and implementation guide
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
    - Path: repo://configs/virtualhome-household-v1.json
      Note: Existing implementation evidence for this design
    - Path: repo://docs/playbook/virtualhome-corpus.md
      Note: Existing implementation evidence for this design
    - Path: repo://src/virtualhome_corpus/core.py
      Note: Existing implementation evidence for this design
    - Path: repo://src/virtualhome_corpus/runner.py
      Note: Existing implementation evidence for this design
ExternalSources: []
Summary: Compare bounded, evidence-grounded verifier behavior on identical local clips.
LastUpdated: 2026-09-06T13:13:51.660493-04:00
WhatFor: ""
WhenToUse: ""
---


# Cosmos and Qwen verifier runtime baseline

## Purpose and model roles

A verifier receives a small, explicitly selected piece of video evidence and a focused question, then proposes a typed observation with cited frame or interval references. This ticket establishes whether a local Cosmos Reason2 candidate and a comparable Qwen vision-language model can perform that role on this Mac with bounded resource use. It does not let a language model decide procedural rules or treat fluent explanations as ground truth.

The output is a runtime capability report, a common verifier adapter, an evidence-validation layer, and a matched comparison on a fixed small question set. Embeddings turn content into vectors for retrieval. A vision-language verifier generates answers conditioned on visual input. Cosmos-Embed, Cosmos Reason, and video generation are different components; this ticket is about the Reason-style verifier only.

The ticket can begin independently of the temporal models using manually selected training/development clips and oracle request fixtures. VIDEO-RULES-001 later integrates the adapter with candidate detection. No local model performance or conversion fidelity is claimed by this document.

## Evidence and candidate selection

The official [Cosmos Reason2-2B card](https://huggingface.co/nvidia/Cosmos-Reason2-2B) identifies the model and its Qwen3-VL-2B-Instruct base. The [community MLX conversion card](https://huggingface.co/hzang/Cosmos-Reason2-2B-8bit) publishes an 8-bit candidate and an image-generation usage example. That example does not prove native video handling or numerical fidelity on this Mac. Keep the conversion author, source revision, quantization details, and runtime revision in the experiment manifest.

Use [Qwen3-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct) as the initial comparison family, selecting an actually compatible pinned MLX checkpoint during implementation. Match parameter scale, quantization as closely as practical, evidence frames, question wording, generation budget, and decoding settings. If quantization or preprocessing cannot be matched, state the difference; the comparison then measures deployed systems rather than an isolated training-method effect.

The existing VirtualHome corpus provides actual RGB videos and endpoint graph truth. For a question such as "is the fridge visibly open in this frame?", use reviewed RGB labels rather than assuming the graph answers the visibility question. Use the current endpoint labels only for explicitly identified world-truth diagnostics.

## Verifier boundary and evidence packet

```text
focused question + entity binding + approved evidence
                         |
                 request validator
                         |
              common verifier adapter
                  /             \
            Qwen MLX         Cosmos MLX
                  \             /
                  bounded raw response
                         |
            parser + citation range checks
                         |
       typed proposal OR unknown / failed request
```

The caller owns evidence selection and the allowed time horizon. The adapter owns model formatting and generation. A deterministic validator owns response shape, entity consistency, and citation validity. The rule engine owns PASS/VIOLATION/UNKNOWN decisions. Keep these responsibilities separate even if the first implementation is one CLI.

```python
# Proposed application protocol, not a vendor signature.
@dataclass(frozen=True)
class VerifyRequest:
    request_id: str
    episode_id: str
    entity_id: str
    predicate: str
    question: str
    evidence_ids: tuple[str, ...]
    allowed_start_us: int
    allowed_end_us: int
    as_of_us: int
    max_output_tokens: int
    deadline_ms: int

class VideoVerifier(Protocol):
    def verify(self, request, evidence) -> VerifyResult: ...
```

An evidence packet includes source hashes, actual frame PTS, image dimensions, representation mode, and stable frame IDs. The allowed interval is half-open. Only frames whose evidence is available by `as_of_us` may be sent. A long video path by itself is not a bounded packet if the processor can inspect the whole file; decode the approved interval first or enforce a verified clipping path.

`VerifyResult` has transport status (`ok`, `timeout`, `invalid`, `runtime_error`), answer (`true`, `false`, `unknown` when status permits), cited evidence IDs, optional uncertainty bounds, a short rationale, model/prompt specification hashes, elapsed time, and raw-response location. Transport failure is not a negative answer. A model-generated confidence number is an uncalibrated field unless separately validated.

## Vendor API integration and capability gates

The conversion card illustrates `mlx_vlm.load`, `generate`, `apply_chat_template`, and `load_config` for an image example. Treat it as a starting reference, inspect the pinned installed signatures, and write a narrow adapter rather than copying a mutable README into application logic. The [MLX-VLM repository](https://github.com/Blaizzy/mlx-vlm) is the implementation reference; its support listing does not remove the need to audit prepared frame counts.

Test three modes separately: a single image, an ordered multi-image packet with explicit frame IDs/timestamps, and native video if supported. Multi-image input is a valid deployment baseline but must not be reported as verified native video. Record prompt template and frame ordering; reversing a clip must preserve actual timestamp labeling or deliberately change it under a declared experimental condition.

One heavy model should occupy the worker at a time initially. Use a separate workbench environment, bounded frame count, bounded output tokens, and a subprocess that can be terminated after a deadline. Python-level request timeout is insufficient if GPU generation continues in the background. Record timeouts as observed failures and reclaim the worker before the next case.

## Parsing and grounding checks

Request a compact JSON answer, but assume that malformed text, extra fields, invalid enums, and invented citations can occur. Validate against a strict schema, reject out-of-packet evidence IDs, reject an entity ID different from the request binding, and reject temporal claims extending beyond the packet. An optional one-time formatting repair consumes the same request budget and cannot add new evidence.

```python
# Pseudocode for the trusted response boundary.
raw = worker.generate(packet, prompt, limits)
parsed = parse_strict_json(raw)
if not schema_valid(parsed):
    return invalid("response_schema", raw)
if not set(parsed.evidence_ids) <= set(packet.frame_ids):
    return invalid("invented_citation", raw)
if parsed.answer != "unknown" and not parsed.evidence_ids:
    return invalid("unsupported_answer", raw)
return proposal(parsed, packet.hash, model_spec.hash)
```

Citation validity proves only that the cited frame exists. It does not prove the frame supports the claim. The comparison set must include human/reviewed checks of support. Keep factual correctness, citation validity, answer coverage, and runtime success as separate metrics.

### Decision: typed proposals instead of final rule verdicts

- **Context:** A fluent model can make unsupported temporal inferences.
- **Options considered:** Ask for a final violation judgment, parse unrestricted prose, or request a focused predicate proposal.
- **Decision:** Return focused typed proposals with evidence IDs and explicit failure states.
- **Rationale:** Deterministic code can enforce bounds and evaluate the actual rule later.
- **Consequences:** The caller must formulate smaller questions; schema validity alone is not factual verification.
- **Status:** proposed.

## Matched comparison protocol

Create a fixed set of at least 12 initial question/evidence pairs spanning open, closed, occluded, and insufficient-temporal-coverage cases for both appliances. Expand only after the pipeline works. Development questions choose prompt format and frame budget; hold-out questions are frozen before comparison. Do not use the model's own explanation to label its answer correct.

Each model receives identical decoded evidence, a neutral question, the same output schema, and equivalent resource limits. Preserve a record of actual preprocessing differences. Run no-verifier as a downstream baseline in VIDEO-RULES-001; this runtime ticket reports per-request behavior without pretending to measure full-system recall.

Report answer accuracy on reviewed answerable cases, abstention on unanswerable cases, unsupported-answer rate, invalid-schema rate, invented-citation rate, timeout rate, p50/p95 latency, and peak measured memory. Show raw counts because the initial sample is small. Stratify native-video and multi-image modes. Deterministic decoding settings do not guarantee bit-identical behavior; retain repeated-case results.

## Implementation phases and acceptance gates

### V1 - Candidate provenance and load gate

Create `verifiers/base.py`, an isolated environment lock, and model specification records. Resolve both checkpoints and inspect actual loading/processing APIs. Start with one local image per model and record success or exact failure. Exit with a complete provenance table and a practical memory/frame budget; a download alone does not pass the gate.

### V2 - Bounded evidence adapter

Implement `verifiers/mlx.py`, packet validation, worker timeout/restart, and instrumentation for actual visual inputs. Test wrong entity, out-of-range frame, future evidence, empty packet, oversized input, and timeout. Exit when a failed request cannot leave the next request using stale worker state.

### V3 - Strict output boundary

Implement `verifiers/schema.py` and preserve raw responses separately from validated proposals. Add malformed JSON, absent citations, fabricated frame IDs, and excessive output fixtures without loading a model. Exit when invalid text cannot silently become a false boolean fact.

### V4 - Comparison and integration handoff

Freeze the question set, run both models sequentially, and write the comparison table with failure examples and resource costs. Hand off a versioned adapter, accepted modes, reproduction commands, and a clear compatibility verdict to VIDEO-RULES-001. If one candidate cannot run after two focused compatibility attempts, report that failure and retain the working baseline; do not switch to a remote service without changing the experiment scope.

## Worked example and limits

A request shows a microwave at 5.2 and 6.1 seconds, but the door is hidden in both frames. A useful verifier answers unknown. An answer such as "it must have been closed because the person left" is an unsupported inference from procedural expectation. Even if the final simulator graph is CLOSED, those pixels do not independently verify the claim. This distinction is why the packet validator and the factual-support evaluation are separate parts of the system.

## Shared system contract and reading map

This guide is a design for future implementation. Existing evidence is the root `src/virtualhome_corpus/` package and the validated assets under `output/virtualhome-corpus/home-v1`. Proposed application modules live under `workbench/src/video_workbench/`, preserving the umbrella guide's layout. Proposed APIs and pseudocode are not installed commands or claims of completed model behavior.

Use integer microseconds, half-open event intervals, opaque episode IDs, and source/producer hashes. Keep event time distinct from evidence/result availability and durable commitment. Keep model-safe inputs separate from evaluator labels. A model-space hash must identify preprocessing as well as weights. Unknown evidence remains unknown until a declared policy and new evidence justify a revision.

The existing corpus is a within-scene starter set, with weak action interiors and endpoint world truth. Exact temporal and dense visual-state metrics require reviewed labels; larger datasets do not remove that requirement. Model/runtime references were checked on 2026-09-06. Pin actual installed versions during implementation rather than assuming a mutable documentation page matches the environment.

### Existing file references

- [Existing generator contracts](../../../../../../src/virtualhome_corpus/core.py): lines 55, 102, and 167: planning, weak intervals, endpoint truth.
- [Existing rendering/export lifecycle](../../../../../../src/virtualhome_corpus/runner.py): lines 54, 125, 202, and 228: annotation quality, generation, validation, indices.
- [Checked v1 experiment](../../../../../../configs/virtualhome-household-v1.json): families, variants, groups, and camera.
- [Corpus operational playbook](../../../../../../docs/playbook/virtualhome-corpus.md): generation, resume, validation, and gallery.
- [Validated corpus report](../../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/design-doc/03-virtualhome-household-corpus-design-and-generation-report.md): observed results and label limitations.

### Ticket dependencies

- No prerequisite model implementation; use the existing corpus and shared schema agreements.
