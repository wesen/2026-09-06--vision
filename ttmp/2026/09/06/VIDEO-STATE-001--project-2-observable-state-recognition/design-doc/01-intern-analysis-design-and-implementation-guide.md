---
Title: Intern analysis design and implementation guide
Ticket: VIDEO-STATE-001
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
Summary: Measure visual state discrimination, context effects, calibration, and abstention.
LastUpdated: 2026-09-06T13:13:51.277202-04:00
WhatFor: ""
WhenToUse: ""
---


# Project 2 - Observable state recognition

## The question and the deliverable

This project asks whether frozen visual features distinguish states that matter to a household procedure: a fridge door open versus closed, a microwave door open versus closed, or an object too occluded to judge. The deliverable is a state-recognition experiment and inspectable timeline, not a general-purpose visual truth engine. The system must be able to say UNKNOWN when the available pixels do not support a decision.

A state is a property over time, such as `door_open`, while an action is a change-producing event such as `OPEN`. Seeing an OPEN action does not prove the door remained open later. Conversely, a clearly open door can be recognized without observing who opened it. This distinction is the foundation for the temporal and rule projects.

Read the corpus report, then compare the raw final graph with the last RGB frame of the same episode. The graph is simulator world truth; the frame is visual evidence. Our current generator explicitly disables dense visual-state supervision because graph/image capture phase is unverified. You must not train a dense state model by simply copying the graph value onto every image.

## Current state, dependencies, and data gate

COSMOS-EMBED-001 provides the frozen encoder contract. VIDEO-SEARCH-001 provides source registration, decoding, and feature caching. VIDEO-CORPUS-001 supplies improved visual annotations and calibration, but this project can begin with a small manually reviewed subset from the existing videos. Temporal metrics remain blocked until a reviewed boundary dataset exists; that does not block static-frame classification experiments.

The v1 corpus contains two appliances, one apartment, one character, and repeated counterfactual routines. It is useful for plumbing and ablations but too narrow to establish robust generalization. Existing `runner.py:54` writes `world-frames.jsonl` and flags capture phase unverified. Existing `core.py:167` checks final world state and arrival in the living room, not visual observability. Those are separate labels with separate intended uses.

## Label vocabulary and annotation workflow

Define an entity instance within an episode, a property, a sample timestamp, and an annotation. For the first release, use property `door_open` with values `true`, `false`, or `unknown`. Keep observability separate from value: `visible`, `occluded`, `out_of_frame`, or `ambiguous`. Unknown is the inference result when evidence is insufficient; it is not a third physical door position. A missing annotation is not an unknown annotation.

```json
{
  "schema_version": 1,
  "episode_id": "ep-example",
  "entity_id": "microwave-1",
  "property": "door_open",
  "sample_us": 5200000,
  "value": true,
  "observability": "visible",
  "label_source": "reviewed_rgb",
  "review_revision": "review-001"
}
```

The example ID is illustrative. Real entities must be registered explicitly and bound consistently across crops, predictions, and rules. Start with manually reviewed fixed target regions or full-frame inputs with an explicit entity binding; automatic tracking is outside this first experiment. Do not infer the target from a filename containing the action variant.

Select a fixed sample grid and transition-focused examples from training and development groups, then reserve the test group before threshold selection. Aim initially for at least 20 reviewed examples per known class per appliance and a deliberate set of occluded/ambiguous frames; if the videos cannot provide enough distinct evidence, report the shortfall and request corpus expansion. Repeated near-identical frames are not independent examples. Have a second reviewer inspect disagreements when available; if only one review is available, record that limitation rather than inventing agreement statistics.

## Proposed recognition pipeline

```text
registered video + entity binding
              |
        timestamped RGB / crop
              |
         frozen encoder
              |
    +---------+----------+
    |                    |
text-hypothesis       linear head
similarities          logits
    |                    |
    +------ calibration--+
              |
  observability + abstention policy
              |
    true / false / unknown + evidence
```

Implement `predicates/labels.py`, `predicates/features.py`, `predicates/classify.py`, `predicates/calibration.py`, and `evaluation/state.py` under the proposed workbench package. The classification layer does not own long-term state persistence; Project 3 consumes these observations and decides what remains known across gaps.

```python
# Proposed application records and API.
@dataclass(frozen=True)
class StateObservation:
    episode_id: str
    entity_id: str
    property: str
    sample_us: int
    available_us: int
    value: bool | None  # None means unknown
    raw_score: float | None
    calibrated_probability: float | None
    reason: str
    evidence_ids: tuple[str, ...]
    model_spec_id: str

def classify(sample, entity, classifier, calibration):
    feature = frozen_encoder(sample.rgb)
    score = classifier.score(feature, entity.property)
    if sample.observability_is_unusable:
        return unknown("unobservable", sample)
    probability = calibration.apply(score)
    if probability >= calibration.positive_threshold:
        return observed(True, probability, sample)
    if probability <= calibration.negative_threshold:
        return observed(False, probability, sample)
    return unknown("ambiguous_score", sample)
```

The pseudocode assumes a separately supplied observability signal. An oracle visibility label may be used in a clearly labeled diagnostic, but an end-to-end test must use a deployable gate or report that visibility gating is manual. Keep those experiment modes separate. Raw cosine similarity is not a calibrated probability, and an uncalibrated model may legitimately return no probability.

## Three baselines and context controls

The first baseline compares a frame embedding with text hypotheses such as "the fridge door is open" and "the fridge door is closed". Use the margin between similarities as a score and record the exact templates. The second adds neutral context, such as the appliance location, through a verified model conditioning path. Changing only the text hypothesis is a text-template experiment, not evidence that visual embeddings were context-conditioned. The third fits a small logistic/linear classifier to frozen features using training examples only.

For the context study, hold images, sample times, split groups, and label review fixed. Compare generic text, correct neutral context, misleading context, and context-only input. A misleading prompt that states the answer can reveal susceptibility to textual shortcuts, but it must be labeled as an adversarial control, not a valid description. If context-only input performs well, investigate label or episode leakage before claiming improved perception.

Train normalization statistics and classifier weights on training data. Select thresholds and any probability calibration on development data, using grouped folds or a separate development subdivision when data permits. Do not fit and report calibration on the same tiny examples without labeling that optimism. Test data must not choose the template, crop, threshold, or stopping epoch.

### Decision: explicit abstention instead of forced classification

- **Context:** The corpus includes occlusion and unverified graph/pixel alignment.
- **Options considered:** Always choose open/closed, add a learned unknown class, or separate observability and threshold abstention.
- **Decision:** Start with separate observability and calibrated abstention.
- **Rationale:** It preserves the distinction between an unseen state and a confidently observed state.
- **Consequences:** Coverage becomes a first-class metric; a manual visibility gate is an oracle condition until replaced.
- **Status:** proposed.

## Evaluation and acceptance criteria

Report per-appliance precision/recall and macro-F1 on visible known labels, confusion matrices, abstention coverage, and error among answered examples. Coverage is answered eligible samples divided by eligible samples. Selective error is incorrect answers divided by answered samples; if there are no answers, report error undefined and coverage zero. Include failures on unobservable examples as false-certainty counts.

Compute uncertainty by episode/group where possible, not by treating thousands of neighboring frames as independent. With only four initialization groups, show raw counts and per-group results rather than precise-looking confidence intervals. A useful report can conclude that context does not help or that the linear head overfits.

Transition-time error requires reviewed onset/offset uncertainty intervals. Until VIDEO-CORPUS-001 supplies those labels, mark that metric unsupported. Do not substitute the simulator's guarded action interiors for exact state transitions. A coarse frame-state score and an action-boundary score answer different questions.

## Implementation phases

### P1 - Reviewable annotation subset

Create a versioned annotation manifest and entity registry, with source hashes and review provenance. Add a contact-sheet export that does not expose intended variants to the annotator where practical. Store missing, unknown, and visible labels distinctly. Exit with a split summary, class counts, review limitations, and a documented list of excluded samples.

### P2 - Frozen-feature baselines

Implement text margins and a linear head using the same features. Add tests with a hand-computed two-class score, a wrong entity binding, and an incompatible feature-space hash. Verify that label-bearing files are read only by training/evaluation. Exit with saved predictions including unknown reasons and source evidence links.

### P3 - Context and calibration experiment

Freeze templates and run the controlled context conditions. Fit calibration and thresholds without the test group. Produce risk/coverage tables and false-certainty examples. Exit when each reported score can be traced to a specific label revision, feature space, and threshold configuration.

### P4 - Timeline and handoff

Add a timeline with observed values, unknown spans, and source playback. Export `StateObservation` rows for Project 3; preserve sample time and result availability. Demonstrate that an occluded sample does not silently inherit the previous state in this layer. Publish the complete experiment table and identify which state distinctions are supported by the present representation.

## Worked review case

Suppose the microwave is visible and open at 5.2 seconds, the actor blocks it at 5.5 seconds, and it is visibly closed at 6.1 seconds. The correct observation stream can be true, unknown, false. It must not assert that closure occurred precisely at 5.5 seconds. A later temporal component can retain an uncertainty bracket or ask for more evidence. That bracket is useful information, not an implementation failure to hide with interpolation.

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

- [COSMOS-EMBED-001](../../COSMOS-EMBED-001--embedding-runtime-baseline-on-mlx/index.md)
- [VIDEO-SEARCH-001](../../VIDEO-SEARCH-001--project-1-timestamped-video-search/index.md)
