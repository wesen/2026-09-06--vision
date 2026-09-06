---
Title: Portable upstream review package
Ticket: MLX-VIDEO-FIX-001
Status: complete
Topics: [video, embeddings, cosmos]
DocType: reference
Intent: long-term
Owners: []
RelatedFiles: []
ExternalSources: []
Summary: Three portable patches for personal fork review, with no public submission.
LastUpdated: 2026-09-06T16:45:00-04:00
WhatFor: Replay and review the focused wrapper repair
WhenToUse: Before a separately authorized upstream contribution
---

# Local review package — no PR or issue created

Fork branch: https://github.com/wesen/mlx-vlm/tree/fix/qwen3-vl-video-embeddings

Base: `d5064772dcd1e31704604f93a873323505ae70d5`
Head: `6452614f6de04694d1e34fd13abaca11f6ffb994`

The three mail patches preserve the focused milestones: failing forwarding regressions, video forwarding, request-local positions/pooling validation. Apply in order with `git am *.patch` in an isolated checkout of the base. The resulting source tree should match the fork head even if replayed commit IDs differ.

Only these files change:

- `mlx_vlm/models/qwen3_vl_embedding/qwen3_vl_embedding.py`
- `mlx_vlm/tests/test_qwen3_vl_embedding_video.py`

The tests use sentinels and tiny synthetic models; they do not require household corpus files or downloaded checkpoints. Run `python -m pytest mlx_vlm/tests/test_qwen3_vl_embedding_video.py -q` on a Mac with MLX GPU access.

Review notes: a native video call previously discarded `pixel_values_videos` before the backbone; a second defect reused cached positions across independent embedding calls. The patch forwards video pixels without relabeling them as images, requires matching pixel/grid pairs, uses current backbone positions, and validates pooling masks. Existing positional argument order, causal/padding masks and deepstack visual features are preserved.

Real-model evidence belongs to the surrounding ticket, not the upstream patch: eight official-weight FP32 cases pass strict parity; independent preprocessing and quantization differences are documented separately. The application integration is also excluded from the fork changes.

The user requested pushing to their fork for personal review only. No external issue, PR, comment or review request was sent.
