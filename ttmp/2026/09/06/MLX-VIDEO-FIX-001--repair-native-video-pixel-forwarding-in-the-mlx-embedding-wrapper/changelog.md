# Changelog

## 2026-09-06

- Initial workspace created


## 2026-09-06

Created dedicated native-video wrapper repair ticket, source snapshots, intern guide, and P0-P5 implementation tasks. Source diagnosis is established; native-video reproduction and repair remain open.


## 2026-09-06

Completed 12-page PDF layout review, archived page previews, and uploaded intern repair guide to /ai/2026/09/06/MLX-VIDEO-FIX-001 with a positive receipt. Repair implementation remains open.


## 2026-09-06 — P3 acceptance

Fresh P0–P2 regression run passed 15 tests. Eight controlled FP32 parity gates passed with explicit processor contract and tolerances. Recorded independent preprocessing interventions, quantization/ranking limits, timings, memory and source hashes. P4 will use official FP32 only; quantized native rollout is not accepted.

## 2026-09-06 — P4 integration

Added explicit native_video CLI mode, official FP32 artifact/processor/runtime checks, source-aware feature identity and separate clip cache. Nine development clips encoded and fully reused; reference parity and 16 focused tests passed in both environments. Baseline remains explicitly selectable and its environment is unchanged.

## 2026-09-06 — P5 review and vault delivery

Pushed fork head 6452614 without a PR/issue. Replayed portable patches to an identical source tree; 34 tests and four subtests passed. Added root-cause report and consumer handoffs. Rebased go-go-parc, added validated 6,805-word textbook article and nine assets, and pushed vault commit 02925f6. All requested phases complete for official FP32 native mode.

## 2026-09-06

Completed P0-P5 for official FP32 native video; fork pushed without PR, validated textbook report rebased and pushed to go-go-parc at 02925f6.
