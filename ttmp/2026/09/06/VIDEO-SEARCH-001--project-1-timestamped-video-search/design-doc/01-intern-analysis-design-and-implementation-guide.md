---
Title: Intern analysis design and implementation guide
Ticket: VIDEO-SEARCH-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://configs/virtualhome-household-v1.json
      Note: Existing implementation evidence for this design
    - Path: repo://docs/playbook/virtualhome-corpus.md
      Note: Existing implementation evidence for this design
    - Path: repo://src/virtualhome_corpus/core.py
      Note: Existing implementation evidence for this design
    - Path: repo://src/virtualhome_corpus/runner.py
      Note: Existing implementation evidence for this design
ExternalSources: []
Summary: Build timestamped retrieval, cache integrity, a local viewer, and split-aware evaluation.
LastUpdated: 2026-09-06T13:13:51.072478-04:00
WhatFor: ""
WhenToUse: ""
---


# Project 1 - Timestamped video search

## What the intern is building

A user types "a person opening the microwave" and receives a ranked list of playable video intervals. Each result must identify the source episode, the exact requested interval, the actual frames encoded, the feature-space version, and the similarity score. Search provides candidate evidence; it does not establish whether the door was closed before departure or whether a procedure was followed.

This project consumes the runtime adapter from COSMOS-EMBED-001 and the existing VirtualHome corpus. It produces an ingest/index/search CLI, a minimal local results viewer, durable metadata, and an evaluation report. It does not train an encoder or implement temporal rules. The first release is local and single-user; a distributed vector service would add complexity without addressing the current uncertainty about feature quality.

## Existing artifacts and the gap

`runner.py:228` already writes model-safe `inputs.jsonl`, separate `labels.jsonl`, and four weak action-retrieval queries. The corpus has 24 videos with group splits. `core.py:102` retains raw action endpoints and emits guarded interiors explicitly labeled weak supervision. There is no feature cache, retrieval index, or application search API yet. The existing gallery is for labeled inspection, not an inference input.

Treat the supplied query intervals as a coarse starter benchmark. They are not exact boundaries, and the four query families are too few for strong statistical conclusions. We can measure whether retrieval finds relevant action interiors without claiming that it segments actions accurately. Before selecting window lengths or prompts, freeze the query set and decide which groups are development and test.

## Architecture and data ownership

```text
corpus inputs -> ingest -> episode registry
                              |
                        chunk + sample
                              |
                     embedding adapter [E]
                              |
                       arrays + clip rows
                              |
query -> same-space vector -> cosine ranking
                              |
                     interval hits -> viewer

labels + weak queries ----------> evaluator only
```

`ingest.py` owns source metadata and hash verification. `sampling.py`, initially owned by the embedding ticket, owns source PTS selection. `cache.py` owns content-addressed features and publication of completed rows. `retrieval.py` owns exact cosine ranking and deterministic tie-breaking. `api.py` and a minimal viewer present stored results. `evaluation/retrieval.py` joins predictions to evaluator labels after inference.

All these paths are proposed under `workbench/src/video_workbench/`. Do not move the working generator into this package. Ingestion should accept a generic corpus manifest so real recordings can later use the same path without a Unity dependency.

## Time and chunk contracts

Use integer microseconds and half-open intervals `[start_us, end_us)`. Adjacent windows share a boundary without double-counting that endpoint. Store source duration and actual PTS. At 10 FPS, the current frame 52 occurs at 5.2 seconds, but real-video decoding must use PTS rather than assuming a constant frame rate.

A `ClipSpec` contains episode ID, source hash, requested interval, actual selected PTS, sampling specification, and feature-space ID. Its key must change when any input that affects vectors changes. An `Episode` contains ID, relative path, source hash, split, split group, duration, and decoder metadata. Neither needs the intended action variant.

```python
@dataclass(frozen=True)
class SearchHit:
    episode_id: str
    clip_id: str
    start_us: int
    end_us: int
    score: float
    feature_space_id: str

# Proposed application API.
def search(query: str, index_id: str,
           split: str, top_k: int) -> list[SearchHit]: ...
```

Require positive bounded `top_k`, a known index and split, and compatible query/document vectors. Return a clear empty result for an empty valid partition. A malformed request is an error, not an empty successful search. Keep raw cosine scores; do not label them "confidence" without a separate calibration experiment.

## Storage and atomic publication

Start with SQLite metadata and NumPy arrays. SQLite gives transactions and searchable records without a server; the standard [Python 3.11 sqlite3 API](https://docs.python.org/3.11/library/sqlite3.html) documents `connect`, parameterized `execute`, and transaction handling. Use bound parameters, enable foreign keys, and keep one application writer initially. Store migrations under `workbench/migrations/`.

```sql
CREATE TABLE episode (
  id TEXT PRIMARY KEY, sha256 TEXT NOT NULL,
  path TEXT NOT NULL, split TEXT NOT NULL,
  split_group TEXT NOT NULL, duration_us INTEGER NOT NULL
);
CREATE TABLE clip (
  id TEXT PRIMARY KEY,
  episode_id TEXT NOT NULL REFERENCES episode(id),
  start_us INTEGER NOT NULL, end_us INTEGER NOT NULL,
  space_id TEXT NOT NULL, array_path TEXT NOT NULL,
  array_sha256 TEXT NOT NULL, sample_json TEXT NOT NULL,
  CHECK (start_us >= 0 AND end_us > start_us)
);
```

Write a new array to a temporary file, flush it, publish it atomically, then commit its metadata row. A crash between file publication and row commit can leave an orphan file, which a maintenance scan can identify. The reverse order can leave a committed row pointing at missing bytes and should be avoided. Existing completed entries are reused only after their hashes and space specification match. Never mutate an array in place while search is using it.

An index manifest freezes the ordered clip IDs, matrix checksum, space ID, split-manifest hash, source hashes, sampling settings, and code revision. It is the reproducible unit of evaluation; merely recording a model name is insufficient.

## Exact retrieval before approximate indexing

For normalized query vector `q` and row-normalized matrix `X`, scores are `X @ q`. Sort descending and use clip ID as a stable tie-breaker. The first implementation should compare exact ranking against hand-computed fixtures before introducing any approximate nearest-neighbor library.

```python
# Pseudocode; vector spaces checked before arithmetic.
assert query.space_id == index.space_id
rows = index.rows_for_split(split)
scores = rows.matrix @ query.vector
ranked = sorted(zip(scores, rows.clip_ids),
                key=lambda pair: (-pair[0], pair[1]))
hits = [registry.hit(clip_id, score)
        for score, clip_id in ranked[:top_k]]
```

Overlapping windows can fill all top-five slots with nearly identical results. Keep raw ranking for reproducibility and optionally apply a documented same-episode overlap suppression for the viewer. Evaluate raw and suppressed outputs separately. Suppression must not cross episode boundaries or depend on labels.

### Decision: exact local search

- **Context:** The corpus is tiny and embedding semantics are uncertain.
- **Options considered:** NumPy exact search, an approximate index, or a hosted vector database.
- **Decision:** Begin with exact NumPy cosine ranking and SQLite metadata.
- **Rationale:** Ranking is easy to verify and independent of retrieval infrastructure tuning.
- **Consequences:** Large-scale indexing is deferred; preserve an index abstraction for later replacement.
- **Status:** proposed.

## Evaluation protocol with weak relevance

Pre-register the split manifest and query versions. Use training groups for adapter/debug fixtures, development for choosing sampling/window settings, and test only for the final selected configuration. Start with a small matrix such as 2/5/10-second windows and 1/2 FPS; cap the sweep rather than indexing every combination. Include a shorter-window condition because OPEN/CLOSE may be brief. Record the actual number of encoded frames and effective duration for truncated final windows.

For a coarse action hit, define relevance as at least half of a weak action interior covered by the retrieved clip, within the correct episode. This coverage definition is deliberately different from temporal IoU and favors longer windows; report the window duration and a secondary temporal-IoU diagnostic so the tradeoff is visible. Freeze the rule before comparing configurations. A query success at rank K means at least one relevant hit appears among its first K results. Name this `Success@K`, not conventional recall over all relevant intervals. Separately report interval Recall@K using matched relevant intervals divided by total relevant intervals.

No query with zero relevant intervals in a partition should silently disappear. Report it as unsupported for positive-recall calculation and include explicit negative queries to measure spurious similarity. Useful controls include random ranking, a constant-vector fixture, and text-only/context-only representations where applicable. Report results by appliance and query, encoding wall time, cold/warm query latency, matrix size, and failure counts. Four query families yield descriptive results, not a reliable population estimate.

## Minimal user flow and API

Proposed `POST /v1/search` accepts `{query, index_id, split, top_k}` and returns an index identity plus typed hits. Proposed `GET /v1/episodes/{id}/video` resolves only registered source IDs. Never accept an arbitrary filesystem path from the browser. The page has a query box, index selector, ranked intervals, and a video player that seeks to the selected start. Display time in seconds while preserving integer microseconds in the response.

Keep a CLI usable before the web page exists: proposed subcommands are `ingest`, `index`, `search`, and `evaluate-retrieval`. These are implementation targets, not commands installed today. The viewer should display a short explanation that similarity means candidate relevance, and provide direct source playback so the user can judge the evidence.

## Implementation phases and acceptance gates

### S1 - Registry and time fixtures

Implement `ingest.py`, a migration, and manifest validation. Ingest the 24 current videos without reading labels into inference records. Add fixtures for missing files, changed hashes, invalid duration, duplicate IDs, and variable PTS. Exit with an inspect command showing count, duration, splits, and source hashes.

### S2 - Chunk cache and index

Implement deterministic window generation, array publication, resumable indexing, and index manifests. Use the approved adapter specification from COSMOS-EMBED-001. Inject a crash between file and metadata publication and prove recovery does not expose incomplete rows. Exit with an index that can be regenerated or verified without ambiguous defaults.

### S3 - Search and playback

Implement exact ranking, tie-breaking, partition filters, typed hits, and the minimal viewer. Test a tiny known matrix, a mismatched space, and a malicious path-like episode ID. Confirm seeking plays the returned source interval. Exit with a reproducible example query and visible source evidence.

### S4 - Frozen evaluation and handoff

Write query and matching policies, run the bounded development sweep, freeze the winner, and run the held-out partition once. Produce per-query metrics and resource measurements with no requirement that the model achieve an invented quality threshold. Engineering acceptance requires correct indexing, ranking, provenance, and reproducible evaluation; model quality is a reported result. Hand off the decoder, registry, cache contracts, and feature fixtures to Project 2.

## Failure modes the intern should expect

A long window can retrieve an action because of static kitchen context while locating it poorly. A short window can miss the action between sampled frames. A filename can leak an intended outcome if labels enter the input path. An index can produce plausible scores from incompatible spaces if dimension is the only check. A viewer can seek by frame count while the index used PTS and show the wrong moment. Each failure has a direct fixture or audit above; investigate the first broken layer rather than tuning the prompt to hide it.

## Shared system contract and reading map

This guide is a design for future implementation. Existing evidence is the root `src/virtualhome_corpus/` package and the validated assets under `output/virtualhome-corpus/home-v1`. Proposed application modules live under `workbench/src/video_workbench/`, preserving the umbrella guide's layout. Proposed APIs and pseudocode are not installed commands or claims of completed model behavior.

Use integer microseconds, half-open event intervals, opaque episode IDs, and source/producer hashes. Keep event time distinct from evidence/result availability and durable commitment. Keep model-safe inputs separate from evaluator labels. A model-space hash must identify preprocessing as well as weights. Unknown evidence remains unknown until a declared policy and new evidence justify a revision.

The existing corpus is a within-scene starter set, with weak action interiors and endpoint world truth. Exact temporal and dense visual-state metrics require reviewed labels; larger datasets do not remove that requirement. Model/runtime references were checked on 2026-09-06. Pin actual installed versions during implementation rather than assuming a mutable documentation page matches the environment.

### Existing file references

- [Existing generator contracts](../../../../../../src/virtualhome_corpus/core.py): lines 55, 102, and 167: planning, weak intervals, endpoint truth.
- [Existing rendering/export lifecycle](../../../../../../src/virtualhome_corpus/runner.py): lines 54, 125, 202, and 228: annotation quality, generation, validation, indices.
- [Checked v1 experiment](../../../../../../configs/virtualhome-household-v1.json): families, variants, groups, and camera.
- [Corpus operational playbook](../../../../../../docs/playbook/virtualhome-corpus.md): generation, resume, validation, and gallery.
- [Validated corpus report](../../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/design-doc/03-virtualhome-household-corpus-design-and-generation-report.md): observed results and label limitations.

### Ticket dependencies

- [COSMOS-EMBED-001](../../COSMOS-EMBED-001--embedding-runtime-baseline-on-mlx/index.md)
