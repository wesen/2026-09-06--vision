# Tasks

## Design and delivery

- [x] Establish project scope, dependencies, and VirtualHome data policy.
- [x] Write detailed intern analysis/design/implementation guide.
- [x] Validate technical contracts and rendered PDF.
- [x] Upload this ticket guide to reMarkable and record receipt.

## V1 Runtime gate

- [x] Pin Cosmos conversion and comparable Qwen checkpoint provenance.
- [x] Inspect installed load/template/generate interfaces and run image load smoke.
- [x] Record actual frame/token/memory constraints and failed capabilities.

## V2 Evidence adapter

- [x] Define bounded VerifyRequest/Result and evidence packet schemas.
- [ ] Implement image, multi-image, and supported native-video modes distinctly.
- [x] Enforce horizon/size/deadline and subprocess timeout/restart behavior.

## V3 Output validation

- [x] Implement strict JSON parsing and answer/status separation.
- [x] Reject missing/invented citations, wrong entities, and out-of-scope times.
- [x] Preserve raw responses and test malformed/timeout fixtures without models.

## V4 Comparison

- [x] Freeze reviewed question set and matched evidence/prompt/budget conditions.
- [ ] Run both candidates sequentially and report factual support separately from schema validity.
- [x] Publish accuracy/abstention/failure/latency/memory table with raw counts.
- [x] Hand off versioned adapter and accepted capabilities to rule investigation.

## V1 follow-up — 8B runtime gate

- [x] Pin Qwen 8-bit conversion and official Cosmos 8B source; resolve authenticated access.
- [x] Convert Cosmos locally to 8-bit MLX and record timing, settings, and output hashes.
- [x] Run both 8B candidates on the unchanged development image request and preserve separate raw results.
- [x] Publish matched runtime report and visual audit; retain strict Cosmos JSON failure.

The historical 8B runtime smoke is complete. Subsequent work below accepts the bounded single-image implementation; multi-image/video and broader semantic acceptance remain open.

## Reviewed rerun and practical JSON fences

- [x] Freeze all 48 existing reviewed development/test point-state cases and run four pinned 2B/8B candidates (192 responses).
- [x] Retrain native temporal heads from the accepted 792-window feature cache and check reproducibility; targeted 18-test regression selection passed.
- [x] Inspect sanitize and implement traced outer-fence normalization with 11 output-boundary smoke cases.
- [x] Reparse saved responses separately; report strict versus normalized results and preserve visual evidence.
- [x] Later: evaluate visibility-aware abstention and a host-owned request envelope on a separately planned development/evaluation protocol.

These point-state comparisons do not complete multi-image/native-video, temporal-insufficiency, full rationale-support, or end-to-end rule evaluation acceptance.
- [ ] Cosmos tracking item (C1–C4 below): compare direct versus explicit NVIDIA reasoning configuration on development; freeze prompt, final-answer parser, sampling controls, larger budget and deadline before fresh test evaluation. <!-- t:ln02 -->

Accepted V2–V4 checkmarks above cover the bounded single-image contract and reviewed point-state comparison only. Multi-image/native-video support, full rationale-support scoring, reliable abstention, and end-to-end rule recall remain open. See references 05 and 06.
- [ ] Qwen follow-up (implemented through R1–R4 below): compare explicit Instruct decoding and prompted step-by-step reasoning against the greedy direct baseline; record seed, penalty scope and processed image dimensions. <!-- t:9y1n -->
- [ ] Qwen follow-up: pin and smoke-test a separate 8B Thinking checkpoint/conversion; freeze its template, final-answer contract, budget and deadline before a fresh reviewed test comparison. <!-- t:fk2c -->
- [ ] Later: evaluate approved full-frame plus target crop for small visible objects, preserving crop transforms and aliases; keep occluded cases unknown and multi-image capability explicitly gated. <!-- t:ovsi -->

## Prompted reasoning implementation — design 02

The existing broad Qwen/Cosmos follow-ups remain tracking items; R1–R5 below are the concrete implementation sequence. Prompted reasoning uses the current Instruct weights. The separate Thinking checkpoint follows afterward.

- [ ] R1: implement validated generation profiles and revised bounded 4096-token contract, raw/final limits, explicit MLX seed/sampling and processed-image provenance (design 02). <!-- t:vnez -->
- [ ] R2: add prompted step-by-step reasoning to current Qwen Instruct; parse one declared reasoning block plus final JSON, preserving raw output and existing host/citation validation. <!-- t:slzs -->
- [ ] R3: pilot budgets on development, freeze fresh reviewed dev/test episodes and four Qwen Instruct arms: direct/reasoning crossed with greedy/sampled decoding; keep three predefined sampled seeds. <!-- t:pmfe -->
- [ ] R4: run frozen development selection and untouched test/control comparison; report abstention, unsupported certainty, final-rationale support, failures and resource costs with visual case galleries. <!-- t:ker0 -->
- [ ] R5: smoke-test parser/budget/process failure boundaries at feature completion, validate one live selected-style RULES handoff, and publish evidence/diary before separate Cosmos or Qwen Thinking comparisons. <!-- t:ng4c -->

## Cosmos Reason2 experiment — design 03

Reuse shared R1–R2 before C1–C4. Freeze both model protocols before examining a shared test set; otherwise collect fresh Cosmos test cases.
- [ ] C1: pin the existing Cosmos 8B conversion and add four direct/reasoning x greedy/reasoning-sampling profiles with common minimal system prompt and preserved media-first template. <!-- t:5ce4 -->
- [ ] C2: smoke the explicit Cosmos reasoning envelope and 4096-token/120-second budget using the shared adapter; freeze profiles, prompts, seeds and reviewed cases before evaluation. <!-- t:b87k -->
- [ ] C3: run Cosmos development selection and untouched selected/control test comparison; prevent Qwen test feedback from tuning Cosmos; report uncertainty, rationale support, failures and runtime. <!-- t:tu95 -->
- [ ] C4: retain annotated case galleries and raw outputs, run one live selected-style Cosmos RULES handoff, and publish measured report/diary with explicit semantic acceptance limits. <!-- t:l9u8 -->
