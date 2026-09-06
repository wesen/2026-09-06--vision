---
Title: Implementation diary
Ticket: VIDEO-LOCALIZATION-001
Status: active
Topics:
    - video
    - embeddings
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/localization/__main__.py
      Note: Prepare and review CLI
    - Path: repo://workbench/src/video_workbench/localization/annotations.py
      Note: Visibility and geometry contracts
    - Path: repo://workbench/src/video_workbench/localization/crops.py
      Note: Controlled detector and oracle crop materialization
    - Path: repo://workbench/src/video_workbench/localization/data.py
      Note: Source-hash audit and requested-target deduplication
    - Path: repo://workbench/src/video_workbench/localization/detector_audit.py
      Note: Verified detector source joins and measured confidence sweep
    - Path: repo://workbench/src/video_workbench/localization/evaluate.py
      Note: Best-overlap recall versus unique binding
    - Path: repo://workbench/src/video_workbench/localization/experiment.py
      Note: Measured fixed state comparison and source-bound missing observations
    - Path: repo://workbench/src/video_workbench/localization/features.py
      Note: Actual fixed image features and explicit missing masks
    - Path: repo://workbench/src/video_workbench/localization/review.py
      Note: Source-verified overlay renderer and provisional annotation review checkpoint
    - Path: repo://workbench/src/video_workbench/perception/contracts.py
      Note: Shared half-open geometry
    - Path: repo://workbench/src/video_workbench/predicates/regions.py
      Note: Existing production requested-class binder
    - Path: repo://workbench/tests/test_localization_contracts.py
      Note: |-
        Hand-computed metric and review checks
        Exact population and changed-source rejection tests
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T17:01:56.371871-04:00
WhatFor: ""
WhenToUse: ""
---






# Implementation diary

## Goal

Complete VIDEO-LOCALIZATION-001 as part of the active three-ticket objective, preserving the full design, delivery, implementation, evaluation, screenshot, and commit requirements. VIDEO-TEMPORAL-001 remains part of the same goal.

## Step 1: Create the ticket and develop the intern design

Created the ticket and detailed intern guide after inspecting the existing simulator, native FP32 adapter, detector/state contracts, and completed evaluation reports. The design assigns explicit phases and acceptance gates rather than treating a successful runtime call as a quality result.

### Prompt Context
**User prompt (verbatim):** "create both tickets, Create  a detailed analysis / design / implementation guide that is for a new intern, explaining all the parts of the system needed to understand what it is, with prose paragraphs and bullet point sand pseudocode and diagrams and api references and file references. It should be very clear and technical. Store in the ticket and the nupload to remarkable for each. Then implement all 3 tickets, commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill), Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Create and deliver both new guides, then implement actions, localization, and temporal models/memory completely.

**Inferred user intent:** A sustained implementation effort with intern-readable explanations, reviewable evidence, and chronological progress records.

### What I did
- Created both ticket workspaces, design guides, diaries, phased tasks, and source relations with docmgr.
- Read the existing temporal design and diary so its full T1–T4 scope remains intact.
- Checked local API signatures and primary VirtualHome, Ultralytics, PyTorch, and sqlite3 references.
- Rendered eight-page guides with the established Pandoc/XeLaTeX configuration and rasterized every page.
- Printed the overall plan: HTTP 200, printed true, 2026-09-06T21:02:54Z.

### Why
The new work must separate action direction, localization availability, state inference, and temporal reasoning while preserving compatible time/provenance contracts.

### What worked
Both tickets pass docmgr doctor. Existing runtimes and source assets provide concrete starting points. The initial PDF renders succeeded and contact sheets exposed readable diagrams and pseudocode.

### What didn't work
A guessed AIST path under `virtualhome/simulation` did not exist; the installed source uses `simulation/` directly. Inspected that actual path and found STANDUP in the action definitions. A guide reference used `expanded_rect`; inspection corrected it to the existing `perception.contracts.expand`. The action diagram initially said four encoders instead of three and was corrected before upload.

### What I learned
The existing posture generator stops after Sit, so a new version must add a real standing operation. The source API lists STANDUP, but successful visible Unity behavior still requires a capability probe.

### What was tricky to build
Guides must distinguish proposed modules from installed APIs and include explicit gates for weak versus visually reviewed labels. Reversed movies are diagnostic interventions, not new labeled simulator actions.

### What warrants a second pair of eyes
Single-reviewer visibility and box annotations, apartment/class confounds, and source-versus-availability semantics. The guides do not claim that the proposed implementation is already complete.

### What should be done in the future
Finish PDF visual approval and individual reMarkable uploads, then execute the ticket phases without dropping the remaining temporal project.

### Code review instructions
Read the intern guide, tasks, related source files, and PDF validation record. The shared delivery script lives in the actions ticket's `scripts/01-deliver-guides.py`.

### Technical details
Guides are under `design-doc/`; rendering artifacts are under `output/pdf/next-guides/`. The task-specific simulator will use its own port and process. Native GPU inference remains isolated from pooled and detector environments.

## Step 2: Deliver the reviewed guide and begin the paired-action phase

Both eight-page guides passed full contact-sheet review and selected full-page inspection. Source hashes were frozen after correcting the action encoder count and localization API reference. Each guide's dry-run and real upload completed successfully, with the positive receipt retained.

### Prompt Context
**User prompt (verbatim):** See Step 1.

**Assistant interpretation:** Finish independent guide delivery, then implement all three projects.

**Inferred user intent:** Read the designs on reMarkable while implementation continues with evidence and phase checkpoints.

### What I did
- Rendered both guides, inspected all pages, and recorded reviewed source/PDF hashes.
- Uploaded each guide to its own `/ai/2026/09/06/` ticket folder; both returned `OK: uploaded`.
- Added the explicit paired-actions program policy with Sit/LookAt/StandUp; kept the prior release's behavior as the default.
- Added an owned simulator launcher on port 18084 and a three-apartment posture capability probe.

### Why
Guide delivery must precede implementation, and a listed simulator operation must be exercised before relying on it in the complete corpus.

### What worked
`PYTHONPATH=src workbench/.venv/bin/python -m pytest tests -q` passed 19 tests and five subtests. Both reMarkable uploads succeeded. The A1 start slip printed successfully at 2026-09-06T21:11:56Z.

### What didn't work
No PDF compilation or upload failure occurred. The simulator probe is still running and is not yet recorded as successful.

### What I learned
The existing generator can preserve its old program semantics while selecting an explicit new policy in a separately named release.

### What was tricky to build
The provided simulator launcher shares one log filename, so the task uses its own launcher and log as well as a separate port. No existing simulator was reset.

### What warrants a second pair of eyes
The added inverse posture operation still needs visible source confirmation; passing a program test does not establish useful rendering.

### What should be done in the future
Complete capability probes, render/review the paired corpus, implement all representation controls, then finish localization and temporal tasks under the same active goal.

### Code review instructions
Inspect the delivered guides and receipts, `configs/virtualhome-paired-actions-v1.json`, the optional program policy, and its inverse-posture test.

### Technical details
Owned simulator port: 18084. Corpus destination: `output/virtualhome-corpus/paired-actions-v1`. Simulator log: `output/action-benchmark-v1/unity.log`.

## Step 3: Freeze localization sources and separate recall from usable binding

Started the localization implementation after the action benchmark report. The inventory joins all 144 state samples and 24 pilot references by source video hash, exact frame, and requested entity. Six pilot references duplicate existing state targets, leaving 162 unique annotation units. Every imported image and video hash was checked. Source-only review sheets contain no detector predictions or state labels.

Implemented explicit visibility/geometry validation and pure target matching under the frozen confidence policies. Best-overlap localization can succeed while multiple requested-class boxes make production binding ambiguous. These outcomes remain separate. Started source annotation with six draft rectangles on the first temporal sheet; 156 targets remain unreviewed, so no measured localization recall is published yet.

### Prompt Context
**User prompt (verbatim):** (see Step 1).

**Assistant interpretation:** Continue the full requested three-ticket implementation with localization source review, tests, diary, and evidence.

**Inferred user intent:** Determine whether detector localization or downstream state recognition causes missing and incorrect object evidence.

**Commit (code):** `6cf3cc2` — Add deduplicated localization source inventory and target matching contracts.

### What I did
- Read the localization design, previous state sample schema, detector records, and pilot rectangle conventions.
- Added `localization/data.py` and CLI commands to verify hashes, deduplicate requested entities, retain original aliases, and render native source review sheets.
- Added separate class-support and visibility fields with finite half-open rectangle validation.
- Added confidence-policy target matching, wrong-class overlap, best IoU, unique binding, size strata, and null zero-denominator summaries.
- Generated 42 source sheets for 162 targets; preserved the inventory, sheet index, initial source sheet, and in-progress review in the ticket.
- Saved a local phase-plan layout with `--no-print`. It has not been printed; the prior Almanach destination approval remains pending.

### Why
The same source frame must not count twice because it appears in two earlier experiments. Requested class, reviewed visibility, detector vocabulary support, best matching box, and uniquely usable evidence answer different questions and require separate fields.

### What worked
- Source inventory: 168 references, 162 unique requested targets, six duplicates, all 144 state references preserved.
- All source image and video hashes matched after resolving the actual successful attempt path.
- New geometry tests verify exact IoU 0.5, ambiguous two-instance binding, wrong-class overlap, unsupported categories, null empty denominators, and review identity rejection.
- Combined corpus/action/localization contract run: 27 tests passed and five subtests passed.

### What didn't work
The initial pilot importer assumed `attempt-0001/video.mp4`. It failed with `FileNotFoundError: [Errno 2] No such file or directory: 'output/virtualhome-corpus/diversity-v2/episodes/dv-673fa0ed90d3c06a/attempt-0001/video.mp4'`. The completed episode manifest identifies `attempt-0002`. Changed the importer to follow that manifest and reran successfully. The failed import published no dataset directory.

### What I learned
Numbered attempts are authoritative provenance, not a cosmetic filename convention. Source duplication must include requested entity identity as well as frame identity because one image could support multiple independent target questions.

### What was tricky to build
Visibility and detector class support are independent axes. An unsupported plate can still have a visible rectangle; a supported microwave can be unobservable. Similarly, a unique wrong-location class detection is a binding output but not correct localization. The metrics retain each distinction rather than equating a nonempty box list with successful evidence.

### What warrants a second pair of eyes
The first six rectangles are draft single-reviewer visible extents and use temporal contact-sheet context. Overlay review is still required. No previous pilot rectangle has been silently accepted as a fresh annotation. The detector-source loader and measured matching pass remain to be implemented after source review.

### What should be done in the future
Complete the remaining 156 source annotations, validate all rectangles and overlays, run the confidence sweep, materialize identical D/O crop geometry, execute all F/D/O and fusion state conditions, and publish the localization report and temporal handoff. Then implement the complete temporal ticket.

### Code review instructions
Start at `localization/data.py:prepare`, then `annotations.py:validate_review` and `evaluate.py:match`. Run `workbench/tests/test_localization_contracts.py`. Inspect `various/source-audit-v1/manifest.json` and all original aliases before interpreting the unique-target count.

### Technical details
Dataset: `output/localization-v1/dataset`. Source sheets: `output/localization-v1/source-review`. Tracked draft annotations: `various/source-audit-v1/reviews-in-progress.json`. No GPU job or measured localization run was started in this step.

## Step 4: Complete provisional source annotations and render review overlays

Completed the source-only annotation pass across the 162 unique requested targets. This includes the 144 state frames and 18 additional pilot frames. The draft now contains 158 visible-extent rectangles, one unobservable book, and three ambiguous requested-instance cases. These remain provisional single-reviewer annotations, not a certified localization benchmark.

Added a source-verified overlay renderer and preserved six visually checked sheets in the ticket. All 42 episode sheets were rendered, but only sheets 20, 29, 33, 34, 35, and 40 have completed the overlay inspection pass at this checkpoint. The remaining overlay review precedes measured detector recall.

### Prompt Context
**User prompt (verbatim):** (see Step 1).

**Assistant interpretation:** Continue implementing localization with source evidence, meaningful commits, and a detailed diary before proceeding to the temporal ticket.

**Inferred user intent:** Obtain a reproducible comparison that distinguishes incorrect object localization from insufficient state evidence.

**Commit (code):** `74216dc` — Annotate localization source population and add source-verified review overlays.

### What I did
- Reviewed source sheets through the full 162-target population without detector overlays.
- Recorded visible appliance body and protruding door extents separately for each frame, shrinking boxes where an actor hides an extremity.
- Kept visibility independent of detector vocabulary support and state observability.
- Added `localization/review.py:render_overlays` and the `overlays` CLI command.
- Added tests for exact population coverage, duplicate review rejection, and changed-source rejection.
- Preserved six checked overlay JPGs, the full rendering manifest, and a checkpoint listing precisely which sheets were inspected.

### Why
A successful JSON validation only proves schema and source identity. Overlay inspection is still needed to find inaccurate manual geometry. Multiple visible mugs or plates cannot be assigned to a requested simulator entity from class identity alone.

### What worked
- All 162 draft reviews pass source hash, visibility, and rectangle validation.
- Provisional distribution: 86 visible unique, 72 partially visible unique, one unobservable, three ambiguous instances.
- The renderer produced 42 source-bound review sheets and hashes.
- `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_localization_contracts.py -q`: four tests passed.

### What didn't work
An initial diary lookup used the wrong basename and returned `zsh:1: no matches found: ttmp/2026/09/06/VIDEO-LOCALIZATION-001*/reference/01-diary.md`. Located and read the actual `01-implementation-diary.md` with `rg --files`. No annotation or rendering command failed. Printing remains pending after the previously documented automatic approval rejection; no external print retry was made.

### What I learned
The edge-on TV remains localizable although its screen state cannot be judged. A source frame with two mugs supports class presence but does not necessarily support requested-instance identity. The heavily occluded microwave requires a rectangle over the remaining visible left portion rather than its inferred full body.

### What was tricky to build
Half-open source rectangles must be displayed with their final coordinate minus one to avoid drawing an extra boundary pixel. Population validation runs before rendering, so a missing or duplicate review cannot silently produce an apparently complete gallery. A manifest explicitly says rendering does not certify annotation quality.

### What warrants a second pair of eyes
Manual boxes are approximate and use one reviewer. State-frame annotations use temporal contact-sheet context. Sectional-sofa extents, protruding appliance doors, truncation, and actor occlusion need particular attention in the remaining overlay review. No detector metrics should treat this checkpoint as final ground truth.

### What should be done in the future
Inspect the remaining overlay sheets, correct and freeze annotations, verify detector source identities, run the confidence sweep, and execute F/D/O crop and fusion comparisons. Complete the localization report and then the full temporal implementation.

### Code review instructions
Start with `localization/review.py:render_overlays` and `test_overlay_requires_exact_population_and_unchanged_source`. Inspect the six tracked overlay images and `review-checkpoint.json`. Reproduce the full overlay gallery using the CLI below. Do not mark the source-review task complete until all sheets have been inspected.

### Technical details
Run `PYTHONPATH=workbench/src workbench/.venv/bin/python -m video_workbench.localization overlays --dataset output/localization-v1/dataset --reviews ttmp/2026/09/06/VIDEO-LOCALIZATION-001--requested-object-localization-and-crop-evidence-coverage/various/source-audit-v1/reviews-in-progress.json --out output/localization-v1/overlay-review`.

## Step 5: Freeze reviewed rectangles and measure detector coverage

Inspected all 42 overlay sheets and corrected three source rectangles before running detector comparisons. The final review contains 158 rectangles among 162 targets, with three ambiguous requested instances and one unobservable book left without rectangles. The frozen annotations retain the limitations of approximate visible extents from one reviewer.

Implemented a source-verified detector join and measured the complete confidence sweep. At confidence 0.25, 78 of 156 eligible targets reach IoU 0.5, while 74 have a unique correct binding. Confidence 0.10 increases recall to 123/156 but produces 19 ambiguous class bindings. These results diagnose localization; they do not yet establish improved downstream state recognition.

### Prompt Context
**User prompt (verbatim):** (see Step 1).

**Assistant interpretation:** Finish source review and measured localization evaluation before crop/state comparison and temporal implementation.

**Inferred user intent:** Identify concrete failure sources with source-bound measurements, reproducible artifacts, and visual evidence.

**Commit (code):** `67a5cc2` — Freeze reviewed localization boxes and audit source-verified detector coverage.

### What I did
- Inspected the 36 remaining overlay sheets and rechecked the three corrected sheets.
- Corrected refrigerator top background, an excluded refrigerator door edge, and a partially occluded but still visible microwave door extent.
- Saved `reviews-v1.json`, corrections, a freeze record, and corrected overlay screenshots while preserving the earlier draft.
- Added a detector loader that validates run and producer identities, episode manifests, artifact hashes, source video hashes, frame clocks/dimensions, detection vocabulary, and requested-frame matches.
- Added the `audit` CLI and complete confidence/size/view/apartment/class/occlusion summaries.
- Preserved all 486 matching rows, summaries, and provenance in the ticket.

### Why
Detector comparisons require exact video and frame identity. A processed frame with no detections is a valid negative output; an unprocessed or missing frame is a provenance failure and must not be counted as a detector miss. Best matching recall and uniquely usable binding remain separate measurements.

### What worked
- Frozen review SHA256: `6d45dd67a0c8884783f1a53a472a152b7fe6aab42fdca3b093b9d13e201b2a76`.
- All requested detector sources matched the reviewed population.
- At confidence 0.10: 123/156 localized, 104 uniquely correct, 19 ambiguous bindings.
- At confidence 0.25: 78/156 localized, 74 uniquely correct, four ambiguous bindings.
- At confidence 0.50: 46/156 localized, 45 uniquely correct, one ambiguous binding.
- Visible book and mug targets were missed at all policies. Four unsupported targets remain separate from two unreviewable supported targets.
- `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_localization_contracts.py -q`: five tests passed.

### What didn't work
The initial audit invocation failed with `ValueError: incomplete or changed detector run`. The original detector spec hashes an integer-keyed Ultralytics class map; JSON reload converts those keys to strings, changing sorted serialization order. Restoring integer keys reproduced both the original run ID and producer ID exactly. Added a test with class IDs 2 and 10 to exercise this ordering distinction. The failed audit did not publish a result directory. No print retry was attempted while destination approval remains pending.

### What I learned
Reducing confidence increases both recall and multi-instance ambiguity. On this population, microwave localization falls from 69/96 at confidence 0.10 to 34/96 at 0.25 and 7/96 at 0.50. Aggregate detection presence is insufficient for evaluating requested-object evidence.

### What was tricky to build
Provenance spans several layers: the top-level run lists episode manifest hashes, each episode lists JSONL hashes, each frame has an identity derived from source and clocks, and each detection names a producer and frame. The loader checks each layer before joining requested targets. It restores the original class-map type explicitly rather than dropping the run hash check.

### What warrants a second pair of eyes
Single-reviewer visible-extent boxes differ from amodal detector conventions, particularly for occluded appliances and sectional sofas. The full-population sweep is diagnostic, not permission to tune a production threshold on held-out results. Confidence 0.25 remains the planned D-crop condition for the controlled comparison.

### What should be done in the future
Materialize identically padded D/O crops, encode fixed F/D/O and fusion conditions, evaluate state predictions with full-population and paired denominators, save the comparison gallery, and publish the localization report and temporal handoff. Then implement the complete temporal ticket.

### Code review instructions
Inspect `detector_audit.py:load_detections`, the synthetic source-integrity test, `source-audit-v1/overlay-corrections.json`, and `detector-audit-v1/summary.json`. Missing requested frames must raise; valid processed frames with zero boxes must return an empty list. Check the three corrected overlay screenshots against the before/after rectangles.

### Technical details
Reproduce with `PYTHONPATH=workbench/src workbench/.venv/bin/python -m video_workbench.localization audit --dataset output/localization-v1/dataset --reviews ttmp/2026/09/06/VIDEO-LOCALIZATION-001--requested-object-localization-and-crop-evidence-coverage/various/source-audit-v1/reviews-v1.json --detector output/video-perception/detect-v1 --out output/localization-v1/detector-audit-reproduction`. A new destination is required. IoU threshold is 0.5; confidence policies are 0.10, 0.25, and 0.50; small means visible box area below 1024 pixels.

## Step 6: Materialize D/O crops and encode all fixed image conditions

Materialized source-bound detector and reviewed crops using the same expansion, clipping, size, and interpolation. Detector binding uses exactly one usable requested-class box above confidence 0.25. This reproduces the prior state crop coverage: 46/96 training, 23/24 development, and 0/24 test. Reviewed diagnostic crops exist for every state frame.

Ran the actual fixed community 4-bit image encoder on F, D, and O evidence, and computed normalized F+D and F+O fusion. State labels were not read during selection or encoding. All five arrays contain 144 rows with explicit availability; missing D rows store zero vectors and must become null prediction scores. No state-quality conclusion is drawn at this checkpoint.

### Prompt Context
**User prompt (verbatim):** (see Step 1).

**Assistant interpretation:** Continue the controlled crop/state diagnostic using identical evidence geometry and a fixed encoder.

**Inferred user intent:** Determine whether better object localization enables better state predictions while preserving missing production evidence.

**Commit (code):** `6e31c68` — Materialize controlled localization crops and encode fixed image conditions.

### What I did
- Added `localization/crops.py:prepare` with frozen crop policy and source/producer identities.
- Reused `perception.contracts.expand` for 25-percent expansion and clipping; both D and O use 320-by-240 PIL bicubic rasterization.
- Kept low-resolution filtering on expanded extent, matching the existing production policy; multiple usable class candidates remain ambiguous.
- Added `localization/features.py:encode` with F, D, O, FD, and FO arrays, masks, encoder identity, source manifest hash, and per-condition producer spaces.
- Ran local MLX inference with existing weights and offline model settings; preserved metadata and independent feature checks.
- Saved and inspected a six-row source/detector/oracle contact sheet. It includes repeated initial frames as a checkpoint, not six independent selected examples.

### Why
The changed experimental factor is object geometry. Oracle crops must be identified as diagnostic, and missing D crops must remain visible in full-population denominators. Fusions use full-frame fallback when a crop is unavailable, rather than pretending a missing crop was inferred.

### What worked
- D state availability: 69/144; O state availability: 144/144.
- Five feature arrays have shape `[144,2048]`; maximum available-vector norm error is approximately 1.2e-7.
- All unavailable D vectors are zero and have `available=false`.
- FD equals F exactly wherever D is unavailable.
- Actual feature producer: `ab37c9127597993070b7183dc756b44c30f2df1852749b04d85dce10e931fa8b`.
- Six localization tests pass, including equal D/O raster hashes for identical geometry and explicit multi-instance ambiguity.

### What didn't work
A speculative model directory lookup returned `ls: output/video-workbench/models: No such file or directory`. The existing model is `output/models/qwen3-vl-embedding-2b-4bit`; no download or environment change was needed. No crop or inference failure occurred. External printing remains paused after the earlier automatic approval rejection.

### What I learned
The independent crop implementation exactly reproduces the production state availability counts, supporting the interpretation that missing held-out crops arise before state classification. The oracle crop enlarges the held-out appliance but still includes foreground bottles and limited views; localization alone does not guarantee observable state.

### What was tricky to build
The production binder filters low-resolution expanded rectangles before selecting a unique candidate. Using best-IoU selection or binding before the usability check would implement a different D condition. Feature extraction filters the shared localization inventory to state aliases without importing reviewed state labels.

### What warrants a second pair of eyes
The feature extraction API accepts a crop manifest, so the evaluator must verify its hash and exact state-alias order before joining labels. Missing numerical storage is not an inference output; the observation writer must emit null raw score and probability for missing D evidence. F+D has a larger pixel budget than F, and oracle conditions are unavailable in production.

### What should be done in the future
Fit text-margin and ridge-head methods with training/development-only calibration, emit full-population and paired metrics, preserve null missing predictions and evidence availability, and produce a fuller nonduplicated comparison gallery and report. Complete temporal implementation after localization handoff.

### Code review instructions
Inspect `crops.py:prepare` and `features.py:encode`, then `test_crop_policy_keeps_ambiguity_and_matches_oracle_raster`. Review `various/crop-comparison-v1/feature-validation.json` and the contact sheet. Actual arrays remain at `output/localization-v1/features-v1/features.npz`; metadata records their hash.

### Technical details
Crop directory: `output/localization-v1/crops-v1`. Feature directory: `output/localization-v1/features-v1`. Runtime: `workbench/.venv` with `PYTHONPATH=workbench/src HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`. GPU execution session 95629 completed successfully. Model: `output/models/qwen3-vl-embedding-2b-4bit`. No native-video acceptance claim is made for this image-only diagnostic.

## Step 7: Evaluate state quality and preserve missing inference

Ran both text-margin and ridge-head state methods across F, D, O, FD, and FO. Heads fit available known training rows; calibration and abstention use available known development rows. Labels join only after feature extraction, through verified state aliases and exact source clocks. The evaluator publishes all 1,440 observations, including unavailable detector evidence.

The reviewed-crop linear head gets 16/17 known test states correct, compared with 10/17 for the full-frame head. This is an exploratory oracle-assisted result on previously inspected scenes. All evidence-bearing methods still answer on all seven unknown test frames. Detector-only methods have no test evidence, and the paired F/D/O test denominator is zero with null metrics.

### Prompt Context
**User prompt (verbatim):** (see Step 1).

**Assistant interpretation:** Complete the measured state comparison while preserving source identity, split discipline, unknowns, and missing evidence.

**Inferred user intent:** Determine how much localization helps state recognition and whether that improvement is usable downstream.

**Commit (code):** `b2a89e9` — Evaluate controlled crop state baselines with explicit missing evidence.

### What I did
- Added `localization/experiment.py:run` with feature/artifact verification and exact state-alias joins.
- Reused the existing ridge, margin, calibration, and policy implementations.
- Evaluated ten condition/method combinations over train, development, and test.
- Reported full-population metrics and paired F/D/O subsets with explicit zero denominator.
- Emitted validated StateObservation records with evidence IDs, producer identity, oracle flags, and offline source-horizon availability.
- Preserved raw results, fitted parameters, observations, completion manifest, and validation counts in the ticket.

### Why
Conditional metrics can conceal complete localization failure. Missing D rows must remain in the experiment with null score/probability and unknown value. Oracle crop improvements cannot be presented as production detector coverage or proof of reliable abstention.

### What worked
- All ten baselines completed using existing encoded features; no new model download or inference was needed.
- Test linear-head known correct counts: F 10/17, D 0/17 with no evidence, O 16/17, FD 3/17, FO 16/17.
- All evidence-bearing text-margin conditions predict the 15 known closed frames correctly and miss both known open frames.
- All evidence-bearing methods answer on seven unknown test frames; this remains a visibility/abstention failure.
- Validated all 1,440 StateObservation records, including 150 missing-evidence records with paired null scores.
- All paired test metrics are null with n=0. Six localization tests still pass.

### What didn't work
No evaluation command failed. The FD linear head performs poorly on test (14/17 known errors), although FD test features equal F because every D crop is missing. Its fitted head/calibration differ because training and development contain a different mix of cropped and fallback evidence. This measured failure is retained. Printing remains pending after the earlier automatic approval rejection.

### What I learned
Correct object geometry helps the learned state head in this small diagnostic, but does not fix unknown false certainty. Full-frame fallback preserves evidence availability without preserving the distribution used to train a fusion head. The comparison therefore needs both coverage and state risk.

### What was tricky to build
Localization IDs differ from the original state sample IDs. The evaluator follows state aliases, verifies source and entity identity and timestamps, and reorders labels to the feature rows. It verifies each condition space against the feature producer before scoring. Missing inference cites the requested source only for traceability and is marked unavailable; it does not claim that a crop was seen.

### What warrants a second pair of eyes
The full label file hash identifies the evaluation revision, but fitting uses only explicit training/development row lists. The test partition was inspected previously and has only two known open examples. Availability is an offline source horizon, not measured execution latency. O/FO observations must never be mixed into a production temporal stream without retaining their oracle flag.

### What should be done in the future
Publish the detailed localization failure analysis, a nonduplicated outcome gallery, and a measured improvement plan. Validate the temporal handoff and complete the temporal ticket's dense feature, decoder, neural model, and durable-memory implementation.

### Code review instructions
Start at `localization/experiment.py:run`. Verify row joins and masks before reading metrics. Inspect `various/state-comparison-v1/results.json` for fitted row IDs and test confusion counts, and `observations.jsonl` for null missing D scores and oracle flags. The independent validation record counts 1,440 validated observations and 150 missing rows.

### Technical details
Output: `output/localization-v1/state-comparison-v1`. Inputs: state `samples-v2.json` and `labels-v2.json`, `output/localization-v1/crops-v1/manifest.json`, and `output/localization-v1/features-v1`. Run through `PYTHONPATH=workbench/src workbench/.venv/bin/python` and call `localization.experiment.run` with a new destination. Ridge strength remains the existing 0.01 default; no held-out threshold selection was performed.
