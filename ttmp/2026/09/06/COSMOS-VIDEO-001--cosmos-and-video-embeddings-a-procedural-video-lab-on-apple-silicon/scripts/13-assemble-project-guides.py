#!/usr/bin/env python3
"""Apply authored guide drafts and task breakdowns to existing child tickets.

Drafts are named TICKET-guide.md in --draft-dir. Final Markdown is the source
of truth after assembly; do not rerun against subsequently edited tickets.
"""
import argparse,json,os,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
repo=Path.cwd()
parser=argparse.ArgumentParser(); parser.add_argument('--draft-dir',type=Path,required=True)
args=parser.parse_args()
records=json.loads((ROOT/'various/project-tickets.json').read_text())
TASKS={
'COSMOS-EMBED-001':[
('E1 Environment and provenance',['Create isolated workbench environment and record Python/runtime/hardware versions.','Resolve model and conversion to immutable revisions; record weight and processor hashes.','Inspect installed embedding entry points and document actual signatures.']),
('E2 Contracts and sampling',['Implement FeatureSpace, SampledClip, and vector-validation contracts.','Implement deterministic PTS sampling with irregular/duplicate/truncated fixtures.','Verify cache identity changes for every preprocessing or model-space change.']),
('E3 Adapter and smoke',['Implement text, image, and native-video methods without silent fallback.','Implement separately named frame-pooled mode and space identity.','Audit prepared frame count and original/reversed/repeated-frame controls.','Record capability failures, finite dimensions, normalization, and repeatability.']),
('E4 Measurement and handoff',['Benchmark cold and repeated warm runs with materialization and bounded frame counts.','Record preprocessing/inference/total time, memory, and real-time factor.','Publish selected defaults, capability matrix, cache fixture, and reproduction command.'])],
'VIDEO-SEARCH-001':[
('S1 Registry',['Implement generic manifest ingest and SQLite episode migration.','Verify source hashes, group splits, duplicate IDs, and PTS metadata.','Add inspect command and corrupt/missing/variable-rate fixtures.']),
('S2 Cache and index',['Implement deterministic windows and selected-PTS metadata.','Implement atomic array publication and resumable index manifests.','Test crash recovery and rejection of incompatible spaces.']),
('S3 Search and viewer',['Implement exact cosine ranking, stable ties, and split filtering.','Implement typed search API and registered-ID-only video access.','Build minimal query/results/player UI and verify interval seeking.']),
('S4 Evaluation',['Freeze queries, weak-interior relevance, and split policy.','Run bounded development window/FPS sweep and freeze selected configuration.','Run final test partition with Success@K, interval Recall@K, and resource metrics.','Publish reproducible index/evaluation report and shared decoder/cache handoff.'])],
'VIDEO-STATE-001':[
('P1 Labels',['Define entity/property/visibility/unknown annotation schema.','Build source-hashed reviewed RGB subset with grouped splits.','Record class counts, unresolved labels, and reviewer limitations.']),
('P2 Baselines',['Implement text-hypothesis margins and frozen-feature linear head.','Add feature-space/entity mismatch and hand-computed score tests.','Export predictions with evidence, availability, unknown reasons, and producer IDs.']),
('P3 Context and calibration',['Freeze generic/correct/misleading/context-only conditions.','Fit weights on train and select calibration/thresholds on development only.','Report risk/coverage, visible-state F1, and false certainty with raw counts.']),
('P4 Timeline and handoff',['Build observation timeline with gaps and evidence playback.','Export StateObservation contract for temporal memory.','Report transition metrics only if reviewed boundary labels are available.','Publish ablation table and supported/unsupported state distinctions.'])],
'VIDEO-TEMPORAL-001':[
('T1 Data and baseline',['Implement timestamped feature sequences, validity, and weak-label masks.','Create oracle omission/repetition/gap fixtures and linear baseline.','Verify feature-index to source-time mapping.']),
('T2 Classical models',['Adapt reviewed HMM/filter/smoother and HSMM contracts.','Implement timestamp-based hysteresis and tiny exhaustive decoder tests.','Compare constrained and unconstrained paths; verify errors are preserved.']),
('T3 Causal TCN',['Implement small frozen-feature TCN and training/checkpoint metadata.','Test future perturbation, chunk equivalence, masking, and feature availability.','Compare seed runs and development-selected settings against linear baseline.']),
('T4 Memory',['Implement append-only facts, supersession/retraction, and SQLite migration.','Implement as-of state queries with conflict, coverage, and expiry rules.','Test late facts, duplicate ingestion, restart, and no future leakage.','Publish separate offline/causal metrics and rule-engine handoff.'])],
'COSMOS-VERIFY-001':[
('V1 Runtime gate',['Pin Cosmos conversion and comparable Qwen checkpoint provenance.','Inspect installed load/template/generate interfaces and run image load smoke.','Record actual frame/token/memory constraints and failed capabilities.']),
('V2 Evidence adapter',['Define bounded VerifyRequest/Result and evidence packet schemas.','Implement image, multi-image, and supported native-video modes distinctly.','Enforce horizon/size/deadline and subprocess timeout/restart behavior.']),
('V3 Output validation',['Implement strict JSON parsing and answer/status separation.','Reject missing/invented citations, wrong entities, and out-of-scope times.','Preserve raw responses and test malformed/timeout fixtures without models.']),
('V4 Comparison',['Freeze reviewed question set and matched evidence/prompt/budget conditions.','Run both candidates sequentially and report factual support separately from schema validity.','Publish accuracy/abstention/failure/latency/memory table with raw counts.','Hand off versioned adapter and accepted capabilities to rule investigation.'])],
'VIDEO-RULES-001':[
('R1 AST and oracle logic',['Define typed operators, entity bindings, units, and bounded schema validation.','Implement three-valued logic, missing-trigger applicability, and interval semantics.','Add hand-derived threshold/equality/overlap/wrong-entity oracle tests.']),
('R2 Coverage and store',['Implement coverage union/gap checks and uncertain duration bounds.','Integrate as-of fact views and explicit supersession.','Test late revisions, restart equivalence, and explanations for unknown.']),
('R3 Investigation',['Implement finite call/frame/token/deadline budgets and request fingerprints.','Enforce evidence horizon and strict verifier proposals.','Append auditable fact/decision revisions and test disagreement/timeout/exhaustion.']),
('R4 Evaluation',['Freeze rule/candidate/matching policies and versioned prompts.','Compare oracle, predicted/no-verifier, Qwen, and Cosmos conditions.','Include missed candidates in end-to-end recall and report unknown/cost/latency.','Keep endpoint-world-truth diagnostics separate from reviewed temporal evaluation.'])],
'VIDEO-REPLAY-001':[
('W1 Clock and broker',['Implement monotonic replay/source time mapping and packet horizon.','Test delayed/future frames and precomputed-feature availability.']),
('W2 Scheduler',['Implement bounded queues, mandatory/optional priorities, and deadlines.','Emit explicit gaps for dropped/deferred work and measure queue delay.','Prove bounded behavior with a deliberately slower-than-source worker.']),
('W3 Lifecycle and recovery',['Define stable incident identity, workflow state, and immutable decision revisions.','Implement transactional result/outbox and idempotent publication.','Test duplicate events and crash recovery around commits and cursor updates.']),
('W4 Viewer',['Implement bounded registered-ID API and reuse search/video contracts.','Build video/state/event/incident timeline and revision evidence panel.','Verify as-of history, seeking, and absence of client-side rule evaluation.']),
('W5 Evaluation',['Freeze staged real-video collection/review protocol and held-out set.','Run declared sustained replay and separate looped capacity stress test.','Report false alerts/hour, misses, unknowns, latency, queues, coverage, and memory.','Publish real-video transfer failures and measured next-step capacity decision.'])],
'VIDEO-CORPUS-001':[
('C1 Preserve and probe',['Verify immutable v1 inventory and create separate expansion config/output.','Probe additional VirtualHome scenes, target bindings, and camera visibility.','Record supported/unsupported scene/action/view capabilities.']),
('C2 Calibrate',['Export native-resolution transition neighborhoods and review schema.','Review repeated OPEN/CLOSE cases for both appliances and multiple views.','Compare raw action, graph state, and visual uncertainty bounds.','Publish per-subset timing/visibility eligibility without global false guarantees.']),
('C3 Expand',['Plan at most 48 initial new episodes with explicit variation factors.','Record lineage, transforms, seeds, duration controls, and preassigned group splits.','Generate only verified scenes; retain attempts/failures and immutable provenance.']),
('C4 Audit and handoff',['Validate all media and annotation/source-hash compatibility.','Audit cross-split lineage plus exact and perceptual duplicate diagnostics.','Inspect every scenario/view family and full calibration transition neighborhoods.','Publish model-safe inputs and separately scoped state/action/rule labels.'])]}
common='''
## Shared system contract and reading map

This guide is a design for future implementation. Existing evidence is the root `src/virtualhome_corpus/` package and the validated assets under `output/virtualhome-corpus/home-v1`. Proposed application modules live under `workbench/src/video_workbench/`, preserving the umbrella guide's layout. Proposed APIs and pseudocode are not installed commands or claims of completed model behavior.

Use integer microseconds, half-open event intervals, opaque episode IDs, and source/producer hashes. Keep event time distinct from evidence/result availability and durable commitment. Keep model-safe inputs separate from evaluator labels. A model-space hash must identify preprocessing as well as weights. Unknown evidence remains unknown until a declared policy and new evidence justify a revision.

The existing corpus is a within-scene starter set, with weak action interiors and endpoint world truth. Exact temporal and dense visual-state metrics require reviewed labels; larger datasets do not remove that requirement. Model/runtime references were checked on 2026-09-06. Pin actual installed versions during implementation rather than assuming a mutable documentation page matches the environment.
'''
for r in records:
    guide=Path(r['guide']);front=guide.read_text().split('---',2)[1]
    front=front.replace('Summary: ""','Summary: '+json.dumps(r['scope']))
    text=(args.draft_dir/(r['ticket']+'-guide.md')).read_text()
    refs=[('Existing generator contracts',repo/'src/virtualhome_corpus/core.py','lines 55, 102, and 167: planning, weak intervals, endpoint truth'),('Existing rendering/export lifecycle',repo/'src/virtualhome_corpus/runner.py','lines 54, 125, 202, and 228: annotation quality, generation, validation, indices'),('Checked v1 experiment',repo/'configs/virtualhome-household-v1.json','families, variants, groups, and camera'),('Corpus operational playbook',repo/'docs/playbook/virtualhome-corpus.md','generation, resume, validation, and gallery'),('Validated corpus report',ROOT/'design-doc/03-virtualhome-household-corpus-design-and-generation-report.md','observed results and label limitations')]
    if r['ticket']=='VIDEO-TEMPORAL-001':
        refs += [('Sequence teaching lab',ROOT/'sources/procedural_video_labs/sequence_lab.py','forward, smooth, viterbi, hsmm_viterbi'),('Neural teaching lab',ROOT/'sources/procedural_video_labs/neural_lab.py','CausalMultiStageTCN and segmentation_loss')]
    links='\n'.join(f'- [{label}]({os.path.relpath(path,guide.parent)}): {note}.' for label,path,note in refs)
    deps='\n'.join(f'- [{d}]({os.path.relpath(Path(next(x["path"] for x in records if x["ticket"]==d))/"index.md",guide.parent)})' for d in r['dependencies']) or '- No prerequisite model implementation; use the existing corpus and shared schema agreements.'
    guide.write_text('---'+front+'---\n\n'+text+common+'\n### Existing file references\n\n'+links+'\n\n### Ticket dependencies\n\n'+deps+'\n')
    path=Path(r['path'])
    tasks='# Tasks\n\n## Design and delivery\n\n- [x] Establish project scope, dependencies, and VirtualHome data policy.\n- [x] Write detailed intern analysis/design/implementation guide.\n- [ ] Validate technical contracts and rendered PDF.\n- [ ] Upload this ticket guide to reMarkable and record receipt.\n'
    for phase,items in TASKS[r['ticket']]:
        tasks+='\n## '+phase+'\n\n'+'\n'.join('- [ ] '+item for item in items)+'\n'
    (path/'tasks.md').write_text(tasks)
    index=path/'index.md';s=index.read_text().replace('Design preparation is in progress; implementation has not started.','The detailed design and implementation breakdown are written. Technical/PDF review and delivery are pending; application implementation has not started.')
    parent_link=os.path.relpath(ROOT/'index.md',path)
    s=s.replace('Parent: COSMOS-VIDEO-001.',f'Parent: [COSMOS-VIDEO-001]({parent_link}).')
    index.write_text(s)
    r['word_count']=len(re.findall(r'\b\S+\b',guide.read_text()))
(ROOT/'various/project-tickets.json').write_text(json.dumps(records,indent=2)+'\n')
print('\n'.join(f'{r["ticket"]}: {r["word_count"]} words' for r in records))
