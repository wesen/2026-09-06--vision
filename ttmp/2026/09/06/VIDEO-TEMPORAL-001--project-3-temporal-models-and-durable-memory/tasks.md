# Tasks

## Design and delivery

- [x] Establish project scope, dependencies, and VirtualHome data policy.
- [x] Write detailed intern analysis/design/implementation guide.
- [x] Validate technical contracts and rendered PDF.
- [x] Upload this ticket guide to reMarkable and record receipt.

## T1 Data and baseline

- [x] Implement timestamped feature sequences, validity, and weak-label masks.
- [x] Create oracle omission/repetition/gap fixtures and linear baseline.
- [x] Verify feature-index to source-time mapping.

## T2 Classical models

- [x] Adapt reviewed HMM/filter/smoother and HSMM contracts.
- [x] Implement timestamp-based hysteresis and tiny exhaustive decoder tests.
- [x] Compare constrained and unconstrained paths; verify errors are preserved.

## T3 Causal TCN

- [x] Implement small frozen-feature TCN and training/checkpoint metadata.
- [x] Test future perturbation, chunk equivalence, masking, and feature availability.
- [x] Compare seed runs and development-selected settings against linear baseline.

## T4 Memory

- [x] Implement append-only sampled observations and initial SQLite schema.
- [x] Implement exact-sample as-of queries, source-unknown handling, and stream isolation.
- [x] Test late facts, duplicate ingestion, restart, and no future leakage.
- [x] Publish separate offline/causal metrics and rule-engine handoff.

### Final scope decision

The user requested wrap-up after questioning speculative memory machinery. Closure covers the implemented observation store, exact-sample as-of queries, actual producer replay, and rule handoff. General supersession, retraction, expiry, uncertainty-interval reconciliation, and continuous-state inference are explicitly deferred until a concrete consumer requires them; they are not completed implementation claims. The original intern guide remains an immutable record of the initial design and delivery.

The measured comparisons and observation memory are complete. See `reference/04-observation-memory-and-practical-rule-handoff.md`, the final vault report in `various/vault-report.md`, and diary Step 10 for the closure decision and publication receipt.


## Native FP32 follow-up

- [x] N1: Implement native dense producer and validate an eight-window pixel-sensitive pilot with accepted runtime provenance.
- [x] N2: Extract and source-audit all 792 matched native FP32 windows without changing pooled artifacts.
- [x] N3: Train fresh ridge and TCN heads under the existing development-selection policy; save matched per-class/paired comparisons.
- [x] N4: Publish measured native-versus-pooled findings, figure, diary, commits, and local phase-slip layouts; record the printing blocker.
- [x] Print saved native follow-up slips after explicit Almanach approval; all five printer responses successful, archived in various/native-print-receipts.json.
