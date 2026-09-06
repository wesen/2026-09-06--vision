---
Title: Project design and delivery diary
Ticket: COSMOS-VIDEO-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/scripts/14-validate-project-guides.py
      Note: Documentation example and link checks
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/scripts/15-render-upload-project-guides.py
      Note: Per-ticket render and delivery recipe
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/scripts/16-review-project-pdfs.py
      Note: 48-page raster review artifacts
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T13:36:57.241765-04:00
WhatFor: ""
WhenToUse: ""
---


# Diary

## Goal

Record decomposition of the umbrella into eight independently designed project tickets, technical/PDF review, and per-ticket reMarkable delivery. Child diaries contain their individual design and implementation boundaries.

## Step 1: Create the eight project designs

Created separate tickets for the embedding runtime, five application projects, verifier runtime, and VirtualHome expansion. Each has an approximately 1,700-2,000-word intern guide with diagrams, proposed API contracts, pseudocode, phased tasks, review fixtures, acceptance gates, and references to actual repository files. The umbrella now links to their task lists and explains shared ownership and reading order.

### Prompt Context

**User prompt (verbatim):** "Ok, create the tickets, and Create  a detailed analysis / design / implementation guide that is for a new intern, explaining all the parts of the system needed to understand what it is, with prose paragraphs and bullet point sand pseudocode and diagrams and api references and file references. It should be very clear and technical. Store in the ticket and the nupload to remarkable."

**User prompt (verbatim):** "for each"

**User prompt (verbatim):** "use virtual home instead of habitat btw"

**User prompt (verbatim):** "you don't need to print so many slips, only when something meaningful has been done / is about to start"

**Assistant interpretation:** Create one complete design/guide/ticket per project, use VirtualHome exclusively in the active simulator plan, and limit printing to meaningful milestones.

**Inferred user intent:** Give a new intern concrete, independent work packages with enough context to implement them correctly and read them on reMarkable.

**Commit (designs):** `edd3d34` — `docs(vision): split roadmap into eight intern-ready project tickets`.

### What I did
- Used docmgr to create eight ticket workspaces, dedicated design documents, and diaries.
- Inspected current generator/configuration/labels, existing teaching APIs, and prior design documents.
- Rechecked primary runtime/model/API references; distinguished vendor capabilities from unmeasured local behavior.
- Wrote the dependency map and replaced the umbrella's broad unchecked project tasks with links to child task lists.
- Marked old simulator alternatives as historical; active corpus work extends VirtualHome.
- Ran `scripts/14-validate-project-guides.py`: document structure, Python pseudocode syntax, JSON parsing, SQL schema, and local links passed.
- Ran docmgr doctor for all eight child tickets: all passed.

### Why
- Project-level contracts and acceptance gates make implementation assignable and independently reviewable.
- Label calibration is necessary before stronger state/timing claims, even though corpus integrity checks already pass.

### What worked
- Eight guides with compatible time, feature identity, evidence, and split policies are now in their tickets.
- Proposed workbench modules are clearly distinguished from the existing generator and teaching code.

### What didn't work
- Browsing a guessed MLX-VLM embedding directory returned `Cache miss`; the design uses the verified README and requires inspecting the installed entry point.
- Initial `git diff --cached --check` reported `changelog.md:11: new blank line at EOF.` on the eight generated changelogs. The shell command continued and committed; trailing blank lines were removed afterward and the final staging check is enforced separately.
- The PDF operation helper was not at repository `container_tools/`; its installed PDF-skill path was found and the operation marker succeeded before authoring the eight PDFs.

### What I learned
- A frozen evidence cutoff differs from a later verifier result's availability. The rule design was corrected so new evidence proposals are not backdated into old fact views.
- Runtime candidates must preserve named native-video versus multi-image/frame-pooled modes instead of silently falling back.

### What was tricky to build
- Splitting the program risks circular dependencies and conflicting schema ownership. The map assigns ownership and allows oracle/model-free fixtures before integration.
- Current corpus graph labels cannot support all requested temporal metrics. Every guide makes the appropriate data-quality gate explicit.

### What warrants a second pair of eyes
- Downstream evaluation assumptions, particularly reviewed visibility, boundary uncertainty, and independent split units.
- Actual vendor signatures and model conversion fidelity when implementation begins.

### What should be done in the future
- Execute the embedding runtime and search tickets first; calibrate VirtualHome labels before stronger temporal claims.

### Code review instructions
- Start with the project ticket map, then follow a child guide and its phase checklist.
- Run the documentation validator and docmgr doctor after edits. These are documentation checks, not model integration tests.

### Technical details
- Ticket inventory: `various/project-tickets.json`.
- Documentation checks: `various/project-guide-validation.json`.
- User printing correction supersedes the earlier fine-grained phase-slip plan; subsequent printing is reserved for the substantial completed delivery milestone.

## Step 2: Review 48 pages and deliver eight individual guides

Rendered each guide as six pages, inspected all pages through contact sheets, and checked one API/code/diagram page per guide at larger raster size. All eight dry runs and actual uploads succeeded. Per-ticket diaries, indices, and receipts now record delivery; 107 application implementation tasks remain open.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Complete independent reMarkable delivery for every project after review.

**Inferred user intent:** Have the complete guide set available on the device with an auditable local source.

### What I did
- Ran the PDF skill's operation marker successfully for eight PDF outputs.
- Used the existing Pandoc/XeLaTeX layout with individual ticket headers.
- Ran shared render, raster-review, dry-run, and upload scripts; verified every positive upload receipt.
- Recorded source/PDF hashes, 48 reviewed pages, and per-ticket destinations in `various/project-guide-delivery.json`.
- Kept all application implementation tasks unchecked; only design/delivery tasks are complete.

### Why
- Each project needs a standalone readable guide, not merely a link into one large umbrella document.

### What worked
- Eight six-page PDFs; no visible clipping, overlap, missing glyphs, or split code/diagram blocks in reviewed pages.
- All uploads returned `OK: uploaded`; no redundant cloud listings were needed.

### What didn't work
- Optional local PDF Python modules were absent; Ghostscript supplied rasterization, text extraction, and ink bounds.
- No rendering, dry-run, or upload failure occurred.

### What I learned
- Approximately 15,000 words across eight focused guides produced a manageable 48-page reading set.

### What was tricky to build
- Per-ticket source hashes were frozen after file relations and verified before upload. Subsequent bookkeeping edits affect diaries/tasks rather than the uploaded guide source.

### What warrants a second pair of eyes
- Actual runtime capability and evaluation assumptions remain implementation work; PDF checks do not substitute for those experiments.

### What should be done in the future
- Start COSMOS-EMBED-001 and VIDEO-SEARCH-001; schedule VirtualHome label calibration before precise temporal evaluation.

### Code review instructions
- Follow the ticket map and delivery inventory to source guides, review evidence, and individual receipts.

### Technical details
- Remote pattern: `/ai/2026/09/06/<TICKET-ID>/<TICKET-ID>_Intern_Guide.pdf`.
- Local PDFs: `output/pdf/project-guides/<TICKET-ID>/`.
- The inspected local PDF hash is recorded; uploads use the same reviewed source and renderer configuration, without claiming remote-byte identity verification.

### Final validation and milestone receipt

Docmgr doctor passed for the umbrella and all eight child tickets. The final documentation validator and whitespace check passed. All eight individual upload receipts contain a positive success result. One substantial completion slip printed at 17:40:59 UTC (HTTP 200, printer OK, 384x380), respecting the user's revised preference to avoid frequent small-phase slips. The two original root input files remain untracked and unchanged; generated PDFs/raster QA remain under ignored `output/`.
