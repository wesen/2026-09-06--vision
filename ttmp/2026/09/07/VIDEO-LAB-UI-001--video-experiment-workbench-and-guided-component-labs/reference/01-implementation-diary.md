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
