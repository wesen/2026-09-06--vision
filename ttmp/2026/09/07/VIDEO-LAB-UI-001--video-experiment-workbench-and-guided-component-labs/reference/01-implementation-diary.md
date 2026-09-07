---
Title: Implementation diary
Ticket: VIDEO-LAB-UI-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles: []
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-07T10:05:37.359166-04:00
WhatFor: ""
WhenToUse: ""
---

# Implementation diary

## Goal

Build an educational video experiment workbench with reproducible evidence, real component execution, and staged browser review.

## Step 1: Define the experiment contract and intern guide

Inspected the existing media, perception, embedding, verifier, temporal and replay adapters. Created a six-phase design that keeps evidence immutable while allowing interactive parameter changes. The guide explains mathematical operations and their limits before presenting the proposed API and implementation sequence.

### Prompt Context

**User prompt (verbatim):**

Ok, Create a new docmgr ticket to flesh out the UI. Create  a detailed analysis / design / implementation guide that is for a new intern, explaining all the parts of the system needed to understand what it is, with prose paragraphs and bullet point sand pseudocode and diagrams and api references and file references. It should be very clear and technical. Store in the ticket and the nupload to remarkable.
Then implement, commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done.

After each significant feature, run the web UI and allow me to play with it to give you feedback. Also make sure to write a detailed guide / explanation on each page about what the different components are, what the different options mean, what the maths is behidn it, etc... This could be both hover help text but also a guide tab or foldout.

**Assistant interpretation:** Create, document, deliver and implement an experiment workbench, with in-page teaching and user feedback at feature boundaries.

**Inferred user intent:** Make the system understandable and experimentally useful, especially when valid model answers are visually wrong.

### What I did

- Read docmgr, diary, brutalist-work-slip, remarkable-upload and textbook-authoring skills.
- Created VIDEO-LAB-UI-001 and the intern guide; mapped existing source APIs and separate inference environments.
- Printed the six-phase plan (HTTP 200, printed true, 2026-09-07T14:06:01Z).
- Started guide delivery using the skill-prescribed remarquee bundle command.

### Why

- The current replay only connects camera departure and exact-image verification; experimentation needs direct access to intermediate components.

### What worked

- Existing adapters provide reusable timestamp, feature identity, mask, tracking and bounded verification contracts.

### What didn't work

- No new failure in this step. Existing native-video reasoning remains unsupported by the accepted verifier contract.

### What I learned

- Tracking requires explicit cadence; reasoning currently accepts one image; pooled and native feature identities are incompatible.

### What was tricky to build

- Separating planned UI capabilities from already accepted runtime modes. The guide labels single-image sequences accurately and requires exact checkpoint/preprocessing identity for action heads.

### What warrants a second pair of eyes

- Review experiment bounds and state-transition semantics before relying on derived events.

### What should be done in the future

- Implement the six phases and update proposed API references to the final schema.

### Code review instructions

- Read the intern guide, especially sections 5, 8, 9 and 12. Compare referenced symbols against workbench/src/video_workbench.

### Technical details

- Baseline commit: 881cb1f. Source originals procedural_video_labs.zip and video_understanding_for_procedural_work.md are unrelated and remain untracked.
- Guide destination: /ai/2026/09/07/VIDEO-LAB-UI-001.

## Step 2: Deliver guide and expose exact evidence workspace

Implemented the first usable laboratory page with 121 corpus-qualified sources, PTS-based sampling, normalized crops, exact PNG previews and component-specific teaching panels. The page is running on port 8780 and the user has been invited to try it before further UI decisions.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Deliver a working evidence-selection feature and ask for feedback while developing independent inference adapters.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

### What I did

- Created lab catalog, contracts, evidence preparation, FastAPI app and responsive HTML UI.
- Uploaded Video Laboratory Intern Design Guide.pdf to /ai/2026/09/07/VIDEO-LAB-UI-001.
- Captured various/p2-workspace.png and ran two focused smoke tests.

### Why

Exact inputs and corpus identity must exist before component outputs can be compared.

### What worked

- reMarkable reported OK: uploaded.
- Browser selected home-v1--ep-7d3106fb1cac9776 and decoded two exact frames without error.
- pytest workbench/tests/test_lab.py: 2 passed.

### What didn't work

- Initial upload: Error: pandoc failed: xelatex not found. Fixed PATH=/Library/TeX/texbin:$PATH and explicit Helvetica/Menlo fonts using the existing TeX installation.
- Initial server startup: ValueError: conflicting source identity. Corpus versions reuse episode IDs with different bytes; fixed by dataset-qualified laboratory IDs.
- Browser initially reported a missing favicon; no application execution failure.

### What I learned

121 model-safe recordings are available across corpus versions, considerably more than the twelve replay measurement recordings.

### What was tricky to build

An episode ID is only unique within a corpus version. The catalog retains original_episode_id for artifact matching but uses dataset--episode_id as the UI identity; hashes remain authoritative.

### What warrants a second pair of eyes

Check crop and timestamp presentation and whether the shared layout leaves enough room for model controls.

### What should be done in the future

Connect immutable run supervision and actual perception/reasoning execution, then review the UI again.

### Code review instructions

Read lab/contracts.py, evidence.py and catalog.py. Run PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_lab.py -q. Try http://127.0.0.1:8780/.

### Technical details

Design commit 37e1019. Server process 28859. Preview maximum 64 actual samples; full-frame evidence unchanged by browser seeking. Plan and P1 start slips printed at 14:06:01Z and 14:06:20Z.
