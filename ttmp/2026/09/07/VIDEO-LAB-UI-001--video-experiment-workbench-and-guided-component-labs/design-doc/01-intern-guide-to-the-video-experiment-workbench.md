---
Title: Intern guide to the video experiment workbench
Ticket: VIDEO-LAB-UI-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://workbench/src/video_workbench/media.py
      Note: Exact timestamp sampling
    - Path: repo://workbench/src/video_workbench/native_video.py
      Note: Accepted native embedding feature space
    - Path: repo://workbench/src/video_workbench/perception/tracking.py
      Note: Cadence and track identity
    - Path: repo://workbench/src/video_workbench/replay/app.py
      Note: Existing replay integration
    - Path: repo://workbench/src/video_workbench/verifiers/adapter.py
      Note: Accepted bounded evidence contract
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-07T10:05:37.170133-04:00
WhatFor: ""
WhenToUse: ""
---


# Building the video experiment workbench

## 1. Purpose and experimental method

This workbench lets a researcher select visual evidence, execute one component of the video understanding system, and inspect how its output changes when an input or parameter changes. The primary object is an experiment: an immutable selection of a registered video, a half-open time range, a sampling policy, an optional crop, a component, and its configuration. A result belongs to that experiment rather than to the current contents of a form. Editing the form must never relabel an earlier result.

The immediate research problem is concrete. Our camera-departure measurement found twelve departures, but both eight-billion-parameter verifiers missed four open-fridge cases. Valid JSON did not imply correct visual interpretation. A researcher needs to see the actual image presented to the model, enlarge or crop the fridge, compare Qwen and Cosmos on identical evidence, and save a review of the resulting answer. The workbench must also make it possible to investigate earlier stages: detector misses, poorly sampled transitions, weak action classifiers, and retrieval windows that conflate several actions.

This is a local research application. It reuses the existing Python adapters and their separate environments. It does not add model training orchestration, a distributed scheduler, revision/supersession machinery, or a general graph editor. Experiments are separate runs; reviews are separate annotations. This keeps the implementation proportionate while preserving reproducibility.

The experimental loop is:

```text
Select recording and range
         |
Preview exact sampled frames and crop
         |
Select component, model, and configuration
         |
Snapshot request -> run isolated worker -> save result
         |
Inspect overlays, scores, evidence, and failures
         |
Compare runs -> review -> export evaluation case
```

An intern should first run an inexpensive detection experiment over two seconds, inspect its input thumbnails and output boxes, and change the confidence threshold. Next, compare full-frame and cropped reasoning on the same timestamp. Only after understanding these examples should they combine state estimates into transitions or rules.

## 2. Repository map and existing responsibilities

All Python paths below are relative to `workbench/src/video_workbench/`. Read the source functions referenced here before modifying their contracts. The new `lab/` package owns experiment orchestration and presentation; it must not silently change the established feature spaces or verification rules.

| File or package | Responsibility and entry points |
|---|---|
| `media.py` | `probe`, `selected_indices`, and `decode_selected` establish actual presentation timestamps and decode selected RGB images. |
| `registry.py` | `Registry` binds episode IDs to source hashes and partitions; `file_hash` verifies bytes. |
| `perception/detector.py` | `Detector.predict` returns source-coordinate YOLO detections and vendor results. |
| `perception/segmentation.py` | Existing mask probe demonstrates `result.masks.xy` polygon extraction in source coordinates. |
| `perception/tracking.py` | `TrackerSession.update` maintains class-separated ByteTrack tracks at explicit cadence and resets on gaps. |
| `embedding.py` | `QwenEmbedder.image`, `.pool`, and `.text` implement the pooled-image baseline with a hashed `FeatureSpace`. |
| `native_video.py` | `NativeVideoEmbedder.video` and `.text` implement the repaired, accepted native video feature space. |
| `index.py`, `native_index.py` | Immutable retrieval indices and feature-space checks; `Index.search` compares compatible vectors. |
| `temporal/linear.py` | Frozen multiclass ridge fitting/prediction with strict feature-space identity. |
| `temporal/tcn.py` | Temporal convolutional heads trained on frozen sequence features. |
| `temporal/store.py` | Exact observations carry event and availability times; missing samples remain unknown. |
| `rules/evaluate.py` | Pure three-valued rule evaluation over explicit observations/events/coverage. |
| `rules/departure.py` | Camera disappearance candidate generation; this does not recognize door opening. |
| `verifiers/worker.py` | `run` loads an approved local model and executes single-image inference in the verifier environment. |
| `verifiers/adapter.py` | `check_packet`, `supervise`, and `verify` validate evidence and enforce bounded execution. |
| `verifiers/profiles.py` | Named generation profiles, sampling settings, and profile identity. |
| `verifiers/recovery.py` | Strict parsing followed by conservative wrapper recovery; recovery must not invent answers. |
| `replay/app.py`, `replay/engine.py` | Existing causal replay API, worker scheduling, evidence and decision history. |
| `lab/app.py` (planned) | Catalog, preview, experiments, comparison and review HTTP API. |
| `lab/worker.py` (planned) | Component execution using a fixed interpreter and model mapping. |
| `lab/viewer.html` (planned) | Shared video workspace, component controls, rendered results and teaching panels. |

There are four relevant Python environments. `workbench/.venv` serves the application and runs ordinary numerical/media code. `workbench/perception-env/.venv` contains PyTorch and Ultralytics. `workbench/verify-env/.venv` contains the accepted MLX-VLM reasoning runtime. `output/mlx-video-fix/.venv` contains the repaired native embedding runtime. Preserve these environments and the old pooled artifacts. In particular, do not resolve a virtual environment's Python symlink to the system interpreter: use its absolute path without following symlinks.

## 3. Capabilities and model identity

The capability catalog is explicit application data, not a claim derived from a model name. Each component reports whether it can run fresh, can inspect saved artifacts, or is unavailable. Local checkpoint existence is a prerequisite, not an acceptance test. Failures at load or generation time remain visible in the run record.

| Component | Model/runtime | Initial supported evidence |
|---|---|---|
| Detection | YOLO11n, PyTorch/Ultralytics, CPU or MPS | Sampled RGB frames, optional crop |
| Segmentation | YOLO11n-seg, same environment | Instance masks and boxes on sampled frames |
| Tracking | Existing class-separated ByteTrack | Detector outputs at supported fixed cadence |
| Reasoning | Qwen3-VL-Instruct-8B, local 8-bit MLX weights | One RGB image per bounded request |
| Reasoning | Cosmos-Reason2-8B, local 8-bit group-64 MLX weights | One RGB image per bounded request |
| Embeddings | Qwen3-VL-Embedding-2B, community 4-bit pooled baseline | Independent frames, then normalized mean |
| Embeddings | Qwen3-VL-Embedding-2B, official FP32 with repaired MLX | Ordered timestamped video frames |
| State and transitions | Verifier samples and explicit deterministic transition policy | Target door state at sampled times |
| Action classification | Existing frozen TEMPORAL heads and their measured artifacts | Matching feature space and training preprocessing only |
| Rules | Existing pure rule evaluator | Explicit state/event evidence and coverage |
| Replay | Existing bounded replay | Recorded perception; optional fresh single-image verifier |

Do not label the eight-billion-parameter reasoning models as embedding models. They answer questions; the accepted embedding models are the two-billion-parameter Qwen embedding checkpoints. Native and pooled embeddings have different feature identities even when their vector dimensions agree. No vector from one space may be searched against vectors from the other.

Multi-image or native-video reasoning is not currently accepted by `check_packet`. The UI must explain this limitation. A range reasoning experiment can run a sequence of independent single-image requests, but it must label that modality accurately. Such a sequence does not establish that the model understood temporal motion.

## 4. Shared workspace and interaction design

The page has a persistent recording selector, video player, start/end controls, sample rate, crop controls, and evidence preview. Component navigation changes the experiment controls and teaching material without clearing the source selection. The result view is explicitly bound to a saved run. Selecting an old run restores its configuration or displays the difference from the current form.

```text
+--------------------------------------------------------------------+
| Video Laboratory              Source / partition / runtime status   |
+-------------------------------+------------------------------------+
| Video player                  | Component and model                |
| Current time and crop         | Component options with help        |
| Start / end / FPS             | Exact input summary                |
| Sampled evidence thumbnails   | Run / cancel / saved runs          |
+-------------------------------+------------------------------------+
| Detection | Reasoning | States/events | Embeddings | Compare/review  |
+--------------------------------------------------------------------+
| Timeline / overlays / answers / scores / failure reasons             |
| [Guide: concepts, equations, examples, limitations, source links]    |
+--------------------------------------------------------------------+
```

A compact field explanation answers what the option changes and gives its units. The guide panel develops the underlying concept with prose and a worked example. Raw JSON is an optional inspection view, not the default explanation. A result renderer must show meaningful distinctions: unknown versus false, predicted versus observed tracks, similarity versus probability, and baseline versus model-conditioned rule decisions.

Source selection includes the dataset partition. Training labels must never be injected into inference inputs. An annotation created while exploring the test partition is tagged as test review; exporting it must not move it into training silently.

The first usable stage should run at a dedicated loopback URL while the existing replay viewer remains accessible. After each significant feature, provide the URL, a short suggested experiment, and a feedback opportunity. Keep the server running during that review. Screenshots should capture actual model outputs and failure states, not only empty forms.

## 5. Evidence selection, timestamps, and crops

Video frames have presentation timestamps (PTS). Frame index is an ordinal and is not a general clock: variable-frame-rate video can have unequal intervals. `probe` records each raw timestamp, stream time base, normalized microsecond timestamp, dimensions, and the duration of the final frame. The selection interval is half-open: a frame at the end timestamp is excluded.

For requested sampling rate f, the grid is `start + k * 1,000,000 / f` microseconds. For each grid point, select the first available frame at or after it, provided that frame is before the interval end. Duplicate selected indices are removed. The preview must return the actual selected timestamps; requested FPS alone does not describe the evidence.

```python
assert 0 <= start_us < end_us <= source.duration_us
indices = selected_indices(source.pts_us, start_us, end_us, fps)
assert 0 < len(indices) <= MAX_SAMPLES
frames = decode_selected(source.video, indices)
for index in indices:
    save_png(frames[index])
    record(index, source.pts_us[index], raw_pts[index], sha256(png))
```

Use a bounded maximum sample count and reject oversized selections before decoding. A crop is specified in normalized source coordinates `[x0, y0, x1, y1]` with `0 <= x0 < x1 <= 1` and the equivalent y inequality. Conversion to pixels must be deterministic and must reject an empty crop. Save both the source size and exact integer crop rectangle. A full-frame image and a crop are different evidence inputs even if they share a timestamp.

For an output box in crop coordinates, source coordinates add the crop origin. For normalized crop selection, `left = floor(x0 * width)` and `right = ceil(x1 * width)` with bounds clipping. The UI overlay uses the image's displayed content rectangle, not the outer video element when letterboxing exists. The initial implementation can draw overlays directly into saved images to avoid ambiguous browser scaling; interactive source-coordinate overlays can use the same transformation later.

Changing an episode invalidates its crop context and clamps/reset ranges. Clicking an evidence thumbnail seeks the player to its actual timestamp. Browser video seeking is a convenience; the decoded PNG is authoritative evidence.

## 6. Experiment execution and persistence

A run receives a unique ID and a new output directory. Its immutable request contains schema version, component, source hash, partition, selection, model/profile identity, producer code hashes, and upstream run IDs where applicable. Selected images receive hashes. Result files record runtime versions and timing. Reviews are stored separately and never rewrite predictions.

```text
output/video-lab/<run-id>/
    request.json          validated snapshot and evidence specification
    inputs/*.png          actual input images
    result.json           structured result or explicit error
    worker.log            bounded diagnostic output
    artifacts/*.png       overlays and explanatory visual evidence
    review-<id>.json       independent user annotation
```

The service runs one expensive experiment at a time on this Mac. Start returns HTTP 202 immediately. A background supervisor launches a fixed Python module in the appropriate environment, captures status, enforces a wall-clock deadline, and kills/reaps the worker process group on cancellation. The browser polls for status and never blocks the HTTP request on model inference. A second concurrent run returns 409 with an explanation; a distributed queue is unnecessary here.

```text
created -> running -> completed
                  -> failed
                  -> timed_out
                  -> cancelled
```

Startup must classify abandoned nonterminal runs as interrupted. Cancellation is explicit and must not be reported as a valid negative model answer. Only server-owned catalog IDs and output filenames may cross the API boundary; clients do not provide executable paths or arbitrary filesystem paths. Bound sample counts, runtime, output size, and request lengths. Preserve raw failures for debugging without flooding the browser with logs.

## 7. Detection, masks, and tracking

Detection predicts a class, score, and rectangle for each object candidate. The score threshold determines which predictions survive filtering. It is not an estimated probability that a downstream state is correct. Nonmaximum suppression removes overlapping predictions according to an intersection-over-union threshold:

`IoU(A, B) = area(A intersection B) / area(A union B)`.

A lower confidence threshold usually reveals more weak candidates and more false positives. A higher NMS IoU threshold allows more overlapping boxes to survive. The UI should expose confidence, NMS IoU, image inference size, device, and class filter, and save them with each run. YOLO's class label identifies an object category; it does not tell whether a fridge door is open.

Instance segmentation adds a polygon or pixel mask associated with each instance. Display masks translucently over the exact input image and list mask area as a descriptive measurement. A mask boundary is a model prediction, not an annotation. A missing fridge mask should remain visible as a failure, not be replaced by a manually chosen crop without disclosure.

Tracking associates detections between samples. The existing `TrackerSession` separates classes, requires increasing timestamps, and resets when a gap exceeds its cadence policy. A predicted track without a current detection must be styled differently from an observed track. For irregular sampling, reject unsupported cadence or display explicit resets. Never rescale timestamps to pretend that sparse frames form native-rate video.

Useful experiments include changing confidence on identical frames, comparing detector and segmentation checkpoint results, and inspecting whether a crop increases target detections while removing relevant context. Comparisons must show the input difference.

## 8. Reasoning and state experiments

Reasoning controls select Qwen or Cosmos, an accepted generation profile, output token budget, target label, and exact image input. The approved verifier contract asks a bounded question about `door_open`; a general free-form explanation is a different experiment contract and should not bypass validation. Show the actual prompt, processed input dimensions, raw answer, parsed result, recovery status, and runtime separately.

A malformed answer, a timeout, and a visually unknown answer are different outcomes. None means closed. A closed case means the target door was judged not open under the contract; it does not mean that the whole incident was resolved. For a rule requiring a closed door at departure, a valid false `door_open` answer can condition the rule to PASS, but visual correctness still needs review.

A state experiment applies the bounded image verifier independently to each selected timestamp. It produces samples such as `(8.0 s, closed)`, `(9.0 s, unknown)`, `(10.0 s, open)`. It does not fill the unknown interval automatically. Sequence execution may reuse a loaded model only if the worker retains per-request evidence and validation; the first implementation can prioritize correctness over load amortization.

A transition is inferred from two valid samples of the same target. Closed at a and open at b supports an OPEN transition somewhere in `(a, b]`, provided the gap is within the chosen maximum and there is no intervening unknown sample. It does not support an exact action time or actor attribution.

```python
previous = None
for sample in ordered_samples:
    if sample.state == UNKNOWN:
        previous = None
        continue
    if previous and sample.time - previous.time <= max_gap:
        if previous.state != sample.state:
            emit(kind='OPEN' if sample.state == OPEN else 'CLOSE',
                 start=previous.time, end=sample.time,
                 evidence=[previous.id, sample.id])
    previous = sample
```

The guide must distinguish object state, state change, and human action. The temporal action head predicts classes such as OPEN, CLOSE, GRAB, PUTBACK, and WALK from frozen visual features. It is a separate statistical model. Connecting it requires exact checkpoint, preprocessing, window policy, and feature-space identity. Display existing measured action artifacts while implementing fresh compatible inference; do not apply a pooled head to native vectors.

## 9. Embedding windows and retrieval mathematics

An embedding is a finite vector representing an input under a specific model and preprocessing policy. Unit normalization computes `u = x / sqrt(sum(x_i^2))`. Similarity between two unit vectors is their dot product, which equals cosine similarity. This score is not a calibrated probability and cannot be compared numerically across unrelated spaces.

The pooled baseline encodes frames independently, normalizes them, averages the vectors, and normalizes the mean. Consequently, permuting the frames does not change the mathematical pooling result. The native adapter encodes ordered frames and timestamps jointly. The accepted native system also changes precision and preprocessing; a measured quality gain does not isolate temporal ordering as its sole cause.

```python
pooled = normalize(mean([embed_image(frame) for frame in frames]))
native = embed_video(frames, actual_pts_us, window_start_us)
query_vector = matching_encoder.embed_text(query)
score = dot(window_vector, query_vector)
```

The UI exposes window duration, stride, FPS, query, and feature mode. Generate windows within the selected interval, save the actual frame membership for each window, and rank only within a compatible space. A shorter window provides finer localization but less context. Overlapping windows share frames and are not independent examples. Show the ranked windows and a similarity-over-time plot, with an explicit empty-window/error result.

A comparison between pooled and native runs matches source, range, query, and window membership. Show ranked results side by side and warn if any of those differ. Do not subtract vectors or present mixed-space nearest neighbors. Saving vectors and the complete feature-space description allows subsequent runs to inspect the result without reloading a model.

## 10. Rules and replay

Rules consume explicit evidence. For `state_at_event`, an exact known state satisfying the condition yields PASS, a known contradicting state yields VIOLATION, and absent or unknown evidence yields UNKNOWN. `before` checks strict ordering. `no_event_in` requires explicit coverage of the whole interval. A missing detection is not evidence of no event unless the coverage contract supports that inference.

The workbench should let a user choose upstream experiment results and a small set of rule templates. A first useful template asks whether a door is closed at an explicitly selected time. If no state sample exists at that time, show UNKNOWN and explain why. Do not silently choose the nearest observation. An event inferred over an interval has temporal uncertainty; rules requiring an exact event instant need an explicit policy or remain unknown.

Replay introduces availability time and service constraints. Event time says when something happened in the recording. Availability time says when the system could use the evidence. An as-of view excludes results arriving later, even if their video timestamp is earlier. The existing replay viewer remains the reference implementation for bounded queues, dropped work, and baseline versus conditioned decisions. Link or mount it from the laboratory and explain that offline component runs do not measure causal streaming performance.

## 11. Comparison, review, and export

A comparison selects two immutable runs. First compare source hashes, partitions, ranges, frame timestamps, crops, models, profiles, and feature IDs. Display differences before outcome differences. Identical timestamps with different crops are an input intervention; identical evidence with different models is a model comparison. Neither establishes population-level improvement from one example.

Reviews have `correct`, `incorrect`, or `unjudgeable`, a free-text explanation, and optional state/event annotations. Store run identity, reviewer-provided text, source identity, partition, and creation time. Never modify the model's answer to match a review. A JSON export bundles the experiment request, results, and reviews; source and evidence identities remain present so future training/evaluation tooling can reconstruct the case.

Pipeline presets are ordinary saved configurations and explicit dependencies: for example, sampled state verification followed by transition extraction. Avoid a generic visual node editor. A preset must show its stages and allow inspection of each intermediate output. A detection-to-reasoning preset must show the actual selected detection/crop and its provenance; it must not silently choose the highest-confidence object of an unrelated class.

## 12. Proposed HTTP interface

The implementation may refine names while preserving these contracts. FastAPI's generated `/docs` and `/openapi.json` become the authoritative executable schema; this guide should be updated if the implemented request fields change.

| Method and path | Request/result |
|---|---|
| GET `/v1/lab/catalog` | Registered sources, component/model capabilities, supported bounds and presets. |
| POST `/v1/lab/preview` | Validated source/range/FPS/crop; returns exact frame IDs, PTS and image URLs. |
| GET `/v1/lab/sources/{id}/video` | Hash-verified registered MP4 with range support. |
| POST `/v1/lab/runs` | Immutable experiment configuration; returns 202 with run ID. |
| GET `/v1/lab/runs` | Recent run summaries. |
| GET `/v1/lab/runs/{id}` | Request, status, structured result and artifact links. |
| POST `/v1/lab/runs/{id}/cancel` | Cancels the active experiment and reaps its worker. |
| GET `/v1/lab/runs/{id}/artifacts/{name}` | Bound artifact access; no arbitrary paths. |
| POST `/v1/lab/runs/{id}/reviews` | Independent review attached to this immutable run. |
| GET `/v1/lab/runs/{id}/export` | Reproducible experiment and review JSON. |

Illustrative request (the final Pydantic schema governs exact fields):

```json
{
  "episode_id": "ep-7d3106fb1cac9776",
  "start_us": 9500000,
  "end_us": 10500000,
  "fps": 2,
  "crop": null,
  "component": "segmentation",
  "model": "yolo11n-seg",
  "confidence": 0.25,
  "iou": 0.7
}
```

Return 422 for invalid ranges, unsupported combinations, or excessive samples; 404 for unknown source/run; 409 for active-worker conflicts or changed source bytes. The UI should display these messages near the controls and preserve the user's selections.

## 13. Implementation phases and acceptance

1. **Design and delivery.** Create this ticket, relate source files, document contracts and teaching content, upload the intern guide to reMarkable, and commit the design.
2. **Shared workspace.** Implement catalog, range/crop sampling, authoritative thumbnails, persistent run history and page guide. Smoke-test range validation and source binding; open the UI for feedback and capture screenshots.
3. **Perception and reasoning.** Add isolated workers, cancellation, YOLO boxes/masks/tracks, and both accepted reasoning models. Run actual segmentation and reasoning on selected frames, inspect overlays and raw/parsed output, and offer browser feedback.
4. **States, events, and embeddings.** Add sampled state inference and explicit transition extraction, compatible embedding windows/query scores, and honest action artifact inspection/fresh adapter coverage. Verify a real native/pooled comparison without mixing features. Offer browser feedback.
5. **Comparison, review, presets, and rules.** Add saved run comparison, user review/export, explicit pipeline presets, and rule inputs. Integrate replay navigation. Verify that current form changes cannot relabel old evidence.
6. **Handoff.** Perform focused final smoke testing, inspect the browser console and screenshots, update the guide to actual APIs, archive measurements and limitations, commit implementation and diary, and leave the UI running for review.

Test at feature boundaries rather than after every small edit. Focus tests on real failure risks: invalid/empty selections, source mutation, worker cancellation, stale result display, crop coordinate mapping, incompatible feature spaces, and unknown state handling. Actual model smoke runs are necessary to verify environment and preprocessing integration; repeated exhaustive model runs are not needed for layout changes.

Every meaningful phase receives a start/done work slip. Every significant feature receives a screenshot and a feedback opportunity. The diary records exact failures, corrective changes, validation commands, and code commit IDs. Completion means usable experiments with truthful capability labels and explanatory pages, not merely navigation shells.

## 14. Project browser and supporting resources

The user requested a separate project browser while reviewing the first UI. `/resources` now provides a searchable tree of current local source files and ticket documents. Selecting a file opens an embedded reader; `/resources?file=<id>` preserves the selection in a shareable URL. `/resources/<id>` opens the reader directly, and `/resources/<id>/raw` returns the original text. Source lines have anchors such as `#L42`.

Markdown is parsed with markdown-it-py with raw HTML disabled. Pygments highlights source files and fenced code blocks. Markdown headings receive anchors and a contents foldout; tables and indexed raster images render in the document. Relative links to indexed project resources are rewritten to served URLs. Unindexed local links are marked unavailable. The reader displays the current file SHA-256, so a reader can distinguish working-tree content from a historical experiment snapshot.

`lab/resources.py` owns the allowlisted catalog, curated component reading paths, link rewriting, and HTML rendering. `lab/browser.html` implements search, filtering, the file tree and embedded reader. The browser cannot request arbitrary filesystem paths: IDs map only to indexed project code, ticket design/reference Markdown and ticket raster figures. Source and document content are escaped; the rendered reader uses a restrictive content security policy.

The experiment Guide tab includes three reading groups: source code, local designs/measured reports, and official online resources. Upstream examples may describe different checkpoint versions or modalities, so each external link has a short explanation of its relationship to the local implementation. Online references were checked on 2026-09-07. Rendering requires no CDN, external JavaScript, or new service.

The server accepts repeated `--host` flags. The current command binds loopback and this Mac's Tailscale address, so both `http://127.0.0.1:8780/` and `http://mimimi:8780/` reach the same laboratory. The default remains loopback when no host is specified.

## 15. Delivered implementation update

The implementation now includes fresh ridge action inference in addition to frozen-result inspection. `lab/worker.py: actions` validates the frozen training feature manifest and encoder identity, computes new native or pooled embeddings, and applies the matching ridge weights. Full-frame 2 FPS input and half-second range endpoints are required; the two-second trailing context resets at the selected range start. TCN execution remains outside the offered modes.

`lab/analysis.py` implements comparison, independent reviews/export, frozen action inspection and exact-point rules. `lab/analysis.js` renders comparisons, similarity plots, rule controls and reviews. `/resources` is the separate project browser requested during feedback. The authoritative API reference and measured walkthrough are in [Delivered workbench API and measured feature walkthrough](../reference/02-delivered-workbench-api-and-measured-feature-walkthrough.md), with screenshots and a table of actual local runs.

The first implementation uses one shared sampling grid per selection, then filters those actual frames into embedding windows. It does not restart a sampling grid at every arbitrary window boundary. This policy is saved in each result. Comparison checks exact frame identities before reporting matched evidence. The API's generated schema is archived with the ticket and served at `/openapi.json`.
