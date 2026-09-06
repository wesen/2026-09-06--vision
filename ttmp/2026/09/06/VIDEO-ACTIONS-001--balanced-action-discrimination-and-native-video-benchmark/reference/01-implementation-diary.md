---
Title: Implementation diary
Ticket: VIDEO-ACTIONS-001
Status: active
Topics:
    - video
    - embeddings
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/VIDEO-ACTIONS-001--balanced-action-discrimination-and-native-video-benchmark/scripts/04-review-posture-timing.py
      Note: Dense posture evidence
    - Path: repo://workbench/src/video_workbench/actions/__main__.py
      Note: Runnable experiment commands
    - Path: repo://workbench/src/video_workbench/actions/encode.py
      Note: Representation identities and source caches
    - Path: repo://workbench/src/video_workbench/actions/evaluate.py
      Note: Coverage and development-only selection
    - Path: repo://workbench/src/video_workbench/actions/review.py
      Note: Source-frame contact sheets
    - Path: repo://workbench/tests/test_action_contracts.py
      Note: Timing, lineage and metric contracts
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T17:01:56.120052-04:00
WhatFor: ""
WhenToUse: ""
---


# Implementation diary

## Goal

Complete VIDEO-ACTIONS-001 as part of the active three-ticket objective, preserving the full design, delivery, implementation, evaluation, screenshot, and commit requirements. VIDEO-TEMPORAL-001 remains part of the same goal.

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

## Step 3: Resolve simulator inverse-posture failures without falsifying action labels

The generic StandUp verb stalled after Sit and Watch: frames 96 and 1018 had identical SHA-256 values while the owned process continued recording. The request failed after 90 seconds. Preserved the failed manifest, log, and source images, identified the exact owned PID, and terminated that process before restarting. AIST's Stand operation completed in apartments 0 and 1.

Apartment 2 rejected the original sequence and two alternative bindings. The log implicated Watch planning. The minimal Sit/Stand program then completed on the original bed with 204 frames, so the final v4 config restores the original target and uses a separately versioned minimal posture policy. The full 48-trajectory generation is now running.

### Prompt Context
**User prompt (verbatim):** See Step 1. Additional steering: "how brittle is virtualhome?"

**Assistant interpretation:** Continue implementation and explain actual simulator failure modes candidly.

**Inferred user intent:** Understand whether the tool is reliable enough for the planned experiments without abandoning the active work.

**Commit (design/delivery):** `efda71c`.

### What I did
- Preserved the stalled attempt in `various/standup-failure/`, including equal source images at frames 96 and 1018.
- Revalidated the live process (PID 34414, port 18084), terminated only that owned process, and confirmed exit 143 before restarting.
- Probed Stand on sofas, then an apartment-2 chair and sofa; retained rejected versions v1–v3.
- Removed intervening/final LookAt from the posture program under `paired-actions-v2`; the v4 bed probe completed.
- Added source-window and intervention contracts plus an official FP32 image-pooling adapter under `actions/`.

### Why
A reversed video cannot substitute for a successfully rendered standing example. A source-defined operation can still be unavailable or broken in the installed Unity build.

### What worked
- Stand completed with 148 and 181 frames in the first two apartments; minimal Sit/Stand completed with 204 frames on the third apartment's original bed.
- Two action-contract tests pass, including fixed-window bounds, split leakage rejection, and preserved monotonic intervention slots.
- Existing corpus tests passed 19 tests and five subtests before further minimal-policy changes; rerun before the code checkpoint.

### What didn't work
- `UnityCommunicationException: HTTPConnectionPool(host='127.0.0.1', port=18084): Read timed out. (read timeout=90)` for StandUp.
- Apartment-2 chair 295: `PROCESS WALK: Can not select object: chair. REASON: Unknown`.
- Nonminimal bed/sofa programs: `EXECUTION_GENERAL: Script is impossible to execute`.
- Initial docmgr changelogs contained final blank lines; the commit command proceeded after reporting them. Removed those lines for the next checkpoint.

### What I learned
AIST Stand differs operationally from the generic StandUp entry. Scene bindings and inserted Watch actions can determine feasibility even when each verb exists.

### What was tricky to build
A timed-out HTTP call does not cancel Unity. Recovery required proving the process was still recording unchanged evidence and stopping the owned instance, not blindly starting another attempt against a busy scene.

### What warrants a second pair of eyes
The completed inverse-posture clips still require visual review. Config v4 is the final generation candidate, while v1–v3 are preserved probe history rather than independent benchmark data.

### What should be done in the future
Finish all 48 renders, audit and review direction windows, execute native/FP32 pooled/4-bit pooled controls, then complete localization and all temporal phases.

### Code review instructions
Inspect the optional program policy, the minimal posture branch, the source equality of stalled frames, and `actions/data.py`/`encoders.py` contracts.

### Technical details
Current generation: port 18084, `configs/virtualhome-paired-actions-v4.json`, `output/virtualhome-corpus/paired-actions-v4`. Separate config hashes and numbered attempts preserve every failure.

## Step 4: Validate 48 trajectories and correct posture windows from source evidence

The owned AIST/VirtualHome generation completed all 48 trajectories, producing 3,880 frames and 16 trajectories in each partition. Deep corpus validation succeeded. The initial candidate extraction produced 72 two-second windows without duration exclusions. I inspected all twelve source contact sheets and preserved them in the ticket.

Visual inspection exposed a selection error: the midpoint of a long exported Sit span often precedes the actual descent. Dense review of all six posture trajectories established visible descents near the exported end. A new dataset-v2 uses the same fixed rule for every Sit candidate: center at exported end minus 750 milliseconds. The initial dataset and review remain preserved; no model inference or score informed this correction.

### Prompt Context
**User prompt (verbatim):** (see Step 1). Additional correction: "oh so you consider AIST a different program? it's building upon virtualhome, no?"

**Assistant interpretation:** Continue the three-ticket implementation while distinguishing the installed AIST fork from upstream VirtualHome.

**Inferred user intent:** Obtain reproducible technical results and an inspectable source trail, without interpreting simulator requests as visual truth.

**Commit (code):** `3fe057f` — Add action encoding and evaluation pipeline with source-reviewed posture timing.

### What I did
- Polled generation session 53020 and verified successful terminal completion; did not restart it.
- Ran `diversity_runner validate` on the complete v4 release: 48 trajectories, 3,880 frames.
- Prepared 72 candidates, rendered and inspected twelve contact sheets, then generated six dense posture timing sheets with `scripts/04-review-posture-timing.py`.
- Preserved source/sample/protocol snapshots and a provisional per-sample review in `various/action-source-review-v1/`.
- Implemented separate encoding processes, resumable source caches, intervention provenance, coverage-aware evaluation, development-only abstention, and CLI commands.
- Canonicalized encoder metadata through JSON before immutable manifest comparison, preventing tuple/list mismatches during reuse.
- Added validation for all representation conditions, query order, feature row counts, review eligibility, and nonempty finite development inputs.

### Why
Balanced requested actions do not guarantee balanced observable actions. Timing and visibility must be corrected or recorded before the encoder comparison can support a conclusion.

### What worked
- Corpus generation and validation completed successfully.
- All six dense posture sheets show a real descent near the end of the exported Sit interval.
- `PYTHONPATH=src:workbench/src workbench/.venv/bin/python -m pytest tests workbench/tests/test_action_contracts.py -q`: 22 passed, 5 subtests passed.
- Candidate v2 extraction again produced 72 windows with no duration exclusions.

### What didn't work
- Initial midpoint windows for several Sit proposals show waiting or truncate descent; those labels remain pending until corrected-window review.
- Four lamp interaction windows do not establish visible on/off changes. Two edge-on television windows conceal display state. These six remain unobservable for action direction.
- The progress-slip network request first failed with `dial tcp: lookup almanach.crib.scapegoat.dev: no such host`. Escalated execution was rejected by automatic approval review because it considered project metadata sent to the Almanach service unauthorized sensitive egress. No retry or alternate route was attempted after rejection. The layout is saved locally, but this checkpoint was not printed. User approval for that destination is pending.
- Initial contact-sheet timestamps overlapped the image edge. Increased row spacing and moved captions into a white margin, then regenerated the sheets.

### What I learned
The action export is a proposal interval, including positioning or waiting. Its midpoint is not a reliable visual action center. This failure is in our window-selection assumption and does not mean the simulator failed to render sitting.

### What was tricky to build
Changing a source window changes its evidence identity and cache key. The correction therefore creates a new dataset version instead of mutating the original freeze. Eligibility remains separate from requested action; the provisional review has 20 pending rows requiring corrected-window or native-resolution inspection.

### What warrants a second pair of eyes
Review the six Sit timing sheets and uniform end-relative rule. The three encoder modes have implementation and contract checks but still require actual model execution, pixel dependence, and cache reuse validation. The evaluation must not be described as measured yet.

### What should be done in the future
Finish v2 source review and small-prop detail inspection, freeze final labels, run all three representations and interventions, report measured results, and provide timestamped features to the temporal ticket. Localization and temporal implementation remain within the active goal.

### Code review instructions
Start at `actions/data.py:action_center`, then inspect encoding identity and `evaluate.py` input gates. Reproduce candidate extraction with a new output directory and run the contract suite above. Review `candidate-review.json` alongside the named contact sheet; pending rows are deliberately not eligible ground truth.

### Technical details
The complete release is `output/virtualhome-corpus/paired-actions-v4`. Original and corrected candidates are `output/action-benchmark-v1/dataset` and `dataset-v2`. Review images are in `review`, `review-v2`, and `posture-timing`, with the original audit images copied into ticket storage. The owned simulator remains separate on port 18084; generation is terminal.

## Step 5: Measure three encoders and publish an honest failure report

Completed native-resolution review of the twenty unresolved windows and froze 62 eligible labels with ten unknown or ambiguous examples. All six corrected Sit windows show descent. The test split retains only six supported classes, including no confidently visible closing or switching examples. This eligibility loss remains explicit throughout evaluation.

Ran all three representations and original/reverse/repeat-first interventions on the frozen 72-window dataset. Every model completed actual inference and returned its same run identity during a second invocation. Published raw predictions, retrieval rankings, confusion and direction metrics, development-only abstention, a local browser gallery, and a sparse timestamped handoff. The models discriminate these generic action descriptions poorly; successful runtime checks do not establish action understanding.

### Prompt Context
**User prompt (verbatim):** (see Step 1).

**Assistant interpretation:** Complete the action experiment and preserve source evidence before proceeding to localization and temporal implementation.

**Inferred user intent:** Obtain measured, reproducible conclusions and useful downstream contracts, including negative results.

**Commit (code):** `3efda5a` — Add supported-query retrieval and timestamped action feature handoff.

### What I did
- Inspected twenty native-resolution detail sheets and copied final source reviews, source hashes, label counts, and images into `various/action-source-review-v2`.
- Executed official FP32 pooling, accepted native video, and the isolated community 4-bit baseline sequentially; then invoked all three again to verify completed-run reuse.
- Verified native black-frame pixel dependence and pooled permutation invariance.
- Added supported-query retrieval with interval union coverage and raw rankings, plus explicit original direction margins.
- Wrote the measured reference report and generated `various/comparison-v2/index.html`, with overview and full-page browser screenshots.
- Exported 144 sparse per-episode/per-space sequences and verified all 216 feature rows against source identities and clocks.

### Why
The experiment must compare identical evidence without hiding unobservable examples, quantization differences, or unsuccessful calibration transfer. Downstream memory and temporal models require explicit availability and validity rather than implicit dense labels.

### What worked
- Native: 225 fresh cached vectors, 58.1 seconds in the encoding loop. FP32 pooled: 297 vectors, 45.5 seconds. 4-bit pooled: 297 vectors, 46.1 seconds. All repeated invocations reported reused runs with 72 samples.
- Native original-versus-black cosine was 0.498; maximum vector component change was 0.146.
- Pooled original/reverse maximum differences were below 6e-8; native reversal changed components by up to 0.0808.
- Contract suite: 24 tests passed and five subtests passed, including interval-overlap union and reordered sparse handoff clock/mask checks.

### What didn't work
- Native generic test classification: 1/17; FP32 pooled: 0/17; 4-bit pooled: 7/17, mostly approach-only controls.
- None of the opposite-action margins changed sign under reversal, despite native vector changes.
- Development abstention did not transfer reliably. Native accepted four wrong known test answers and one unknown answer; FP32 pooling accepted seven wrong known answers and two unknown answers.
- Microwave close requests did not establish visible closing in the sampled windows. The monitor concealed one book transfer. These remain unknown instead of receiving requested labels.
- Printing remains blocked by the prior automatic approval rejection; no additional network print attempt was made without the requested destination approval.

### What I learned
Retrieval can improve while nine-way classification remains poor: native Success@5 is 4/6 supported test queries, but a relevant hit need not prefer its correct description over all other descriptions. Threshold confidence also changes across apartments and checkpoints.

### What was tricky to build
Source review may use larger images to establish labels, while model preprocessing remains fixed and may lose small-object evidence. Reporting must preserve that distinction. Retrieval must also retain unknown distractors and avoid manufacturing metrics for unsupported queries. Sparse temporal export requires sorting by availability and keeping unknown labels distinct from valid visual evidence.

### What warrants a second pair of eyes
The label pass has one assistant reviewer and no independent agreement estimate. Check small-prop partial labels and the unknown microwave rows against the preserved images. Treat the temporal export as sparse evidence, not dense action segmentation supervision.

### What should be done in the future
Implement the requested-object localization experiment, then construct dense trailing-window features, classical/TCN baselines, and append-only memory under VIDEO-TEMPORAL-001. The active goal remains open until both implementations and outstanding meaningful printing are handled.

### Code review instructions
Inspect `actions/evaluate.py` for undefined unsupported metrics, development-only policy selection, and opposite-query margins. Inspect `actions/handoff.py` for row ordering and mask semantics. Run `scripts/07-audit-handoff.py` to verify all exported artifacts and open the source-linked HTML gallery.

### Technical details
Run IDs: native `b42181da3d85aca62c3e78fd9be9992ca2b0ef0cd16e05b49fb65e8c288aeb5e`; FP32 pooled `b9f5be3d798a5b863a3bdcb1c781119fe94ef75a28771c5161382b0ab7b606ac`; 4-bit pooled `6e814e65fd90c9116b13bc8cd5dd0ded7fbdab213f6fcedda8e5ac19a2589847`. All encoding sessions are terminal. Local gallery server uses loopback port 8776. No test score informed the final label freeze or query selection.
