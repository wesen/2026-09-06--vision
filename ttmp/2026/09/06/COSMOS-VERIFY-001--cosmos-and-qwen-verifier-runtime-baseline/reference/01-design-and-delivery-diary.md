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
