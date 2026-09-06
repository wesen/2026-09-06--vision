---
Title: Implementation diary
Ticket: VIDEO-SEARCH-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/README.md
      Note: Reproduction handoff
    - Path: repo://workbench/src/video_workbench/api.py
      Note: Tested local API and playback
    - Path: repo://workbench/src/video_workbench/evaluation.py
      Note: Frozen evaluation and metric denominators
    - Path: repo://workbench/src/video_workbench/index.py
      Note: Atomic features and real index measurements
    - Path: repo://workbench/src/video_workbench/media.py
      Note: Decoded PTS and deterministic selection
    - Path: repo://workbench/src/video_workbench/registry.py
      Note: Transactional model-safe video registry
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T13:43:38.941231-04:00
WhatFor: ""
WhenToUse: ""
---



# Diary

## Goal

Implement Project 1 timestamped video search, including its embedding-runtime prerequisite, and preserve commands, failures, screenshots, validation, and milestone commits.

## Step 1: Establish runtime prerequisites and implementation phases

Started VIDEO-SEARCH-001 with the required COSMOS-EMBED-001 runtime gate. Inspected the existing corpus, task breakdown, local Python modules, and model cache before installing or indexing anything. The existing environment has NumPy/PyTorch but no MLX, MLX-VLM, or PyAV; the only discovered cached model is a text-only Qwen3-4B checkpoint, unsuitable for the requested visual embeddings.

### Prompt Context
**User prompt (verbatim):** "Now work on the first project, commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill). Print out a brutalist work slip with the plan / different phases for the ticket. then before stsarting a phase, plrint a split about the phase, and print one when the phase is done."

**User prompt (verbatim):** "take screenshots as you work for the reports and diary and such."

**Assistant interpretation:** Implement timestamped search end to end, beginning with the embedding dependency; document and photograph meaningful application results.

**Inferred user intent:** Obtain a working, evaluated search tool with a reviewable implementation trail and visual evidence.

### What I did
- Read the project/runtime checklists and applicable diary, printing, and commit skills.
- Inspected local modules and model-cache directory names.
- Selected five implementation phases: runtime gate, registry, feature index, search/viewer, and held-out evaluation.

### Why
- Real model capabilities must be verified before committing the feature-space and cache contracts.

### What worked
- The 24-video VirtualHome corpus and verified generation playbook are available locally.

### What didn't work
- Runtime smoke failed: `ImportError: apply_chat_template requires jinja2 to be installed. Please install it using `pip install jinja2`.` Added Jinja2 as an explicit project dependency; the base install did not pull the optional chat-template dependency.
- Initial plan-print command failed with `FileNotFoundError: [Errno 2] No such file or directory: 'ttmp/2026/09/06/VIDEO-SEARCH-001--project-1-timestamped-video-search/various/work-slips/search-plan.yaml'`. Created the missing archive directory before retrying.

### What I learned
- A cached text model cannot substitute for a visual embedding model simply because it shares the Qwen family name.

### What was tricky to build
- The first application project depends on an unimplemented runtime ticket. Treat the runtime as an explicit gate, not a hidden download or silent image-pooling fallback.

### What warrants a second pair of eyes
- Actual video input handling, feature-space identity, and timestamped evidence provenance.

### What should be done in the future
- Complete the runtime gate and proceed through S1-S4; capture real UI screenshots once those surfaces exist.

### Code review instructions
- Start with the search and embedding design guides and their task checklists.

### Technical details
- Starting repository commit: `3ce81cb`.
- No model behavior is inferred from the preceding design-only work.

## Step 2: Verify embeddings and register presentation timestamps

Committed the working embedding gate as `358db7e`, then implemented model-safe manifest ingestion and a transactional SQLite registry. Every video is hashed and fully decoded before any incoming rows are committed. Stored timestamps come from the decoder, including raw PTS, stream time base, origin, and the last-frame duration provenance.

Captured the actual source gallery before building search: [corpus screenshot](../various/screenshots/01-corpus-before-search.png). The gallery contains evaluator labels; only `inputs.jsonl` and video pixels enter the search registry.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build reliable ingest and preserve visual and technical evidence.

**Inferred user intent:** Search results should point to actual video intervals without leaking answer labels.

**Commit (code):** `358db7e` — embedding gate; registry commit recorded in the changelog.

### What I did
- Added `media.py`, `registry.py`, CLI ingest/inspect, and variable-rate/corrupt/missing/split/rollback tests.
- Registered all 24 source videos: 4,261 frames and 426.1 seconds.
- Printed E-done and S1-start milestone slips; remote responses reported `printed: true`.

### Why
- Frame number divided by nominal FPS is not a valid general timestamp strategy.
- Validate the entire incoming batch before writing, preventing a partial ingest after a bad file.

### What worked
- Nine tests passed after fixture corrections; registry re-ingestion is idempotent.
- MLX smoke established finite normalized vectors, exact same-image repetition, and pixel-sensitive differences.

### What didn't work
- Initial VFR test: `assert [0, 2] == [0, 2, 3]`. libx264 rounded requested 350/450ms timestamps to 400/500ms using its implicit codec time base. Set both stream and codec time bases to 1/1000 to create the intended fixture.
- Missing-file fixture: `TypeError: row() got multiple values for argument 'video'`. Renamed helper positional parameter to `path`.

### What I learned
- The decoder was correct; the fixture encoder had changed the requested timestamps.

### What was tricky to build
- Sampling must deduplicate when several requested times map to the same future frame, and must exclude frames outside the half-open clip interval.
- Last-frame duration lacks a following PTS; preserve whether its duration was encoded or estimated.

### What warrants a second pair of eyes
- VFR selection, immutable episode comparisons, and split-group/hash leakage checks.

### What should be done in the future
- Build resumable arrays and exact search on this registry.

### Code review instructions
- Run `workbench/.venv/bin/pytest workbench/tests -q`.
- Run `workbench/.venv/bin/video-workbench inspect` to inspect registered media metadata.

### Technical details
- Database: ignored local `output/video-workbench/registry.sqlite`, schema version 1.
- Ingest: `workbench/.venv/bin/video-workbench ingest output/virtualhome-corpus/home-v1/inputs.jsonl`.

## Step 3: Publish a real resumable feature index

Built the first actual 24-video index from 861 independently encoded frames. The 95 five-second windows at 2 FPS took 134.37 seconds to encode and publish; their matrix occupies 778,368 bytes. The explicit mean-of-normalized-image-vectors baseline preserves appearance but discards frame order.

The viewer phase began while this independent GPU build was finishing. No evaluation results have been inspected or used to choose parameters. The initial 5s/2FPS setting is an engineering smoke configuration; selection will happen in the bounded development sweep.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Build durable features and prove repeatability before exposing search.

**Inferred user intent:** Recover interrupted indexing and review every result against its provenance.

**Commit (code):** `3749908` — completed registry; cache implementation commit recorded in changelog.

### What I did
- Implemented content-addressed frame features, exact-PTS keys, normalized pooling, immutable index manifests, checksums, writer locks, and exact ranking.
- Added injected-crash recovery, corruption, space mismatch, stable-tie, window-boundary, and cache-reuse tests.
- Preserved first-build measurements in `various/initial-index-build.json`.

### Why
- Write and fsync array bytes before committing cache metadata. An interrupted write may leave an orphan, but cannot expose a completed metadata row pointing to unpublished data.

### What worked
- Initial real build: 861 new frames, 95 windows, 134.37s; no model or decode failures.
- Cache/ranking suite passed; the expanded API suite now totals 13 passing tests.

### What didn't work
- Registry milestone commit initially stopped at `new blank line at EOF` in the docmgr changelog. Trimmed its generated trailing blank line and committed successfully.
- FastAPI/Starlette tests emit upstream TestClient deprecation warnings for httpx and BlockingPortal. Tests pass; these do not affect runtime behavior.

### What I learned
- This small corpus needs under 1 MB for the pooled feature matrix; exact cosine ranking is sufficient.

### What was tricky to build
- Per-frame keys include raw PTS and time base as well as normalized timestamps and model-space identity. Changing windows reuses frames without mixing incompatible feature spaces.
- The first index was built while producer provenance was being finalized. A verified cache-only rebuild publishes the finalized manifest with source-file hashes.

### What warrants a second pair of eyes
- Atomic file-before-row ordering, source checksum verification, and normalized pooling.

### What should be done in the future
- Finish actual browser seeking and freeze the development/test evaluation protocol.

### Code review instructions
- Read `index.py` and `test_index.py`, especially the injected exception between rename and SQLite commit.
- Run `video-workbench index --seconds 5 --fps 2` twice: the second build must report zero fresh frames.

### Technical details
- CLI: `workbench/.venv/bin/video-workbench index --seconds 5 --fps 2`.
- Features live under ignored `output/video-workbench/frames/<space>/`; completed indices live under `indices/<index-id>/`.

## Step 4: Search the real index and inspect timestamped playback

Implemented the typed FastAPI endpoint and local HTML viewer, then searched the training partition through the browser. The first query returned five candidates in 0.19 seconds. Clicking the top interval loaded the registered source video at exactly 5.0 seconds, with readyState 4 and 640×480 decoded video.

Saved [the actual search and seek screenshot](../various/screenshots/02-first-search-and-seek.png), including sampled PTS. This is an engineering demonstration on training data, not the held-out evaluation. The independently repeated index build reused all 861 frames in 0.124 seconds with zero new encodes.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Present real ranked evidence and verify browser playback, not just API JSON.

**Inferred user intent:** Obtain a usable search tool with visual proof of its behavior.

**Commit (code):** `522afe4` — completed cache/index milestone; viewer commit recorded in changelog.

### What I did
- Added strict request/response models, same-space checks, split filtering, a serialized model call, registered video routes, and range responses.
- Built a responsive query/results/player page with source and timestamp evidence.
- Tested malicious IDs, unknown indexes, invalid requests, empty valid splits, modified videos, and HTTP byte ranges.

### Why
- The browser should receive registered IDs and source URLs, never arbitrary filesystem access.

### What worked
- All 13 tests passed; actual browser POST returned 200 and video request returned 206 Partial Content.
- Browser seek: `currentTime: 5`, `duration: 19.9`, `readyState: 4`, video 640×480.
- Playback near the end paused successfully. Screenshot captured actual rendered video and search results.

### What didn't work
- The first endpoint stop used only `timeupdate`, stopping at 10.245371s for a 10s endpoint. Added animation-frame checks and clamped the final seek to the boundary, improving visible interval stopping.
- Browser logged an irrelevant missing favicon 404; no application JS errors were observed.

### What I learned
- A server-side range-response test does not by itself establish that the browser decodes and seeks the source correctly; both checks matter.

### What was tricky to build
- MLX model instances cache state, so API calls must serialize access to the encoder. Query and index space IDs are checked before ranking.

### What warrants a second pair of eyes
- Browser media timing precision, registry/index consistency, and source-hash verification on playback.

### What should be done in the future
- Freeze six candidate configurations and run the selected test setting once.

### Code review instructions
- Read `api.py`, `viewer.html`, and `test_api.py`.
- Start `video-workbench serve --manifest <manifest.json>` and open http://127.0.0.1:8767/.

### Technical details
- `POST /v1/search`: query, optional loaded index ID, split, top_k.
- `GET /v1/index`: immutable index and feature-space metadata.
- `GET /v1/episodes/{episode_id}/video`: registered source with range support.
- OpenAPI: `/docs` and `/openapi.json`.

## Step 5: Freeze evaluation before reading development results

Prepared a six-configuration protocol, copied and hashed the four positive query families, and added two explicit negative controls. The evaluator separates query Success@K from interval Recall@K and reports a temporal-IoU diagnostic, per-query results, random-ranking controls, and resource measurements. It durably saves the development winner before test ranking and rejects accidental reruns of the held-out report.

Hardened cache provenance to include actual MLX, Metal, NumPy, Pillow, and PyAV versions. This intentionally creates a new space identity and fresh final-baseline features; the earlier smoke measurements remain valid for their recorded earlier identity.

### Prompt Context
**User prompt (verbatim):** (see Step 1)

**Assistant interpretation:** Select on development data and evaluate the held-out partition once, with precise metric definitions.

**Inferred user intent:** Distinguish working retrieval infrastructure from measured model quality.

### What I did
- Added frozen query/protocol files and the evaluator CLI.
- Added hand-computed relevance and freeze-before-test/retest-guard fixtures.
- Formatted the Python implementation and prevented overwriting an already published index matrix.

### Why
- Long windows can satisfy weak coverage while locating an action poorly. Report that bias explicitly and include IoU.

### What worked
- Hand-computed metric fixture distinguishes query success, interval recall, duplicate hits, and zero-positive queries.
- Model-safe inference code does not import evaluator labels.

### What didn't work
- Offline formatter initially failed creating `/Users/manuel/.local/share/uv/tools/.lock`: `Operation not permitted (os error 1)`. Set `UV_TOOL_DIR=output/uv-tools` to keep tool state in the workspace.
- First evaluator workflow fixture failed with `KeyError: 'limitations'`: its minimal protocol omitted a required reporting field. Added the field to the fixture.

### What I learned
- A frozen query set must be joined against exactly the frozen source manifest, not merely a registry with matching group names.

### What was tricky to build
- The evaluator must save a selected configuration and its provenance before the first test ranking. An exclusive test-start marker prevents an accidental rerun from silently replacing the result.

### What warrants a second pair of eyes
- Metric denominator definitions and the fixed development tie-break order.

### What should be done in the future
- Run this committed protocol, report results without retuning on test, and publish the handoff.

### Code review instructions
- Read `configs/retrieval/home-v1-protocol.json`, `evaluation.py`, and `test_evaluation.py`.

### Technical details
- Development group g03; held-out group g04. Six settings: 2/5/10 seconds × 1/2 FPS.
- Relevance: same episode and at least 50% coverage of the weak interior.
- Select by macro Success@5, interval Recall@5, best IoU@5, then smaller window and FPS.

## Step 6: Report the held-out result and finish the search handoff

The committed protocol selected 10-second windows at 1 FPS. Its one held-out aggregate evaluation produced Success@5 75%, macro interval Recall@5 68.75%, and mean best IoU@5 0.0949. Random ranking reached 74% Success@5, so the report treats this as coarse candidate retrieval rather than reliable action localization. The final serving index contains 55 windows across all 24 videos.

Archived the frozen development/test JSON, exact query vectors, source/index manifests, and four actual browser screenshots. Wrote the implementation report and reproduction README, and repeated the runtime smoke under the finalized feature identity. The user then requested a textbook-style technical deep dive in the Obsidian vault with a vault commit and push; that publication is the remaining delivery step.

### Prompt Context
**User prompt (verbatim):** "write a detailed project report for the obsidian vault as a deep dive technical analysis blog post using a textbook writing style (no analogies, see skill).      
 Commit and push the bsidian vault when done (go-go-parc vault)."

**Assistant interpretation:** Finish the search report and publish a detailed, evidence-backed technical article in go-go-parc, then commit and push that vault.

**Inferred user intent:** Preserve a readable explanation of how the system works, what was measured, and what the result does and does not establish.

**Commit (code):** `aeeaa30` — evaluator/protocol frozen before execution.

### What I did
- Ran six development settings and one frozen test report; preserved all outputs under `various/evaluation/`.
- Recorded final UI seek at 10s with readyState 4 and 0.09s observed query response.
- Saved and inspected final playback and evaluation-summary screenshots.
- Added a pinned-model download script and a full reproduction README.
- Serialized registry validation and publication with `BEGIN IMMEDIATE` during final review; this prevents concurrent writers from validating stale split ownership.

### Why
- A working application and favorable-looking aggregate are insufficient evidence of accurate localization. The random baseline, interval recall, and temporal IoU must accompany Success@K.

### What worked
- All 15 automated tests pass; actual browser decoding, source seeking, byte ranges, and final endpoint clamp were verified.
- Final runtime smoke again produced unit, finite 2048-dimensional vectors and exact same-frame repetition.
- Final matrix: 450,688 bytes. Peak MLX allocation: 2.152 GB.

### What didn't work
- Microwave closing had zero matched interiors in its top five held-out results.
- Mean best IoU@5 was only 0.0949; long windows dominate the coverage-oriented selection criterion.
- Negative controls still return candidates because no calibrated abstention policy exists.

### What I learned
- Success@10 reaches 100% when retrieving ten of fourteen test windows, so that number carries little evidence of discriminative quality.
- Macro interval recall (68.75%) differs from the micro matched-interior fraction (9/12 = 75%). The report names its denominator.

### What was tricky to build
- Preserve the frozen result while later browsing its hits: final UI screenshots are post-evaluation inspection, not another aggregate evaluation or a tuning opportunity.
- Broad embedding-runtime profiling remains separate from this search baseline. Native video is still explicitly unsupported.

### What warrants a second pair of eyes
- The interpretation of weak relevance, model-card lineage uncertainty, and the open native-video wrapper repair.

### What should be done in the future
- Publish the requested vault deep dive, then pursue reviewed temporal labels and a separately validated native-video feature space.

### Code review instructions
- Read `reference/03-implementation-and-evaluation-report.md`, `workbench/README.md`, and the frozen JSON.
- Re-run tests rather than overwriting the held-out run; its test-start marker intentionally prevents accidental replacement.

### Technical details
- Serving index: `e9ba74dabd6c07eafc1df2ee28c2b77a6f0235b87a7e7b3e0fff2e3df893bbce`.
- Final feature space: `9246fa13a4a2d32fbb78ba1614024d65bb44339b757497bf0e90cdd6f07a0bf4`.
- Four screenshots are linked from the implementation report; original PNGs are under `various/screenshots/`.

## Step 7: Publish the textbook-style deep dive to the Obsidian vault

Wrote a new 6,247-word technical article explaining the implemented system from source identity through frozen evaluation. The article uses direct technical prose, worked examples, equations, three Mermaid diagrams, and four copied screenshots. It includes an analytical random-ranking calculation: the exact expected Success@5 is 73.926%, consistent with the recorded 74% random control.

Validated frontmatter, diagram fences, image signatures and hashes, wiki-link targets, reported metrics, and append-only destinations. Copied the article and images into today's go-go-parc project folder, committed only those five files, and pushed main successfully. The vault is clean and reports zero commits ahead or behind origin/main.

### Prompt Context
**User prompt (verbatim):** (see Step 6)

**Assistant interpretation:** Publish an evidence-backed technical blog post in the vault, preserving existing notes and making figures self-contained.

**Inferred user intent:** Keep a durable, readable account that teaches the system and its evaluation limits.

**Commit (code):** `cc58db0` — completed implementation/report source. **Commit (vault):** `8e8a8745603d330e6fec408531a73e7e9ae90b5e` — technical article and four screenshots.

### What I did
- Applied the textbook-authoring and obsidian-vault-writing skills; read the existing VirtualHome vault article for continuity.
- Wrote the new article in the ARTICLE style with source and protocol revisions.
- Added `scripts/03-publish-vault-article.py` to validate and copy only new note/asset files.
- Fetched origin, verified the vault had no unrelated staged changes, committed the five intended files, and pushed main.

### Why
- The vault article teaches the mechanisms and measured implications rather than repeating the implementation changelog.
- Colocated `_assets/` images make the post independent of the source checkout's screenshot paths.

### What worked
- Vault push: `a45ea5d..8e8a874 main -> main`.
- Post-push status clean; `HEAD...origin/main` divergence `0 0`.
- All four vault assets match their reviewed source PNG hashes.

### What didn't work
- The prior source commit's whitespace check found the six intentional trailing spaces in the user's verbatim prompt. After verifying that was the sole finding, retained the exact prompt and used a per-command `core.whitespace=-blank-at-eol` check for that source commit. The vault article passed the ordinary whitespace check.

### What I learned
- Relevant-window counts of 4, 2, 4, and 2 among fourteen candidates explain the high random Success@5 without any new model evaluation.

### What was tricky to build
- Preserve a strict distinction between post-run explanatory analysis, browser inspection, and another held-out evaluation. The post adds the closed-form random expectation; it does not change configuration or rerun model selection.

### What warrants a second pair of eyes
- Future native-video claims should use the exact installed implementation and a separately validated feature space.

### What should be done in the future
- Continue the separate native-video and reviewed-label workstreams. No requested publication work remains.

### Code review instructions
- Open the vault article and confirm the three diagrams, equations, and four local screenshot embeds.
- Review `various/vault-article-validation.json` for paths, word count, and asset hashes.

### Technical details
- Vault path: `Projects/2026/09/06/ARTICLE - Timestamped Video Search - From Verified Pixels to Frozen Evaluation.md`.
- Source repo: `/Users/manuel/code/wesen/2026-09-06--vision`.
- Vault repo: `/Users/manuel/code/wesen/go-go-golems/go-go-parc`.

## Step 8: Adopt the repaired native runtime under a fixed development protocol

Followed the user's native-video handoff using the accepted repair and existing isolated runtime. Built a fresh FP32 native index at two-second windows and 2 FPS, then verified exact source evidence equality with the existing pooled development index. Both indices contain 55 clips from six videos.

### Prompt Context
**User prompt (verbatim):** The full quoted native-video handoff is preserved in `various/native-pooled-v1/user-handoff.txt`.

**Assistant interpretation:** Execute the repaired runtime and compare it with the pooled baseline on matched development evidence.

**Inferred user intent:** Start using the fixed MLX implementation without invalidating prior results or assuming a retrieval-quality improvement.

**Commit (code):** Workbench integration `127921a`; repaired fork `6452614f6de04694d1e34fd13abaca11f6ffb994`. Comparison script follows in the next commit.

### What I did
- Read the README and repair handoff; retained isolated runtime extras and official FP32 weights.
- Ran the requested index command with a fresh `--root output/native-pooled-comparison-v1/native`.
- Froze queries, two-second/2 FPS setting, development-only split, and existing relevance metrics before reading comparison scores.
- Added a reproducible script that rejects clip/PTS differences and query/index feature-space mismatches.
- Corrected the README's stale opening statement that all native video remained rejected.

### Why
The repaired implementation has passed numerical acceptance, while retrieval quality remains a separate question. The existing pooled index provides a preserved comparison on identical observations.

### What worked
All 55 native clips encoded successfully; build elapsed time was 14.8026 seconds excluding encoder construction. Exact source evidence matches the pooled index. The plan slip printed successfully (HTTP 200, 2026-09-06T20:50:03Z).

### What didn't work
No runtime failure occurred in this phase. The two systems use different precision, model artifacts, and preprocessing; this experiment cannot isolate temporal architecture as the cause of a result difference.

### What I learned
No baseline re-encoding is needed: an immutable two-second/2 FPS pooled development index already exists and its full source metadata matches.

### What was tricky to build
Chunk IDs must differ because they include feature-space identity. The comparison excludes only that derived ID when verifying the underlying source records, retaining source hashes, raw PTS, origin, time base, partitions, and interval boundaries.

### What warrants a second pair of eyes
Weak program-supervised relevance and one development group limit semantic conclusions. No test data is ranked and no default-mode promotion is authorized by these measurements.

### What should be done in the future
Finish query ranking, preserve per-query differences and screenshots, and report the result with the system-level confounds.

### Code review instructions
Review `scripts/04-compare-native-pooled.py`, the frozen protocol, source manifests, and the README native section.

### Technical details
Native output: `output/native-pooled-comparison-v1/native`. Pooled index: `78b4ccb4780da259733f3ab253cf359b759b147da556b90b7af6421b02eb8a1b`. Native index: `ed99514634df6f1c8f952be1ce54a281ebf80a576f98806c3e894dfda7d9eb23`.
