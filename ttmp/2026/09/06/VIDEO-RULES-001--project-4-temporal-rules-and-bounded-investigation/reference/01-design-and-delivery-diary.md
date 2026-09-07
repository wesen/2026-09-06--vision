---
Title: Design and delivery diary
Ticket: VIDEO-RULES-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/VIDEO-RULES-001--project-4-temporal-rules-and-bounded-investigation/design-doc/01-intern-analysis-design-and-implementation-guide.md
      Note: Authored project guide
    - Path: repo://ttmp/2026/09/06/VIDEO-RULES-001--project-4-temporal-rules-and-bounded-investigation/scripts/01-pdf-header.tex
      Note: Per-ticket PDF header
    - Path: repo://ttmp/2026/09/06/VIDEO-RULES-001--project-4-temporal-rules-and-bounded-investigation/tasks.md
      Note: Phased implementation breakdown
    - Path: repo://ttmp/2026/09/06/VIDEO-RULES-001--project-4-temporal-rules-and-bounded-investigation/various/pdf-validation.json
      Note: Visual review and artifact hashes
    - Path: repo://ttmp/2026/09/06/VIDEO-RULES-001--project-4-temporal-rules-and-bounded-investigation/various/remarkable-upload.json
      Note: Successful individual delivery
    - Path: repo://workbench/src/video_workbench/rules/evaluate.py
      Note: Flat deterministic rule evaluator
    - Path: repo://workbench/src/video_workbench/rules/stored.py
      Note: Read-only as-of observation integration
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T13:13:51.924897-04:00
WhatFor: ""
WhenToUse: ""
---




# Diary

## Goal

Record evidence, design decisions, implementation-task decomposition, and reMarkable delivery for VIDEO-RULES-001. This ticket is a design deliverable now; application implementation remains open.

## Step 1: Establish the project boundary

Created this child of COSMOS-VIDEO-001 and inspected the existing generator, validated corpus, teaching labs, and umbrella guide. The project scope is: Evaluate typed three-valued rules and audit bounded evidence refinement. Dependencies are VIDEO-TEMPORAL-001, COSMOS-VERIFY-001.

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

Wrote the project-specific analysis, proposed contracts, data flow, decision records, implementation phases, test strategy, and review exercise. The guide explains evaluate typed three-valued rules and audit bounded evidence refinement. It distinguishes the working VirtualHome generator from future workbench modules and keeps the current corpus's label limits explicit.

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
- Recorded `OK: uploaded VIDEO-RULES-001_Intern_Guide.pdf -> /ai/2026/09/06/VIDEO-RULES-001`.

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
- Reproduce with the shared render script and `--ticket VIDEO-RULES-001`; repeat review after content/layout changes.

### Technical details
- Remote directory: `/ai/2026/09/06/VIDEO-RULES-001`.
- Local inspected PDF: `/Users/manuel/code/wesen/2026-09-06--vision/output/pdf/project-guides/VIDEO-RULES-001/VIDEO-RULES-001_Intern_Guide.pdf`.
- Six-page visual review and individual dry-run/upload receipts are stored under `various/`.

## Step 4: Simplify the design and implement the first two RULES features

Revised RULES and COSMOS-VERIFY integration around immutable evidence and repeated evaluations. The initial RULES implementation now uses three flat templates and one focused evidence-request handoff, deferring recursive composition, autonomous investigation, and revision/incident machinery. Required entity, clock, unknown, and coverage checks remain.

Implemented the pure rule evaluator and read-only sampled-store adapter, then ran a smoke check at each completed feature boundary. Preserved a reviewed oracle outcome figure and the complete actual-data evaluation trail. These steps establish logical behavior and integration, not end-to-end procedural accuracy.

### Prompt Context
**User prompt (verbatim):** "ok, update the design docs if needed. then work on RULES. Anything in RULES that seems overengineered? if so, explain why"

**Assistant interpretation:** Update the designs to remove unneeded revision machinery, explain other premature abstractions, and implement practical rule evaluation.

**Inferred user intent:** Make progress on concrete rules without a generic framework or repetitive testing overhead.

**Commits (code):** `26453c0` — Simplify RULES scope and implement flat evidence-based templates; `ed3b624` — Connect flat rules to sampled observation memory.

### What I did
- Read RULES/VERIFY guides, RULES tasks/diary, and the implemented temporal store.
- Updated RULES with a prominent scope section that supersedes the broader original design; clarified VERIFY outputs as immutable answers rather than replacements.
- Defined flat `state_at_event`, `before`, and `no_event_in` JSON templates with strict fields and integer time bounds.
- Implemented pure PASS/VIOLATION/UNKNOWN evaluation, correct subject/stream binding, exact-sample state matching, strict uncertain event ordering, and explicit oracle/reviewed absence coverage.
- Added a read-only SQLite adapter that selects durably available observations for a single run/stream/entity/property.
- Ran 16 hand-derived oracle cases and three malformed schemas once at the R1 boundary, then a separate actual 864-observation integration smoke at R2 completion.
- Printed the meaningful implementation plan with the standing Almanach approval; saved its layout.
- Marked R1 and R2 tasks complete and retained R3/R4 as open.

### Why
A seven-operator recursive language, generic investigator, and revision chains introduce policy before a concrete consumer exists. In contrast, missing triggers, wrong entities, time uncertainty, and uncovered intervals already create false-rule risks on the available corpus.

### What worked
- Sixteen oracle cases and three invalid schemas passed. Exact equality fails strict ordering, overlapping uncertainty stays unknown, and an observed prohibited event violates absence despite other gaps.
- Actual sampled-state integration: all 864 queries were unknown before commitment; afterward 662 PASS, 52 VIOLATION, and 150 UNKNOWN across six separate state streams.
- Reopening the database for repeated calls preserved evaluation identity/results; no database writes or observation replacement occurred.
- Opened `various/r1-oracle/rule-outcomes.png` and checked labels/reasons for readability.
- Almanach reported HTTP 200, `printed: true`, rendered at 2026-09-06T23:52:56Z, 384×461.

### What didn't work
No smoke case or implementation command failed. Exact departure events are not established by the available state handoff, so the real-data integration explicitly uses sampled-frame triggers. It does not relabel them as departures or treat decision counts as accuracy. The original reMarkable guide receipts refer to the earlier editions; updated source is not claimed as already delivered.

### What I learned
The practical rule interface can stay small while preserving the important distinctions. A missing trigger is an applicability limitation, a missing exact frame is a state-evidence limitation, and an uncovered interval is an absence-evidence limitation; each yields a different recorded reason for UNKNOWN.

### What was tricky to build
The store has point observations, so uncertain trigger bounds cannot safely select a nearby frame. The evaluator returns UNKNOWN instead. Event absence uses half-open intervals while event uncertainty bounds include their endpoints; an uncertain event touching the interval boundary prevents a false PASS. Explicit coverage spans are unioned without bridging gaps.

### What warrants a second pair of eyes
Hand-authored event coverage is oracle/reviewed evidence, not something generated from sparse predictions. The actual integration tests rule behavior against predicted values, not reviewed procedural truth. Whole interval and exact-departure quality remain unproven. The updated guide keeps the original broader explanations below an explicit superseding scope section.

### What should be done in the future
Implement the single focused verifier-request handoff and immutable repeated-evaluation contract, then publish the scoped oracle/predicted comparison. Actual Qwen/Cosmos execution remains gated on COSMOS-VERIFY acceptance. Refresh the revised guide editions separately from their historical receipts.

### Code review instructions
Read `rules/evaluate.py`, `rules/stored.py`, and `workbench/configs/rules/household-v1.json`. The feature smoke scripts are ticket `scripts/02-flat-rule-smoke.py` and `scripts/03-stored-rule-smoke.py`, run with `PYTHONPATH=workbench/src workbench/.venv/bin/python`. Review saved oracle outcomes and actual per-stream counts under `various/r1-oracle` and `various/r2-stored`.

### Technical details
Rule decisions have content-derived evaluation IDs, rule hashes, evidence IDs, subject scope, as-of time, applicability, and evaluator version. The stored adapter additionally records run identity. Actual source SQLite SHA: `3a2f5051660eba3dabdd92685e3dd11df4a261e638e7861447b2524e798aa2c3`. No revisions, supersession, model calls, recursive expressions, or mutable global state are used by the evaluator.

R1/R2 completion slip also printed successfully: HTTP 200, `printed: true`, 384×414, rendered 2026-09-07T00:00:17Z. Layout and both printing receipts are saved under `various/`.

## Step 5: Complete the focused handoff and measured RULES report

Added a shared request/answer contract and a one-request planner for unknown point-state decisions. Requests bind approved exact-time frames and the target object; answers create an independent verifier evidence condition rather than replacing the original evaluation. Missing triggers and interval-coverage uncertainty do not trigger an irrelevant state question.

Published the measured RULES report with explicit distinctions between oracle logic, actual predicted decision counts, and injected verifier responses. The handoff is ready for COSMOS-VERIFY, while full-system recall remains gated on a reviewed candidate/evaluation set.

### Prompt Context
**User prompt (verbatim):** "ok, commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Finish the agreed handoff, then begin verifier runtime work, retaining commits, diary, and meaningful printed phase boundaries.

**Inferred user intent:** Move the functioning rule layer into real model verification with an auditable implementation trail.

**Commit (code):** `5fecab4` — Add focused verifier request handoff and measured RULES report.

### What I did
- Added `verifiers/contracts.py` for bounded image requests and strict cited JSON answers.
- Added `rules/handoff.py` for a single focused request and separately selected verifier evaluation.
- Generated actual full-frame packets for the 150 unknown crop decisions; deduplicated to 75 request identities.
- Ran one completed-feature smoke covering true/false/unknown injected answers, invalid JSON, duplicate keys, invented citations, future frames, and missing triggers.
- Wrote the measured report and saved/reviewed the handoff figure; marked R3 complete and recorded the R4 candidate-recall gate.
- Printed the R3 start slip and requested the completion slip before VERIFY startup.

### Why
Additional verifier evidence does not automatically invalidate the old prediction. Keeping a separate evaluated condition makes this policy explicit without adding revision machinery. A fixed request boundary also separates model execution from deterministic rule semantics.

### What worked
- Actual packets: 150 candidate decisions, 75 unique requests, zero model calls at this stage.
- Three injected answers produced separate VIOLATION/PASS/UNKNOWN results and preserved the original UNKNOWN evaluation.
- Bad citations/schema and a future frame were rejected; a missing trigger produced no request.
- Reviewed `various/r3-handoff/handoff-trace.png`; labels distinguish actual requests from injected answers.
- The report keeps 662 PASS / 52 VIOLATION / 150 UNKNOWN as decision counts, not accuracy.

### What didn't work
No handoff smoke case failed. An exploratory shell glob `workbench/requirements*` had no matches; dependency pins are in `workbench/pyproject.toml` and `uv.lock`. Live verifier accuracy and upstream missed-candidate recall remain unavailable and are not replaced by fixture results.

### What I learned
The two crop classifiers share missing samples, so request deduplication removes repeated questions over identical evidence. The fallback packet uses original full frames, which changes evidence relative to crop-only recognition and must be acknowledged in later comparisons.

### What was tricky to build
The existing store concerns exact timestamps, so the request cannot answer a point-state question from a nearby frame. The request's half-open allowed interval is one microsecond wide around the exact sample. Request identity includes evidence and resource bounds. Result availability is checked against request time, preventing backdated evaluations.

### What warrants a second pair of eyes
Schema/citation validity does not prove factual support. Frame byte hashes must be checked by the runtime before inference. Model confidence is not treated as calibrated. Separate verifier-conditioned results do not constitute reconciliation or correction of the baseline.

### What should be done in the future
Begin V1 with pinned Qwen/Cosmos image candidates in an isolated environment, then implement bounded execution and a reviewed question comparison. Return to RULES end-to-end recall only with reviewed candidate coverage and accepted verifier outputs.

### Code review instructions
Read `rules/handoff.py`, `verifiers/contracts.py`, and `reference/02-measured-rules-and-focused-verifier-handoff.md`. Run ticket `scripts/04-handoff-smoke.py` at the feature boundary under `PYTHONPATH=workbench/src workbench/.venv/bin/python`. Inspect the actual packet table and injected-answer provenance separately.

### Technical details
Current limits: one to four exact-time images, 256 requested output tokens, 60-second request deadline; contract caps are 512 tokens and 120 seconds. The planner executes no model and has no retry loop. Raw responses are retained. Missing-trigger/interval cases remain UNKNOWN without a request.

## Step 6: Freeze the camera-departure population and causal candidate policy

The remaining recall task needs reviewed events, including events that never generate a request. The paired-action corpus does not contain the required departures. I inspected the original household recordings and prepared twelve development/test recording reviews, with every native frame around each visible exit retained as screenshots.

The event is precisely a departure from the camera view. Room crossings outside that view are not observable. The reference annotations come from RGB inspection, and several microwave recordings remain visibly closed despite scenario names suggesting reopening. No program-derived state labels enter this experiment.

### Prompt Context
**User prompt (verbatim):** "finish RULES measurement → simplify REPLAY design → implement the replay viewer and bounded scheduler. commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Complete measured rule coverage, then simplify and implement the replay workbench, recording phase boundaries and evidence.

**Inferred user intent:** Connect the existing perception and verifier components into an inspectable bounded system with defensible measurements.

### What I did
- Printed the four-phase work plan and P1 start slip; saved layouts in REPLAY and RULES `various/`.
- Added review scripts 05 and 06, twelve complete-recording contact sheets, twelve native-frame exit sheets, a source manifest, separate reviewed labels, and a frozen protocol.
- Added `rules/departure.py`: constant-memory causal person-disappearance candidates, armed after three detections and confirmed after three absences at score threshold 0.25.
- Added script 07 to run the existing pinned YOLO adapter over every frame without reading reviewed labels.
- Fixed one-to-one event matching tolerance at 500 ms before candidate/model outcomes; selected the already accepted direct-greedy Qwen and Cosmos profiles.

### Why
A verifier-only image comparison cannot count missed triggers. The new population contains both visible open and closed target doors at camera departure and preserves false candidate opportunities throughout each recording.

### What worked
- All twelve source video hashes matched their manifests.
- RGB review located six open and six closed target states at visible exits.
- Candidate input and reviewed labels are separate files; candidate extraction has no access to scenario variants, programs, or state truth.
- Plan print: HTTP 200, printed true, 384×461 at 2026-09-07T04:35:21Z. P1 start: HTTP 200, printed true, 384×358 at 2026-09-07T04:35:42Z.

### What didn't work
- `cat workbench/src/video_workbench/perception/detect.py` failed with `No such file or directory`; the adapter is `detector.py`.
- The first native-frame sheet run failed with `IndexError: list index out of range` because review intervals assumed split grouping while the manifest is sorted by episode ID. Corrected the interval order and reran successfully.

### What I learned
Synthetic program intent does not establish visible endpoint state. The benchmark must name the camera event it actually observes. An actor can also disappear before a detector's full-body score ceases to pass, or a detector can lose the actor early; matching needs an explicit tolerance.

### What was tricky to build
Disappearance must emit at the first absent timestamp but become available only after confirmation. The implementation stores both times and only rearms after a fresh consecutive presence sequence. It retains every false candidate rather than selecting the event nearest the reviewed departure.

### What warrants a second pair of eyes
These are assistant-reviewed synthetic frames, not independent human adjudication. Full-recording review is sampled while exit neighborhoods are dense. Small microwave door geometry and a few foreground actor pixels at the image boundary warrant independent review. This is an exploratory camera-exit measurement, not a general room-departure benchmark.

### What should be done in the future
Run detection, materialize exact candidate frames, execute the two accepted verifiers, and report misses, false candidates, unknowns, cost, and latency. Then simplify REPLAY without adding revision machinery.

### Code review instructions
Start with `various/r4-review/protocol.json`, `reviewed-events.json`, and the saved exit sheets. Read `rules/departure.py` and script 07. Candidate extraction runs under the perception environment with explicit MPS; feature smoke checks follow implementation completion.

### Technical details
Policy: YOLO person score ≥0.25, three consecutive detections to arm, three consecutive absences to emit, first absent PTS as event time, third absent PTS as availability. Event matching is within episode, maximum one-to-one cardinality followed by minimum absolute timestamp error, tolerance 500,000 us. The no-verifier state baseline requires exact timestamps and otherwise remains UNKNOWN.
