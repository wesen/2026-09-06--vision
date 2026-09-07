---
Title: Implementation diary
Ticket: VIDEO-LAB-UI-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/lab/__main__.py
      Note: Tailscale and loopback listeners
    - Path: repo://workbench/src/video_workbench/lab/browser.html
      Note: Separate searchable project browser
    - Path: repo://workbench/src/video_workbench/lab/resources.py
      Note: Curated resources and Markdown/source renderer
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-07T10:05:37.359166-04:00
WhatFor: ""
WhenToUse: ""
---


# Implementation diary

## Goal

Build an educational video experiment workbench with reproducible evidence, real component execution, and staged browser review.

## Step 1: Define the experiment contract and intern guide

Inspected the existing media, perception, embedding, verifier, temporal and replay adapters. Created a six-phase design that keeps evidence immutable while allowing interactive parameter changes. The guide explains mathematical operations and their limits before presenting the proposed API and implementation sequence.

### Prompt Context

**User prompt (verbatim):**

Ok, Create a new docmgr ticket to flesh out the UI. Create  a detailed analysis / design / implementation guide that is for a new intern, explaining all the parts of the system needed to understand what it is, with prose paragraphs and bullet point sand pseudocode and diagrams and api references and file references. It should be very clear and technical. Store in the ticket and the nupload to remarkable.
Then implement, commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done.

After each significant feature, run the web UI and allow me to play with it to give you feedback. Also make sure to write a detailed guide / explanation on each page about what the different components are, what the different options mean, what the maths is behidn it, etc... This could be both hover help text but also a guide tab or foldout.

**Assistant interpretation:** Create, document, deliver and implement an experiment workbench, with in-page teaching and user feedback at feature boundaries.

**Inferred user intent:** Make the system understandable and experimentally useful, especially when valid model answers are visually wrong.

### What I did

- Read docmgr, diary, brutalist-work-slip, remarkable-upload and textbook-authoring skills.
- Created VIDEO-LAB-UI-001 and the intern guide; mapped existing source APIs and separate inference environments.
- Printed the six-phase plan (HTTP 200, printed true, 2026-09-07T14:06:01Z).
- Started guide delivery using the skill-prescribed remarquee bundle command.

### Why

- The current replay only connects camera departure and exact-image verification; experimentation needs direct access to intermediate components.

### What worked

- Existing adapters provide reusable timestamp, feature identity, mask, tracking and bounded verification contracts.

### What didn't work

- No new failure in this step. Existing native-video reasoning remains unsupported by the accepted verifier contract.

### What I learned

- Tracking requires explicit cadence; reasoning currently accepts one image; pooled and native feature identities are incompatible.

### What was tricky to build

- Separating planned UI capabilities from already accepted runtime modes. The guide labels single-image sequences accurately and requires exact checkpoint/preprocessing identity for action heads.

### What warrants a second pair of eyes

- Review experiment bounds and state-transition semantics before relying on derived events.

### What should be done in the future

- Implement the six phases and update proposed API references to the final schema.

### Code review instructions

- Read the intern guide, especially sections 5, 8, 9 and 12. Compare referenced symbols against workbench/src/video_workbench.

### Technical details

- Baseline commit: 881cb1f. Source originals procedural_video_labs.zip and video_understanding_for_procedural_work.md are unrelated and remain untracked.
- Guide destination: /ai/2026/09/07/VIDEO-LAB-UI-001.

## Step 2: Deliver guide and expose exact evidence workspace

Implemented the first usable laboratory page with 121 corpus-qualified sources, PTS-based sampling, normalized crops, exact PNG previews and component-specific teaching panels. The page is running on port 8780 and the user has been invited to try it before further UI decisions.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Deliver a working evidence-selection feature and ask for feedback while developing independent inference adapters.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

### What I did

- Created lab catalog, contracts, evidence preparation, FastAPI app and responsive HTML UI.
- Uploaded Video Laboratory Intern Design Guide.pdf to /ai/2026/09/07/VIDEO-LAB-UI-001.
- Captured various/p2-workspace.png and ran two focused smoke tests.

### Why

Exact inputs and corpus identity must exist before component outputs can be compared.

### What worked

- reMarkable reported OK: uploaded.
- Browser selected home-v1--ep-7d3106fb1cac9776 and decoded two exact frames without error.
- pytest workbench/tests/test_lab.py: 2 passed.

### What didn't work

- Initial upload: Error: pandoc failed: xelatex not found. Fixed PATH=/Library/TeX/texbin:$PATH and explicit Helvetica/Menlo fonts using the existing TeX installation.
- Initial server startup: ValueError: conflicting source identity. Corpus versions reuse episode IDs with different bytes; fixed by dataset-qualified laboratory IDs.
- Browser initially reported a missing favicon; no application execution failure.

### What I learned

121 model-safe recordings are available across corpus versions, considerably more than the twelve replay measurement recordings.

### What was tricky to build

An episode ID is only unique within a corpus version. The catalog retains original_episode_id for artifact matching but uses dataset--episode_id as the UI identity; hashes remain authoritative.

### What warrants a second pair of eyes

Check crop and timestamp presentation and whether the shared layout leaves enough room for model controls.

### What should be done in the future

Connect immutable run supervision and actual perception/reasoning execution, then review the UI again.

### Code review instructions

Read lab/contracts.py, evidence.py and catalog.py. Run PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_lab.py -q. Try http://127.0.0.1:8780/.

### Technical details

Design commit 37e1019. Server process 28859. Preview maximum 64 actual samples; full-frame evidence unchanged by browser seeking. Plan and P1 start slips printed at 14:06:01Z and 14:06:20Z.

## Step 3: Serve the laboratory over Tailscale and add a project browser

The user reviewed the evidence workspace and asked for tailnet access, linked resources, and a separate project browser with rendered Markdown. Added explicit interface binding and a searchable document/source browser without changing the unfinished model-execution stage.

### Prompt Context

**User prompts (verbatim):**

> can you serve it such that I can access it over http://mimimi:8780/ over tailscale (i'm on the same tailscale network)

> is "run experiment" still disabled?

> add links to resources (on the net, locally as markdown, links to the source which you can serve as well, with syntax highlighting). That way we can really get some insight into it all.

> also render markdown files. maybe it should be a different page that is just a project browser really.

**Assistant interpretation:** Expose the existing workspace on the tailnet and make local implementation and documentation browsable beside experiments.

**Inferred user intent:** Read deeply into the system while trying it from another device.

### What I did

- Added repeatable --host binds; verified HTTP 200 from mimimi and 100.113.140.75 on port 8780.
- Added lab/resources.py and browser.html: 179 indexed code/Markdown resources, filtered tree, rendered Markdown, highlighted source, line anchors and raw views.
- Added component-specific source, report and official-resource links to each guide.
- Checked official Ultralytics, Qwen, Cosmos and PyAV pages. Declared existing markdown-it-py/Pygments dependencies in pyproject.toml.
- Captured p3-project-browser-markdown.png and p3-project-browser-source.png in various/.

### Why

The experiment controls need a direct path to both explanatory documents and the code that implements their semantics.

### What worked

- Browser reached http://mimimi:8780/resources over the Tailscale hostname.
- Intern guide rendered 14 top-level/section headings and three tables. Native video source rendered highlighted lines with anchors.
- Focused smoke: 3 passed. Unknown resource IDs and path traversal attempts return 404; raw source is plain text.

### What didn't work

- tailscale ip -4 warned: client version "1.41.0-ERR-BuildInfo" != tailscaled server version "1.98.10-t0ee734d30-g6b4108809". Address discovery and HTTP access succeeded despite this warning.
- Existing Starlette/httpx and AnyIO deprecation warnings remain in test output.
- Run experiment remains disabled at this checkpoint; inference files were drafted before interruption but are not yet integrated or committed.

### What I learned

Current upstream documentation can show newer YOLO examples than the local YOLO11 checkpoint; resource descriptions must make that difference explicit.

### What was tricky to build

Relative Markdown links must resolve through the indexed project catalog rather than expose arbitrary paths. The renderer rewrites known links, marks unindexed references unavailable, escapes raw HTML and adds a restrictive CSP. The embedded reader permits user-initiated top-level navigation for its back links without allowing document scripts.

### What warrants a second pair of eyes

Review tree organization, reading width and links from actual reports containing figures. Current working-file hashes are not historical commit identities.

### What should be done in the future

Continue the model execution phase after the resource-browser feedback opportunity. Add any newly implemented components to their curated reading paths.

### Code review instructions

Start with lab/resources.py: Resources.path, rewrite, render and attach; inspect browser.html and test_project_reader_and_resource_boundaries. Open http://mimimi:8780/resources and search for native_video or COSMOS-VERIFY.

### Technical details

Workspace commit eab4b83. Current server has listeners on 127.0.0.1 and 100.113.140.75, port 8780. The Project browser is a separate page; experiment selection remains in its original tab. No new package installation was necessary.

## Step 4: Enable real perception and bounded reasoning experiments

Connected the browser to a one-worker experiment supervisor. Real YOLO segmentation and Qwen inference completed from the UI, preserving exact input images and configuration; Cosmos is being checked on the same image. Same-origin replay routes now work for tailnet clients as well.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Continue the approved component workbench after incorporating the resource-browser request.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

### What I did

- Added manager.py and worker.py for fixed-environment execution, total deadlines, cancellation and saved status.
- Enabled Run experiment, live progress, run history, structured input/result inspection and mask/box overlays.
- Connected accepted verifier profiles and parsing directly in the supervised worker.
- Added cancellation and state-transition boundary tests.

### Why

Model controls are useful only when they execute real adapters and retain enough evidence to diagnose wrong answers.

### What worked

- YOLO11n-seg run-8fda97b444ed459c completed in 4.64 s on two frames; overlays show the target missing at 9.5 s and detected at 10.0 s.
- Qwen run-86eba27c442048b7 completed in 7.83 s, returning a schema-valid CLOSED answer on the selected fridge frame.
- Five focused tests passed, including terminating and reaping a real subprocess on cancellation.
- Saved segmentation and Qwen result screenshots.

### What didn't work

PyAV/OpenCV again emitted duplicate AVFFrameReceiver/AVFAudioReceiver Objective-C class warnings; the YOLO run completed. Qwen's structurally valid answer is not a visual accuracy acceptance result.

### What I learned

The new UI exposes the difference between model output validity and factual visual correctness without needing the replay scheduler.

### What was tricky to build

Worker cancellation must terminate the entire process group while leaving a durable terminal status. The model runtime cannot run in the HTTP thread. Current form edits must not change saved result labels; renderResult uses the immutable request.

### What warrants a second pair of eyes

Review timestamp/crop provenance on saved runs and the distinction between a completed process and a valid/correct model answer.

### What should be done in the future

Finish both-model smoke and enable comparisons, reviews, embedding plots and explicit state/rule experiments.

### Code review instructions

Read lab/manager.py admission/supervision, worker.py perception/reasoning adapters and viewer.html renderResult. Run the five test_lab.py checks; inspect the saved run artifacts and screenshots.

### Technical details

Fixed runtimes retain venv executable paths without resolving symlinks. Admission allows one expensive worker; selections max 64 images and embeddings max 128 windows. The worker has no client-provided executable or checkpoint path.

## Step 5: Compare representations and expose state/rule review workflows

Native FP32 and pooled embeddings now execute on the same selected windows, producing separately identified feature spaces and query-score plots. Added comparisons that check pixel/timestamp identity before displaying outcomes, independent user review/export, explicit point-rule evaluation, and source-matched frozen action inspection.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Complete the experiment loop from component execution to comparison, review and reusable evidence.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

### What I did

- Added analysis.py and analysis.js for evidence comparison, score plots, reviews, exports, presets and exact-point rules.
- Added a saved-results-only action viewer that matches source hashes and original temporal windows.
- Verified Qwen/Cosmos side-by-side comparison reports identical visual evidence and a model-only configuration difference.
- Ran native and pooled embedding experiments on 8–12 s at 2 FPS with identical windows and query.

### Why

Results need to be comparable without mixing incompatible feature vectors or silently substituting nearby state samples.

### What worked

- Native run-c91ef4d1a5c54ed9: 4 windows, 11.22 s.
- Pooled run-cb3fcc4c7afa4e55: 4 windows, 5.88 s.
- Cosmos run-813cb7b91060423b: 8.46 s, valid CLOSED answer.
- Six focused tests passed, including PASS/VIOLATION/UNKNOWN at exact versus missing timestamps.
- Saved p5-matched-reasoning-comparison.png.

### What didn't work

No new runtime failure in this step. Frozen action predictions intentionally remain labeled saved results only; they are not newly executed action-head inference.

### What I learned

The matched model comparison is useful even when both models make the same answer: it exposes common visual failure while holding the input pixels fixed.

### What was tricky to build

Feature-space identity and visual-input identity are different checks. Comparisons require the latter for controlled evidence, while native/pooled score plots remain separate. Rule evaluation uses the existing evaluator and exact sample times; the user-selected trigger is explicitly not a detected event.

### What warrants a second pair of eyes

Review that action inspection excludes weak labels and filters original windows fully contained in the selection. Review exports must retain source partitions.

### What should be done in the future

Complete the state/tracking/action browser smoke, archive final API schema and model summaries, and update the intern guide to the delivered behavior.

### Code review instructions

Read lab/analysis.py compare, point_rule and action_artifacts; inspect analysis.js rendered comparisons and review binding. Test a rule at an exact state timestamp and 0.1 s later.

### Technical details

Perception/reasoning feature commit 03eaa80. Native and pooled output vectors are stored separately in per-run vectors.npz; no cross-space dot product occurs. Resource browser commit ff06003.
