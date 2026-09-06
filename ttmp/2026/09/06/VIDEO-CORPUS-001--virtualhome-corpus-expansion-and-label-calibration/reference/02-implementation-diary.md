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
    - Path: repo://src/virtualhome_corpus/diversity_review.py
      Note: Native transition evidence, world-state runs and split/duration diagnostics
    - Path: repo://src/virtualhome_corpus/diversity_runner.py
      Note: Attempt-preserving generator and media/source validation, commit 5867103
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

## Step 5: Verify RGB/graph disagreement during the release

The first two encoded fridge videos passed full decoding and per-frame source-hash validation. Native image inspection shows an open door during both trajectories, while every exported graph labels the target CLOSED. This confirms that the graph stream cannot supply dense visual door-state labels for this subset. Continued generation with the existing conservative annotation policy and expanded calibration review to include each entire action interval with neighboring frames.

### Prompt Context
**User prompt (verbatim):** (see Steps 1–2)

**Assistant interpretation:** Preserve technical findings and screenshots while completing the varied corpus.

**Inferred user intent:** Support an accurate future report and avoid training on incorrect automatic labels.

**Commit (code):** `5867103` — "Corpus: validate diverse household scenarios and add provenance-preserving exporter"

### What I did
- Validated both initial MP4s using full FFmpeg decoding and raw PNG/graph/source hashes.
- Inspected both fridge contact sheets and matched training-apartment pickup, sitting, and switching sheets.
- Saved matched comparison sheets under `various/screenshots/`.
- Added `docs/playbook/virtualhome-diversity.md` with commands, artifact contracts, observed exclusions, and evaluation limits.
- Started the remaining release recordings using the committed producer.

### Why
- More action diversity is useful only if metadata quality and nuisance factors are explicit.

### What worked
- RGB shows actual door opening/closing and terminal seated poses.
- All completed release recordings have passed export-time media checks.

### What didn't work
- Both first fridge graph streams contain only CLOSED despite visible opening. No graph transition exists from which to estimate a timing offset.
- The historical prompt referred to `docs/playbooks/*`; `rg --files docs/playbooks` returned `No such file or directory`. The actual directory is `docs/playbook/`, and the new playbook uses that location.
- `cat README.md` found no root README; the existing simulator/corpus playbooks are the entry points.

### What I learned
- A raw action interval can include preparatory pose or waiting, and a program's LOOKAT can export as TURNTO. Preserve raw rows rather than rename them to the intended verb.

### What was tricky to build
- A neighborhood around just the action endpoints can miss the visually informative movement. The review exporter now retains the complete OPEN/CLOSE interval and three neighboring frames on each side, at native resolution.

### What warrants a second pair of eyes
- Pickup props are small; TV screen state differs in observability by view. Dense state supervision remains disabled even where gross actor movement is visible.

### What should be done in the future
- Complete all apartments, audit duration confounds and source compatibility, then sign the per-subset visual review separately from raw exports.

### Code review instructions
- Compare `world-state-runs.json` with the fridge OPEN/CLOSE contact-sheet frames.
- Read the playbook's interpretation limits and inspect the matched review sheets.

### Technical details
- Initial fridge trajectories: 69 and 70 frames at 10 FPS.
- Annotations retain `precise_boundary_supervision_allowed: false` and `dense_visual_state_supervision_allowed: false`.

## Step 6: Preserve cross-bedroom scenarios and remove the duration shortcut

The first 40 recordings completed, then the exporter rejected the scene-2 bed scenario with `RuntimeError: Actor placed in wrong room`. Inspection showed that the actor was at the configured coordinates, in bedroom 358, while bed 296 is in bedroom 253. This was the exact successful probe start: the program legitimately walks between bedrooms. Replaced the overly strict same-room assumption with coordinate validation and explicit starting/target room metadata.

The full trajectories also have an obvious duration confound: interaction programs contain more actions than their controls. Added a separate two-second window exporter that retains the original videos and lineage. It selects the first target action, the terminal sitting interval, or the terminal control interval, with no padding and no split reassignment. These are weak program-conditioned windows, not exact visual action segments.

### Prompt Context
**User prompt (verbatim):** (see Steps 1–2)

**Assistant interpretation:** Complete varied situations, including legitimate travel between rooms, and provide a usable comparison set without length alone identifying the condition.

**Inferred user intent:** Improve discrimination of actions, props, and locations while keeping the corpus reproducible.

### What I did
- Preserved failed attempt 0001 for `dv-673fa0ed90d3c06a`, including a post-failure graph snapshot.
- Checked actual actor coordinates against the configured start; they differ only at floating-point precision.
- Added `placement_room`, requiring one initial room and horizontal coordinate error below 0.25 m.
- Added regression coverage for cross-room starts, coordinate drift, ambiguous room edges, window clamping, terminal SIT selection, and rejection of short sources rather than padding.
- All 18 corpus tests passed.

### Why
- Same-room insertion was an implementation assumption, not a requirement of the scenario. Changing the established configuration would invalidate the release identity; preserving the verified starting coordinates maintains the intended scenario.

### What worked
- Existing 40 videos remain immutable and valid.
- Placement checks now distinguish a legitimate different room from an actual incorrect insertion.

### What didn't work
- `PYTHONPATH=src output/virtualhome-install/.venv/bin/python -m virtualhome_corpus.diversity_runner generate` stopped at the same-room assertion after 40 successful episodes.
- The original inventory/probe recorded the target room but did not separately assert the actor's starting room. The release gate exposed that omission.

### What I learned
- Duplicate room class names require exact room IDs and coordinates. A route across rooms is useful variation when represented honestly.

### What was tricky to build
- The first 40 recordings use the earlier exporter hash; the remaining recordings will use the corrected placement validator. Every attempt retains its own exact producer hashes. The audit must report this producer split rather than claim a single identical exporter for all episodes.

### What warrants a second pair of eyes
- Compare actual start transforms across matched conditions, verify windows contain informative movement, and avoid treating program-conditioned crop selection as a natural untrimmed benchmark.

### What should be done in the future
- Resume the final eight recordings, build fixed-duration windows, and audit both datasets together.

### Code review instructions
- Review `placement_room` and its regression test, then `diversity_windows.select_window` and source hash checks.
- Failed attempt evidence lives under the original episode directory; no successful artifact was rewritten to conceal the failure.

### Technical details
- Configured bed-scenario start: `[1.98290539, 1.25, 1.5227592]`; observed: `[1.9829042, 1.25, 1.52275848]`.
- Starting room: 358; target room: 253.
- Fixed windows: 20 frames at 10 FPS, sourced directly from hashed PNGs.

## Step 7: Complete the release, calibration assessment, and report evidence

All 48 full trajectories completed after the placement-check correction, and all 48 equal-duration windows were encoded from verified original PNGs. The release contains 3,682 paired frames and 368.2 seconds of full video, plus 96 seconds of window video. Full media decoding, raw/source hash checks, split ownership, exact duplicate checks, and original-v1 preservation checks passed.

Reviewed all six appliance trajectories across complete action intervals, inspected native endpoint composites, and sampled every fixed window at its start, midpoint, and end. Preserved 50 evidence images, including actual browser captures, with a SHA-256 inventory. Wrote the release implementation/evidence reference and operational playbook for future report preparation.

### Prompt Context
**User prompt (verbatim):** (see Steps 1–2)

**Assistant interpretation:** Finish the broader corpus and preserve an auditable record of its useful coverage and remaining limitations.

**Inferred user intent:** Have training/testing material that supports meaningful follow-up experiments and a technically honest future report.

**Commit (code):** `e0fe884` — "Corpus: support verified cross-room starts and add equal-duration windows"

### What I did
- Completed 16 train, 16 development, and 16 test trajectories; each partition contains all four families and both conditions/views.
- Ran `python -m virtualhome_corpus.diversity_review` for full video/source validation, world-state runs, perceptual diagnostics, and native transition pages.
- Ran `python -m virtualhome_corpus.diversity_windows`; all 48 clips are exactly 20 frames at 10 FPS, with no padding.
- Ran ticket `scripts/10-final-audit.py` to check derivative provenance, split ownership, model-input keys, producer history, duration baseline, and original v1 hashes.
- Signed separate calibration and window visual assessments; raw annotations remain unchanged.
- Captured browser screenshots of the release overview, test apartment, and microwave evidence, and inspected the resulting screenshot.
- Printed the C2–C3-complete / C4-start slip and stopped the owned Unity session after generation.

### Why
- Simulator success, video integrity, visibility, and training-label eligibility are different claims. Each needs separate evidence.

### What worked
- All 96 MP4 files passed decoding and media checks.
- Zero cross-split lineage/group violations and zero exact video duplicates were found in the audited releases.
- The full-video perceptual diagnostic's nearest cross-split pair has mean Hamming distance 18/64; the method remains a limited diagnostic rather than an exhaustive duplicate detector.
- All 24 original videos and the original inputs manifest are unchanged.
- Nine conservative RGB transition brackets were recorded across the six appliance trajectories.

### What didn't work
- All six appliance graph streams retain CLOSED throughout, including visibly open fridge frames. Graph-to-RGB timing offsets cannot be estimated from missing graph transitions.
- Both microwave CLOSE sequences lack visibly confirmed closure; the door remains open in the reviewed post-action frames. Their CLOSE rows are excluded from visually confirmed closing evaluation.
- The left microwave opening is substantially occluded. Small pickup props and some device contact/state views also remain weak-only or partially occluded.
- One development door control contains a brief near-camera actor clipping/floating-hand artifact; its signed review excludes it from a visual benchmark.
- A train-fitted 5.7-second duration threshold scores 100% train, 100% development, and 75% test on full trajectories. This confirms a shortcut. Equal-duration windows remove that particular signal but retain program-conditioned selection and other context biases.

### What I learned
- More situations exposed simulator/export defects and evaluation shortcuts that the single-appliance setup could hide.
- A conservative release can be useful without claiming dense visual ground truth. Explicit exclusions are part of the dataset contract.

### What was tricky to build
- Rerunning the automated audit regenerates unsigned review templates. Kept signed assessments as separate versioned files with video hashes and repository-relative evidence bases, so tooling cannot silently overwrite reviewer judgments.
- Original and derived inputs use different relative-path bases. The playbook names both bases and keeps all evaluator metadata separate.

### What warrants a second pair of eyes
- Independently adjudicate visual brackets and ambiguous props before using them as gold labels. Inspect the flagged rendering artifact and program-conditioned cropping biases.
- Do not mix v1 evaluation with v2 training as unseen-apartment evaluation; both include apartment 0.

### What should be done in the future
- Use the fixed-window inputs for coarse action-discrimination experiments and report results by family/view.
- Keep exact boundary and dense state learning disabled until an independently reviewed subset supports stronger labels.
- Use the archived images, assessments, and commit-linked diary as the basis of the future technical report.

### Code review instructions
- Start with `reference/03-diverse-household-release-implementation-and-evidence.md` and `various/release-audit.json`.
- Inspect `various/screenshots/release-test-apartment-browser.png`, `release-calibration-browser.png`, and the per-family window sheets.
- Reproduce with the playbook commands; unit suite: `PYTHONPATH=src output/virtualhome-install/.venv/bin/python -m unittest discover -s tests -v` (18 passing tests).

### Technical details
- Full inputs: `output/virtualhome-corpus/diversity-v2/inputs.jsonl`.
- Window inputs: `output/virtualhome-corpus/diversity-v2/windows-v1/inputs.jsonl`.
- Evidence dashboard: `http://127.0.0.1:8770/release-gallery.html`; full gallery: `http://127.0.0.1:8771/gallery.html` while the local servers remain running.
- Producer history: 40 initial-exporter recordings and eight placement-fix recordings; one configuration and one installation variant.
- The single failed release attempt remains under `episodes/dv-673fa0ed90d3c06a/attempt-0001`.

- Final documentation check: `docmgr doctor --ticket VIDEO-CORPUS-001 --stale-after 30 --fail-on error` passed. Ticket closure generated a blank EOF line reported by `git diff --check`; normalized the changelog before staging.
