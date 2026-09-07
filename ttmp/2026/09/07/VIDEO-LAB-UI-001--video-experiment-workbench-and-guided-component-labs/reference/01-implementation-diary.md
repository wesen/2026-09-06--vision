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
    - Path: repo://workbench/src/video_workbench/lab/handoff.py
      Note: Detector crop resolution and provenance validation (bc4916f)
    - Path: repo://workbench/src/video_workbench/lab/presentation.py
      Note: Shared prompt preview and safe highlighted YAML rendering
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

## Step 6: Finish fresh action inference, live smoke and delivery

Completed the fresh action-head adapter and the final browser/API checks. The laboratory remains available over Tailscale, and the updated intern guide plus measured walkthrough were uploaded as a new reMarkable document. User feedback opportunities were offered after the evidence workspace, project browser, model execution and comparison features.

### Prompt Context

**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Finish the authorized workbench implementation and preserve a reproducible technical handoff while leaving the UI available for review.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

**Commit (code):** 21dc706 — Add compatible fresh action heads and finalize guided lab behavior

### What I did

- Added fresh native and pooled ridge action inference with matching encoder/checkpoint identities and enforced training sampling policy.
- Added per-image verifier deadlines and complete reasoning-checkpoint identity; ran the final Qwen smoke after that change.
- Archived the final OpenAPI schema, live API smoke, model run identities and screenshots.
- Updated workbench README, intern guide and delivered API walkthrough.
- Uploaded Video Laboratory Delivered Guide and Walkthrough.pdf to /ai/2026/09/07/VIDEO-LAB-UI-001 (OK: uploaded).

### Why

Fresh component execution, readable source and evidence-bound comparison must all work together before the workbench is useful for experiments.

### What worked

- Fresh native ridge run-2b41c5b71eba45ee completed in 10.41 s; pooled ridge run-354329c3cd2542a3 in 5.26 s.
- Qwen two-image state run-fc7db205cb284dcd completed in 13.18 s.
- YOLO/ByteTrack run-7e52c6665e804620 produced 10 records in 4.53 s.
- Final Qwen identity/deadline run-832f394de7414eab completed in 13.41 s.
- Seven focused tests passed. Live API smoke verified 8 frozen-action rows, exact PASS, missing-time UNKNOWN, independent review persistence and test-partition-preserving export.
- Native/pooled comparison asserted matched evidence and different feature spaces. Browser console reported zero errors/warnings.

### What didn't work

No new final smoke failure. Action accuracy remains weak: native ridge predicted WALK on initial scene windows, which is recorded as model output rather than an accepted event. Current Markdown reader leaves Mermaid fences as code. Multi-image/video reasoning and fresh TCN execution remain unoffered modes.

### What I learned

Fresh action inference can reuse the existing trained ridge models safely only by checking the complete encoder description against the frozen training manifest, not merely matching vector dimensions.

### What was tricky to build

The trained action space wraps encoder identity and dataset policy; the adapter separately validates the encoder digest, feature manifest hash and head space ID. Selection-start context resets are disclosed. Final server reload occurred only after verifying no active laboratory run; the UI remains bound to loopback and Tailscale.

### What warrants a second pair of eyes

User review of experimental ergonomics and visual model failures. The laboratory's single worker does not coordinate GPU usage with the separate replay manager or external processes. The automated smoke review is explicitly unjudgeable and is not a human accuracy label.

### What should be done in the future

Use feedback and reviewed failure cases to choose the next improvements. Keep unsupported modalities explicit; do not infer that a successful smoke establishes model quality.

### Code review instructions

Open http://mimimi:8780/ and /resources. Read the delivered walkthrough, inspect various/final-api-smoke.json and measured-runs.json, and run PYTHONPATH=workbench/src workbench/.venv/bin/python -m pytest workbench/tests/test_lab.py -q. Source readers expose #L anchors and current file SHA-256.

### Technical details

Final server process 32382, exec session 79936, explicit listeners 127.0.0.1:8780 and 100.113.140.75:8780. Source originals remain untracked. No source push was requested. Meaningful printed receipts: browser done 14:28:37Z; P3/P4 14:33:46Z; P4/P5 14:39:19Z; P5/P6 14:45:09Z, all HTTP 200 printed true. Early code commits: 37e1019 design, eab4b83 workspace, ff06003 project browser, 03eaa80 real model runs, 79f6bd3 comparisons.

Final delivery receipt: P6 completion slip printed successfully at 2026-09-07T14:51:23Z (HTTP 200, printed true). Final project browser indexed 182 Markdown/source resources and rendered the delivered walkthrough over mimimi:8780. Ticket doctor passed; all six implementation tasks are checked. Ticket remains active for user feedback.

## Step 7: Separate source directories and ticket browsing

Applied the user's typography and navigation feedback. The project browser now has separate Code and Tickets sections, and source/Markdown code uses a sans-serif font while preserving syntax highlighting and line anchors.

### Prompt Context

**User prompt (verbatim):** "sans-serif for code. nice directory style browser for the code. Separate section for the tickets."

**Assistant interpretation:** Use a true source directory hierarchy and give ticket documents their own navigation section.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

### What I did

- Replaced the mixed resource list with Code/Tickets navigation, nested directories, folder expansion state, file-type labels and path breadcrumbs.
- Added source tests and ticket overview/tasks/changelog files to the indexed resources.
- Changed code fonts in the source reader, Markdown code and experiment JSON views to system-ui sans-serif.
- Captured p7-code-directory-browser.png and p7-ticket-browser.png.

### Why

Source navigation should follow actual directories; ticket material should be grouped by ticket rather than interleaved with code.

### What worked

Browser smoke found 13 code directories and no ticket entries in Code. The Tickets view contained no source entries and showed all seven matching VIDEO-LAB-UI-001 documents. Computed source font was system-ui, sans-serif and #L42 remained available.

### What didn't work

No failure during this change.

### What I learned

Ticket overview, tasks and changelog belong in the project browser alongside designs and reports, not just the original design/reference index.

### What was tricky to build

Selection, section switching and browser history share URL state. Direct file links infer their section when absent; searches filter within the selected section and folder expansion persists during navigation.

### What warrants a second pair of eyes

Try the directory hierarchy and ticket grouping from the user's device; verify reading comfort with proportional code text.

### What should be done in the future

Incorporate further browsing feedback as needed.

### Code review instructions

Inspect browser.html directoryTree, switchSection and restore; resources.py font styles and explicit catalog expansion. Try /resources?section=code and /resources?section=tickets.

### Technical details

Server restarted only after confirming no active run; now PID 33408, exec session 32592, serving loopback and Tailscale on port 8780. This presentation-only change used browser smoke rather than rerunning model inference.

## Step 8: Capture report evidence and continue the saved-run workflow

Captured the updated Code and Tickets browser for the future report, then continued with clickable saved-run timelines and settings restoration. The timeline owns a player bound to the saved recording, keeping inspection separate from the editable experiment configuration.

### Prompt Context

**User prompts (verbatim):**

> ok, cool. Take screenshots btw for the diary / a future report.

> then continue

**Assistant interpretation:** Preserve screenshot evidence while continuing practical improvements to experimentation.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

### What I did

- Captured p8-worker-source-browser.png and p8-ticket-report-browser.png.
- Added exact-input, detection/track, state, transition, action-window and embedding-window timeline lanes.
- Added a saved-run video player and exact evidence image with explicit timestamp captions.
- Added Load settings to modify and rerun, restoring all saved options and regenerating the preview.
- Captured full-page and detailed timeline screenshots.

### Why

The user needs to inspect when a model output applies and rerun an experiment without manually copying every option.

### What worked

Browser smoke verified 12 timeline items for the saved native embedding run. Clicking the 10–12 s window sought the saved player to 10.0 s, displayed the exact 10.0 s PNG, and left the form unchanged. Loading settings restored every option exactly and regenerated eight preview frames without creating another run.

### What didn't work

No failure during browser smoke. No model inference was rerun for this presentation/navigation change.

### What I learned

A result-bound player avoids misleading source changes when browsing historical runs while keeping a different experiment form open.

### What was tricky to build

Point observations and interval windows require different visual semantics. Point-button width does not imply duration; intervals retain actual bounds, overlapping windows occupy separate rows, and captions identify the specific sampled image displayed. Explicit settings loading changes the form; timeline inspection does not.

### What warrants a second pair of eyes

Try dense timelines and settings restoration from another device. Check whether the saved-run player and evidence view make comparisons easier to interpret.

### What should be done in the future

Use this screenshot trail in the future technical report and incorporate further interaction feedback.

### Code review instructions

Read analysis.js loadRunSettings and resultTimeline. Open run-c91ef4d1a5c54ed9, click the 10–12 s window, then load settings and verify start/end/FPS/model/query match the saved request.

### Technical details

UI assets are served directly, so this update required no server restart. Existing service PID 33408 remains available over Tailscale. Screenshots are in the ticket various/ directory.

## Step 9: Keep evidence previews within the workspace and filter history

Fixed the reported eight-frame preview overflow and added filtering to saved experiments. The workspace columns now stay within the viewport, thumbnails wrap, and the same filters govern history and both comparison selectors.

### Prompt Context

**User prompt (verbatim):**

the top view should stay a consistent width and wrap the thumbnails, it seems to grow horizontally rn. can't paste it over ssh, but basically I see 8 frames after loading and it pushes the parameter pane out. 

Allow filtering run history by experiment preset / component / model to make it easier to select

**Assistant interpretation:** Keep the parameter pane visible after loading multiple frames and make saved experiments easier to find by preset, component and model.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

### What I did

- Changed desktop columns to minmax(0, ...) and allowed panels/controls to shrink within their grid tracks.
- Replaced the horizontal thumbnail strip with a wrapping responsive grid.
- Added combined preset/component/model filters, matching-run counts, clear filters and an empty state.
- Unified preset definitions for experiment setup and saved-option matching.
- Removed the duplicate history fetch/render path; filtering survives history refresh.
- Captured p9-wrapped-eight-frame-preview.png and p9-filtered-history.png.

### Why

Grid min-content sizing let thumbnail content expand the left column and displace the parameter pane. Unfiltered run lists made selecting comparable experiments difficult.

### What worked

At 1280 px, the parameter pane stayed at x=771.20 with width 484.80 before and after loading eight frames; thumbnails wrapped into two rows and page width remained 1280 px. At 960 px thumbnails occupied three rows with no overflow. At 740 px the layout stacked into one 708 px column with page width 740 px. Preset native matched two runs, reasoning plus Qwen matched two, conflicting filters matched zero with Compare disabled, and clearing filters restored all twelve current runs.

### What didn't work

No new failure in browser smoke. Historical runs do not record the original preset selection, so preset filters explicitly match saved component/model/FPS rather than inventing provenance.

### What I learned

Preventing overflow requires shrinking the grid tracks and their children as well as wrapping the thumbnails. Filtering the comparison selectors alongside the history avoids showing unrelated candidates.

### What was tricky to build

The old history code fetched and rendered twice, which could overwrite filtering during a refresh. A single fetch path now retains filter values and calls one renderer; filter changes clear stale comparison output. Preset matching is documented in the UI and applies to existing runs without modifying artifacts.

### What warrants a second pair of eyes

Verify the layout on the user's actual SSH/Tailscale client screen and try combinations of filters against newly created runs.

### What should be done in the future

Continue collecting screenshots and user feedback. If historical preset provenance becomes necessary, add explicit run metadata rather than infer it.

### Code review instructions

Inspect viewer.html grid/thumbnail styles and history filter controls; analysis.js matchingHistory, renderHistory and refreshHistory. Load run-c91ef4d1a5c54ed9 settings and verify eight frames wrap without moving the parameter pane. Filter history and confirm both comparison selectors have the same candidates.

### Technical details

Presentation-only browser smoke; no model inference or server restart required. Existing user-created runs were read without modification. UI assets remain live on mimimi:8780.

## Step 10: Overlay embedding comparisons on shared axes

Replaced independent side-by-side embedding charts with one overlaid chart. Both curves now use common time and cosine-score bounds computed across all displayed windows, making vertical differences visually faithful to their numerical values.

### Prompt Context

**User prompt (verbatim):** "when comparing graphs left and right, say on embedding against two runs, overlay the curves so they use the same scales."

**Assistant interpretation:** Make embedding-run comparisons use shared axes and overlaid curves rather than independently scaled plots.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

### What I did

- Added a reusable multi-series similarity renderer and used it for comparison overlays.
- Added mint solid A and orange dashed B curves, run-ID legends, grid lines and exact-value hover labels.
- Kept per-run ranked window lists and existing feature-space interpretation text.
- Captured p10-shared-embedding-overlay.png.

### Why

Independent vertical scaling visually magnified small variations and hid the actual score separation between runs.

### What worked

Browser smoke with native run-c91ef4d1a5c54ed9 and pooled run-cb3fcc4c7afa4e55 found exactly one chart containing two curves. Matched window starts mapped to identical x coordinates; both curves used the combined y transform. Legends correctly identified A/native and B/pooled. No UI error was displayed.

### What didn't work

No failure during this change.

### What I learned

Shared graphical axes improve reading of raw scores but do not statistically calibrate different model feature spaces; that distinction remains visible in the chart explanation.

### What was tricky to build

Bounds must include both runs, including different time ranges. The renderer sorts each curve by window start, uses one transform for every point, and preserves original A/B identities even if only one side has embedding results.

### What warrants a second pair of eyes

Try same-model and cross-model comparisons, including runs with different time ranges, and check legend/hover readability.

### What should be done in the future

Use the overlay screenshot in the future comparison report.

### Code review instructions

Inspect analysis.js addSimilarityPlot and comparison rendering. Compare the saved native and pooled embedding runs and verify only one chart is displayed with both curves.

### Technical details

UI-only asset change; no model inference or server restart. Screenshot and diary preserve the comparison evidence.

## Step 11: Restore and share comparison settings through the URL

Added URL state for comparison selections and history filters. A shared URL now restores the selected view and automatically redraws an active comparison, while browser Back and Forward restore previous choices.

### Prompt Context

**User prompt (verbatim):** "Add selected settings for comparison in the URL so we can refresh / share url."

**Assistant interpretation:** Preserve comparison settings across refresh and make comparisons shareable on the existing Tailscale service.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

### What I did

- Added query parameters for run A/B, preset/component/model filters, selected tab and active comparison.
- Added a Comparison permalink link and browser history updates for user selection changes.
- Restore state after loading run history; fetch linked runs individually if outside the recent list.
- Reject invalid IDs, unknown filters and linked runs excluded by filters rather than silently comparing other runs.
- Guard asynchronous comparisons so older results cannot overwrite a later selection.
- Captured p11-restored-comparison-url.png.

### Why

Refreshing previously lost selected runs and filters, making it difficult to reproduce or share a comparison.

### What worked

Browser created a URL for native-versus-pooled embeddings with the embeddings component filter. Opening that URL restored the history tab, exact A/B IDs, filter and two overlaid curves with no error. Changing the model filter updated the URL; browser Back restored the original model filter and comparison chart.

### What didn't work

No failure in the URL round-trip or browser-back smoke.

### What I learned

Restoration must wait until filter/select options exist. Links must resolve run IDs directly because shared runs can eventually fall outside the recent-history page.

### What was tricky to build

URL restoration and user selection changes both trigger asynchronous data loading. Restoration suppresses history writes, comparison requests have generation guards, and filter changes invalidate any pending chart to avoid stale output.

### What warrants a second pair of eyes

Open a shared comparison link from the user's other tailnet device and verify the same runs and filters appear. Source run artifacts must remain available on this Mac.

### What should be done in the future

Continue the screenshot trail for the future report; add more URL state only when needed by a concrete workflow.

### Code review instructions

Read saveComparisonUrl, refreshHistory restoration and the comparison request generation guard in analysis.js. Create a filtered comparison, refresh its URL, change a filter and use browser Back.

### Technical details

Query fields: tab, a, b, history_preset, history_component, history_model, compare=1. No inference or server restart was needed; links reference saved runs on mimimi:8780.

## Step 12: Connect selected detections to exact reasoning crops

Implemented the next concrete dependency from the UI design: a selected perception box can prepare an explicit single-image reasoning draft. The saved child request preserves the parent evidence rather than treating a manually entered crop as a detector result.

The actual browser smoke selected the refrigerator at 10 seconds, previewed a 185×289 crop and completed a fresh Qwen run. Screenshots preserve both the editable draft and completed evidence.

### Prompt Context

**User prompt (verbatim):** ok, continue with the ticket

**Assistant interpretation:** Continue VIDEO-LAB-UI-001 with the next useful designed component connection.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

**Commit (code):** bc4916f

### What I did

Added task oxek, printed the P7 plan, implemented validated handoff references and coordinate conversion, added UI selection/padding/preview/detach controls, and stored parent provenance with child runs. Updated the intern guide and measured walkthrough.

### Why

The user can now test whether object-local visual context changes reasoning while retaining a reproducible connection to the detector output.

### What worked

`PYTHONPATH=workbench/src workbench/.venv/bin/pytest -q workbench/tests/test_lab.py`: 8 passed. Browser draft preserved exact 10-second PTS. Qwen run `run-6903f06e821843c6` completed in 13.583 seconds with parsed status ok and state closed. Parent provenance was saved. Start slip printed successfully at 2026-09-07T15:57:06Z.

### What didn't work

The deliberate tampering probe returned HTTP 422: `handoff crop changed; detach the handoff before editing evidence`. This expected rejection generated the browser network-console error. Pytest emitted existing Starlette/httpx and AnyIO deprecation warnings; no test failures occurred. Automatic approval review rejected remote completion-slip printing: the payload included ticket, commit and network-access details destined for an unverified remote service. Generated p12-handoff-done.yaml locally with --no-print; completion printing remains pending permission. The earlier start slip printed successfully.

### What I learned

Detector coordinates belong to the parent input crop, not necessarily the original source. Applying its origin is required before normalization. Cropping did not change the closed answer in this one smoke case.

### What was tricky to build

Retaining a binding while permitting model/decoding changes, restoring all form fields without silently dropping provenance, and keeping the exact timestamp separate from apparent state duration.

### What warrants a second pair of eyes

Whether the restricted appliance selection and context padding are sufficient for meaningful user experiments. Actual PNG crop boundaries remain authoritative over floating-point normalized coordinates.

### What should be done in the future

Collect user feedback on the draft workflow, then compare crop versus full-frame reasoning on a deliberately varied set with independent visual reviews. Do not infer quality from successful execution.

### Code review instructions

Start with lab/handoff.py, follow Manager.start admission and saved request construction, then inspect analysis.js detectionHandoffPanel and loadRunSettings wrappers. Read the focused nested-crop test and inspect both p12 screenshots.

### Technical details

Draft endpoint: POST /v1/lab/handoff. The request binding contains parent run/frame/detection IDs plus padding. Submission snapshots parent request/result hashes and verifies evidence-source equality. The selected interval is [10000000,10000001) microseconds; actual crop is [167,94,352,383]. Server was idle before restart; the live service remains on mimimi:8780. Source implementation commit: bc4916f.

## Step 13: Expose editable reasoning prompts and readable YAML

Added an editable pre-run user prompt to the experiment controls and replaced raw-data JSON panels with highlighted YAML. The same default template builder now serves preview and inference, while custom text is snapshotted before model execution.

A real Qwen crop experiment confirmed that the edited textarea, immutable snapshot and runtime prompt were identical. Screenshots preserve the editor and highlighted output for a later report.

### Prompt Context

**User prompt (verbatim):** render raw data as yaml with syntax highliting, not raw json. Display and allow editing prompt in the "choose an experiment" part (if possible).

**Follow-up prompt (verbatim):** also don't forget to ccommit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill), if you haven't

**Assistant interpretation:** Make model instructions editable and structured evidence easier to inspect while preserving exact experiment provenance.

**Inferred user intent:** Make experimental evidence understandable and reproducible.

**Commit (code):** cab931d

### What I did

Added lab/presentation.py, prompt preview and YAML rendering endpoints, optional validated prompt configuration, pre-run snapshots, a keyword-only worker override, editor/reset/restore controls and lazy YAML views. Declared the already installed PyYAML dependency. Updated the technical guide and measured walkthrough.

### Why

The user should see and experiment with instructions before paying for inference, and read multiline prompt/output evidence without JSON escape clutter.

### What worked

Nine lab tests passed, followed by 38 existing profile/visibility tests. The added null regression test passed after its fix. Browser reset and saved-prompt restoration passed. Qwen run run-805e04781b4846b7 completed in 12.096 seconds; snapshot and runtime prompt matched the edited text exactly. YAML output contained syntax-highlight spans.

### What didn't work

Browser probe POST /v1/lab/render-yaml with body null initially returned HTTP 422 because FastAPI treated the required body as absent. Changed Body(...) to Body(default=None) and added a regression test. Existing Starlette/httpx and AnyIO deprecation warnings remained.

### What I learned

Default prompt generation must be shared with the actual verifier, rather than duplicated in JavaScript. Displaying a user message before execution is distinct from showing the model-specific chat template, which is resolved by the runtime.

### What was tricky to build

Asynchronous default refreshes could overwrite edits; a generation counter invalidates old requests, and custom text is retained literally. Saved-run loading restores custom/default mode explicitly. Optional comparison values require the YAML endpoint to accept null.

### What warrants a second pair of eyes

Custom prompts can violate the expected output schema or ask a different question; the UI explains that parsing and door-state rule semantics remain fixed. The safe YAML dumper and Pygments escaping are covered by a script-tag test.

### What should be done in the future

Gather feedback on prompt editing and record controlled prompt comparisons with independent visual reviews. A successful custom-prompt run is not evidence of improved accuracy.

### Code review instructions

Read presentation.reasoning_prompt, manager prompt_snapshot, and the worker override path first. Then review refreshPrompt/loadRunSettings and viewer.jsonDetails. Inspect p13 screenshots and the saved smoke run.

### Technical details

API: POST /v1/lab/prompt and POST /v1/lab/render-yaml. Optional options.prompt is limited to 16000 characters. Actual input pixels, system message, formatted prompt and raw model output remain recorded. Implementation commit cab931d; source and UI service remain available on mimimi:8780.
