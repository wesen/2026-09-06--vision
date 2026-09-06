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
    - Path: repo://workbench/src/video_workbench/temporal/encode.py
      Note: Actual pooled extraction and source audit (0d47851)
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
