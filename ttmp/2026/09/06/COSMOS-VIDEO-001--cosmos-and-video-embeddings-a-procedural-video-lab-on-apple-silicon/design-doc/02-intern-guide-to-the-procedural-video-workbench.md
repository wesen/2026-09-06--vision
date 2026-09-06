---
Title: Intern guide to the procedural video workbench
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
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/sources/procedural_video_labs/neural_lab.py
      Note: Verified causal TCN signatures and tensor shapes
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/sources/procedural_video_labs/sequence_lab.py
      Note: Verified sequence algorithms and limitations
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/sources/video_understanding_for_procedural_work.md
      Note: Conceptual and mathematical foundations
ExternalSources: []
Summary: A technical onboarding, architecture, and implementation guide for building a local procedural-video research system.
LastUpdated: 2026-09-06T12:00:00-04:00
WhatFor: Teach a new intern the concepts, contracts, algorithms, and implementation sequence.
WhenToUse: Read before implementing the video workbench and when reviewing each project milestone.
---


# Intern guide to the procedural video workbench

This system turns a recording of a procedure into searchable evidence, a timeline of observed actions and object states, and explicit judgments about procedural rules. Your job is to build an inspectable research application in which each judgment can be traced back to video and each component can be evaluated independently.

The first implementation targets the MacBook Pro inspected for this ticket: Apple M1 Max, 10 CPU cores, 32 GPU cores, and 64 GB unified memory. It begins with recorded video, frozen pretrained models, small supervised models, and local files. The central research question is whether semantic video embeddings preserve enough detail to support procedural reasoning, and whether temporal models and focused Cosmos verification improve the result.

**Implementation status:** the ticket contains research documents, imported sources, and extracted teaching labs. The application modules and application APIs described below are a proposed design. They do not exist yet. Code blocks labeled pseudocode specify behavior; they are not a claim that an installable package already implements that behavior. Vendor references were checked on 6 September 2026; pin the actual versions when you implement adapters.

> Planning update: the user selected VirtualHome on 2026-09-06. Simulator alternatives below are historical; the active implementation plan is [the child ticket map](04-project-ticket-map-and-intern-reading-order.md) and VIDEO-CORPUS-001. The previously uploaded umbrella PDF predates this update.

## 1. The problem, through one complete example

Suppose a recording shows a person operating a demonstration machine. The relevant rule is: the machine must be stopped continuously for at least two seconds immediately before its guard opens. This is a teaching scenario. The same implementation can use a household activity, an assembly procedure, or a staged tabletop mechanism with visible state indicators.

The camera observes a stop-button press at 10.0 seconds, visible motion ceasing somewhere between 10.8 and 11.0 seconds, and the guard opening between 12.7 and 12.9 seconds. A button press is an action. A stopped machine is a state. The required two-second interval is a procedural condition. These are different propositions, and recognizing the first does not prove the second or third.

```text
Episode E17, machine M1, worker W1

10.0       10.8 11.0              12.7 12.9
  |           [stop boundary]        [open boundary]
  v
press stop     machine stationary     guard opens

Shortest possible stopped duration = 12.7 - 11.0 = 1.7 s
Longest possible stopped duration  = 12.9 - 10.8 = 2.1 s
Required duration                 = 2.0 s

Result: UNKNOWN; the evidence spans the threshold.
Next action: inspect more frames near both boundaries.
```

If higher-resolution review narrows the stop boundary to [10.90, 10.95] and the open boundary to [12.75, 12.80], the longest possible duration is 1.90 seconds. Under continuous adequate observation, that supports a violation. If the camera was obstructed during the interval, the system must preserve the gap and may remain unknown. More confident language from a model cannot repair missing observation.

The application should eventually show the rule, bound entities, estimated boundary intervals, arithmetic, evidence frames, and decision revision. That display is the end-to-end contract you should keep in mind while implementing the lower-level pieces.

### 1.1 Vocabulary used throughout the guide

- An **episode** is one identified execution of a procedure. It is the unit of labeling, replay, and most dataset splits.
- A **clip** is a bounded interval extracted from an episode. Clips may overlap.
- An **embedding** is a vector computed from text, images, or video. Its coordinates encode learned information useful for a model's training objective.
- An **action segment** assigns an action label to an interval, such as opening a guard.
- A **state fact** assigns a property value to an entity over an interval, such as M1 being stopped.
- A **predicate** is a proposition the rule engine can evaluate as true, false, or unknown.
- An **incident** is a durable, versioned record of a candidate or supported procedural error. Repeated detections need not create new incidents.
- A **VLM**, or vision-language model, consumes visual evidence and language and produces language or structured outputs. An embedding model and a VLM have different output contracts.

### 1.2 Four outputs that must remain separate

Recognition answers what action is visible. Segmentation answers where that action begins and ends. State estimation answers what is established about an entity. Procedural reasoning answers whether those established facts satisfy a rule. A system can be correct at one level and wrong at another.

For example, a model may retrieve the right clip for “tightening a fastener” while failing to distinguish left from right. A temporal decoder may produce a plausible normal sequence while incorrectly inserting a step that was skipped. A rule engine may apply the right arithmetic to a boundary estimated from the wrong machine. Independent interfaces and independent evaluation reveal these failures.

## 2. Architecture and ownership

Start with a Python package and one local SQLite database. The initial application needs neither a distributed event bus nor a collection of independent network services. Use explicit module interfaces so that a component can later run in another process without changing its meaning.

```text
                    VIDEO + EPISODE MANIFEST
                              |
                     decode and sample
                              |
               +--------------+--------------+
               |                             |
         semantic clips                short causal clips
               |                             |
         embedding adapter             feature adapter
               |                             |
         vector cache/index          linear head / TCN
               |                             |
      text ---> search                  action/state evidence
               |                             |
               +--------> evidence store <---+
                              |
                       temporal state store
                              |
                         rule evaluator
                              |
                    candidate / unknown result
                              |
                     bounded investigator
                              |
                 focused Qwen / Cosmos VLM
                              |
                   validated fact proposals
                              |
                   reconciliation + reevaluation
                              |
                       incident revisions
                              |
                        timeline viewer
```

The two feature branches need not use different encoders initially. They have different temporal contracts: a broad retrieval clip is useful for locating a scene, while a short causal clip is designed to preserve action timing. Sharing an encoder does not make their cached outputs interchangeable.

The database owns durable records; the model adapters own model-specific preprocessing; the temporal store owns reconciliation and state validity; the rule evaluator owns logical conclusions. The investigator can request new evidence but cannot declare that an arbitrary generated sentence is a verified fact. The viewer reads these outputs and does not recompute procedural logic in JavaScript.

### 2.1 Proposed module layout

The following paths are **implementation targets under a future `workbench/` package**, not existing files. Create modules as their milestone requires them.

```text
workbench/
  pyproject.toml
  src/video_workbench/
    cli.py                  command entry points
    contracts.py            IDs, intervals, typed records
    ingest.py               manifests and video metadata
    sampling.py             PTS-aware frame selection
    cache.py                feature keys and atomic writes
    embeddings/base.py      encoder protocol
    embeddings/qwen_mlx.py  local embedding adapter
    embeddings/cosmos.py    optional remote NIM adapter
    retrieval.py            cosine ranking and evidence hits
    predicates.py           state classifiers and abstention
    temporal/tcn.py         causal neural model
    temporal/decoder.py     HMM/HSMM baseline adapters
    temporal/store.py       fact reconciliation and history
    rules/ast.py            validated rule representation
    rules/evaluate.py       deterministic temporal evaluation
    investigation.py        bounded evidence requests
    verifiers/base.py       structured verifier protocol
    verifiers/mlx.py        local Qwen/Cosmos implementation
    incidents.py            lifecycle and idempotency
    replay.py               availability clock and queues
    api.py                  local viewer endpoints
    evaluation.py           metrics and experiment reports
  migrations/001_initial.sql
  configs/
  tests/
  ui/
```

Keep downloaded weights, videos, and derived arrays outside Python source directories. A run manifest should point to those assets by content hash and path. A successful experiment is reproducible from its source revision, configuration, split manifest, and referenced assets; the trained checkpoint alone is insufficient.

### 2.2 One writer and bounded model work

The first implementation should serialize SQLite writes through a repository object or one writer queue. A worker can decode frames and another can compute embeddings, but they should return typed results to the writer. This makes transaction boundaries, retries, and duplicate handling easier to reason about.

Run one large model at a time initially. MLX inference and PyTorch training share physical memory and compute resources on this Mac. Caching features allows you to unload the encoder before training the TCN. Add concurrency only after measuring whether it improves throughput without excessive memory pressure or queue growth.

## 3. Dataset design before model code

Choose one procedure with about five visually distinguishable steps. The textbook's bracket example is suitable: pick, align, insert, tighten, inspect. Include valid executions, a skipped step, a repeated step, rework, background activity, and an observation gap. Distinguishing these cases forces the labeling and rule contracts to be explicit.

Record ground truth in a separate annotation file. A useful record includes episode and procedure version, action intervals, actor and object IDs, state changes, visibility intervals, and error labels. Document how a human annotator decides each boundary. If two annotators cannot agree whether a state is visible, a model accuracy number against an arbitrary label is misleading.

```yaml
# Proposed episode manifest; paths are illustrative.
episode_id: E17
procedure_version: guard-demo-v1
video_path: videos/E17.mp4
video_sha256: HASH_OF_VIDEO_BYTES
split_group: recording-session-03
entities:
  - id: M1
    kind: machine
  - id: W1
    kind: person
annotations_path: annotations/E17.json
```

Do not put the answer into a machine description supplied to the model. “A green lamp indicates operation” describes an observation convention. “The machine is running in this clip” provides the target. Simulator state and annotation files must be available to the evaluator while remaining inaccessible to inference, except during a clearly labeled oracle test.

### 3.1 Split complete sources, then generate clips

Make training, development, and test assignments before extracting overlapping windows. Otherwise a training clip can contain almost the same frames as a test clip. Group recordings from the same session and synthetic variations from the same underlying scenario together. Hold out actors or camera arrangements when testing generalization to those conditions.

Development data selects thresholds and architectures. Training data fits parameters. The final test set estimates performance after decisions are frozen. With a small corpus, document grouped cross-validation rather than pretending three tiny partitions produce a stable operational estimate.

### 3.2 An initial corpus and a controlled expansion

Ten to twenty short videos are sufficient for a pipeline smoke test, not a reliable industrial benchmark. Begin with a small fixed set of search queries and explicit relevant intervals. Expand only after failures can be inspected and labels are stable.

For synthetic data, generate pairs whose appearance is held constant while timing or order changes. Keep the pair ID in the split group. A simulator's world state may be exact even when the camera cannot see the state transition; therefore record both world truth and visibility. The rule engine's behavior on gold world facts and the perception system's behavior on pixels are separate experiments.

## 4. Time, intervals, and video decoding

Time is part of the model input contract. A frame index is not a timestamp, a clip endpoint is not necessarily a prediction time, and event time is not processing time. Many apparent reasoning errors are actually timestamp or alignment errors.

Use integer microseconds for persisted episode-relative time. Convert decoder presentation timestamps using their rational time base, then normalize to the chosen episode origin. Preserve original PTS and time base for debugging. PyAV exposes frame `pts`, `time_base`, and `time`; its frame documentation explains these fields. [PyAV frame API](https://pyav.org/docs/stable/api/frame.html)

A frame with missing PTS needs an explicit policy: reject the episode, reconstruct timing from verified constant-rate metadata, or mark reconstructed timestamps. Do not silently use frame number divided by a nominal rate for variable-frame-rate footage.

### 4.1 Half-open intervals and availability

Use `[start_us, end_us)` for all nonempty intervals. Two adjacent segments can then meet without double-counting their boundary. Represent a detected point event's uncertainty separately as `earliest_us` and `latest_us`; these are bounds on an unknown event time, not a video segment.

Every feature record has at least three temporal fields:

- `support_start_us` and `support_end_us` identify the video that contributed to it.
- `anchor_us` is the temporal position being predicted or indexed.
- `available_at_us` is when the application could first use the result under replay, including decoding and inference delay.

For causal prediction, every supporting frame must have a timestamp no later than the anchor. A window supporting `[8, 10)` can be anchored at 10 seconds and become available at 10.4 seconds. Anchoring it at 9 while claiming zero lookahead is incorrect.

### 4.2 Sampling algorithm

Sampling frequency controls which frames enter the model; feature stride controls how often a vector is produced; clip width controls how much video each vector summarizes. Keep these as separate configuration fields. For example, a two-second clip sampled at four FPS and advanced every half second produces overlapping features from approximately eight frames each.

```python
# Pseudocode: presentation-order causal sampling.
def sample_window(frames, start_us, end_us, fps):
    targets = grid(start_us, end_us, period_us=1_000_000 / fps)
    chosen = []
    for target in targets:
        frame = latest_frame_at_or_before(frames, target)
        if frame is None or frame.time_us < start_us:
            return MissingEvidence("no suitable source frame")
        if target - frame.time_us > allowed_sample_age_us:
            return MissingEvidence("source gap")
        chosen.append((frame.id, frame.time_us, frame.rgb))
    return SampledClip(chosen, start_us, end_us)
```

Repeated frame IDs are possible when requested FPS exceeds source FPS. Record the duplication so the benchmark does not confuse repeated images with additional motion evidence. Seek to an earlier keyframe when needed, decode forward, and filter by actual timestamps. A compressed-video seek does not guarantee an exact frame boundary.

## 5. Embeddings, similarity, and feature caches

An encoder maps an input into a vector `e` with `D` coordinates. A compatible text encoder maps a query into a vector in the same learned space. Cosine similarity compares vector directions: divide their dot product by the product of their lengths. If both vectors are normalized to unit length, their dot product is already cosine similarity.

```python
# Pseudocode; NumPy-like operations.
def normalize(v):
    require(all_finite(v))
    n = sqrt(sum(v * v))
    require(n > 1e-12)
    return v / n

def search(query, matrix, clip_ids, k):
    # matrix: [number_of_clips, D], normalized row-wise
    q = normalize(encoder.embed_text(query))
    require(q.shape == (matrix.shape[1],))
    scores = matrix @ q
    order = stable_sort_descending(scores)[:min(k, len(scores))]
    return [(clip_ids[i], float(scores[i])) for i in order]
```

A similarity of 0.81 is a ranking score, not an 81 percent probability that an action occurred. Different queries can have different score distributions. Start by inspecting ranked results and measuring retrieval recall, then evaluate classification separately.

### 5.1 Qwen adapter contract

Qwen3-VL-Embedding is the first candidate because its official materials describe text, image, video, and mixed inputs with configurable instructions. The official repository's Transformers example uses `Qwen3VLEmbedder` from `src.models.qwen3_vl_embedding`, followed by `model.process(inputs)`. This import is from that repository, not an API guaranteed to exist in a generic Transformers installation. [Qwen implementation reference](https://github.com/QwenLM/Qwen3-VL-Embedding)

The local application should depend on its own small protocol. The MLX adapter translates this protocol to the pinned runtime and preserves the model's expected preprocessing and embedding extraction. MLX-VLM documents native embedding endpoints and lists Qwen3-VL-Embedding support, but architecture support alone does not validate our video inputs or timestamp handling. [MLX-VLM reference](https://github.com/Blaizzy/mlx-vlm)

```python
# Proposed internal protocol, not a vendor API.
class VideoEmbedder:
    def describe(self) -> EncoderSpec: ...
    def embed_text(self, text, instruction) -> Vector: ...
    def embed_video(self, sampled_clip, instruction) -> Vector: ...

class EncoderSpec:
    model_id: str
    model_revision: str
    runtime_version: str
    quantization: str
    output_dimension: int
    preprocessing_hash: str
    extraction_method: str
    normalized: bool
```

The first integration must compare a small reference set against the documented extraction behavior. Normal-looking vectors do not prove correctness: using the wrong token, omitting the visual input, or changing the prompt template can silently damage retrieval. Test text, image, video, a changed video, and a frame-order reversal. Reversal is a diagnostic; a model returning similar vectors may reveal a representation limitation rather than a software bug.

### 5.2 Cache identity and atomicity

An embedding cache key must identify more than a video filename. Include the video hash, interval, exact sampled frame timestamps, encoder specification, instruction text, resize/crop configuration, and vector dimension. Changing any of those creates a different feature space or a different observation.

Write arrays to a temporary path, validate shape and finite values, then atomically rename them into their final content-addressed location. Commit the SQLite row only after the final artifact exists. On restart, orphan temporary files can be cleaned and completed hashes reused. Never attach a new model's text query to an old model's video matrix merely because both vectors have the same dimension.

For scale intuition, 10,000 float32 vectors with 2,048 dimensions require 81,920,000 bytes, about 78 MiB, before metadata. That is manageable locally. Decoded video tensors and model activations are likely to be more expensive than the initial vector index, so measure those first.

### 5.3 Retrieval output and evidence navigation

Return episode ID, source clip interval, score, encoder identity, and a stable clip ID. Search can return several overlapping hits from the same event; expose raw hits for evaluation and optionally group nearby intervals for the viewer. Keep grouping rules fixed so a cosmetic change does not silently alter Recall@K.

A search result is a pointer to evidence. It should open the original episode at the matching interval, not only a generated caption. Text descriptions can help browsing but should not replace the source frames needed to verify a judgment.

## 6. State recognition and text-context experiments

To estimate a property such as open versus closed, first compare two text hypotheses against the same clip vector. Let the margin be similarity to “guard open” minus similarity to “guard closed.” Positive values favor open; negative values favor closed. Learn useful thresholds from labeled development clips rather than assigning semantic meaning to zero by assumption.

A more informative baseline fits a linear classifier over frozen embeddings. With feature matrix `E` shaped `[T, D]`, weight matrix `W` shaped `[D, C]`, and bias `[C]`, the logits are `E @ W + b`, shaped `[T, C]`. Softmax normalizes scores over the known classes, but it can still be overconfident on an unfamiliar or occluded input.

```python
# Pseudocode: keep visibility separate from class competition.
def classify_state(feature, visibility, classifier, calibration):
    if visibility != "adequate":
        return Unknown(reason="insufficient observation")
    logits = classifier(feature)
    probabilities = calibration.apply(logits)
    best, runner_up = top_two(probabilities)
    if best.value < threshold or best.value - runner_up.value < margin:
        return Unknown(reason="ambiguous state")
    return StateProposal(best.label, best.value)
```

The thresholds, margin, and calibration are selected parameters, not universal constants. Include UNKNOWN in the application output even when the trained classifier predicts only known physical states. Report the fraction of clips on which the system abstains; a model that refuses nearly everything can have deceptively high accuracy among accepted predictions.

### 6.1 Test whether context helps or supplies an answer

Run matched conditions using the same clips and splits: no context, a generic task instruction, an accurate description of visible indicators, an incorrect description, and context without video. The final control tests whether text alone predicts labels through an accidental correlation.

Each instruction-conditioned video representation needs a compatible retrieval or classification protocol. Do not assume similarities from different instruction spaces are directly comparable. Fit and report a separate decision rule for each condition where appropriate, and preserve exact prompt strings in the run manifest.

## 7. Temporal models: what each additional layer buys

Independent frame or clip predictions do not explicitly model persistence, order, or action duration. A sequence model uses neighboring evidence to make a temporal estimate. This can reduce noisy fragmentation, but it can also hide a brief real action or force an unusual execution into a normal pattern.

Use cached features so experiments change the temporal model while keeping visual evidence fixed. Begin with independent predictions, add hysteresis or an HMM, then a small causal TCN. Add an HSMM comparison when explicit durations matter. Evaluate ordinary executions and procedural mistakes separately.

### 7.1 Hysteresis and hidden Markov models

Hysteresis uses different evidence thresholds for entering and leaving a state. Requiring persistent support before switching reduces flicker. It also delays detection, so record both the estimated event boundary and the time at which persistence allowed commitment. Do not rewrite that commitment time as if it were known earlier.

An HMM introduces a latent state for each time position, transition scores between states, and observation scores. Filtering estimates the current state using the prefix. Forward-backward smoothing uses the whole sequence and is offline. Viterbi finds a highest-scoring complete path, which can also revise earlier states when later evidence arrives.

```python
# Pseudocode: log-space filtering, scores[t, state].
alpha = log_initial + observation_scores[0]
for t in range(1, T):
    for state in states:
        next_alpha[state] = observation_scores[t, state] + logsumexp(
            alpha[previous] + log_transition[previous, state]
            for previous in states
        )
    alpha = next_alpha - logsumexp(next_alpha)
    emit_current_distribution(exp(alpha))
```

The teaching lab accepts log observation potentials. If you pass neural class posteriors directly, call the result a scored hybrid unless you explicitly account for the distinction between posterior probabilities and generative emissions. This matters when interpreting a path score as a probability.

### 7.2 Causal temporal convolutional networks

A TCN applies learned convolutions along time. A dilated convolution reads inputs separated by a fixed spacing; stacking increasing dilations reaches farther into the past without a very large kernel. A causal implementation pads only on the left and uses no future values.

For one kernel-size-three convolution at dilations 1, 2, and 4, the receptive field spans `1 + 2*(1+2+4) = 15` feature positions. At a 0.5-second stride, the oldest and newest anchors are seven seconds apart. The encoder clip width extends the full raw-video support further. A refinement stage can expand support again.

```python
# Pseudocode using the extracted teaching module's real shapes.
# features starts as [batch, time, dimension].
x = features.transpose(1, 2)        # [B, D, T]
valid = valid_positions             # Boolean [B, T]
outputs = model(x, valid)            # [stages, B, classes, T]
loss = segmentation_loss(outputs, targets, valid)
loss.backward()
optimizer.step()
```

Cross-entropy trains the label at each valid position. A temporal smoothing term penalizes rapid changes in adjacent predicted distributions. Excessive smoothing can erase brief actions, so compare short-action recall alongside segmental F1. Padding masks exclude padded positions from loss; they do not define a complete policy for a camera outage inside a sequence.

Test causality in evaluation mode by changing future inputs and checking that earlier outputs remain unchanged. Also compare a standalone prefix with the same prefix from a full sequence. Then test the encoder: a causal TCN cannot remove future information already present in centered features or whole-sequence normalization.

### 7.3 Explicit duration with an HSMM

An HSMM assigns a score to a whole state segment and its duration. A bounded dynamic program considers possible segment lengths and predecessor states. Duration can distinguish a quick reach from a long inspection when their observations are otherwise similar.

```text
best[end, state] = maximum over duration and previous state of:

  best[start, previous]
  + transition_score(previous, state)
  + duration_score(state, duration)
  + observation_sum(start, end, state)

where start = end - duration
```

The extracted `hsmm_viterbi` assumes the final segment has completed. A live prefix often ends inside an ongoing action. Repeatedly running this offline decoder on a prefix does not turn it into a correctly censored online duration model. Keep the first HSMM comparison offline; use filtering or a causal TCN for initial live output.

Most importantly, preserve the observed action path independently of a normal-procedure graph. If the true sequence is align then tighten, a normal-only graph may label tightening as insertion to make the path legal. The error engine needs the unexpected action, not a repaired narrative.

## 8. Durable facts and temporal memory

A classifier emits a proposal about one observation. The temporal store reconciles proposals into a history that can answer “what was established about this entity at that time?” It must also answer “what did we know at the time we made the decision?” Those questions differ when a later investigation revises an earlier estimate.

Store immutable evidence and append-only fact revisions. A current projection can accelerate queries, but retain the revision history that explains prior incidents. Each fact should identify its episode, entity, property, value, validity interval, source evidence, revision, and availability time. Use a separate uncertainty or coverage record instead of overloading the physical value with transport errors.

### 8.1 Minimal persistence schema

The following SQL is a proposed starting migration. It is intentionally small enough to understand. The full implementation must add action-event, coverage, rule-version, and incident tables with the same identity and provenance conventions.

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE episodes (
  episode_id TEXT PRIMARY KEY,
  video_sha256 TEXT NOT NULL,
  procedure_version TEXT NOT NULL,
  split_group TEXT NOT NULL
);

CREATE TABLE evidence (
  evidence_id TEXT PRIMARY KEY,
  episode_id TEXT NOT NULL REFERENCES episodes,
  start_us INTEGER NOT NULL,
  end_us INTEGER NOT NULL,
  available_at_us INTEGER NOT NULL,
  artifact_path TEXT NOT NULL,
  producer_spec_hash TEXT NOT NULL,
  CHECK (start_us >= 0 AND end_us > start_us)
);

CREATE TABLE fact_revisions (
  fact_id TEXT NOT NULL,
  revision INTEGER NOT NULL CHECK (revision >= 1),
  episode_id TEXT NOT NULL REFERENCES episodes,
  entity_id TEXT NOT NULL,
  property TEXT NOT NULL,
  value TEXT NOT NULL,
  start_us INTEGER NOT NULL,
  end_us INTEGER NOT NULL,
  available_at_us INTEGER NOT NULL,
  evidence_id TEXT NOT NULL REFERENCES evidence,
  PRIMARY KEY (fact_id, revision),
  CHECK (start_us >= 0 AND end_us > start_us)
);

CREATE INDEX facts_lookup ON fact_revisions
  (episode_id, entity_id, property, start_us, end_us);
```

This schema uses one primary evidence reference per fact revision. Add a join table when a fact depends on multiple clips, and a supersession/retraction record when proposals are withdrawn. Database constraints validate shapes and referential integrity; they do not prove that overlapping facts are semantically consistent.

Python's `sqlite3.connect`, parameterized `execute`, and explicit transaction control provide the basic persistence API. Set transaction policy deliberately rather than depending on version-sensitive defaults; use bound parameters for values. [Python SQLite API](https://docs.python.org/3/library/sqlite3.html)

### 8.2 As-of queries and conflicting evidence

For an as-of query, first filter revisions to those available by the requested knowledge time. Then select the highest revision for each logical fact. Only after that should you test whether the selected revision covers the queried event time. Reversing this order can accidentally resurrect an older revision whose interval was later corrected.

```python
# Pseudocode: input includes event time and knowledge time.
def state_at(episode, entity, prop, event_us, as_of_us):
    rows = load_revisions(episode, entity, prop)
    visible = [r for r in rows if r.available_at_us <= as_of_us]
    latest = highest_revision_per_fact(visible)
    covering = [r for r in latest
                if r.start_us <= event_us < r.end_us]
    if coverage_missing(episode, entity, prop, event_us, as_of_us):
        return Unknown("observation gap")
    return reconcile(covering)  # conflicts can return UNKNOWN
```

Do not hold RUNNING or STOPPED forever after the last frame. Define a property-specific maximum evidence age and continuity rule, fitted or justified for the experiment. Losing visibility should expire or suspend the inference; it must not imply that the machine became safe or that an incident resolved.

Entity identity belongs in this contract. Initially, use one known machine region and one worker per episode if automatic tracking is not implemented. Later, a tracker must expose identity uncertainty and reset rules. A worker label changing after occlusion must not silently combine two people's histories.

## 9. The rule language and deterministic evaluator

A rule is a versioned specification over typed events, states, entities, and intervals. Begin with a validated JSON abstract syntax tree, or AST. Natural-language compilation can later produce that AST, but it must pass the same validation as a hand-written rule. Do not execute model-generated Python.

The first rule vocabulary should be deliberately small: event triggers, entity bindings, conjunction, a state that holds immediately before a trigger, and bounded absence with explicit coverage requirements. Reject unknown operators, undeclared entities, negative durations, and unsupported nesting rather than approximating their meaning.

```json
{
  "rule_id": "guard_requires_stop",
  "version": 1,
  "trigger": {
    "event_type": "guard_open",
    "bind": {"machine": "target_entity_id"}
  },
  "require": {
    "op": "state_for_immediately_before",
    "entity": "$machine",
    "property": "operating_state",
    "value": "STOPPED",
    "duration_us": 2000000
  },
  "lookback_us": 30000000,
  "unknown_policy": "investigate"
}
```

The trigger binds the target machine, not necessarily the worker. A rule about “the same worker who stopped the machine” would need an additional actor binding and a different predicate. Keep this distinction explicit instead of letting language ambiguity change implementation behavior.

### 9.1 Three-valued logic

A proposition can be true, false, or unknown. In a conjunction, any known false term makes the conjunction false; all true terms make it true; otherwise it is unknown. Negating unknown remains unknown. Rule output also distinguishes NOT_APPLICABLE when no trigger exists from UNKNOWN when a trigger exists but its requirement cannot be resolved.

Map a triggered requirement's true value to PASS, false to VIOLATION, and unknown to UNKNOWN. Do not collapse UNKNOWN into false when persisting a Boolean or serializing to JSON.

```text
Requirement A   Requirement B   A AND B
TRUE            TRUE            TRUE
TRUE            UNKNOWN         UNKNOWN
FALSE           UNKNOWN         FALSE
UNKNOWN         UNKNOWN         UNKNOWN
```

For absence, “no detected insertion” is insufficient. A bounded omission test needs a known opportunity or deadline, adequate coverage of the relevant interval, and a defined sensitivity assumption for the detector. If a camera gap could hide the action, the result is unknown. Absence from a short retrieved clip is especially weak evidence because retrieval is not exhaustive coverage.

### 9.2 Duration with uncertain boundaries

The interval arithmetic in section 1 assumes a single stopped interval continues until the guard opens. If the machine can restart in between, inspect the whole required interval; subtracting two boundary estimates alone is not enough.

```python
# Pseudocode for a continuous stopped interval ending at trigger.
def minimum_stop_rule(stop_bounds, open_bounds, required, evidence):
    if not evidence.adequate_for_relevant_interval:
        return Unknown("incomplete coverage")
    if evidence.has_conflicting_state_or_possible_restart:
        return Unknown("state continuity not established")
    stop_lo, stop_hi = stop_bounds
    open_lo, open_hi = open_bounds
    shortest = open_lo - stop_hi
    longest = open_hi - stop_lo
    if shortest >= required:
        return Pass(shortest, longest)
    if longest < required:
        return Violation(shortest, longest)
    return Unknown("boundary uncertainty spans threshold")
```

If a known running interval overlaps the required stopped interval, that can establish false directly. The conservative pseudocode above defers more complex continuity cases to the general interval evaluator. Record the exact semantics of equality: “at least two seconds” passes at exactly two seconds.

### 9.3 Test logic with gold facts first

Write deterministic examples for pass, violation, unknown, a restart, the wrong target entity, a missing trigger, duplicate delivery, and a revised boundary. Gold facts isolate the rule implementation from visual recognition. Only when those cases behave correctly should predicted facts feed the evaluator.

A normal-procedure graph expresses expectations and permitted rework. A fact store expresses observed or established state. Rework can invalidate an earlier postcondition: removing a fastener makes “fastener inserted” false again. The teaching prerequisite monitor is monotone, so production rework requires an explicit invalidation transition.

## 10. Bounded investigation and Cosmos verification

The investigator is a controller that spends extra computation on an unresolved predicate. It can retrieve a bounded time range, resample video, or ask a focused question. Its output is additional evidence or a structured proposal, followed by deterministic reevaluation.

```text
rule evaluator     investigator      video store        VLM
      |                  |                |               |
      |-- UNKNOWN ------>|                |               |
      |                  |-- interval --->|               |
      |                  |<-- frames -----|               |
      |                  |-- question + timestamps ------>|
      |                  |<-- structured proposal --------|
      |                  |-- validate + reconcile         |
      |<-- reevaluate ---|                |               |
      |-- result revision                 |               |
```

Define budgets in the run configuration: maximum calls per candidate, maximum frames, maximum evidence span, maximum generated tokens, and wall-time deadline. Three calls is a reasonable initial engineering setting to measure, not a scientific optimum. Stop when the result resolves, the budget expires, or no new admissible evidence remains.

### 10.1 Verifier request and response

A verifier request includes the question, entity crop or identity description, sampled frame IDs and timestamps, observation quality, and allowed response schema. Avoid telling the model the desired verdict. Ask when visible motion stopped, or whether a specified object is visible, rather than asking it to justify a suspected violation.

```python
# Proposed application interface.
class VideoVerifier:
    def verify(self, request: VerificationRequest) -> VerificationResult:
        ...

# Example result payload, values illustrative.
result = {
    "status": "supported",   # or uncertain / unavailable / invalid
    "predicate": "operating_state",
    "entity_id": "M1",
    "value": "STOPPED",
    "boundary_us": [10900000, 10950000],
    "evidence_frame_ids": ["E17-f327", "E17-f329"],
    "observation": "Visible shaft motion ceases between samples."
}
```

Validate the schema, referenced frame IDs, entity bindings, and timestamp bounds. A response citing a frame not supplied to the model is invalid. A response assigning precision finer than the evidence supports needs conservative widening or rejection. A timeout is a service outcome; it is not evidence that the predicate is false.

### 10.2 Where Cosmos fits

Cosmos Reason is a vision-language reasoning model candidate for this verifier interface. It is different from Cosmos-Embed1, which produces retrieval vectors, and from video-generation components that synthesize footage. Evaluate each role separately.

A community MLX conversion of Cosmos Reason2-2B is available, while NVIDIA's own model card describes the model's physical-reasoning purpose. This establishes a candidate to test, not validated Mac performance. [NVIDIA model card](https://huggingface.co/nvidia/Cosmos-Reason2-2B), [conversion author's model card](https://huggingface.co/hzang/Cosmos-Reason2-2B-8bit)

Compare no verifier, a small Qwen VLM, and the Cosmos candidate on identical evidence packets. Record changed decisions, introduced errors, unknown rate, added latency, and calls per episode. Repeated calls on the same frames are correlated; do not multiply their stated confidence values as if they were independent measurements.

A future remote Cosmos-Embed1 adapter can use NIM's `POST /v1/embeddings` endpoint. The documented text-query body specifies `model`, `input`, and `request_type: query`. Video request formats and bulk behavior differ from a generic text-only embedding API; translate them in the adapter rather than leaking vendor payloads into the rule engine. [Cosmos NIM API](https://docs.nvidia.com/nim/cosmos-embed1/latest/api-reference.html)

## 11. Incident lifecycle, replay, and recovery

An incident is a stable record with revisions, not one row for every frame that supports an error. Choose an identity based on episode, rule version, bound entities, and a stable trigger ID. Avoid using the estimated trigger timestamp as the identity because investigation may change that timestamp.

```text
candidate ---- evidence supports error ----> confirmed
    |                                          |
    | insufficient evidence                    | new evidence
    v                                          v
 unresolved <------------------------------ revised
    |
    +---- evidence establishes compliance ----> dismissed
```

Keep decision state separate from service health. A camera outage can make an active incident unobservable without proving that the underlying condition ended. Store resolution evidence explicitly and preserve the historical confirmed revision if later evidence changes the current judgment.

### 11.1 Availability-faithful replay

Offline footage gives access to the future, so replay needs a clock that restricts what every component may read. Advance a simulated availability clock and release frames/results only when admissible. A verifier may look forward only within declared lookahead and only once those frames have become available.

```python
# Pseudocode: stable ordering for replay events.
queue = sort_by_available_time_then_stable_id(input_events)
for event in queue:
    replay_clock.advance_to(event.available_at_us)
    with database.transaction():
        if already_processed(event.id):
            continue
        append_evidence(event)
        update_current_projection(event)
        append_incident_revisions(evaluate_affected_rules(event))
        mark_processed(event.id)
        save_replay_cursor(event.cursor)
```

This transaction describes the durable step after expensive model work completes. Do not hold a database transaction open while awaiting a VLM. Persist a pending job, execute outside the transaction, and commit its validated result idempotently. After restart, retry pending jobs with the same request identity.

### 11.2 Capacity and backpressure

If one sampled clip arrives every half second and takes 0.8 seconds to encode serially, the encoder accumulates work. A bounded queue makes that visible; an unbounded queue merely postpones failure. Measure service time on the Mac, reduce sample load or model cost, and reserve expensive verification for selected candidates.

Record queue depth, processing delay, dropped work, and memory. If dropping a clip creates a coverage gap, persist the gap so a later rule does not treat unprocessed time as observed. Report latency from the real trigger to the committed incident, including clip assembly, persistence, queueing, and verification delays.

## 12. Local application API and viewer

The viewer needs a small API over persisted results. The following endpoints are **proposed application endpoints**, not endpoints supplied by Qwen, Cosmos, or the teaching labs. Implement the CLI first, then expose the same domain functions through HTTP.

| Endpoint | Purpose |
|---|---|
| `POST /api/episodes` | Register a local video asset and manifest. |
| `POST /api/search` | Rank clips within a specified encoder space. |
| `GET /api/episodes/{id}/timeline` | Fetch actions, states, gaps, and incidents. |
| `GET /api/evidence/{id}` | Return evidence metadata and media reference. |
| `GET /api/state` | Query a property at event time and knowledge time. |
| `POST /api/rules/validate` | Validate an AST without executing model code. |
| `POST /api/replays` | Start a replay job with a frozen configuration. |
| `GET /api/jobs/{id}` | Inspect progress, failure, or completion. |
| `GET /api/incidents/{id}` | Fetch incident history and supporting evidence. |

Use stable IDs rather than accepting arbitrary filesystem paths in browser media requests. The media handler resolves an ID to a registered asset. Start with a local-only server; exposing it to other machines is a separate deployment decision.

```json
{
  "query": "person opens the guard",
  "encoder_spec_hash": "SPEC_HASH",
  "episode_ids": ["E17"],
  "k": 5,
  "available_by_us": 15000000
}
```

The search response should include `clip_id`, `episode_id`, `start_us`, `end_us`, `score`, and `encoder_spec_hash`. A missing encoder index is an explicit error, not a fallback to a different embedding space. Use validation errors for invalid timestamps or unsupported AST operators; use job status for expensive processing. Duplicate requests with an idempotency key should return the existing job.

### 12.1 The viewer's teaching purpose

Display synchronized tracks for video, actions, object state, observation gaps, rule triggers, and incident revisions. Clicking a segment should reveal its evidence support and producer specification. Show similarity as a score and calibrated probability only when calibration exists.

A useful inspection panel answers:

- Which frames supported this estimate, and when were they available?
- Which rule version and entity bindings produced the judgment?
- Which facts were unknown, conflicting, or revised?
- Did verification change the decision, and at what additional delay?
- Is the timeline showing current knowledge or knowledge as of replay time?

The interface is an instrument for debugging the system. It should make an incorrect claim easy to challenge rather than presenting every output as a polished certainty.

## 13. Evaluation that identifies the first failing component

Evaluate each stage with its own denominator. Retrieval Recall@K asks whether relevant evidence was among the first K hits. Predicate precision and recall measure state labels. Segmental F1 measures localized action intervals. Rule precision and recall measure procedural judgments. False alerts per hour and latency measure the integrated system's behavior over time.

For segments, compute temporal intersection over union: overlap length divided by union length. Match predictions and ground truth one-to-one under a stated IoU threshold and label requirement. A long prediction should not count as several correct actions merely because it overlaps them all. Edit score compares collapsed label order and complements boundary-sensitive metrics.

Use oracle substitutions to locate errors. Give gold actions to the rule engine, gold entity identities to state reconciliation, or gold boundaries to duration evaluation. An oracle score is diagnostic and must never be reported as end-to-end deployable performance.

### 13.1 Required experiment table

For every run, record its source commit, data split, model and runtime revisions, preprocessing, feature stride, allowed lookahead, and thresholds. Then report at least the following, with sample counts and exposure duration.

| Layer | Measure | Failure it exposes |
|---|---|---|
| Retrieval | Recall@5 and query latency | Missing relevant evidence. |
| State | Macro-F1 and abstention coverage | Wrong state or excessive refusal. |
| Segments | F1, edit score, short-action recall | Fragmentation or erased steps. |
| Timing | Boundary error and uncertainty coverage | False timestamp precision. |
| Rules | Precision/recall by error type | Logic or evidence failures. |
| System | False alerts/hour, p95 delay | Unusable alert behavior. |
| Compute | Peak memory, queue growth, calls | Unsustainable local execution. |

Confidence intervals and per-episode results become important as the corpus grows. For the initial ten-query smoke benchmark, report the raw count as well as a percentage. Never imply that eight successful queries establish general recognition quality.

### 13.2 Regression cases worth keeping

Tests should protect semantic behavior, not simply mirror implementation lines. A useful core suite includes:

- Changing future frames does not change committed past output.
- A fact revision correcting its interval does not resurrect the old interval in an as-of query.
- A coverage gap changes an omission judgment to unknown.
- A state restart breaks the continuous stopped interval.
- The wrong machine's state cannot satisfy the bound machine's requirement.
- Retrying the same event or verifier job creates no duplicate incident.
- A model/configuration change cannot reuse an incompatible feature cache.
- A missing or out-of-range cited frame invalidates a verifier response.

## 14. Implementation milestones for the intern

Each milestone ends in a small runnable artifact and a written finding. The findings may be negative: learning that context hurts classification or that a local model cannot sustain the desired rate is useful progress. Do not compensate for an inconvenient result by changing the test set.

### Milestone 0: Environment and numerical exercises

Read sections 1–4, then run the extracted teaching labs. Create an isolated Python environment for application work and record the interpreter version. Confirm the intended MLX model/runtime combination on one text, image, and video input before downloading a large corpus.

PyTorch's MPS backend exposes `torch.backends.mps.is_available()` and device `mps`. Select it only when available, and retain a CPU baseline for the small temporal model. MPS availability is not proof that every operation or precision choice used by a pretrained model works. [PyTorch MPS API](https://docs.pytorch.org/docs/main/notes/mps.html)

Done means: the numerical exercises pass; a runtime report records supported inputs, observed shapes, memory, and timings; no application performance claim is based solely on model loading.

### Milestone 1: Searchable video notebook

Implement `contracts.py`, ingestion, timestamped sampling, the encoder adapter, cache, retrieval, and a CLI. Register the small corpus, extract a fixed configuration, and run fixed search queries. Add the simplest possible clip viewer after the CLI results are correct.

Done means: every hit opens the correct source interval; incompatible caches are rejected; the retrieval report includes raw query outcomes and encoding cost. A proposed CLI shape is `video-workbench search --query TEXT --run RUN_ID`; implement and document it before presenting it as an executable command.

### Milestone 2: State-recognition experiment

Implement frozen-feature linear classification, visibility-aware abstention, context ablations, and state proposals. Keep the initial entity association explicit and simple. Inspect mistakes visually before tuning a more complex model.

Done means: generic and context-conditioned conditions are compared on identical splits; thresholds are chosen without the final holdout; unknown rate is reported; evidence is available for each state transition.

### Milestone 3: Temporal learning and durable memory

Integrate the TCN and sequence baselines, add action segments, implement fact revisions and as-of queries, and define coverage expiration. Review the lab limitations before reusing its code. Keep an unconstrained observation path when adding procedural expectations.

Done means: the causality tests and revision tests pass; a skipped-step example remains observable; segment metrics and short-action recall are reported against the independent baseline.

### Milestone 4: Rules and a bounded verifier comparison

Implement the AST validator and deterministic gold-fact tests before adding a VLM. Then implement typed verifier requests, evidence validation, budgets, and fact reconciliation. Compare the selected Qwen model and Cosmos candidate with the same admissible evidence.

Done means: pass, violation, unknown, and non-applicable cases are explicit; timeout and invalid response handling work; the comparison reports system recall and added delay, including upstream candidate misses.

### Milestone 5: Replay, incidents, and transfer

Implement durable jobs, replay cursor recovery, incident revisions, and the complete timeline viewer. Exercise interruptions and duplicate delivery. Hold out staged real footage from tuning to test transfer from the development domain.

Done means: sustained replay has measured queue and memory behavior; incident identities survive revisions; restart reproduces the same committed outputs under the declared policy; the report includes false alerts per hour and latency.

### Optional corpus milestone: Habitat first, with a timebox

After the first real-video baseline works, attempt one actor/object interaction with synchronized video and state export. Habitat's HITL documentation names macOS and M1 Pro/Max, while Habitat-Sim documents that its EGL headless option does not work on macOS. Use an attached-display path and validate the specific assets and actions you need. [Habitat HITL](https://github.com/facebookresearch/habitat-lab/blob/main/habitat-hitl/README.md), [Habitat-Sim](https://github.com/facebookresearch/habitat-sim)

Limit the first spike to half a day. Success is one controlled episode and one timing counterfactual with evaluator-only truth. If setup dominates, return to staged footage; the main milestones should remain runnable without a simulator.

## 15. Existing file map and exact teaching APIs

All paths in this section refer to real ticket files. Paths in section 2 are proposed implementation targets. Read the roadmap for project priorities, the imported textbook for derivations, and the extracted code for executable numerical examples.

- [Project roadmap](01-source-analysis-and-mac-project-roadmap.md) explains the five-project sequence and Mac-specific decisions.
- [Imported textbook](../sources/video_understanding_for_procedural_work.md) supplies the broader theoretical development. Read chapters 5–6 for embeddings and clocks, 7–13 for sequence models, 14–16 for errors and streaming, and 18–21 for evaluation and labs.
- [Original notes](../sources/cosmos-random-notes.txt) contain the search/state/DSL curriculum and simulator alternatives. They are brainstorming material, including claims qualified by the roadmap.
- [Import manifest](../sources/import-manifest.json) records provenance for the two originally requested source files.
- [Lab README](../sources/procedural_video_labs/README.md) states dependencies and deliberate limitations.
- [Sequence lab](../sources/procedural_video_labs/sequence_lab.py) contains `forward`, `smooth`, `viterbi`, `hsmm_viterbi`, `collapse`, `temporal_iou`, `edit_score`, `PrerequisiteMonitor`, and `PersistenceGate`.
- [Neural lab](../sources/procedural_video_labs/neural_lab.py) contains `CausalBlock`, `Stage`, `CausalMultiStageTCN`, and `segmentation_loss`.
- [Regression tests](../sources/procedural_video_labs/test_labs.py) independently enumerate tiny sequence cases and test missing evidence, timestamps, and metrics.
- [Investigation diary](../reference/01-investigation-diary.md) records current work, failures, and validation; [tasks](../tasks.md) track implementation follow-ups.

### 15.1 Sequence-lab contracts

`forward(log_e, log_a, log_pi)` returns log forward messages and a total log score. `smooth` returns offline state marginals and the total score. `viterbi` returns a dense best path and its score. Inputs are observation scores `[T, K]`, transitions `[K, K]`, and initial scores `[K]`.

`hsmm_viterbi(log_e, log_a, log_pi, log_duration)` adds duration scores `[K, max_duration]`, where column `d-1` represents duration `d`. It returns half-open segments in feature-index coordinates and a score. Map indices through the feature timestamp grid before presenting seconds. It rejects non-finite emissions because its segment sums use prefix sums.

`PrerequisiteMonitor.observe(step, postcondition)` models a simplified monotone procedure. `gap()` makes coverage incomplete. `PersistenceGate.update(time_s, score)` enforces increasing timestamps and returns lifecycle hints such as possible, incident, active, normal, or observation_gap. Neither class is a replacement for the durable incident and interval reconciliation design above.

### 15.2 Neural-lab contracts

`CausalMultiStageTCN(input_dim, classes, channels=16, layers=3, stages=2)` consumes `[B, D, T]` features and Boolean `[B, T]` validity. It returns `[S, B, C, T]`. `segmentation_loss(outputs, target, valid, smooth_weight=0.05, clip=4.0)` consumes integer `[B, T]` targets. Review the actual implementation when changing masking, smoothing, or stage count.

### 15.3 Commands that work on the extracted teaching files

From this ticket's `sources/procedural_video_labs/` directory, with NumPy and PyTorch installed:

```sh
python3 sequence_lab.py
python3 -m unittest -v test_labs.py
python3 neural_lab.py
```

These existing exercises were run during guide preparation on this Mac. The 20 sequence tests passed. The neural demo reported a zero future-perturbation prefix error, output shape `[2, 2, 3, 24]`, and decreasing synthetic loss over 40 optimizer steps with PyTorch 2.5.1. The features in that optimization exercise encode the target classes, so its success is deliberately limited to numerical behavior.

## 16. Reading and review checklist

On your first day, explain the example in section 1 without referring to model brand names. Then identify where the same evidence enters retrieval, state estimation, and procedural judgment. If those responsibilities are clear, the model adapters become replaceable implementation choices rather than the definition of the system.

Before submitting each milestone, include a concise report of the question tested, the exact data split, the changed component, the results, and one representative failure. Link to the supporting clip and run manifest. A reviewer should be able to reproduce the result and see why the next implementation step follows from it.

- Verify that every displayed timestamp has a documented origin and unit.
- Verify that every probability label refers to a calibrated quantity, or relabel it as a score.
- Verify that source files, proposed modules, and vendor APIs remain distinguishable in documentation.
- Verify that unknown evidence remains unknown through persistence, rules, and UI rendering.
- Verify that an unexpected procedure does not get silently rewritten into a valid one.
- Verify that the next component solves an observed failure rather than simply adding complexity.

The first useful result is a small, reproducible system whose mistakes can be explained from its evidence. Each later milestone should preserve that property while extending what the system can recognize and reason about.
