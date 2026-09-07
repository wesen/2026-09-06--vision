---
Title: FP32 native follow-up diary
Ticket: VIDEO-TEMPORAL-001
Status: complete
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
LastUpdated: 2026-09-06T20:21:56.172291-04:00
WhatFor: ""
WhenToUse: ""
---

# FP32 native follow-up diary

## Goal

Measure repaired native FP32 features on the frozen TEMPORAL benchmark, preserving the original pooled comparison and concurrent verifier work.

## Step 1: Freeze comparison and implement native extraction

The follow-up reopens TEMPORAL for a measured representation comparison. A separate producer retains the existing data-loader contract and audits actual source timestamps before encoding each trailing window with the accepted native adapter.

### Prompt Context

**User prompt (verbatim):** "ok, do fp32. › ok, add the tasks to the ticket and a design doc, then implement this. commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a         
  brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Add a native FP32 benchmark follow-up, implement it, measure it, and record progress.

**Inferred user intent:** Establish whether the repaired representation improves the temporal baseline before relying on pooled results.

### What I did
- Added design document 02, four follow-up tasks, and this separate diary.
- Added `workbench/src/video_workbench/temporal/encode_native.py`, reusing the existing NPZ contract and accepted native adapter.
- Launched an eight-window pilot with the isolated repaired interpreter and offline model loading.
- Saved the phase plan locally using the brutalist-work-slip script.

### Why
- Exact window identity permits a paired comparison; fresh features and trained heads prevent mixing incompatible feature spaces.

### What worked
- Eight-window native pilot passed: {"wall_seconds": 8.743343333015218, "load_seconds": 6.31398820807226, "pixel_probe": {"sample_id": "988bed041b8cf1b2b9761f0d", "black_cosine": 0.4544495642185211, "max_abs_difference": 0.2967677116394043}}
- Located frozen inputs, original ridge/TCN artifacts, and native runtime pins.
- Kept shared training modules and main-thread VERIFY files unchanged.

### What didn't work
- Sandboxed pilot failed: `ImportError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.` Re-running with authorized GPU access passed.
- Automatic approval review rejected sending plan metadata to the external Almanach service because this side conversation had not explicitly authorized that destination and payload. Explicit destination approval is pending; local layouts are retained.
- `ps` failed with `zsh:1: operation not permitted: ps`; no process-inspection escalation attempted.
- Initial read used `temporal/encode.py` instead of the package path and returned `No such file or directory`; corrected to `workbench/src/video_workbench/temporal/encode.py`.

### What I learned
- Existing TCN report prose hardcodes pooled features; only the new run report must be annotated after using the unchanged trainer.

### What was tricky to build
- Native windows must carry actual selected PTS, including early odd-frame windows. The accepted adapter handles padding; extraction preserves the original source indices and rejects timestamp drift.

### What warrants a second pair of eyes
- Representation, precision, and preprocessing change together in this comparison. A gain cannot establish that temporal ordering caused it.

### What should be done in the future
- Extract 792 windows, train and compare with frozen selection policies.

### Code review instructions
- Read design document 02, then `encode_native.encode`; inspect manifest hashes and source audits.
- Pilot command: `PYTHONPATH=workbench/src HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 output/mlx-video-fix/.venv/bin/python -m video_workbench.temporal.encode_native output/temporal-v1/dataset output/temporal-native-fp32-v1/pilot --limit 8`.

### Technical details
- Features are 2048-dimensional float32 unit vectors, with a validity mask and ordered sample IDs.
- The producer never opens weak labels. A black-pixel intervention checks sensitivity, not semantic quality.
