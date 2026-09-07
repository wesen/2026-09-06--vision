---
Title: Cosmos and Qwen verifier runtime baseline
Ticket: COSMOS-VERIFY-001
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
LastUpdated: 2026-09-06T13:13:51.590478-04:00
WhatFor: ""
WhenToUse: ""
---

# Cosmos and Qwen verifier runtime baseline

Compare bounded, evidence-grounded verifier behavior on identical local clips.

Parent: [COSMOS-VIDEO-001](../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/index.md). Dependencies: existing VirtualHome corpus.

- [Intern guide](design-doc/01-intern-analysis-design-and-implementation-guide.md)
- [Tasks](tasks.md)
- [Diary](reference/01-design-and-delivery-diary.md)
- [Measured reasoning comparison and case gallery](reference/08-measured-qwen-and-cosmos-prompted-reasoning-comparison.md)

Design and reMarkable delivery are complete. The bounded single-image runtime, practical JSON recovery, and matched 8B reasoning comparison are implemented. Both direct controls scored 22/24 on the latest held-out set; Cosmos reasoning scored 20/24, and all conditions missed both unknown cases. Multi-image/native-video verification and broader semantic acceptance remain open. See the phased task list.

## Guide delivery

Uploaded to `/ai/2026/09/06/COSMOS-VERIFY-001/COSMOS-VERIFY-001_Intern_Guide.pdf`.

- [PDF review and hashes](various/pdf-validation.json)
- [Upload receipt](various/remarkable-upload.json)
