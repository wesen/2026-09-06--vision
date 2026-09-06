---
Title: Implementation diary
Ticket: VIDEO-CORPUS-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://configs/virtualhome-diversity-v2.json
      Note: Proposed bindings awaiting capability validation
    - Path: repo://src/virtualhome_corpus/diversity.py
      Note: Matched scenario planner and typed action programs
    - Path: repo://ttmp/2026/09/06/VIDEO-CORPUS-001--virtualhome-corpus-expansion-and-label-calibration/various/probe-gallery.html
      Note: Visual evidence from successful and failed probes
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T14:38:18.621682-04:00
WhatFor: ""
WhenToUse: ""
---


# Implementation diary

## Step 1: Diversify data before state classification

The user clarified that the immediate objective is a wider range of training/testing situations, actions, props, and views. Switched from the numbered state-recognition project to this corpus-expansion ticket. The existing 24-video corpus remains immutable; probes use a separate owned simulator on port 18082 and a separate output directory.

### Prompt Context
**User prompt (verbatim):** "We have someone working on the MLX fix. In the meantime, do the next project. commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**User prompt (verbatim):** "actually, can we create a wider range of testing training data and situations? instead of that one action and camera thing?"

**Assistant interpretation:** Build a separately versioned, substantially varied VirtualHome corpus with source provenance, matched controls, and preassigned grouped splits.

**Inferred user intent:** Make subsequent models distinguish actions and situations rather than memorizing one recurring camera/appliance sequence.

### What I did
- Read the corpus-expansion guide, existing exporter, and installed simulator client.
- Preserved the deferred state-preparation work in commit `90f80df`.
- Launched an owned graphics-enabled simulator on port 18082 and started inventory probes for scenes 0, 1, and 2.
- Printed the revised C1–C4 plan and C1-start slip.

### Why
- The simulator must prove that proposed props, actions, and camera placements work before batch generation.

### What worked
- Existing generator helpers and a pinned native simulator installation are available.

### What didn't work
- No simulator-probe failures yet. The earlier state-project interpretation was superseded by the user clarification.

### What I learned
- The installed reset API documents seven apartment indices; this release will probe three instead of assuming their contents.

### What was tricky to build
- Variation must be crossed with actions, not simply assign a different action to each scene or camera. Related variants and views must remain in one split.

### What warrants a second pair of eyes
- Camera visibility, action execution, exact and perceptual duplicate diagnostics, and label quality.

### What should be done in the future
- Complete capability probes, transition review, matched generation, and final audit.

### Code review instructions
- Read `scripts/02-probe-scene-inventory.py` and the preserved v1 hash inventory.

### Technical details
- Active output: `output/virtualhome-corpus/diversity-probes`.
- Planned initial bound: at most 48 new episodes after capability validation.
- No embedding-runtime edits are required for this work.

## Step 2: Preserve failed probes and visual evidence

Three apartment inventories loaded, and the proposed configuration crosses four interaction families with two conditions and two camera views in each apartment. The first execution sweep proved that inventory affordances alone do not establish executable or visually useful scenarios. Saved both camera captures from completed probes and a review gallery, including failures, for the future report.

### Prompt Context
**User prompt (verbatim):** "don't forget to write a diary and keep screenshots for a future report."

**Assistant interpretation:** Preserve a chronological implementation record and actual visual evidence throughout generation and debugging.

**Inferred user intent:** Make the future technical report reproducible and honest about simulator limitations.

### What I did
- Added a separate schema-v2 scenario planner and four unit tests; all 14 corpus tests passed.
- Verified all 24 original video hashes and preserved their inventory.
- Recorded three scene inventories, action programs, camera transforms, results, and native 640×480 camera images.
- Created `various/probe-gallery.html` and copied completed probe captures into the ticket's `various/screenshots/` folder.
- Interrupted the owned probe process and simulator after the sofa sequence exceeded the client timeout and continued exporting thousands of frames.

### Why
- Failed examples must not silently enter the training release. Inventory support does not guarantee navigation, animation completion, or visible state change.

### What worked
- Scene 0 fridge OPEN/CLOSE and TV SWITCHON/SWITCHOFF programs reported success.
- The initial planner gives 48 distinct episode IDs and keeps related conditions/views in a single apartment split.

### What didn't work
- `PYTHONPATH=src output/virtualhome-install/.venv/bin/python .../scripts/03-probe-actions-and-cameras.py` produced `ScriptExcutor 0: EXECUTION_GENERAL: Script is impossible to execute` for mug and book pickup programs.
- Chair 110 and cabinet 233 failed with `PROCESS WALK: Can not select object: chair. REASON: Unknown` and the corresponding cabinet error.
- Sofa 301 produced `UnityCommunicationException("HTTPConnectionPool(host='127.0.0.1', port=18082): Read timed out. (read timeout=180)")`; recording was still progressing after the timeout. This is a failed probe, not a completed episode.
- A sandboxed process inspection returned `zsh:1: operation not permitted: ps`; owned execution sessions were stopped directly instead.

### What I learned
- Action-level probes need bounded execution and isolated evidence directories. Whole-program failures do not identify the failing primitive.

### What was tricky to build
- A simulator request timeout does not stop the Unity action or recording. Continuing with reset requests would mix subsequent probes with a still-running action. Stopped both owned sessions before further probing.

### What warrants a second pair of eyes
- Camera occlusion and whether successful graph state changes have visible RGB evidence; the TV final frame does not by itself prove the complete transition.

### What should be done in the future
- Diagnose individual actions, replace inaccessible targets, and verify both views before generating the release.

### Code review instructions
- Compare `various/action-camera-probes.json` with the labeled gallery and planner configuration.
- Run `PYTHONPATH=src output/virtualhome-install/.venv/bin/python -m unittest discover -s tests -v`.

### Technical details
- Probe images are actual simulator captures, not generated illustrations. Browser screenshots of the review page are retained separately.
- The original v1 corpus and the independently maintained MLX repair are untouched.

## Step 3: Isolate action-sequence failures

Single-primitive probes narrowed the pickup failure to the return operation. A minimal WALK/GRAB/PUTOBJBACK sequence succeeded, while the longer sequence containing LOOKAT after GRAB failed in a subsequent recorded run. Sitting itself succeeded without recording, but the extended seated sequence failed or stalled. The next probe uses terminal SIT and a minimal pickup/return sequence; these remain candidate programs until recording succeeds.

### Prompt Context
**User prompt (verbatim):** (see Steps 1–2)

**Assistant interpretation:** Keep pursuing varied, executable household scenarios while preserving the investigation and screenshots.

**Inferred user intent:** Obtain usable training data with a defensible account of how it was generated.

**Commit (code):** `de014ed` — "Corpus: plan matched diversity release and preserve capability probe evidence"

### What I did
- Committed the initial planner and evidence milestone.
- Probed WALK, LOOKAT, GRAB, PUTBACK, SIT individually using `/tmp/probe-primitives.py` with a 30-second client timeout and unrecorded animation at time scale 5.
- Replaced the inaccessible scene-0 chair with sofa 375 and scene-1 cabinet with fridge 155.
- Ran a second recorded sweep in its own directory and stopped at its first exception.
- Began a separate expansion runner with immutable configurations, attempt history, source hashes, fixed lineage initialization, and model-safe exports.

### Why
- A full program can fail after earlier actions changed the world; successful individual commands do not establish that their composition works.

### What worked
- Minimal `<char0> [Walk] <mug> (454)`, `[Grab]`, `[PutObjBack]` reported success.
- WALK and SIT on sofa 375 individually reported success.
- The generator reuses the existing media/action parser without changing the v1 producer files.

### What didn't work
- PUTBACK reported `ScriptExcutor 0: EXECUTION_GENERAL: Script is impossible to execute`.
- PUTOBJBACK after the longer recorded sequence reported `PROCESS PUTBACK: Object mug not grabbed`.
- LOOKAT on the sofa while seated reported `EXECUTION_GENERAL: Script is impossible to execute`.
- The revised recorded posture program exceeded `Read timed out. (read timeout=60)`. Stopped the owned simulator session rather than continue queueing commands.

### What I learned
- PUTOBJBACK and PUTBACK are materially different simulator operations. Terminal sitting is a useful positive example even if stand-up sequences cannot be validated in this build.

### What was tricky to build
- Recording and command composition expose behavior that isolated unrecorded primitives do not. The release must be validated in its actual recording mode, with full programs and final camera views.

### What warrants a second pair of eyes
- Graph holding relations after pickup, visible sitting, and pose/camera differences across matched episodes.

### What should be done in the future
- Finish minimal recorded probes before batch generation; preserve unsupported sequences as explicit exclusions.

### Code review instructions
- Compare the revised programs in `src/virtualhome_corpus/diversity.py` with both probe result files.
- Review `diversity_runner.py` for timeout handling and separation of evaluator metadata from model inputs.

### Technical details
- A second sweep lives in `output/virtualhome-corpus/diversity-probes-r2`; it does not overwrite initial evidence.
- The first complete release is still pending. No failed probe has been published as training data.

## Step 4: Freeze executable scenarios and start recording

The third recorded sweep completed all twelve minimal programs. Camera review then rejected two otherwise executable bindings: a fridge occluded the scene-1 light switch and scene-2 chair. The accepted replacements are scene-1 TV 313 and scene-2 bed 296. Both replacement views were inspected at native resolution. The release now spans kitchens, living rooms, and bedrooms, with two appliance types, three pickup props, sofas/bed, and TVs/lamp.

### Prompt Context
**User prompt (verbatim):** (see Steps 1–2)

**Assistant interpretation:** Generate the wider release only after empirical action and visual checks, with evidence suitable for a future report.

**Inferred user intent:** Make action recognition experiments less dependent on one appliance and one repeated viewpoint.

### What I did
- Saved accepted capabilities separately from all rejected probe attempts.
- Captured three scenario overview sheets plus native replacement views.
- Froze each scenario's verified actor position in the versioned configuration.
- Printed the combined C1-complete / C2–C3-start milestone slip.
- Started two release recordings to exercise media encoding, per-frame source hashing, and export validation.

### Why
- Camera visibility is a separate acceptance criterion from simulator success. Fixed positions keep condition and view pairs comparable without claiming deterministic animation.

### What worked
- Minimal pickup/return and terminal sitting executed in all three apartments.
- The scene-2 bed gives a visible seated pose from both views.
- Scene-1 TV is visible from both views and its program succeeds.

### What didn't work
- Scene-1 lamp 272, proposed as a replacement, failed with `PROCESS WATCH: Can not select object to watch: tablelamp`.
- Light switch 82 and chair 163 were executable but visually unsuitable due to fridge occlusion. They remain excluded from the release.

### What I learned
- A useful corpus needs separate execution, camera, label, and split checks. Inventory affordances are only the first filter.

### What was tricky to build
- Related conditions must use the same starting position, but simulator insertion can choose a different location on each reset. Copied the successful probe position into each scenario; the runner additionally checks the actor's room edge and records its actual transform.

### What warrants a second pair of eyes
- Small pickup props and actor occlusion still limit fine state labels. Successful action programs only provide weak labels until their visual transitions are reviewed.

### What should be done in the future
- Validate the first encoded episodes, commit the exporter milestone, then finish the 48-video batch and audit.

### Code review instructions
- Read `various/accepted-capabilities.json`, the revised configuration, and `diversity_runner.generate`.
- Inspect `various/screenshots/revised-scene-*-overview.jpg`; these deliberately include the two subsequently rejected camera cases.

### Technical details
- Planned factors: 3 apartments × 4 families × 2 conditions × 2 views = 48 episodes.
- Partition assignment: scene 0 train, scene 1 development, scene 2 test. This is a small scene-held-out experiment, not a broad generalization benchmark.
- Recording: 640×480 at 10 FPS. Full trajectory durations are retained and are not matched between conditions.
