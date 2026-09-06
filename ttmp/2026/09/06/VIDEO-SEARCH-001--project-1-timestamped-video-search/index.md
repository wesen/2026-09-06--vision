---
Title: Project 1 - Timestamped video search
Ticket: VIDEO-SEARCH-001
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
LastUpdated: 2026-09-06T14:31:39.122269-04:00
WhatFor: ""
WhenToUse: ""
---


# Project 1 - Timestamped video search

Build timestamped retrieval, cache integrity, a local viewer, and split-aware evaluation.

Parent: [COSMOS-VIDEO-001](../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/index.md). Dependencies: COSMOS-EMBED-001.

- [Intern guide](design-doc/01-intern-analysis-design-and-implementation-guide.md)
- [Tasks](tasks.md)
- [Diary](reference/01-design-and-delivery-diary.md)

Design, technical validation, six-page PDF review, and reMarkable delivery are complete. The pooled-image search implementation and frozen evaluation are complete. Native-video repair and broader runtime profiling remain in the embedding workstream.

## Guide delivery

Uploaded to `/ai/2026/09/06/VIDEO-SEARCH-001/VIDEO-SEARCH-001_Intern_Guide.pdf`.

- [PDF review and hashes](various/pdf-validation.json)
- [Upload receipt](various/remarkable-upload.json)

## Implemented application

- [Implementation report and measured results](reference/03-implementation-and-evaluation-report.md)
- [Implementation diary](reference/02-implementation-diary.md)
- [Actual final viewer screenshot](various/screenshots/03-selected-index-test-playback.png)
- [Frozen evaluation screenshot](various/screenshots/04-frozen-evaluation-report.png)

Selected configuration: 10-second windows at 1 FPS. Held-out Success@5: 75%; random baseline: 74%. Treat the output as coarse candidate evidence.

## Vault deep dive

Published a 6,247-word textbook-style technical article with three Mermaid diagrams and four screenshots in go-go-parc. Vault commit `8e8a874` is pushed to main. [Delivery validation](various/vault-article-validation.json).


## Native-video repair handoff — 2026-09-06

MLX-VIDEO-FIX-001 completed the wrapper repair and explicit FP32 native mode. The repair is pushed to `wesen/mlx-vlm` at `6452614`; workbench integration is commit `127921a`. Eight official-reference FP32 cases and a nine-clip development build/reuse passed. Native uses its own runtime, processor/PTS contract and clip-cache identity. The existing pooled-image baseline and environment remain available; quantized native rollout and semantic superiority are not accepted claims.

See [the root-cause and review handoff](../MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/reference/03-root-cause-and-review-handoff.md). The 6,805-word textbook report is committed and pushed in go-go-parc at `02925f6`. No public PR or issue was created; the user is reviewing the fork personally.
