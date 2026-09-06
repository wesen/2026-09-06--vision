# Tasks

## Design and delivery

- [x] Establish project scope, dependencies, and VirtualHome data policy.
- [x] Write detailed intern analysis/design/implementation guide.
- [x] Validate technical contracts and rendered PDF.
- [x] Upload this ticket guide to reMarkable and record receipt.

## E1 Environment and provenance

- [ ] Create isolated workbench environment and record Python/runtime/hardware versions.
- [ ] Resolve model and conversion to immutable revisions; record weight and processor hashes.
- [ ] Inspect installed embedding entry points and document actual signatures.

## E2 Contracts and sampling

- [ ] Implement FeatureSpace, SampledClip, and vector-validation contracts.
- [ ] Implement deterministic PTS sampling with irregular/duplicate/truncated fixtures.
- [ ] Verify cache identity changes for every preprocessing or model-space change.

## E3 Adapter and smoke

- [ ] Implement text, image, and native-video methods without silent fallback.
- [ ] Implement separately named frame-pooled mode and space identity.
- [ ] Audit prepared frame count and original/reversed/repeated-frame controls.
- [ ] Record capability failures, finite dimensions, normalization, and repeatability.

## E4 Measurement and handoff

- [ ] Benchmark cold and repeated warm runs with materialization and bounded frame counts.
- [ ] Record preprocessing/inference/total time, memory, and real-time factor.
- [ ] Publish selected defaults, capability matrix, cache fixture, and reproduction command.
