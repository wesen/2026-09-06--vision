---
Title: Intern analysis design and implementation guide
Ticket: VIDEO-LOCALIZATION-001
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
LastUpdated: 2026-09-06T17:01:56.274637-04:00
WhatFor: ""
WhenToUse: ""
---

# Requested-object localization: intern analysis, design, and implementation guide

## Purpose and measurable outcome

This project identifies why the YOLO crop pipeline fails to provide requested objects and measures whether better localization can improve observable-state recognition. It annotates source frames at the actual state sample times, evaluates requested-object coverage across confidence policies and visual conditions, compares detector crops with manually reviewed crops, and reruns fixed state baselines with explicit missing evidence.

The deliverable is a complete diagnostic pipeline and measured report. It does not require a favorable detector or state score. The existing state follow-up had accepted crops for 46/96 training frames, 23/24 development frames, and 0/24 held-out frames. Treating crop-only zero errors as good abstention would conceal that total held-out localization failure. This ticket makes the missing evidence measurable at the object boundary.

## Current architecture and observed failure

`perception/pipeline.py` decodes every registered native frame and writes YOLO detections with source geometry. `tracking.py` associates saved boxes. `derive.py` materializes contextual crops at periodic and state sample times. `predicates/regions.py` selects exactly one usable requested-class target crop. The map binds fridge to refrigerator and microwave to microwave. More than one candidate is ambiguous, while no candidate is missing; neither is a proof that the physical object is absent.

The detector is pinned YOLO11n in an isolated Ultralytics environment. The detection run retained boxes at confidence 0.10 and created usable crops under a stricter 0.25 policy. The pilot localized 11 of 19 supported visible targets at IoU at least 0.5; all three reviewed small targets were missed. Four targets had unsupported classes and one was unreviewable. These target-level counts are not full-scene average precision.

The state dataset contains 144 source-bound frames with reviewed open/closed/unknown labels. The labels concern visual state, not necessarily a complete object extent. This ticket must add an independent localization review and retain both label layers. A door can be impossible to classify as open or closed while part of the appliance remains localizable. Conversely, a requested object can be too ambiguous to assign a unique box even when a scene suggests its category.

## Annotation units and taxonomy

The primary unit is the requested entity in a particular source frame. Review the full-resolution image before viewing model predictions to reduce anchoring. Record a visible extent rectangle when a unique target can be identified. Preserve truncation and occlusion flags and distinguish visible extent from an estimated amodal full-object rectangle. Use visible extent for the baseline; do not alternate conventions within the same metric.

Localization statuses are visible_unique, partially_visible_unique, ambiguous_instances, unobservable, absent, and unsupported_category. Unsupported refers to the detector's class vocabulary, while unobservable refers to source evidence. They are separate axes in the stored schema even if a summary groups them. An object can be visible and unsupported. A requested class supplied by the task is not itself a reviewed object identity.

The initial annotation inventory includes all 144 existing state sample frames and the fixed small-prop/other-family pilot. Reuse prior reviewed boxes only when image hashes and annotation conventions match. Audit duplicate source frames before counting; repeated references to one image do not create independent observations. Review temporal contact sheets for context, but assign each rectangle to its exact frame and record whether temporal context was used by the annotator. Context-derived boxes must not be described as independently visible single-frame evidence.

```python
# Proposed localization review record.
ObjectReview = {
    'sample_id': 'source-bound id', 'episode_id': 'opaque',
    'frame_index': 0, 'image_sha256': 'sha256',
    'requested_entity': 'episode:target', 'requested_class': 'microwave',
    'visibility': 'partially_visible_unique',
    'visible_xyxy': [100, 80, 230, 175],
    'occluded': True, 'truncated': False,
    'detector_class_supported': True,
    'reviewer': 'identified reviewer', 'rationale': 'Visible front panel',
}
```

A missing rectangle is null, not `[0,0,0,0]`. Validation requires finite positive coordinates within the image, a rationale for ambiguous/unobservable cases, and source-hash agreement. The label revision includes the reviewer and convention. Manual boxes are approximate annotations and should be described as single-reviewer estimates until a second review exists.

## Geometry and detector evaluation

Boxes use half-open source coordinates `[x0,y0,x1,y1)`. Intersection width is `max(0,min(ax1,bx1)-max(ax0,bx0))`, and intersection height is analogous. Intersection over union divides the intersection area by the combined area minus intersection. Reject degenerate boxes before division. Pixel rounding should occur only when extracting raster crops, with the resulting integer source rectangle preserved separately from the reviewed float coordinates.

A correct requested-class localization requires both the mapped class and sufficient overlap. Report recall at IoU 0.5 under frozen confidence policies 0.10, 0.25, and 0.50. Because the stored detector run has a 0.10 floor, it cannot measure policies below that threshold without rerunning inference. The score sweep is descriptive across the frozen samples; selecting a deployment threshold must use development data only.

For each threshold, preserve candidate count, best IoU, accepted unique binding, ambiguous binding, no-class detection, wrong-class overlap, and source-size strata. Separate best-match detector recall from usable binding coverage. An oracle selecting the best-overlap box can localize correctly even when the production binder sees several same-class candidates and must abstain. Calling those two metrics equivalent would hide an entity-resolution failure.

```text
for sample in frozen_samples:
    review = lookup_review(sample)
    predictions = source_frame_detections(sample)
    for confidence in [0.10, 0.25, 0.50]:
        candidates = requested_class_boxes_above(confidence)
        localization = best_iou(candidates, review.visible_box)
        binding = unique_candidate_or_ambiguous_or_missing(candidates)
        save(review_status, localization, binding, size, view, split)
```

The upstream prediction API exposes result boxes with class, confidence, and coordinates. This project uses the installed pinned adapter and saved detections; it does not depend on changing defaults from the online documentation. [Ultralytics prediction reference](https://docs.ultralytics.com/modes/predict/).

## Controlled crop experiment

Create three primary evidence conditions at the exact same state sample times: F for original full frame, D for detector-selected crop, and O for a manually reviewed crop. Add F+D and F+O fusion if needed to distinguish loss of global context from a bad crop. All crop images use the same 25-percent expansion, clipping, 320-by-240 output size, and bicubic resize. When comparing crops, keep the encoder and state scoring method fixed so geometry is the changed factor.

O is an oracle-assisted diagnostic. It uses a human-provided location and cannot be presented as production evidence availability. A manually localized crop can answer whether the representation might succeed with better localization. It cannot prove that YOLO can deliver that crop. D keeps missing and ambiguous cases explicit. If the source target is unobservable, O also remains unavailable instead of drawing an imaginary full appliance.

State labels are joined only after crop selection and feature encoding. The existing text-margin and ridge-head implementations in `predicates/classify.py` can be reused with new feature identities. Fit heads on training rows with available visual labels; calibrate and choose abstention on development. Keep the existing test split as an explicitly reused exploratory partition. A new untouched test corpus would be required for a fresh generalization claim.

```text
reviewed source frame --------> full image F
          |
     +----+--------------------+
     |                         |
YOLO unique binding      reviewed visible rectangle
     |                         |
 detector crop D          diagnostic crop O
     |                         |
     +----- same image encoder +
                     |
          fixed state head / text margin
                     |
        coverage + risk + unknown errors
```

## Metrics and denominator rules

Report localization recall over supported reviewable targets; unsupported, ambiguous, absent, and unobservable examples remain in separate counts. Report end-to-end evidence coverage over all requested samples, including those without a crop. For state recognition, show known correct over all known states, known errors among answered known states, unknown false certainty, overall answer coverage, and missing-evidence count. Conditional accuracy alone is insufficient.

Use paired subsets to compare F, D, and O when all required evidence exists, and also show each condition over the full population. If no D crop exists in a test group, the paired metric is null with denominator zero, not zero accuracy or perfect accuracy. Missing inference has null raw score and probability. Model abstention after actual inference can retain numerical scores with an explicit reason. This is already represented in `StateObservation`; downstream temporal code must preserve the distinction.

Stratify by requested class, apartment, view, source area, and occlusion. A target below 1,024 square pixels is a useful predeclared small-object stratum inherited from the pilot, but it is not a universal boundary of detector capability. Show raw counts beside each rate. Do not derive full-scene precision or mask quality from one requested target per image.

## Implementation map and APIs

Proposed modules under `workbench/src/video_workbench/localization/` are `annotations.py` for reviewed source boxes, `evaluate.py` for target-level matching and coverage, `crops.py` for D/O materialization, and `experiment.py` for the fixed state diagnostic. A lightweight review page should show native source pixels, requested entity, reviewed rectangle, detector candidates, and state outcome; it should allow hiding predictions during source-first annotation.

Reuse `perception.contracts.expand`, crop transforms, and `crop_record` rather than inventing a second coordinate convention. Reuse source SHA checks and atomic JSON publication. When a new crop policy is introduced, include its identity in every crop and feature cache. Do not overwrite `output/video-perception/derived-v1` or the existing state region cache.

The local `NativeVideoEmbedder._encode` implementation demonstrates the accepted official processor path. If a new FP32 image adapter is shared with VIDEO-ACTIONS-001, give it a public image method and an explicit feature space instead of asking callers to rely on a private method indefinitely. This ticket's primary localization comparison should retain one fixed encoder across F/D/O, with any additional precision comparison clearly separate.

## Decisions

### Decision: manual crops diagnose an upstream failure

- **Context:** Every held-out requested microwave crop was missing in the production binder.
- **Options considered:** Lower thresholds until a crop appears, train a state model only on available crops, or compare detector and reviewed geometry explicitly.
- **Decision:** Evaluate frozen thresholds and an oracle-assisted geometry control, preserving missing cases.
- **Rationale:** This separates localization, binding, representation, and calibration failures.
- **Consequences:** Annotation effort is required, and oracle quality is not deployment quality.
- **Status:** accepted.

### Decision: defer model replacement until error categories are measured

- **Context:** Missing boxes can arise from unsupported classes, tiny targets, wrong class predictions, or ambiguous instances.
- **Options considered:** Fine-tune immediately, switch detector, or annotate/evaluate first.
- **Decision:** Complete the diagnostic before recommending a replacement or fine-tuning dataset.
- **Rationale:** Different failure categories require different interventions.
- **Consequences:** This ticket delivers a concrete next-model decision, not an unvalidated training run.
- **Status:** accepted.

## Implementation phases and gates

- **L1 — Annotation and source audit.** Freeze the 144 state frames plus deduplicated pilot targets, review source rectangles/statuses, and save contact sheets. Gate: no missing source binding, explicit visibility taxonomy, and per-group counts.
- **L2 — Localization measurement.** Evaluate frozen confidence policies, IoU, candidate ambiguity, wrong-class overlap, size, and occlusion strata. Gate: hand-computed metric tests and a raw row for every requested target.
- **L3 — Crop/state diagnostic.** Materialize D/O crops, encode F/D/O and paired fusion controls, fit the existing state methods under fixed partitions, and retain missing evidence. Gate: real model outputs, source/crop identities, and full-population plus paired metrics.
- **L4 — Review and handoff.** Publish failure/success screenshots, detailed report, and a measured localization improvement plan. Gate: no claim that oracle evidence is production coverage; temporal handoff retains unknowns and availability.

## Validation and unresolved risks

Tests must cover finite in-bounds annotation geometry, half-open IoU arithmetic, unsupported versus missing class distinctions, two-instance ambiguity, zero paired denominator, source hash mismatch, and crop transform round trips. A small actual-image smoke must verify that expanded crops contain the intended target. Reuse the state observation validation tests for paired null scores; do not create fake numerical confidence for missing evidence.

A single reviewer may underestimate hidden extents or identify a target using temporal context unavailable to a frame model. Preserve those flags and request independent review before treating the annotations as a strong benchmark. The current apartment/class assignment is confounded and the held-out state set has very few open examples. This ticket can establish a local diagnostic, while future balanced action/state generation must provide stronger generalization evidence.

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
