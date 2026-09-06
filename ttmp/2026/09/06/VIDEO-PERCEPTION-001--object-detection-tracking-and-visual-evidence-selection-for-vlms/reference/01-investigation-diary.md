---
Title: Investigation diary
Ticket: VIDEO-PERCEPTION-001
Status: active
Topics:
    - video
    - embeddings
DocType: reference
Intent: long-term
Owners: []
RelatedFiles: []
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T14:52:49.972433-04:00
WhatFor: ""
WhenToUse: ""
---
# Investigation diary

## Step 1: Define a separate visual-perception project

Created VIDEO-PERCEPTION-001 for object detection, tracking, crops, event proposals, and VLM evidence selection. Inspected the current workbench and neighboring design contracts, then wrote a 5,000-word intern guide with a rendered architecture diagram, typed records, pseudocode, API references, evaluation controls, and four implementation phases.

### Prompt Context

**User prompt (verbatim):** "Ok, create a new ticket, Create  a detailed analysis / design / implementation guide that is for a new intern, explaining all the parts of the system needed to understand what it is, with prose paragraphs and bullet point sand pseudocode and diagrams and api references and file references. It should be very clear and technical. Store in the ticket and the nupload to remarkable."

**Assistant interpretation:** Create and deliver a technical project design for conventional vision preprocessing that augments VLM inference.

**Inferred user intent:** Give a new intern enough context and concrete implementation guidance to build and evaluate this missing subsystem.

### What I did

- Used docmgr to create the ticket, design guide, and diary.
- Inspected media, registry, embedding, index, API, tests, dependencies, and neighboring verifier/state/temporal designs.
- Checked primary Ultralytics, PyTorch, OpenCV, and ByteTrack references on 2026-09-06.
- Rendered the proposed architecture from `scripts/01-architecture.dot`.
- Kept all new artifacts local to this ticket; did not alter the concurrent corpus or MLX work.

### Why

- Existing full-frame cache keys cannot safely identify different crops at one timestamp.
- Detector class predictions, tracked identities, visual states, and action intervals require separate contracts and evaluations.

### What worked

- Existing PTS/source-hash infrastructure provides a reusable integration boundary.
- The official detector/tracker APIs provide a concrete first adapter; the guide marks future application APIs as proposed.

### What didn't work

- A discovery command returned `rg: docs/playbooks: IO error for operation on docs/playbooks: No such file or directory (os error 2)`. Used existing ticket guides and inspected source instead.
- The Python launch printed `pyenv: cannot rehash: /Users/manuel/.pyenv/shims isn't writable`; the guide-generation command still exited successfully. No environment configuration was changed.

### What I learned

- The inspected embedding cache has no crop-coordinate component, so focused evidence needs a distinct identity contract.
- Standard COCO vocabulary does not cover every proposed household prop, including lightswitches and table lamps.

### What was tricky to build

- A tracker ID must not become an assumed simulator entity ID. The design separates local visual tracks, reviewed entity bindings, and downstream state observations.
- Crop and proposal selection can introduce future evidence. The guide defines source, evidence, and availability times separately.

### What warrants a second pair of eyes

- Crop geometry and browser letterboxing; detector class mapping; causal timing; budget-matched recognition ablations; held-out grouping.

### What should be done in the future

- Complete D1–D4 implementation tasks. No detection runtime or local performance result is claimed by this documentation work.

### Code review instructions

- Start with guide Sections 3–5 and compare symbol anchors to the current workbench.
- Review all proposed acceptance tasks before selecting a model or installing packages.

### Technical details

- Inspected base commit: `de014edd18e7ee00324c83a88139d4ee481415c9`.
- Diagram source and rendered image are stored in this ticket.
- Current external API pages are mutable; implementation must pin installed packages and model artifacts.

## Step 2: Review and deliver the 14-page guide

Rendered the completed guide with Pandoc/XeLaTeX and reviewed every page using Ghostscript raster contact sheets. Corrected long-path table overlap, unbroken inline identifiers, and a tracking pseudocode footer collision. Uploaded the corrected guide to reMarkable after a successful dry-run.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Deliver a readable technical document, preserving local source and validation evidence.

**Inferred user intent:** Read the complete intern implementation plan on reMarkable and return to a traceable ticket later.

### What I did

- Added ticket-local rendering and upload scripts with source-hash checks.
- Ran `docmgr doctor --ticket VIDEO-PERCEPTION-001 --stale-after 30`; all checks passed.
- Rendered the PDF, inspected contact sheets and affected pages, and checked ink bounds.
- Ran `scripts/02-deliver-guide.py dry-run`, followed by the authorized `upload` mode.
- Marked documentation and delivery tasks complete; implementation tasks remain open.

### Why

- Markdown correctness does not ensure that code blocks and file references fit an e-reader PDF.

### What worked

- The final PDF has 14 pages, a table of contents, an actual architecture figure, readable code, and source/API references.
- Upload returned `OK: uploaded VIDEO-PERCEPTION-001_Intern_Guide.pdf -> /ai/2026/09/06/VIDEO-PERCEPTION-001`.
- Positive upload receipt, dry-run receipt, PDF hashes, and visual validation are retained in `various/`.

### What didn't work

- Initial layout had overlapping long file paths in the source table and clipped inline identifiers. Shortened table labels while documenting their directory mappings.
- A reflow placed the tracking pseudocode into the footer. Added an explicit page break before that block and re-reviewed affected pages.

### What I learned

- Bounding-box checks catch margin overflow but cannot alone detect internal table or footer collisions; visual review is necessary.

### What was tricky to build

- The reviewed source changed during layout repair. Re-rendered and regenerated the dry-run receipt after the final edit so delivery checks used the same source hash.

### What warrants a second pair of eyes

- The proposed detector/tracker adapter still needs actual package/version smoke testing during D1. This deliverable validates documentation layout, not runtime capability.

### What should be done in the future

- Implement D1–D4 from `tasks.md`, starting with coordinates, source identity, class coverage, and one reviewed detector episode.

### Code review instructions

- Read `various/pdf-validation.json` and `various/remarkable-upload.json` for delivery evidence.
- Open `various/pdf/VIDEO-PERCEPTION-001_Intern_Guide.pdf` for the local rendered guide.

### Technical details

- Renderer: Pandoc/XeLaTeX, Helvetica/Menlo, 11pt body, 0.8-inch margins.
- QA: Ghostscript PNG pages, contact sheets, and ink bounds.
- No runtime files or git state were changed by this side-conversation ticket work.

## Step 3: Start complete perception implementation and state follow-up

The user authorized the complete YOLO perception project and a subsequent return to state recognition. Began with source-coordinate/provenance contracts and an isolated Torch environment. The completed state run remains the frozen full-frame comparison; its labels and test results will not be used to select detector thresholds or crops.

### Prompt Context
**User prompt (verbatim):** "Do the whole yolo thing and then continue with the state ticket"

**Assistant interpretation:** Implement D1–D4, preserve the visual trail, then compare perception-derived evidence in the state task.

**Inferred user intent:** Build the missing visual pipeline end to end and measure whether it improves the weak state baseline.

### What I did
- Read the perception task list and investigation diary, and rechecked current official prediction/tracking/model documentation.
- Started an isolated Python 3.11 environment with a hash-locked dependency set; no MLX environment mutation.
- Added pure box geometry, crop transforms, packet/citation validation, and atomic artifact publication.
- Submitted the complete D1–D4/state-follow-up work-slip plan.

### Why
- Detection, track association, crop identity, visual state, and action proposals require distinct contracts before model integration.

### What worked
- Dependency resolution selected Ultralytics 8.4.142; exact versions and distribution hashes are retained in the lock.
- Existing source registry and presentation-time decoder can be reused without simulator labels entering inference.

### What didn't work
- A discovery command included absent `.agents`, producing `rg: .agents: No such file or directory (os error 2)`; no applicable AGENTS file was found in the workspace.
- Initial lock generation echoed a long dependency list; subsequent tool output is bounded.

### What I learned
- Current vendor documentation has evolved since the earlier design; implementation will inspect and pin the actual installed tracker interface.

### What was tricky to build
- Preserve the old state result while adding richer representations. The experiment will freeze evidence policies before scoring, and report post-baseline test reuse explicitly.

### What warrants a second pair of eyes
- Entity binding, crop coordinates, class vocabulary gaps, and causal versus offline evidence timing.

### What should be done in the future
- Complete detector CPU/MPS smoke, reviewed pilot, tracking, packets, gallery, and state comparison.

### Code review instructions
- Start with `perception/contracts.py` and `store.py`; inspect the isolated lock before running vendor code.

### Technical details
- Starting revision: `069174a`.
- Inference will use local pinned YOLO11 nano weights; mask support will receive a bounded real-output probe, separately from the box baseline.

## Step 4: Validate the detector runtime and start native-cadence inference

Installed the isolated lock and ran identical training pixels on CPU and MPS. Both produced source-aligned detections; MPS warm inference was faster on this one-frame smoke. Started inference on all 60 source episodes: all 48 diversified household videos plus the 12 original microwave training videos required by the state comparison.

### Prompt Context
**User prompt (verbatim):** (see Step 3)

**Assistant interpretation:** Establish a measured detector and reusable artifacts before tracking and state comparison.

**Inferred user intent:** See actual visual outputs and make implementation decisions from the Mac's measured behavior.

### What I did
- Downloaded official YOLO11 nano detection and segmentation weights and retained their local artifact hashes in model manifests.
- Ran CPU/MPS on the same RGB frame and saved both overlays.
- Inspected installed ByteTrack source: this version uses `BYTETracker(args)`, without a frame-rate constructor parameter.
- Added private session ID counters and class-separated tracker instances, gap/shot resets, predicted-lost observations, and prefix-replay tests.
- Implemented completed-bin causal proposals, periodic full-scene fallback, and explicit rejection reasons.
- Six perception contract/tracking/proposal tests pass.

### Why
- The detector runs every native frame while expensive visual evidence is selected separately. Sparse inference must not be passed to ByteTrack as adjacent frames.

### What worked
- CPU warm times: 47.7, 50.4, 48.8 ms; MPS: 17.8, 12.2, 9.0 ms. First calls cost 2.61s and 3.10s respectively.
- Plan slip confirmed printed at `2026-09-06T19:59:43Z`, HTTP 200.
- Package installation completed after 6m17s of downloads, including Torch's large shared library.

### What didn't work
- macOS logged duplicate `AVFFrameReceiver` / `AVFAudioReceiver` classes from PyAV and OpenCV FFmpeg bundles. The smoke still completed; no library files were removed or renamed.
- Relative `YOLO_CONFIG_DIR` caused vendor fallback to `/tmp/Ultralytics`; created and supplied an absolute workspace directory for subsequent runs.
- A sandbox `ps` inspection returned `operation not permitted`; authorized escalation showed an active Torch download rather than a hung process.

### What I learned
- Vendor track IDs are process-global by default. Creating independent class trackers can reset another tracker's numbering unless the adapter owns private counters.

### What was tricky to build
- The low-score ByteTrack association is also class-agnostic. Class-separated sessions preserve class compatibility across both association stages without patching vendor matching internals.

### What warrants a second pair of eyes
- Measured speed is a one-frame smoke, not full-video throughput. Actual per-frame timing is retained during the full run.

### What should be done in the future
- Review fixed-grid target boxes and contiguous identity spans; derive crops and packets from the stored detections.

### Code review instructions
- Compare CPU/MPS overlays, `detector-smoke.json`, `tracking.py`, and the actual tracker signature recorded by the smoke script.

### Technical details
- Detector floor 0.10, reporting/new-track threshold 0.25, NMS IoU 0.70, fixed 640×640 letterbox input. PIL supplies RGB; returned coordinates are validated in 640×480 source pixels.
- Tracker buffer is ten native 10 Hz updates (one second). Excessive gaps reset; unsupported variable cadence rejects.
