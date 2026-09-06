# Generate and review the diverse household corpus

The diversity release supplements the original 24-video appliance corpus. Its configuration is `configs/virtualhome-diversity-v2.json`; it uses a separate output directory, `output/virtualhome-corpus/diversity-v2`. Do not point the diversity exporter at the v1 directory.

The initial design crosses three apartments, four interaction families, two conditions, and two views, producing 48 videos. Each apartment contains all four families. Every scenario has an interaction program and an approach-only control. Both programs are recorded from left and right fixed cameras. The controls share the target, initial actor position, apartment, and camera construction with their interaction counterparts. They are not duration-matched counterfactuals: their programs are shorter, and the simulator may produce slightly different trajectories across resets.

| Family | Training apartment 0 | Development apartment 1 | Test apartment 2 |
|---|---|---|---|
| Open and close | Fridge 308 | Fridge 155 | Microwave 174 |
| Pick up and return | Mug 454 | Book 332 | Plate 67 |
| Sit | Sofa 375 | Sofa 301 | Bed 296 |
| Switch on/off | TV 433 | TV 313 | Table lamp 268 |

These IDs belong to the pinned simulator scenes. The exporter checks the object's class, affordance, and room after resetting the scene. Configuration positions come from successful recorded probes. Each actual insertion must preserve the requested horizontal coordinates within 0.25 m and identify one actual starting room. Starting and target rooms may differ: the final apartment has two bedrooms, and its verified programs can approach the target from the other bedroom. Ambiguous room names are not used for release generation.

## Environment and ownership

Use the pinned environment in [the installation playbook](virtualhome-video-generation.md). The Unity client environment is `output/virtualhome-install/.venv`; it is separate from the MLX workbench environment. Neither embeddings nor the MLX video fix are needed to generate this corpus.

Launch an owned simulator on a free port, keeping graphics enabled:

```sh
output/virtualhome-install/.venv/bin/python \
  ttmp/2026/09/06/COSMOS-VIDEO-001--cosmos-and-video-embeddings-a-procedural-video-lab-on-apple-silicon/scripts/07-launch-corpus-simulator.py \
  --port 18082
```

The launch script checks that the port is free and writes `output/virtualhome-corpus/unity-18082.log`. Stop only the simulator session you own. A client request timeout does **not** cancel Unity execution. If recording times out, stop the owned simulator and inspect the failed attempt before restarting it. The expansion runner stops on the first exception rather than sending more commands to a possibly busy simulator.

## Inspect, generate, and resume

Run commands from the repository root:

```sh
PYTHONPATH=src output/virtualhome-install/.venv/bin/python \
  -m virtualhome_corpus.diversity_runner plan

PYTHONPATH=src output/virtualhome-install/.venv/bin/python \
  -m unittest discover -s tests -v

PYTHONPATH=src output/virtualhome-install/.venv/bin/python \
  -m virtualhome_corpus.diversity_runner generate --port 18082
```

Use `--limit 2` to generate two new episodes. Already completed episodes are validated and skipped, so the limit counts new recordings rather than total existing files. The output directory has an exclusive filesystem lock. Reusing a directory with a different configuration is rejected. Failed attempts remain numbered under their episode; retrying creates a new attempt.

Every manifest records the exact installation metadata and producer file hashes used for that attempt. The current runner does not enforce identical producer hashes across separate invocations: use the same committed implementation for a release and inspect producer consistency in the final audit. If changing the exporter or installation, use a new release name and output directory. Configuration identity alone is not sufficient evidence of identical production code.

## Validation and review

```sh
PYTHONPATH=src output/virtualhome-install/.venv/bin/python \
  -m virtualhome_corpus.diversity_runner validate

PYTHONPATH=src output/virtualhome-install/.venv/bin/python \
  -m virtualhome_corpus.diversity_review

python3 -m http.server 8771 --bind 127.0.0.1 \
  --directory output/virtualhome-corpus/diversity-v2
```

Open `http://127.0.0.1:8771/gallery.html`. The gallery is evaluator-only: its headings and sheets contain labels. Open `calibration.html` to inspect native 640×480 frames through every appliance OPEN/CLOSE interval and neighboring frames. These are references to original PNGs, not downsampled substitutes. The action and graph timelines identify candidate locations for review; they do not establish a visual boundary.

Validation verifies each video hash, full video decoding, dimensions, FPS, frame count, duration, raw PNG/graph hashes, action-export agreement, and supporting annotation hashes. The audit rejects lineage/group or exact video duplication across splits. A five-frame, 64-bit difference-hash comparison reports nearest cross-split pairs as a diagnostic. It does not prove that all perceptually equivalent clips have been detected.

## Artifact contracts

- `config.json` freezes scenario factors, recording dimensions, positions, and split policy.
- `initializations/*.json` records the initial transform reused by each four-episode lineage.
- `episodes/dv-*/manifest.json` points to the current numbered attempt. Attempts retain raw simulator files, graph snapshots, program, annotations, source hashes, MP4, and inspection sheet.
- `inputs.jsonl` exposes only opaque episode ID, split/group, video path, and video SHA-256. Pass videos selected through this file to model inference.
- `labels.jsonl` is evaluator-only: scenario, condition, view, lineage, and annotation reference.
- `annotations.json` preserves raw exported action names and program correspondence. For example, LOOKAT may export as TURNTO. Its guarded action interiors remain weak program supervision.
- `observable-world-runs.json` preserves target states, actor states, and holding relations with the explicit quality `simulator_world_state_not_visual_truth`.
- `audit.json` reports completeness, nearest perceptual pairs, condition durations, and review rows.
- `calibration-review.json` is an unsigned review template and source inventory. Human or assistant review results belong in a separately versioned signed assessment; rerunning the audit regenerates the template.

## Interpretation and experimental limits

The first two fridge recordings visibly opened and closed while every exported graph retained CLOSED. No constant timing correction can recover a missing intermediate state. Keep both `precise_boundary_supervision_allowed` and `dense_visual_state_supervision_allowed` false unless a separately reviewed subset establishes a stronger contract. Do not infer pickup visibility merely from a holding relation, or lamp illumination merely from an ON state.

Whole apartments are assigned to partitions: 16 train, 16 development, and 16 test episodes. All related views and conditions remain together. This avoids testing on another camera view of the same scenario lineage, but one apartment per partition is a small evaluation. Scene, layout, prop identity, and partition are partly confounded. One actor is used, so actor generalization is untested.

Interaction videos are expected to be longer than approach-only controls. Report a duration-only baseline before treating binary interaction classification as evidence of visual understanding. Prefer localized action retrieval, action-class comparisons within the interaction subset, and explicit prop/view stratification. The release increases coverage; it does not by itself establish a statistically strong benchmark.

## Simulator findings to preserve

The ticket contains successful and failed probes, camera captures, and browser screenshots. In this pinned build, the tested explicit PUTBACK-to-desk program failed; a minimal GRAB/PUTOBJBACK program succeeded. LOOKAT during the held-object or seated sequence caused failures in tested compositions. Terminal SIT worked. Some graph-advertised chairs/cabinets could not be approached. Some executable objects were hidden by other furniture. These are observed exclusions for tested programs and bindings, not universal statements about all VirtualHome versions.
