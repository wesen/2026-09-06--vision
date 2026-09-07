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
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/native_video.py
      Note: Accepted official FP32 runtime and preprocessing gates
    - Path: repo://workbench/src/video_workbench/temporal/benchmark.py
      Note: Frozen identity joins and ridge selection
    - Path: repo://workbench/src/video_workbench/temporal/encode_native.py
      Note: Audited native extraction committed in 176a300
    - Path: repo://workbench/src/video_workbench/temporal/native_compare.py
      Note: Paired comparison smoke-tested for outcome accounting and timestamp mismatch rejection
    - Path: repo://workbench/src/video_workbench/temporal/train.py
      Note: Unchanged six-run head training policy
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

**Commit (code):** `176a300` — "temporal: add audited native FP32 extraction and comparison design"

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
- `ruff format ...` initially failed through pyenv: `pyenv: ruff: command not found`. Selecting the installed tool with `PYENV_VERSION=3.11.4 ruff format ...` succeeded.
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

## Step 2: Extract the complete native cache and implement paired comparison

The full extraction completed with 792 windows across 48 episodes. Runtime was 199.086 seconds including 5.934 seconds of model loading; peak MLX allocation was 9,611,490,824 bytes. All original source hashes and native timestamp mappings passed the producer's checks.

The separate comparison runner calls the existing ridge and TCN routines and records corrected/worsened predictions only after matching supervision populations. It annotates the new TCN report's representation description without changing the trainer or any old artifact.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Complete the frozen-data native comparison with fresh heads and measured results.

**Inferred user intent:** Obtain experimental evidence rather than extrapolating from repair parity.

### What I did
- Ran the full native producer into `output/temporal-native-fp32-v1/features`.
- Archived complete and pilot manifests under `various/native-fp32-v1`.
- Implemented `native_compare.py` and launched ridge plus six CPU TCN runs.
- Saved the N2 completion/N3 start slip locally.

### Why
- Existing pooled checkpoints are incompatible with the new representation. Identical selection policies make a system comparison interpretable.

### What worked
- Every source audit passed; all valid vectors are finite and unit-normalized.
- Pilot frame counts were `[1,2,3,4,4,4,4,4]`.
- `PYENV_VERSION=3.11.4 ruff check` passed on both new modules.
- Inline comparison smoke passed: one corrected and one worsened prediction counted correctly; changed timestamps raised `ValueError`.

### What didn't work
- Physical slips remain pending explicit approval of the external printing destination. No rendering request was sent after rejection.

### What I learned
- Actual extraction was about 3 minutes 19 seconds on this machine, substantially below the preliminary 5–15 minute estimate.
- MLX allocator peak and macOS process RSS are distinct measures; neither should be described as total system memory use.

### What was tricky to build
- Old ridge and TCN reports encode validity slightly differently. Paired joins require exact label masks, timestamps, targets, and compatible valid masks before evaluating changed outcomes.

### What warrants a second pair of eyes
- Check the native source audit and preserved pooled source hashes. Check architecture selection remains development-only even when selected architectures differ between representations.

### What should be done in the future
- Finish training, inspect class-level results, publish findings, and close the follow-up after recording any remaining print blocker.

### Code review instructions
- Review `native_compare.paired` and `native_compare.run`.
- Reproduce with `PYTHONPATH=workbench/src workbench/perception-env/.venv/bin/python -m video_workbench.temporal.native_compare output/temporal-v1/dataset output/temporal-native-fp32-v1 output/temporal-v1` in fresh training destinations.

### Technical details
- Full feature NPZ SHA: `d646bacbd17abfee891388019aff8c35cfbba74784755ef6fa8e88068d3a5a26`.
- Native feature-space ID: `3292df2cb67f9a384041d24493084bf80a6945e5fb5ce0177a0d551e504b8ef4`.
- macOS process peak RSS: 5,372,346,368 bytes. Per-call timings and source audits are retained in the feature manifest.
