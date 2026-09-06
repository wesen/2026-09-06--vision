---
Title: Intern analysis design and implementation guide
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
    - Path: repo://configs/virtualhome-household-v1.json
      Note: Existing implementation evidence for this design
    - Path: repo://docs/playbook/virtualhome-corpus.md
      Note: Existing implementation evidence for this design
    - Path: repo://src/virtualhome_corpus/core.py
      Note: Existing implementation evidence for this design
    - Path: repo://src/virtualhome_corpus/runner.py
      Note: Existing implementation evidence for this design
ExternalSources: []
Summary: Integrate causal replay, incident revisions, a viewer, and held-out real-video evaluation.
LastUpdated: 2026-09-06T13:13:52.051767-04:00
WhatFor: ""
WhenToUse: ""
---


# Project 5 - Replay and incident workbench

## The system the intern will integrate

This project turns the earlier components into an inspectable application. It replays recorded video at a controlled availability rate, schedules bounded inference, stores facts and incident revisions, and lets a user inspect why a procedural conclusion changed. The purpose is to test causality, latency, recovery, and transfer to real footage before claiming that the workbench can operate live.

A video file contains future frames that are already on disk. An availability-faithful replay must nevertheless behave as if those frames have not arrived yet. Hiding them in the viewer is insufficient if a background encoder or verifier can read the entire file. The scheduler and evidence broker enforce the horizon; model workers receive only approved packets.

The deliverable includes a replay CLI, incident lifecycle, small local UI, fault-injection fixtures, and a held-out real-video report. It depends on Projects 1 through 4. It does not require a live camera or a distributed service, and it must remain useful when a verifier is unavailable.

## Current state and architectural gap

The existing VirtualHome generator writes complete recordings and a static evaluator gallery. It does not simulate evidence arrival, schedule models, maintain incident revisions, or recover in-flight work. Project 1 provides source registration and retrieval; Project 2 provides state observations; Project 3 provides availability-aware facts; Project 4 provides deterministic decisions and bounded refinement. This project integrates those contracts rather than reimplementing them in browser code.

Use the 24 current episodes for replay and failure fixtures, while retaining their weak-label limitations. Synthetic footage is not evidence of real-video accuracy. Collect a small staged real-video set with reviewed labels and permission to use the recordings, freeze it before final tuning, and report it as a separate domain. No collection has been performed by this design task.

## Architecture and ownership

```text
registered recording -> replay clock -> evidence broker
                                            |
                                      bounded queues
                                            |
                                  embedding / state / TCN
                                            |
                                      temporal store
                                            |
                                   rules + investigator
                                            |
                                    incident revisions
                                            |
                                   read-only local API
                                            |
                                  timeline and playback
```

Proposed modules under the workbench package are `replay/clock.py`, `replay/broker.py`, `replay/scheduler.py`, `incidents.py`, and `api.py`. Add `workbench/ui/` only after the replay log and API fixtures are usable. The database remains the durable source for facts, jobs, and incident revisions. One model worker at a time is the initial memory-safe scheduling policy; measured capacity may justify changes later.

## Three clocks and availability policy

Event time locates an observation in the source video. Evidence availability is when the required frames may be used. Result availability includes the time at which the computation completes. Commitment time records durable persistence. Use a monotonic run clock and an explicit mapping to source PTS; store wall-clock timestamps separately for operational logs.

For a trailing window ending at source second 10, inference cannot begin before its last required frame arrives. If processing takes 1.2 seconds, a result may become available at replay second 11.2 or later, depending on queue delay. Do not assign the result time 10 merely because that is the window end. A faster-than-real-time test mode must declare its clock policy and cannot be mixed with real-time latency measurements.

```python
# Proposed broker contract.
def evidence_packet(episode_id, interval, as_of_us):
    frames = catalog.frames_in(interval)
    approved = [f for f in frames if f.available_us <= as_of_us]
    return Packet(approved, horizon_us=as_of_us)

# Pseudocode: scheduling is constrained by evidence arrival.
while clock.running:
    ready = broker.release_through(clock.now_us())
    scheduler.enqueue_ready_windows(ready)
    for result in workers.completed():
        result.available_us = clock.now_us()
        store.commit_result_and_outbox(result)
    publish_outbox()
```

The broker should supply decoded approved frames or an actually truncated clip. Passing the original complete video path to a worker can bypass the horizon. Cached features also carry latest-source-frame time and availability policy; a precomputed whole-episode representation cannot masquerade as an online feature.

## Bounded scheduling and overload behavior

A queue that grows without bound hides the fact that the model is slower than the incoming stream. Bound jobs by count and estimated input bytes, record enqueue/start/finish times, and make overload explicit. The first policy can drop redundant queued sampling windows while preserving an explicit gap event. Never drop a frame silently and then claim continuous observation coverage.

Separate optional verifier jobs from essential ingest/state jobs. Give verifier work a finite budget and deadline; cancel or defer optional jobs when they would starve the base stream. Define whether a dropped window can later be processed offline and tag any such result as a delayed revision. The UI should distinguish "no violation observed" from "observation unavailable because processing fell behind."

Measure arrival rate and service rate in compatible units. A real-time factor above one for sustained mandatory processing implies queue growth unless sampling, model cost, or workload changes. A short demonstration with an initially empty queue is not proof of sustainable real-time capacity.

## Incident identity and revision lifecycle

An incident groups decisions about one rule scope for one episode and bound entity. Its ID must remain stable when the status changes. Suggested identity components are rule version, episode ID, entity binding, and a stable triggering-event ID or explicitly defined interval scope. Avoid using the current status, free-form message, or arrival timestamp as the identity.

Use lifecycle states such as candidate, confirmed, dismissed, and unresolved, while preserving the underlying rule decision PASS/VIOLATION/UNKNOWN. Lifecycle describes workflow; decision describes evidence. A late verifier proposal can create a new revision without erasing the original alert. The record should show what was known when the original alert was emitted.

```json
{
  "incident_id": "incident-example",
  "revision": 2,
  "decision": "UNKNOWN",
  "lifecycle": "unresolved",
  "event_start_us": 8000000,
  "available_us": 12000000,
  "supersedes_revision": 1,
  "reason": "late conflicting evidence",
  "evidence_ids": ["frame-example"]
}
```

The example is illustrative. Real revisions must reference stored evidence, rule versions, and fact IDs. A unique `(incident_id, revision)` key and idempotent job IDs prevent duplicate replay messages from creating duplicate incidents.

## Persistence, restarts, and event delivery

Persist a job result, its fact/decision revisions, and an outbox notification in one database transaction where practical. The outbox is a table of notifications awaiting delivery; a publisher can retry it safely. The browser consumes revision IDs idempotently. This avoids losing the notification after committing an incident or emitting a notification for a transaction that later fails.

On restart, load the replay cursor, recover queued/in-flight jobs under an explicit retry policy, and resume from a durable watermark. A worker may have completed before a crash while its result was not committed; reprocessing is acceptable if the result identity is idempotent. Do not assume exactly-once model execution. Aim for at-least-once work with exactly-once durable identity.

Use explicit SQLite transactions through [Python's sqlite3 API](https://docs.python.org/3.11/library/sqlite3.html). Keep the writer policy and connection ownership documented, and test transaction rollback rather than relying on implicit defaults from a different Python version.

### Decision: prerecorded replay before live capture

- **Context:** We need repeatable latency and failure experiments with known source content.
- **Options considered:** Live camera first, unrestricted file processing, or horizon-enforced replay.
- **Decision:** Build horizon-enforced prerecorded replay first.
- **Rationale:** It makes future leakage and restart behavior reproducible while retaining realistic evidence arrival.
- **Consequences:** A later camera adapter is still required; replay performance alone does not prove live deployment readiness.
- **Status:** proposed.

## Local API and the intern-facing viewer

Proposed endpoints are `POST /v1/replays` to create a run from a registered episode and policy, `GET /v1/replays/{id}` for queue/cursor status, `GET /v1/incidents` with pagination and run filters, and `GET /v1/incidents/{id}/revisions` for evidence history. Project 1 owns the shared video source endpoint and search contract; reuse them. A revision stream may use server-sent events or WebSocket later, but polling is sufficient for the first verified UI.

The page should align four tracks: video playback, state observations including unknown regions, temporal events, and incident revisions. Selecting an incident shows the rule, supporting/contradicting evidence, as-of horizon, and revision history. It must not recompute rules in JavaScript. Restrict media requests to registered IDs and use bounded pagination; the UI should not expose arbitrary filesystem reads.

## Implementation phases and acceptance gates

### W1 - Clock and evidence broker

Implement the run clock, source-to-run time mapping, and broker with a mock worker. Test delayed frames and a forbidden future-frame request. Exit when changing inaccessible future source content does not change any past committed result.

### W2 - Scheduler and overload policy

Implement bounded queues, priorities, deadlines, and explicit gap records. Inject a worker slower than the source rate and show bounded memory with visible coverage loss or delay. Exit with enqueue/start/finish metrics and a documented policy for every dropped/deferred job.

### W3 - Incident lifecycle and recovery

Implement stable identities, revisions, transactional outbox, and cursor recovery. Inject duplicate events and crashes before/after result commit. Exit when restart produces the same durable incidents without duplicate identities and preserves the history of earlier decisions.

### W4 - Viewer and integration

Build the minimal API and timeline using stored records. Verify source seeking, revision ordering, unknown display, and no client-side rule recomputation. Exit with an inspectable demo that can explain both a correct detection and a failure.

### W5 - Sustained replay and real-video transfer

Run a declared-duration replay workload, including a looped stress stream if necessary. Label looped stress results as capacity tests, not independent accuracy samples. Measure false alerts per hour, missed violations, unknown rate, p50/p95 decision latency, queue depth, dropped coverage, and memory. Evaluate untouched staged real footage separately and report domain shift. Exit with a reproducible report and an evidence-based decision about whether live capture is a reasonable next step.

## Review exercise

Delay a verifier result about source second 8 until replay second 14. Query the incident history as of seconds 10 and 15. The earlier query must show only the evidence available then; the later one may show a revision. If both queries return the final answer, the application has lost its causal history even if its final classification is correct.

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

- [VIDEO-SEARCH-001](../../VIDEO-SEARCH-001--project-1-timestamped-video-search/index.md)
- [VIDEO-STATE-001](../../VIDEO-STATE-001--project-2-observable-state-recognition/index.md)
- [VIDEO-TEMPORAL-001](../../VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/index.md)
- [VIDEO-RULES-001](../../VIDEO-RULES-001--project-4-temporal-rules-and-bounded-investigation/index.md)
