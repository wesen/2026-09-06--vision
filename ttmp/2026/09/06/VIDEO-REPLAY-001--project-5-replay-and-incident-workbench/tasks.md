# Tasks

## Design and delivery

- [x] Establish project scope, dependencies, and VirtualHome data policy.
- [x] Write detailed intern analysis/design/implementation guide.
- [x] Validate technical contracts and rendered PDF.
- [x] Upload this ticket guide to reMarkable and record receipt.
- [x] Supersede the broad original implementation scope with the bounded replay contract and explicit deferred tasks.

## P3 Clock, broker, scheduler, and persistence

- [x] Implement monotonic source/run mapping, cycles, and dependency availability enforcement.
- [x] Broker only released bounded evidence; never pass complete source-video paths to workers.
- [x] Bound admitted jobs and input bytes including running work; implement mandatory priority and optional eviction.
- [x] Enforce queue-inclusive deadlines, isolated worker timeout/reaping, cancellation, and bounded output loading.
- [x] Emit durable explicit gaps and reset departure prefix state across missing frame coverage.
- [x] Persist immutable case/condition records with stable identity and bounded as-of cursor queries.
- [x] Smoke-test causal clocks, future dependencies, queue policy, worker failure, and persistence at feature completion.

## P4 Integration, viewer, and measurement

- [x] Integrate recorded YOLO traces, exact-time stored states, rule candidates, and recorded or live accepted verifier execution.
- [x] Implement the loopback registered-ID run/evidence/video API and one-active-run policy.
- [x] Build source/state/event/rule/gap timeline with separate evidence conditions and explicit as-of seeking.
- [x] Inspect the browser and retain screenshots of a missed fridge violation, detected microwave violation, and overload gaps.
- [x] Complete a normal actual-evidence run and one fresh accepted-verifier run.
- [x] Run a separate repeated accelerated slow-worker capacity experiment; report latency, queue/byte bounds, drops, coverage, and memory.
- [x] Publish measured report, reproduction commands, diary, and final phase slips.

## Deferred follow-ups (outside current bounded replay delivery)

- [ ] LATER: General revision/supersession, reconciliation, and incident workflow lifecycle, only with a concrete consumer requirement.
- [ ] LATER: Transactional publication/outbox and automatic crash recovery of queued/in-flight work.
- [ ] LATER: Fresh live perception/native-embedding adapter and measured multi-worker scheduling.
- [ ] LATER: Freeze staged real-video collection/review protocol and evaluate real-video transfer separately.
- [ ] LATER: Live camera capture and operational false-alert/coverage acceptance.
