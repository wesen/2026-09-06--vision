---
Title: Project ticket map and intern reading order
Ticket: COSMOS-VIDEO-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/various/project-guide-delivery.json
      Note: Individual PDF destinations and hashes
    - Path: repo://ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/various/project-tickets.json
      Note: Eight project scopes and dependencies
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T13:14:14.096505-04:00
WhatFor: ""
WhenToUse: ""
---


# Project ticket map and intern reading order

Eight child tickets now divide the implementation into independently reviewable projects. Each has a dedicated intern guide, phased implementation tasks, a diary, and its own reMarkable edition. This umbrella remains the program overview and home of the completed VirtualHome v1 corpus. Creating design tickets does not mark their application implementation complete.

The user selected VirtualHome explicitly. The active simulator plan is to preserve the working corpus and improve its labels and diversity; Habitat is no longer an implementation task. Historical imported sources remain unchanged.

## Ticket map

- [COSMOS-EMBED-001: Embedding runtime baseline on MLX](../../COSMOS-EMBED-001--embedding-runtime-baseline-on-mlx/index.md). Prove text, image, and video embedding behavior and freeze a feature-space contract.
- [VIDEO-SEARCH-001: Project 1 - Timestamped video search](../../VIDEO-SEARCH-001--project-1-timestamped-video-search/index.md). Build timestamped retrieval, cache integrity, a local viewer, and split-aware evaluation.
- [VIDEO-STATE-001: Project 2 - Observable state recognition](../../VIDEO-STATE-001--project-2-observable-state-recognition/index.md). Measure visual state discrimination, context effects, calibration, and abstention.
- [VIDEO-TEMPORAL-001: Project 3 - Temporal models and durable memory](../../VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/index.md). Compare temporal decoders and store availability-aware facts without inventing missing steps.
- [COSMOS-VERIFY-001: Cosmos and Qwen verifier runtime baseline](../../COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/index.md). Compare bounded, evidence-grounded verifier behavior on identical local clips.
- [VIDEO-RULES-001: Project 4 - Temporal rules and bounded investigation](../../VIDEO-RULES-001--project-4-temporal-rules-and-bounded-investigation/index.md). Evaluate typed three-valued rules and audit bounded evidence refinement.
- [VIDEO-REPLAY-001: Project 5 - Replay and incident workbench](../../VIDEO-REPLAY-001--project-5-replay-and-incident-workbench/index.md). Integrate causal replay, incident revisions, a viewer, and held-out real-video evaluation.
- [VIDEO-CORPUS-001: VirtualHome corpus expansion and label calibration](../../VIDEO-CORPUS-001--virtualhome-corpus-expansion-and-label-calibration/index.md). Extend the working VirtualHome corpus with calibrated labels, controlled variations, and verified additional scenes.

## Dependency graph and recommended order

```text
existing VirtualHome corpus
    |
    +--> EMBED --> SEARCH --> STATE --> TEMPORAL --> RULES --> REPLAY
    |                          ^            ^         ^
    +--> CORPUS calibration ----+------------+---------+
    |
    +--> VERIFY runtime ------------------------------+
```

The graph shows implementation/data flow, not a requirement to wait for every upstream experiment before writing fixtures. The embedding runtime and Project 1 form the first application path. The verifier runtime can be investigated independently using reviewed packets. VirtualHome calibration can proceed independently and supplies stronger labels before Projects 2 through 4 make dense-state or exact-time claims. The rule evaluator begins with oracle facts before integrating predicted facts. Replay begins with mock workers before integrating every model.

Read the child guides in this order: embedding runtime, video search, VirtualHome calibration, state recognition, temporal models, verifier runtime, rules, and replay. An intern assigned to one project should read its own guide first, then the contract sections of direct dependencies. The original umbrella intern guide remains a broader textbook-style introduction; the child guides define the current project-level scope and acceptance gates.

## Shared ownership, so implementations fit together

All application modules proposed in these guides live under `workbench/src/video_workbench/`, matching the original umbrella layout. They do not exist yet. The working generator remains under root `src/virtualhome_corpus/`. The embedding ticket creates the initial package, shared identity/time records, sampling contracts, and encoder protocol. Search extends generic video ingestion, feature storage, retrieval, and shared source playback. State owns observation/calibration records. Temporal owns model sequences and the fact store. Verifier owns bounded request/result packets. Rules owns the AST, evaluator, and investigation budgets. Replay owns scheduling, incident lifecycle, and the integrated viewer.

The interfaces are proposed design contracts. When implementation reveals an unsupported runtime API, change the narrow adapter and document the capability result. Do not let each project create a second incompatible definition of timestamps, source identity, or feature-space identity. Changes to shared contracts should update producer and consumer fixtures together.

## Common acceptance rules

- Preserve source/producer hashes and immutable experiment manifests.
- Use integer microseconds and half-open video intervals; store actual source PTS.
- Separate event time, evidence/result availability, and durable commitment.
- Keep evaluator labels out of model inputs, cache keys that reach models, and prompt text.
- Preserve UNKNOWN for unobservable, stale, conflicting, or incomplete evidence.
- Distinguish native video, pooled image, offline smoothing, and causal inference modes.
- Split by lineage/group before deriving overlapping windows or alternate views.
- Treat v1 action interiors as weak labels and final graph verdicts as endpoint world truth.
- Mark proposed files/APIs as proposed and actual observations as measured.
- Report a null model-quality result honestly; successful implementation does not require a fabricated accuracy target.

## What the current corpus enables and what it cannot establish

The validated v1 release contains 24 videos, 4,261 paired RGB/graph frames, and 426.1 seconds of footage. It supports source/cache integration, coarse action retrieval, sample-based visual inspection, and endpoint oracle checks. It does not provide calibrated dense visual-state labels or precise departure/action boundaries. Camera shifts inside one apartment do not establish unseen-home generalization.

VIDEO-CORPUS-001 therefore starts with transition review and export calibration, then adds controlled variations and only verified additional scenes. This replaces the old broad simulator-installation spike with an evidence-driven extension of a working system. Projects may use hand-authored fixtures and small reviewed subsets while that work proceeds; their reports must state which data-quality gates remain unmet.

## Delivery and implementation status

Each child ticket's `tasks.md` separates completed design/delivery work from unchecked implementation phases. The guides contain prose explanations, diagrams, proposed API records, pseudocode, existing file references, decision records, test cases, failure handling, and acceptance criteria. All eight guides have been rendered, visually reviewed, and uploaded individually. Each is six pages (48 total). Per-ticket receipts are linked from the ticket indices; the [delivery inventory](../various/project-guide-delivery.json) records all source/PDF hashes and destinations. There are 107 open implementation tasks across the eight projects.
