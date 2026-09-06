---
Title: Requested object localization and crop evidence coverage
Ticket: VIDEO-LOCALIZATION-001
Status: active
Topics:
    - video
    - embeddings
DocType: index
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/perception/contracts.py
      Note: Source box geometry and crop transforms
    - Path: repo://workbench/src/video_workbench/predicates/classify.py
      Note: Fixed state scoring methods
    - Path: repo://workbench/src/video_workbench/predicates/regions.py
      Note: Existing unique requested-class binding and missing crops
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T17:01:56.173719-04:00
WhatFor: ""
WhenToUse: ""
---


# Requested object localization and crop evidence coverage

## Overview

<!-- Provide a brief overview of the ticket, its goals, and current status -->

## Key Links

- **Related Files**: See frontmatter RelatedFiles field
- **External Sources**: See frontmatter ExternalSources field

## Status

Current status: **active**

## Topics

- video
- embeddings

## Tasks

See [tasks.md](./tasks.md) for the current task list.

## Changelog

See [changelog.md](./changelog.md) for recent changes and decisions.

## Structure

- design/ - Architecture and design documents
- reference/ - Prompt packs, API contracts, context summaries
- playbooks/ - Command sequences and test procedures
- scripts/ - Temporary code and tooling
- various/ - Working notes and research
- archive/ - Deprecated or reference-only artifacts

## Scope and dependencies

Part of the active three-ticket goal with VIDEO-ACTIONS-001, VIDEO-LOCALIZATION-001, and VIDEO-TEMPORAL-001. Existing search, state, perception, corpus, and MLX repair results are preserved as inputs.

- [Intern guide](design-doc/01-intern-analysis-design-and-implementation-guide.md)
- [Implementation diary](reference/01-implementation-diary.md)
- [Phased tasks](tasks.md)

## Guide delivery

Uploaded the reviewed eight-page guide to `/ai/2026/09/06/VIDEO-LOCALIZATION-001/VIDEO-LOCALIZATION-001_Intern_Guide.pdf`. See [PDF review](various/pdf-validation.json) and [upload receipt](various/remarkable-upload.json). Implementation phases remain open.
