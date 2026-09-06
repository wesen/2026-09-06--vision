# Tasks

## Design and delivery

- [x] Inspect existing source/time/cache/verifier contracts and current primary API references.
- [x] Write the detailed intern guide, architecture diagram, and investigation diary.
- [x] Validate ticket metadata and render/review the complete PDF.
- [x] Dry-run and upload the reviewed guide to reMarkable; retain delivery receipt.

## D1 Contracts and detector baseline

- [x] Create perception contracts, coordinate validation, and immutable artifact store.
- [x] Create an isolated dependency lock; pin checkpoint, class map, and artifact hashes.
- [x] Implement detector adapter over registered source PTS with explicit RGB and box conventions.
- [x] Measure CPU/MPS smoke behavior, class coverage, misses, and small-object performance.
- [x] Build source-aligned overlays and a reviewed detection pilot.

## D2 Tracking and crops

- [x] Implement stored-detection replay and a pinned ByteTrack adapter with explicit cadence.
- [x] Test episode/shot resets, gaps, ID switches, predicted versus observed locations, and prefix replay.
- [x] Implement contextual target/person crops and invertible transforms.
- [x] Add crop-specific evidence/cache identities and source-hash validation.
- [ ] Review contiguous identity-labeled spans and save failure/success screenshots.

## D3 Proposals and evidence packets

- [x] Implement uniform full-scene scheduling and logged proposal budgets.
- [x] Add measured proximity/movement/change cues with approach-only controls.
- [x] Export bounded verifier packets with citation, source, and availability checks.
- [ ] Measure coverage versus calls/pixels and complete short-action misses.
- [x] Verify causal future-perturbation behavior separately from offline selection.

## D4 Recognition and replay

- [ ] Integrate read-only perception overlays with registered video playback.
- [ ] Freeze F/C/FC/FCH/FCW/H evidence ablations and grouped train/development/test policy.
- [ ] Run fixed-interval representation comparisons separately from proposal-selection comparisons.
- [ ] Publish per-group detection/tracking/recognition metrics, raw counts, timings, and failure gallery.
- [ ] Write final implementation report and identify evidence-based mask/pose/Core ML/fine-tuning follow-ups.
