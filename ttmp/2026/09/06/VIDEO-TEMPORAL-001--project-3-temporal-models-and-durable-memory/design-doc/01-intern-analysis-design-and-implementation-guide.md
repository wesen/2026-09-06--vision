---
Title: Intern analysis design and implementation guide
Ticket: VIDEO-TEMPORAL-001
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
Summary: Compare temporal decoders and store availability-aware facts without inventing missing steps.
LastUpdated: 2026-09-06T13:13:51.46714-04:00
WhatFor: ""
WhenToUse: ""
---


# Project 3 - Temporal models and durable memory

## Purpose: use history without rewriting reality

Independent frame predictions are noisy. A door can be hidden for a moment, and short actions can be missed between samples. This project compares ways to use temporal context and then stores observations and inferred intervals so downstream rules can ask what was known at a particular time. The central constraint is that temporal smoothing must not invent a normal procedure when the actual recording omitted or repeated an action.

The deliverables are a frozen-feature sequence benchmark, linear/hysteresis/HMM/causal-TCN/duration-aware baselines, and a durable fact store with explicit availability semantics. Full encoder fine-tuning and a natural-language rule system are outside scope. The intern should understand both the sequence model and the database clock model; otherwise a numerically correct decoder can still leak future information into replay.

## Existing evidence and dependencies

Project 1 supplies registered videos, sampled feature sequences, and source identities. Project 2 supplies state observations and calibration. The existing teaching `sequence_lab.py` implements `forward` at line 52, `smooth` at 62, `viterbi` at 74, and `hsmm_viterbi` at 95. `neural_lab.py` contains causal blocks, a multistage TCN, and masked segmentation loss. These are small executable numerical examples, not a deployed video pipeline.

The VirtualHome corpus currently has weak action interiors, not a calibrated dense segmentation ground truth. Begin with numerical oracle sequences and explicitly weak action training. Report exact-boundary metrics only on reviewed labels from VIDEO-CORPUS-001. This dependency is a data-quality gate, not a reason to block implementation of the model interfaces and store.

## The different models and what they assume

An independent linear classifier maps each feature vector to class scores. It is the baseline against which temporal complexity must earn its cost. Hysteresis requires sustained evidence to enter or leave a state; it reduces flicker but adds delay and can miss brief actions. An HMM combines observation likelihoods with probabilities of changing hidden state. A causal TCN learns patterns across a fixed history using convolutions. An HSMM adds explicit duration scores and is initially an offline decoding baseline.

Filtering conditions on observations available up to now. Smoothing uses future observations as well. Viterbi finds a high-scoring joint path over the supplied sequence; running it on a whole episode is not an online causal result. Do not compare these methods under one "real-time" label merely because all execute quickly.

```text
frozen features [T,D] + validity + timestamps
                       |
       +---------------+----------------+
       |               |                |
   linear head    HMM / hysteresis    causal TCN
       |               |                |
       +---------- observation scores --+
                       |
          optional offline HSMM baseline
                       |
         segments + uncertainty + provenance
                       |
             append-only temporal store
```

## Input and model contracts

A sequence record contains episode ID, feature-space ID, features `[T,D]`, per-feature end/availability times, source evidence IDs, validity mask, and label mask. Missing evidence is not background. Keep labels such as OPEN, CLOSE, WALK, and OTHER separate from the validity mask; masked samples do not contribute supervised loss.

The existing neural lab consumes features `[B,D,T]` and Boolean validity `[B,T]`, returning logits `[stages,B,classes,T]`. Its `segmentation_loss` takes integer targets `[B,T]` plus validity. Inspect its implementation before adapting masking to weak interiors. In the workbench, a label mask should exclude unreviewed boundaries even when the video frame itself is valid.

```python
# Proposed application protocol.
class TemporalModel(Protocol):
    def predict_offline(self, sequence) -> SegmentBatch: ...
    def step(self, feature, event_us, available_us) -> Updates: ...
    def checkpoint(self) -> bytes: ...

# Explicit weak-label loss mask.
loss_mask = frame_valid & label_reviewed_or_weak_interior
loss = cross_entropy(logits[loss_mask], target[loss_mask])
```

If a model does not implement streaming, its `step` method should be unavailable and its capability report should say offline-only. Do not emulate causal operation by repeatedly decoding the full known future clip.

## HMM and duration details

For K states, log emissions have shape `[T,K]`, transition scores `[K,K]`, and initial scores `[K]`. A forward filter combines the previous state distribution with transitions and the current emission. Use log-space operations to avoid underflow. Distinguish normalized likelihoods from arbitrary discriminative logits; if logits are used as scores, describe the result as a scored decoder unless the probabilistic assumptions have been justified.

The teaching `hsmm_viterbi` expects duration scores `[K,max_duration]`, with column `d-1` representing duration d. It returns half-open segments in feature-index coordinates. Map them through the actual feature grid before reporting seconds. A five-sample segment does not always mean five seconds if sampling gaps exist.

Allow repetitions, skips, and unexpected transitions in at least one unconstrained observation path. A normal-only transition graph can assign zero probability to a missing step and force a false normal sequence. Keep a constrained procedure decoder as an explicit ablation, alongside the unconstrained result. Measure whether known errors survive decoding.

## Causal TCN and future-leakage tests

A one-dimensional convolution with kernel size k and dilation d needs `(k-1)*d` past samples. The causal implementation must left-pad and avoid right-context access. For a stack with one convolution per layer, receptive field is `1 + sum((k-1)*d)`; if blocks contain multiple convolutions, count each one. Inspect the actual teaching block rather than copying a formula for a different architecture. The [PyTorch Conv1d reference](https://docs.pytorch.org/docs/2.14/generated/torch.nn.Conv1d.html) defines input layout, dilation, and padding; causal semantics remain the application's responsibility.

A causal head does not rescue noncausal features. A window centered at time t contains future frames even if the TCN only uses its current feature. Either use trailing windows whose end is the feature event time, or set availability after the latest source frame and evaluate with that delay.

```python
# Numerical causality test, with fixed weights/eval mode.
x2 = x.copy()
x2[:, :, cutoff+1:] = different_future()
y1 = model(x, valid)
y2 = model(x2, valid)
assert close(y1[..., :cutoff+1], y2[..., :cutoff+1])
# Also test chunked step output against prefix-only evaluation.
```

Train small heads on frozen features first. Pin seeds and record multiple training runs when feasible. Exclude padding from loss and metrics, avoid normalizing across future time, and measure the delay caused by any persistence threshold.

## Durable facts and the three clocks

A fact has an event interval describing when it concerns the video, an available time describing when the system could use its evidence/result, and a committed time describing when it was durably written. All are relative to a documented run clock, not a mixture of Unix time and video PTS. A prediction about second 5 that finishes at replay second 8 must not appear in an as-of-second-6 query.

Store immutable revisions with fact ID, episode/entity/property, value, event bounds, uncertainty bounds, available time, committed time, evidence IDs, producer version, and optional `supersedes_id`. A retraction should be explicit. The store owns reconciliation; the UI reads it without inventing a latest-state policy.

```python
# Proposed query semantics, not a nearest-row lookup.
def state_at(episode, entity, prop, event_us, as_of_us):
    rows = store.visible_revisions(as_of_us)
    rows = rows.for_entity_property(episode, entity, prop)
    rows = resolve_explicit_supersession(rows)
    candidates = rows.covering(event_us)
    if conflicting_values(candidates):
        return unknown("conflicting_evidence")
    if not adequate_coverage(candidates, event_us):
        return unknown("gap_or_stale")
    return reconciled(candidates)
```

A last-known state needs an expiry/coverage policy. Holding CLOSED forever across a camera gap would create false evidence for a continuous-closure rule. Project 2 observations remain immutable; inferred intervals cite them and can be superseded when new evidence arrives.

### Decision: keep offline and causal outputs distinct

- **Context:** Offline models can improve segmentation using future evidence.
- **Options considered:** One generic prediction stream or separate capability-tagged streams.
- **Decision:** Store model mode and availability with every output, and evaluate offline and causal results separately.
- **Rationale:** Replay must reproduce what was knowable at each moment.
- **Consequences:** More metadata and separate reports, but no hidden future access.
- **Status:** proposed.

## Implementation phases and review gates

### T1 - Sequence adapter and independent baseline

Create `temporal/data.py`, `temporal/base.py`, and `temporal/linear.py` under the proposed workbench package. Build a five-event oracle sequence with omission, repetition, and gap cases, then map current weak action interiors onto the feature grid without supervising uncertain boundaries. Exit with correct shapes, masks, timestamp mapping, and an independent baseline report.

### T2 - Classical temporal comparisons

Adapt reviewed teaching functions into `temporal/hmm.py` and `temporal/duration.py`, preserving input contracts and adding tiny exhaustive-path tests. Add timestamp-based hysteresis. Compare independent, filtered, smoothed, and offline-duration results with mode labels. Exit when the omitted-step fixture remains an omission in the unconstrained output and every method's future-access policy is explicit.

### T3 - Causal learned head

Implement `temporal/tcn.py`, a training command, seed/checkpoint metadata, and future-perturbation/chunk-equivalence tests. Choose hyperparameters on development groups only. Report performance versus the linear baseline, memory, wall time, and latency. Exit with causal behavior verified through both the model and feature availability path, regardless of whether the TCN improves accuracy.

### T4 - Store and replay-safe queries

Create `temporal/store.py`, SQLite migrations, append/retract APIs, and as-of queries. Test late contradictory evidence, supersession, duplicate ingestion, gaps, expiry, and restart. Use explicit transactions through the documented sqlite3 API. Exit with the same query answers before and after restart for every saved as-of point, and a clear handoff to VIDEO-RULES-001.

## Evaluation and worked failure case

Report frame accuracy only as one metric. Add segmental F1 at declared IoU thresholds, normalized edit score, short-action recall, and error-preservation rate on labeled omission/repetition fixtures. Declare matching rules and treatment of OTHER/UNKNOWN. Boundary error is meaningful only against reviewed uncertainty intervals. Show per-episode results and avoid treating overlapping windows as independent test units.

Consider OPEN, WALK, CLOSE, OPEN, WALK. A procedure-constrained decoder may compress this to one successful open-close cycle. That is precisely the error this project must expose: the final reopen matters. A useful model may smooth noisy WALK predictions while retaining both OPEN events, and the store should preserve their evidence and time uncertainty. If smoothing erases the reopen, a higher frame accuracy does not justify using it for procedural rules.

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
- [Sequence teaching lab](../../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/sources/procedural_video_labs/sequence_lab.py): forward, smooth, viterbi, hsmm_viterbi.
- [Neural teaching lab](../../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/sources/procedural_video_labs/neural_lab.py): CausalMultiStageTCN and segmentation_loss.

### Ticket dependencies

- [VIDEO-SEARCH-001](../../VIDEO-SEARCH-001--project-1-timestamped-video-search/index.md)
- [VIDEO-STATE-001](../../VIDEO-STATE-001--project-2-observable-state-recognition/index.md)
