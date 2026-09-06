---
Title: Measured localization and crop state comparison report
Ticket: VIDEO-LOCALIZATION-001
Status: active
Topics:
    - video
    - embeddings
DocType: reference
Intent: long-term
Owners: []
RelatedFiles: []
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T18:24:08.034211-04:00
WhatFor: ""
WhenToUse: ""
---

# Requested-object localization and observable-state recognition

## Result and scope

Correctly reviewed object locations improve the learned state head on this small local diagnostic. The oracle-crop head identifies 16 of 17 known held-out states correctly, compared with 10 of 17 for the full-frame head. That improvement does not solve evidence availability or unknown-state recognition. The production detector provides no accepted crops for the 24 held-out state frames, and every evidence-bearing method answers all seven visually unknown held-out frames.

The experiment therefore supports two separate engineering priorities: improve requested-object localization, and implement an observability or abstention mechanism that is evaluated on unknown examples. A better state classifier alone cannot recover a missing crop. A better crop alone does not establish that an appliance door state is visible.

This report describes a completed local diagnostic using the installed AIST fork/build of VirtualHome, YOLO11n, and the existing community 4-bit Qwen image embedding model. It makes no claim about native-video acceptance for that checkpoint. Native and pooled action experiments belong to VIDEO-ACTIONS-001. The state test scenes have been inspected previously, so these results are exploratory rather than a fresh generalization estimate.

## Source population and annotation process

The inventory begins with 144 reviewed state samples and 24 requested-target references from the earlier perception pilot. Six pilot references point to existing state targets. Deduplication uses source video SHA256, exact frame index, and requested entity, leaving 162 unique localization units. Aliases preserve the original experiment IDs so state labels can be joined after inference without changing the population.

Each localization unit receives an independent localization review. The first pass views source images without detector predictions. The second pass overlays the manually supplied rectangle on the source. All 42 episode sheets were inspected, and three geometry errors were corrected: background above a refrigerator, an excluded outer refrigerator-door edge, and an excluded visible microwave-door portion. The prior draft, corrections, final annotations, and rendering hashes remain in `various/source-audit-v1/`.

The final review includes 86 visible unique objects, 72 partially visible unique objects, one unobservable book, and three ambiguous requested-instance cases. Thus 158 targets have rectangles. Four requested targets belong to unsupported detector categories: plates and table lamps. Two supported targets have no unique reviewable rectangle. The detector recall denominator is consequently 156, rather than 162 or 158.

Rectangles describe visible extents using half-open source coordinates. They include a protruding appliance door when visible, but do not infer a hidden edge behind an actor. Unsupported vocabulary and source visibility are separate axes. A table lamp can be visible despite having no supported detector mapping; an edge-on television can be localized while its screen state remains unobservable. The 144 state frames were reviewed in temporal contact sheets, and that context flag remains in the records.

These are approximate single-reviewer annotations. No inter-reviewer agreement was measured. Visible-extent rectangles can differ from the implicit amodal conventions of a pretrained detector, especially under occlusion. The results should be read with that limitation rather than treating annotation hashes as proof of semantic accuracy.

## Source verification and matching

`localization/detector_audit.py` checks the detector run identity, its producer identity, episode manifest hashes, JSONL artifact hashes, source video hashes, frame identity, native timestamps, dimensions, and detection vocabulary. A requested frame absent from the detector run raises an error. A processed frame with no boxes produces an empty detection list. These cases must remain distinct because only the latter is a measured detector output.

The original detector spec hashes an integer-keyed class dictionary. JSON serialization changes its keys to strings. Reconstructing the original integer keys reproduces the existing run and producer hashes exactly; the loader performs this explicitly before checking identities.

A requested target is localized when a box has the mapped class and intersection over union of at least 0.5 with the reviewed rectangle. Best-box recall and unique binding measure different behavior. Several same-class boxes may include a correct box, but the production binder cannot use the reviewed rectangle to decide which instance was requested.

```text
source frame + requested class
    -> verify detector source and producer
    -> filter by frozen confidence
    -> measure best requested-class IoU against review
    -> independently count usable class candidates
    -> preserve missing, unique, ambiguous, and unsupported outcomes
```

## Detector results

| Confidence | Localized / eligible | Recall | Unique correct | Ambiguous bindings |
|---|---:|---:|---:|---:|
| 0.10 | 123 / 156 | 78.8% | 104 | 19 |
| 0.25 | 78 / 156 | 50.0% | 74 | 4 |
| 0.50 | 46 / 156 | 29.5% | 45 | 1 |

The lower threshold retrieves more true target boxes but increases ambiguity. The sweep is descriptive; it does not authorize selecting a production threshold from held-out performance. Confidence 0.25 remains the fixed D-crop condition in the state comparison.

Microwave recall changes substantially: 69/96 at 0.10, 34/96 at 0.25, and 7/96 at 0.50. Refrigerator recall is 46/48, 36/48, and 32/48 respectively. Both beds are localized at every threshold. Four sofas are localized at 0.10 and 0.25, with three at 0.50. Only two of four reviewable TVs are localized at each threshold. The one reviewable book and one reviewable mug are missed throughout. These small class counts cannot establish population-wide detector performance.

Wrong-class boxes overlap six eligible targets at confidence 0.25. This distinguishes classification confusion from having no overlapping region at all. The raw audit includes class, split, apartment, view, size, and occlusion strata. Small means reviewed area below 1,024 pixels; the boundary is a predeclared diagnostic convention, not a universal detector limit. Full-scene average precision and segmentation-mask accuracy were not measured by this requested-target audit.

## Controlled evidence construction

The primary conditions are F, the original full frame; D, a uniquely bound detector crop; and O, a reviewed-location crop. FD and FO normalize the sum of the corresponding unit embeddings. When the crop is unavailable, fusion uses the full-frame vector. Both crop types use the same 25-percent expansion, source clipping, 320-by-240 raster size, and PIL bicubic interpolation. A minimum expanded extent of 12 pixels matches the existing production crop policy.

D selects exactly one usable requested-class candidate. It does not select the best IoU box using the review. O uses the manual location and is explicitly oracle-assisted. Crop preparation reads no reviewed state labels. Feature extraction then encodes the three image conditions with the same fixed Qwen image encoder and constructs the two fusions.

| Partition | State frames | D available | O available |
|---|---:|---:|---:|
| Train | 96 | 46 | 96 |
| Development | 24 | 23 | 24 |
| Test | 24 | 0 | 24 |

The independent materializer exactly reproduces the previous production state-crop coverage. Each feature array has shape `[144,2048]`. D has 69 available rows; the other conditions have 144. Missing D storage contains zero vectors with an availability mask, and the observation writer converts unavailable inference to null raw scores and probabilities. FD equals F numerically on all test rows, but its learned head and calibration differ because it was fitted on mixed evidence conditions.

## State fitting and evaluation

`localization/experiment.py` joins labels only after encoding. It follows original state aliases, verifies entity, image, video, frame, partition, and timestamp identity, and reorders labels to match feature rows. Ridge heads use available known training examples with the existing ridge strength 0.01. Text scores compare open and closed hypothesis embeddings. Platt calibration and the abstention policy use available known development examples only.

This design holds encoder and scoring methods fixed while refitting each condition on its own representation. It measures the learnability of each representation under the existing partitions, rather than applying one shared fitted head across incompatible input distributions. Full-population metrics count missing evidence, known correct answers, known errors, and answers on unknown states. A paired subset includes rows where F, D, and O are all available. The paired test denominator is zero, so its metrics are null.

| Linear-head condition | Known correct / 17 | Known errors | Unknown answers / 7 | Test evidence / 24 |
|---|---:|---:|---:|---:|
| F | 10 | 7 | 7 | 24 |
| D | 0 | 0 | 0 | 0 |
| O | 16 | 1 | 7 | 24 |
| FD | 3 | 14 | 7 | 24 |
| FO | 16 | 1 | 7 | 24 |

The D row is an evidence failure, not a successful low-risk classifier. O and FO improve known-state classification but still answer every unknown example. Their known-state confusion is 15 true negatives, one true positive, one false negative, and no false positives. There are only two known open test frames, making any action-specific interpretation fragile.

All evidence-bearing text-margin conditions classify the 15 known closed frames correctly and miss both known open frames. Their apparent known-state accuracy of 15/17 is therefore dominated by the class imbalance. They also answer all seven unknown frames. The FD linear result demonstrates that fallback availability does not guarantee distributional compatibility: test FD vectors equal F, but a head fitted on fused training evidence can perform substantially differently.

## Visual evidence and artifact reading order

The checked source overlays are under `various/source-audit-v1/overlay-checkpoint/` and `overlay-final/`. `various/crop-comparison-v1/source-detector-oracle.jpg` shows full-frame, detector, and reviewed crops, including missing detector evidence. Its initial checkpoint contains repeated rows and must not be interpreted as additional independent samples. All quantitative results use the deduplicated population.

Read the following files together:

- `various/source-audit-v1/freeze-v1.json`, `reviews-v1.json`, and `overlay-corrections.json`: annotation revision and explicit limitations.
- `various/detector-audit-v1/summary.json` and `rows.json`: aggregate and target-level localization outcomes.
- `various/crop-comparison-v1/crop-manifest.json`: source rectangles, hashes, detector IDs, and oracle provenance.
- `various/crop-comparison-v1/feature-metadata.json`: actual encoder identity and feature archive hash.
- `various/state-comparison-v1/results.json`: fitted parameters, training/development row IDs, and full/paired metrics.
- `various/state-comparison-v1/observations.jsonl`: all 1,440 condition-specific observations, including 150 unavailable D inferences.

Large arrays and crop rasters remain under `output/localization-v1/`. The tracked manifests identify those bytes but do not embed all model weights or arrays. The source implementations are `annotations.py`, `detector_audit.py`, `crops.py`, `features.py`, `experiment.py`, and `handoff.py` under `workbench/src/video_workbench/localization/`.

The final outcome gallery in `various/outcome-gallery-v1/` contains five distinct samples with source detector overlays, D/O rasters, reviewed state, and all five linear-head outcomes. It includes a successful training crop, a development crop, a known open test example, an unknown test example, and the oracle-head test error. All five sheets were visually inspected. Reproduce it with `scripts/02-outcome-gallery.py`.

## Improvement plan

First, construct a balanced validation corpus crossing appliance class, apartment, camera view, visible state, occlusion, and object size. Keep lineage groups together across splits and preserve unknown examples. The current apartment/class assignment and small positive counts prevent a reliable estimate of generalization. The installed AIST/VirtualHome build should be validated per scenario; the observed execution failures do not establish that every VirtualHome version has the same behavior.

Second, benchmark a higher-capacity or higher-resolution detector on that frozen corpus before fine-tuning. Evaluate recall and unique requested-instance binding separately. The confidence sweep shows available low-score detections, but lowering the threshold alone increases ambiguity. Unsupported classes need a vocabulary strategy, while small props need sufficient source pixels and suitable training examples. Neither problem is fixed by calibrating the state head.

Third, add a dedicated observability decision or train abstention using unknown examples. Evaluate unknown false certainty and coverage jointly. The current known-only development calibration cannot be claimed to control risk on visually unknown states. Preserve null outcomes rather than forcing open/closed decisions.

Fourth, evaluate fusion and fallback explicitly under missing-crop conditions. Train and development should contain the missingness patterns expected at deployment. Retain F as a measured fallback baseline; do not assume that a fusion head behaves like the F head when its feature input happens to equal F.

Fine-tuning is deferred until these failure categories and balanced partitions are available. The immediate engineering value of this ticket is the source-bound diagnostic and evidence contracts, not an unvalidated detector replacement.

## Temporal handoff

The handoff separates production-available F/D/FD observations from oracle O/FO observations. It retains source video/image hashes, entity, frame index, event time, availability time, evidence citations, producer, feature space, unknown reason, and null missing scores. Consumers must select one producer/condition rather than counting alternative predictions as independent observations.

Availability currently equals the offline source horizon. It does not include measured inference or database commit latency. The temporal implementation must preserve the difference between event, availability, and commit clocks rather than treating these exported times as a live latency measurement. Six sampled frames per episode are sparse state observations, not dense temporal ground truth. Dense trailing-window features remain a separate VIDEO-TEMPORAL-001 implementation requirement.

## Validation and limits

Six localization contract tests cover rectangle/source validity, IoU matching, class ambiguity, unsupported categories, changed artifacts, missing frames, and equal-policy crop rasterization. The completed feature check validates shapes, normalization, missing storage, and fusion fallback. All 1,440 exported StateObservation records pass the existing observation contract; missing D rows retain paired null scores. These checks establish software and artifact integrity, not annotation consensus or real-world state reliability.

The intern guides were already rendered, visually reviewed, and uploaded to reMarkable. This report records measured implementation results. Meaningful print slips remain pending because automatic approval review rejected the external Almanach print-service request; no successful print receipt is claimed for the blocked boundaries.
