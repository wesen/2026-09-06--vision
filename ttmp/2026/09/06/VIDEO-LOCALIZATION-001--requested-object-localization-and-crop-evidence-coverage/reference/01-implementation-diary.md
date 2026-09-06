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
    - Path: repo://workbench/src/video_workbench/localization/data.py
      Note: Source-hash audit and requested-target deduplication
    - Path: repo://workbench/src/video_workbench/localization/evaluate.py
      Note: Best-overlap recall versus unique binding
    - Path: repo://workbench/src/video_workbench/perception/contracts.py
      Note: Shared half-open geometry
    - Path: repo://workbench/src/video_workbench/predicates/regions.py
      Note: Existing production requested-class binder
    - Path: repo://workbench/tests/test_localization_contracts.py
      Note: Hand-computed metric and review checks
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
