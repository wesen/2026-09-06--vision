---
Title: Object detection tracking and visual evidence selection for VLMs
Ticket: VIDEO-PERCEPTION-001
Status: active
Topics:
    - video
    - embeddings
DocType: index
Intent: long-term
Owners: []
RelatedFiles: []
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T14:52:49.80359-04:00
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
