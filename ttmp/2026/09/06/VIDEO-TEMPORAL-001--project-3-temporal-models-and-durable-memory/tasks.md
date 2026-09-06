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

- [ ] Implement append-only facts, supersession/retraction, and SQLite migration.
- [ ] Implement as-of state queries with conflict, coverage, and expiry rules.
- [ ] Test late facts, duplicate ingestion, restart, and no future leakage.
- [ ] Publish separate offline/causal metrics and rule-engine handoff.
