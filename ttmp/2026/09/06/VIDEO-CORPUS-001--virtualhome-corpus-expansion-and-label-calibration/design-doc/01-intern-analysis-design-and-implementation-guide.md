---
Title: Intern analysis design and implementation guide
Ticket: VIDEO-CORPUS-001
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
Summary: Extend the working VirtualHome corpus with calibrated labels, controlled variations, and verified additional scenes.
LastUpdated: 2026-09-06T13:13:52.251711-04:00
WhatFor: ""
WhenToUse: ""
---


# VirtualHome corpus expansion and label calibration

## Purpose and explicit simulator choice

This ticket extends the working VirtualHome corpus. The user explicitly selected VirtualHome in place of Habitat, so there is no simulator migration or Habitat installation phase. The goal is to improve what the dataset can teach and evaluate: observable state labels, calibrated temporal uncertainty, controlled variations, and verified additional scenes when feasible.

The existing 24 videos are complete and useful. Preserve that v1 dataset and its provenance. The new work produces a separately versioned dataset and annotation release, with a documented quality gate before scale increases. More videos with the same ambiguous timing would increase storage without solving the key evaluation problem.

## Existing system, from program to video

The installed AIST checkout is recorded at revision `122d3b0aee04768d988e02929f6eeeb38f2f28a8`. The pinned simulator build is `Door_Modified_Build_2023_0404`; the local playbook records the app path and compatibility adjustments. The [VirtualHome-AIST repository](https://github.com/aistairc/virtualhome_aist) documents its additional actions, cameras, and per-frame JSON export. The local installed code and observed runs are the authoritative basis for this ticket's actual behavior.

`configs/virtualhome-household-v1.json` defines two appliance families, three variants, and four initialization/view groups. `core.py:55` plans 24 opaque episode IDs. `core.py:67` selects current graph objects; IDs are rebound after every reset. `core.py:87` builds programs that open a target, walk to a neighboring appliance, optionally close/reopen it, and leave for the living room. `runner.py:125` owns attempts, camera insertion, rendering, endpoint checks, and manifests.

```text
checked config -> episode plan -> owned Unity process
                                      |
                             current graph bindings
                                      |
                              action program + camera
                                      |
                          PNG / graph / action exports
                                      |
                          validation + MP4 + weak labels
                                      |
                         review + calibration release
```

The v1 run has 4,261 paired RGB/graph frames at 10 FPS, 426.1 seconds of video, 12/6/6 train/development/test episodes, and no failed attempts. All four group sheets were sampled visually. These facts establish pipeline integrity and limited sampled visibility, not exact action boundaries or generalization to other homes.

## The label problem to solve first

Unity's raw action file can insert WALK rows and repeat source-program indices. The current parser preserves those rows, accepts a terminal endpoint equal to frame count, and trims two frames from each interval edge. Its output is deliberately weak supervision. The two-frame guard is a heuristic; it does not establish the exporter uses inclusive endpoints or that graph updates align with RGB capture.

Pilot evidence showed graph state changes that did not reliably align with visible action intervals. Consequently `runner.py:54` sets `precise_boundary_supervision_allowed` and `dense_visual_state_supervision_allowed` to false. Do not flip those booleans globally after one successful example. Calibrate by build, action family, camera mode, and export path; preserve unsupported cases as weak or unknown.

Separate four concepts in the annotation release: intended program, executed world state, visible pixel state, and reviewed transition-time bounds. A simulator can know a door is open while the character blocks it. The label for a visual classifier should describe the evidence available in pixels, with observability and uncertainty recorded independently from world truth.

## Proposed calibration experiment

First run isolated OPEN and CLOSE programs with a visible dwell between them, using the existing stable camera and an owned simulator process. Retain the raw export and source hashes. Inspect frame-by-frame transition neighborhoods at native resolution, not only action midpoint contact sheets. Record the last definitely-old-state frame and first definitely-new-state frame; the interval between them is a reviewed boundary bracket.

Do this for both appliances, at least two views, and repeated executions. Compare raw action endpoints, graph state transitions, and reviewed visual brackets. Measure offsets and variability; do not choose a single global correction when errors vary by action or occlusion. A graph transition that never appears must be recorded as missing rather than forced into an offset estimate.

```python
# Pseudocode for a reviewed transition comparison.
for episode in calibration_release:
    raw = load_action_rows(episode)
    graphs = load_world_state_runs(episode)
    reviews = load_rgb_boundary_reviews(episode)
    for transition in reviews:
        assert transition.source_sha == episode.video_sha
        emit_comparison(
            action_export=match_raw_transition(raw, transition),
            world_export=match_world_transition(graphs, transition),
            visual_bounds=transition.bounds,
            visibility=transition.visibility,
        )
```

A missing or ambiguous visual transition should remain unscorable for exact timing. A calibration release may improve some subsets while leaving others weak. The acceptance artifact is an evidence table and explicit scope, not an assertion that all simulator labels are perfect.

## Annotation release schema and provenance

Store reviewed labels outside model inputs and independently of immutable generator manifests. A proposed review row includes episode ID, entity binding, property/action, source video hash, frame indices, time bounds, visibility, reviewer identity, review revision, and rationale. Keep manual review distinct from automated graph-derived inference.

```json
{
  "episode_id": "ep-example",
  "entity_id": "fridge-1",
  "transition": "closed_to_open",
  "earliest_us": 5100000,
  "latest_us": 5400000,
  "visibility": "partially_occluded",
  "source_kind": "reviewed_rgb",
  "review_revision": "rgb-review-v1"
}
```

The numeric bracket is illustrative. It is not a measurement of a current episode. A second reviewer can adjudicate uncertain cases; if unavailable, label the release single-reviewer and retain unresolved cases. Version the ontology and temporal convention. An annotation release should identify compatible corpus/model-input manifest hashes so a later re-encode cannot silently inherit old timing labels.

## Controlled variations without overstating counterfactuals

The current related variants reuse an initial actor position, but complete orientation and rendering determinism are not verified. Describe them as grouped variants, not perfectly matched counterfactual twins. For v2, log initial transforms, camera transforms, scene ID, actor resource, random seed, execution program, and actual object bindings. Compare repeated runs before promising determinism.

Add one factor at a time: camera shift, actor resource, dwell duration, extra irrelevant movement, omitted closure, repeated reopening, or another verified room layout. Duration-matched distractors help test whether a classifier merely distinguishes long reopening programs from short omission programs. If the simulator lacks a supported wait action, use a measured neutral motion or a verified API-supported alternative; do not invent a command or silently pad duplicate frames as if they were new animation.

Additional scene indices must pass capability probes. The current selector assumes a kitchen containing both a fridge and microwave and a destination living room. A new scene may lack those objects, use different relations, or have an obstructed camera. Produce a scene capability report before including it in the plan. Skip unsupported scenes with explicit reasons rather than relaxing bindings until a program runs on the wrong target.

## Split and leakage design

All variants from a common base initialization and their alternate camera views belong in the same split group. Derive grouping from scenario lineage, not from individual video filename. If v2 evaluates unseen scenes, assign complete scenes to partitions before generating views. If there are too few supported scenes, state that unseen-scene evaluation is unavailable; camera offsets within one room are not a substitute.

Preserve v1 splits for historical reproduction. Do not merge v1 test videos into v2 training and then compare the old test score as if the benchmark remained untouched. Track parent episode/group IDs, exact video hashes, and perceptual near-duplicate diagnostics. Exact-byte duplicate rejection in `runner.py:228` is useful but insufficient for visually identical re-encodes.

### Decision: versioned expansion after calibration

- **Context:** The pipeline works, but label timing and scene diversity remain limited.
- **Options considered:** Generate hundreds of v1-like episodes, switch simulators, or calibrate and expand VirtualHome incrementally.
- **Decision:** Keep VirtualHome and publish a new calibrated release in bounded stages.
- **Rationale:** It builds on verified local behavior and addresses the current evaluation gaps.
- **Consequences:** Some cases remain weakly labeled; larger scale waits for demonstrated label and scene quality.
- **Status:** accepted for simulator choice by user instruction; proposed for expansion details.

## Implementation phases and acceptance gates

### C1 - Preserve baseline and add capability probes

Verify v1 hashes, retain its inventory, and create a new configuration/output name. Add scene/action/camera probes under the ticket's scripts directory, then promote reusable pieces into `src/virtualhome_corpus/` where justified. Use only an owned port and keep graphics enabled. Exit with supported-scene/object/view evidence and explicit unsupported reasons.

### C2 - Label calibration and review tools

Add transition-neighborhood exports, reviewed label schema, and comparisons between raw action, world graph, and RGB evidence. Review both appliances across repeated runs and views. Exit with a calibration report, uncertainty bounds, and a precise list of labels eligible for each downstream metric. No global timing guarantee is required if evidence does not support one.

### C3 - Bounded v2 design and generation

Plan a modest expansion, initially at most 48 new episodes, varying one or two factors with grouped lineage. Record the intended comparison and expected artifact size before rendering. Add new scenes only after C1 passes. Generate with immutable provenance, separate attempts, and split rules; preserve failures. Exit with every planned case accounted for, all successful media validated, and no hidden cross-split lineage.

### C4 - Audit and consumer handoff

Extend integrity checks to review/source-hash compatibility, group lineage, and near-duplicate diagnostics. Inspect sampled footage from every scenario/view family and full transition neighborhoods in the calibration subset. Publish model-safe inputs, evaluator labels, review scope, resource totals, and known exclusions. Give Projects 2 and 3 only the label subsets appropriate to their metrics; give Project 4 separately identified endpoint and temporal rule truth.

## API references and operational limits

The installed `simulation/unity_simulator/comm_unity.py` exposes `reset` at line 214, `add_character` at 121, `add_camera` at 175, `environment_graph` at 291, and `render_script` at 332. The local generator demonstrates their actual success/result conventions. `<char0>` is an actor ordinal in a program, not a world graph node ID. Rebind appliance IDs after reset and verify final executed state rather than trusting the intended script.

The generator refuses resume when configuration, installation metadata, or exporter source hashes change. Use a fresh v2 output directory after modifying export behavior. Its filesystem lock protects a corpus directory, not all clients of a simulator port; operational ownership must remain explicit. Stop only the process launched for this run after rendering and verification.

## First review exercise

Choose an episode whose raw OPEN interval begins before the door is visibly open. Compare the action row, graph transition, and native-resolution RGB frames. Write down what each source actually establishes. If the only defensible visual statement is "the door became open somewhere between these two frames," preserve that interval. That is stronger scientific evidence than a precise timestamp copied from an uncalibrated export.

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
