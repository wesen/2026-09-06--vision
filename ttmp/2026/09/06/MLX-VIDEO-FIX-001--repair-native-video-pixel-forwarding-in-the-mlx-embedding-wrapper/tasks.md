# Tasks

## Documentation and delivery

- [x] Create dedicated repair ticket linked to embedding and search projects.
- [x] Archive exact source evidence and historical image smoke with hashes.
- [x] Write intern analysis, design, implementation, and validation guide.
- [x] Validate frontmatter, references, and rendered PDF layout.
- [x] Upload reviewed guide to reMarkable and record delivery receipt.

## P0 Reproduce and pin

- [x] Create isolated MLX-VLM checkout and environment; record upstream revision.
- [x] Recheck upstream issue and PR history for the exact omission.
- [x] Add failing public-call-to-helper video-pixel forwarding regression.
- [x] Add helper-to-backbone forwarding regression with sentinel tensors.
- [x] Freeze same-metadata, different-pixels fixture using development media.
- [x] Run unpatched native-video request and record exact exception or output.
- [x] Instrument video vision-tower calls and capture tensor/grid identities.

## P1 Forward pixels

- [x] Add explicit pixel_values_videos to both embedding wrapper signatures.
- [x] Forward video pixels and video grids separately from image inputs.
- [x] Verify mixed image/video routing and preserve deep visual features.
- [x] Add explicit invalid pixel/grid pairing tests at the appropriate boundary.
- [x] Run existing text/image regression suite against the minimal patch.

## P2 Positions and request isolation

- [x] Test video-to-text, text-to-video, and image-to-video request sequences.
- [x] Compare repeated inputs against fresh model instances.
- [x] Establish request-local positional computation if cached state leaks.
- [x] Test left/right padding, all-padding rejection, and last-token pooling.
- [x] Verify supported batching or document and test explicit rejection.

## P3 Real-model validation

- [ ] Run identical-token/grid pixel interventions and end-to-end processor tests.
- [ ] Test single-frame, odd-frame, and asymmetric reversed-frame inputs.
- [ ] Build a controlled unquantized conversion from the official checkpoint.
- [ ] Compare preprocessing, visual features, positions, pooling, and vectors.
- [ ] Freeze precision-specific parity tolerances with an explicit rationale.
- [ ] Evaluate the 4-bit model separately for numerical and ranking differences.
- [ ] Measure materialized cold/warm latency, MLX peak memory, and RSS.
- [ ] Publish JSON evidence and fixture/contact-sheet or comparison screenshots.

## P4 Workbench integration

- [ ] Pin repaired dependency or a reviewable isolated patch.
- [ ] Add native-video adapter after required capability gates pass.
- [ ] Define new feature-space identity including runtime and temporal policy.
- [ ] Test old pooled-image cache rejection and failed-inference publication.
- [ ] Re-encode a development subset and document explicit rollback selection.

## P5 Handoff

- [ ] Write root-cause report with reproduction, patch, evidence, and limits.
- [ ] Prepare minimal upstream issue/PR package for separate submission.
- [ ] Relate implementation files and commits; update embedding/search handoff.
- [ ] Close only when native-video correctness and integration gates pass.
