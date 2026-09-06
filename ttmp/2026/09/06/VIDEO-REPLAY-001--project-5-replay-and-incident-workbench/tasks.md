# Tasks

## Design and delivery

- [x] Establish project scope, dependencies, and VirtualHome data policy.
- [x] Write detailed intern analysis/design/implementation guide.
- [ ] Validate technical contracts and rendered PDF.
- [ ] Upload this ticket guide to reMarkable and record receipt.

## W1 Clock and broker

- [ ] Implement monotonic replay/source time mapping and packet horizon.
- [ ] Test delayed/future frames and precomputed-feature availability.

## W2 Scheduler

- [ ] Implement bounded queues, mandatory/optional priorities, and deadlines.
- [ ] Emit explicit gaps for dropped/deferred work and measure queue delay.
- [ ] Prove bounded behavior with a deliberately slower-than-source worker.

## W3 Lifecycle and recovery

- [ ] Define stable incident identity, workflow state, and immutable decision revisions.
- [ ] Implement transactional result/outbox and idempotent publication.
- [ ] Test duplicate events and crash recovery around commits and cursor updates.

## W4 Viewer

- [ ] Implement bounded registered-ID API and reuse search/video contracts.
- [ ] Build video/state/event/incident timeline and revision evidence panel.
- [ ] Verify as-of history, seeking, and absence of client-side rule evaluation.

## W5 Evaluation

- [ ] Freeze staged real-video collection/review protocol and held-out set.
- [ ] Run declared sustained replay and separate looped capacity stress test.
- [ ] Report false alerts/hour, misses, unknowns, latency, queues, coverage, and memory.
- [ ] Publish real-video transfer failures and measured next-step capacity decision.
