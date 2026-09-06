---
Title: VirtualHome corpus expansion and label calibration
Ticket: VIDEO-CORPUS-001
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
LastUpdated: 2026-09-06T15:23:51.618195-04:00
WhatFor: ""
WhenToUse: ""
---


# VirtualHome corpus expansion and label calibration

Extend the working VirtualHome corpus with calibrated labels, controlled variations, and verified additional scenes.

Parent: [COSMOS-VIDEO-001](../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/index.md). Dependencies: existing VirtualHome corpus.

- [Intern guide](design-doc/01-intern-analysis-design-and-implementation-guide.md)
- [Tasks](tasks.md)
- [Diary](reference/01-design-and-delivery-diary.md)

Design, technical validation, six-page PDF review, and reMarkable delivery are complete. Application implementation remains open in the phased task list.

## Guide delivery

Uploaded to `/ai/2026/09/06/VIDEO-CORPUS-001/VIDEO-CORPUS-001_Intern_Guide.pdf`.

- [PDF review and hashes](various/pdf-validation.json)
- [Upload receipt](various/remarkable-upload.json)

## Completed release — 2026-09-06

Implemented 48 full trajectories across three apartments and four interaction families, plus 48 two-second windows with preserved lineage. All 96 videos passed decoding/media checks; the 24 original videos remain unchanged. The corpus is scoped to weak action supervision, with explicit visual exclusions and conservative calibration findings.

- [Implementation and evidence report](reference/03-diverse-household-release-implementation-and-evidence.md)
- [Detailed implementation diary](reference/02-implementation-diary.md)
- [Release audit](various/release-audit.json)
- [Visual evidence dashboard](various/release-gallery.html)
- [Screenshot inventory](various/screenshots/index.json)

Full inputs: `output/virtualhome-corpus/diversity-v2/inputs.jsonl`. Fixed-window inputs: `output/virtualhome-corpus/diversity-v2/windows-v1/inputs.jsonl`.
