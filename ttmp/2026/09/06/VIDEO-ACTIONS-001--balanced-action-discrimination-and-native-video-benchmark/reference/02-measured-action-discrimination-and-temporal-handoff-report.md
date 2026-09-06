---
Title: Measured action discrimination and temporal handoff report
Ticket: VIDEO-ACTIONS-001
Status: active
Topics:
    - video
    - embeddings
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/VIDEO-ACTIONS-001--balanced-action-discrimination-and-native-video-benchmark/scripts/05-review-window-details.py
      Note: Native-resolution label audit
    - Path: repo://ttmp/2026/09/06/VIDEO-ACTIONS-001--balanced-action-discrimination-and-native-video-benchmark/scripts/06-publish-comparison.py
      Note: Reproduce evidence gallery
    - Path: repo://ttmp/2026/09/06/VIDEO-ACTIONS-001--balanced-action-discrimination-and-native-video-benchmark/scripts/07-audit-handoff.py
      Note: Verify all sparse sequence evidence
    - Path: repo://ttmp/2026/09/06/VIDEO-ACTIONS-001--balanced-action-discrimination-and-native-video-benchmark/various/action-source-review-v2/labels.json
      Note: Source-reviewed action eligibility
    - Path: repo://ttmp/2026/09/06/VIDEO-ACTIONS-001--balanced-action-discrimination-and-native-video-benchmark/various/comparison-v2/results.json
      Note: Measured raw metrics and rankings
    - Path: repo://workbench/src/video_workbench/actions/evaluate.py
      Note: Frozen classification, direction and supported retrieval metrics
    - Path: repo://workbench/src/video_workbench/actions/handoff.py
      Note: Sparse timestamped feature export
ExternalSources: []
Summary: Measured three-space action benchmark, source-review coverage, failed direction discrimination, and sparse temporal handoff.
LastUpdated: 2026-09-06T17:45:02.87274-04:00
WhatFor: ""
WhenToUse: ""
---


# Measured action discrimination on paired household trajectories

The action benchmark now runs three real representations on the same reviewed source windows: accepted official FP32 native video, official FP32 image pooling, and the preserved community 4-bit pooled baseline. The principal finding is weak generic action discrimination. Native video achieves one correct prediction among seventeen eligible test windows. Its embeddings respond to changed pixels and frame order, but none of the reviewed opposite-action margins changes sign when time is reversed. This separates successful implementation from demonstrated action understanding.

The benchmark contains 48 rendered AIST/VirtualHome trajectories and 72 candidate windows. Source review accepts 62 windows and leaves ten ambiguous or unobservable. The held-out apartment has no confidently visible closing or switching examples under the frozen sampling protocol. Consequently, test accuracy and balanced accuracy describe six supported classes, not a complete nine-class evaluation. The source exclusions are part of the result.

## Experimental construction

The final simulator release uses `configs/virtualhome-paired-actions-v4.json`. Three apartments supply four action families, two camera views, and interaction or approach-only conditions. Each interaction executes a physical inverse pair. A reversed pixel sequence is a model intervention and never becomes a newly rendered physical-action label. All views and derived windows retain their original lineage partition.

The installed simulator is the AIST fork of VirtualHome. Earlier StandUp requests stalled, and some scene/program combinations failed planning. The accepted posture program uses AIST Stand and omits intervening Watch instructions. Those failures and the successful configuration are documented in diary Step 3. The completed release contains 3,880 encoded frames and passed corpus validation. There are sixteen trajectories in each split.

Each benchmark input contains four frames sampled at two frames per second from a two-second source interval. Sampling uses presentation timestamps and selects the first frame at or after each grid point. Source video hashes, frame indices, raw and normalized timestamps, interval bounds, and availability accompany each sample. No requested verb or reviewed label enters the encoder prompt.

Initial midpoint selection failed on long Sit exports because their spans include positioning and waiting. All six trajectories visibly descend near the exported end. Version two therefore centers every Sit window 750 milliseconds before that end. This rule was established through source inspection before model scores were inspected. The original windows and dense timing sheets remain in `various/action-source-review-v1`; corrected windows and final labels are in `various/action-source-review-v2`.

## Reviewed labels and coverage

A single assistant review inspected all 72 source contact-sheet rows and twenty native-resolution detail sheets. This is an auditable annotation pass, not a measurement of inter-reviewer agreement. Visible and sufficiently informative partial examples are eligible. Ambiguous and unobservable examples retain null action labels, remain in coverage denominators, and remain distractors in retrieval galleries.

| Split | Candidate windows | Eligible | Unknown | Supported classes |
|---|---:|---:|---:|---:|
| Train | 24 | 22 | 2 | 9 |
| Development | 24 | 23 | 1 | 9 |
| Test | 24 | 17 | 7 | 6 |

The unknown set includes four lamp switching windows without a clear light-state change, two edge-on television windows, one monitor-obscured book transfer, and three microwave windows whose visible evidence does not establish the requested direction. These are observation limitations. Neither graph state nor a successful simulator response resolves them into visual truth.

## Representation and intervention controls

Official native and official image pooling load the accepted FP32 artifacts in the repaired MLX environment. Image pooling encodes each frame through the official image processor and model path, normalizes each vector, averages the four vectors, and normalizes the result. Native video processes the frame sequence with official video preprocessing and monotonic timestamp slots. The 4-bit baseline uses its existing isolated environment and community checkpoint. Each representation has a distinct feature-space identity and separately encoded copies of the same nine generic query texts.

Original, reversed, and repeat-first conditions use identical source membership. Reversal reverses pixels while preserving monotonic slot timestamps; repeat-first replaces all slots with the first sampled source image. Pooled permutations should agree within floating-point tolerance. Native vectors may differ under reordering, but vector sensitivity alone does not imply correct direction discrimination.

All three runs completed real inference and returned the same immutable run identity on a second invocation. The FP32 pooled run wrote 297 cached image/query vectors, native wrote 225 video/query vectors, and 4-bit pooling wrote 297. Measured encoding-loop times were approximately 45.5, 58.1, and 46.1 seconds respectively; these exclude model initialization and are single-run timings rather than a performance benchmark.

The native black-frame probe produced original-versus-black cosine 0.498 and maximum component difference 0.146. Reversing source order changed a native vector component by up to 0.0808; pooled differences stayed below 6e-8. Repeating the first image changed all three representations. Runtime manifests and numerical checks are preserved in `various/comparison-v2`.

## Classification, direction, and retrieval

Generic classification selects the largest within-space cosine among nine fixed action descriptions. The following table uses original eligible test windows. Supported-class macro F1 omits classes with no eligible test support; the raw results also include macro F1 across all nine declared classes and the complete confusion matrix.

| Representation | Accuracy | Balanced accuracy | Supported macro F1 | False action on controls |
|---|---:|---:|---:|---:|
| Native FP32 | 1/17 (0.059) | 0.021 | 0.037 | 7/8 |
| Pooled FP32 | 0/17 | 0.000 | 0.000 | 8/8 |
| Pooled 4-bit | 7/17 (0.412) | 0.146 | 0.101 | 1/8 |

The 4-bit system's accuracy is mainly attributable to recognizing approach-only controls. Its balanced accuracy remains low. Comparing native with this system changes both temporal processing and checkpoint quantization; it cannot isolate a benefit or penalty from native video alone. The official FP32 pooled control reduces that confound, but its image token structure still differs from native video.

Family-conditioned direction compares a reviewed action query only with its opposite. All three representations produce positive correct-direction margins for five of nine eligible test interactions. No opposite-action margin changes sign under reversal in any split. Native margin magnitudes and vectors do change. The warranted conclusion is sensitivity without demonstrated reversal-consistent direction understanding under these queries.

Retrieval uses each split's original windows as a gallery and reviewed action equality as relevance. Unknown examples remain distractors. Unsupported queries have undefined metrics and are excluded from query means. Interval coverage uses the union of relevant source intervals per video, preventing overlapping windows from counting the same source duration twice. Raw rankings preserve sample and episode identities; there are only three apartment groups, so these means do not support broad confidence claims.

| Representation | Test Success@5 | Test interval coverage@5 | Supported queries |
|---|---:|---:|---:|
| Native FP32 | 0.667 | 0.354 | 6 |
| Pooled FP32 | 0.333 | 0.208 | 6 |
| Pooled 4-bit | 0.333 | 0.333 | 6 |

Retrieval and classification answer different questions. A query can retrieve a relevant clip among five hits even when that clip's highest-scoring description is another action. The stronger native retrieval score therefore does not contradict its poor classification result.

## Abstention and failure evidence

Each representation selects a top-two cosine-gap threshold using development only: maximize answer coverage subject to at most twenty percent observed error on known labels and no answers on unknown labels. This policy is frozen before held-out evaluation. It is an empirical development constraint, not a guaranteed risk bound.

Native accepts five test windows: four known answers are wrong and one unknown example receives an answer. FP32 pooling accepts nine: seven known answers are wrong and two unknown examples receive answers. The 4-bit system accepts two: one correct known answer and one unknown answer. These results show poor transfer of a tiny development calibration set. No test-driven threshold revision was made.

The local evidence gallery at `various/comparison-v2/index.html` combines measurements, source intervals, label rationale, predictions, confidence gaps, and full feature-space identities. It includes corrected sitting, a small microwave, an occluded book transfer, invisible lamp state, and an approach-only control. Its examples were selected after evaluation for explanation and were not used to retune queries. Browser screenshots accompany the source images.

## Temporal handoff and remaining interpretation limits

`output/action-benchmark-v1/temporal-handoff-v2/manifest.json` references 144 sparse sequences: 48 episodes in each of three separate feature spaces. Each NPZ has features `[T,D]`, event and availability times, validity, reviewed-label mask, and integer targets. Original windows alone enter this handoff. Unknown labels do not invalidate their source evidence, and unrepresented intervals do not become background.

These sequences contain one or two benchmark windows per episode. They are useful for validating source mapping and observation ingestion, but are not a dense segmentation training corpus. VIDEO-TEMPORAL-001 must construct a denser trailing-window feature grid for meaningful temporal training and report its weak supervision separately. Event and availability equal source-window end here; actual deployment must additionally account for inference and ingestion latency.

The implementation is reproducible through `python -m video_workbench.actions` prepare, review, encode, and evaluate commands. Run native/FP32 image modes in `output/mlx-video-fix/.venv`; run the 4-bit baseline in `workbench/.venv`. `actions/handoff.py:export` builds the sparse sequence artifacts. `scripts/05-review-window-details.py` and `scripts/06-publish-comparison.py` reproduce the visual audit outputs. Never combine vectors from different spaces in one metric computation.

The next substantive experiment is localization diagnosis followed by temporal modeling with explicit validity and availability. Neither should assume that the present generic action predictions are reliable facts. Oracle fixtures can establish implementation correctness, while weak-feature and real-observation evaluations measure how much useful evidence the system actually has.

## Preserved browser views

![Measured overview](../various/comparison-v2/action-benchmark-v2-overview.png)

[Full source-linked failure gallery screenshot](../various/comparison-v2/action-benchmark-v2-failure-gallery.png).
