# Tasks

## Design and delivery

- [x] Establish project scope, dependencies, and VirtualHome data policy.
- [x] Write detailed intern analysis/design/implementation guide.
- [x] Validate technical contracts and rendered PDF.
- [x] Upload this ticket guide to reMarkable and record receipt.

## S1 Registry

- [x] Implement generic manifest ingest and SQLite episode migration.
- [x] Verify source hashes, group splits, duplicate IDs, and PTS metadata.
- [x] Add inspect command and corrupt/missing/variable-rate fixtures.

## S2 Cache and index

- [ ] Implement deterministic windows and selected-PTS metadata.
- [ ] Implement atomic array publication and resumable index manifests.
- [ ] Test crash recovery and rejection of incompatible spaces.

## S3 Search and viewer

- [ ] Implement exact cosine ranking, stable ties, and split filtering.
- [ ] Implement typed search API and registered-ID-only video access.
- [ ] Build minimal query/results/player UI and verify interval seeking.

## S4 Evaluation

- [ ] Freeze queries, weak-interior relevance, and split policy.
- [ ] Run bounded development window/FPS sweep and freeze selected configuration.
- [ ] Run final test partition with Success@K, interval Recall@K, and resource metrics.
- [ ] Publish reproducible index/evaluation report and shared decoder/cache handoff.
