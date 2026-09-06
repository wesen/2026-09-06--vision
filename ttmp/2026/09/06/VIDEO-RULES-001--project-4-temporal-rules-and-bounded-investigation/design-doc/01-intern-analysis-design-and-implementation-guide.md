---
Title: Intern analysis design and implementation guide
Ticket: VIDEO-RULES-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://configs/virtualhome-household-v1.json
      Note: Existing implementation evidence for this design
    - Path: repo://docs/playbook/virtualhome-corpus.md
      Note: Existing implementation evidence for this design
    - Path: repo://src/virtualhome_corpus/core.py
      Note: Existing implementation evidence for this design
    - Path: repo://src/virtualhome_corpus/runner.py
      Note: Existing implementation evidence for this design
ExternalSources: []
Summary: Evaluate typed three-valued rules and audit bounded evidence refinement.
LastUpdated: 2026-09-06T13:13:51.855592-04:00
WhatFor: ""
WhenToUse: ""
---


# Project 4 - Temporal rules and bounded investigation

## What a rule engine adds

A search hit says that an interval resembles a query. A state observation says that a property appears true or false at a time. A temporal rule combines facts into a precisely defined procedural conclusion. This project builds that deterministic layer and a bounded investigator that can request additional visual evidence when a conclusion is uncertain.

The deliverable is a typed JSON rule representation, an oracle-tested evaluator, a bounded evidence planner, and a no-verifier/Qwen/Cosmos comparison using the runtime adapter from COSMOS-VERIFY-001. Natural-language rule compilation is deferred until the typed rules behave correctly. No Python `eval`, arbitrary generated code, or unrestricted recursive agent loop is needed.

Start with household rules: the target is closed at an observed departure, it remains closed throughout a declared interval, and no reopening occurs inside a fully covered interval after closure. These are distinct claims. The current corpus's `close_target_before_departure` manifest field establishes endpoint world truth and explicitly does not certify exact departure timing. Do not reuse that field as gold for every stronger temporal rule.

## Current evidence and dependencies

VIDEO-TEMPORAL-001 supplies an as-of fact store and immutable revisions. VIDEO-STATE-001 supplies observations with unknown handling. COSMOS-VERIFY-001 supplies the evidence-bounded verifier. The evaluator can be implemented before those systems using hand-authored oracle facts. Current VirtualHome endpoint labels are useful for a narrowly named endpoint diagnostic; VIDEO-CORPUS-001 is needed for reviewed temporal/visibility labels.

Existing `core.py:167` checks actual final graph state and actor destination. It returns PASS for normal closure and VIOLATION for the two open-ended variants, with `scope: episode_endpoint_world_truth`. This is a concrete example of narrow semantics. The new rule engine must retain that precision rather than expanding a convenient label into a claim it never measured.

## Three-valued logic and knowledge limits

Use PASS, VIOLATION, and UNKNOWN for rule decisions. For factual predicates use true, false, and unknown. Unknown means insufficient or conflicting evidence. It is not equivalent to false, and logical negation preserves unknown. A conjunction is false if any operand is false, true if all are true, and otherwise unknown. A disjunction is true if any operand is true, false if all are false, and otherwise unknown.

Absence requires coverage. If no reopening was detected between seconds 8 and 12 but the camera was unavailable between 9 and 11, the system cannot conclude that reopening did not occur. Coverage is an explicit evidence object, not a byproduct of returning an empty SQL result. Distinguish a closed interval with no event from an interval that has not finished arriving yet.

## Typed AST and entity bindings

An abstract syntax tree (AST) is a data structure representing a rule, with each node having a known operator and typed arguments. Validation prevents meaningless combinations, unbounded intervals, and missing entity bindings before evaluation.

```json
{
  "schema_version": 1,
  "rule_id": "target-closed-at-departure-v1",
  "op": "state_at_event",
  "event": "departure",
  "entity_role": "target",
  "property": "door_open",
  "expected": false,
  "missing_event_policy": "unknown"
}
```

The JSON above is a proposed rule instance, not the existing corpus manifest schema. Bind `target` and `departure` to episode-specific entities/events through a separate registry. A rule about the microwave must never satisfy its prerequisite with a fridge event merely because both have property `door_open`.

The first AST should support `state_at_event`, `before`, `continuously_for`, `no_event_in`, `all`, `any`, and `not`, with explicit bounded intervals. Keep count thresholds and natural-language compilation out until these operators have oracle tests. Validate maximum depth, allowed operators, duration units, and finite bounds; reject extra fields instead of guessing their meaning.

## Architecture and trust boundaries

```text
validated rule + entity bindings + as-of horizon
                         |
                   deterministic evaluator
                         |
              PASS / VIOLATION / UNKNOWN
                         |
               optional evidence planner
                         |
      retrieval / resampling / focused verifier
                         |
               validated fact proposal
                         |
             append revision -> reevaluate
```

The evaluator is a pure function of a rule, a fact-view snapshot, and a policy version. It must not load a model or inspect the filesystem. The investigator owns the budget and evidence requests. The fact store owns reconciliation and audit history. The verifier proposes observations; it cannot overwrite the rule or declare its own answer authoritative.

Proposed modules are `rules/ast.py`, `rules/validate.py`, `rules/evaluate.py`, `rules/coverage.py`, `investigation/planner.py`, and `investigation/budget.py` under the workbench package. Keep rule fixtures in `workbench/tests/fixtures/rules/` and rule configuration under `workbench/configs/rules/`.

## Time uncertainty and exact operator semantics

Represent an uncertain event time by lower and upper bounds. If event A occurs in `[a_lo,a_hi]` and B in `[b_lo,b_hi]`, the possible elapsed duration lies in `[b_lo-a_hi, b_hi-a_lo]`. For a minimum duration d, PASS when the minimum possible duration is at least d, VIOLATION when the maximum possible duration is below d, otherwise UNKNOWN, subject to sufficient evidence and entity consistency.

```python
# Pseudocode for a minimum-duration predicate.
def elapsed_at_least(a, b, required_us):
    if not usable(a) or not usable(b):
        return UNKNOWN
    minimum = b.lo_us - a.hi_us
    maximum = b.hi_us - a.lo_us
    if minimum >= required_us:
        return PASS
    if maximum < required_us:
        return VIOLATION
    return UNKNOWN
```

For example, closure at `[5.0,5.4]` seconds and departure at `[7.1,7.5]` imply a duration between 1.7 and 2.5 seconds. A two-second requirement is UNKNOWN. Subtracting the midpoints and declaring 2.1 seconds a pass would hide the measurement uncertainty.

Define `before` as strict ordering: PASS when `a_hi < b_lo`, VIOLATION when `a_lo >= b_hi`, and UNKNOWN otherwise, assuming both events are observed and usable. Define what happens with missing events explicitly; the default is unknown unless a completed, adequately covered scope establishes required-event absence. Do not make a universal rule vacuously pass because its trigger was not observed; return an applicability field such as `not_observed` alongside UNKNOWN under the initial policy.

`continuously_for` requires supported state over the entire target interval, not just its endpoints. `no_event_in` can return PASS only when the interval is closed under the as-of horizon and event-detection coverage meets the declared policy. If a verified prohibited event exists, it can return VIOLATION despite unrelated gaps. If no event exists but coverage is incomplete, return UNKNOWN.

## Decision and evidence records

A decision record should include stable rule/episode/entity identity, decision revision, status, applicability, evaluated event scope, as-of time, supporting and contradicting fact IDs, coverage IDs, uncertainty reason, evaluator version, and investigation cost. Preserve the initial decision and every later revision. A verifier disagreement should be visible in the evidence history, not silently replace an earlier observation.

```python
# Proposed application API.
def evaluate(rule, bindings, fact_view, as_of_us) -> Decision: ...
def plan_refinement(decision, evidence_catalog, budget) -> Request: ...
def append_proposal(result, provenance) -> FactRevision: ...
```

A decision's stable incident identity must not depend on its current PASS/VIOLATION status; otherwise an update creates a second incident. Project 5 owns user-facing lifecycle transitions but consumes this stable identity and revision lineage.

### Decision: oracle evaluator before model integration

- **Context:** A wrong rule and a wrong observation can accidentally cancel each other.
- **Options considered:** End-to-end VLM prompting first or a deterministic oracle fixture suite first.
- **Decision:** Implement and test the evaluator using hand-authored facts before predicted evidence.
- **Rationale:** It isolates logical correctness from perception quality.
- **Consequences:** Early demos use synthetic facts; final evaluation must separately report oracle and predicted inputs.
- **Status:** proposed.

## Bounded investigation and stopping

The first planner chooses among retrieving a relevant window, resampling within an approved interval, or asking one focused verifier question. Its budget includes at most three external/model calls per candidate initially, a total deadline, maximum frames, maximum output tokens, and an allowed evidence horizon. These are proposed engineering defaults to tune on development data, not guaranteed optimal settings.

```python
# Pseudocode: every iteration consumes a finite budget.
while decision.needs_refinement and budget.remaining_calls > 0:
    request = planner.choose(decision, catalog, budget)
    if request is None or request.fingerprint in attempted:
        break
    assert request.latest_source_us <= policy.evidence_cutoff_us
    budget.reserve(request)
    result = executor.run(request, deadline=budget.deadline)
    attempted.add(request.fingerprint)
    if result.valid:
        facts.append_revision(result.proposal)
    decision = evaluate(rule, bindings, facts, clock.now_us())
return decision.with_budget_usage(budget)
```

The evidence cutoff freezes which source frames may be inspected. Result availability advances when computation completes; reevaluation uses that later as-of time while preserving the original evidence cutoff. A newly produced proposal must not be backdated into an earlier fact view. For live or availability-faithful replay, the investigator cannot ask for future frames. A bounded lookahead mode is allowed only as a separately named offline/delayed policy; its added delay must be included in latency. Repeated questions on identical evidence are not independent corroboration. Stop when the budget expires, no new evidence can be acquired, or the decision becomes sufficiently supported under policy. Unknown is a valid terminal result.

## Implementation phases and acceptance gates

### R1 - AST and pure logic

Define schemas, units, entity bindings, three-valued truth tables, and operator semantics. Add tests for missing triggers, wrong entities, exact threshold equality, overlapping uncertainty intervals, and invalid AST depth. Exit when every fixture has a hand-derived expected result and no evaluator call touches models or mutable global state.

### R2 - Coverage and fact-store integration

Implement coverage unions, gap detection, uncertain-boundary handling, and as-of fact queries. Use the temporal-store API rather than reading the latest database row directly. Test late revisions and queries before/after their availability. Exit with oracle rules producing the same conclusions after restart and a trace explaining every unknown.

### R3 - Bounded investigator

Implement budget reservation, request fingerprints, allowed-horizon enforcement, strict verifier proposal validation, and append-only revisions. Test repeated requests, timeouts, invented evidence IDs, contradictory proposals, and exhausted budgets. Exit when no path exceeds its budget or accesses future evidence.

### R4 - End-to-end comparison

Freeze candidates, rules, prompts, budgets, and matching policy. Compare oracle facts, predicted facts without a verifier, Qwen refinement, and Cosmos refinement. Include upstream missed candidates in full-system recall; conditional verifier accuracy alone is not system recall. Report violation precision/recall, unknown rate, false certainty, calls, and added latency. Use endpoint corpus labels only in the endpoint-world-truth diagnostic and reviewed temporal labels for stronger claims.

## Review exercise

Trace a reopened-before-leaving episode. A CLOSE event exists, but a later OPEN event contradicts the claim that the target remained closed until departure. Verify that `before(close, departure)` can pass while `continuously_for(closed, close_to_departure)` fails or remains unknown depending on evidence coverage. The rule names and traces should make this difference obvious to a new intern and to a user inspecting an incident.

## Shared system contract and reading map

This guide is a design for future implementation. Existing evidence is the root `src/virtualhome_corpus/` package and the validated assets under `output/virtualhome-corpus/home-v1`. Proposed application modules live under `workbench/src/video_workbench/`, preserving the umbrella guide's layout. Proposed APIs and pseudocode are not installed commands or claims of completed model behavior.

Use integer microseconds, half-open event intervals, opaque episode IDs, and source/producer hashes. Keep event time distinct from evidence/result availability and durable commitment. Keep model-safe inputs separate from evaluator labels. A model-space hash must identify preprocessing as well as weights. Unknown evidence remains unknown until a declared policy and new evidence justify a revision.

The existing corpus is a within-scene starter set, with weak action interiors and endpoint world truth. Exact temporal and dense visual-state metrics require reviewed labels; larger datasets do not remove that requirement. Model/runtime references were checked on 2026-09-06. Pin actual installed versions during implementation rather than assuming a mutable documentation page matches the environment.

### Existing file references

- [Existing generator contracts](../../../../../../src/virtualhome_corpus/core.py): lines 55, 102, and 167: planning, weak intervals, endpoint truth.
- [Existing rendering/export lifecycle](../../../../../../src/virtualhome_corpus/runner.py): lines 54, 125, 202, and 228: annotation quality, generation, validation, indices.
- [Checked v1 experiment](../../../../../../configs/virtualhome-household-v1.json): families, variants, groups, and camera.
- [Corpus operational playbook](../../../../../../docs/playbook/virtualhome-corpus.md): generation, resume, validation, and gallery.
- [Validated corpus report](../../COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/design-doc/03-virtualhome-household-corpus-design-and-generation-report.md): observed results and label limitations.

### Ticket dependencies

- [VIDEO-TEMPORAL-001](../../VIDEO-TEMPORAL-001--project-3-temporal-models-and-durable-memory/index.md)
- [COSMOS-VERIFY-001](../../COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/index.md)
