---
Title: Bounded replay implementation and viewer contract
Ticket: VIDEO-REPLAY-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/api.py
      Note: Registered video API contract
    - Path: repo://workbench/src/video_workbench/rules/handoff.py
      Note: Existing exact-frame handoff and separate evidence conditions
    - Path: repo://workbench/src/video_workbench/temporal/store.py
      Note: Exact-time immutable state observations
    - Path: repo://workbench/src/video_workbench/verifiers/worker.py
      Note: Accepted isolated model worker
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-07T00:56:38.765537-04:00
WhatFor: ""
WhenToUse: ""
---


# Bounded replay implementation and viewer contract

## Decision and concrete deliverable

Implement a local replay application that exposes when evidence arrives, when bounded work starts and finishes, what gets dropped, and how separate rule conditions differ. The active deliverable is a CLI, a loopback API, a viewer, a saved replay log, feature-boundary smoke checks, and measured normal/overloaded runs with screenshots. This document supersedes the initial guide's implementation scope. The earlier guide and PDF remain historical design artifacts.

The immediate workload is the measured RULES camera-departure population from `output/rules-departure-v1/`. It contains twelve videos, full per-frame YOLO detections and timings, approved verifier frames, a sparse state-store baseline, and actual Qwen/Cosmos outcomes. Both models missed the four open-fridge violations. The viewer must explain that failure, not merely display successful alerts.

There are two explicit execution modes. **Recorded** mode releases previously measured detector outputs causally and schedules previously measured verifier results with their recorded service durations. This tests replay scheduling and inspection without spending additional model work, and must be labeled recorded throughout. **Live verifier** mode uses the same recorded perception stream but runs the accepted local verifier on the approved image through an isolated worker. Neither mode claims fresh live YOLO or native-embedding inference. A future live perception adapter fits the same bounded packet boundary.

## Existing components and ownership

- `perception/detector.py` owns the pinned YOLO adapter and its saved per-frame timing/provenance.
- `rules/departure.py` owns the causal disappearance proposal; its state resets across dropped or nonconsecutive frame coverage.
- `rules/evaluate.py` owns deterministic rule semantics. The viewer never reimplements rules.
- `rules/handoff.py` and `verifiers/contracts.py` own exact-time questions, bindings, and separately conditioned evidence.
- `verifiers/worker.py`, `profiles.py`, and `visibility.py` own model execution and output parsing. Live replay must use the accepted profile and strict evidence validation.
- `temporal/store.py` owns exact-time observation history. Imported observations carry original availability and become visible only after the replay horizon reaches it.
- `api.py` establishes the existing registered episode video URL and hash-checked media-serving pattern. Replay uses the same `/v1/episodes/{id}/video` contract without requiring a loaded search index.

New modules belong in `workbench/src/video_workbench/replay/`: `clock.py`, `broker.py`, `scheduler.py`, `store.py`, `engine.py`, `worker.py`, `app.py`, and `viewer.html`. A module CLI (`python -m video_workbench.replay`) exposes run and serve commands without constructing an embedding model.

## Clock and source model

Each run selects one registered episode and a bounded repetition count. Repetitions are capacity experiments, never additional independent accuracy samples. Source event time and wall service duration remain separate. The monotonic replay clock maps elapsed wall seconds to run microseconds with a declared positive speed. Each cycle occupies one source-video duration; a local frame PTS maps to `cycle * duration_us + pts_us`.

A frame is unavailable before its run source timestamp. A precomputed detection or feature is also unavailable before its declared dependency end and availability time. Cached files being present on disk does not make their contents available to workers. Result availability is assigned from the replay clock when the host observes completion; it is never copied from the frame timestamp. A speed other than one is explicitly accelerated replay, and wall latency is reported without relabeling it as real-time latency.

The clock continues while work drains after end of source. A run transitions from running to draining to complete; cancellation produces a terminal cancelled run. An unexpected process exit leaves a visibly interrupted run on later inspection. Automatic resume and model retries are deferred.

## Evidence broker

The trusted host may index complete source metadata and paths. Workers receive bounded job payloads containing only released observations or exact approved image files. They never receive the original complete video path. For image evidence, the broker validates registration and source hash, decodes the requested exact source frame, writes an immutable PNG into the run's evidence directory, and binds its hash and local PTS. Frame and feature requests beyond the supplied horizon fail before worker launch.

The broker rejects unknown IDs, mismatched source hashes, unavailable dependencies, oversized payloads, and requests outside the selected episode/cycle. Disk evidence is retained for inspection; in-memory queued payloads are bounded. Decoder work may use source preroll internally, but only the selected released frame leaves the broker. The worker is a trusted local subprocess, not an OS filesystem security sandbox; the guarantee is a reviewed application data boundary, not resistance to malicious worker code.

```text
registered video + measured trace + sampled state store
                         |
                  monotonic clock
                         |
                 evidence broker
                         |
             bounded mandatory/optional jobs
                         |
                  one subprocess worker
                         |
             append-only replay records
                         |
            rules + separate verifier evidence
                         |
             loopback API and timeline viewer
```

## Queue and execution policy

Bound the total admitted input bytes and job count, including the running job. One job runs at a time. Mandatory perception work has priority over optional verifier work among queued jobs; running work is nonpreemptive until its deadline. When admitting mandatory work would exceed a bound, evict queued optional work first. If still full, drop the arriving job. Optional work cannot evict mandatory work. Every rejection, eviction, deadline, cancellation, or worker failure creates a record with job identity, affected source time, reason, and condition.

A queued job has an absolute wall deadline established at admission. Its remaining budget, not a fresh full timeout, applies at launch. The host launches each worker in its own process group, polls without blocking source ingestion, kills and reaps the group on timeout/cancellation, bounds the result payload before loading it, and records enqueue/start/finish wall times. Fixed trusted worker entry points prevent the API from launching arbitrary commands.

Perception gaps break the consecutive-frame assumptions of the departure detector. Reset its prefix state on a missing frame index or cycle change and expose the gap in the log. A dropped optional verifier leaves its baseline UNKNOWN visible. No absence-of-event coverage claim is inferred from an overloaded stream.

```python
while source_remains or scheduler.has_work:
    horizon = clock.now_us()
    for released_item in source.ready_through(horizon):
        packet = broker.approve(released_item, horizon)
        scheduler.submit(packet, count_limit, byte_limit, deadline)
    for completion in scheduler.poll():
        store.append(completion, available_us=clock.now_us())
        if completion.is_perception:
            reset_prefix_if_coverage_gap(completion)
            candidate = departure.observe(completion)
            if candidate:
                baseline = evaluate_exact_time_state(candidate)
                store.append(baseline)
                maybe_submit_one_verifier(candidate, baseline)
        elif completion.is_verifier:
            store.append(separate_conditioned_evaluation(completion))
```

## Persistence, identity, and as-of queries

Use SQLite with one host writer and append-only event rows. Each row has a sequence ID, type, stable case ID when applicable, cycle, source event time, availability time, and a bounded JSON payload. Job/result identities are stable within the run and duplicate insertion is rejected or idempotent only for identical content. Polling clients request rows after a sequence cursor and through an explicit `as_of_us`, with bounded page size.

A case groups a rule, bound target, cycle, and trigger. It does not derive its identity from PASS/VIOLATION/UNKNOWN. Baseline and verifier results are separate immutable conditions attached to that case. Selecting a later as-of time may reveal additional conditions without deleting an earlier one. This provides inspectable history without a general revision or supersession mechanism.

Persist run configuration and measured summary with the replay records. Restart supports read-only inspection of a completed or interrupted run. It does not resume in-flight work or promise exactly-once model execution. There is no network publisher, so no transactional outbox is needed; the viewer polls committed rows directly.

## API and viewer

The server binds to loopback. The source registry is fixed by an operator-supplied manifest. API callers select an episode ID and bounded replay options; they cannot choose arbitrary filesystem paths, model directories, or executable commands. Only one active replay is allowed per server, preserving the one-worker memory policy. Historical run listing is bounded.

| Endpoint | Contract |
|---|---|
| `GET /v1/replay/sources` | Registered episodes, durations, target labels, supported modes |
| `POST /v1/replays` | Start one run with registered episode, mode, speed, repetitions, and queue policy |
| `GET /v1/replays` | Bounded list of saved runs |
| `GET /v1/replays/{id}` | Status, clock horizon, queue metrics, summary |
| `POST /v1/replays/{id}/cancel` | Cancel queued work and terminate active worker |
| `GET /v1/replays/{id}/events` | Cursor pagination and explicit as-of visibility |
| `GET /v1/replays/{id}/evidence/{id}` | Hash-checked approved image from this run |
| `GET /v1/episodes/{id}/video` | Existing registered-ID video contract with range support |

The page aligns source video, sampled state observations, candidate events, separate rule conditions, and coverage gaps. Selecting a case displays exact approved evidence, rule parameters, baseline/conditioned results, runtime status, and event/availability/queue timings. A visible run mode label distinguishes recorded results from fresh verifier calls. Seeking changes the as-of query and never reveals a future condition early. Ordinary source playback uses local PTS; cycle/run time remains visible beside it.

Use plain HTML/JavaScript and the existing FastAPI stack. Polling is sufficient. Use text insertion for model rationales; no model output becomes HTML. The API supplies all decisions and explanations.

## Acceptance evidence

P3 must provide meaningful feature smoke for future-frame rejection, precomputed dependency gating, source-to-run mapping, delayed completion visibility, count and byte bounds including running work, mandatory priority, optional eviction, queue expiry, worker timeout/reaping, malformed/oversized worker output, cancellation, and frame-gap prefix reset. A deliberately slower-than-source worker must produce visible drops or expiry while retaining the declared bounds.

P4 must provide a completed normal recorded run over actual RULES evidence, a live accepted-verifier run on an approved image, and a separate repeated accelerated capacity run. Measure wall service/queue/total latency, count/byte high-water marks, dropped work, processed source coverage, process memory, and run duration. The underlying reviewed rule accuracy is inherited from the fixed RULES experiment; repetitions are not re-scored as new independent observations.

Inspect the actual viewer in a browser and save screenshots of at least a missed open-fridge case, a detected open-microwave case, and overload/gap visibility. Verify registered media serving, source seeking, pagination, as-of history, rejected unknown IDs, and absence of browser-side rule evaluation. Record reproduction commands, actual measured limits, and remaining limitations in the ticket diary and report.

## Explicitly deferred work

- Revision/supersession chains, conflict reconciliation, and lifecycle states beyond immutable separate conditions.
- Transactional outbox, distributed publication, automatic crash recovery, and durable in-flight retries.
- Fresh live YOLO/native-embedding inference during replay and multi-worker model scheduling.
- Staged real-video collection and transfer evaluation. Existing synthetic evidence cannot satisfy this gate.
- Live camera capture, multi-person identity, room-threshold inference, and operational false-alert acceptance.

These remain visible follow-up tasks. They are not silently marked complete by the bounded replay implementation.
