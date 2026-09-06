# Generate the household training corpus

Use the installed environment described in [the simulator playbook](virtualhome-video-generation.md). The implementation lives in `src/virtualhome_corpus/`; its checked configuration is `configs/virtualhome-household-v1.json`.

The first corpus has 24 episodes: two appliances (fridge and microwave), four grouped initializations/views, and three variants per appliance. Each routine opens the target, walks to the neighboring appliance, and then either closes it, omits closure, or closes and reopens it before walking to the living room. The detour gives the door state time to remain visible. These are procedural demonstrations, not instructions for hazardous appliance operation; no heating or cooking action is used.

## Start an owned simulator

Use the ticket's `scripts/07-launch-corpus-simulator.py --port 18081` with `output/virtualhome-install/.venv/bin/python`. It checks that the port is free and writes a separate Unity log under `output/virtualhome-corpus/`. Keep graphics enabled. Do not reset a simulator another process owns.

## Inspect the plan and test the exporter

Run from the repository root:

```sh
PYTHONPATH=src output/virtualhome-install/.venv/bin/python \
  -m virtualhome_corpus plan

PYTHONPATH=src output/virtualhome-install/.venv/bin/python \
  -m unittest discover -s tests -v
```

## Generate and resume

```sh
PYTHONPATH=src output/virtualhome-install/.venv/bin/python \
  -m virtualhome_corpus generate \
  --port 18081 --output output/virtualhome-corpus/home-v1
```

Use `--limit 1` and a separate output directory for a smoke test. Repeating the same generation command verifies and skips completed episodes. Failed attempts remain under their episode directory, and retries receive a fresh attempt directory. A filesystem lock prevents two writers from controlling the same corpus run.

The generator refuses to resume a corpus with changed configuration, installation metadata, or exporter source hashes. Choose a new output directory after such changes. The port explicitly identifies an owned simulator; it is not a process-discovery or ownership protocol.

## Validate every asset

```sh
PYTHONPATH=src output/virtualhome-install/.venv/bin/python \
  -m virtualhome_corpus validate \
  --output output/virtualhome-corpus/home-v1 --deep
```

Validation checks source frame continuity, RGB/graph pairing, JSON decoding, dimensions, MP4 FPS/count/duration, video SHA-256, endpoint truth, and agreement between raw action rows and exported annotations. It rejects an incomplete corpus or identical video bytes crossing splits.

## Output contracts

- `corpus.json` and `plan.json` freeze configuration and provenance.
- `groups/*.json` record the initial actor position reused across related variants. Full pose/render determinism is not claimed.
- `inputs.jsonl` contains only episode ID, split/group, video path, and hash. Supply videos through these opaque episode IDs to model inference.
- `labels.jsonl` contains evaluator-only family, variant, action-annotation path, and endpoint rule truth.
- `retrieval-queries.json` provides four query families with weakly labeled relevant action interiors.
- `summary.json` reports completeness, counts, split distribution, and limitations.
- `episodes/ep-*/manifest.json` points to the latest attempt. Every attempt retains the program, graph snapshots, raw Unity PNG/JSON/pose/action files, MP4, annotations, world-state streams, and a labeled contact sheet.

The configured split is 12 training episodes, six development episodes, and six test episodes. All six episodes in an initialization/view group stay together. This is a within-scene split: it does not establish generalization to unseen homes, actors, or simulators.

## Annotation limits and permitted use

VirtualHome may insert WALK rows and repeat a source-program index. The parser keeps all rows. Raw endpoint convention remains unresolved. Exported intervals trim two frames from either end and are explicitly **weak program supervision**; the trimming is not proof of physical boundary alignment.

Per-frame graphs are preserved as simulator world-state exports. Their capture phase relative to RGB is unverified, and an initial fridge pilot showed no intermediate OPEN state in a complete open-close sequence. Consequently, precise boundary supervision and dense visual state supervision are disabled in the annotations. Endpoint verdicts are checked against the final graph and actor destination, not inferred solely from the intended program.

Use this first corpus for coarse action recognition, retrieval, pipeline development, and oracle episode-rule tests. Inspect contact sheets and the actual video before accepting individual clips as visually labeled training data. Exact transition timing and automatic visibility labels require a separate calibration task.
