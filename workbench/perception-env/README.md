# Isolated perception runtime

Python 3.11, Torch/Ultralytics, PyAV, and ByteTrack dependencies are isolated from MLX and the simulator. Restore from the hash-locked set:

```bash
uv venv --python 3.11 workbench/perception-env/.venv
uv pip sync --python workbench/perception-env/.venv/bin/python workbench/perception-env/requirements.lock
```

Run from the repository root with `PYTHONPATH=workbench/src` and set `YOLO_CONFIG_DIR` to an existing absolute writable directory such as the workspace's `output/perception-settings`. Use `python -m video_workbench.perception --help`. Model weights live in ignored `output/models/yolo11`; exact hashes are recorded in run metadata. YOLO11 detection/segmentation weights were obtained from the official `ultralytics/assets` v8.3.0 release; the selected Ultralytics package carries AGPL-3.0 metadata. This is the local research runtime, not a distribution decision.

The selected version is Ultralytics 8.4.142 with Torch 2.14.0, torchvision 0.29.0, and lap 0.5.13. `BYTETracker(args)` accepts stored NumPy-backed `Boxes`; the adapter owns session-local IDs, class separation, native cadence, and resets. Tests requiring ByteTrack run in this environment; pure geometry/packet tests also run in the MLX environment.
