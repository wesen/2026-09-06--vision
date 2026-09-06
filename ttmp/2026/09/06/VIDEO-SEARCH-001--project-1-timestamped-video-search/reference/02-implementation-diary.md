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
