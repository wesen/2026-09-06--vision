---
Title: Design and delivery diary
Ticket: COSMOS-VERIFY-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/design-doc/01-intern-analysis-design-and-implementation-guide.md
      Note: Authored project guide
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/scripts/01-pdf-header.tex
      Note: Per-ticket PDF header
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/scripts/02-pin-download.py
      Note: Pinned conversion provenance
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/scripts/03-image-runtime-gate.py
      Note: Sequential process supervisor
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/scripts/04-archive-image-gate.py
      Note: Reproducible audit figure
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/tasks.md
      Note: Phased implementation breakdown
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/various/pdf-validation.json
      Note: Visual review and artifact hashes
    - Path: repo://ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/various/remarkable-upload.json
      Note: Successful individual delivery
    - Path: repo://workbench/src/video_workbench/verifiers/smoke_worker.py
      Note: Image gate and raw runtime measurements
    - Path: repo://workbench/verify-env/README.md
      Note: Isolated environment reproduction
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T13:13:51.729574-04:00
WhatFor: ""
WhenToUse: ""
---




# Diary

## Goal

Record evidence, design decisions, implementation-task decomposition, and reMarkable delivery for COSMOS-VERIFY-001. This ticket is a design deliverable now; application implementation remains open.

## Step 1: Establish the project boundary

Created this child of COSMOS-VIDEO-001 and inspected the existing generator, validated corpus, teaching labs, and umbrella guide. The project scope is: Compare bounded, evidence-grounded verifier behavior on identical local clips. Dependencies are the existing corpus and shared schema agreements; no model ticket is a hard prerequisite.

### Prompt Context

**User prompt (verbatim):** "Ok, create the tickets, and Create  a detailed analysis / design / implementation guide that is for a new intern, explaining all the parts of the system needed to understand what it is, with prose paragraphs and bullet point sand pseudocode and diagrams and api references and file references. It should be very clear and technical. Store in the ticket and the nupload to remarkable."

**User prompt (verbatim):** "for each"

**User prompt (verbatim):** "use virtual home instead of habitat btw"

**Assistant interpretation:** Create a separate technical intern guide and executable task breakdown for every project; use VirtualHome for synthetic data.

**Inferred user intent:** Make each project independently understandable, reviewable, and ready for an intern to implement.

### What I did
- Created ticket, guide document, diary, and explicit dependency boundary with docmgr.
- Inspected `src/virtualhome_corpus/core.py`, `runner.py`, the checked configuration, and the corpus inventory.

### Why
- The umbrella checklist is too broad to assign or verify without project-level contracts and acceptance gates.

### What worked
- Existing 24-episode corpus and teaching code provide concrete inputs and API examples.

### What didn't work
- No ticket-creation failure occurred. Runtime APIs are references to verify at implementation time, not measured local model support.

### What I learned
- Current corpus timing is weak supervision; endpoint simulator truth must not become certified pixel labels.

### What was tricky to build
- Avoiding circular dependencies requires shared schema ownership and oracle fixtures before model integration.

### What warrants a second pair of eyes
- Scope boundaries and whether acceptance gates depend on evidence the present corpus cannot provide.

### What should be done in the future
- Complete the project-specific guide, validate its examples and PDF, upload it, then implement the open tasks in phase order.

### Code review instructions
- Read the guide alongside the umbrella corpus report; distinguish existing files from proposed modules.

### Technical details
- Parent: COSMOS-VIDEO-001.
- Simulator selection: VirtualHome, explicitly requested by the user.

## Step 2: Write the intern guide and implementation phases

Wrote the project-specific analysis, proposed contracts, data flow, decision records, implementation phases, test strategy, and review exercise. The guide explains compare bounded, evidence-grounded verifier behavior on identical local clips. It distinguishes the working VirtualHome generator from future workbench modules and keeps the current corpus's label limits explicit.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Make this project independently understandable and implementable by a new intern.

**Inferred user intent:** Receive a technical design with enough detail to assign and review concrete work.

### What I did
- Authored the dedicated guide and phased task list in this ticket.
- Added direct local file references and linked dependency tickets.
- Validated code-fence balance, JSON examples, Python pseudocode syntax, SQL schema where present, and existing local links using umbrella `scripts/14-validate-project-guides.py`.
- Reviewed shared feature identity, time, evidence, and split contracts across all eight guides.

### Why
- Separate projects need compatible contracts and explicit data-quality gates to avoid duplicate implementations and misleading evaluation.

### What worked
- Every guide passed structural/example/link validation. The checks validate documentation syntax and references, not the future application.
- Existing file references point to real generator/config/playbook files; proposed workbench paths are clearly identified.

### What didn't work
- The web fetch for a guessed MLX-VLM embedding directory returned `Cache miss`. The design uses the verified maintainer README and requires inspection of the pinned installed entry point instead of inventing an API.
- No documentation parser or local-link validation failure occurred.

### What I learned
- Runtime support listings establish candidates, not measured local video behavior.
- Calibration and reviewed visibility are dependencies for stronger temporal claims, even when corpus media integrity passes.

### What was tricky to build
- A verifier's evidence cutoff and result availability are different clocks. The rules design preserves the cutoff but reevaluates at the later result time; it does not backdate new proposals.
- Multiple projects share schemas. The ticket map assigns ownership and allows oracle fixtures before full model integration.

### What warrants a second pair of eyes
- The project-specific acceptance gates and any claim relying on weak simulator timing.
- Vendor signatures and conversion fidelity must be checked again when actual runtimes are installed.

### What should be done in the future
- Render and inspect this guide, upload its own reMarkable edition, then execute the unchecked implementation phases.

### Code review instructions
- Read this ticket's guide and tasks, then follow direct dependency links.
- Run the umbrella guide-validation script to check examples and file references after editing.

### Technical details
- Guide: `design-doc/01-intern-analysis-design-and-implementation-guide.md`.
- Simulator: VirtualHome only for the active synthetic-data plan.

## Step 3: Review and deliver the reMarkable edition

Rendered this guide as a six-page PDF with a dedicated contents page, readable Helvetica/Menlo type, and unbroken code/diagram blocks. Inspected all six pages via contact sheets and a selected contract/code page at full raster size. The dry run and real upload both succeeded; the receipt is stored in this ticket.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Complete this ticket's independent PDF delivery after technical and visual review.

**Inferred user intent:** Read the implementation guide on reMarkable and retain reviewable source and delivery evidence locally.

**Commit (design source):** `edd3d34` — `docs(vision): split roadmap into eight intern-ready project tickets`.

### What I did
- Ran the shared `scripts/15-render-upload-project-guides.py render` and rasterized every page with `scripts/16-review-project-pdfs.py`.
- Verified JSON/Python/SQL documentation examples and local references; docmgr doctor passed.
- Reviewed all six pages and the larger API/code/diagram sample; recorded source and PDF hashes.
- Ran a per-ticket dry run, then uploaded this guide using the same source and renderer configuration.
- Recorded `OK: uploaded COSMOS-VERIFY-001_Intern_Guide.pdf -> /ai/2026/09/06/COSMOS-VERIFY-001`.

### Why
- Successful PDF compilation alone cannot establish readability, and a design is not delivered until the requested upload succeeds.

### What worked
- Six pages with legible text, contents, headers, page numbers, code, and diagrams; no visible clipping or overlap.
- Upload returned a positive success receipt. No redundant cloud listing was performed, following the reMarkable upload skill.

### What didn't work
- Generated changelogs had trailing blank lines reported by `git diff --cached --check`; these were removed in final bookkeeping.
- Local `pypdf`, `pdfplumber`, and `fitz` modules were absent. Existing Ghostscript provided page rasterization, text extraction, and ink bounds without installing packages.
- No rendering or upload failure occurred.

### What I learned
- The shared proven Pandoc/XeLaTeX configuration produced a consistent six-page edition for each project while preserving project-specific content.

### What was tricky to build
- PDF source hashes were captured after docmgr relations and checked again before upload; later task/diary updates do not alter the reviewed guide source.
- Upload regenerates from the reviewed Markdown and renderer settings; the stored PDF hash identifies the inspected local artifact, not a downloaded remote-byte verification.

### What warrants a second pair of eyes
- Future implementation must validate the proposed contracts and candidate runtimes; documentation checks do not establish model behavior.

### What should be done in the future
- Begin the open implementation phases in `tasks.md` when this project is scheduled.

### Code review instructions
- Compare this guide's source hash in `various/pdf-validation.json` and `various/remarkable-upload.json`.
- Reproduce with the shared render script and `--ticket COSMOS-VERIFY-001`; repeat review after content/layout changes.

### Technical details
- Remote directory: `/ai/2026/09/06/COSMOS-VERIFY-001`.
- Local inspected PDF: `/Users/manuel/code/wesen/2026-09-06--vision/output/pdf/project-guides/COSMOS-VERIFY-001/COSMOS-VERIFY-001_Intern_Guide.pdf`.
- Six-page visual review and individual dry-run/upload receipts are stored under `various/`.

## Step 4: Pin and measure the isolated image runtimes

Implemented the first VERIFY runtime gate after committing RULES' focused handoff. Both pinned 2B 8-bit conversions successfully loaded and generated from the same approved microwave frame. Qwen returned valid JSON; Cosmos surrounded its JSON with Markdown fences, so the strict parser rejected it. The original responses, input image, prompts, API signatures, model revisions, measurements, and a visually inspected audit figure are retained in this ticket.

This step accepts only single-image runtime viability at the measured size and budget. It does not accept native video, multi-image reasoning, conversion parity, or factual accuracy on a reviewed test set. The existing pooled and repaired native-video environments remain separate.

### Prompt Context

**User prompt (verbatim):** "ok, commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Finish the agreed RULES handoff, begin VERIFY, and keep reviewable commits, detailed diary entries, and meaningful printed phase boundaries.

**Inferred user intent:** Progress through the practical verifier implementation with an evidence trail and explicit limits on what the models can do.

**Commit (code):** `a5e01ee` — "Establish isolated pinned Qwen and Cosmos image runtime gate".

### What I did

- Created `workbench/verify-env/.venv` using the frozen workbench lockfile and its existing `pooled-images` dependency extra. The extra name refers to dependencies; this worker performs generation.
- Pinned and downloaded Qwen revision `b0338e0e843d8e1befe873d144b81fefdc47efa6` and Cosmos revision `69ae5c81f0f7651368989ef160da6808af6514cf`.
- Implemented `verifiers/smoke_worker.py` and the sequential, killable supervisor in `scripts/03-image-runtime-gate.py`.
- Ran the feature-completion image gate once per candidate: both processes exited zero, taking 5.752 and 3.950 seconds including process startup.
- Archived raw measurements and rendered `various/v1-image-gate/runtime-audit.png`; opened the figure and inspected the input and both raw responses.
- Printed the implementation plan/V1 start and V1 completion after the implementation commit. Completion returned `printed: true`, HTTP 200, at `2026-09-07T00:30:36Z`; receipt archived.

### Why

- Actual installed APIs and measured model loading establish whether later adapter work has viable local backends.
- Strict parsing must retain the distinction between a successful generation and an accepted answer. Silently stripping Cosmos' fences would erase a measured interface failure.

### What worked

- MLX 0.32.2, MLX-VLM 0.6.17, and Transformers 5.16.1 loaded both local conversions without runtime compatibility patches.
- Qwen generated 140 tokens with a 3.563 GB peak MLX allocation; Cosmos generated 150 tokens with a 3.579 GB peak. Both stayed within the 256-token budget.
- Full-frame input hash verification succeeded. Offline workers ran one at a time and preserved the full formatted prompts.
- The source frame visibly shows an open microwave door. This review supports the specific binary example, not a general accuracy estimate.

### What didn't work

- Cosmos emitted a Markdown-fenced object; strict parsing returned `Expecting value: line 1 column 1 (char 0)`. It remains an invalid result.
- The installer appeared quiet for several minutes. Escalated `lsof` showed an active download of `mlx.metallib`; it was not restarted. After context continuation, polling returned `write_stdin failed: Unknown process id 21138`; checking installed package metadata confirmed the environment was complete.
- The first figure attempt failed with `ModuleNotFoundError: No module named 'matplotlib'`. Replaced the figure renderer with already-installed Pillow and the local Menlo font, without adding a package.
- Initial sandboxed process inspection was denied; escalated read-only inspection established installation activity.

### What I learned

- Both converted models have usable single-image generation in the existing locked runtime. No repair of the native-video embedding environment was needed for this path.
- Cosmos' extra phrase “interior contents” is more specific than the image warrants. Rationale support must be reviewed separately from the answer enum and citation identity.

### What was tricky to build

- Resolving the virtualenv Python symlink would bypass its environment context. The supervisor uses an absolute path without resolving the interpreter symlink.
- The V1 supervisor uses a 120-second whole-process safety ceiling, whereas the request carries a 60-second budget. Both runs completed below six seconds, but this gate is not the production deadline implementation. V2 must enforce the request's budget and exercise cleanup fixtures.
- A declared `num_images=1` and 515 prompt tokens do not establish the actual visual token count or maximum context capacity. The report states these limits explicitly.

### What warrants a second pair of eyes

- Candidate provenance differs between conversions; deployment comparisons should not be presented as controlled comparisons of training alone.
- Review strict answer parsing and process-group cleanup before exposing the adapter to callers. Runtime status and answer status must remain separate.

### What should be done in the future

- Implement V2 bounded execution, distinct mode capabilities, request deadlines, and timeout cleanup.
- Complete V3 invalid-output fixtures and V4 frozen reviewed comparison. Keep this development smoke outside held-out evaluation.

### Code review instructions

- Start at `workbench/src/video_workbench/verifiers/smoke_worker.py`, then inspect ticket scripts `02-pin-download.py`, `03-image-runtime-gate.py`, and `04-archive-image-gate.py`.
- Compare `various/v1-image-gate/manifest.json` with the original raw JSON records and audit figure.
- Reproduce in a fresh output location; the smoke supervisor refuses to overwrite successful result files. Do not rerun expensive models just to regenerate the figure.

### Technical details

- Setup: `UV_PROJECT_ENVIRONMENT="$PWD/workbench/verify-env/.venv" uv sync --project workbench --extra pooled-images --frozen`.
- Gate: `PYTHONPATH=workbench/src workbench/verify-env/.venv/bin/python ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/scripts/03-image-runtime-gate.py`.
- API: `load(..., trust_remote_code=False)`, `apply_chat_template(..., num_images=1)`, `generate(..., max_tokens=256, temperature=0.0)`.
- Worker subprocesses use `start_new_session=True`; timeout cleanup uses `os.killpg(..., SIGKILL)` and `wait()`.

## Step 5: Scale the matched verifier runtime gate to 8B

The user requested the 8B reasoning models and explicitly deferred a separate 8B embedding experiment. Pinned the public Qwen 8-bit conversion and official Cosmos 8B source. A repository search found Cosmos GGUF and other formats but no public matching 8-bit MLX checkpoint; the chosen path is a local 8-bit affine conversion with group size 64. The existing 2B artifacts are preserved.

### Prompt Context
**User prompt (verbatim):** "ok, add notes and tasks but mark them for later, then go back to the 8B reasoning models"

**Assistant interpretation:** Record the larger embedding comparison as later work and execute the already-approved larger generative verifier comparison.

**Inferred user intent:** Evaluate stronger local verifiers while maintaining clear experimental boundaries.

### What I did
- Committed the deferred embedding proposal and four tasks in TEMPORAL as `8f25290`.
- Added pinned downloader and local converter scripts; made the existing gate and audit renderer accept separate input/output locations.
- Printed the 8B phase plan/start successfully at `2026-09-07T00:45:11Z`, HTTP 200.
- Began downloading the 9.9 GB Qwen conversion and 17.5 GB official Cosmos source sequentially.

### Why
- Using the same generation worker, evidence, question, and budget retains comparability with the 2B runtime gate.
- Local Cosmos conversion retains MLX-VLM as the common engine instead of introducing GGUF engine differences into this size comparison.

### What worked
- Exact source revisions and repository file metadata were recorded before download.
- The official native FP32 TEMPORAL report confirms a separate embedding path; those artifacts are unaffected.

### What didn't work
- Guessed repositories `hzang/Cosmos-Reason2-8B-8bit` and `mlx-community/Cosmos-Reason2-8B-8bit` returned `RepositoryNotFoundError` with HTTP 401. Public model enumeration found no matching MLX conversion; this is not evidence that no such conversion exists anywhere.
- Even `python -m mlx_vlm.convert --help` initializes Metal; the sandbox returned `ImportError: [metal::load_device] No Metal device available`. Inspected local converter source without importing Metal; actual conversion runs with authorized GPU access.

### What I learned
- Model names and parameter counts do not establish the availability of a matching conversion. Conversion provenance must be recorded independently.

### What was tricky to build
- Weight downloads dominate initial waiting; quantization time has not yet been measured. The user was given a provisional few-minute estimate for conversion after download, not a measured promise.
- Quantization applies to supported modules; the saved configuration and tensor types must establish actual coverage, including any floating-point vision components.

### What warrants a second pair of eyes
- Community Qwen versus locally converted Cosmos has different conversion provenance despite matching declared bit width and group size.
- A strict JSON failure must remain visible even if a larger model answers the binary question plausibly.

### What should be done in the future
- Complete the pending download/conversion and matched smoke, then append actual results and resource measurements to this step.

### Code review instructions
- Read `scripts/05-download-8b.py` and `06-convert-cosmos-8b.py`, then the arguments added to the existing gate and archive scripts.
- Validate once the complete feature is ready with the real matched image gate; preserve raw answers and inspect its rendered audit figure.

### Technical details
- Qwen revision: `a0093b9b5fda6f76ddd4a462c6830ae7c4fe47ec`.
- Official Cosmos revision: `a9fae2cf89dc64db96b12860417f0eb403013bb9`.
- Runtime: isolated MLX-VLM 0.6.17; conversion uses `trust_remote_code=False`, `q_bits=8`, `q_group_size=64`, `q_mode='affine'`.

### Execution update: Qwen complete; Cosmos awaits access

Qwen 8B completed the identical image request with valid JSON and answer true: 1.507 seconds load, 6.937 seconds generation, 149 generated tokens, 10.857 GB peak MLX allocation, and 10.269 seconds total worker wall time. Archived and visually inspected `various/v1-image-gate-8b/runtime-audit.png`. This remains a single development example, not a quality comparison.

Official Cosmos download failed before conversion with `huggingface_hub.errors.GatedRepoError: 401 Client Error` and `Access to model nvidia/Cosmos-Reason2-8B is restricted. You must have access to it and be authenticated to access it. Please log in.` A cached token exists, but access was rejected. No quantization duration has been measured. The user offered to log in and requested the page be opened. Browser plugin discovery returned `No browser is available` and an empty browser list; macOS `open https://huggingface.co/nvidia/Cosmos-Reason2-8B` succeeded as the fallback. No credentials were read or printed.

Resume the pinned downloader once account access is available, then convert and run Cosmos into its own output directory (the Qwen result must not be overwritten). The full 8B phase remains incomplete; do not print a completion slip yet.

### Access retry after web agreement

The user said "ok i agreed, try again". Retried the pinned downloader; Cosmos still returned `GatedRepoError` / HTTP 401 for `chat_template.json`. A separate read-only credential check established `implicit_token_disabled: False`, but `HfApi().whoami(token=True)` failed with `HfHubHTTPError`. Explicit authenticated `config.json` download also returned HTTP 401. Thus browser agreement has not supplied a valid CLI credential; requested local `hf auth login` for the approved account. No token or account details were printed. Conversion and Cosmos inference remain unexecuted; Qwen results remain intact.

## Step 6: Complete Cosmos conversion and the matched 8B runtime gate

The updated local login resolved model access. Downloaded the pinned official Cosmos source, converted it locally to 8-bit affine MLX weights, and ran the exact Qwen request through the same worker. Both 8B models successfully generate; Qwen is schema-valid, while Cosmos' Markdown fences remain a strict output failure. The complete original responses and a visually inspected comparison figure are archived.

### Prompt Context
**User prompt (verbatim):** "ok try again"

**Assistant interpretation:** Retry with the updated credential and complete the already-authorized conversion and inference if access succeeds.

**Inferred user intent:** Finish the larger verifier runtime comparison after resolving authentication.

**Commit (code):** `537ad1e` — "Complete local Cosmos 8B conversion and matched verifier runtime gate".

### What I did
- Retried `scripts/05-download-8b.py`; Cosmos source download completed in approximately 252 seconds.
- Ran `scripts/06-convert-cosmos-8b.py` offline with Metal access, recording conversion and hashing time separately.
- Ran the existing gate with `--pins various/cosmos-8b-runtime-pins.json --output output/verifier-v1/image-gate-cosmos-8b`.
- Added `07-report-8b.py` to require identical request objects, combine preserved runs, and regenerate the report/audit figure without new model calls.
- Opened and visually inspected `various/v1-image-gate-8b-comparison/runtime-audit.png`.

### Why
- The requested comparison needed actual larger-model execution; model availability or successful conversion alone is insufficient.
- Separating download, conversion, and hashing directly answers the user's timing question.

### What worked
- Local conversion took 8.634 seconds; output hashing took 6.581 seconds. Total recorded conversion-plus-hashing time was 15.216 seconds.
- Converter reported source dtype bfloat16 and effective 8.993 bits per weight under the selected 8-bit quantization policy.
- Cosmos loaded in 1.434 seconds, generated 158 tokens in 6.992 seconds, and used 10.857 GB peak MLX allocation. Total worker time was 10.495 seconds.
- Qwen's preserved run loaded in 1.507 seconds, generated 149 tokens in 6.937 seconds, and used 10.857 GB peak MLX allocation. Total worker time was 10.269 seconds.
- Both raw answers say the microwave door is open; the archived image supports that binary observation.

### What didn't work
- Cosmos emitted a fenced JSON block; strict parsing returned `Expecting value: line 1 column 1 (char 0)`. The output was not silently repaired.
- Cosmos' rationale mentions “contents inside,” which is more specific than the visible evidence warrants; schema and factual rationale support remain separate checks.
- The earlier few-minute estimate for conversion was conservative: the actual conversion completed in under nine seconds. Downloading was the dominant wait.

### What I learned
- Both 8B candidates are practical for this bounded single-image request on the 64 GB M1 Max. This does not establish video-mode capability or accuracy improvements over 2B.

### What was tricky to build
- Authentication involved two independent steps: web agreement and a valid local CLI credential. The successful retry needed no code change or credential exposure.
- Quantization bit width is a configuration, not a guarantee that every stored tensor is 8-bit. The converter's effective bit count includes its quantization policy and overhead; exact converted file hashes are retained.
- Separate result directories allow completing Cosmos after Qwen without rerunning or overwriting the successful Qwen gate. The report join asserts full request equality.

### What warrants a second pair of eyes
- Local conversion has not been compared numerically with the official full-precision model.
- This prompt requests direct JSON within 256 tokens; it does not evaluate a long-form reasoning configuration or establish Cosmos' best achievable quality.

### What should be done in the future
- Proceed with V2 bounded evidence execution, V3 malformed/timeout fixtures, and V4 reviewed matched cases with development-only prompt selection.
- Keep the separately recorded 8B embedding experiment deferred.

### Code review instructions
- Inspect conversion settings and file hashes in `various/cosmos-8b-conversion.json`, then the comparison manifest and raw result objects.
- Run `07-report-8b.py` to reproduce the figure/report from saved evidence; no additional inference is necessary for that check.

### Technical details
- Official Cosmos revision: `a9fae2cf89dc64db96b12860417f0eb403013bb9`.
- Converted weights: `output/models/cosmos-reason2-8b-8bit-local`.
- Shared runtime: MLX-VLM 0.6.17, MLX 0.32.2, Transformers 5.16.1.
- Selected quantization: affine, eight bits, group size 64, `trust_remote_code=False`.

Phase-completion slip confirmed `printed: true`, HTTP 200 at `2026-09-07T01:07:37Z`; archived in `various/8b-done-print-receipt.json`. Ticket doctor passed.

## Step 7: Rerun reviewed verifier evaluation and native temporal heads

Expanded the single-frame verifier smoke to all 48 existing reviewed development/test state frames, comparing both 2B and both 8B models with unchanged questions and generation budgets. In parallel, retrained the native temporal ridge and six TCN heads from the accepted 792-window native FP32 feature cache, preserving the original heads and pooled artifacts. These are separate component evaluations; there is no new claim that native embeddings feed the reasoning models or that an integrated detector-to-rule system has been validated.

### Prompt Context
**User prompt (verbatim):** "ok, can we rerun the tests now that we have bigger models and also native embeddings?"

**Assistant interpretation:** Execute meaningful upgraded-model evaluations, preserving populations and reporting representation and reasoning effects separately.

**Inferred user intent:** Determine whether the newly available models improve actual task outcomes beyond runtime smoke success.

**Commit (code):** `f075df7` — "Freeze reviewed verifier evaluation and reuse resident models across bounded requests".

### What I did
- Froze all 24 development and 24 test reviewed RGB frames in `various/rerun/protocol.json`, including input/label hashes and original reviewer provenance.
- Added a resident-model evaluation runner: one heavy model process at a time, fresh generation per request, a 60-second active request deadline enforced by the supervising process, and 120 seconds for startup.
- Preserved raw answers, request/image binding, parser status, runtime and resource measurements for all cases.
- Created a fresh temporal comparison directory with a link to the unchanged accepted feature cache and trained fresh heads with the existing selection policy.
- Ran the targeted temporal/native regression selection: 18 passed in 1.19 seconds.
- Printed the evaluation plan/start successfully at `2026-09-07T01:14:19Z`.

### Why
- Reusing the model avoids repeatedly loading large weights; each generation has a fresh default cache and the model never receives labels or previous answers.
- Retaining all existing development/test cases avoids selecting only images where larger models look successful. No prompt changes are selected using these results.
- Fresh temporal training checks reproducibility without repeating the already accepted costly pixel extraction.

### What worked
- Native ridge reproduced 24.546% test macro recall; mean native TCN reproduced 24.311%. The selected seed outcomes reproduce the previous comparison.
- The 18 regression tests cover temporal data, classical models, TCN causality, observation storage, and native cache/time contracts.

### What didn't work
- No test or runtime failure has occurred at this stage; the verifier sweep is still running. Strict model output failures will be counted separately from process execution failures.

### What I learned
- This reviewed population is confounded by appliance and split: development is fridge, test is microwave. Test has 15 closed, 2 open, and 7 unknown cases. Development has 22 closed and 2 open cases. Aggregate accuracy requires that context.

### What was tricky to build
- Existing feature caches and results must remain separate across feature spaces. The fresh temporal directory links only the accepted native features; trained heads and reports are new files.
- The supervisor records progress independently of model prose and kills the entire worker process group if a request exceeds its deadline. This evaluation runner is not the full V2 production adapter; timeout/restart fixtures remain future acceptance work.

### What warrants a second pair of eyes
- Reviewed labels were produced previously by an assistant from RGB frames; the dataset is small, repeated within episodes, and not an independent human-labeled benchmark.
- Strict answer correctness is evaluated against reviewed labels. Full rationale support is not automatically established by a correct enum or a valid citation.
- Current 256-token direct-answer prompting is frozen for comparability; it does not measure an optimized long-form Cosmos reasoning configuration.

### What should be done in the future
- Complete the running sweep, inspect the report and visual inputs, record raw counts, and preserve the scope limits.
- Use a separately frozen evaluation for future development-selected prompt or output-contract changes; do not repeatedly tune against this test set.

### Code review instructions
- Start with `08-freeze-rerun.py`, the protocol hashes, and `09-rerun-verifiers.py`; inspect `smoke_worker.run`'s optional resident model bundle.
- Use `10-report-rerun.py` after all four runs finish to verify request bindings and compare the fresh temporal results with the original accepted comparison.

### Technical details
- Native head rerun: `PYTHONPATH=workbench/src workbench/perception-env/.venv/bin/python -m video_workbench.temporal.native_compare output/temporal-v1/dataset output/temporal-native-fp32-rerun-v1 output/temporal-v1`.
- Regression command: `PYTHONPATH=workbench/src workbench/perception-env/.venv/bin/python -m pytest workbench/tests/test_temporal_data.py workbench/tests/test_temporal_classical.py workbench/tests/test_temporal_tcn.py workbench/tests/test_temporal_store.py workbench/tests/test_native_video.py -q`.
- Native extraction timing in the rerun report is inherited provenance from the original extraction, not a fresh extraction measurement.

## Step 8: Normalize Markdown wrappers without changing answer contents

The user asked about JSON errors during the sweep, then requested inspection of the local sanitize project and handling backticks. Inspection showed a dedicated `markdown_fence_wrapper` rule. Implemented that narrow wrapper normalization in Python: preserve raw responses, trace the transformation, then apply the existing strict JSON and semantic checks. The broader sanitizer repairs are not enabled.

### Prompt Context
**User prompt (verbatim):** "ok, look at ~/code/wesen/go-go-golems/sanitize and maybe the tackle the backticks too."

**Assistant interpretation:** Use the existing sanitizer approach to remove the observed Markdown fence friction.

**Inferred user intent:** Make the output contract practical without confusing formatting failures with visual understanding.

**Commit (code):** `e7b34b0` — "Accept traced outer JSON fences while preserving verifier validation".

### What I did
- Read sanitize README, JSON heuristic/rule registration, and `pkg/json/fix.go:78` at revision `c142cca399ff596da307d287fceda8de4155a3dd`.
- Added `verifiers/normalization.py` and `allow_markdown_fence` control to the answer parser, retaining untouched raw output and a normalization trace.
- Added 11 output-boundary cases and ran them at feature completion: all passed in 0.02 seconds.
- Added separate normalized replay reporting over saved responses; original strict observations remain preserved.

### Why
- All 48 Cosmos 2B responses had syntactically valid JSON inside a Markdown fence. Treating these as unusable obscures the semantic comparison.
- A narrow wrapper transform has different consequences from changing values, removing duplicate keys, or correcting identity fields.

### What worked
- Bare and json-tagged fences, surrounding whitespace, and CRLF wrappers normalize while preserving literal backticks inside JSON string values.
- Tests confirm rejection of prose, multiple blocks, truncated JSON, duplicate keys, nonfinite values, wrong IDs, invented citations, and other language fences.

### What didn't work
- Searching a guessed sanitize `AGENTS.md` returned `No such file or directory`; repository README and source files were available.
- Three Qwen 2B responses copied the request ID incorrectly. One dropped its final character. This wrapper change intentionally does not repair those identity fields.

### What I learned
- The observed syntax failures and binding failures require separate reporting. A formatting repair may recover an incorrect answer as well as a correct one.

### What was tricky to build
- The model sweep was active. Waited until the last model process had imported the original parser and completed requests before changing the parser source, so every baseline result used the original behavior. Future reruns explicitly disable wrapper normalization for the strict condition.
- Normalized replay operates on saved raw responses and produces separate summary/raw files. It does not rerun generation or overwrite the strict records.

### What warrants a second pair of eyes
- Request-ID echoing is still brittle. A future host-owned envelope can remove that obligation, but should preserve evidence binding and be measured as another explicit contract change.
- Post-observation normalization results must be labeled as such, not presented as untouched test evaluation.

### What should be done in the future
- Finish the sweep and normalized replay, report both score sets, and preserve practical V2/V4 acceptance limits.

### Code review instructions
- Compare `normalization.unwrap_json_fence` with sanitize's fence-wrapper rule, then inspect `contracts.parse_answer` and `tests/test_verifier_output.py`.
- Run `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_verifier_output.py -q`.

### Technical details
- Sanitizer source: `/Users/manuel/code/wesen/go-go-golems/sanitize/pkg/json/fix.go:78` and `heuristics.go:10`.
- No files in sanitize were modified; no Go executable or new runtime dependency was introduced.
- `parse_answer(..., allow_markdown_fence=False)` retains original strict wrapper behavior.

### Completed sweep and separate normalized replay

All four model processes completed all 48 requests: 192 retained responses, no process timeout or execution failure. The fresh native ridge/TCN comparison structures exactly matched the accepted earlier comparison. Strict and normalized report scripts completed; viewed the outcome chart and both 24-frame contact sheets.

Strict test scores: Qwen 2B 13/24, Qwen 8B 16/24, both Cosmos sizes 0/24 because every Cosmos response was fenced. Separate normalization recovered all 96 Cosmos fences. Cosmos 2B then scored 7/24 test and 2/24 development, retaining three binding failures across splits. Both 8B models scored 24/24 development and 16/24 test with identical answer enums. They got 16/17 visible test labels right but incorrectly called all seven unknown cases closed. Their test score exceeds the always-closed baseline by only one answer; no robust uncertainty handling or 8B Cosmos advantage is established.

During normalized reporting, the first diagnostic categorizer mislabeled remaining binding failures as fence errors merely because raw text still contained a fence. Corrected categorization to use the post-normalization parser reason when a transformation has already occurred; scores were unchanged. Updated the normalized chart title to distinguish it from the strict plot. Original raw responses and scores remain unchanged.

The original Step 7 no-failure note referred to process/tests during execution, not output correctness. The sweep is now complete, while broader V2/V4 scope remains open. No prompts were tuned and no embedding extraction was repeated. The 18 regression tests and 11 new output-boundary tests passed at their respective feature completion points.

Completed evidence/report commit: `7ffab0b`. Completion slip printed successfully with HTTP 200 at `2026-09-07T01:34:11Z`; receipt archived in `various/rerun-done-print-receipt.json`.

## Step 9: Bound visibility requests and preserve a fresh visual comparison

Implemented a host-owned answer envelope and one-image subprocess adapter, then evaluated direct and visibility prompts on fresh reviewed images. The integration now retains an independent verifier-conditioned RULES result. The comparison also exposed a semantic limit: neither 8B model abstained on the four occluded test cases.

### Prompt Context

**User prompt (verbatim):** "ok. commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill) . Take screenshots as well so we can use that for a detailed report later on as well, to explain what a closed case is and such."

**Assistant interpretation:** Implement the next bounded verifier step with reviewable evidence, commits, and a visual case guide.

**Inferred user intent:** Make the verifier usable while preserving enough evidence to explain its behavior and failures.

**Commit (code):** `c6dd120` — bounded visibility adapter, fresh cases, and initial cookbook archive.

### What I did

- Added visibility prompt/parser, isolated worker, host adapter, and `rules.handoff.investigate`.
- Reviewed 24 original frames, four contact sheets, and annotated closed/open/unknown panels. Original images remain separate from annotations.
- Froze labels and selection before model calls; ran 48 development calls then 24 selected-prompt test calls.
- Ran one real Cosmos RULES handoff: baseline UNKNOWN remained unchanged; separate conditioned decision was PASS.
- Printed the phase plan successfully: HTTP 200, printed true, 2026-09-07T01:40:40Z, 384 by 483 pixels. Layout is `various/visibility-plan.yaml`.

### Why

- Long identity copying caused avoidable failures; host binding removes that model obligation.
- Positive closed-door criteria and reviewed occlusions let us measure whether visibility instructions address false certainty.

### What worked

- All 26 focused smoke tests passed in 0.29 seconds at feature completion.
- All 72 model calls returned valid responses without reported truncation. Test accuracy was Qwen 8/12 and Cosmos 7/12.
- Raw output, actual formatted prompts, timing, model allocation, original frames, and the separate live RULES trace are preserved.

### What didn't work

- Initial integration fixture used incorrect rule fields and raised `ValueError: rule schema fields/version invalid`. Corrected the fixture to `schema_version=1, rule_id=...`; production validation remained unchanged.
- Both models gave known answers for all four unknown test labels. Visibility wording did not solve abstention.
- A later diary read used the guessed name `reference/01-diary.md` and returned `No such file or directory`; discovered and used the actual `01-design-and-delivery-diary.md`.

### What I learned

- Valid visibility flags are model assertions, not an independently validated visibility detector.
- A one-point development selection advantage is weak evidence, especially with correlated synthetic frames.

### What was tricky to build

- Host binding must preserve approved evidence identity without accepting invented model citations. The model sees F1; the host validates and maps only that alias.
- The deadline spans setup plus worker execution. Process-group termination and reaping prevent a timed-out worker from surviving into the next request.
- The test partition was kept out of prompt selection. New research did not change the frozen implementation during inference.

### What warrants a second pair of eyes

- Conservative side-view RGB labels and apartment overlap across episodes limit independence. Obtain human review before treating this as a benchmark.
- Inspect timeout cleanup, completion timestamps, and the distinction between baseline and conditioned streams.

### What should be done in the future

- Evaluate explicitly prompted reasoning separately. Keep multi-image/video and full rationale-support acceptance open.

### Code review instructions

- Start at `visibility.parse_visibility`, `adapter.verify`, and `handoff.investigate`; compare the live trace with the unchanged baseline.
- Validation command: `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_visibility_adapter.py workbench/tests/test_verifier_output.py -q`.
- Read reference 05 and reproduce archived summary counts with script 18.

### Technical details

- Frozen protocol SHA-256: `b11aa2a5538ee1cf8f8b5670aeb466c99f4a096d852ea1300294f0c01e9a24cb`.
- Selection scores: direct 1, visibility 2; correct count minus unsupported known-on-unknown answers, aggregated across both models.
- Single image, at most ten MiB and 1920×1080 pixels; benchmark temperature zero, 384 output tokens; 60-second deadline.

## Step 10: Review official Cosmos Reason2 guidance and archive primary sources

Expanded the requested warehouse review into the official model card, prompting guide, inference examples, quantization guide, and troubleshooting documentation. Wrote a source-linked analysis distinguishing our short JSON baseline from NVIDIA's explicitly prompted reasoning configuration.

### Prompt Context

**User prompt (verbatim):** "also look at the "worker safety in a classical warehouse" notebookby nvidia in the cosmos cookbook, if there are things you can use to improve our system. Store any relevant resources int he ticket sources/ folder"

**User prompt (verbatim):** "look at other guidance and information about cosmos reason 2"

**Assistant interpretation:** Inspect broader authoritative guidance, preserve relevant resources, and identify useful system changes.

**Inferred user intent:** Avoid missing model-specific conventions that might explain weak verifier results.

### What I did

- Archived seven cookbook resources and seven official Reason2/model-card resources with pinned revisions and SHA-256 manifests.
- Compared documented message order and generation profiles with our actual saved MLX formatted prompts and worker code.
- Wrote reference 06 with current-versus-recommended settings, source inconsistencies, and a bounded follow-up sequence.

### Why

- Increasing model size does not automatically enable the documented reasoning response protocol.
- Primary-source examples clarify compatibility and expected inputs, but require task-specific evaluation.

### What worked

- Official inference utility agrees with the cookbook sampling profiles. Saved MLX input already places media before task text.
- The archive can be reproduced without running downloaded upstream Python.

### What didn't work

- Official guidance is inconsistent about placing reasoning instructions in the system versus user turn and using a separate answer tag. Documented both conventions rather than silently mixing them.
- Some cookbook examples infer hidden authorization or physical properties; these are not suitable ground-truth policies for our verifier.

### What I learned

- Our worker has no system turn and uses temperature zero with a short budget. It is a deliberate direct-answer experiment, not a reproduction of the vendor reasoning profile.
- Reason2 video timestamps belong in its input representation; annotated review images must not be substituted for original inputs.

### What was tricky to build

- Guidance arrived during a frozen comparison. Preserved that experiment and recorded recommendations as separately versioned follow-up tasks instead of changing prompts mid-run.

### What warrants a second pair of eyes

- Review the future reasoning-envelope parser and actual MLX sampling support before claiming vendor-configuration parity.

### What should be done in the future

- Run development-only direct versus explicit reasoning configurations, then freeze an independent test evaluation.
- Consider crops and short timestamped videos only under explicitly extended packet contracts.

### Code review instructions

- Read reference 06, both provenance manifests, and script 16. Compare `worker.py` with archived `inference_sample.py` and `inference.py`.

### Technical details

- Official repository revision: `a3b4a1db4065fe13c4b1f4d2fb8605bad647f4b9`.
- Cookbook revision: `d0857364e8a727be41b181731e03f478213e4558`.
- Official 8B model-card revision: `a9fae2cf89dc64db96b12860417f0eb403013bb9` (source manifest carries the full authoritative checkpoint revision).

Completed reports, raw evidence, source archive, and bookkeeping in `ccfce45`. Ticket doctor and diff whitespace checks passed. Meaningful completion slip printed successfully (HTTP 200) at `2026-09-07T02:03:08Z`; receipt and generated layout are archived in `various/visibility-done*`.

## Step 11: Review Qwen guidance against the installed verifier runtime

Reviewed Qwen3-VL documentation with the same source-preserving method used for Cosmos. The key result is that our current Qwen Instruct checkpoint and a Qwen Thinking checkpoint are different candidates. A future experiment must separate checkpoint changes from decoding changes, while preserving the existing visibility comparison.

### Prompt Context

**User prompt (verbatim):** "Now do the same research with qwen potentially too."

**Assistant interpretation:** Review authoritative Qwen guidance, compare it with our implementation, and archive relevant material and actionable findings in this ticket.

**Inferred user intent:** Identify model-specific improvements and avoid treating Cosmos conventions as universal.

### What I did

- Archived 16 original source files with immutable revisions and SHA-256 hashes, including four notebooks and Instruct/Thinking model metadata.
- Generated readable notebook cell extracts without executing notebook code; original notebooks preserve upstream visual examples.
- Inspected installed MLX generation defaults and penalty interfaces directly from source, without loading models.
- Wrote reference 07 and added follow-up tasks for explicit Instruct decoding, a separate Thinking checkpoint, and a later bounded crop experiment.

### Why

- Our frozen temperature-zero JSON run does not reproduce Qwen's published stochastic evaluation recipe.
- The model's saved generation configuration and an inference library's Python defaults need not agree.

### What worked

- Script 20 verified all 16 archived source hashes and captured five local source/config identities.
- The official repository documents separate Instruct and Thinking checkpoints and reproduction settings.
- Local inspection established MLX top-p 1.0 and top-k 0 defaults; the worker explicitly chooses temperature zero.

### What didn't work

- The initial guessed single-file runtime path failed with `zsh:1: no matches found: workbench/verify-env/.venv/lib/python*/site-packages/mlx_vlm/generate.py`. Used `rg --files --hidden --no-ignore` to locate the installed generation package instead.
- Thinking checkpoint metadata specifies temperature 1.0 while the repository evaluation recipe specifies 0.6. Recorded both rather than presenting a single universal default.
- Some evaluation and notebook examples retain older model names or preprocessing assumptions. They cannot all be copied unchanged into our Qwen3 MLX path.

### What I learned

- Qwen Thinking is a separate checkpoint experiment, not simply a Cosmos-style prompt change.
- A crop can improve access to small visible detail but cannot resolve complete occlusion.
- Penalty context scope is another runtime setting to check before claiming inference parity.

### What was tricky to build

- Guidance comes from several layers: model files, repository reproduction settings, utility APIs, and installed runtime code. Kept each claim attached to its source and recorded differences explicitly.
- Notebook originals contain visual output and can be large. Preserved the requested relevant originals, while cell extracts make the code review practical without executing downloads or exposing external API keys.

### What warrants a second pair of eyes

- Inspect Thinking template/final-answer behavior and quantization provenance when choosing the actual candidate.
- Check processed tensor resolution and penalty semantics before assuming that named parameter equality establishes parity.

### What should be done in the future

- Follow the ordered experiments in reference 07; use a fresh reviewed test population because the existing test outcomes have already been inspected.

### Code review instructions

- Start with reference 07 and `sources/qwen3-vl/provenance.json`; compare the archived generation configurations against installed-source excerpts in `local-runtime-audit.json`.
- Run script 20 for source-hash verification. No model tests were rerun because this step changes research artifacts and tasks only.

### Technical details

- Qwen repository revision: `96588727e44c78b25ba03ea03b8e12f7e64fd0da`.
- Existing MLX Instruct conversion revision: `a0093b9b5fda6f76ddd4a462c6830ae7c4fe47ec`.
- Archives: scripts 19–20; official model revisions are recorded in each provenance URL.

Research and source archive committed in `0cf74e2`. Ticket doctor and diff checks passed. The research completion slip printed successfully (HTTP 200, 384×586) at `2026-09-07T02:12:09Z`; generated layout and receipt are in `various/qwen-research-done*`.

## Step 12: Design prompted reasoning on the current Qwen Instruct checkpoint

Added a concrete follow-up design and five implementation tasks. The first experiment now crosses direct versus step-by-step prompting with greedy versus sampled decoding on the existing checkpoint. The separate Thinking model remains a subsequent comparison rather than a prerequisite.

### Prompt Context

**User prompt (verbatim):** "Ok, add follow up tasks and design. You can ask for chain of thought in qwen maybe, if it's not a reasoning model."

**Assistant interpretation:** Specify and task an experiment that explicitly prompts Qwen Instruct to reason before its final answer.

**Inferred user intent:** Test whether prompting alone improves verification before requiring another checkpoint.

### What I did

- Wrote design 02 with a four-arm experiment, example reasoning instruction, explicit final-answer grammar, generation profile, resource bounds, dataset policy, selection rule, and implementation file map.
- Added R1–R5 tasks and linked the earlier research recommendation to this refined sequence.
- Inspected the actual request validator and adapter limits before proposing a longer response budget.

### Why

- Prompt style and decoding should be separated from checkpoint changes so the result has a clear interpretation.
- Model-generated explanations are useful diagnostics but do not independently establish visible facts.

### What worked

- Existing host binding, citation validation, and separate RULES evidence can remain the final-answer path.
- The current Instruct weights suffice for the proposed prompted-reasoning arms; no new download is required for this first experiment.

### What didn't work

- The prior research's suggested 4096-token trial cannot pass the current 512-token request maximum. The design now explicitly includes a bounded contract update and coordinated raw/final limits.
- No execution failures occurred; no model runs were started for this design-only request.

### What I learned

- The final JSON parser and raw explanation need separate size limits and a declared extraction style.
- Equal output ceilings do not mean equal realized compute, so report actual tokens and end-to-end latency.

### What was tricky to build

- Adding reasoning and sampling together would confound two changes. The four-arm layout measures each separately with the checkpoint, images, and shared task definitions fixed.
- Reasoning text may contain JSON-like material; the parser must validate only the suffix after one declared reasoning block, never search for whichever object looks usable.

### What warrants a second pair of eyes

- Review the profile identity binding, revised request maximum, raw UTF-8 byte limits, and truncation classification when implementing.
- Verify that sampled-case averaging does not inflate the number of independent observations.

### What should be done in the future

- Implement R1–R5, complete feature-level smoke checks, and run the frozen comparison before a separate Thinking checkpoint experiment.

### Code review instructions

- Start with design 02 and task group R1–R5; inspect `contracts.validate_request`, `visibility.parse_visibility`, and `adapter.verify` for the existing limits being changed.
- This commit is documentation only; validate docmgr metadata and whitespace rather than rerun model or application tests.

### Technical details

- Proposed common ceiling: 4096 generated tokens, 120-second deadline; existing callers retain their requested budgets.
- Proposed raw/worker limits: 256 KiB UTF-8 raw text and one MiB serialized worker result; final JSON remains limited to 16000 characters.
- Sampled seeds: 3407, 3408, 3409. Selection averages per case before comparing arms.

## Step 13: Make the Cosmos reasoning follow-up concrete

Added a dedicated Cosmos experiment design and C1–C4 tasks. It uses the existing 8B conversion and the shared profile/parser implementation from design 02, while freezing NVIDIA-specific prompting and decoding choices explicitly.

### Prompt Context

**User prompt (verbatim):** "and for cosmos reason?"

**Assistant interpretation:** Provide the same concrete follow-up design and implementation breakdown for Cosmos Reason2.

**Inferred user intent:** Ensure both verifier candidates receive equivalent investigation rather than leaving Cosmos as a vague later task.

### What I did

- Added design 03 with four fixed-checkpoint arms, explicit reasoning output grammar, budgets, selection policy, and implementation dependencies.
- Added C1–C4 and linked the original Cosmos research note to the concrete design.
- Re-read the archived official inference defaults to specify the reasoning sampling profile accurately.

### Why

- Both prompt and decoding change in a vendor-style reasoning run; controlled arms distinguish their effects.
- Shared adapter work should be implemented once and used by both model experiments.

### What worked

- Existing local Cosmos weights and conversion provenance support the proposed experiment without another model download.
- The same final visibility contract and host identity binding can validate Cosmos output after explicit reasoning extraction.

### What didn't work

- No execution failures occurred. No model runs or production changes were made during this design step.

### What I learned

- The direct arm using reasoning sampling must be labeled a control, not the official default direct profile.
- Shared test cases can leak information across model experiments if the second model's prompt is tuned after viewing the first model's test errors.

### What was tricky to build

- The official minimal system message differs from the historical worker prompt. Applying it to all new arms yields a matched control, but historical-to-new changes cannot be attributed solely to reasoning.
- Reusing a test population is defensible only when both protocols are frozen before any shared test results are inspected; otherwise collect new Cosmos cases.

### What warrants a second pair of eyes

- Check actual MLX template/output boundaries against the frozen reasoning convention and verify profile parameters are applied rather than ignored.

### What should be done in the future

- Implement shared R1–R2, then C1–C4, keeping semantic abstention acceptance separate from parser/runtime success.

### Code review instructions

- Read design 03 alongside design 02 and the archived `inference.py:get_defaults` source.
- Validate ticket metadata and diff hygiene; no application tests are needed for these documentation-only changes.

### Technical details

- Reasoning sampling: temperature 0.6, top-p 0.95, top-k 20, repetition penalty 1.0, presence penalty 0.0; seeds 1234–1236.
- Proposed common ceiling: 4096 tokens and 120 seconds, contingent on the shared contract update and development pilot.

## Step 14: Implement the shared reasoning boundary

Implemented explicit immutable experiment profiles, step-by-step prompts, and declared reasoning-block extraction followed by the existing visibility parser. The worker records the actual processed image grid and applies seeded decoding. Existing short-answer callers retain their requested prompts and budgets.

### Prompt Context

**User prompt (verbatim):** "Implement. commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**Assistant interpretation:** Complete the shared feature, real-model pilots, frozen comparisons, and handoff validation with traceable commits and phase slips.

**Inferred user intent:** Turn the approved experiment designs into measured implementation evidence.

**Commit (code):** `4608902` — "Implement bounded reasoning profiles and validated final-answer extraction".

### What I did

- Added `profiles.py`, explicit request/profile limit binding, hashed profile propagation, bounded final-answer extraction, and optional profile support in RULES.
- Raised the request maximum to 4096 tokens without changing existing requested budgets; experimental raw and worker records have separate bounds.
- Added feature-completion smoke tests; all 48 selected tests passed in 0.36 seconds.
- Printed the plan and P1 start slips successfully: HTTP 200 at 02:33:58Z and 02:34:36Z on 2026-09-07. Layouts are archived in `various/reasoning-*`.

### Why

- The comparison needs independent control over prompt and decoding while retaining trusted host identities.
- Reasoning text may contain candidate answers, so only the explicitly delimited final JSON is validated.

### What worked

- Tests cover invalid profile values, changed seeds/hashes, UTF-8 size bounds, malformed reasoning delimiters, duplicate/trailing answers, and worker profile substitution.
- Existing visibility, timeout recovery, and raw-output tests still pass.

### What didn't work

- No test failures occurred in this feature batch. Real-model template and runtime acceptance remain for the next phase.

### What I learned

- Installed MLX tracks recent input/generated tokens for penalties. Recorded a 4096-token context and labeled it a local approximation, not vLLM parity.

### What was tricky to build

- Capturing processor output without processing twice: the experimental worker prepares inputs once, records tensor/grid shape, and passes those exact tensors into generation.
- Larger raw explanations must not weaken the final 16000-character visibility limit. Extraction separates the two bounds.

### What warrants a second pair of eyes

- Inspect prepared tensor forwarding and actual template behavior during pilots.
- Verify that all failed experimental results preserve profile provenance as well as successful results.

### What should be done in the future

- Complete P2 pilots and fresh RGB review, then freeze both model protocols before any test run.

### Code review instructions

- Start with `profiles.validate_profile`, `visibility.parse_experiment`, and `worker.run`, then inspect host profile checking in `adapter.verify`.
- Smoke command: `PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_reasoning_profiles.py workbench/tests/test_visibility_adapter.py workbench/tests/test_verifier_output.py -q`.

### Technical details

- Profiled runs use 4096 tokens and 120000 ms, one approved image, 256 KiB raw text, one MiB worker JSON.
- Greedy and sampled profiles preserve distinct IDs and seeds; model family and system-message policy are explicit fields.

## Step 15: Pilot both models and freeze the visual experiment

Ran eight real-model development pilots, corrected the Qwen reasoning delimiter based on those outputs, then ran a separate eight-call pilot. Reviewed fresh images before freezing 48 cases and both model protocols together. No test inference occurred during this phase.

### Prompt Context

**User prompt (verbatim):** (see Step 14)

**Assistant interpretation:** Verify real runtime behavior, preserve failures, and prepare a reviewable comparison before model selection.

**Inferred user intent:** Obtain measured behavior with a clear visual trail and avoid tuning on test outcomes.

### What I did

- Piloted all four arms for both models on an existing development frame. Initial Qwen reasoning responses failed; Cosmos completed the requested format.
- Changed only Qwen's declared wrapper to `<reasoning>...</reasoning>`, retaining Cosmos `<think>...</think>`, then ran a separate pilot attempt. All eight revised calls passed the output contract in about 7–12 seconds.
- Added a focused Qwen-envelope test; all 23 reasoning-profile tests passed in 0.13 seconds after the delimiter change.
- Reviewed eight contact sheets and two refined opening-interval sheets, retaining original frames and separate review layouts.
- Froze prompts, model pins, profiles, code hashes, 48 frame identities and RGB labels before any comparison inference.

### Why

- A missing wrapper cannot safely be repaired by searching arbitrary explanation text for JSON.
- Initial uniform sampling underrepresented visible open states. RGB review identified opening intervals for additional reviewed samples before the freeze.

### What worked

- Literal Qwen reasoning tags worked in the second pilot under both decoding modes. Cosmos retained the documented think convention.
- Processed image provenance showed a 480×640 image, grid [1,30,40], and 1200×1536 patch tensor on the pilot frame.
- All new case episode IDs and frame hashes differ from earlier verifier populations.

### What didn't work

- Initial Qwen reasoning pilots returned `incomplete or repeated reasoning envelope`; raw responses contained explanations and final JSON but no requested think delimiters. Preserved them in `various/reasoning-v3/pilot`.
- One valid sampled Cosmos pilot answered open for the reviewed closed frame. Runtime acceptance is not semantic acceptance.
- Remaining episodes do not meet the proposed 8/8/8 label balance. Frozen development is 15 closed, 3 open, 6 unknown; test is 18 closed, 4 open, 2 unknown. Documented that limitation rather than duplicating cases.

### What I learned

- Explicit nonreserved tags can work for a prompted Instruct explanation without requiring a different checkpoint.
- The newer paired corpus includes approach-only episodes; an unseen episode is not automatically a diverse state sequence.

### What was tricky to build

- Both model protocols and selections must precede test inference. The runner requires a complete two-model selection manifest before test mode and checks frozen code identities.
- The experiment retains three seeds for sampled arms and one run for greedy arms; selection averages within each case before comparing arms.

### What warrants a second pair of eyes

- Small side-view microwave labels and near-closed transition frames deserve independent RGB review. This remains assistant-reviewed synthetic evidence.
- Only two unknown test cases and highly correlated opening frames limit broad quality claims.

### What should be done in the future

- Complete the 384-call development comparison, then selected/control test runs and measured report.

### Code review instructions

- Inspect scripts 21–24 and `various/reasoning-v3/protocol.json`, then the original and revised pilot raw outputs.
- Reproduce code/frame hashes and label counts before accepting the frozen population.

### Technical details

- Frozen protocol SHA-256: `629d7769ee9f47cf4cc0634d90e94daa3492f98b034a8b7745742953a208ace3`.
- P1 completion and P2 start printed HTTP 200 at 02:38:51Z and 02:39:23Z on 2026-09-07.
- Main comparison has 24 development cases × (1+1+3+3) runs × two models = 384 calls; selected/control test size depends on development selection.

P2 implementation/pilot/freeze commit: `5aa10eb`. P2 completion and P3 start slips printed successfully at 02:46:51Z and 02:47:12Z on 2026-09-07. Consolidated receipts are in `various/reasoning-print-receipts.json`. P3 development inference started with both model protocols frozen.

## Step 16: Run the frozen comparison and preserve diagnostic panels

Started the sequential 384-call development sweep using the frozen two-model protocol. While execution proceeds, prepared complete-result archiving, per-case aggregation, a declared limited rationale-review sample, and live selected-profile RULES validation. This step is in progress until the final results below are recorded.

### Prompt Context

**User prompt (verbatim):** (see Step 14)

**Assistant interpretation:** Complete the planned comparison and retain enough evidence to distinguish formatting success from factual support.

**Inferred user intent:** Determine whether prompted reasoning improves the actual verifier and document its practical limits.

### What I did

- Started script 24 development mode with immutable code and profile identities.
- Added scripts 25–26 for complete raw records, metrics, test panels, and live handoff validation after selection.
- Added script 27 and visually inspected the first three completed Qwen development panels: closed, open, and unknown.
- Drafted reference 08's frozen method and API explanation while the run continued.

### Why

- Averaging sampled results per case avoids counting seeds as independent visual examples.
- A side-by-side panel exposes unsupported claims that can be obscured by an aggregate accuracy score.

### What worked

- Qwen direct greedy and reasoning greedy each completed 24/24 valid responses, with 18 correct labels and six unsupported answers on unknown cases.
- Both modes correctly classified the visibly open and closed development examples inspected in the panels.
- The original images and short final rationales are readable in the saved comparison panels.

### What didn't work

- Prompted greedy reasoning did not improve Qwen's six unknown development cases. The explanation asserted a visible seated microwave door where the review rubric deemed its state insufficiently inspectable.
- Full development selection and test results remain pending at this checkpoint; no quality winner is declared yet.

### What I learned

- Additional explanation can repeat the same visual mistake instead of correcting it.
- Recorded patch tensors establish input forwarding, not target visibility or semantic correctness.

### What was tricky to build

- Test gating requires both model selections, not just the first completed model. The report tools preserve per-case and per-seed identities while the runner remains unchanged.
- Generation includes cold model setup per call, so wall-clock timing must not be presented as pure token-generation performance.

### What warrants a second pair of eyes

- Review the limited rationale-audit sample definition and prevent its support rate from being extrapolated to every response.
- Inspect case-level scores and episode summaries because the frame population is correlated and imbalanced.

### What should be done in the future

- Finish both development selections, untouched test/control runs, live handoffs, factual-support review, and final measured report.

### Code review instructions

- Read scripts 24–27 and reference 08; trace a saved panel to its frozen frame and raw worker result.
- Use the archived per-call JSONL and protocol identities to reproduce final aggregate tables after completion.

### Technical details

- Reporting/phase-record commit: `e7511f4`.
- Early development diagnostic: Qwen D-G and R-G each 18/24, unknown recall 0/6, no invalid outputs.
- No test outputs had been generated or inspected when these diagnostics were written.
