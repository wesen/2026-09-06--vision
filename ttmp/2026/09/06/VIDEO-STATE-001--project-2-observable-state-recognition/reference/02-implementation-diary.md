---
Title: Implementation diary
Ticket: VIDEO-STATE-001
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
LastUpdated: 2026-09-06T14:35:08.443987-04:00
WhatFor: ""
WhenToUse: ""
---

# Implementation diary

## Step 1: Establish the independent state-recognition scope

Started the next numbered application ticket, VIDEO-STATE-001. Its static-frame baselines can use the verified image encoder while another person repairs native video. The existing corpus remains a narrow within-apartment fixture; its weak graph/program labels will not be promoted to reviewed visual state labels.

### Prompt Context
**User prompt (verbatim):** "We have someone working on the MLX fix. In the meantime, do the next project. commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Implement Project 2 observable-state recognition with independent labels, measured baselines, explicit abstention, and evidence playback.

**Inferred user intent:** Make progress on the next application without duplicating the concurrent native-video repair.

### What I did
- Read the state and corpus-expansion guides, current adapter, cache, and existing diary.
- Asked an optional clarification about numbered Project 2 versus the recent corpus-diversification proposal; proceeded with the stated numbered-project interpretation after the initial review period.
- Selected four phases: reviewed labels, baselines, context/calibration, and evidence timeline.

### Why
- Static state recognition does not require native-video encoding, but it does require labels justified by visible pixels.

### What worked
- The existing registry, PTS decoder, model, and image feature path are available.

### What didn't work
- No implementation failures yet.

### What I learned
- The state ticket explicitly allows a small reviewed RGB subset while expanded corpus calibration remains separate.

### What was tricky to build
- Unknown physical state and poor observability are distinct fields. Manual visibility gating must remain an explicitly labelled diagnostic.

### What warrants a second pair of eyes
- Single AI-reviewer label provenance, sampling bias, near-duplicate evidence, and the boundary between static states and temporal transition claims.

### What should be done in the future
- Complete P1–P4 and preserve screenshots and raw-count results.

### Code review instructions
- Begin with this ticket's design guide and the completed search implementation.

### Technical details
- Starting source revision: `ebd1211`.
- Existing untracked MLX-VIDEO-FIX-001 ticket belongs to the concurrent workstream and is left untouched.

## Step 2: Defer state recognition in favor of corpus diversification

The user clarified that the next work should broaden training/testing situations instead of building on the existing repeated action/camera fixture. Stopped state implementation and switched to VIDEO-CORPUS-001. The 144 fixed-grid RGB samples and preparation script are preserved as preparatory work; no state labels, classifier, or completed-state claim was produced.

### Prompt Context
**User prompt (verbatim):** "actually, can we create a wider range of testing training data and situations? instead of that one action and camera thing?"

**Assistant interpretation:** Prioritize a varied VirtualHome corpus over Project 2 classification.

**Inferred user intent:** Make later model experiments discriminate actions, locations, and props rather than exploit repeated visual context.

### What I did
- Preserved review preparation and moved the untested label-schema draft into ticket scripts.
- Removed the newly created runtime package stub; no existing implementation was removed.
- Left all Project 2 implementation tasks open and moved execution to VIDEO-CORPUS-001.

### Why
- Better dataset variation is the user's current priority.

### What worked
- The fixed-grid export completed 144 samples from 24 videos without altering v1.

### What didn't work
- The initial interpretation of “next project” as numbered Project 2 did not match the clarified intent.

### What I learned
- Corpus diversification is the immediate dependency to address.

### What was tricky to build
- Preserve useful preparatory work without presenting an unreviewed label draft as an implemented classifier contract.

### What warrants a second pair of eyes
- No reviewed labels exist in this deferred subset yet.

### What should be done in the future
- Resume state recognition after the diversified corpus is available.

### Code review instructions
- Read the preparation script and this explicit scope-change entry; runtime state implementation remains open.

### Technical details
- Ignored preparation output: `output/state-workbench/review-v1`.
- Active implementation ticket: VIDEO-CORPUS-001.

## Step 3: Resume with a reviewed, apartment-separated RGB subset

Resumed the second numbered project after the diversified corpus was completed. Prepared and visually inspected 144 RGB frames from 24 appliance episodes, preserving all 24 native-resolution contact sheets in the ticket. Labels describe visible door geometry, with separate ambiguous and occluded unknowns. Simulator commands and graph states are not label truth.

The old microwave videos all belong to apartment 0, so this experiment assigns all of them to training rather than preserving their earlier within-apartment split. Development is apartment 1 and test is apartment 2. This prevents apartment leakage but leaves appliance and evaluation domain confounded; the experiment is an exploratory implementation check, not a generalization benchmark.

### Prompt Context
**User prompt (verbatim):** "Now continue on the second ticket."

**Assistant interpretation:** Resume VIDEO-STATE-001 implementation using the expanded corpus.

**Inferred user intent:** Progress from corpus generation to measurable, evidence-linked state recognition, preserving a detailed diary and screenshots.

### What I did
- Printed the resumed P1–P4 plan; service returned `printed: true`, HTTP 200, at `2026-09-06T19:34:03Z`.
- Selected six fixed relative timestamps per episode and verified video/image SHA-256 hashes.
- Reviewed 24 contact sheets at native resolution and froze 136 visible labels plus eight unknowns.
- Added strict label/observation contracts and source, entity, split, and label completeness validation.
- Saved the review codes, full manifests, class-count summary, and all contact sheets under `various/`.

### Why
- State recognition must distinguish false, unknown, and missing annotations. Independent source identity and group ownership prevent accidental reuse across splits.

### What worked
- `workbench/.venv/bin/python .../scripts/05-freeze-labels.py` validates all 144 rows and their source hashes.
- Training has 39 open / 56 closed / one ambiguous frame; development has two open / 22 closed; test has two open / 15 closed / seven unknown.

### What didn't work
- The corpus does not meet the proposed per-appliance class minimum: training has only four visibly open fridge frames. Adding nearby duplicate frames would inflate counts without adding independent situations.
- No independent second reviewer has adjudicated the labels; this is single-assistant RGB review.

### What I learned
- Several frames following microwave CLOSE remain visibly open. Left-camera actor occlusion prevents labeling parts of the test sequence.

### What was tricky to build
- Mixing the original corpus with the diversified release would leak apartment 0 if the old split were preserved. Explicit experiment-specific reassignment solves that without modifying either source release.
- Partial door motion can look like closed geometry at small scale. Conservatively retained ambiguous frames instead of inferring the action's intended outcome.

### What warrants a second pair of eyes
- Review all unknowns, partially visible doors, and the very small open-fridge subset. Development has no unknown examples and only two positives, limiting calibration.

### What should be done in the future
- Fit and evaluate frozen baselines with raw-count reporting and preserve the distinction between model abstention and an oracle visibility diagnostic.

### Code review instructions
- Start at `predicates/contracts.py`, then preparation/freezing scripts and `various/label-summary-v2.json`.
- Compare `review-codes-v2.json` with the corresponding six-panel sheets; C=closed, O=open, A=ambiguous, U=occluded.

### Technical details
- Sampling grid: 0, 20, 40, 60, 80, 100 percent of decoded frame indices; timestamps are actual MP4 presentation times in microseconds.
- Full-frame evidence remains 640×480; the existing image encoder will resize to 320×240. No crop is selected using model scores.
- Unrelated MLX repair and perception tickets remain untouched.
