---
Title: Intern analysis design and implementation guide
Ticket: COSMOS-EMBED-001
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
Summary: Prove text, image, and video embedding behavior and freeze a feature-space contract.
LastUpdated: 2026-09-06T13:13:50.883389-04:00
WhatFor: ""
WhenToUse: ""
---


# Embedding runtime baseline on MLX

## Purpose and first-day orientation

This ticket answers a concrete prerequisite: can this Mac turn text, images, and short household video windows into compatible numerical vectors with a documented cost? An embedding is a fixed-length vector whose geometry is intended to preserve useful similarity. It is neither an action label nor a probability that a procedure was correct. Before building search or training a classifier, we must establish exactly which inputs produced each vector and whether the runtime actually consumed the video frames.

The deliverable is a small tested adapter, an immutable feature-space specification, and a measured smoke report. Successful completion may select native video embeddings, or explicitly select pooled image embeddings while recording why native video failed. It does not require a favorable benchmark result. Training the encoder, serving a network API, and implementing search belong outside this ticket.

Read the existing corpus playbook first, open the local gallery, and compare a fridge closure episode with an omission episode. Then trace `runner.py:228` to see that `inputs.jsonl` contains video identifiers, paths, splits, and hashes, while evaluator labels are separate. The present implementation is a generator; there is no production model adapter in `src/`. All `workbench/` paths below are proposed additions.

## Existing evidence and feasibility assumptions

We have 24 validated VirtualHome recordings at 640x480 and 10 FPS. Their total duration is 426.1 seconds, split by initialization group into 12 training, six development, and six test episodes. They are a manageable integration fixture, not an independent-home benchmark. The M1 Max has 64 GB unified memory according to the umbrella hardware investigation; usable inference memory and speed must be measured in a fresh run.

The official [Qwen embedding model card](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B) describes text/image/video inputs and configurable embedding dimensions. The [MLX-VLM maintainer README](https://github.com/Blaizzy/mlx-vlm) lists Qwen3-VL-Embedding support. These establish candidates, not verified video support on this installation. Inspect the pinned runtime's embedding implementation before selecting pooling or writing a call adapter. A failed attempt to browse a guessed embedding subdirectory is not API evidence; use the repository's actual tree at the chosen revision.

Keep the existing VirtualHome environment intact. Create a separate workbench environment when implementation begins, record its Python and package versions, and pin a model revision and conversion provenance. No model download or benchmark has been performed for this design ticket.

## System boundaries and vocabulary

A decoder converts compressed video into RGB frames and presentation timestamps (PTS). A sampler chooses a reproducible subset of those frames. A processor applies model-specific resizing, tokenization, and video packaging. The encoder performs neural inference; a pooling rule maps token outputs or per-frame embeddings to one vector. Normalization divides by vector length so dot product becomes cosine similarity. The cache stores the vector together with the specification of this entire transformation.

```text
inputs.jsonl -> hash-checked video -> PTS decoder
                                      |
                                  RGB samples
                                      |
text queries ------------------> model adapter
                                      |
                               finite float32 vector
                                      |
                             FeatureSpace + cache row
```

Two vectors with the same length are not necessarily comparable. Model revision, quantization, prompt template, preprocessing, pooling, output dimension, and normalization together define a feature space. The adapter must return its space identifier; downstream code must reject a query vector from another space.

## Proposed contracts and module ownership

This ticket owns the initial `workbench/pyproject.toml`, `src/video_workbench/contracts.py`, `embeddings/base.py`, `embeddings/qwen_mlx.py`, `sampling.py`, and a runtime smoke CLI. Project 1 will extend ingestion and persistence; agree on the small records below before independently creating incompatible schemas. Here and elsewhere, package-relative paths live under `workbench/`.

```python
# Proposed application protocol, not a vendor API.
class EmbeddingBackend(Protocol):
    def specification(self) -> FeatureSpace: ...
    def encode_text(self, texts: list[str]) -> FloatMatrix: ...
    def encode_image(self, images: list[RGBImage]) -> FloatMatrix: ...
    def encode_video(self, clips: list[SampledClip]) -> FloatMatrix: ...

@dataclass(frozen=True)
class SampledClip:
    episode_id: str
    start_us: int
    end_us: int
    frames: tuple[RGBImage, ...]
    source_pts_us: tuple[int, ...]
```

`FloatMatrix` is an owned, materialized float32 array with shape `[batch, dimension]`. Reject empty batches where unsupported, empty clips, inconsistent dimensions, nonfinite values, zero-norm vectors, and unsorted timestamps. Do not silently replace failed video requests with text-only inference. A fallback must have a different backend mode and feature-space hash.

`FeatureSpace` should include schema version, model repository and resolved revision, weight/conversion hash, runtime versions, quantization, processor configuration hash, instruction template hash, modality mode, sampling policy, frame cap, pooling rule, dimension, dtype, and normalization. Serialize it canonically, hash it with SHA-256, and retain the complete JSON. The existing `core.py:12` illustrates canonical hashing; avoid importing simulator concerns into the new package just to reuse a few lines.

A feature row adds source video hash, episode ID, half-open window, actual selected PTS values, embedding array checksum, and computation timestamps. The space hash names a transformation; the row key also identifies the transformed input. Text queries need the same model-space rules but a text-input hash rather than a video-window hash.

## Sampling and native-video verification

For a window `[2_000_000, 5_000_000)` sampled at 2 FPS, target times are 2.0, 2.5, 3.0, 3.5, 4.0, and 4.5 seconds. Select actual decoded frames by a documented nearest-time policy, break ties deterministically, and record the selected PTS. Keep requested times separate from actual times. Variable-frame-rate videos cannot use `frame_index / nominal_fps` as their universal clock, even though that arithmetic is valid for the current fixed-rate corpus.

Start with one image and a two-second clip, batch size one, and a conservative frame cap. Increase duration only after measuring working memory. In the runtime adapter, inspect processor outputs or instrumentation to establish that multiple visual frames and their timestamps reached the model. Then compare the same sequence in original order, reversed order, and repeated-frame form. An unchanged vector is a diagnostic result, not proof that all video support is absent; an order-sensitive vector is not proof of temporal reasoning.

```python
# Pseudocode: vendor invocation is isolated in the adapter.
clip = sample_pts(video, start_us, end_us, sampling_policy)
assert len(clip.frames) == len(clip.source_pts_us)
prepared = adapter.prepare_video(clip)
audit_prepared_frame_count(prepared, len(clip.frames))
t0 = monotonic()
raw = adapter.forward(prepared)
adapter.materialize(raw)  # force lazy work to finish
vector = adapter.pool_and_normalize(raw)
assert finite(vector) and abs(norm(vector) - 1) < 1e-4
elapsed = monotonic() - t0
persist(vector, clip, adapter.specification(), elapsed)
```

The [MLX lazy-evaluation documentation](https://ml-explore.github.io/mlx/build/html/usage/lazy_evaluation.html) explains why timing only Python dispatch can undercount work. Use the pinned runtime's supported evaluation/materialization mechanism; report cold load, warm preprocessing, inference, and serialization separately. Measure process memory and supported MLX allocator statistics without pretending they represent disjoint pools on unified memory.

## Baseline modes and interpretation

Native-video mode processes an ordered sampled clip using a verified video path. Frame-pooled mode embeds each frame independently, averages the frame vectors, and renormalizes the result. They get distinct space IDs even if they use identical weights. Mean pooling is deliberately insensitive to frame order and can provide a useful semantic search baseline. It cannot establish that one action preceded another.

Include identical-input repeatability, unrelated text/image comparisons, a text-only control, and open/closed image pairs selected from the training group. The acceptance threshold for repeatability should account for the chosen precision and be recorded before the held-out run. Do not require a particular open/closed accuracy as a runtime gate; that question belongs to Project 2.

### Decision: start with a local Python adapter

- **Context:** Runtime feasibility is unknown and the dataset is small.
- **Options considered:** Python calls, a local HTTP model server, or a remote embedding service.
- **Decision:** Use a pinned Python adapter and one heavy model at a time.
- **Rationale:** It exposes preprocessing and synchronization directly while avoiding server lifecycle ambiguity.
- **Consequences:** Later serving needs an adapter wrapper; application code must depend on the protocol rather than vendor objects.
- **Status:** proposed.

### Decision: preserve separate modality modes

- **Context:** A video path may fail even when image encoding succeeds.
- **Options considered:** Silent image pooling, blocking all downstream work, or a named fallback.
- **Decision:** Allow a named frame-pooled baseline with its own space hash.
- **Rationale:** It preserves useful progress and honest experiment interpretation.
- **Consequences:** Evaluation tables must compare modes explicitly; caches cannot be mixed.
- **Status:** proposed.

## Implementation phases and acceptance gates

### E1 - Environment and model provenance

Create the isolated environment, record supported Python/runtime versions, and resolve a small model checkpoint to an immutable revision. Save model-card links, conversion lineage, package lock, hardware snapshot, and download size. Inspect the actual installed embedding entry point and document its signature. Exit when another engineer can identify exactly which bytes and processor implementation will run; loading weights alone is not completion.

### E2 - Contracts and deterministic sampling

Implement `contracts.py`, `sampling.py`, and tests using a tiny synthetic PTS fixture with duplicates, irregular spacing, and a truncated final window. Reject invalid intervals and ensure sample selection never crosses the requested window. Implement vector validation and canonical feature-space serialization. Exit when modality mismatch, hash changes, and corrupt input fixtures fail clearly without model inference.

### E3 - Adapter and capability smoke

Implement the three adapter methods and the explicitly named fallback. Run text, image, and native-video smoke cases with one training episode. Audit prepared visual inputs, normalize vectors, record dtype/dimension, and test the original/reversed/repeated clip controls. Exit with a capability matrix that includes failures and their exact exceptions.

### E4 - Resource report and handoff

Benchmark short and longer windows, one cold run and at least five warm runs per selected configuration. Record selected PTS, frame count, preprocessing/inference time, total wall time, memory, and real-time factor (wall seconds / video seconds). Publish recommended conservative defaults and a stop condition for memory pressure or unsupported operators. Give Project 1 a pinned spec, a small cache fixture, and a reproduction command. A CPU fallback must be labeled and remeasured.

## Review checklist and failure handling

A reviewer should deliberately change model revision, prompt text, pooling, and frame cap and confirm that the feature-space or input identity changes appropriately. Kill a cache write and ensure no partial array is considered complete. Feed a zero vector and confirm normalization fails rather than dividing by zero. Inspect a manifest to ensure family/variant labels are absent from model inputs.

The first useful downstream artifact is not a large vector database. It is a small set of vectors whose semantics, source frames, and cost can be explained without relying on hidden defaults. If native video remains unsupported after two focused adapter attempts, record the evidence and hand off frame-pooled mode; do not spend the whole project reverse-engineering a runtime before producing an honest baseline.

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
