---
Title: Design and delivery diary
Ticket: VIDEO-REPLAY-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/VIDEO-REPLAY-001--project-5-replay-and-incident-workbench/design-doc/01-intern-analysis-design-and-implementation-guide.md
      Note: Authored project guide
    - Path: repo://ttmp/2026/09/06/VIDEO-REPLAY-001--project-5-replay-and-incident-workbench/scripts/01-pdf-header.tex
      Note: Per-ticket PDF header
    - Path: repo://ttmp/2026/09/06/VIDEO-REPLAY-001--project-5-replay-and-incident-workbench/tasks.md
      Note: Phased implementation breakdown
    - Path: repo://ttmp/2026/09/06/VIDEO-REPLAY-001--project-5-replay-and-incident-workbench/various/pdf-validation.json
      Note: Visual review and artifact hashes
    - Path: repo://ttmp/2026/09/06/VIDEO-REPLAY-001--project-5-replay-and-incident-workbench/various/remarkable-upload.json
      Note: Successful individual delivery
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T13:13:52.123558-04:00
WhatFor: ""
WhenToUse: ""
---



# Diary

## Goal

Record evidence, design decisions, implementation-task decomposition, and reMarkable delivery for VIDEO-REPLAY-001. This ticket is a design deliverable now; application implementation remains open.

## Step 1: Establish the project boundary

Created this child of COSMOS-VIDEO-001 and inspected the existing generator, validated corpus, teaching labs, and umbrella guide. The project scope is: Integrate causal replay, incident revisions, a viewer, and held-out real-video evaluation. Dependencies are VIDEO-SEARCH-001, VIDEO-STATE-001, VIDEO-TEMPORAL-001, VIDEO-RULES-001.

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

Wrote the project-specific analysis, proposed contracts, data flow, decision records, implementation phases, test strategy, and review exercise. The guide explains integrate causal replay, incident revisions, a viewer, and held-out real-video evaluation. It distinguishes the working VirtualHome generator from future workbench modules and keeps the current corpus's label limits explicit.

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
- Recorded `OK: uploaded VIDEO-REPLAY-001_Intern_Guide.pdf -> /ai/2026/09/06/VIDEO-REPLAY-001`.

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
- Reproduce with the shared render script and `--ticket VIDEO-REPLAY-001`; repeat review after content/layout changes.

### Technical details
- Remote directory: `/ai/2026/09/06/VIDEO-REPLAY-001`.
- Local inspected PDF: `/Users/manuel/code/wesen/2026-09-06--vision/output/pdf/project-guides/VIDEO-REPLAY-001/VIDEO-REPLAY-001_Intern_Guide.pdf`.
- Six-page visual review and individual dry-run/upload receipts are stored under `various/`.

## Step 4: Simplify the implementation contract after measured RULES completion

The completed RULES experiment supplies actual delayed verifier work and clear visual failures for replay inspection. I replaced the initial broad implementation checklist with a concrete clock/broker/scheduler/viewer contract and retained the original guide as historical design. Separate immutable evidence conditions provide the required history without introducing revision chains or an incident workflow.

The design explicitly distinguishes recorded service replay from a fresh live verifier. This prevents cached detector/model output from being presented as newly measured end-to-end inference capacity.

### Prompt Context
**User prompt (verbatim):** "finish RULES measurement → simplify REPLAY design → implement the replay viewer and bounded scheduler. commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Implement a bounded inspectable replay workbench after finishing the measured rule integration, with meaningful commits, diary, and phase slips.

**Inferred user intent:** Make the connected system observable and test its behavior under processing delay and overload without premature infrastructure.

### What I did
- Read existing replay design, search/perception APIs, temporal store, rule handoff, and worker contracts.
- Added design document 02 with explicit modules, clocks, queue policy, subprocess deadlines, persistence, endpoints, and acceptance evidence.
- Added a superseding scope note to guide 01 and rewrote active tasks; deferred work remains unchecked and labeled LATER.
- Printed P1 RULES completion and P2 design start slips, preserving layouts and receipts.

### Why
The old plan coupled a usable replay viewer to general revision machinery, outbox publication, restart recovery, and real-video collection. Those are independent features. The current application needs stable case IDs, separate decisions, and as-of visibility, which are simpler and sufficient for inspecting measured evidence.

### What worked
- Existing verifier execution and strict contracts can be reused without another model wrapper.
- Existing media serving establishes registered-ID and hash-validation conventions.
- RULES commit `51b2f0f` contains the completed measured comparison and evidence images.
- P1 done print: HTTP 200, printed true, 384×627 at 2026-09-07T04:56:34Z. P2 start: HTTP 200, printed true, 384×358 at 2026-09-07T04:56:38Z.

### What didn't work
No new command failed during this design step. The original guide's automatic recovery and real-video acceptance are not implemented and remain explicitly deferred rather than marked done.

### What I learned
Recorded per-frame service timings provide a reproducible queue workload, while fresh verifier execution is needed to demonstrate that the broker and scheduler actually invoke the accepted runtime. Both modes need prominent labels and separate measurements.

### What was tricky to build
Source time advances at a declared replay speed while worker budgets remain wall-clock deadlines. Queue delay must consume the deadline, and completion must be timestamped when observed. Dropping a frame also breaks the detector's consecutive-frame evidence; it requires a prefix reset and a visible gap, not merely a throughput counter.

### What warrants a second pair of eyes
The recorded mode measures application scheduling, not fresh perception throughput. The approved-packet boundary is an application contract for trusted workers, not an OS security sandbox. The first viewer must expose both facts clearly.

### What should be done in the future
Implement P3 and P4 against the new acceptance contract, inspect the actual browser, and measure normal plus overloaded runs before claiming completion.

### Code review instructions
Read `design-doc/02-bounded-replay-implementation-and-viewer-contract.md`, then the revised task list. The note atop guide 01 explains which requirements are historical. Verify that every deferred item remains visible and every active acceptance condition has a planned artifact.

### Technical details
One active replay/server, one worker/run, queued mandatory work before optional work, nonpreemptive execution with hard deadline, count and byte bounds including running payload, append-only SQLite records, bounded polling, recorded/live-verifier modes, and hash-checked registered media.

## Step 5: Implement the bounded replay primitives

Added the monotonic source clock, approved evidence broker, one-worker subprocess scheduler, immutable replay store, and fixed worker entry point. The scheduler accounts for the running payload as well as queued work and reports every terminal outcome to the host for durable logging. Queue waiting consumes the same wall deadline used during execution.

This is the core implementation checkpoint. Trace/rule integration and the viewer remain open; passing primitive tests does not establish the whole replay application.

### Prompt Context
**User prompt (verbatim):** (see Step 4)

**Assistant interpretation:** Build and verify the bounded execution and history primitives before connecting the actual workloads.

**Inferred user intent:** Ensure overload and delayed evidence remain inspectable and do not create silent future leakage.

### What I did
- Added `replay/clock.py`, `broker.py`, `scheduler.py`, `store.py`, and `worker.py`.
- Enforced future dependency rejection, registered frame timestamps, source hashing, and exclusion of path/command fields from released trace data.
- Added mandatory queue priority and optional eviction, count/byte admission including active work, queue expiry, worker process-group termination/reaping, cancellation, and bounded result loading.
- Added immutable SQLite rows with stable IDs, ordered commitment horizons, and bounded as-of cursor queries.
- Ran `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest -q workbench/tests/test_replay_core.py`: ten checks passed in 0.54 s.
- Printed and archived P2 completion and P3 start slips.

### Why
A prerecorded file already contains future evidence. Explicit broker checks prevent accidental worker access through the application contract. A finite queue alone is insufficient if the running job is omitted from memory accounting or receives a renewed deadline after waiting.

### What worked
- Real subprocess timeout and cancellation checks confirmed terminated PIDs no longer exist.
- Mandatory jobs evicted queued optional work and never exceeded either high-water bound.
- Cached feature dependency times beyond the horizon were rejected.
- Earlier as-of views hid later verifier rows; reopening the database retained both separate conditions.
- P2 done print: HTTP 200, printed true, 384×533 at 2026-09-07T05:02:03Z. P3 start: HTTP 200, printed true, 384×380 at 2026-09-07T05:02:07Z.

### What didn't work
No feature smoke failed. Source inspection showed the accepted verifier worker exports `run`, not `main`; corrected the live-worker invocation before attempting model execution. Live execution is not yet validated by this checkpoint.

### What I learned
Subprocess lifecycle tests are inexpensive and directly establish the important deadline invariant. The API and engine can consume terminal events without introducing a background publication mechanism.

### What was tricky to build
A worker may finish between polls after its deadline. The scheduler conservatively records timeout when completion is observed past the deadline, even if an output file exists. Input payloads are serialized and copied at admission so later caller mutation cannot silently change the actual worker input. As-of pagination is safe because commitment horizons are monotonic.

### What warrants a second pair of eyes
The engine still needs to persist every scheduler outcome, reset detector prefix state on dropped frames, and validate model output against the request. The broker is a trusted-code boundary, not filesystem isolation. The scheduler's output cap applies before JSON loading; worker disk artifacts remain available to the host.

### What should be done in the future
Connect actual recorded traces, exact-time states, candidate rules, recorded/live verifier paths, then implement and inspect the viewer. Complete the full P3/P4 gates before closing the ticket.

### Code review instructions
Read `replay/scheduler.py` admission, poll, and cancel paths, then the broker horizon checks and SQLite as-of query. Run the targeted test file at this feature boundary. Check that no complete source-video path is inserted into a worker job.

### Technical details
Default admission bounds are sixteen jobs and sixteen MiB, including running work. Worker results are capped at one MiB. One process group runs at a time; stdout/stderr are discarded and structured output is read from the bounded result file. The engine will attach explicit failed/timeout records rather than treating absent output as a negative model answer.

## Step 6: Connect the measured workload and observe real queue loss

Connected full recorded YOLO traces, sampled observations, departure rules, and the accepted verifier contract to the new scheduler. A normal-speed recorded run completed over an actual open-microwave episode. It correctly produced a separate VIOLATION after the recorded Qwen service delay, while the nonpreemptive verifier caused visible perception drops and queue expiry.

The result establishes why the queue needs explicit coverage records: one long optional call can block mandatory frames already arriving, even though queued mandatory work has priority once the worker becomes free.

### Prompt Context
**User prompt (verbatim):** (see Step 4)

**Assistant interpretation:** Verify connected replay behavior and retain evidence before building the viewer.

**Inferred user intent:** Inspect actual delayed decisions and understand bounded overload behavior.

**Commit (code):** `1deb161` — bounded replay clock, broker, scheduler, and immutable history primitives.

### What I did
- Added `replay/engine.py` and module CLI with recorded/live-verifier modes, bounded options, and a fixed operator registry.
- Added source/trace integrity checks, exact-time sampled-state import, stable case IDs, separate baseline/verifier records, and retained approved images.
- Reset the departure prefix across missing frame indices or cycle boundaries.
- Reparsed recorded model text against the newly bound approved request after checking identical image bytes and profile identity.
- Ran the connected recorded episode `ep-c1c313b64f579794` at speed 1.
- Expanded feature smoke to twelve passing checks, including dropped-frame prefix reset and bounded option validation.

### Why
The primitive scheduler cannot demonstrate correct rule integration by itself. Real trace execution checks the available evidence, rule timing, request boundary, and commitment history together.

### What worked
- Run `replay-5e4499f558614b62` completed in 17.29 wall seconds for 13.7 source seconds.
- One camera candidate, one UNKNOWN baseline, and one separate recorded-Qwen VIOLATION were committed.
- 97/137 perception frames completed; ten were dropped and thirty expired. Every loss has an explicit gap record.
- Queue high water was exactly sixteen jobs, including the running verifier, and 1,236,979 admitted bytes under the sixteen-MiB bound.
- No frame was passed to a verifier before its source availability; recorded model output required exact approved image hash equality.

### What didn't work
The first CLI attempt failed during memory sampling with `PermissionError: [Errno 1] Operation not permitted (originated from sysctl() malloc 1/3)` when psutil enumerated all process children. Replaced global process enumeration with sampling only the known scheduler worker PID and renamed the metric to host-and-worker RSS. The subsequent run completed successfully. The failed construction directory remains as diagnostic evidence and is not counted as a completed run.

### What I learned
Priority among queued jobs cannot preempt a running model call. The current policy preserves memory bounds and explicitly loses coverage during that call. It does not establish sustainable full-frame real-time processing with one shared worker.

### What was tricky to build
The recorded result uses old host-bound request IDs, so copying its parsed answer would be invalid. The engine verifies identical image bytes and profile identity, then reuses only the original raw model response and parses it under the new request. Live mode additionally requires the worker's new request ID to match exactly.

### What warrants a second pair of eyes
The normal run demonstrates queue loss, not complete source coverage. Recorded service replay does not execute YOLO anew. Live verifier execution is being validated separately. Deadline statistics currently include terminal dropped/expired work as well as completed work; the report must state this or group them by outcome.

### What should be done in the future
Build the API and viewer, inspect the missed-fridge/detected-microwave cases and gap timeline, complete a fresh live verifier run and a separate repeated capacity experiment, then publish measured results and screenshots.

### Code review instructions
Read engine source release, candidate packet construction, and completion handling. Inspect the saved replay SQLite rows and summary under `output/replay-workbench/replay-5e4499f558614b62/`. Run the twelve focused tests after changing engine boundary behavior.

### Technical details
CLI: `PYTHONPATH=workbench/src workbench/.venv/bin/python -m video_workbench.replay run ep-c1c313b64f579794 --speed 1 --max-jobs 16`. The live mode invokes the existing accepted worker's `run` function in the scheduler-owned process group, so its deadline covers loading and inference directly.
