---
Title: Project 2 - Observable state recognition
Ticket: VIDEO-STATE-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: index
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/predicates/region_app.py
      Note: Evidence review API
    - Path: repo://workbench/src/video_workbench/predicates/region_experiment.py
      Note: Coverage-aware evaluation
    - Path: repo://workbench/src/video_workbench/predicates/regions.py
      Note: Source-bound crop and hint policies
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T16:23:51.617928-04:00
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

The evidence timeline runs at `http://127.0.0.1:8772/`. The YOLO follow-up is now complete: six representations and two classifiers on the same fixed samples. No held-out microwave crop was accepted. Prioritize localization and observability data before temporal memory.

- [YOLO region comparison and failure analysis](reference/04-yolo-region-evidence-state-comparison-and-failure-analysis.md)
- [Region results](various/region-run-v1/results.json)
- [Region observations](various/region-run-v1/observations.jsonl)

Region comparison UI: `http://127.0.0.1:8774/`.

## Guide delivery

Uploaded to `/ai/2026/09/06/VIDEO-STATE-001/VIDEO-STATE-001_Intern_Guide.pdf`.

- [PDF review and hashes](various/pdf-validation.json)
- [Upload receipt](various/remarkable-upload.json)
