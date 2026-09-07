# Tasks

## Design and delivery

- [x] Establish project scope, dependencies, and VirtualHome data policy.
- [x] Write detailed intern analysis/design/implementation guide.
- [x] Validate technical contracts and rendered PDF.
- [x] Upload this ticket guide to reMarkable and record receipt.

## R1 Flat templates and oracle logic

- [x] Define three flat rule templates, explicit entity bindings, units, and bounded schema validation.
- [x] Implement PASS/VIOLATION/UNKNOWN, missing-trigger applicability, and exact operator semantics.
- [x] Add hand-derived threshold/equality/overlap/wrong-entity oracle tests.

## R2 Coverage and store

- [x] Implement explicit event-coverage union/gap checks and uncertain event bounds.
- [x] Integrate exact-sample as-of observation views without supersession.
- [x] Smoke-test late observations, restart equivalence, and explanations for unknown at the feature boundary.

## R3 Investigation

- [x] Emit at most one focused evidence request per unknown evaluation, with stable request identity.
- [x] Enforce evidence horizon and strict injected verifier answers; runtime limits remain owned by COSMOS-VERIFY.
- [x] Preserve immutable evidence/evaluations and smoke-check disagreement/unavailable-verifier behavior.

## R4 Evaluation

- [x] Freeze rule/candidate/matching policies and versioned prompts.
- [x] Compare oracle and predicted/no-verifier conditions; document the accepted-adapter gate for later Qwen/Cosmos integration.
- [ ] Include missed candidates in end-to-end recall and report unknown/cost/latency.
- [x] Keep endpoint-world-truth diagnostics separate from reviewed temporal evaluation.

## Explicit follow-ups outside initial implementation

Recursive rule composition, continuous-state inference from sparse frames, automatic multi-step investigation, incident lifecycle, and general correction/supersession are deferred. Live Qwen/Cosmos refinement comparison follows COSMOS-VERIFY runtime acceptance; its absence must remain visible in reports. Existing original-edition reMarkable receipts are retained as history.
