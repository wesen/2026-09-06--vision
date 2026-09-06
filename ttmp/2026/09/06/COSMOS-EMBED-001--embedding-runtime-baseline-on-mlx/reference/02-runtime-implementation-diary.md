---
Title: Runtime implementation diary
Ticket: COSMOS-EMBED-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/embedding.py
      Note: Verified pooled-image adapter and feature identity, commit 358db7e
    - Path: repo://workbench/uv.lock
      Note: Exact runtime dependency versions
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T13:43:39.015949-04:00
WhatFor: ""
WhenToUse: ""
---


# Runtime implementation diary

## Step 1: Verify the real pooled-image baseline

Installed an isolated, locked MLX environment and loaded a pinned 4-bit Qwen3-VL-Embedding checkpoint. The published MLX embedding class drops native video pixels, so this implementation explicitly exposes pooled images and rejects native video. This is a capability-limited baseline, not a native-video result.

### Prompt Context
**User prompt (verbatim):** (see VIDEO-SEARCH-001 implementation diary Step 1)

**Assistant interpretation:** Supply a verified visual embedding prerequisite for timestamped search.

**Inferred user intent:** Ensure search features depend on actual pixels and are reproducible.

### What I did
- Added workbench package, uv lock, artifact hashing, explicit feature-space identity, last-token encoder, normalized image pooling, and a measured smoke script.
- Checked official Qwen preprocessing and local MLX source. Reset cached position IDs for independent samples.

### Why
- The checkpoint config names the generative model class; loading requires an explicit in-memory `qwen3_vl_embedding` override. Model artifacts remain unmodified.

### What worked
- `workbench/.venv/bin/pytest workbench/tests -q`: 2 passed.
- Actual GPU smoke: 2048 dimensions, norm 1, exact repeated frame, black-image cosine 0.366 versus adjacent-frame cosine 0.963.
- MLX peak 2,151,787,081 bytes; warm image calls 0.19–0.23 seconds. Full evidence in `various/runtime-smoke.json`.

### What didn't work
- First smoke: `ImportError: apply_chat_template requires jinja2 to be installed. Please install it using pip install jinja2`. Added explicit Jinja2 dependency.
- Native video is unsupported: `_last_hidden_state` never forwards `pixel_values_videos` from `__call__`. No native-video performance claim is made.
- GitHub raw reference URL returned HTTP 404; fetched the official script from the Hugging Face model repository instead.

### What I learned
- A callable accepting video kwargs does not establish visual-video support.
- The community model card has conflicting lineage metadata; preserve the exact artifact hashes rather than claiming independently verified conversion provenance.

### What was tricky to build
- Generic loader remapping does not map qwen3_vl to its embedding class. `config_overrides` selects the actual encoder without editing downloaded files.

### What warrants a second pair of eyes
- Prompt template, last-token pooling, and future native video forwarding require separate numerical validation.

### What should be done in the future
- Complete remaining embedding benchmark breadth separately; this smoke unlocks the explicitly named pooled-image search baseline.

### Code review instructions
- Read `workbench/src/video_workbench/embedding.py`; rerun `scripts/02-runtime-smoke.py` with the workbench Python and local model.

### Technical details
- Checkpoint revision: `99b57b385f543a94c46d9f8e85a354de4c836b37`.
- Official reference: https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B/raw/main/scripts/qwen3_vl_embedding.py
- Packages and every model/config hash are recorded in the lock and smoke JSON.
