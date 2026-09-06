---
Title: Embedding runtime baseline on MLX
Ticket: COSMOS-EMBED-001
Status: active
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
LastUpdated: 2026-09-06T13:13:50.814553-04:00
WhatFor: ""
WhenToUse: ""
---

# Embedding runtime baseline on MLX

Prove text, image, and video embedding behavior and freeze a feature-space contract.

Parent: [COSMOS-VIDEO-001](../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/index.md). Dependencies: existing VirtualHome corpus.

- [Intern guide](design-doc/01-intern-analysis-design-and-implementation-guide.md)
- [Tasks](tasks.md)
- [Diary](reference/01-design-and-delivery-diary.md)

Design, technical validation, six-page PDF review, and reMarkable delivery are complete. Application implementation remains open in the phased task list.

## Guide delivery

Uploaded to `/ai/2026/09/06/COSMOS-EMBED-001/COSMOS-EMBED-001_Intern_Guide.pdf`.

- [PDF review and hashes](various/pdf-validation.json)
- [Upload receipt](various/remarkable-upload.json)


## Native-video repair handoff — 2026-09-06

MLX-VIDEO-FIX-001 completed the wrapper repair and explicit FP32 native mode. The repair is pushed to `wesen/mlx-vlm` at `6452614`; workbench integration is commit `127921a`. Eight official-reference FP32 cases and a nine-clip development build/reuse passed. Native uses its own runtime, processor/PTS contract and clip-cache identity. The existing pooled-image baseline and environment remain available; quantized native rollout and semantic superiority are not accepted claims.

See [the root-cause and review handoff](../MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/reference/03-root-cause-and-review-handoff.md). The 6,805-word textbook report is committed and pushed in go-go-parc at `02925f6`. No public PR or issue was created; the user is reviewing the fork personally.
