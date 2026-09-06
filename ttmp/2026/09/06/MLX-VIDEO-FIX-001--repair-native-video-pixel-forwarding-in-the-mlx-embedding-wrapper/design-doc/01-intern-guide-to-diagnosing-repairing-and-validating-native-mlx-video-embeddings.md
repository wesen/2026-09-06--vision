---
Title: Intern guide to diagnosing repairing and validating native MLX video embeddings
Ticket: MLX-VIDEO-FIX-001
Status: active
Topics:
    - video
    - embeddings
    - cosmos
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles:
    - Path: repo://ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/sources/manifest.json
      Note: Source snapshot provenance and hashes
    - Path: repo://ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/sources/mlx-vlm-0.6.17-backbone.py
      Note: Separate image and video routing contracts
    - Path: repo://ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/sources/mlx-vlm-0.6.17-embedding.py
      Note: Exact omitted argument in installed wrapper
    - Path: repo://ttmp/2026/09/06/MLX-VIDEO-FIX-001--repair-native-video-pixel-forwarding-in-the-mlx-embedding-wrapper/sources/official-qwen-reference.py
      Note: Reference forward and pooling implementation
    - Path: repo://workbench/src/video_workbench/embedding.py
      Note: Existing explicit pooled-image adapter and future integration boundary
    - Path: repo://workbench/src/video_workbench/media.py
      Note: Shared PTS-aware frame sampling
ExternalSources: []
Summary: ""
LastUpdated: 2026-09-06T14:00:28.608154-04:00
WhatFor: ""
WhenToUse: ""
---


# Repairing native video embeddings in MLX

> Status update, 2026-09-06: This guide preserves the original design. P0–P2 have since been implemented and experimentally verified; the fresh targeted run passed 15 tests at `6452614`. P3 processor/reference parity remains under investigation. Historical statements below about work not yet performed refer to guide creation. See the current diary and tasks before resuming.

## 1. Mission and completion criteria

This ticket repairs the path from decoded video pixels to a Qwen3-VL embedding in MLX. The immediate consumer is the timestamped video search workbench in VIDEO-SEARCH-001. Its embedding prerequisite is COSMOS-EMBED-001. The corpus contains household actions generated with VirtualHome, including opening, closing, and reopening fridge and microwave doors. Correctly representing the frames is a prerequisite for studying those actions; successfully representing frame order is a separate question that must be measured.

The target defect is in the installed `mlx-vlm==0.6.17` embedding wrapper. Its public call accepts arbitrary keyword arguments, but its hidden-state helper does not receive or forward `pixel_values_videos`. The shared Qwen3-VL backbone has a separate video-pixel branch. This is strong source-level evidence of an omitted argument. It is not yet an experimentally reproduced claim that every video call returns identical embeddings: a particular request may fail earlier, fail later, or depend on token and timestamp metadata even when visual content is missing.

The deliverable is a small, reviewable repair supported by a failing regression test, a passing repaired test, real pixel-dependence measurements, text/image regression checks, and comparison with a controlled reference. A vector of the expected size alone does not establish correctness. Native video remains disabled in the application until these gates pass.

This document is an analysis and implementation plan. No repair, native-video reproduction, GPU benchmark, or upstream issue submission was performed while creating it. The existing image smoke is historical evidence and is archived separately. All proposed modules and commands below are explicitly labelled when they do not exist yet.

Acceptance requires:

- Video tensors and their matching grids reach the vision tower without being relabelled as images.
- Text, image, video, and mixed image/video cases either work under an explicit contract or fail clearly as unsupported.
- Results for an independent request do not depend on the preceding request.
- Padding does not change which semantic token is pooled.
- Real pixel interventions change the computed visual features; materialization and measurement are explicit.
- Numerical comparison separates implementation differences from quantization and preprocessing differences.
- The application gives native video its own feature-space identity and never reuses pooled-image cache entries.

## 2. Read this system from the outside inward

A retrieval system converts a text query and candidate clips into vectors in a shared feature space. Ranking often uses cosine similarity: for unit vectors, this is simply their dot product. The retrieval index stores vectors, clip identifiers, and timestamps. It does not know whether the encoder actually saw the pixels. That is why a defect at the model boundary can contaminate a perfectly well-engineered index.

An embedding model is not merely a chat model asked to emit a list of numbers. Here the language model produces a hidden state at every input token. The embedding wrapper selects the last non-padding token's hidden state and normalizes it. It does not generate a textual answer. The checkpoint was trained for this embedding use; substituting an arbitrary instruct checkpoint would change the task even if the architecture and vector dimension matched.

The visual encoder first turns images or short video frame groups into patch features. The multimodal backbone places those features into the token sequence at designated image/video placeholder positions. Qwen3-VL also supplies intermediate visual features to language-model layers. The resulting hidden states therefore depend on both text and visual content when the data flow is correct.

```text
Registered clip and actual frame timestamps
                  |
                  v
       Decoder / deterministic sampler
                  |
          RGB frames + metadata
                  |
                  v
       Chat template and processor
          /                    \
  token IDs + mask       pixels + matching grids
          \                    /
           v                  v
          Embedding wrapper boundary   <--- repair here
                       |
                       v
          Shared multimodal backbone
          /                        \
  token embeddings           vision tower
          \                        /
           visual-token feature insertion
                       |
             language-model hidden states
                       |
             last valid token, then L2
                       |
               [batch, 2048] vectors
```

The current application baseline takes a different route: it embeds individual images, averages their unit vectors, and normalizes again. The arithmetic mean is invariant to permutation, so reversing those already computed frame vectors produces the same pooled result. Native video can encode temporal information, but merely enabling its input path does not guarantee useful opening-versus-closing discrimination.

## 3. Evidence ledger and scope of uncertainty

### 3.1 What is established locally

The source snapshots under `sources/` preserve the exact installed wrapper, backbone, loader, official reference script, and prior smoke JSON. `sources/manifest.json` records their source paths and SHA-256 hashes. Review these snapshots first; the active workbench may continue changing independently of this ticket.

In the wrapper snapshot, `Model.__call__` accepts `**kwargs`. It calls `_last_hidden_state` with `pixel_values`, `image_grid_thw`, and `video_grid_thw`, but no video pixels. The helper's signature also has no video pixel argument. Consequently a standard `pixel_values_videos` keyword cannot travel through this call chain.

The backbone snapshot is materially different. `get_input_embeddings` reads `pixel_values_videos` from kwargs and sends it to `vision_tower` with `video_grid_thw`. Image pixels use `image_grid_thw` and are inserted at image tokens; video pixels use the video grid and video tokens. These separate branches are the intended downstream interfaces for the repair.

The recorded image smoke used MLX 0.32.2, MLX-VLM 0.6.17, and Transformers 5.16.1. It returned finite 2,048-dimensional unit vectors, exact repetition for the same image, and different outputs for an adjacent frame and a black image. That supports the image path only. Its native-video entry records an explicit unsupported exception from the application adapter, not an executed test of the upstream video path.

### 3.2 What must still be established

We need a minimal processed video request, an observation of the actual failure mode, and proof that the missing tensor causes it. We also need to inspect the positional-state behavior under independent requests. The wrapper currently resets cached positions only when image pixels are present. Adding video to that condition is a plausible partial repair, but a subsequent text-only call could still inherit earlier state. Treat request isolation as a separately tested invariant.

The community checkpoint is pinned to `arthurcollet/Qwen3-VL-Embedding-2B-mlx-4bit`, revision `99b57b385f543a94c46d9f8e85a354de4c836b37`. Its metadata contains conflicting model-lineage cues. Preserve the artifact hashes and avoid claiming independently verified conversion provenance. Strict reference comparison should use a controlled conversion from the same official source checkpoint.

### 3.3 Upstream investigation

Related upstream work exists. PR #1642 fixed PIL frame-list preprocessing and PR #1048 added Qwen video processing infrastructure. Neither establishes that this embedding wrapper forwards video pixels correctly. No exact matching issue was found in the accessible search results; some GitHub search pages failed to load, so this is not an exhaustive absence claim.

References:

- [MLX-VLM embedding wrapper](https://github.com/Blaizzy/mlx-vlm/blob/main/mlx_vlm/models/qwen3_vl_embedding/qwen3_vl_embedding.py)
- [PIL video-input repair, PR 1642](https://github.com/Blaizzy/mlx-vlm/pull/1642)
- [Qwen video processors, PR 1048](https://github.com/Blaizzy/mlx-vlm/pull/1048)
- [Official Qwen embedding implementation](https://github.com/QwenLM/Qwen3-VL-Embedding/blob/main/src/models/qwen3_vl_embedding.py)

The links above are moving references. Before implementation, record the upstream checkout commit and verify whether the defect still exists at that revision. The archived local files are the fixed evidence for this ticket's diagnosis.

## 4. Tensor contracts an intern must understand

### 4.1 Text, placeholders, and masks

`input_ids` has shape `[B, L]`: batch size by token sequence length. A token ID can represent text, a role delimiter, or a visual placeholder. The presence of a video token only tells the model where a visual feature belongs. It does not contain the image itself.

`attention_mask` is ordinarily `[B, L]` with one for valid tokens and zero for padding. The embedding wrapper combines valid-token masks with a causal mask before running the language model. A causal mask controls which earlier positions a token can attend to. Correct masking is especially important in a batch of unequal-length inputs.

For sample `b`, the pooled position should be the greatest index `j` whose mask is one. It is not always `L - 1` and, with left padding, is not generally `sum(mask) - 1`. Explicitly reject an all-padding sample rather than letting an argmax accidentally choose a token.

```text
Right padded:  [A B C _ _]  mask [1 1 1 0 0] -> C
Left padded:   [_ _ A B C]  mask [0 0 1 1 1] -> C
All padding:   [_ _ _ _ _]  mask [0 0 0 0 0] -> reject
```

### 4.2 Pixel tensors and grids

`pixel_values` carries image patches. `pixel_values_videos` carries video patches. Their shapes are processor-dependent and should be logged rather than assumed to be `[B, T, C, H, W]`: by the time they reach the model, preprocessing may already have flattened and packed patches.

`image_grid_thw` and `video_grid_thw` describe temporal, height, and width patch grids. These are not the original pixel dimensions. Temporal patch grouping and spatial merging change the relationship between frame count, patch count, and language-model visual-token count. Use the processor and architecture configuration to derive consistency checks; do not hard-code a universal patch-count formula.

A video grid without its pixels is insufficient. Conversely, pixel data with the wrong grid can misalign shapes or visual-token insertion. For mixed media, both pairs must survive independently. Simply assigning `pixel_values = pixel_values_videos` is not the recommended repair for the inspected backbone: that routes video data through the image branch and associates it with the image grid and mask.

### 4.3 Position information and deep visual features

Qwen's multimodal rotary positional encoding, often called MRoPE, represents spatial/temporal placement as well as sequence position. `get_rope_index` constructs positional information from token IDs, grids, and masks. The language model also stores `_position_ids` and `_rope_deltas`. These private attributes are implementation details, not a stable application API.

Independent embedding calls should behave as independent requests. The safest design to investigate is to compute positions from the current request and avoid reusing prior-request positions. Prefer the current backbone's returned `InputEmbeddingsFeatures.position_ids` when its semantics match the embedding path; otherwise recompute from current inputs. Resetting private fields can be a minimal pinned-version tactic, but tests must demonstrate that it actually establishes isolation.

`visual_pos_masks` identifies visual token positions. `deepstack_visual_embeds` carries intermediate vision features consumed within language-model layers. A patch that forwards only the final visual features but loses these intermediate features could remain numerically wrong. Preserve the backbone's complete `InputEmbeddingsFeatures` result.

### 4.4 Output and timing

The last hidden state is `[B, L, D]`; the pooled embedding is `[B, D]`. For the selected 2B checkpoint, `D = 2048`. Normalize each vector with its L2 norm, reject nonfinite or near-zero vectors, and convert to float32 for storage and comparisons.

MLX is lazy: constructing an output can schedule work without completing it. Call `mx.eval` on the measured output before stopping a timer. Separate model loading, preprocessing, inference, and host conversion. Report cold and warm timings separately, together with MLX peak allocated memory and process RSS. These counters describe different memory views and should not be added together.

## 5. File and API navigation map

All repository paths in this document are relative to `/Users/manuel/code/wesen/2026-09-06--vision`, unless explicitly marked upstream. Archived source line numbers are stable within this ticket; installed package paths can disappear when an environment is rebuilt.

Archived files, relative to this ticket:

- `sources/mlx-vlm-0.6.17-embedding.py`: wrapper `_last_hidden_state` near line 30 and `__call__` near line 93. Locate the missing argument.
- `sources/mlx-vlm-0.6.17-backbone.py`: `get_input_embeddings` near line 44; separate video branch near line 92; positional result near line 123.
- `sources/mlx-vlm-0.6.17-encoder-loader.py`: `load_encoder_model` handles configuration overrides, quantization, and weight loading.
- `sources/official-qwen-reference.py`: official forward pass, processor preparation, and last-token pooling.
- `sources/existing-runtime-smoke.json`: historical image evidence and model/config hashes.

Application files, relative to the repository root:

- `workbench/src/video_workbench/embedding.py`: existing `FeatureSpace` and `QwenEmbedder`; `video` deliberately rejects unsupported native video.
- `workbench/src/video_workbench/media.py`: PTS-aware decoding and frame selection shared with search.
- `workbench/pyproject.toml` and `workbench/uv.lock`: dependency declarations and resolved environment.

Relevant installed upstream APIs are `mlx_vlm.embedding_loader.load_embedding_model`, `mlx_vlm.encoder_loader.load_encoder_model`, `mlx_vlm.utils.prepare_inputs`, the Qwen3-VL `Model.get_input_embeddings`, and `language_model.get_rope_index`. Do not confuse the high-level HTTP embedding endpoint with model-level support: a repaired model can still require separate server input-schema work. Server video support is outside this ticket's first acceptance gate.

The existing loader uses an in-memory `config_overrides` selection of `qwen3_vl_embedding`, because the checkpoint configuration names `qwen3_vl`. Keep this distinction explicit. Do not rewrite shared cached checkpoint files to make a loader select another class.

Proposed future application files are `workbench/src/video_workbench/native_video.py`, `workbench/tests/test_native_video_contract.py`, and a dedicated `tests/integration/` GPU suite. These are design targets, not files delivered by this documentation task. Prefer upstream tests in the MLX-VLM checkout for the wrapper repair, plus a small application contract test for the chosen dependency.

## 6. Reproduction before repair

Start in a separate checkout and environment so the active search work and its locked environment remain reproducible. Pin the faulty package version and record Python, macOS, MLX, Transformers, NumPy, and processor versions. Work from the archived source if upstream has already changed. Create a new implementation diary step before running a model experiment.

First reproduce the argument loss without downloading weights. A lightweight wrapper test can call the real public method on a harness whose hidden-state helper records kwargs and returns a tiny valid hidden state. Supply a sentinel as `pixel_values_videos`; assert that the helper received the same object. Add a second boundary test for helper-to-backbone forwarding using a stub backbone result and minimal language-model harness. The first failing test should identify the omission, rather than merely asserting the final vector differs.

```python
# Pseudocode: construct harnesses for the real methods.
video = sentinel_tensor()
harness = RecordingEmbeddingHarness()
call_real_embedding_method(
    harness,
    input_ids=valid_ids,
    attention_mask=valid_mask,
    pixel_values_videos=video,
    video_grid_thw=grid,
)
assert harness.hidden_call["pixel_values_videos"] is video
# Repeat at the helper -> get_input_embeddings boundary.
```

Next prepare a real short video request. Use two clips with identical frame count, dimensions, selected timestamps, prompt, and grids, but different pixels. A normal household clip and an all-black version of those same sampled frames make a controlled intervention. Do not compare unrelated video files whose frame counts or durations differ: changes in tokenization and timestamps would confound the result.

Instrument the vision tower or the backbone boundary in the test process. Record whether it was called for video, the received tensor shapes, hashes of input arrays, and the grid. Keep full pixel arrays and model weights out of textual logs. Try the unpatched model and record the exact exception or output. If it crashes because positional metadata and placeholders are inconsistent, that is a valid reproduction; do not rewrite the report to say silent corruption occurred.

For a content-sensitivity test, reuse one tokenized request and replace only its video-pixel tensor with a second compatible tensor. Also perform a separate end-to-end processor test. The first isolates forwarding and computation; the second checks that the processor, model, and application agree on the full contract.

## 7. Proposed repair

### 7.1 Forward the two modalities separately

The minimal production change adds an explicit optional `pixel_values_videos` argument to both wrapper methods and passes it unchanged into `get_input_embeddings`. Preserve the image arguments and grids. An explicit signature makes the supported input visible to reviewers and tools; do not rely on opaque `**kwargs` for a required modality.

```python
# Pseudocode, not a drop-in patch.
def __call__(self, input_ids, attention_mask=None,
             pixel_values=None, pixel_values_videos=None,
             image_grid_thw=None, video_grid_thw=None,
             **kwargs):
    hidden = self._last_hidden_state(
        input_ids=input_ids,
        attention_mask=attention_mask,
        pixel_values=pixel_values,
        pixel_values_videos=pixel_values_videos,
        image_grid_thw=image_grid_thw,
        video_grid_thw=video_grid_thw,
    )
    return pool_last_valid_and_normalize(hidden, attention_mask)
```

The helper must retain the same separation when it calls the backbone. Keep image and video grids paired with their respective pixels. Preserve masks, deep visual features, and all currently supported output fields. This ticket does not propose duplicating the vision encoder or replacing the language model.

### 7.2 Establish request-local position semantics

Position handling deserves a focused test and, if necessary, a separate commit. Read the current backbone's positional output, then choose a single authoritative source for current-request positions. Avoid computing valid positions in the backbone and discarding them in favor of a previous request's cache.

```python
# Pseudocode: exact integration follows pinned upstream APIs.
features = self.get_input_embeddings(
    input_ids=input_ids,
    pixel_values=pixel_values,
    pixel_values_videos=pixel_values_videos,
    image_grid_thw=image_grid_thw,
    video_grid_thw=video_grid_thw,
    mask=attention_mask,
)
positions = positions_for_this_request(features, input_ids,
                                      attention_mask, grids)
hidden = language_model.model(
    input_ids,
    inputs_embeds=features.inputs_embeds,
    position_ids=positions,
    mask=current_causal_padding_mask,
    cache=None,
    visual_pos_masks=features.visual_pos_masks,
    deepstack_visual_embeds=features.deepstack_visual_embeds,
)
```

The decision function above is explanatory, not an API to invent mechanically. If the backbone's positions have the correct shape and padding semantics, use them. If the embedding wrapper must compute them differently, explain the difference in a test and derive them solely from current inputs. Preserve generation behavior by making the change in the embedding path unless shared-code evidence requires otherwise.

### 7.3 Reject invalid contracts clearly

At the application boundary, reject empty videos, zero selected frames, invalid timestamp order, and missing pixel/grid pairs. Enforce a bounded frame and token budget before inference. Do not silently truncate away visual placeholders while retaining the full pixel tensor. For an unsupported batching or mixed-modality configuration, return a clear error and document the limit.

Do not solve this by swallowing all exceptions and embedding a fallback string. That would allow a failed video request to enter the same index as valid video vectors. Errors should prevent cache publication.

## 8. Validation ladder

### 8.1 Fast structural and regression tests

The CPU-friendly contract suite should establish the two forwarding boundaries using sentinel objects, retain the image path, and cover invalid input combinations. Add pooling tests for left padding, right padding, a single token, and all padding. These tests should expose meaningful behavior rather than duplicate the implementation's syntax.

The GPU integration suite should include:

- Text-only, one image, a short video, and text plus video.
- A mixed image/video request where both branches are observed, if supported by the pinned processor.
- Original video pixels versus black or shuffled-content pixels with identical metadata.
- Repeated input on the same model instance.
- Video A, text B, video A again; compare A with a fresh instance.
- Image, video, and text requests in different orders.
- Unequal-length padded batches if batching is supported; otherwise a verified explicit rejection.
- Single-frame and odd-frame inputs to document temporal-padding behavior.

Frame reversal is an exploratory temporal test, not a guaranteed model acceptance threshold. Use asymmetric sequences and record the change. A model may represent two directions similarly even when the runtime is correct. Passing pixel-dependence and reference-parity tests is what establishes the repair; action discrimination belongs to evaluation.

### 8.2 Reference comparison without confounding quantization

Use the official Qwen implementation as the computational reference, but inspect its preprocessing and error paths rather than assuming every call is correct. The archived reference chooses CUDA or CPU. On this Mac, a small CPU reference run is the conservative starting point. MPS acceleration would need an explicit device adaptation and its own validation; CUDA-specific FlashAttention settings are not a Mac recipe.

For strict parity, use the same source checkpoint and a controlled unquantized MLX conversion. Compare the processor outputs before comparing embeddings: token IDs and masks, grids, timestamps, resized frames, pixel normalization, and patch layout must agree. If the processors use different internal layouts, compare after a documented layout transformation instead of expecting raw arrays to match blindly.

Then compare hidden-state pooling and final vectors. Report maximum absolute error, cosine similarity, norm, and pairwise similarity-matrix differences. An initial proposed target for matching float32 paths is cosine at least 0.999 with small absolute error; this is a review starting point, not a measured guarantee. Establish the actual precision-dependent tolerance on a predeclared fixture and justify changes with intermediate comparisons.

Only after the high-precision implementation is aligned should the 4-bit checkpoint be evaluated. For quantization, compare ranking stability and downstream retrieval alongside numerical differences. Do not demand bitwise equality between independent floating-point backends or mistake 4-bit approximation error for a forwarding bug.

### 8.3 Fixture and measurement design

Freeze a small development-only fixture before tuning. Include distinctly different scenes, a blank visual intervention, mixed media, and paired temporal sequences. Use VirtualHome train/development episodes for household examples. Do not repeatedly inspect the search project's held-out test split while debugging the runtime.

For each case, save a record with:

- Case ID and input media hashes; split and episode ID if applicable.
- Selected actual PTS values, frame count, resize policy, and processor arguments.
- Model revision, conversion settings, source hashes, package lock, and code commit.
- Tensor shapes, valid-token counts, grids, and vision-call observations.
- Output norms and hashes, comparison metrics, cold/warm timings, and memory counters.
- Pass/fail status, exact exception when present, and the tolerance policy used.

Store a small frame contact sheet and a readable comparison chart in the ticket report. Caption them as fixture evidence or measured results. Screenshots are useful for review but cannot replace the machine-readable measurements.

## 9. Application integration and cache migration

The existing `QwenEmbedder.video` deliberately raises an unsupported error. Replace that behavior only after the native-video gates pass. Expose the runtime mode explicitly: `pooled_images` and `native_video` are different feature spaces even when both return 2,048 floats.

The native feature-space record must include checkpoint and artifact identity, runtime patch/revision, processor and prompt identity, sampling policy, frame budget, resolution, temporal padding, pooling, output dtype, normalization, and relevant package versions. Frame selection belongs to a reproducible policy; individual clip records additionally contain the actual selected timestamps and source hash.

```text
Existing pooled-image space ---> existing immutable cache

Verified native-video space ---> NEW cache / index manifest
                                      |
                          explicit native query encoder
                                      |
                             compatible-space search
```

Text queries must be encoded with the matching native-space configuration, including prompt and normalization, even if their numerical encoding currently matches the pooled baseline. Compatibility should be an explicit contract, not inferred from equal dimensions. A changed encoder implementation cannot silently reuse old vectors.

Keep publication atomic: a failed inference leaves no valid cache entry. Persist the full feature-space identity before publishing an index manifest. Search should reject a query/index mismatch. Rollback means selecting the previous named index and runtime mode, not deleting or relabelling existing vectors.

This repair does not require regenerating the VirtualHome corpus. It requires re-encoding the selected clips under the new feature space after validation. The existing decoder should supply frames with their PTS; do not introduce a second nominal-FPS sampler that changes evidence timing.

## 10. Implementation phases and review checkpoints

### P0: Pin evidence and reproduce

Create an isolated upstream checkout, capture its revision and environment, and reproduce the two argument boundaries. Prepare a minimal real-video fixture and record whether the faulty path crashes or returns an output. Check current upstream issues again. The checkpoint is a failing test with a precise explanation, not a broad claim that video support is broken everywhere.

Suggested commit: `test(qwen3-vl-embedding): reproduce dropped video pixels`.

### P1: Repair forwarding

Add the explicit video-pixel arguments and forward them through both wrapper layers. Test image-only and mixed inputs. Preserve output shape and normalization. Keep the patch small enough that a reviewer can follow every new argument from public call to vision encoder.

Suggested commit: `fix(qwen3-vl-embedding): forward native video pixels`.

### P2: Validate positions and independent requests

Add request-order and padding regressions. If cached positions leak, fix request-local position selection in a separate commit and explain why the generation path remains valid. Verify video-to-text and text-to-video transitions on a reused model instance.

Suggested commit: `fix(qwen3-vl-embedding): isolate embedding position state` only if the tests establish that repair is needed.

### P3: Establish real-model parity and cost

Run controlled pixel interventions, then unquantized reference alignment and the 4-bit comparison. Produce a JSON report and frame/contact-sheet evidence. Record failed configurations rather than omitting them from averages. If parity fails, locate the first divergent stage: sampling, processor, vision features, insertion, positions, hidden states, or pooling.

Suggested commit: `test(embeddings): add native-video parity fixtures and report`.

### P4: Integrate the verified runtime

Pin the repaired dependency or maintain a small reviewed patch until an upstream release exists. Implement the application native-video adapter and new feature-space identity. Test cache incompatibility and failed-inference publication behavior. Re-encode a development subset before a full index rebuild.

Suggested commit: `feat(workbench): enable verified native video embeddings`.

### P5: Handoff and upstream contribution

Write the final incident-style report: trigger, observed failure, root cause, patch, test evidence, remaining limits, and reproduction command. Prepare an upstream issue/PR body and minimal fixture without bundling large weights. Posting upstream is a separate action from preparing the ticket; this documentation request does not submit anything publicly.

Close the repair ticket only after the required native-video gates and integration checks are met. A completed guide or successful image smoke does not close implementation work.

## 11. Alternatives and decision rules

The separate MLX-Embeddings package is worth inspecting, but the retrieved implementation aliases video pixels to image pixels before invoking a shared backbone. That could interact badly with newer separate modality branches. Treat it as a candidate requiring the same forwarding and reference tests, not a drop-in escape from validation. Its source is at [MLX-Embeddings Qwen model](https://github.com/Blaizzy/mlx-embeddings/blob/main/mlx_embeddings/models/qwen3_vl/model.py).

The official PyTorch implementation provides a reference with explicit video forwarding. A small CPU comparison is useful even if too slow for production indexing. A separate MPS experiment could establish Apple GPU viability, but it should not delay obtaining a minimal reference result with supported settings.

A community [llama.cpp/Metal port](https://github.com/ceveyne/qwen3-vl-embedding) reports validation for text and image paths. That evidence does not establish native-video support. It becomes an alternative only after an equivalent video fixture and parity check pass.

Continue using pooled images as an explicitly named baseline while the repair is unresolved. Compare it with native video later to learn whether temporal encoding actually improves household retrieval. Do not redefine successful repair as beating pooled images on four queries: runtime correctness and retrieval quality are distinct acceptance questions.

## 12. Intern's first working session

Read sections 2–4, then trace the archived wrapper and backbone with a pencil or debugger. Explain to a reviewer why token placeholders cannot substitute for pixels, and why image/video grids must remain paired with their tensors. Read the existing workbench adapter to understand the explicit unsupported behavior and feature-space contract.

Start with a weight-free regression that fails on the archived behavior. Resist the temptation to download multiple models or rebuild a whole index before proving the boundary failure. Once the test fails for the intended reason, implement the smallest forwarding change, rerun the fast suite, and proceed to actual video inference.

Useful existing commands, run from the repository root:

```sh
# Inspect the active application dependency and mode.
rg -n 'mlx-vlm|transformers' workbench/uv.lock
rg -n 'FeatureSpace|def video|position_ids' \
  workbench/src/video_workbench/embedding.py

# Read the fixed source evidence archived with this ticket.
rg -n 'pixel_values|video_grid|position_ids' \
  ttmp/2026/09/06/MLX-VIDEO-FIX-001*/sources/*.py
```

Proposed commands after the relevant tests and modules are implemented:

```sh
pytest workbench/tests/test_native_video_contract.py -q
pytest workbench/tests/integration/test_native_video.py -q
```

The final review should answer four questions with evidence: Did the video pixels reach the encoder? Did independent requests remain independent? Did the implementation agree with a controlled reference? Did the application give the changed behavior a new, reproducible feature space? Those answers form the handoff from this repair to the search project.
