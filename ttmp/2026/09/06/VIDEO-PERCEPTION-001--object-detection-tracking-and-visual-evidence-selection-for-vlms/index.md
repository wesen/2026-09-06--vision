---
Title: Object detection tracking and visual evidence selection for VLMs
Ticket: VIDEO-PERCEPTION-001
Status: complete
Topics:
    - video
    - embeddings
DocType: index
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/perception/app.py
      Note: Read-only source-aligned replay
    - Path: repo://workbench/src/video_workbench/perception/proposals.py
      Note: Causal proposal policy and budgets
    - Path: repo://workbench/src/video_workbench/predicates/regions.py
      Note: Fixed region evidence comparison
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T16:44:31.957609-04:00
WhatFor: ""
WhenToUse: ""
---



# Object detection, tracking, and visual evidence selection

This project supplies source-aligned object detections, tracks, contextual crops, and candidate interaction intervals to the video workbench. It evaluates whether focused evidence and fallible detector hints improve VLM recognition at a measured inference budget.

The design is complete; implementation is planned. No detector packages were installed or runtime code changed by this ticket.

- [Intern analysis, design, and implementation guide](design-doc/01-intern-analysis-design-and-implementation-guide.md)
- [Investigation diary](reference/01-investigation-diary.md)
- [Implementation phases and acceptance tasks](tasks.md)
- [Architecture diagram](various/architecture.png)

Dependencies: VIDEO-SEARCH-001, VIDEO-CORPUS-001, VIDEO-STATE-001, VIDEO-TEMPORAL-001, COSMOS-VERIFY-001, and VIDEO-REPLAY-001. This is a separate perception project; it does not replace temporal action segmentation.

Delivery receipts and PDF validation are retained under `various/`.

## Implemented and evaluated

D1–D4 are implemented. The 60-video run, reviewed pilot, short identity spans, fixed mask probe, causal proposals, and twelve-condition state comparison are complete. Quality limitations remain explicit: six of nine transition brackets were missed by proposals and no held-out microwave crop was accepted.

- [Implementation and measured evidence report](reference/02-yolo-perception-implementation-and-measured-evidence-report.md)
- [Implementation diary](reference/01-investigation-diary.md)
- [Pipeline counts and proposal evaluation](various/pipeline-evaluation.json)

Replay: `http://127.0.0.1:8773/`.

The full YOLO technical article was published to go-go-parc in commit `03dc93c` and pushed to `origin/main`. [Publication receipt](various/vault-publication.json).
