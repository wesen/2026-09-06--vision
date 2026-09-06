---
Title: Project 2 - Observable state recognition
Ticket: VIDEO-STATE-001
Status: complete
Topics:
    - video
    - embeddings
    - cosmos
DocType: index
Intent: long-term
Owners: []
RelatedFiles: []
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T15:55:49.214649-04:00
WhatFor: ""
WhenToUse: ""
---


# Project 2 - Observable state recognition

Measure visual state discrimination, context effects, calibration, and abstention.

Parent: [COSMOS-VIDEO-001](../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/index.md). Dependencies: COSMOS-EMBED-001, VIDEO-SEARCH-001.

- [Intern guide](design-doc/01-intern-analysis-design-and-implementation-guide.md)
- [Tasks](tasks.md)
- [Diary](reference/01-design-and-delivery-diary.md)

Implementation and evaluation are complete. Five frozen baselines were evaluated on 144 reviewed RGB frames; the held-out results expose poor transfer and false certainty under occlusion. This is a completed exploratory experiment, not a deployment-ready recognizer.

- [Implementation and evidence report](reference/03-observable-state-baseline-implementation-and-evidence-report.md)
- [Implementation diary](reference/02-implementation-diary.md)
- [Frozen predictions](various/run-v2/observations.jsonl)
- [Results and producer configuration](various/run-v2/results.json)

The evidence timeline runs at `http://127.0.0.1:8772/`. Next recommended work: VIDEO-PERCEPTION-001 D1–D2 (detection, tracking, and contextual crops), followed by a fixed-interval representation comparison before temporal memory.

## Guide delivery

Uploaded to `/ai/2026/09/06/VIDEO-STATE-001/VIDEO-STATE-001_Intern_Guide.pdf`.

- [PDF review and hashes](various/pdf-validation.json)
- [Upload receipt](various/remarkable-upload.json)
