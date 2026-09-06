# Generate local test videos with VirtualHome-AIST

This playbook uses the already installed VirtualHome-AIST simulator on the M1 Max. It is intended for a coding agent generating small synthetic videos for retrieval, state-recognition, or temporal-model tests. No Unity Editor, cloud service, or model inference is needed.

The verified example is one character walking to a sofa and sitting down in scene 0. Other activities are supported by the simulator, but each new action sequence must be checked for successful execution and useful visual output.

## 1. Installation and working directories

Run the commands in this playbook from:

```text
/Users/manuel/code/wesen/2026-09-06--vision
```

The installation is isolated under `output/virtualhome-install/`:

- `.venv/bin/python`: Python 3.11.4 with the installed AIST dependencies.
- `virtualhome-aist/`: AIST Python source at `122d3b0aee04768d988e02929f6eeeb38f2f28a8`.
- `simulator/`: official macOS application, universal ARM64/x86_64 binary.
- `start-simulator.py`: launcher that reads `CFBundleExecutable` and defaults to port 18080.
- `notebook.sh`: optional JupyterLab launcher.
- `smoke_test.py`: installation check; uses a fixed output directory, so prefer the fresh-run recipe below for dataset generation.
- `installation.json`, `requirements-mac.txt`, `requirements-lock.txt`: provenance and environment details.

The parent repository ignores `output/`. Videos and environments are local assets. Copy or archive selected artifacts intentionally if another machine needs them.

The two local compatibility changes are already applied: the application executable has execute permission, and the camera helpers use `collections.abc.Iterable`. Do not reinstall the obsolete requirements file from the AIST repository; use the existing environment and its lock snapshot.

## 2. Start a simulator you own

In a dedicated terminal:

```sh
output/virtualhome-install/.venv/bin/python \
  output/virtualhome-install/start-simulator.py --port 18080
```

Leave this process running while generating episodes. Its log is `output/virtualhome-install/logs/unity.log`. Start a separate process on a different port if another agent owns the simulator already. Resetting a shared simulator would destroy that agent's current scene.

Check readiness with a bounded HTTP request:

```sh
output/virtualhome-install/.venv/bin/python - <<'PY'
import requests
response = requests.post(
    'http://127.0.0.1:18080',
    json={'id': 'readiness-check', 'action': 'idle'},
    timeout=5,
)
response.raise_for_status()
result = response.json()
if not result.get('success'):
    raise RuntimeError(result)
print('VirtualHome-AIST is ready')
PY
```

Graphics must remain enabled for RGB generation. Do not add `-nographics`. The installation test successfully used batch mode with graphics, but the provided persistent launcher opens the normal application session.

If a sandbox prevents process launch, local socket access, or Unity's runtime writes, use the tool's normal approval mechanism for that concrete operation. Do not change global macOS security settings or terminate unrelated Unity processes.

## 3. Generate one complete episode

This recipe connects to the process on port 18080. It resets scene 0, adds one character, chooses a sittable sofa, and records walking followed by sitting. Every invocation creates a unique output directory. A failed run retains its artifacts and a `failed` manifest for diagnosis.

The source program's `<char0>` token is an actor index. It is not a graph ID. The recipe discovers the added character's graph ID and records the mapping.

```sh
output/virtualhome-install/.venv/bin/python - <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import uuid

from simulation.unity_simulator import UnityCommunication

root = Path('output/virtualhome-install').resolve()
run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run_id += '-' + uuid.uuid4().hex[:8]
run = root / 'episodes' / run_id
run.mkdir(parents=True, exist_ok=False)

fps = 10
width, height = 640, 480
seed = 7
manifest = {
    'episode_id': run_id,
    'status': 'started',
    'scene_index': 0,
    'port': 18080,
    'recording': {
        'fps': fps, 'width': width, 'height': height,
        'camera_mode': ['AUTO'],
        'out_graph': True, 'per_frame': 1,
    },
    'render_seed': seed,
    'initial_room': 'livingroom',
    'determinism_verified': False,
    'action_endpoint_convention': 'unresolved',
    'graph_image_capture_phase': 'unverified',
    'installation': json.loads((root / 'installation.json').read_text()),
}

def save_manifest():
    temporary = run / 'manifest.tmp'
    temporary.write_text(json.dumps(manifest, indent=2) + '\n')
    temporary.replace(run / 'manifest.json')

save_manifest()
comm = UnityCommunication(port='18080', timeout_wait=180)
try:
    if not comm.reset(0):
        raise RuntimeError('Scene reset failed')
    ok, before = comm.environment_graph()
    if not ok:
        raise RuntimeError('Initial graph fetch failed')
    (run / 'graph-before.json').write_text(json.dumps(before, indent=2))

    sofas = [node for node in before['nodes']
             if node['class_name'] == 'sofa'
             and 'SITTABLE' in node.get('properties', [])]
    if not sofas:
        raise RuntimeError('Scene has no sittable sofa')
    target = min(sofas, key=lambda node: node['id'])

    if not comm.add_character('Chars/Male1', initial_room='livingroom'):
        raise RuntimeError('Character insertion failed')
    ok, initial = comm.environment_graph()
    if not ok:
        raise RuntimeError('Post-insertion graph fetch failed')
    characters = [node for node in initial['nodes']
                  if node['class_name'] == 'character']
    if len(characters) != 1:
        raise RuntimeError(f'Expected one character, got {len(characters)}')
    (run / 'graph-initial.json').write_text(json.dumps(initial, indent=2))

    program = [
        f"<char0> [Walk] <sofa> ({target['id']})",
        f"<char0> [Sit] <sofa> ({target['id']})",
    ]
    manifest['bindings'] = {
        'char0': characters[0]['id'], 'target_sofa': target['id'],
    }
    manifest['program'] = program
    (run / 'actions.txt').write_text('\n'.join(program) + '\n')
    save_manifest()

    ok, result = comm.render_script(
        program,
        recording=True,
        randomize_execution=False,
        random_seed=seed,
        output_folder=str(run),
        file_name_prefix='episode',
        frame_rate=fps,
        image_width=width,
        image_height=height,
        camera_mode=['AUTO'],
        save_pose_data=True,
        out_graph=True,
        per_frame=1,
    )
    manifest['render_result'] = result
    if not ok:
        raise RuntimeError(f'Action execution failed: {result}')

    ok, after = comm.environment_graph()
    if not ok:
        raise RuntimeError('Final graph fetch failed')
    (run / 'graph-after.json').write_text(json.dumps(after, indent=2))

    frame_dir = run / 'episode' / '0'
    images = {int(p.name.split('_')[1]): p
              for p in frame_dir.glob('Action_*_0_normal.png')}
    graphs = {int(p.name.split('_')[1]): p
              for p in frame_dir.glob('Action_*_0_graph.json')}
    if not images or set(images) != set(graphs):
        raise RuntimeError('Missing or mismatched RGB/graph frame keys')
    if sorted(images) != list(range(len(images))):
        raise RuntimeError('RGB indices are not contiguous from zero')
    for path in graphs.values():
        json.loads(path.read_text(encoding='utf-8-sig'))

    video = run / 'episode.mp4'
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error',
        '-framerate', str(fps), '-start_number', '0',
        '-i', str(frame_dir / 'Action_%04d_0_normal.png'),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart', str(video),
    ], check=True)
    metadata = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,nb_frames,r_frame_rate',
        '-show_entries', 'format=duration', '-of', 'json', str(video),
    ], text=True))
    stream = metadata['streams'][0]
    if int(stream['nb_frames']) != len(images):
        raise RuntimeError('Encoded video frame count differs from PNGs')
    if (stream['width'], stream['height']) != (width, height):
        raise RuntimeError('Unexpected encoded dimensions')

    manifest.update({
        'status': 'complete',
        'frame_count': len(images),
        'graph_count': len(graphs),
        'video': 'episode.mp4',
        'video_sha256': hashlib.file_digest(video.open('rb'), 'sha256').hexdigest(),
        'video_metadata': metadata,
        'graph_encoding': 'utf-8-sig',
    })
    save_manifest()
    print(run)
    print(json.dumps(manifest, indent=2))
except Exception as error:
    manifest.update({'status': 'failed', 'error': str(error)})
    save_manifest()
    raise
PY
```

This recipe is adapted from the verified installation test and adds fresh directories, explicit errors, actor binding, validation, and encoding. The original smoke test was executed successfully; the expanded recipe is documented for the next agent and has not itself been run end-to-end yet. Its syntax and installed API arguments were checked during authoring.

The render seed does not establish full determinism. `add_character(initial_room=...)` does not specify a fixed character pose. Record the post-insertion graph and test repeated runs before claiming deterministic data generation.

## 4. Inspect the result before using it

Open `episode.mp4` and inspect frames near each action transition. The manifest being complete means the structural checks passed; it does not mean the intended action is visible from the selected camera.

Check these independently:

1. The program names the intended actor and object instance.
2. The simulator reports successful execution.
3. The images show the action and relevant objects clearly enough for the task.
4. Every RGB frame has a matching parseable graph file.
5. The encoded frame count matches the source sequence.
6. The annotations support the intended label rather than merely containing a related field.

The first verified installation run produced 61 RGB frames and 61 graph files at ten FPS. The encoded video was 6.1 seconds long. Frame 30 showed a standing character near the sofa; frame 60 showed the character seated.

## 5. Important annotation limits

### Raw action endpoints are unresolved

The first run's `ftaa_aist-smoke.txt` contained:

```text
0 WALK 0 32
1 SIT 33 61
```

Image indices were 0 through 60. Do not silently interpret both endpoints as inclusive or both as half-open. Preserve the raw file and determine the exporter's convention before training an action-boundary model. The generation recipe deliberately records `action_endpoint_convention: unresolved`.

### Graph state and action labels are different

The final character graph in the verified run had no explicit `SITTING` state despite successful execution and a visibly seated pose. `SITTABLE` on a sofa is an affordance, not evidence that someone is sitting on it. Graph IDs also differ from actor indices: `<char0>` mapped to graph entity 1 in that run.

The graph's three-dimensional `bounding_box` is not a pixel-space 2D detection rectangle. AIST advertises a separate 2D-box capability, but that output has not been verified locally.

### Matching keys do not prove capture phase

Matching frame IDs establish how to pair files. They do not prove whether Unity exported the graph immediately before or after rendering the image. Verify capture phase using an observable state transition before making precise timing claims.

### Scene truth may be invisible

The graph may contain objects outside the camera view or behind other objects. Keep visibility or ambiguity labels separate from world truth. Do not score a model as wrong for failing to observe a state absent from its supplied pixels.

## 6. Change the activity carefully

Use `comm.environment_graph()` to discover objects and properties. Build action strings from the current scene's IDs rather than copying IDs from another scene.

```python
ok, graph = comm.environment_graph()
if not ok:
    raise RuntimeError('Graph fetch failed')
for node in graph['nodes']:
    if node['class_name'] in {'fridge', 'cabinet', 'cup', 'sofa'}:
        print(node['id'], node['class_name'], node.get('properties', []))
```

To attempt a new task, change the target selection and program in the recipe. For example, walking to an openable object and opening it is a useful state-transition experiment, but must be checked against the actual action vocabulary and scene preconditions. Read `virtualhome-aist/simulation/unity_simulator/comm_unity.py` and the AIST demo notebooks for the installed interface.

A simulator may reject an intentionally invalid sequence or perform navigation needed by an action. A textual mutation is therefore not automatically a useful valid/violation video pair. Verify the actual result and preserve failure responses.

For controlled test sets:

- Change one semantic factor per pair, such as target identity, action repetition, or order.
- Keep related variants in the same train/development/test split group.
- Use consistent camera settings before testing additional views.
- Record scene, character initialization, program, seeds, simulator release, and client revision.
- Keep truth files out of pixel-only model inputs. Avoid label-bearing filenames in the model prompt.

## 7. Interactive notebooks

```sh
output/virtualhome-install/notebook.sh
```

Use `UnityCommunication(port='18080')` if connecting to the persistent launcher. Replace upstream Windows paths and default-port assumptions before executing their setup cells. Do not let two notebooks reset or control the same simulator concurrently.

## 8. Troubleshooting

| Symptom | Check or action |
|---|---|
| Cannot import `simulation` | Use the installation's `.venv/bin/python`; its `.pth` file points to the AIST checkout. |
| Connection refused | Confirm the simulator process and port; use the readiness request. |
| Startup failure | Read `logs/unity.log`; inspect the bundle executable and execute permission. |
| Missing `collections.Iterable` | Confirm the local `collections.abc.Iterable` patch in `comm_unity.py`. |
| JSON parse error at the first character | Read graph JSON using `utf-8-sig`. |
| Render reports failure | Inspect returned per-character details, target ID, object properties, and action preconditions. |
| Black or irrelevant frames | Keep graphics enabled and inspect camera selection; execution success does not prove visibility. |
| Unexpected extra frames | Use a unique run directory; stale exports from earlier runs must not be counted. |
| MP4 shorter than expected | Validate contiguous source indices before FFmpeg and compare encoded frame count afterward. |
| Notebook examples fail | Distinguish an old notebook API assumption from a broken installation; start with the small known-working program. |

When finished, stop only the simulator process started for this experiment, normally with Ctrl-C in its terminal. Retain the episode manifest and failed-run logs when reporting an issue.

## 9. References

- Local installation: `output/virtualhome-install/README.md`.
- Verified test: `output/virtualhome-install/smoke_test.py` and `smoke-output/result.json`.
- API implementation: `output/virtualhome-install/virtualhome-aist/simulation/unity_simulator/comm_unity.py`.
- [AIST project](https://github.com/aistairc/virtualhome_aist).
- [Installed simulator release](https://github.com/aistairc/virtualhome_unity_aist/releases/tag/Door_Modified_Build_2023_0404).
- Vault report: `Projects/2026/09/06/PROJ - VirtualHome-AIST - Native Apple Silicon Simulation and Video Ground Truth.md` in go-go-parc.
