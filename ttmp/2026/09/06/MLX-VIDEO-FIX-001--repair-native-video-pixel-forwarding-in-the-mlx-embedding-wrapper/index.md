---
Title: Repair native video pixel forwarding in the MLX embedding wrapper
Ticket: MLX-VIDEO-FIX-001
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
LastUpdated: 2026-09-06T14:00:19.916299-04:00
WhatFor: ""
WhenToUse: ""
---

# Repair native video forwarding in MLX embeddings

The installed MLX-VLM embedding wrapper omits video pixels when calling its hidden-state helper, although the shared backbone has a separate video branch. This ticket specifies reproduction, a minimal repair, request-isolation tests, numerical validation, and integration under a new feature-space identity.

**Current state (fresh audit, 2026-09-06):** P0–P2 are implemented in the clean isolated fork checkout at `6452614` on `fix/qwen3-vl-video-embeddings`. A fresh targeted run passed all 15 tests. P3 is active: existing 14:46–14:51 parity evidence is partial, including independent-processor token/pixel differences. P4 and P5 remain gated on correctness. See the diary for current findings.

- [Intern guide](design-doc/01-intern-guide-to-diagnosing-repairing-and-validating-native-mlx-video-embeddings.md)
- [Phased implementation tasks](tasks.md)
- [Investigation and delivery diary](reference/01-investigation-and-delivery-diary.md)
- [Source provenance](sources/manifest.json)

## Dependencies and consumers

- [COSMOS-EMBED-001 runtime baseline](../COSMOS-EMBED-001--embedding-runtime-baseline-on-mlx/index.md): supplies model pin, image baseline, and feature-space contract.
- [VIDEO-SEARCH-001 timestamped search](../VIDEO-SEARCH-001--project-1-timestamped-video-search/index.md): consumer of a verified native-video mode.
- [COSMOS-VIDEO-001 umbrella](../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/index.md): overall household-video research roadmap.

The search implementation and pooled-image environment remain independent. Repair checkout: `output/mlx-video-fix/mlx-vlm`; runtime: `output/mlx-video-fix/.venv`.

## Delivery

Uploaded the reviewed 12-page guide to `/ai/2026/09/06/MLX-VIDEO-FIX-001/MLX-VIDEO-FIX-001_Intern_Guide.pdf`.

- [PDF validation and preview paths](various/pdf-validation.json)
- [Upload receipt](various/remarkable-upload.json)
