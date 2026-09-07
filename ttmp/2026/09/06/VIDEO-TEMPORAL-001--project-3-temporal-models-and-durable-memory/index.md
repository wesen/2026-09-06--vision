---
Title: Project 3 - Temporal models and durable memory
Ticket: VIDEO-TEMPORAL-001
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
LastUpdated: 2026-09-06T19:32:18.108515-04:00
WhatFor: ""
WhenToUse: ""
---


# Project 3 - Temporal models and durable memory

Measured classical and learned temporal decoders, with availability-aware sampled observation memory that does not invent missing steps.

Parent: [COSMOS-VIDEO-001](../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/index.md). Dependencies: VIDEO-SEARCH-001, VIDEO-STATE-001.

- [Intern guide](design-doc/01-intern-analysis-design-and-implementation-guide.md)
- [Tasks](tasks.md)
- [Diary](reference/01-design-and-delivery-diary.md)

Implementation and measured comparisons are complete. The final memory scope is immutable sampled observations and exact-time as-of queries; general revisions, retractions, expiry, and inferred continuous state were explicitly deferred during user-requested wrap-up.

## Measured outcome and final report

- 48 VirtualHome-AIST episodes; 792 dense pooled-image features.
- Independent test macro recall 21.16%; selected smoother 21.31% with lower accuracy; selected causal TCN mean 18.63% across three seeds.
- 2448 actual state/action observations; 4896 replay queries preserved across restart.
- [Classical comparison](reference/02-measured-classical-temporal-comparison.md)
- [Causal TCN results](reference/03-causal-tcn-training-and-streaming-results.md)
- [Practical memory and rules handoff](reference/04-observation-memory-and-practical-rule-handoff.md)
- [Full vault report source](various/vault-report.md)

The 4321-word textbook-style vault report and four figures were committed and pushed to go-go-parc in `da20dfa`: `Projects/2026/09/06/ARTICLE - Temporal Video Models - Causality Weak Supervision and Observation Memory.md`. The inline architecture diagram and four result figures preserve the implementation/evidence trail.

The delivered intern guide below records the initial broader design; the final scope above supersedes its proposed general memory features.

## Guide delivery

Uploaded to `/ai/2026/09/06/VIDEO-TEMPORAL-001/VIDEO-TEMPORAL-001_Intern_Guide.pdf`.

- [PDF review and hashes](various/pdf-validation.json)
- [Upload receipt](various/remarkable-upload.json)


## Active native FP32 follow-up

Reopened at the user's request to measure repaired native-video features before drawing conclusions from the pooled TEMPORAL results. The completed initial scope above remains historical. See [comparison design](design-doc/02-fp32-native-temporal-feature-comparison-design.md) and [follow-up diary](reference/05-fp32-native-follow-up-diary.md).

Native follow-up computation is complete: 792 FP32 windows extracted in 199 seconds; ridge macro recall 24.55% and TCN seed mean 24.31%. See [measured findings](reference/06-native-fp32-temporal-benchmark-measured-findings.md) and [follow-up diary](reference/05-fp32-native-follow-up-diary.md). The remaining open item is physical printing, pending explicit external-destination approval; the local slip layouts are saved.
