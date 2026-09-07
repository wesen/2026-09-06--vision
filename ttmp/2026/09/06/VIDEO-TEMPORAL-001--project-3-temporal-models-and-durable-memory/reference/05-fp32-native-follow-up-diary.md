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
    - Path: repo://docs/playbooks/temporal-native-fp32.md
      Note: Standalone operational guide with validated inspection command
    - Path: repo://ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/reference/06-native-fp32-temporal-benchmark-measured-findings.md
      Note: Measured findings and experiment limits
    - Path: repo://ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/various/native-fp32-v1/results.json
      Note: Paired result evidence
    - Path: repo://ttmp/2026/09/06/VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/various/native-fp32-v1/smoke.json
      Note: Final artifact and causality verification
    - Path: repo://workbench/README.md
      Note: Native setup section links to the playbook
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

**Commit (code):** `8e59d45` — "temporal: extract native FP32 cache and add matched head comparison"

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

## Step 3: Complete head comparison, smoke validation, and measured report

Native ridge reaches 24.55% test macro recall versus 21.16% pooled, while native TCN averages 24.31% versus 18.63% pooled. These are improvements in this frozen experiment; native TCN still does not exceed native ridge on its mean and its seed spread is substantially larger.

The report explains the precision/preprocessing confound, weak labels, class imbalance, paired prediction changes, and causal checks. Tracked evidence includes per-class results, selected predictions, hashes, manifests, an SVG figure, and its visually inspected PNG rendering. Full feature vectors and weights remain in the local output directory.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish the comparison and preserve reviewable evidence with focused commits.

**Inferred user intent:** Decide how much confidence to place in the repaired native path before further engineering.

### What I did
- Completed fresh ridge selection and all six TCN training runs using unchanged routines.
- Published reference document 06 and archived comparison results, manifests, TCN results, and ridge results without large weight arrays.
- Ran a final artifact smoke check; saved `various/native-fp32-v1/smoke.json`.
- Rendered the comparison SVG with `rsvg-convert` and visually inspected the PNG for legibility.
- Saved phase-transition and completion slip layouts locally.

### Why
- All three selected seeds and per-class counts are necessary to avoid overstating a favorable aggregate or a favorable seed.

### What worked
- Exact matched population: 792 windows, 48 episodes, 308 supervised test positions.
- All six checkpoint hashes and preserved pooled source hashes verified.
- Largest streamed-versus-full logit error: 0.0000105947; largest future perturbation error: zero.
- Pilot cache rejected by the full population loader.
- Ruff and whitespace checks passed on the completed changes.

### What didn't work
- No selected native head correctly classifies CLOSE, GRAB, PUTBACK, or TURNTO test examples. Native ridge SWITCHOFF recall regresses to zero.
- External Almanach printing remains blocked pending explicit destination/payload approval; local layouts are not physical receipts.

### What I learned
- Better native features do not yet establish a reason to prefer a TCN over the simpler native ridge head.
- Seed 17 gains macro recall while losing accuracy; minority-class improvements coexist with additional WALK errors.

### What was tricky to build
- The unchanged trainer's pooled-description field was misleading for new features. The follow-up annotates only its new result document; algorithm hashes and model-selection policy are retained.
- Sparse action support makes apparently large recall changes correspond to only one or two examples. The report includes counts alongside aggregate values.

### What warrants a second pair of eyes
- Interpret these as a system comparison, not an isolated test of temporal ordering. Check the changed predictions and development-selected checkpoints rather than picking the best test seed.

### What should be done in the future
- Print the saved layouts once explicit Almanach destination approval arrives. No additional experiment was silently added to this follow-up.

### Code review instructions
- Start with reference document 06 and `various/native-fp32-v1/results.json`.
- Inspect `smoke.json`, six candidate checkpoint hashes, per-class counts, and the unchanged training algorithm source hashes.
- Reproduction commands are in the findings document and require fresh output destinations.

### Technical details
- Native TCN seed macro recalls: 0.1739759, 0.2721938, 0.2831727; mean 0.2431141, standard deviation 0.0490931.
- Ridge paired outcomes: 230 both correct, 24 native corrected, 4 native worsened, 50 both wrong.
- Six native training loops total 9.027 seconds; extraction took 199.086 seconds. These measure separate operations, not complete end-to-end project duration.

## Step 4: Print approved slips and close the follow-up

The user explicitly approved printing after the destination blocker was explained. All five saved plan and phase slips received successful printed responses from Almanach and the printer. The final slip now points to the implementer handoff.

### Prompt Context

**User prompt (verbatim):** "print. also, give me a paragraph or two to give to our main implementer about the work you did."

**Assistant interpretation:** Print the queued slips and provide a concise implementation handoff.

**Inferred user intent:** Complete the physical record and transfer the experimental findings to ongoing work.

### What I did
- Printed the plan, three phase-transition slips, and final completion slip sequentially.
- Archived five responses in `various/native-print-receipts.json` and closed the remaining task.

### Why
- Explicit approval resolved the earlier external-destination blocker.

### What worked
- Every response reported `printed: true`, HTTP 200, and printer `ok: true`.

### What didn't work
- N/A; no print retries were necessary.

### What I learned
- The saved layouts could be printed directly after approval without repeating experimental work.

### What was tricky to build
- The completion layout contained the stale printing-blocker text; regenerated it through the skill script before printing.

### What warrants a second pair of eyes
- N/A.

### What should be done in the future
- Use the measured results and preserved feature-space boundaries in subsequent implementation.

### Code review instructions
- Inspect the five archived print responses and the completed task list.

### Technical details
- Destination: `https://almanach.crib.scapegoat.dev/api/render-and-print`.
- Experiment commits: `176a300`, `8e59d45`, `209cea4`; no experiment code changed in this printing step.

## Step 5: Defer the 8B embedding experiment

Recorded a separate 8B native embedding proposal and four explicitly deferred tasks. No weights, feature caches, or heads were changed. The completed native 2B FP32 comparison remains the measured reference while active work returns to the 8B generative verifiers in COSMOS-VERIFY.

### Prompt Context
**User prompt (verbatim):** "ok, add notes and tasks but mark them for later, then go back to the 8B reasoning models"

**Assistant interpretation:** Preserve the larger embedding idea without executing it now; resume the separate reasoning experiment.

**Inferred user intent:** Keep the roadmap precise and avoid confusing representation changes with verifier capacity changes.

### What I did
- Added `design-doc/03-deferred-8b-native-embedding-comparison.md` and tasks LATER E8-1 through E8-4.
- Read the colleague's native FP32 measured report and retained its exact comparison population and precision caveats.

### Why
- Embedding-8B would require new vectors and newly trained heads. It is not an interchangeable checkpoint for the generative verifier.

### What worked
- The deferred proposal preserves the 792-window population, training policy, and separate artifact identities.

### What didn't work
- N/A; no runtime experiment was attempted.

### What I learned
- Default output dimensions differ: 4096 for 8B versus 2048 for 2B. Matching dimensions would still not make feature spaces compatible.

### What was tricky to build
- The completed ticket now contains future tasks, so each task and the new note explicitly say later; this does not reopen the completed 2B acceptance claim.

### What warrants a second pair of eyes
- Future FP32 memory requirements and any assumptions that the repaired adapter supports the larger architecture unchanged.

### What should be done in the future
- Run the bounded pilot and matched comparison only when this work is scheduled.

### Code review instructions
- Review the new design note and the final deferred section in tasks.md. No model execution or tests are needed for this scheduling change.

### Technical details
- Candidate: `Qwen/Qwen3-VL-Embedding-8B`.
- Existing producer and comparison: `temporal/encode_native.py`, `temporal/native_compare.py`.
- Existing reference commits: `176a300`, `8e59d45`, `209cea4`.

## Step 5: Publish a runnable native comparison playbook

Created `docs/playbooks/temporal-native-fp32.md` to collect the runtime prerequisites, frozen-data checks, optional pilot, full extraction, head training, result inspection, and failure recovery. Linked it from the workbench README and ticket index so operators can find it without reading the experiment history.

### Prompt Context

**User prompt (verbatim):** "Ok, create playbook"

**Additional user prompt (verbatim):** "and commit"

**Assistant interpretation:** Publish and commit a standalone operational guide.

**Inferred user intent:** Make the completed experiment easy for another implementer to reproduce and inspect.

### What I did
- Added commands using a fresh run destination and the two existing isolated interpreters.
- Documented incomplete-run recovery, expected artifacts, measured timings, and interpretation limits.
- Validated local links, all shell blocks with `bash -n`, and embedded Python with `compile`.
- Executed the documented final inspection command on the existing v1 artifacts.

### Why
- The previous reproduction section lacked a complete operator sequence and explicit recovery instructions.

### What worked
- The documented inspection passed population, feature/result/checkpoint hash, preserved pooled source, and causal checks.
- All playbook links resolve and all command snippets are syntactically valid.

### What didn't work
- No execution failures. An initially incorrect ticket-relative link was corrected before validation and commit.

### What I learned
- A completed run can be checked without loading the native model or repeating training.

### What was tricky to build
- Extraction permits a pilot alongside a fresh full cache, but comparison rejects any existing head-output directories. The playbook distinguishes these destination requirements and documents copying completed features into a new run root after training interruption.

### What warrants a second pair of eyes
- Ignored local videos, weights, and dataset artifacts are prerequisites; a clone alone is insufficient.

### What should be done in the future
- N/A.

### Code review instructions
- Read the playbook from prerequisites through inspection, then follow its links to the producer and comparison implementation.
- GPU extraction and training were not rerun for this documentation change.

### Technical details
- The example new destination is `output/temporal-native-fp32-v2`; existing-run inspection uses v1 only.
