---
Title: Intern analysis design and implementation guide
Ticket: VIDEO-ACTIONS-001
Status: active
Topics:
    - video
    - embeddings
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles: []
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T17:01:56.024769-04:00
WhatFor: ""
WhenToUse: ""
---

# Action discrimination benchmark: intern analysis, design, and implementation guide

## Purpose and measurable outcome

This project determines whether the repaired native-video encoder distinguishes household action identity and direction across varied source situations. It constructs balanced candidate examples for opening/closing, picking up/putting down, sitting/standing, and switching on/off, with approach-only controls. It then separates candidate balance from visually confirmed eligibility, and compares native video with pooled representations on the same original frames.

The required outcome is an implemented, reproducible benchmark and measured report. A favorable native score is not an acceptance requirement. Completion requires real model inference, source-bound reviewed labels, opposite-direction controls, grouped partitions, recorded failures, and an explanation of which conclusions the data support. Fine-tuning the large video encoder and deploying an action service are outside this ticket; small frozen-feature heads and temporal sequences belong to the next ticket.

## Current architecture and gaps

The existing diversity planner creates 48 full trajectories across three apartments, four families, two conditions, and two camera views. Door and switch interactions contain inverse operations. Pickup uses Grab followed by PutObjBack. Posture currently ends after Sit, so a standing action is missing from its program. `program_for` in `diversity.py` contains these exact choices. The current release must remain immutable; a new version must introduce inverse posture and record its own successful attempts.

The fixed two-second diversity clips control duration but do not automatically contain a complete requested action. The detector pilot already found tiny props and occluded targets, while calibration found appliance graph states that disagree with RGB. A direction benchmark must therefore inspect the temporal sequence rather than copy graph state into labels. Existing development retrieval uses weak program interiors and a single scene group. It measures retrieval under that protocol, not balanced direction discrimination.

The local simulator API can render programs, add fixed cameras, and export per-frame source data. A new generation command should reuse the validated runner lifecycle and introduce explicit versioned program policy rather than monkey-patching the previous release. The first capability probe must establish the installed spelling and behavior of the stand-up operation and the visible put-back behavior. If a target cannot support an operation, preserve the failure and choose a verified binding within the same declared family, recording the change before rendering the final dataset.

## Dataset design and partition policy

The initial design reuses the three-apartment/four-family/two-view organization and creates complete paired interactions plus approach-only controls in a new release. Each interaction should contain both directions in its family. This yields a planned 48-trajectory collection and a candidate inventory of 48 direction examples plus 24 controls, before any visual exclusions. The number is a bounded initial experiment, not a claim of independent statistical power. A lineage includes the scene, target, initial actor placement, program policy, and camera family. All derived windows and interventions from one lineage remain in its assigned partition.

The candidate table records requested action separately from reviewed visible action. A reviewer can mark an example visible, partial, ambiguous, or unobservable. Only sufficiently visible action direction is eligible for the primary classification score. Excluded examples remain in the coverage denominator and failure report. Both raw candidate counts and eligible counts are reported by action, apartment, target class, and view. If one direction disappears after review, do not rebalance by duplicating a successful example or count a reversed movie as a new simulator execution.

Use fixed-duration windows around program-derived candidate intervals, with actual timestamps retained. The policy must define how windows near video boundaries are handled; prefer shifting a fixed window within source bounds rather than padding with unrelated frames. Short videos may require an explicit insufficient-duration status. Declare the window duration and sampling frequency before model scoring. Program intervals may center the review proposal, but they do not certify that the action happened at that exact time.

```text
versioned simulator config
          |
  paired programs + controls
          |
source RGB + PTS + lineage ------> model-safe candidate windows
          |                                  |
     visual review                       three encoders
          |                                  |
reviewed labels and exclusions --------> evaluator
                                             |
                        class/direction/coverage report
```

## Records and interfaces

Proposed implementation modules live in `workbench/src/video_workbench/actions/`. `data.py` owns source-window validation and label joins. `encode.py` runs one representation in its appropriate environment. `evaluate.py` calculates fixed-query scores and preserves raw predictions. `review.py` generates a source-only review page and records reviewed labels. Ticket scripts provide repeatable commands and reference the same modules rather than carrying a second implementation.

```python
# Proposed record shapes, with image content external to JSON.
Candidate = {
    'sample_id': 'digest', 'episode_id': 'opaque',
    'video_sha256': 'sha256', 'lineage_id': 'digest',
    'split': 'train', 'start_us': 0, 'end_us': 4000000,
    'selected_pts_us': [0, 500000, 1000000],
    'condition': 'original', 'parent_sample_id': None,
}
Review = {
    'sample_id': 'digest', 'action': 'open',
    'visibility': 'visible', 'rationale': 'Observed door motion',
    'reviewer': 'identified reviewer', 'source_sha256': 'sha256',
}
```

Production records must include the complete selected frame list; the abbreviated example illustrates the fields, not a valid four-second sample. Source and evaluator files must be loadable independently. Validation rejects duplicate IDs, cross-split lineage, source mismatch, nonmonotonic source times, unknown action labels, or incompatible feature spaces. Changing a review creates a new label revision; it does not mutate model features.

## Representations and temporal interventions

The primary systems are accepted FP32 native video and preserved 4-bit image pooling. Add an FP32 image-pooling control using the same official artifacts and repaired wrapper as native. That adapter must process individual images with the official image processor and average normalized frame vectors, while retaining a distinct feature-space identity. The control reduces weight-precision and tokenizer differences; image versus video token structure and preprocessing remain architectural differences that must be documented.

For each original source window, create reversed-order and repeated-frame interventions. Reversal changes image order while keeping the slot timestamps increasing; passing decreasing PTS into the accepted native adapter would violate its contract. Record both slot PTS and source-image provenance so a reversed clip cannot be mistaken for original source chronology. A repeated-first-frame control keeps the same number of temporal slots but replaces every image with the first one. All interventions remain in their parent's partition.

A reversed clip is a diagnostic input, not a newly labeled real action. A person standing in a movie played backwards may resemble sitting, but contact dynamics and simulator animations can be physically implausible. Report changes in action margins and rankings under reversal separately from accuracy on original videos. Mean pooling must be invariant to frame permutation up to numerical tolerance; this is a software test and a baseline property. Repeated-frame controls diagnose whether the native result depends on motion rather than only static scene content.

```text
for candidate in frozen_candidates:
    frames, source_pts = decode_verified(candidate)
    for transform in [original, reverse, repeat_first]:
        images = transform_pixels(frames)
        slots = source_pts          # monotonic temporal slots
        provenance = source_frame_mapping(transform)
        native = encode_video(images, slots)
        pooled = unit(mean(encode_each_image(images)))
        save_vector_and_identity(transform, provenance)
```

Do not compare native and pooled vectors directly. Encode the same fixed action query texts in each system's own space and compare their rankings or within-space margins. The query set includes both directions and a no-target-action description for controls. Candidate scoring must not receive the requested program verb or reviewed action as prompt context. Report generic action discrimination and family-conditioned direction margins distinctly, since telling the model the family makes an easier task.

## Metrics, controls, and failure analysis

Primary metrics on original eligible examples are macro F1, balanced accuracy, per-class confusion, and control false-action rate. Coverage is eligible reviewed examples divided by all proposed examples. For direction pairs, report the margin between opposite text hypotheses, with a sign convention fixed in the protocol. Keep an UNKNOWN review category outside positive action training; separately report how often the model answers an action on unknown examples. If fitting an abstention threshold, fit only on development and freeze it before held-out evaluation.

Retrieval is a secondary view: use identical original windows and query text for each representation, report Success@K and interval coverage with the same relevance policy, and preserve raw top hits. Do not combine original and reversed variants into one retrieval gallery because near-duplicates would change candidate density. Aggregate by lineage or episode rather than pretending every adjacent frame is independent. Report the small number of scene groups and avoid confidence claims unsupported by that sample size.

A useful failure gallery includes a direction confusion, an approach-only false action, an occluded prop, a small object, and a case where reversing time changes the native score. Each caption identifies the source interval, review status, prediction, and model identity. The gallery is selected after evaluation and must not be used to retune a frozen test result.

## Decisions

### Decision: version a new paired-action release

- **Context:** The existing posture program lacks standing and historical releases are already evaluated.
- **Options considered:** Rewrite old programs, synthesize reversed movies as labels, or generate a new release.
- **Decision:** Generate a new release with verified inverse operations and retain previous media.
- **Rationale:** This preserves provenance and provides real rendered inverse actions.
- **Consequences:** Additional rendering and review are required; exact counts may decrease after honest visibility exclusions.
- **Status:** accepted.

### Decision: distinguish system comparison from temporal attribution

- **Context:** The current native and pooled systems differ in precision and preprocessing.
- **Options considered:** Claim any gain is temporal, compare only existing systems, or add a same-artifact FP32 pooling control.
- **Decision:** Run all three representations plus order/static interventions.
- **Rationale:** The controls narrow plausible causes without claiming complete architectural isolation.
- **Consequences:** Separate environments and cache namespaces are necessary; run GPU jobs sequentially.
- **Status:** accepted.

## Implementation phases and gates

- **A1 — Corpus and review.** Probe inverse operations, add versioned paired generation, create source-bound windows, review all families/views, and audit lineages. Gate: both directions and controls exist as candidates, with actual eligibility counts and preserved failures.
- **A2 — Encoders and interventions.** Implement the FP32 pooled adapter, native/4-bit runs, order/static variants, identities, and cache reuse. Gate: real vectors, source parity, native pixel dependence, and pooled permutation invariance.
- **A3 — Frozen evaluation.** Freeze queries and partitions, run all conditions sequentially, report class/direction/coverage metrics and raw predictions. Gate: no test-driven tuning and no mixed feature-space comparisons.
- **A4 — Evidence and temporal handoff.** Save screenshots, reports, manifests, and timestamped feature sequences usable by VIDEO-TEMPORAL-001. Gate: downstream sequence construction can locate every feature's source and availability.

## Test and review strategy

Unit tests should cover source-window boundary handling, lineage split rejection, intervention provenance, pooled permutation invariance, score orientation, and hand-computed confusion/macro metrics. Model smoke tests establish actual FP32 image and native video behavior; mocks cannot establish pixel dependence. Integration tests verify completed caches can be reused and corrupted source/feature identities fail. Review screenshots at native source resolution before accepting action labels. Use existing media and immutable runs to keep tests fast; reserve simulator execution for explicit capability and corpus runs.

The main residual risk is visual eligibility rather than generator success. A successful StandUp call may occur behind furniture, and a small returned prop may remain invisible. Record this directly, adjust future scenarios with a new version, and retain the original failed or excluded observation. The intern's job is to produce an honest benchmark whose limitations are inspectable.

## Shared evidence system: what an intern must understand first

The repository has two Python application layers. `src/virtualhome_corpus/` plans and renders simulator episodes. `workbench/src/video_workbench/` reads registered media and computes derived evidence. Generated media, model weights, and large arrays live under `output/`, which is ignored by Git. Ticket directories under `ttmp/` retain the protocol, design, diary, scripts, selected screenshots, and evaluation records. A Git commit alone does not contain enough bytes to reproduce a model run; it identifies the code and the manifests needed to find and verify those bytes.

A simulator program is an instruction sequence, while a source video is a sequence of rendered observations. The program can say Open even when a camera cannot see the door or the rendered state does not change. Therefore the generator exports program-derived annotations as weak supervision. An evaluator may use those annotations to propose review windows, but the model-facing input must not contain action names, desired outcomes, graph states, or reviewed answers. Source identity, timing metadata, and partitions are allowed inputs because they locate and organize observations rather than supply their interpretation.

The `Registry` API in `registry.py` accepts model-safe episode records and checks media metadata and hashes. Its `episodes(split)` method returns registered source paths and presentation timestamps. `media.selected_indices(pts, start, end, fps)` selects actual frames inside a half-open interval. `media.decode_selected(video, indices)` returns PIL RGB images. Time is represented as integer microseconds; retain raw PTS, time base, and origin so a conversion remains auditable. The end of `[start_us,end_us)` is excluded. A frame exactly at the end belongs to the next interval.

An embedding is a fixed-dimensional vector produced from an image, clip, or text. Cosine comparison requires compatible normalization and a shared feature space. The feature-space identity includes model artifacts, preprocessing, pooling, runtime, and relevant producer code. Two vectors both having 2,048 entries is insufficient evidence that they can be compared. `Index(manifest, expected_space)` checks the space and array identity before ranking; callers must not relabel old arrays to fit a new encoder.

The accepted native runtime is `output/mlx-video-fix/.venv` with the repaired MLX-VLM fork at `6452614f6de04694d1e34fd13abaca11f6ffb994`, official FP32 weights, and pinned official preprocessing. `NativeVideoEmbedder.video(frames, pts_us, start_us)` receives source images and increasing timestamps. It accepts at most 32 selected frames, repeats the last image and timestamp for odd input counts, and returns a normalized vector. `text(query)` uses the same feature space. The existing `QwenEmbedder` in `embedding.py` remains a distinct community 4-bit pooled-image baseline. Its environment is `workbench/.venv`. Never install both conflicting runtime extras into one environment.

The first matched native comparison encoded 55 development clips. Interval Recall@5 improved from 0.25 to 0.4375, but both microwave query families remained unsuccessful at K=5. This justifies a more discriminating experiment; it does not establish action understanding. The corresponding report is in VIDEO-SEARCH-001 reference 04. The independent YOLO report is in VIDEO-PERCEPTION-001 reference 02. Read both before interpreting a successful numeric output as a useful observation.

## Producer identity, failures, and publication

Every completed experiment must preserve hashes of its configuration, model-facing inputs, labels, model artifacts, and feature arrays. Keep labels in a separate file whose revision is included in the evaluation producer. Store a row-level status for missing evidence rather than dropping the row and changing the denominator. Failed generation attempts remain in numbered attempt directories; a timeout does not establish that Unity stopped rendering. Poll the owned process or request before retrying, and never reset another agent's simulator.

A useful publication sequence is: create a new output directory, write pending artifacts, validate their shapes and hashes, atomically publish a completion manifest, and only then expose the run in a viewer. A manifest should distinguish runtime completion from experimental quality. It is valid for a completed experiment to report that a detector missed every target or that an action classifier failed a class. It is invalid to mark an experiment complete if the required model never ran and only a stub output exists.

The implementation diary follows the diary skill, with prompt context, changes, commands, exact failures, review instructions, and future work. Save screenshots at meaningful review points. Print a plan before the project and a status slip at substantive phase boundaries; retain the YAML and actual print receipt, distinguishing HTTP success from an uncertain timeout. Commit code and evidence at phase boundaries using explicit paths so concurrent work remains outside the commit.

## Shared references and API reading order

Read these existing local files in order; the new modules named elsewhere in this guide are proposed until their implementation tasks pass:

1. `docs/playbook/virtualhome-video-generation.md`: installed simulator, owned process, readiness, recording, and source review.
2. `src/virtualhome_corpus/diversity.py`: target affordance checks, scenario lineages, camera geometry, and program construction.
3. `src/virtualhome_corpus/diversity_runner.py`: reset/render/export lifecycle, numbered attempts, source hashes, and validation.
4. `workbench/src/video_workbench/registry.py` and `media.py`: source registration and actual timestamp sampling.
5. `workbench/src/video_workbench/native_video.py`: accepted wrapper/artifact checks and official processor invocation.
6. `workbench/src/video_workbench/perception/contracts.py` and `predicates/contracts.py`: geometry, evidence, and unknown state semantics.

The primary VirtualHome repository documents the distinction between program execution, graph simulation, and Unity-rendered video. Local installed AIST source and the successful playbook govern actual call signatures on this machine. [VirtualHome project reference](https://github.com/xavierpuigf/virtualhome).

## Review checklist for the intern

Before requesting review, demonstrate that source hashes match, labels are excluded from inference inputs, every model condition has its own producer identity, and all required partitions and classes are counted. Point to raw records for each aggregate metric. Include at least one failure screenshot. Explain whether an experiment tests software correctness, representation quality, or end-to-end evidence availability; do not use one as proof of another.

No module should silently turn a missing observation into background, invent a class label from a simulator instruction, or use a future frame before its declared availability. These rules are shared with VIDEO-TEMPORAL-001, where a prediction becomes an input to temporal decoding and durable memory. Correctness at the source boundary prevents later code from hiding a data failure with a plausible sequence.
