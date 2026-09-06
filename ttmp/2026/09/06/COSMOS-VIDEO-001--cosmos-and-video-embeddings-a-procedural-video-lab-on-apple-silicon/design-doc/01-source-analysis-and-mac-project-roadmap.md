---
Title: Source analysis and Mac project roadmap
Ticket: COSMOS-VIDEO-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/sources/cosmos-random-notes.txt
      Note: Imported curriculum and simulator proposals
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/sources/video_understanding_for_procedural_work.md
      Note: Imported textbook supplying temporal modeling and evaluation foundations
ExternalSources: []
Summary: Evidence-based synthesis of imported sources and five local projects, with Cosmos and simulator compatibility gates.
LastUpdated: 2026-09-06T11:31:47.451412-04:00
WhatFor: ""
WhenToUse: ""
---


# Source analysis and Mac project roadmap

## Recommendation

Build a local procedural-video research workbench with five cumulative projects: semantic search, state recognition, learned temporal segmentation, a temporal rule investigator, and streaming replay. Add a small synthetic-corpus experiment after the first working video baseline. Use Qwen embeddings as the first representation candidate and Cosmos Reason as a comparison verifier. Keep Cosmos-Embed1 behind a replaceable adapter for a later NVIDIA-hosted comparison.

This is an exploration plan, not a report of model performance. No models or simulators were installed or benchmarked during this investigation.

## Evidence and machine

The inspected machine is a MacBook Pro with Apple M1 Max, 10 CPU cores, 32 GPU cores, 64 GB unified memory, and approximately 329 GiB available storage at inspection. Memory makes modest quantized models and cached-feature experiments plausible; throughput, video preprocessing, and supported operators still require measurement. Unified memory is not CUDA GPU memory.

Imported originals are preserved byte-for-byte in [sources](../sources/). [The manifest](../sources/import-manifest.json) records original paths, sizes, and SHA-256 hashes.

- [Textbook](../sources/video_understanding_for_procedural_work.md): 22 chapters covering labels, embeddings, HMM/HSMM inference, causal TCNs, procedure state, verification, streaming, and evaluation. Most relevant: chapters 3, 5–6, 13–19, and labs 20–21. It explicitly separates research recommendations from illustrative constructions and measured results. Its references to an earlier report are not substitutes for having that report.
- [Random notes](../sources/cosmos-random-notes.txt): a conversational five-project curriculum followed by synthetic-data and simulator proposals. It advocates context-conditioned embeddings, temporal memory, a constrained DSL, recursive evidence gathering, and controlled temporal counterfactuals. Recommendations change from Unity to VirtualHome to Habitat/TDW; treat those as alternatives to test. The file contains stray UI text, retained as part of the original.
- The workspace also contains `procedural_video_labs.zip`; its archive listing includes sequence and neural labs, tests, and recorded outputs. It was inspected by filename listing only, not imported or executed. Reuse should begin with code review and rerunning its tests; historical test output is not a local result.

## What to retain, qualify, and combine

| Source idea | Assessment and project consequence |
|---|---|
| Embeddings can retrieve relevant video | Strong starting experiment. Retrieval quality does not establish step boundaries or correctness. |
| Machine descriptions improve embeddings | A hypothesis to test. Include generic, correct-context, misleading-context, and context-only controls; a null result is useful. |
| Similarity scores are confidence | Reject this interpretation without calibration. Keep raw similarities, margins, calibrated confidence, and observation quality separate. |
| A state persists across chunks | Useful, but stale or occluded evidence must become unknown under an explicit policy. Track entity identity and evidence coverage. |
| TCN plus HSMM/procedure graph | Add after a frozen-feature linear baseline. Retain an unconstrained observation path so a normal-only graph cannot invent a missing step. |
| A VLM investigates uncertain predicates | Useful with bounded calls and typed outputs. Deterministic code evaluates rules; a model's plausible explanation is not independent evidence. |
| Exact timing from sparse video samples | Unsupported. Represent boundary uncertainty; resampling can improve resolution but cannot reveal invisible events. |
| Synthetic state is perfect ground truth | It is exact simulator truth, not necessarily visible truth. Label what is occluded or visually ambiguous separately. |
| Five weeks produces a real-time system | Treat as a rough curriculum estimate. Local real-time capacity is an experimental result, not an assumption. |

The textbook's crucial addition to the notes is a learned temporal baseline between embeddings and procedural logic. Otherwise the curriculum risks testing semantic descriptions and hand-built hysteresis without learning whether features preserve short actions.

## Model and runtime choices

References below were checked on 2026-09-06. These are specific candidates, not claims about the newest or best model in each family.

| Component | Verified evidence | Decision for this Mac |
|---|---|---|
| Qwen3-VL-Embedding-2B | Official card lists text, image, video, mixed inputs, instruction support, and 64–2048 output dimensions. [Qwen card](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B) | First local embedding candidate. Pin preprocessing, model revision, pooling, and normalization. |
| MLX-VLM | Maintainer README lists Qwen3-VL-Embedding among supported embedding architectures. [Runtime](https://github.com/Blaizzy/mlx-vlm) | Validate the actual video path, not just text embeddings or model loading. |
| Cosmos Reason2-2B | NVIDIA describes a physical-reasoning VLM; a conversion author publishes an MLX 8-bit model. [NVIDIA card](https://huggingface.co/nvidia/Cosmos-Reason2-2B), [MLX conversion](https://huggingface.co/hzang/Cosmos-Reason2-2B-8bit) | Bounded local verifier experiment. Community conversion availability does not establish fidelity, video handling, speed, or official Mac support. Compare with a small Qwen VLM on identical evidence. |
| Cosmos-Embed1 | VSS describes joint video/text embeddings; NIM documents CUDA preprocessing and GPU video decoding. [VSS model](https://docs.nvidia.com/vss/3.1.0/models/cosmos-embed1.html), [NIM overview](https://docs.nvidia.com/nim/cosmos-embed1/latest/introduction.html) | Keep the official serving stack as a future NVIDIA-hosted baseline. An Apple port would be a separate investigation. Do not confuse the documented 40 GB training requirement with an inference minimum. |
| Cosmos generation / VSS deployment | Distinct responsibilities from embedding and verification | Defer generation and full infrastructure deployment. Generated video also cannot substitute for exact, independently labeled temporal ground truth. |

Smoke-test gates: embed text, an image, and a short video; confirm finite normalized vectors and stable output dimension; test reversed frame order; record peak memory and seconds per video-second. For a VLM, test video/timestamp handling and structured evidence outputs. Cache embeddings and run one heavy model at a time initially. If video encoding fails, use an explicitly labeled frame-embedding baseline while debugging it; frame pooling is not equivalent to temporal encoding.

## Proposed projects in order

### 1. Searchable video notebook — approximately 3–4 focused days

Start with 10–20 short recordings of one observable tabletop or household procedure. Define episode IDs, half-open intervals in seconds, and labels before extracting features. Build a Python CLI that chunks videos, caches embeddings, and returns playable timestamped matches. Use NumPy cosine search and SQLite metadata initially.

Compare 5/10/20-second windows and 1/2/4 FPS on a small development subset; retain a shorter-window condition for brief actions. Pin the model and preprocessing for each cache. Measure Recall@5, query latency, encoding time, and memory on held-out episodes. An initial engineering target can be 8 of 10 fixed queries retrieving relevant evidence in the top five, explicitly a small smoke benchmark rather than a general performance claim.

Deliverable: a search command, clip viewer, versioned feature cache, and benchmark table. Complete the local runtime gate before broad indexing.

### 2. State-recognition microscope — approximately 3–5 days

Use visually observable predicates such as door open/closed or object present/absent. Compare text-hypothesis similarity, context-conditioned similarity, and a small supervised linear head over frozen features. Include UNKNOWN, visibility labels, and misleading-context controls.

Measure per-predicate precision/recall, macro-F1, abstention coverage, and transition-time error. Fit thresholds on development data and hold out complete recording sessions. Improvement from context is a question, not the required answer.

Deliverable: a state timeline with scores, uncertainty, and clickable evidence; a report identifying which distinctions the embeddings preserve or lose.

### 3. Temporal-learning and memory lab — approximately 4–6 days

On cached short-window features, compare independent linear predictions, hysteresis/HMM, a small causal TCN, and a duration-aware decoder. Reuse reviewed textbook labs where practical. Maintain SQLite events and state intervals per entity with provenance, availability time, and observation coverage.

Use a five-step procedure with skipped steps, repetitions, rework, and camera gaps. Measure segmental F1, edit score, short-action recall, boundary error, and error preservation. Verify that changing future frames does not change committed past output. Treat an offline HSMM as an offline baseline unless ongoing-duration handling is implemented.

Deliverable: learned step segmentation, `state_at(entity, property, time)`, and an ablation showing which temporal component earns its complexity. Train small heads locally before considering encoder fine-tuning.

### 4. Temporal rule investigator, with Cosmos comparison — approximately 4–6 days

Start with a typed JSON rule AST for `before`, `continuously_for`, and bounded absence; add natural-language compilation after deterministic evaluation works. Bind entity roles explicitly. Support PASS, VIOLATION, and UNKNOWN, including unavailable evidence and expired state.

Feed gold facts first to test the engine, then predicted facts. A bounded investigator can retrieve intervals, resample, and ask a focused VLM question. Start with at most three calls per candidate as a tunable engineering budget. Restrict forward evidence to what is available under the replay/lookahead policy. Store proposed fact revisions and provenance rather than overwriting observations silently.

Compare no verifier, a small Qwen VLM, and the Cosmos Reason2 MLX candidate using the same clips and prompts. Measure end-to-end violation precision/recall, unknown rate, VLM calls, and added delay; include candidates missed upstream in system recall.

Deliverable: three executable rules, an evidence report, and a Cosmos-versus-baseline comparison. For a two-second requirement, uncertain estimated stopping/opening boundaries whose interval spans two seconds must yield UNKNOWN or refinement, not a confident arithmetic verdict.

### 5. Replay workbench and real-video transfer — approximately 4–6 days

Replay prerecorded footage at its original availability rate into a rolling buffer. Integrate search, state estimates, segmentation, rules, and focused verification in a timeline UI. Add dropped frames, duplicate events, delayed results, and restarts. Keep event time, evidence availability, and commitment time distinct.

Measure false alerts per hour, missed violations, p50/p95 end-to-end latency, queue growth, and memory during sustained replay. Deduplicate incident updates by stable identity. Compare synthetic/dev performance with untouched staged real footage. Choose live camera settings from measured capacity.

Deliverable: a reproducible demo and failure report. The output is a research observation/incident system; operational adequacy remains a separate evidence question.

## Supporting experiment: counterfactual video corpus

Do this after Project 1 produces real video results. Begin with approximately 20 paired episodes, changing only order, duration, actor, or object identity. Scale toward the notes' 500 episodes only after the pipeline and labels work. Keep related seeds and variations together in dataset splits.

Habitat is the strongest first simulator spike: its HITL requirements explicitly list macOS and Apple M1 Pro/Max, with an attached display and roughly 20 GB for dependencies/data. That is meaningful evidence for this machine, but not a guarantee that a chosen avatar task works without integration. [Habitat HITL](https://github.com/facebookresearch/habitat-lab/blob/main/habitat-hitl/README.md). Habitat-Sim's EGL headless option does not work on macOS. [Habitat-Sim](https://github.com/facebookresearch/habitat-sim).

Timebox installation and one controlled actor/object/video/state export to half a day. If it succeeds, generate paired episodes and an evaluator-only truth stream. TDW is a fallback: its project documents macOS setup and is in long-term support. [TDW](https://github.com/threedworld-mit/tdw/blob/master/README.md). VirtualHome remains a candidate from the notes, but packaged Apple Silicon compatibility was not verified here. Do not make the first three projects depend on any simulator.

Prerecorded BEHAVIOR clips are another possible source, but the notes' exact dataset/version counts, accessible downloads, licensing, and alignment between video and state labels were not verified. Start with a small inspectable sample if pursuing this route. A factory environment is optional; household actions can exercise the same temporal semantics.

## Shared experiment contract

1. Separate observed action, world-state evidence, procedural expectation, and final decision.
2. Define train/development/test by episode, actor/session, and simulator seed family; never randomly split overlapping chunks across them.
3. Store actual source timestamps and available-at times. Do not infer exact boundary precision from coarse chunks or model narration.
4. Keep simulator truth outside inference inputs except in explicitly labeled oracle tests.
5. Version video hashes, annotations, prompts, model/runtime revisions, quantization, sampling, pooling, and output dimension. Never mix vector spaces in one index.
6. Report retrieval, predicate, segment, rule, and streaming metrics separately. Fit calibration and thresholds without the final holdout.
7. Bound downloads and cache growth initially; disk is shared with the rest of the machine. Model weights fitting in RAM does not imply sustained real-time inference.

## Next decision

Start Project 1 with a local Qwen embedding video smoke test and a tiny recorded corpus. In parallel as a scheduling option, not a prerequisite, run the bounded Cosmos verifier compatibility spike. The expected program is roughly four to six focused weeks plus data collection and setup uncertainty; project durations above are planning estimates.
