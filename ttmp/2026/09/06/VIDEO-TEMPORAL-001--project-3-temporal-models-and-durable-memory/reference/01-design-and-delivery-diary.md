---
Title: Design and delivery diary
Ticket: VIDEO-TEMPORAL-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/design-doc/01-intern-analysis-design-and-implementation-guide.md
      Note: Authored project guide
    - Path: repo://ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/scripts/01-pdf-header.tex
      Note: Per-ticket PDF header
    - Path: repo://ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/tasks.md
      Note: Phased implementation breakdown
    - Path: repo://ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/various/pdf-validation.json
      Note: Visual review and artifact hashes
    - Path: repo://ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/various/remarkable-upload.json
      Note: Successful individual delivery
    - Path: repo://workbench/src/video_workbench/temporal/benchmark.py
      Note: Train-only baseline and development selection (0d47851)
    - Path: repo://workbench/src/video_workbench/temporal/data.py
      Note: Sequence masks clocks and trailing windows
    - Path: repo://workbench/src/video_workbench/temporal/duration.py
      Note: Offline duration decoder
    - Path: repo://workbench/src/video_workbench/temporal/encode.py
      Note: Actual pooled extraction and source audit (0d47851)
    - Path: repo://workbench/src/video_workbench/temporal/hmm.py
      Note: Classical scored inference and prefix filter
    - Path: repo://workbench/src/video_workbench/temporal/hysteresis.py
      Note: Timestamp persistence and gap reset
    - Path: repo://workbench/src/video_workbench/temporal/linear.py
      Note: Independent frozen-feature ridge baseline
    - Path: repo://workbench/src/video_workbench/temporal/prepare.py
      Note: Dense model inputs and weak labels (0d47851)
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T13:13:51.534537-04:00
WhatFor: ""
WhenToUse: ""
---






# Diary

## Goal

Record evidence, design decisions, implementation-task decomposition, and reMarkable delivery for VIDEO-TEMPORAL-001. This ticket is a design deliverable now; application implementation remains open.

## Step 1: Establish the project boundary

Created this child of COSMOS-VIDEO-001 and inspected the existing generator, validated corpus, teaching labs, and umbrella guide. The project scope is: Compare temporal decoders and store availability-aware facts without inventing missing steps. Dependencies are VIDEO-SEARCH-001, VIDEO-STATE-001.

### Prompt Context

**User prompt (verbatim):** "Ok, create the tickets, and Create  a detailed analysis / design / implementation guide that is for a new intern, explaining all the parts of the system needed to understand what it is, with prose paragraphs and bullet point sand pseudocode and diagrams and api references and file references. It should be very clear and technical. Store in the ticket and the nupload to remarkable."

**User prompt (verbatim):** "for each"

**User prompt (verbatim):** "use virtual home instead of habitat btw"

**Assistant interpretation:** Create a separate technical intern guide and executable task breakdown for every project; use VirtualHome for synthetic data.

**Inferred user intent:** Make each project independently understandable, reviewable, and ready for an intern to implement.

### What I did
- Created ticket, guide document, diary, and explicit dependency boundary with docmgr.
- Inspected `src/virtualhome_corpus/core.py`, `runner.py`, the checked configuration, and the corpus inventory.

### Why
- The umbrella checklist is too broad to assign or verify without project-level contracts and acceptance gates.

### What worked
- Existing 24-episode corpus and teaching code provide concrete inputs and API examples.

### What didn't work
- No ticket-creation failure occurred. Runtime APIs are references to verify at implementation time, not measured local model support.

### What I learned
- Current corpus timing is weak supervision; endpoint simulator truth must not become certified pixel labels.

### What was tricky to build
- Avoiding circular dependencies requires shared schema ownership and oracle fixtures before model integration.

### What warrants a second pair of eyes
- Scope boundaries and whether acceptance gates depend on evidence the present corpus cannot provide.

### What should be done in the future
- Complete the project-specific guide, validate its examples and PDF, upload it, then implement the open tasks in phase order.

### Code review instructions
- Read the guide alongside the umbrella corpus report; distinguish existing files from proposed modules.

### Technical details
- Parent: COSMOS-VIDEO-001.
- Simulator selection: VirtualHome, explicitly requested by the user.

## Step 2: Write the intern guide and implementation phases

Wrote the project-specific analysis, proposed contracts, data flow, decision records, implementation phases, test strategy, and review exercise. The guide explains compare temporal decoders and store availability-aware facts without inventing missing steps. It distinguishes the working VirtualHome generator from future workbench modules and keeps the current corpus's label limits explicit.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make this project independently understandable and implementable by a new intern.

**Inferred user intent:** Receive a technical design with enough detail to assign and review concrete work.

### What I did
- Authored the dedicated guide and phased task list in this ticket.
- Added direct local file references and linked dependency tickets.
- Validated code-fence balance, JSON examples, Python pseudocode syntax, SQL schema where present, and existing local links using umbrella `scripts/14-validate-project-guides.py`.
- Reviewed shared feature identity, time, evidence, and split contracts across all eight guides.

### Why
- Separate projects need compatible contracts and explicit data-quality gates to avoid duplicate implementations and misleading evaluation.

### What worked
- Every guide passed structural/example/link validation. The checks validate documentation syntax and references, not the future application.
- Existing file references point to real generator/config/playbook files; proposed workbench paths are clearly identified.

### What didn't work
- The web fetch for a guessed MLX-VLM embedding directory returned `Cache miss`. The design uses the verified maintainer README and requires inspection of the pinned installed entry point instead of inventing an API.
- No documentation parser or local-link validation failure occurred.

### What I learned
- Runtime support listings establish candidates, not measured local video behavior.
- Calibration and reviewed visibility are dependencies for stronger temporal claims, even when corpus media integrity passes.

### What was tricky to build
- A verifier's evidence cutoff and result availability are different clocks. The rules design preserves the cutoff but reevaluates at the later result time; it does not backdate new proposals.
- Multiple projects share schemas. The ticket map assigns ownership and allows oracle fixtures before full model integration.

### What warrants a second pair of eyes
- The project-specific acceptance gates and any claim relying on weak simulator timing.
- Vendor signatures and conversion fidelity must be checked again when actual runtimes are installed.

### What should be done in the future
- Render and inspect this guide, upload its own reMarkable edition, then execute the unchecked implementation phases.

### Code review instructions
- Read this ticket's guide and tasks, then follow direct dependency links.
- Run the umbrella guide-validation script to check examples and file references after editing.

### Technical details
- Guide: `design-doc/01-intern-analysis-design-and-implementation-guide.md`.
- Simulator: VirtualHome only for the active synthetic-data plan.

## Step 3: Review and deliver the reMarkable edition

Rendered this guide as a six-page PDF with a dedicated contents page, readable Helvetica/Menlo type, and unbroken code/diagram blocks. Inspected all six pages via contact sheets and a selected contract/code page at full raster size. The dry run and real upload both succeeded; the receipt is stored in this ticket.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Complete this ticket's independent PDF delivery after technical and visual review.

**Inferred user intent:** Read the implementation guide on reMarkable and retain reviewable source and delivery evidence locally.

**Commit (design source):** `edd3d34` — `docs(vision): split roadmap into eight intern-ready project tickets`.

### What I did
- Ran the shared `scripts/15-render-upload-project-guides.py render` and rasterized every page with `scripts/16-review-project-pdfs.py`.
- Verified JSON/Python/SQL documentation examples and local references; docmgr doctor passed.
- Reviewed all six pages and the larger API/code/diagram sample; recorded source and PDF hashes.
- Ran a per-ticket dry run, then uploaded this guide using the same source and renderer configuration.
- Recorded `OK: uploaded VIDEO-TEMPORAL-001_Intern_Guide.pdf -> /ai/2026/09/06/VIDEO-TEMPORAL-001`.

### Why
- Successful PDF compilation alone cannot establish readability, and a design is not delivered until the requested upload succeeds.

### What worked
- Six pages with legible text, contents, headers, page numbers, code, and diagrams; no visible clipping or overlap.
- Upload returned a positive success receipt. No redundant cloud listing was performed, following the reMarkable upload skill.

### What didn't work
- Generated changelogs had trailing blank lines reported by `git diff --cached --check`; these were removed in final bookkeeping.
- Local `pypdf`, `pdfplumber`, and `fitz` modules were absent. Existing Ghostscript provided page rasterization, text extraction, and ink bounds without installing packages.
- No rendering or upload failure occurred.

### What I learned
- The shared proven Pandoc/XeLaTeX configuration produced a consistent six-page edition for each project while preserving project-specific content.

### What was tricky to build
- PDF source hashes were captured after docmgr relations and checked again before upload; later task/diary updates do not alter the reviewed guide source.
- Upload regenerates from the reviewed Markdown and renderer settings; the stored PDF hash identifies the inspected local artifact, not a downloaded remote-byte verification.

### What warrants a second pair of eyes
- Future implementation must validate the proposed contracts and candidate runtimes; documentation checks do not establish model behavior.

### What should be done in the future
- Begin the open implementation phases in `tasks.md` when this project is scheduled.

### Code review instructions
- Compare this guide's source hash in `various/pdf-validation.json` and `various/remarkable-upload.json`.
- Reproduce with the shared render script and `--ticket VIDEO-TEMPORAL-001`; repeat review after content/layout changes.

### Technical details
- Remote directory: `/ai/2026/09/06/VIDEO-TEMPORAL-001`.
- Local inspected PDF: `/Users/manuel/code/wesen/2026-09-06--vision/output/pdf/project-guides/VIDEO-TEMPORAL-001/VIDEO-TEMPORAL-001_Intern_Guide.pdf`.
- Six-page visual review and individual dry-run/upload receipts are stored under `various/`.

## Step 4: Implement sequence clocks, masks, and numerical oracle baseline

Started temporal implementation after completing the localization diagnostic. Added timestamped feature sequence validation, independent evidence-validity and label masks, source-horizon availability, gap-preserving interval mapping, and dense trailing-window planning on native timestamps. These contracts do not imply that real dense video features have already been extracted.

Added numerical normal, omission, repetition, and gap fixtures plus an independent multiclass ridge baseline. The baseline preserves the known fixture errors and leaves missing features unclassified. This is a numerical software check, explicitly separate from representation quality on rendered video.

### Prompt Context
**User prompt (verbatim):** "Then implement all 3 tickets, commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill), Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Implement the temporal project in addition to the completed action and localization work, retaining evidence and diary checkpoints.

**Inferred user intent:** Use temporal history and durable memory without fabricating missing procedural events or leaking future information.

**Commit (code):** `f7f5f43` — Add temporal sequence clocks masks and oracle linear baseline.

### What I did
- Read the temporal design, tasks, prior delivery diary, and upstream sparse handoff context.
- Added Sequence validation for shape, integer clocks, evidence, finite features, target ranges, and Boolean masks.
- Added half-open trailing-window planning and segment-to-source coverage mapping that retains gaps.
- Added numerical oracle fixtures with irregular durations, omitted CLOSE, repeated OPEN, and a missing-feature interval.
- Added independent ridge fitting and prediction with feature-space validation and missing predictions represented by -1 and NaN scores internally.
- Saved the numerical baseline report in `various/oracle-linear-v1.json`.

### Why
Validity describes whether evidence exists; label masks describe whether supervision is allowed. Combining them prematurely can train missing evidence as background. Segment bounds also must not imply continuous coverage across missing observations.

### What worked
- Four temporal tests pass.
- Oracle known valid accuracy: normal 20/20, omission 16/16, repetition 28/28, gap 16/16.
- The omission contains no invented CLOSE prediction, repetition retains three OPEN runs, and gap samples remain unclassified.
- Irregular native timestamps map to trailing windows without including a frame at the half-open end.
- Delayed availability prevents a feature from appearing in an earlier as-of selection.

### What didn't work
An exploratory lookup of `workbench/src/video_workbench/actions/temporal.py` returned `No such file or directory`; the actual exported handoff exists under `output/action-benchmark-v1/temporal-handoff-v2`. No temporal test or oracle run failed. Printing remains paused because the external Almanach request was previously rejected by automatic approval review; no new external request was made.

### What I learned
Sparse upstream state and action exports are useful provenance examples but cannot substitute for the dense sequence benchmark. Numerical oracle accuracy only demonstrates the controlled fixture, not video understanding.

### What was tricky to build
A feature segment has an overall time span and potentially disjoint evidence coverage. The mapper returns both instead of filling gaps. Availability is constrained to be no earlier than the feature end; label supervision remains an independent mask combined with validity only for loss.

### What warrants a second pair of eyes
The oracle feature vocabulary reserves OTHER but the numerical classifier fits only the three observed event classes. Real corpus supervision needs an explicit class inventory and uncertain-boundary mask. Streaming consumers must not feed unavailable future features merely because a head itself is causal.

### What should be done in the future
Extract actual dense trailing features, map weak interiors without supervising uncertain boundaries, and evaluate the real linear baseline. Then implement classical decoders, causal TCN training and leakage tests, and append-only memory. T1 remains open until actual source mapping and video measurements are complete.

### Code review instructions
Inspect `temporal/data.py:Sequence` and `trailing_grid`, then `fixtures.py` and `linear.py`. Run `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_temporal_data.py -q`. Check the saved report's irregular timestamps, missing masks, and omission/repetition predictions.

### Technical details
Numerical training seed: 1; oracle evaluation seed: 2. Ridge strength: 0.01. Missing feature storage is zero with validity false. Internal missing predictions are -1 with NaN scores; durable observation serialization will require explicit nulls rather than nonfinite JSON. No GPU job was started in this step.

## Step 5: Extract dense video features and measure the weak-label baseline

Completed the actual dense pooled-image run on 48 rendered VirtualHome-AIST episodes. The dataset contains 792 trailing windows with separate model inputs and weak program-interior supervision. Every episode passed the encoder's native timestamp audit before publication. This completes T1's real-data baseline alongside the previous numerical fixtures.

The development-selected ridge model has 75.97% weak-label test accuracy and 21.16% macro recall, below the 80.84% accuracy of an always-WALK classifier. These measurements establish an imbalanced baseline; they do not demonstrate reviewed dense action recognition. Saved and visually reviewed the per-episode weak-label timeline for the future report.

### Prompt Context
**User prompt (verbatim):** (see Step 4)

**Assistant interpretation:** Continue all three implementations with concrete experiments, evidence, and diary checkpoints.

**Inferred user intent:** Determine whether temporal models improve discrimination while preserving source provenance and procedural errors.

**Commit (code):** `0d47851` — Build dense temporal features and measure weak-label linear baseline.

### What I did
- Added `temporal/prepare.py` to create half-open two-second windows at 0.5-second stride, sampled at 2 fps, with labels joined only after encoding.
- Added `temporal/encode.py` and ran the existing four-bit image encoder on unique sampled frames per episode; pooled and normalized each trailing window.
- Checked video SHA, native PTS, raw PTS, time base, origin, and source horizon for every encoded window.
- Added `temporal/benchmark.py`: train-only ridge fitting, development macro-recall selection among 0.01/0.1/1.0, and separate test evaluation.
- Preserved manifests, exact window/label tables, fitted model and predictions, and the reviewed `various/dense-plan-v1/weak-grid.png`.
- Added a test showing that changing masked labels/features cannot change the fitted independent baseline.

### Why
Sparse upstream exports cannot support dense temporal experiments. Separating inputs from supervision prevents weak program labels entering feature production, and macro recall exposes majority-class accuracy that conceals failed action discrimination.

### What worked
- The extraction artifact was complete on resumption; all 48 source-audit entries verified native mapping.
- Five temporal tests passed with `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_temporal_data.py -q`.
- Supervised windows: train 157, development 176, test 308. All ten classes occur in each partition.
- Selected ridge: 0.01. Train accuracy/macro recall 100%/100%; development 78.98%/32.58%; test 75.97%/21.16%.
- Viewed the saved timeline: all 48 rows, the class legend, unlabeled boundary ticks, and the seconds axis are readable.

### What didn't work
Polling the prior GPU session returned `write_stdin failed: Unknown process id 54735`. The completed feature manifest and NPZ existed; their hashes and row identities passed the baseline loader, so the job was not restarted. No extraction or baseline failure was inferred from the expired handle. Printing remains paused after the previously recorded automatic approval rejection of external Almanach egress; no new print request was sent.

### What I learned
WALK occupies 249/308 supervised test windows. Six classes have zero test recall. A temporal decoder can increase apparent accuracy by suppressing uncommon events, so subsequent comparisons must retain per-class metrics and separate numerical omission/repetition tests.

### What was tricky to build
The supervision target is the latest actual sampled source frame, not the nominal trailing-window endpoint. An endpoint can fall in an uncertain boundary or lack a rendered frame. Only a unique weak action at the sampled timestamp receives a label; uncertain boundaries stay masked. Offline availability records the source horizon and excludes real inference latency.

### What warrants a second pair of eyes
These are overlapping pooled-image features with weak program interiors. They are neither repaired native-video features nor reviewed boundary ground truth. Review lineage split enforcement, input/label separation, and timestamp mapping before interpreting future temporal results. Perfect training accuracy with 157 observations and 2048 feature dimensions is not evidence of generalization.

### What should be done in the future
Implement T2 classical inference and duration models with exhaustive numerical checks, then T3 causal TCN comparisons and T4 append-only memory. Keep constrained versus unconstrained behavior and offline versus causal evidence separate.

### Code review instructions
Start with `prepare.prepare`, `encode.encode`, and `benchmark.run`. Inspect the frozen `various/dense-plan-v1/validation.json`, feature manifest, and linear results. Reproduce the baseline with a fresh destination using `benchmark.run('output/temporal-v1/dataset', 'output/temporal-v1/pooled-features', NEW_DESTINATION)` under `PYTHONPATH=workbench/src`. Run the five temporal tests above.

### Technical details
- Feature matrix: 792 by 2048; feature space `92b2a1f338385a4a499cadc27b0b41c3a8d9074e4a7aab53bfa975add80c3f19`.
- Actual cache: `output/temporal-v1/pooled-features`; measured baseline: `output/temporal-v1/linear-v1`.
- Model: `output/models/qwen3-vl-embedding-2b-4bit`, existing pooled-image environment. The repaired native-video runtime remains separate.
- Source horizon is offline availability; production latency must be added by streaming producers.

## Step 6: Verify classical decoders and expose constrained-path fabrication

Adapted the ticket's teaching HMM and HSMM functions into workbench modules, added normalized prefix filtering and timestamp-based categorical hysteresis, and checked the dynamic programs against exhaustive tiny path enumeration. The implementation explicitly distinguishes prefix-causal filtering from full-sequence smoothing and decoding.

A saved numerical comparison demonstrates why the procedure graph must remain an ablation: its OPEN-WALK-CLOSE cycle inserts CLOSE into an omission fixture. Unconstrained scored decoders preserve the omission and all repeated OPEN events. These checks establish numerical behavior, not real-video temporal performance; T2 remains open for that comparison and fuller metrics.

### Prompt Context
**User prompt (verbatim):** (see Step 4)

**Assistant interpretation:** Implement temporal models with evidence that they preserve procedural errors rather than enforcing a normal sequence.

**Inferred user intent:** Build trustworthy temporal inputs for later rule evaluation and memory.

**Commit (code):** `cf153c1` — Add classical temporal decoders and exhaustive oracle checks.

### What I did
- Read the complete `sources/procedural_video_labs/sequence_lab.py` in COSMOS-VIDEO-001.
- Adapted log-space forward, smoothing, Viterbi and explicit-duration Viterbi, retaining finite/-infinity validation and completed-final-segment semantics.
- Added normalized prefix filtering with impossible-prefix rejection.
- Added timestamp hysteresis: startup persistence, delayed switches, cancellation on missing evidence, and restart after excessive sample gaps.
- Added exhaustive HMM partition/marginal/best-path and HSMM segmentation checks plus filtering future-perturbation and irregular-time persistence tests.
- Saved seven-method numerical prediction traces in `various/classical-oracle-v1.json` via `scripts/03-classical-oracle.py`.

### Why
The decoder's transition graph can manufacture a missing procedural step. An unconstrained observation stream must remain available for rules to compare against expected procedures. Explicit duration scores count samples and cannot be reported directly as seconds on irregular grids.

### What worked
- Nine temporal tests passed in 0.06 seconds across data and classical modules.
- HMM partition sum, every smoothed marginal, and optimal path match all enumerated four-step two-state paths.
- HSMM optimal segmentation and score match exhaustive five-step two-state sequences with maximum duration three.
- Unconstrained linear/filter/smooth/Viterbi/HSMM classify every valid numerical fixture sample correctly; missing intervals remain -1 because inference restarts on valid runs.
- Constrained omission accuracy is 15/16 but omission preservation fails: an invented CLOSE appears. The unconstrained omission remains 16/16 without CLOSE.
- Hysteresis delays transitions: normal 14/20, omission 11/16, repetition 19/28, gap 12/16. It retains repeated OPEN runs but cannot be described as cost-free denoising.

### What didn't work
The staged whitespace check reported `workbench/src/video_workbench/temporal/duration.py:64: new blank line at EOF.` The initial local commit occurred despite that check; removed the trailing blank line, confirmed a clean staged check, and amended the just-created commit before recording its final hash. No numerical test failed. Printing remains paused under the earlier external-egress approval rejection.

### What I learned
High frame accuracy can coexist with a procedurally false event: only one changed sample was needed to fabricate CLOSE. The numerical unconstrained comparison uses flat transition/duration potentials as a controlled observation-preservation check; it does not test whether learned temporal priors improve video predictions.

### What was tricky to build
Missing evidence cannot silently become a model prediction. The numerical adapter splits valid runs and restarts each decoder, retaining -1 in gaps. The HSMM excludes same-state adjacent segments so a duration cap cannot be bypassed by repeatedly assigning the same state. Filtering normalizes each prefix independently and rejects impossible prefixes instead of producing NaNs.

### What warrants a second pair of eyes
The current emissions are ridge discriminative scores, not calibrated generative likelihoods. Whole-run Viterbi, smoothing, and HSMM are offline. HSMM has a completed-final-segment assumption. Production wrappers still need explicit availability metadata, source-time mapping of output segments, and per-method capability reporting.

### What should be done in the future
Finish T2 with development-selected real-feature comparisons, segment/edit/short-action metrics on numerical truth, and a reviewed figure of omission/repetition outputs. Keep exact-boundary metrics disabled on weak corpus labels. Continue causal learned heads and durable memory afterward.

### Code review instructions
Read `hmm.py`, `duration.py`, `hysteresis.py`, then `test_temporal_classical.py`. Run `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_temporal_classical.py workbench/tests/test_temporal_data.py -q`. Reproduce the numerical report with the ticket's `scripts/03-classical-oracle.py` under the same PYTHONPATH.

### Technical details
Numerical fixture seeds remain train 1 and evaluation 2; three observed event classes. Unconstrained transition and initial potentials are zero. The constrained matrix permits self-loops and the 0→1→2→0 cycle only. HSMM duration potentials are flat through 32 samples. Hysteresis persistence is 300000 microseconds with a 500000-microsecond maximum gap. Startup requires persistence; missing labels cancel history.

## Step 7: Complete the measured classical comparison with replay metadata

Completed T2 on the frozen dense video features. The benchmark selects temporal settings on development macro recall and evaluates the selected models on test episodes. It records separate causal and offline capabilities, per-output dependency evidence, source-horizon availability, per-class results, and complete candidate measurements.

Added exact numerical segment F1, edit, and short-action metrics while keeping those metrics disabled for weak video boundaries. The saved and visually reviewed trace figure makes the fabricated CLOSE, repeated OPEN events, and missing interval explicit. Classical temporal context did not establish a useful improvement on this corpus.

### Prompt Context
**User prompt (verbatim):** (see Step 4)

**Assistant interpretation:** Complete the temporal comparison with measured outcomes and enough provenance for the later memory layer.

**Inferred user intent:** Evaluate real discrimination and error preservation instead of assuming smoothing is beneficial.

**Commit (code):** `3be2278` — Measure classical temporal models with availability and segment evidence.

### What I did
- Extracted a reusable hash-checked sequence loader, rejecting duplicate identities and closing the feature archive after reading.
- Added training-only transition counts without bridges through masked cells, development selection, and actual six-method train/development/test evaluation.
- Added per-output dependencies and availability for prefix versus offline inference, with missing runs unclassified.
- Implemented one-to-one segment matching, normalized edit score, and declared short-action recall; generated numerical reports at IoU 0.1/0.25/0.5.
- Wrote `reference/02-measured-classical-temporal-comparison.md` and saved the reviewed `various/classical-comparison-v2/oracle-traces.png`.
- Marked the three T2 tasks complete after numerical checks and actual video comparison.

### Why
An offline decoder must cite future inputs and defer availability. Weak boundaries cannot support exact segment quality claims. Development-selected zero temporal strength is a valid negative result and must remain in the candidate set.

### What worked
- Eleven data/classical tests passed, including exhaustive paths, prefix future perturbation, delayed evidence, dependency sets, gaps, and one-to-one segment matching.
- The original linear result reproduced exactly after the loader refactor.
- Test accuracy/macro recall: linear 75.97%/21.16%; selected hysteresis/filter/Viterbi identical; smoother 69.48%/21.31%; HSMM 68.83%/18.35%.
- The figure was opened at generated resolution and clearly shows the invented CLOSE in the constrained omission, three distinct OPEN events in repetition, and white missing intervals.
- Full per-episode predictions, candidates, runtime measurements, and producer hashes are preserved in the ticket evidence.

### What didn't work
No test or measured run failed. The first actual comparison output lacked explicit dependency-evidence arrays; added them and reran into fresh `classical-v2`, retaining v1 as intermediate evidence. Printing remains paused after the previously recorded automatic approval rejection for external Almanach egress.

### What I learned
Development selection chose zero persistence for hysteresis and zero temporal strength for filtering/Viterbi. The smoother's tiny macro-recall increase comes with lower accuracy; the HSMM loses on both. These weak-label measurements give no basis to prefer temporal complexity yet.

### What was tricky to build
Feature support intervals overlap, but decision-grid cells used for numerical segment metrics must be nonoverlapping. The adapter explicitly describes its output cells as grid support rather than reviewed action boundaries. Filter outputs depend on available prefixes; offline outputs depend on entire valid runs. Dependency IDs and availability now express that distinction, and missing runs restart inference.

### What warrants a second pair of eyes
Source-horizon availability still excludes actual compute/transport latency. HSMM duration preferences are scored sample-count ablations, not learned reviewed action durations. The numerical segment matcher is temporal-order greedy, not global assignment; its policy and one-to-one behavior are explicit. The within-scene weak corpus remains unsuitable for generalization or significance claims.

### What should be done in the future
Implement and train the causal TCN with seed/checkpoint metadata and full feature-availability tests, then the append-only fact store and rule handoff. Preserve negative classical results as the baseline.

### Code review instructions
Read `temporal/classical.py`, `classical_benchmark.py`, and `metrics.py`, then the new measured report. Run `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_temporal_classical.py workbench/tests/test_temporal_data.py -q`. Reproduce the actual benchmark with the report's inputs and a fresh output directory, then run `scripts/04-classical-evidence.py` to rebuild the numerical figure and metrics.

### Technical details
Transition strengths: 0/0.25/1; persistence: 0/500000/1000000 microseconds; HSMM mean preferences: 2/4/8 samples. Selection uses development macro recall and first-candidate tie breaking. Short-action threshold is 1500000 microseconds. Actual accepted comparison: `output/temporal-v1/classical-v2`; tracked copies under `various/classical-comparison-v2`. No exact-boundary metrics were computed on the weak video labels.

## Step 8: Train causal heads and verify actual checkpoint streaming

Completed T3 with six actual CPU training runs on the frozen 792-window feature matrix, development-only checkpoint/architecture selection, three selected seed evaluations, and checkpoint hashes. Added a bounded-history streaming wrapper and an availability-ordered sequence adapter, then checked actual trained weights for future leakage and one-cell/full-sequence equivalence.

The selected TCN mean test macro recall is 18.63%, below the linear baseline's 21.16%. This is a completed negative experiment, not a claim that temporal learning improved action recognition. Saved and visually reviewed the seed figure and wrote a technical report including architecture, training, memory, latency, and clock limitations.

### Prompt Context
**User prompt (verbatim):** (see Step 4)

**Assistant interpretation:** Implement, train, and measure causal learned temporal heads while retaining evidence and detailed checkpoints.

**Inferred user intent:** Test learned temporal context rigorously before using its outputs in procedural memory and rules.

**Commit (code):** `fd405d3` — Train causal TCN seeds and verify bounded-history streaming.

### What I did
- Read the complete imported `neural_lab.py` and adapted its two-stage causal residual network into `temporal/tcn.py`.
- Added train-only normalization buffers, independent validity/label masking, class-weighted loss, finite-history chunk prediction, and ordered feature-availability buffering.
- Implemented the `python -m video_workbench.temporal.train` CLI with 80-epoch Adam training, seeds 7/17/27, one-/two-block candidates, development checkpoint selection, and saved inference checkpoints.
- Trained all six candidates on CPU in PyTorch 2.14.0 with two threads and deterministic algorithms; selected one block per stage by mean development macro recall.
- Verified trained test outputs against single-cell streaming and future perturbation, then measured head-only streaming latency.
- Saved `various/tcn-v1` results, latency metadata, and reviewed seed figure; wrote `reference/03-causal-tcn-training-and-streaming-results.md`.
- Marked the three T3 tasks complete.

### Why
A causal architecture alone does not guarantee causal feature availability. Streaming requires finite context and explicit handling of delayed inputs. Multiple seeds and development-only selection expose whether a promising development result transfers to held-out episodes.

### What worked
- Fourteen temporal tests passed across data, classical, and TCN modules.
- Actual selected test macro recall: seed 7 17.82%, seed 17 19.72%, seed 27 18.35%; mean 18.63%, population seed standard deviation 0.80 percentage points.
- Future perturbation changed earlier trained logits by zero. Maximum full-versus-streamed logit discrepancy was 1.15e-5, below the declared 1e-4 trained-check tolerance.
- Arbitrary chunk tests cover a two-block/two-stage receptive field of 13; selected training architecture has a five-sample receptive field.
- Invalid feature value changes do not affect masked model outputs; masked target changes do not affect loss or gradients.
- A delayed second feature blocks later inputs until available; future feature changes cannot alter earlier emitted observations.
- Median measured CPU head push was 0.199–0.203 ms, p95 0.313–0.325 ms over 356 test cells per selected seed.
- Opened the saved figure: development/test bars and architecture/weak-label caveats are readable.

### What didn't work
No test, training, checkpoint reload, or measured streaming check failed. Test macro recall did not improve despite higher development recall. This is recorded as the result, not treated as a reason to select a test-favored seed. Printing remains paused under the previously recorded automatic approval rejection for external Almanach egress.

### What I learned
The small trained heads fit quickly, but added temporal capacity does not overcome the current representation and weak-data limitations. Causality and reproducibility can pass while predictive value remains inferior to the simpler baseline.

### What was tricky to build
The multi-stage receptive field accumulates context across stages. Bounded chunk inference therefore retains raw context for the sum of all causal layers, not only the last stage. Train normalization must be stored with the weights and applied before masking so missing storage values do not become normalized pseudo-observations. The availability adapter enforces ordered buffering rather than silently skipping delayed inputs.

### What warrants a second pair of eyes
Missing cells mask activations but do not reset the TCN's historical receptive field, unlike the classical run-reset adapter. The checkpoints support inference, not exact optimizer resume. Reported head latency excludes tensor construction, decoding, embedding, transport, and persistence. Three seed measurements do not establish confidence intervals or broad generalization.

### What should be done in the future
Implement T4 append-only facts, supersession/retraction, conflict/coverage/expiry queries, late evidence and restart tests, and separate offline/causal rule handoffs. Carry actual availability and producer identity into stored observations.

### Code review instructions
Read `temporal/tcn.py`, `train.py`, and `test_temporal_tcn.py`, then the measured report. Run `PYTHONPATH=workbench/src workbench/perception-env/.venv/bin/python -m pytest workbench/tests/test_temporal_data.py workbench/tests/test_temporal_classical.py workbench/tests/test_temporal_tcn.py -q`. Reproduce training with the CLI and a fresh destination. `scripts/05-tcn-evidence.py` reloads the selected actual checkpoints and rebuilds the latency/figure artifacts.

### Technical details
Selected architecture: input 2048, ten classes, 16 channels, one dilation-one residual block per stage, two stages, 35412 trainable parameters. Parameter/normalization buffer storage is 158032 bytes; batch-one retained raw history is 32772 bytes excluding temporary activations. Process peak RSS on macOS was 401342464 bytes. Adam learning rate 0.003, dropout 0.1, smoothness loss zero, inverse training-frequency weights normalized to mean one. Checkpoints and hashes live under `output/temporal-v1/tcn-v1` and tracked result metadata respectively.
