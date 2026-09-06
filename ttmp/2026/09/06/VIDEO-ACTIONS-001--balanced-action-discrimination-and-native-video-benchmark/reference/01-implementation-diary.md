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
RelatedFiles: []
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
