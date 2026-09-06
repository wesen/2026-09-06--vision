---
Title: Investigation and delivery diary
Ticket: MLX-VIDEO-FIX-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/scripts/03-deliver-guide.py
      Note: Repeatable source-hash-gated render and upload workflow
    - Path: repo://ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/scripts/04-review-pdf.py
      Note: Raster review and page-count evidence
    - Path: repo://ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/various/pdf-validation.json
      Note: Reviewed guide identity and preview archive
    - Path: repo://workbench/src/video_workbench/native_index.py
      Note: Native clip cache and publication
    - Path: repo://workbench/src/video_workbench/native_video.py
      Note: Audited native adapter and feature-space identity
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T14:00:28.695667-04:00
WhatFor: ""
WhenToUse: ""
---



# Investigation and delivery diary

## Goal

Prepare a dedicated repair ticket and intern guide, preserving the distinction between source diagnosis and experimentally validated behavior. Deliver the guide to reMarkable without modifying the ongoing search implementation.

## Step 1: Archive the defect evidence and write the repair design

Created MLX-VIDEO-FIX-001 after the user questioned the native-video fallback and requested a dedicated repair guide. Inspected the installed wrapper and backbone, copied stable source evidence, and wrote a full implementation and validation plan. The guide includes tensor contracts, data-flow diagrams, pseudocode, file/API references, phased tasks, numerical parity strategy, and cache migration.

### Prompt Context

**User prompt (verbatim):**

> Create a new ticket + Create  a detailed analysis / design / implementation guide that is for a new intern, explaining all the parts of the system needed to understand what it is, with prose paragraphs and bullet point sand pseudocode and diagrams and api references and file references. It should be very clear and technical. Store in the ticket and the nupload to remarkable.
>  for fixing the MLX wrapper

**Assistant interpretation:** Create documentation and a concrete repair plan, then upload the reviewed guide; do not perform the repair in this side conversation.

**Inferred user intent:** Give an intern enough technical context and measurable acceptance criteria to restore trustworthy native video embeddings.

### What I did

- Used docmgr and remarkable-upload skills; used the diary skill format for this record.
- Archived the installed MLX-VLM 0.6.17 wrapper, backbone, encoder loader, official reference script, and historical image smoke with SHA-256 provenance.
- Distinguished missing forwarding, possible request-state leakage, and unmeasured semantic quality.
- Created P0-P5 tasks and an approximately 4,400-word guide with readable text diagrams suitable for PDF.

### Why

- Accepting video kwargs or returning 2,048 numbers does not show the video pixels reached the vision encoder.
- A small isolated repair and controlled reference comparison are preferable to silently changing the research task to frame pooling.

### What worked

- The installed sources show the exact omitted argument and the separate downstream image/video branches.
- Existing local PDF rendering scripts provide working BasicTeX settings that can be copied into this ticket.
- No edits to the ongoing workbench implementation were necessary.

### What didn't work

- First PDF review found overlapping long file paths in the two-column navigation table on page 6. Replaced that table with full-width annotated file lists before re-rendering.

- Initial reads guessed two old renderer filenames incorrectly and returned `No such file or directory`; `rg --files` identified `15-render-upload-project-guides.py`.
- Earlier web research could not load some GitHub issue-search pages. The guide therefore does not assert no issue exists.

### What I learned

- The alternative MLX-Embeddings implementation aliases video pixels into the image argument, which still requires compatibility checks against the shared backbone.
- Native-video pixel forwarding and useful temporal discrimination are distinct validation questions.

### What was tricky to build

- The main thread is actively changing the application. Source snapshots provide stable evidence and the ticket owns its scripts so its delivery does not depend on edits to another ticket.
- A minimal forwarding patch is insufficient if request-local positions or deep visual features are mishandled. The plan tests each layer independently.

### What warrants a second pair of eyes

- Request-position semantics, processor layout alignment, and comparison of quantized versus unquantized weights.
- The proposed numerical tolerance is explicitly a starting policy, not an achieved result.

### What should be done in the future

- Execute P0-P5 in an isolated checkout after documentation delivery.
- Recheck upstream state before preparing a public contribution; no issue or PR has been submitted here.

### Code review instructions

- Read guide sections 3, 6, 7, and 8 alongside the archived wrapper and backbone.
- Verify archive hashes using `sources/manifest.json`.
- Review PDF evidence and upload receipt after Step 2.

### Technical details

- New ticket: MLX-VIDEO-FIX-001; implementation remains open.
- Related tickets: COSMOS-EMBED-001, VIDEO-SEARCH-001, COSMOS-VIDEO-001.
- This documentation task did not run a native-video model experiment or modify git state.


## Step 2: Review all PDF pages and deliver to reMarkable

Rendered the guide to a 12-page PDF with a table of contents, page numbers, diagrams, and monospace code. Fixed an overlapping navigation table, rerendered, and inspected every page through contact sheets plus a full-size check of the corrected page. Uploaded the reviewed source using the same rendering settings.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Complete a legible, verified document delivery.

**Inferred user intent:** Read and annotate the intern repair guide on reMarkable.

### What I did

- Ran `scripts/03-deliver-guide.py render`, `scripts/04-review-pdf.py`, then `dry-run` and `upload`.
- Verified archive SHA-256 hashes, local Markdown links, code fences, and docmgr metadata.
- Archived contact sheets and the corrected page image under `various/pdf-review/`.

### Why

- Long technical paths and code can overflow a PDF even when the Markdown is valid.
- Source hash gates ensure the uploaded content matches the reviewed guide.

### What worked

- Docmgr doctor passed; the PDF contains 12 pages.
- Upload returned `OK: uploaded MLX-VIDEO-FIX-001_Intern_Guide.pdf -> /ai/2026/09/06/MLX-VIDEO-FIX-001`.
- [Upload receipt](../various/remarkable-upload.json) and [review record](../various/pdf-validation.json) preserve delivery evidence.

### What didn't work

- The initial narrow file table overlapped; annotated full-width lists resolved it before upload.

### What I learned

- Text diagrams survive the existing PDF pipeline without a separate Mermaid rendering dependency.

### What was tricky to build

- Keep PDF layout verification separate from runtime verification. The preview images prove document legibility, not model correctness.

### What warrants a second pair of eyes

- Implementation should revisit upstream changes and numerical tolerances before using this design as an executable patch.

### What should be done in the future

- Execute the open P0-P5 tasks; no application repair has been made by this ticket-creation task.

### Code review instructions

- Read [all pages 1–9](../various/pdf-review/contact-1.jpg), [pages 10–12](../various/pdf-review/contact-2.jpg), and [the corrected navigation page](../various/pdf-review/page-006.png).
- Start implementation with the failing forwarding tests, not a full corpus re-index.

### Technical details

- Remote folder: `/ai/2026/09/06/MLX-VIDEO-FIX-001`.
- Local rendered PDF: `output/pdf/MLX-VIDEO-FIX-001/MLX-VIDEO-FIX-001_Intern_Guide.pdf`.
- No workbench edits, dependency changes, git mutations, public issue submissions, or running-process changes were made in this documentation task.


## Step 3: Start isolated implementation and fork upstream

The user authorized running the repair in parallel with the search project, then requested milestone commits, diary entries, thermal phase slips, and a fork. Created a separate upstream checkout and environment under `output/mlx-video-fix/`; the active search environment remains untouched. Verified that `wesen/mlx-vlm` is a fork of `Blaizzy/mlx-vlm`.

### Prompt Context

**User prompt (verbatim):** "can we do the repair in parallel?"

**User prompt (verbatim):** "Ok, commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**User prompt (verbatim):** "fork the repo as well"

**Assistant interpretation:** Implement the repair independently, with commits and print/diary evidence, using a personal upstream fork.

**Inferred user intent:** Progress on native video correctness without disrupting ongoing search development.

### What I did

- Forked upstream with `gh repo fork Blaizzy/mlx-vlm --clone=false`; verified `https://github.com/wesen/mlx-vlm` and its parent.
- Cloned tag v0.6.17 for the known failing base, then fetched current upstream main and created `fix/qwen3-vl-video-embeddings` at `d5064772dcd1e31704604f93a873323505ae70d5`.
- Created a dedicated venv and pinned the runtime dependency versions.
- Printed the plan and initiated the P0 start slip.

### Why

- An isolated checkout allows small upstream commits and avoids replacing packages used by the concurrent main-thread work.

### What worked

- Current upstream main still contains the same omitted video-pixel argument.
- Fork creation succeeded and the plan printer returned `printed: true`.

### What didn't work

- First `uv venv` failed: `failed to open file /Users/manuel/.cache/uv/sdists-v6/.git: Operation not permitted (os error 1)`. Retried with an explicit workspace-local cache directory.
- A tag-only shallow clone did not create `upstream/main`: `fatal: invalid reference: upstream/main`. Created the repair branch from the fetched `FETCH_HEAD` instead.
- Initial gh searches parsed an entire expression as a repository name and returned `Invalid search query`; retried with explicit `--repo` flags.
- An optional `cat AGENTS.md` found no such file; `rg --files -g AGENTS.md` found no applicable upstream instructions.

### What I learned

- Source evidence from the released package still applies to current upstream main; the repair should target that current commit.

### What was tricky to build

- Tag-only clone fetch refspecs do not automatically create branch tracking refs. Using the verified fetched commit preserves the intended base without touching unrelated repositories.

### What warrants a second pair of eyes

- Keep fork commits limited to the wrapper and targeted tests; keep corpus-specific evidence in the ticket.

### What should be done in the future

- Finish failing regressions and the real-video baseline before changing wrapper behavior.

### Code review instructions

- Inspect the isolated checkout branch and compare the wrapper with the archived 0.6.17 source.

### Technical details

- Fork: `https://github.com/wesen/mlx-vlm`.
- Checkout: `output/mlx-video-fix/mlx-vlm`.
- Environment: `output/mlx-video-fix/.venv`.


## Step 4: Reproduce silent video-pixel loss

Both structural regressions fail on current upstream. A real four-frame development clip and an all-black pixel intervention produced exactly the same output vector, with zero vision-tower calls in both cases. This establishes the previously unmeasured runtime consequence for the controlled fixture: a finite embedding was returned without processing the video pixels.

### Prompt Context

**User prompt (verbatim):** (see Step 3)

**Assistant interpretation:** Prove the defect before repairing it.

**Inferred user intent:** Obtain trustworthy evidence and a regression that prevents recurrence.

**Commit (code):** `05432ac` — `test(qwen3-vl-embedding): reproduce dropped video pixels`

### What I did

- Added two upstream regressions covering public-call-to-helper and helper-to-backbone video forwarding.
- Ran `PYTHONPATH=output/mlx-video-fix/mlx-vlm output/mlx-video-fix/.venv/bin/python -m pytest output/mlx-video-fix/mlx-vlm/mlx_vlm/tests/test_qwen3_vl_embedding_video.py -q`: 2 failed as expected.
- Ran `scripts/05-video-smoke.py before` on four development frames, holding token IDs, mask, grid, and sample count constant for original versus black pixels.
- Recorded `[1, 2048]` finite vectors, exactly zero maximum absolute difference, and no vision-tower calls in `various/video-smoke-before.json`.

### Why

- A shape-only smoke could pass while ignoring all video content.

### What worked

- Failure 1: the captured kwargs had no `pixel_values_videos`.
- Failure 2: `TypeError: Model._last_hidden_state() got an unexpected keyword argument 'pixel_values_videos'`.
- The controlled real-model intervention isolated pixel content from timestamp and token differences.

### What didn't work

- The initial fresh-cache dependency install waited without progress; canceled it and reused the existing workspace package cache. The separate environment then installed in under a second.
- A report-metric correction was initially launched from the upstream checkout using workspace-relative ticket paths and failed with `FileNotFoundError`; repeated it from the workspace root.
- Corrected the probe's cosine calculation to divide by actual norms. BF16 output norm was about 0.9995, so a raw dot product was not exactly cosine. The exact-zero difference finding is unaffected.

### What I learned

- This is demonstrably silent visual-data loss for the tested video request, not just a suspicious signature.

### What was tricky to build

- The real input contains video metadata tokens that can affect vectors. Comparing identical token/grid layouts while changing only pixels avoids attributing metadata changes to visual understanding.

### What warrants a second pair of eyes

- The quantized checkpoint's output precision and sampling metadata must remain explicit in later parity comparisons.

### What should be done in the future

- Forward pixels, then repeat this exact fixture and check request-order behavior.

### Code review instructions

- Inspect fork commit `05432ac` and `scripts/05-video-smoke.py` alongside `various/video-smoke-before.json`.

### Technical details

- Development episode: `ep-368d6331fc690a2c`; selected PTS: 2.0, 2.4, 2.8, 3.2 seconds.
- Video patch tensor: `[640, 1536]`; grid: `[2, 16, 20]`; token count: 196.


## Step 5: Forward video pixels and verify visual computation

Added explicit video-pixel parameters through the wrapper and helper while preserving existing positional argument order. The same controlled real-video probe now calls the vision tower and distinguishes household pixels from black pixels. Added explicit paired pixel/grid validation so malformed visual input cannot masquerade as text-only input.

### Prompt Context

**User prompt (verbatim):** (see Step 3)

**Assistant interpretation:** Apply the smallest validated forwarding repair and commit it separately.

**Inferred user intent:** Restore actual visual computation before evaluating temporal quality.

**Commit (code):** `d26804d` — `fix(qwen3-vl-embedding): forward native video pixels`

### What I did

- Added video-pixel forwarding at both boundaries and paired image/video grid checks.
- Ran 6 targeted regressions: all passed.
- Ran existing Qwen processor, embedding-processor registration, and video timestamp tests: 20 passed, 148 deselected.
- Repeated the real-model fixture with `scripts/05-video-smoke.py forwarding`.

### Why

- Passing the video tensor through the image argument would select the wrong modality branch in the current backbone.

### What worked

- Vision-tower calls changed from zero to one per video request.
- Original versus black cosine changed from approximately 1 to 0.518210; maximum absolute vector difference is 0.08496094.
- Repeated original input matched exactly for this same-length fixture.

### What didn't work

- First HTTPS push failed with `fatal: could not read Username for https://github.com: Device not configured`. Retried with the existing gh credential helper scoped to that Git command; no global Git configuration changed.

### What I learned

- The minimal patch restores pixel dependence. Same-length repetition alone does not establish independence across different request shapes.

### What was tricky to build

- Preserve the public positional argument order by adding the new optional parameter after existing grid arguments.
- The prior smoke JSON records the preceding commit because the patch was uncommitted during the probe; this entry identifies the exact resulting patch commit.

### What warrants a second pair of eyes

- Request-local positional handling and BF16 normalization precision are separate from the forwarding fix.

### What should be done in the future

- Complete P2 state/padding tests and P3 reference parity before application rollout.

### Code review instructions

- Compare `05432ac..d26804d` in the fork; inspect `various/video-smoke-forwarding.json` against the baseline.

### Technical details

- Measured warm native-video calls: about 0.215 seconds for this four-frame, 196-token fixture.
- MLX peak during probe: 2,384,651,964 bytes; not a full-corpus benchmark.


P2 in-progress failure record: the first request-order probe constructed AutoProcessor before importing the MLX model registration and failed with `Qwen3VLVideoProcessor requires the Torchvision library` and `requires the PyTorch library`. The earlier smoke loaded the model first, which installed the torch-free processor registration. Added an explicit embedding-module import to the new probe before constructing AutoProcessor; no dependency workaround or production change was needed.

P2 structural regressions currently fail in two places: a shorter request uses cached position values 40/41 instead of current 0/1, and all-padding pooling does not raise. The forwarding-only version remains committed separately.


## Step 6: Remove cross-request positional contamination

The forwarding-only repair revealed a separate confirmed state defect. In the real request-order probe, a text query following video differed from its fresh-instance reference by up to 0.35791016 per coordinate (cosine 0.615845 after mixed media). A later video also drifted. The wrapper was reusing a cached positional prefix rather than the positions the backbone had just computed for the current request.

Replaced the duplicate cached-position logic with the current `InputEmbeddingsFeatures.position_ids`. Added pooling validation and actual tiny-model tests for padded batches, visual dependence, and text-after-video. All eleven real mixed-order requests now exactly match fresh-instance references, including single-frame, odd-frame, and mixed image/video requests.

### Prompt Context

**User prompt (verbatim):** (see Step 3)

**Assistant interpretation:** Repair independently demonstrated positional leakage and verify request isolation.

**Inferred user intent:** Ensure a long-running search encoder returns stable results regardless of prior requests.

**Commit (code):** `6452614` — `fix(qwen3-vl-embedding): isolate embedding position state`

### What I did

- Captured the failing cached-prefix and all-padding regressions before modifying positional handling.
- Ran `scripts/06-request-order-smoke.py before` and `after` against fresh model instances.
- Used current backbone positional output and retained causal/padding masks and deep visual features.
- Added actual tiny-model text batching and video/image-related regression coverage.

### Why

- Resetting only for video inputs would still leave a text request vulnerable to prior visual state.

### What worked

- 15 targeted tests passed, including real tiny models without downloaded test weights.
- All eleven real request-order cases matched fresh instances exactly after repair; no preprocessing cases failed.

### What didn't work

- Before repair: stale positions 40/41 were used instead of current 0/1 in the structural test.
- Before repair: all-padding pooling failed to reject an invalid request.
- Initial processor registration failure and its correction are recorded immediately above.

### What I learned

- Current backbone positional output is already request-owned; using it removes both stale state and redundant positional computation.

### What was tricky to build

- The language-model wrapper retains generation-related private fields. The embedding path can avoid them without modifying shared generation behavior.

### What warrants a second pair of eyes

- Confirm the current backbone positional result remains the authoritative embedding input under future architecture changes.

### What should be done in the future

- Complete official-model parity and application integration under a distinct feature space.

### Code review instructions

- Compare `various/request-order-before.json` and `various/request-order-after.json`.
- Inspect `test_actual_model_padded_batch_matches_individual_text` and `test_actual_tiny_video_uses_pixels_and_text_after_video_is_independent`.

### Technical details

- The eleven-case sequence includes video4, text, video2, image, video1, video3, and mixed media with repeated requests.
- Strict same-runtime maximum-absolute difference after repair: 0.0 for every case.

P2 completion: formatter checks completed with upstream-pinned Black 26.3.1 and isort 5.13.2. Black emitted a Python 3.14 target warning under Python 3.11 while successfully formatting; subsequent checks will specify the supported Python target. Five existing Qwen3-VL backbone tests also passed (four subtests). Fork push succeeded through the command-scoped gh credential helper.


## Step 7: Resume with a fresh checkout and evidence audit

Audited the isolated repair checkout before accepting the handoff. It is clean on `fix/qwen3-vl-video-embeddings` at `6452614`; the three repair commits match the handoff. Existing parity JSON files were last modified at 14:46–14:51 on September 6. They remain partial evidence: common-tensor FP32 agreement does not resolve independent processor differences.

Updated the stale ticket introduction and retained the original guide as historical design. The root checkout contains unrelated corpus/perception work, which is excluded from this milestone.

### Prompt Context

**User prompt (verbatim):**

> Resume MLX-VIDEO-FIX-001 in /Users/manuel/code/wesen/2026-09-06--vision. Read the ticket under ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/,      
>  especially reference/01-investigation-and-delivery-diary.md and tasks.md; its index/design introduction is stale and still describes documentation-only status. The actual repair checkout is
>  output/mlx-video-fix/mlx-vlm, with isolated environment output/mlx-video-fix/.venv, on branch fix/qwen3-vl-video-embeddings in the wesen/mlx-vlm fork. Last verified commits were 05432ac (failing         
>  video-forwarding regressions), d26804d (forward video pixels), and 6452614 (request-local positional state and pooling validation). Changes target mlx_vlm/models/qwen3_vl_embedding/qwen3_vl_embedding.py 
>   and mlx_vlm/tests/test_qwen3_vl_embedding_video.py. P0–P2 were complete: video pixels now reach the vision tower, original-versus-black video cosine changed from approximately 1 to 0.518, all 11        
>  mixed-order requests exactly matched fresh-instance references, and 15 targeted tests passed.
>
>  First inspect current Git status, branch history, and evidence timestamps because this handoff reflects the earlier inspection, not a fresh audit. Continue P3 reference parity, reviewing ticket scripts  
>  07-reference-parity.py and 08-processor-parity.py and existing various/reference-parity.json, processor-parity.json, and parity-{torch,mlx,mlx4bit}.json; these are partial evidence, not established      
>  acceptance. Separate preprocessing, positions, visual features, pooling, and quantization differences, then document justified tolerances and measured latency/memory. After correctness gates pass,       
>  complete P4 workbench integration with a pinned repaired dependency, explicit native-video mode, and a distinct feature-space/cache identity; preserve the existing pooled-image baseline and its
>  environment. Finish P5 with a root-cause report and upstream contribution package. Keep a detailed diary, commit focused milestones, and follow the previously requested plan/phase start/completion       
>  thermal-slip workflow; leave unrelated concurrent corpus work untouched.

**User prompt (verbatim):** "commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill)"

**User prompt (verbatim):** "Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Resume correctness validation, then gated integration and contribution preparation; preserve detailed milestone and print records.

**Inferred user intent:** Finish a trustworthy repair without disrupting concurrent corpus work.

### What I did

- Read ticket tasks, diary, parity scripts, and evidence timestamps; inspected both Git checkouts.
- Re-ran the 15 targeted regression tests with GPU access: all passed in 3.46 seconds.
- Corrected stale index/design status and located the existing `/tmp/cosmos-almanach-render-service` printer executable.

### Why

- Prior evidence cannot establish a fresh runtime result or independent-processor correctness.

### What worked

- The isolated branch is clean and the targeted regressions remain green.
- The archived FP32 comparison exposes positions and intermediate visual features independently.

### What didn't work

- Default printer invocation: `FileNotFoundError: [Errno 2] No such file or directory: 'almanach-render-service'`.
- Building the source CLI on macOS: `internal/app/cmd_ble_provision_native.go:39:31: undefined: nativeprov.NewTinyGoTransport`. Existing temporary CLI avoids changing that unrelated repository.
- Sandboxed tests aborted with `Critical nanobind error: refusing to add duplicate key "cpu" to enumeration "mlx.core.DeviceType"!`; GPU-access escalation passed.
- Sandboxed printer health check: `curl: (6) Could not resolve host: almanach.crib.scapegoat.dev`; printing retried with network access.

### What I learned

- `07-reference-parity.py` uses `*-inputs.npz`, which also includes the HF fixtures written by script 08. The 4-bit report consequently contains twelve cases versus the earlier six-case FP32 reports.
- Its case timer includes additional vision-feature diagnostics, so those durations are not isolated embedding latency.
- Independent video processors differ in token count (196 versus 197) and normalized pixel values (maximum about 0.0078433).

### What was tricky to build

- Preserve prior reports as historical evidence while making reruns explicit about fixture family and timing boundaries. Processor registration must remain isolated by process.

### What warrants a second pair of eyes

- Processor prompt wrapping, timestamps, resize kernels, and quantization attribution remain open.

### What should be done in the future

- Complete P3 before enabling application native video; print actual phase completion only after its gates pass.

### Code review instructions

- Start with scripts 07 and 08 and compare case names across existing reports.
- Validation command: `PYTHONPATH=output/mlx-video-fix/mlx-vlm output/mlx-video-fix/.venv/bin/python -m pytest output/mlx-video-fix/mlx-vlm/mlx_vlm/tests/test_qwen3_vl_embedding_video.py -q` (requires Mac GPU access).

### Technical details

- Existing fork commits: `05432ac`, `d26804d`, `6452614`.
- No pooled-image environment or corpus files were modified by this audit.

P3 immediate failure record: script 09 official processor rejected a one-frame input with `ValueError: t:1 must be larger than temporal_factor:2`. Added an explicit repeat-last-frame policy before both processors, retaining duplicate final frame indices in official timestamp metadata. Odd/single frame policy is now part of the audited contract, rather than relying on implicit processor behavior. Plan and P3 start printing succeeded at 20:07:29Z and 20:08:49Z. Audit baseline committed as `ade0f2b`; initial sandbox Git write failed with `Unable to create .../.git/index.lock: Operation not permitted`, then authorized escalation succeeded.


## Step 8: Complete controlled reference parity and separate preprocessing drift

Added an enumerated, process-isolated audit that compares official and MLX processors, identical-input runtime outputs, all visual/deepstack features, positions, pooled states, and normalized vectors. Token-only and pixel-only interventions explain the preprocessing gap. Eight FP32 correctness gates passed; four-bit variants show substantial vector and ranking drift and are not accepted for native integration.

### Prompt Context

**User prompt (verbatim):** (see Step 7)

**Assistant interpretation:** Establish measured correctness and explicit limits before workbench rollout.

**Inferred user intent:** Prevent a superficially working native mode from silently changing semantics or reusing incompatible features.

### What I did

- Added scripts 09/10, explicit audit policy, provenance hashes, fresh timestamped reports, and a reviewed original/reversed contact sheet.
- Ran independent HF/MLX preparation and serial Torch FP32, MLX FP32, BF16, controlled four-bit, and community four-bit model processes.
- Wrote `reference/02-parity-findings.md` with reproduction, bounds, timings, memory, causal distinctions, and limits.

### Why

- Same-input agreement cannot excuse preprocessing changes; community weights cannot isolate pure quantization effects.

### What worked

- Eight FP32 cases passed: text, image, video, black, reverse, video1, video3, and mixed.
- Exact positions; maximum embedding error 2.83123e-6; maximum intermediate error 8.60214e-4.
- Token-only drift dominates pixel-only drift. Warm FP32 video median is 0.2014 seconds.

### What didn't work

- Official single-frame processor rejection required explicit repeat-last padding (recorded above).
- Neither four-bit variant supports numerical/ranking interchangeability with FP32. They remain measurement-only.

### What I learned

- The official processor retains outer delimiters; MLX removes them. Odd-frame timestamps also differ.
- Controlled quantization of all eligible layers is a different conversion policy from an opaque community artifact.

### What was tricky to build

- Model registration mutates processor lookup; separate processes and explicit processor classes prevent contamination.
- Lazy GPU evaluation and diagnostic feature calls must be outside each other's timing boundaries.

### What warrants a second pair of eyes

- The pinned official processor's boundary-token contract is version-specific, not a claim about every Transformers version.
- Eight fixtures and one text query establish implementation parity, not retrieval or temporal-classification quality.

### What should be done in the future

- P4 integrates only official FP32 with pinned preprocessing, isolated dependency, distinct cache identity, and a fresh-process cold adapter benchmark.

### Code review instructions

- Read the parity findings, policy, and `audit-gates.json`; rerun scripts 09/10 in documented order.
- Inspect original/reversed contact sheet and token-only/pixel-only records in `audit-comparison.json`.

### Technical details

- Runtime versions: MLX/Metal 0.32.2; Transformers 5.16.1; Torch 2.14.0; Torchvision 0.29.0; NumPy 2.4.6; Pillow 12.3.0.
- Original/black FP32 cosine 0.429234; original/reverse 0.969836 under official preprocessing.


## Step 9: Integrate explicit native video with separate runtime and clip cache

Added an opt-in native adapter using official FP32 weights and the audited official processor. Native indexing encodes complete sampled clips and preserves actual selected PTS; the existing pooled-image adapter and frame-cache default remain unchanged. Native startup checks the repaired wrapper hash, runtime versions, and official artifact identity.

The first real smoke exactly matched the accepted video vector and matched mixed-order text/single/odd references within 2.98e-8. It encoded nine clips from one development episode into a separate output root, then reused all nine. The parent registry was opened with SQLite `mode=ro`.

### Prompt Context

**User prompt (verbatim):** (see Step 7)

**Assistant interpretation:** Integrate the accepted configuration with an explicit mode, reproducible runtime, and incompatible cache identity.

**Inferred user intent:** Make repaired native video usable without disrupting the pooled baseline or concurrent corpus work.

### What I did

- Added `native_video.py`, `native_index.py`, runtime requirements, CLI mode selection, and clip-cache namespace support.
- Added contract tests for PTS padding, cache separation/reuse, old-index rejection, and inference failure before publication.
- Installed only the isolated repair environment's editable checkout/workbench packages. Baseline `workbench/.venv` was not synced or changed.
- Ran 16 focused workbench tests; all passed. Real adapter cold first inference including preprocessing took 0.3243 seconds, warm calls about 0.208 seconds.
- Printed P3 completion at 20:17:06Z and P4 start at 20:17:12Z; P3 commit is `1effb65`.

### Why

- Native temporal features cannot reuse cached unit frame vectors. Artifact, source, processor, runtime, pooling and timestamp policy must distinguish the space.

### What worked

- Exact accepted fixture parity, stable mixed-order calls, successful development-only build, and full cache reuse.
- Failed inference leaves no feature row, manifest, or latest-build publication.

### What didn't work

- Installing the repaired checkout exposed its actual distribution version `0.7.0rc0`; prior audit imports intentionally used the checkout through PYTHONPATH while distribution metadata still read `0.6.17`.
- The original workbench unconditional `mlx-vlm==0.6.17` dependency conflicts with the repaired distribution. Moved runtime dependencies to mutually exclusive `pooled-images` and `native-video` extras; baseline installation now explicitly selects `pooled-images`. Existing baseline environment is untouched.

### What I learned

- A source commit/hash is necessary: installed distribution metadata alone did not identify code imported through PYTHONPATH.
- Timestamp metadata can represent integer microsecond ticks at a one-million-ticks-per-second rate with sampling disabled, preserving VFR timing exactly.

### What was tricky to build

- Official processor construction must precede MLX auto-registration, and startup rejects accidentally substituted MLX processors.
- Index publication happens only after all clip inference succeeds; prior successful clip cache entries are valid reusable work if a later request fails.

### What warrants a second pair of eyes

- The dependency extras and baseline lock preservation; native artifact/source checks and microsecond timestamp encoding.
- The maximum 32 selected frames is a resource limit, not a demonstrated quality optimum.

### What should be done in the future

- Finish dependency-lock validation, record final smoke identity after formatting/source changes, then prepare P5 root-cause and upstream package.

### Code review instructions

- Start with `NativeVideoEmbedder`, `prepare_video`, and `build_native`; inspect the CLI's explicit mode switch.
- Run the focused native/index/embedding/registry/API tests and ticket script 11 in the isolated environment.

### Technical details

- Smoke output: `output/mlx-video-fix/workbench-native-smoke`; episode `ep-368d6331fc690a2c`; two-second windows at 2 FPS.
- Initial space ID `d20bfb5f21da822c544cc6d12f8c72ed4e921ae9cb4e4d6c13d93217a88bb60e`.

P4 completion evidence: final artifact/source-gated adapter matched video/single/odd references exactly and text within 2.98e-8. Final source identity is `2610572d944abb10b0366c2b00aaf87e701b6f6bb6656b022eca66dd230edecd`; nine fresh development clips and nine reused clips passed. Final fresh-process timing was slower (load 6.562 s, cold inference 2.578 s, warm 0.318–0.371 s) than the first run (load 5.435 s, cold 0.324 s, warm 0.207–0.209 s). Both reports are retained. The machine runs concurrent work; no causal attribution or isolated latency guarantee is made. Final MLX peak 9,539,472,908 bytes; RSS high-water 4,842,110,976 bytes.

The dependency lock resolved mutually exclusive runtimes successfully. `uv pip check --python output/mlx-video-fix/.venv/bin/python` reports all 73 installed packages compatible. Sixteen focused tests passed in both the untouched pooled baseline interpreter and isolated native interpreter. Docmgr doctor passed. Workbench baseline source `embedding.py` is unchanged, and no baseline environment sync occurred.
