---
Title: VirtualHome corpus implementation diary
Ticket: COSMOS-VIDEO-001
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
LastUpdated: 2026-09-06T12:33:35.392573-04:00
WhatFor: ""
WhenToUse: ""
---

# Diary

## Goal

Implement and generate a reproducible VirtualHome household corpus from the local playbook, with honest annotation contracts, tests, commits, and phase print receipts.

## Step 1: Verify the installed simulator, actions, and cameras

Read the local playbook and launched an owned simulator on port 18081. Probed household action sequences and inspected rendered images and graph state exports before choosing the dataset families.

Automatic cameras and raw action exports exposed limitations that materially changed the design. Selected fridge and microwave door routines with a fixed kitchen camera, rather than assuming TV and faucet execution success produced useful state-recognition video.

### Prompt Context

**User prompt (verbatim):** "Use docs/playbooks/* to generate training corpus using virtualhome, you are welcome to adjust the test scenarios to a more "home" based scenario."

**User prompt (verbatim):** "Implement, commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill), Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Build a tested generation workflow, produce local training assets, validate them, and preserve the implementation trail.

**Inferred user intent:** Move from research into usable data for the embedding and procedural-video experiments.

### What I did

- Located `docs/playbook/virtualhome-video-generation.md` (singular directory).
- Printed the corpus plan and C1 start slips through the previously approved Almanach service.
- Launched the installed ARM64 simulator with graphics, an isolated log, and port 18081 via `scripts/07-launch-corpus-simulator.py`.
- Probed fridge, TV, faucet, and microwave programs using `scripts/08-probe-home-actions.py`.
- Tested fixed cameras with `scripts/09-probe-fixed-cameras.py`.

### Why

- Resetting another session's simulator would invalidate its state; the new process and port establish ownership.
- Successful execution does not prove visual evidence quality or annotation timing semantics.

### What worked

- Readiness and scene reset succeeded; scene 0 has a kitchen fridge, microwave, faucet, and a living-room TV.
- Fridge, TV, and faucet programs reported successful execution.
- An open-only fridge program ended with graph state OPEN and a visibly open door.
- Lowering the fixed kitchen camera removed a hanging-lamp obstruction.
- Corpus plan receipt: HTTP 200, printed true, 384 x 461 at 2026-09-06T16:31:08Z.
- C1 start receipt: HTTP 200, printed true, 384 x 331 at 2026-09-06T16:31:22Z.

### What didn't work

- AUTO faucet views were extreme close-ups without useful actor/state evidence. TV cutaways obscured the relevant screen.
- The full fridge open-close pilot's per-frame graph remained CLOSED throughout, despite an independently verified open-only endpoint. Thus intermediate graph state is not treated as exact visual state timing.
- Raw TV and faucet action exports inserted extra WALK rows with repeated source-program indices. A one-row-per-source-action assumption would be incorrect.
- A process-status check was blocked with `zsh:1: operation not permitted: ps`; no process termination or ownership changes followed.

### What I learned

- Graph capture phase and action endpoint convention remain unverified.
- Conservative action interiors can be exported as weak supervision while retaining raw rows and excluding boundary frames.

### What was tricky to build

- The original fridge sequence changed state too briefly to expose a reliable intermediate observation. The planned routines add a walk to the neighboring appliance before closing, preserving a visible open interval.
- Fixed camera configuration must be checked visually; plausible coordinates initially placed a lamp in front of the fridge.

### What warrants a second pair of eyes

- Do not train precise boundary/state-transition models from the raw export without resolving capture semantics.
- The scene is shared across splits; these splits measure within-scene variation, not unseen-home generalization.

### What should be done in the future

- Implement atomic manifests, grouped splits, frame validation, weak action annotations, endpoint rule checks, and resumable generation.

### Code review instructions

- Start with the playbook and the three ticket probe/launcher scripts.
- Inspect pilot contact sheets and raw `ftaa_episode.txt` rows in `output/virtualhome-corpus/pilots/`.

### Technical details

- Installation client revision: 122d3b0aee04768d988e02929f6eeeb38f2f28a8.
- Simulator release: Door_Modified_Build_2023_0404.
- RGB: 640 x 480, 10 FPS, paired graph export per frame.

## Step 2: Implement a resumable corpus exporter

Implemented the configured 24-episode household corpus as a Python package with explicit simulator ownership, immutable run provenance, separate model inputs and evaluator labels, and validation of every recording. A one-episode integration run produced 183 matching RGB/graph frames and an 18.3-second MP4; visual inspection of its contact sheet shows the fridge opening, remaining open during a detour, and closing before departure.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Turn the tested household routines into a reproducible, inspectable generation workflow.

**Inferred user intent:** Obtain usable local training assets and a clear implementation trail.

### What I did
- Added `configs/virtualhome-household-v1.json`, `src/virtualhome_corpus`, ten unit tests, and the corpus playbook.
- Ran `PYTHONPATH=src output/virtualhome-install/.venv/bin/python -m unittest discover -s tests -v`: all ten passed.
- Ran `PYTHONPATH=src output/virtualhome-install/.venv/bin/python -m virtualhome_corpus generate --port 18081 --output output/virtualhome-corpus/generator-smoke --limit 1`: completed in 25.809 seconds.
- Inspected the resulting contact sheet; door and actor are visible with the fixed camera.

### Why
- Retained failed attempts and immutable provenance make reruns auditable; split groups keep related variants together.
- Opaque video paths and separate label files avoid giving the model intended outcomes through filenames.

### What worked
- Fixed camera ID 103 rendered stream 0 successfully; all 183 images had corresponding graphs.
- Final graph confirms CLOSED and actor arrival in the living room.

### What didn't work
- No implementation test or integration failure occurred in this step. After context recovery, polling the finished tool session returned `write_stdin failed: Unknown process id 37448`; the persisted complete manifest supplied the result.

### What I learned
- The neighboring-appliance detour makes intermediate door state visibly persist in sampled frames.

### What was tricky to build
- Unity inserts WALK rows and repeats program indices. The parser preserves them and validates frame bounds rather than assuming one row per source instruction.
- Exported action endpoints and graph capture phase are unverified. Two-frame interior trimming is only weak supervision; precise timing and dense visual-state supervision remain disabled.

### What warrants a second pair of eyes
- Whether these weak action interiors are suitable for a particular downstream loss function.
- Camera visibility across every remaining variant; the smoke only establishes one case.

### What should be done in the future
- Render all 24 episodes, inspect representative action/final frames, and run deep validation.

### Code review instructions
- Start with `core.py` program construction, interval parsing, and endpoint rule; then inspect `runner.py` provenance, attempt lifecycle, and input/label separation.
- Run the test command above; follow `docs/playbook/virtualhome-corpus.md` for generation.

### Technical details
- Configuration SHA-256: `da29d6e35a5b2c716c1a7e868b56a1cc9b349fd3ea3ed8fe4cff09ebdf4d6360`.
- Smoke video SHA-256: `404bead46cb4bc3b3b6379ca4e4ffd7546261b07b8ac64f35606b7d59892d416`.
- Prior C1 implementation commit: `d005b3f`.
