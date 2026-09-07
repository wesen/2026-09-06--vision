---
Title: Deferred 8B native embedding comparison
Ticket: VIDEO-TEMPORAL-001
Status: complete
Topics:
    - video
    - embeddings
    - cosmos
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/temporal/encode_native.py
      Note: Future native producer extension
    - Path: repo://workbench/src/video_workbench/temporal/native_compare.py
      Note: Preserve matched training and comparison policy
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T20:45:06.153936-04:00
WhatFor: ""
WhenToUse: ""
---


# Deferred: 8B native embedding comparison

**Scheduling: later; do not execute during COSMOS-VERIFY.** This is a separate representation experiment, not the 8B generative verifier run. Preserve the completed TEMPORAL baseline and native FP32 comparison.

The candidate is official `Qwen/Qwen3-VL-Embedding-8B`, with a default 4096-dimensional output versus the current 2B model’s 2048 dimensions. Source: https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B . Model availability does not establish support in our repaired MLX adapter.

## Proposed experiment

1. Pin the official checkpoint, processor, and repaired runtime. Inspect hard-coded model identities and dimensions before adding an explicitly separate 8B producer.
2. Run a bounded pilot on the 64 GB M1 Max, measuring actual peak memory, extraction time, pixel sensitivity, finite normalized outputs, and timestamp/frame provenance. FP32 weights alone are roughly 32 GB; runtime fit is not yet measured. If reduced precision is needed, label it a separate experimental condition.
3. Re-encode exactly the existing 792 windows across 48 episodes into a new cache and feature manifest. Never reuse 2B indices, heads, or embeddings, even if output dimensions are reduced to match.
4. Train fresh ridge and six TCN heads under unchanged training, splits, seed identifiers, and development selection policies. Keep test data out of selection.
5. Compare against native 2B FP32: macro recall, per-class failures, seed spread, extraction cost, memory, and causal smoke checks at feature completion. Investigate CLOSE, GRAB, PUTBACK, and TURNTO without claiming larger capacity guarantees improvement.

## Existing measured reference

The colleague’s commits `176a300`, `8e59d45`, and `209cea4` establish native 2B FP32 extraction and comparison. Ridge reached 24.55% test macro recall; mean TCN reached 24.31%, with greater seed variability. See [measured findings](../reference/06-native-fp32-temporal-benchmark-measured-findings.md). Precision and preprocessing changed versus pooled, so that comparison does not isolate frame ordering. An 8B comparison should hold those factors fixed where feasible.

## Entry points

- `workbench/src/video_workbench/temporal/encode_native.py`: native feature producer.
- `workbench/src/video_workbench/temporal/native_compare.py`: matched comparison and artifact audits.
- `output/temporal-native-fp32-v1/`: preserved native 2B reference artifacts.

Resume only when this deferred work is scheduled. Current active work remains the Qwen/Cosmos 8B answer-generating verifiers.
