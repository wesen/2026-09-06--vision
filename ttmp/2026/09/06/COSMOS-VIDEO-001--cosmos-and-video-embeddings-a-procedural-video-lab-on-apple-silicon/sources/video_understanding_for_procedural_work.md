---
title: "Video Understanding for Procedural Work"
subtitle: "Temporal Action Segmentation, Procedure State Estimation, and Error Detection"
author: "A textbook developed from the supplied research"
date: "First edition · September 2026"
lang: en-US
---

# Preface {#preface}

A camera can show that a worker is tightening a fastener without showing that the assembly is correct. The fastener might have been inserted into the wrong location, an alignment step might be missing, or the tool might not provide the required torque. Recognizing the motion is one inference problem. Establishing what that motion means within a procedure is another. This book develops the models, data structures, experiments, and software boundaries needed to keep those questions distinct while connecting their answers.

The organizing research is *Building a Video-Recognition Pipeline for Stepwise Worker Actions and Error Detection*, supplied with this assignment. Its central recommendation is a hybrid system: short-window video representations, a temporal convolutional network or local Transformer, an explicit procedure-and-duration model, a typed error engine, and optional vision-language verification. NVIDIA Video Search and Summarization, abbreviated VSS, supplies a possible video and analytics infrastructure rather than a ready-made worker-step classifier. Those are the book's starting commitments, not conclusions from an experiment performed for this edition. [S]

The book is intended for engineers and researchers who can read Python and are willing to work through basic algebra. The probability and linear-algebra concepts needed for the main algorithms are introduced before those algorithms. A reader already comfortable with them can use Chapter 4 as a notation reference. The software chapters assume familiarity with arrays, functions, and supervised training, but explain tensor shapes and state ownership explicitly.

## What this edition contains

The six-part reading map organizes the material from problem definition and representations through sequence models, procedural reasoning, systems, and laboratories. Each part makes the assumptions needed by the next part explicit.

The appendices collect notation, a glossary, solutions to the chapter exercises, a source-and-qualification map, and references. The Markdown and PDF editions contain the same teaching material. Text diagrams remain readable without an external renderer. Mathematical expressions use conventional TeX notation in Markdown and are typeset in the PDF. The companion Python files reproduce the central numerical traces; no camera, proprietary dataset, VSS deployment, or GPU is required for the small tests.

## Evidence and scope

Three kinds of material are distinguished throughout. **Research basis** refers to claims and recommendations in the supplied report, cited as [S] with its section name. **Textbook constructions** are new explanations, worked examples, synthetic data, code, and exercises developed to teach that material. **Implementation qualifications** are explicitly identified additions that make an underspecified point executable or expose a consequential assumption. Appendix D lists these qualifications so that a reader can distinguish the report's framing from this edition's elaboration.

The research does not provide an industrial training dataset, measured camera performance, a trained worker-action model, a complete procedure specification, or validated operational thresholds. Consequently, this book does not invent those assets or report benchmark results for them. All worked timings, probabilities, and example thresholds are illustrative unless identified otherwise. Passing a laboratory test establishes an algorithmic property on the tested input; it does not establish factory performance.

The report contains citation tokens from an earlier research session and links to earlier purported textbook files. Those tokens do not contain a recoverable bibliography, and those links are not evidence that files exist in this edition. They have not been carried forward. Instead, the references name the report itself and independently checked primary papers and official documentation for the named methods and products.

Vendor references were checked on **4 September 2026**. The deployment discussion deliberately uses the **VSS 3.1.0 documentation snapshot** where available, with a separately identified current secure-deployment page. It does not claim that 3.1.0 is the newest release. Service names, defaults, model configurations, and message formats must be checked against the version actually deployed. The distinction between a source recommendation and a vendor contract is particularly important in Chapters 6 and 17.

## A recurring assembly example

The running procedure attaches a bracket with one fastener. A simplified valid execution is:

```text
pick bracket -> align bracket -> insert fastener
             -> tighten fastener -> inspect assembly
```

The procedure permits a specified rework path after inspection. A worker may pause, put a tool down, or temporarily leave the camera view without completing a new assembly step. Later examples use shortened state names such as `align`, `insert`, and `tighten`; those names refer to this procedure unless stated otherwise. The example is small enough to enumerate paths by hand but contains the same separation between motion, object state, duration, and procedural validity that a larger system requires.

## How to study the book

For a first implementation, read Chapters 1–11, then Chapters 13–14 and 18–21. This route leads from labels and embeddings to a causal TCN and explicit-duration decoder without requiring a Transformer. Read Chapter 12 when an experiment motivates richer temporal interaction, not simply because attention is available.

For production design, read the entire sequence. The mathematical chapters explain what the services are estimating; the streaming chapters explain when those estimates become available; the evaluation chapters explain what evidence supports deployment. Skipping any of those questions can produce a system that works on stored clips yet behaves differently on a live workstation.

Every chapter ends with three exercises. Some ask for a calculation, some for a counterexample, and some for a small implementation change. Solutions are provided in Appendix C. Use the calculations to verify understanding, then use the counterexamples to identify conditions under which the model should decline to make a strong claim.

# Contents and reading map {#reading-map}

| Part | Chapters | Central question |
|:--|:--|:--|
| I. Problem and evidence | 1–3 | What is observed, labeled, and judged? |
| II. Representations | 4–6 | What information reaches the temporal model? |
| III. Sequence models | 7–12 | How are time, order, and duration modeled? |
| IV. Procedural reasoning | 13–15 | When does an observed action imply an error? |
| V. Systems and experiments | 16–19 | Does the system work under deployment conditions? |
| VI. Laboratories and capstone | 20–22 | Can the design be executed, inspected, and challenged? |

1. [From video to procedural decisions](#ch01)
2. [Labels, procedure graphs, and state](#ch02)
3. [Building the dataset](#ch03)
4. [Mathematical tools for temporal inference](#ch04)
5. [Embeddings and representation learning](#ch05)
6. [Sampling, perception, and feature fusion](#ch06)
7. [Hidden Markov models](#ch07)
8. [Forward, backward, and Viterbi inference](#ch08)
9. [Explicit duration with hidden semi-Markov models](#ch09)
10. [Temporal convolutional networks](#ch10)
11. [Multi-stage refinement and training losses](#ch11)
12. [Transformers and multiresolution temporal models](#ch12)
13. [Hybrid recognition and procedure decoding](#ch13)
14. [Typed errors and incident state](#ch14)
15. [Vision-language verification](#ch15)
16. [Streaming inference and latency](#ch16)
17. [NVIDIA VSS and model serving](#ch17)
18. [Evaluation and calibration](#ch18)
19. [An experimental program that answers questions](#ch19)
20. [Laboratory: sequence inference and error evidence](#ch20)
21. [Laboratory: a causal multi-stage TCN](#ch21)
22. [Capstone: from replay to a monitored pilot](#ch22)

[Appendix A: Notation](#appendix-a) · [Appendix B: Glossary](#appendix-b) · [Appendix C: Exercise solutions](#appendix-c) · [Appendix D: Source map and implementation qualifications](#appendix-d) · [References](#references)

# 1. From video to procedural decisions {#ch01}

A useful worker-action system must say more than which action appears somewhere in a video. It must identify the action interval, connect that interval to a particular build and procedure version, decide which prerequisites are established, and distinguish an error from insufficient observation. This chapter defines those outputs before introducing the models that produce them. The definition determines both the annotation effort and the evaluation protocol.

## 1.1 Recognition, localization, and segmentation

In trimmed action recognition, an input clip has already been selected to contain an action. The output is a label such as `tighten_fastener`. Formally, a clip $X_{s:e}$ is mapped to a class $c$. The person or process that selected $s$ and $e$ has already solved a substantial part of the temporal problem.

Temporal action localization, also called temporal action detection in relevant benchmarks, receives an untrimmed video and returns intervals and classes:

$$
X_{1:T}\longmapsto\{(s_i,e_i,c_i)\}_{i=1}^{M}.
$$

Temporal action segmentation assigns a label to each temporal position. A dense output might read `background, background, pick, pick, align, align, insert, ...`. Consecutive equal labels can then be converted into intervals. The supplied research selects this dense segmentation formulation as the primary task and derives discrete events from it. EPIC-KITCHENS provides a useful terminology check: its recognition task labels trimmed segments with verb–noun pairs, while detection includes temporal boundaries in untrimmed video. [S, “What the model actually predicts”; R1]

These formulations are related but not interchangeable. A classifier can perform well when given the exact tightening interval and still fail to find that interval among reaching, waiting, repositioning, and inspection. A detector can find isolated actions while leaving parts of the video unlabeled. A dense segmenter must make its treatment of every included time position explicit.

## 1.2 The output is a record, not a word

Suppose a model returns `tighten` at time 84.0 seconds. The downstream system needs to know whether this is a new action, a continuation, or a revision of an earlier decision. It also needs the object instance, the time interval actually observed, and the state of the correctness judgment. A minimal application event could be:

```json
{
  "build_id": "build-041",
  "procedure_version": "bracket-v7",
  "segment_id": "seg-018",
  "revision": 1,
  "step": "tighten_left_fastener",
  "start_s": 82.4,
  "end_s": 85.75,
  "action_confidence": 0.94,
  "procedural_status": "candidate_error",
  "error_type": "wrong_order",
  "observation_status": "available"
}
```

This is a textbook schema, not a VSS API payload. Separating `action_confidence` from `procedural_status` prevents a common ambiguity. A confident action recognizer does not imply a confident correctness judgment. Conversely, an uncertain action boundary does not necessarily make every previously verified prerequisite uncertain.

An event interval should have a declared convention. This book uses half-open intervals, $[s,e)$, so a boundary shared by two adjacent segments belongs to the second segment and is not counted twice. Time in seconds and index positions are different types of quantities. A feature at index 40 is not automatically at 40 seconds.

## 1.3 Observation, state, and judgment

There are at least three layers between pixels and an alarm. The observation layer estimates motion, objects, hands, tools, and other visible properties. The procedure-state layer records established facts about the assembly and interprets the observed action within its history. The decision layer applies an operational policy to decide whether to log, verify, review, or alert.

```text
VIDEO AND TELEMETRY
        |
        v
OBSERVATION: "tightening motion at left fastener"
        |
        v
PROCEDURE STATE: "insertion not yet established"
        |
        v
JUDGMENT: "wrong-order candidate, or insufficient evidence"
        |
        v
POLICY: log / retrieve evidence / review / alert
```

The distinction is already central to the report. Its hybrid pipeline assigns different responsibilities to the visual encoder, neural temporal model, HSMM or procedure graph, typed error engine, and VLM verifier. [S, “Executive summary”]

Consider two recordings with the same last three seconds. Both show a driver turning. In recording A, the fastener was inserted earlier. In recording B, the insertion opportunity was skipped under continuous observation. The correct action label may be identical, but the procedural conclusion differs. The last three seconds alone do not contain the distinction. It lives in the earlier evidence and procedure state.

Now consider recording C, in which the camera was obstructed during the insertion opportunity. C is not equivalent to B. The system lacks evidence about whether insertion occurred. A design that treats every unobserved prerequisite as false converts sensor failure into worker error.

## 1.4 Offline and online information sets

Let $E=(e_1,\ldots,e_N)$ be the feature sequence extracted from a video. An offline model may predict $y_t$ using all of $E$:

$$p(y_t\mid e_{1:N}).$$

A strictly causal model uses only information available by $t$:

$$p(y_t\mid e_{1:t}).$$

A bounded-lookahead model may use $\ell$ additional feature positions:

$$p(y_t\mid e_{1:t+\ell}).$$

The permitted lookahead must be translated into seconds and included in the latency contract. At a 0.5-second feature stride, four positions correspond to two seconds. A centered video clip may already introduce future dependence before the temporal model receives a feature. Causality is therefore a property of the whole data path, not a label attached to one neural layer. [S, “What the model actually predicts”]

**Implementation qualification.** A live system can emit provisional events and later revise them. That is a separate policy from a strictly irrevocable online decision. Evaluation must state which policy is used. A final segmentation produced after a build cannot be compared directly with alerts committed during the build without accounting for those different information sets.

## 1.5 An operational contract

Before collecting data, write down the decision the system is expected to support. A post-shift quality report may tolerate substantial delay while requiring detailed evidence. Immediate worker assistance may need an earlier, more cautious indication. A safety-related control has additional requirements that are not established by this research and should not be inferred from segmentation accuracy.

A contract for the example workstation might specify that each completed build receives a step timeline, that candidate wrong-order errors include an evidence interval, and that missing video produces an observation-gap record rather than an omission allegation. Those are testable behaviors. “Detect mistakes in real time” is not sufficiently precise because it leaves the relevant mistakes, deadlines, and uncertainty policy undefined.

| Question | Required decision |
|:--|:--|
| What is the unit of work? | One identified bracket assembly, not an entire camera shift. |
| What is the temporal output? | Dense labels plus derived, versioned step intervals. |
| What counts as unavailable evidence? | A defined visibility, timestamp, and stream-health condition. |
| When is a judgment committed? | A declared causal or bounded-lookahead policy. |
| What happens under uncertainty? | Review, deferral, or an explicit nonjudgment state. |

The table is a specification template rather than a recommendation about numeric thresholds. Its purpose is to force agreement between data collection, model training, and downstream behavior.

## 1.6 Exercises

**Exercise 1.1.** A dataset gives the exact start and end of every action at test time. A model predicts labels with high accuracy. Which task has been evaluated, and which two temporal abilities remain untested?

**Exercise 1.2.** A model uses four future feature positions at a stride of 0.5 seconds. Its encoder also uses one second of future video relative to each feature timestamp. What is the maximum input lookahead relative to the predicted position, assuming those dependencies add?

**Exercise 1.3.** Write two event records for the same confidently recognized tightening motion: one after continuously observed missing insertion, and one after a camera obstruction. Which fields should differ?

## 1.7 What follows

The system's basic output is an evidence-backed temporal record, not a class name. Its action estimate, procedure state, and alert policy can disagree without any contradiction because they answer different questions. The next chapter defines the labels and procedural state needed to represent those disagreements explicitly.

# 2. Labels, procedure graphs, and state {#ch02}

A label ontology is part of the model. It determines which distinctions the system can learn, which errors can be explained, and which changes require relabeling the dataset. This chapter develops an ontology that separates visual actions from procedural meaning, then shows why a graph of allowed transitions is useful but not always sufficient to describe an assembly.

## 2.1 Factor the description of an action

The report recommends hierarchical labels rather than one unrelated class for every full procedural sentence. A worker's action can be described by a phase, step, verb, manipulated object, tool, and location. Correctness and error type are recorded separately. [S, “Use hierarchical labels”]

For example, `tighten_left_fastener` can be decomposed into the verb `tighten`, noun `fastener`, instance `left_fastener`, tool `torque_driver`, and location `left_mounting_point`. The fine-step label remains useful because the procedure distinguishes left from right. The factorization exposes shared structure: tightening two different fasteners involves related motion even when their procedural roles differ.

A multi-head recognizer can estimate

$$p(v_t\mid h_t),\quad p(n_t\mid h_t),\quad
p(u_t\mid h_t),\quad p(y_t\mid h_t),$$

where $h_t$ is a temporal representation, $v_t$ the verb, $n_t$ the noun, $u_t$ the tool, and $y_t$ the fine step. The heads need not be independent. They provide several supervised views of the same interval and can be combined with compatibility constraints later.

The factorization does not create information absent from the image. If the left and right mounting points are indistinguishable in a cropped view, a noun head cannot recover the missing location merely because the schema contains a location field. Label design and camera design must agree.

## 2.2 Keep correctness out of the action vocabulary

Consider a flat ontology with these labels:

```text
tighten_correct
tighten_wrong_order
tighten_wrong_tool
tighten_too_long
```

This ontology duplicates the action across several procedural conditions. It also makes the meaning of the visual class depend on information outside the visible action interval. The report warns against this conflation. [S, “Correctness should be separate from the observed action”]

A better record stores the action and its judgment in separate fields:

```yaml
step: tighten_left_fastener
verb: tighten
noun: left_fastener
tool: torque_driver
correctness: error
error_type: wrong_order
judgment_basis:
  missing_prerequisite: insert_left_fastener
```

The same action interval can then support more than one error type without inventing a new visual class. It may have the wrong tool and occur before the required prerequisite. A judgment can also change after review while the visual label remains unchanged.

Use `unknown` deliberately. An unrecognized visible action, a genuine background interval, an unavailable camera observation, and an uncertain correctness judgment are different conditions. Collapsing all four into `other` makes both training and incident analysis difficult because the model cannot distinguish a visual vocabulary limitation from missing data.

## 2.3 A procedure graph

Let $G=(V,\mathcal E)$ contain procedure states and allowed transitions. A simple graph is:

```text
START -> pick -> align -> insert -> tighten -> inspect -> DONE
                            ^                   |
                            |                   |
                            +---- authorized ---+
                                   rework
```

The backward edge is not necessarily an error. It can represent a permitted repair. The graph should be versioned with the product and work instruction rather than reconstructed from whatever ordering happens to dominate the training data. Otherwise, a rare but legitimate execution can be treated as impossible simply because it was not observed often. [S, “The procedure is a graph, not necessarily a list”]

Graph edges serve two distinct purposes. They can constrain a decoder to choose plausible state sequences, or they can define which observed transitions count as valid. Those purposes must not be confused. A decoder restricted to valid paths cannot, by itself, return an invalid path as evidence of a mistake. Chapter 13 develops this consequence explicitly.

## 2.4 Preconditions and postconditions

**Implementation qualification.** A transition graph does not fully describe a procedure containing several prerequisites. Suppose tightening requires both insertion and alignment. The immediately preceding observed action may be `reach_for_driver`; the relevant question is whether the required facts have been established, not whether the last label is exactly `insert`.

Represent the procedure state as a collection of facts:

```text
aligned(left_bracket)       = true
inserted(left_fastener)     = true
tightened(left_fastener)    = unknown
inspected(left_assembly)    = false
```

A precondition states what must hold before an action is procedurally permitted. A postcondition states what the action is expected to establish. Observing tightening motion is not identical to verifying `tightened(left_fastener)`. The latter may require a visible final state or a tool measurement. The source already separates action recognition from correctness and notes the potential value of torque telemetry; the explicit fact representation here is a textbook elaboration. [S, “Typed error detection”; S, “Cross-feature fusion”]

A compact procedure definition might be:

```yaml
procedure_id: bracket_mount
version: 7
steps:
  tighten_left_fastener:
    requires_all:
      - aligned_left_bracket
      - inserted_left_fastener
    expected_postconditions:
      - tightened_left_fastener
    allowed_tools:
      - torque_driver
    authorized_rework: true
```

This is a domain schema, not a complete executable workflow language. Its value is that each field has a distinct role. `requires_all` expresses conjunction, while an adjacency list normally expresses one-step reachability.

## 2.5 Partial order, repetition, and rework

A procedure may allow either left or right fastening first. Enumerating every valid ordering can be wasteful. A prerequisite relation can instead state that both fasteners must be inserted before a final cover is installed, without imposing an order between their insertions. The procedural state then records which prerequisites have been satisfied.

Repeated labels need instance identity. `insert_fastener` performed twice might be two required operations on different fasteners, an unnecessary repetition on the same fastener, or a legitimate reinsertion after removal. The action name alone cannot resolve the case. Use part instance, operation instance, and procedure context when they are observable or externally assigned.

Rework also changes facts. Removing a fastener can invalidate `inserted` and `tightened`, and may invalidate an earlier inspection. A monotone set of completed steps is sufficient only for a simplified procedure whose completed facts never become false. The laboratory in Chapter 20 intentionally uses that simplification and identifies it in its interface; the capstone requires explicit invalidation rules.

## 2.6 An annotation decision that changes the system

Consider the boundary between insertion and tightening. One annotation policy ends insertion when the fastener first enters the hole. Another ends it when the worker releases the fastener. A third waits for initial thread engagement. These policies label different physical events. None can be selected merely by examining a neural architecture.

Write an operational definition such as: “Insertion begins when the fastener is moved toward its assigned hole and ends when the annotator can identify engagement or a specified fallback boundary.” Then define what to do when engagement is obscured. Store boundary confidence and distinguish an uncertain interval from a precise measurement.

This definition affects duration distributions, apparent segmentation accuracy, and the time at which an error becomes observable. A duration model trained under one boundary rule should not be applied without qualification to labels created under another.

## 2.7 Exercises

**Exercise 2.1.** A procedure contains 8 verbs and 20 object types. Explain why 160 possible verb–noun combinations are not necessarily 160 valid or observed actions, and propose a compatibility representation.

**Exercise 2.2.** A cover can be installed only after both left and right fasteners are tightened. Show why a single “previous action” variable cannot always establish this precondition.

**Exercise 2.3.** An inspection is followed by removal and reinsertion of the same fastener. Which previously established facts should a procedure designer consider invalidating, and why?

## 2.8 What follows

The ontology specifies what can be observed; the procedure specifies how established facts permit later actions. Their versions are part of the meaning of every training record and runtime event. The next chapter turns these definitions into a dataset that can support a credible experiment.

# 3. Building the dataset {#ch03}

A temporal model can learn only the distinctions represented consistently in its training data. A procedure monitor can be evaluated only when the dataset records what was visible, what was performed, and which correctness judgments are supported. This chapter develops a dataset design in which those requirements survive annotation, feature extraction, splitting, and later review.

## 3.1 The unit of collection

Collect sessions containing complete attempts at a procedure rather than only clean clips of individual actions. The unit of collection should include build identity, procedure version, camera identities, time references, and the surrounding pauses and transitions. Trimmed examples can help train representations, but they do not replace continuous recordings for learning segmentation and procedural state. [S, “Defining the problem and the training data”]

A session may contain several synchronized views of one execution. Those views are not independent examples of worker behavior. They share the same underlying actions, timing, objects, and mistakes. They are valuable for studying visibility and representation invariance, but all views of one session should remain in the same data split.

Maintain a collection manifest before creating dense labels:

```json
{
  "session_id": "session-0041",
  "build_id": "build-041",
  "worker_pseudonym": "operator-17",
  "station_id": "station-4",
  "product_variant": "widget-A",
  "procedure_id": "bracket_mount",
  "procedure_version": 7,
  "camera_ids": ["cam-front", "cam-side"],
  "time_reference": "session_elapsed_seconds"
}
```

The pseudonym supports worker-disjoint evaluation without requiring the learning system to identify a person from an image. This is a dataset-design choice; it is not a claim that pseudonymization alone resolves every privacy obligation.

## 3.2 Separate annotation layers

At least three annotation layers are useful. The action layer records intervals and factorized labels. The perception layer records relevant object tracks, tools, hands, pose, and visibility when those are part of the experimental design. The judgment layer records correctness, error type, evidence, and reviewer status. The report recommends a simple canonical training representation rather than treating a runtime transport schema as the dataset definition. [S, “Annotation tooling and schema”; S, “How VSS fits the data layer”]

```text
session
  +-- videos and timestamp mappings
  +-- step intervals and boundary confidence
  +-- object/tool tracks and visibility
  +-- procedure version
  +-- error judgments and evidence references
  +-- review history and annotation version
```

A null tool label should mean what the schema says it means. It could mean no tool was used, the tool was not annotated, or the tool could not be identified. Those meanings should not share an undifferentiated null value when the tool head or error engine depends on the distinction.

A practical annotation record extends the report's fields with explicit visibility:

```json
{
  "session_id": "session-0041",
  "camera_id": "cam-front",
  "start_s": 31.2,
  "end_s": 34.65,
  "step": "insert_left_fastener",
  "verb": "insert",
  "noun": "left_fastener",
  "tool": "none",
  "tool_label_status": "observed",
  "observation_status": "partially_occluded",
  "correctness": "uncertain",
  "error_type": null,
  "boundary_confidence": "medium"
}
```

The additional visibility and label-status fields are textbook implementation choices. They make the report's warning that “not detected” differs from “definitely absent” operational.

## 3.3 Annotation protocol and adjudication

Write annotation instructions using visible criteria, not only action names. Include representative boundaries, brief interruptions, authorized rework, occlusion, and examples in which a judgment cannot be made. A training session for annotators should expose disagreements before the dataset is large enough for those disagreements to become expensive.

Have more than one annotator label a selected subset. Inspect disagreement separately for action identity, start boundary, end boundary, tool identity, and correctness. A single agreement number can conceal the fact that annotators agree about the motion but disagree about its completion. Adjudication should produce both a final label and a recorded explanation when the disagreement reveals an ambiguous procedure definition.

CVAT's native video format supports tracks and a range of spatial annotations. It is therefore suitable for the object-level portion of the workflow. A timeline-oriented interface remains useful for procedural segments and their boundaries; this book does not assume that an object-tracking tool automatically supplies the complete procedure-annotation workflow. [R5; S, “Annotation tooling and schema”]

## 3.4 Public datasets as references, not substitutes

Assembly101 is relevant because it studies multi-view assembly activities, mistakes, and corrective behavior. IKEA ASM provides multi-view furniture-assembly data with action and geometric annotations. IKEA Assembly in the Wild concerns alignment between instructional diagrams and real assembly videos. These are different sources of methodological insight rather than interchangeable industrial datasets. [R2–R4]

Use them to ask concrete questions. Does the action vocabulary factor into verbs and manipulated objects? How are mistakes and corrections represented? Which views make a small part visible? How does the instruction representation differ from a dense temporal label? A dataset can be valuable for designing your ontology even when its actions do not match your product.

The supplied research does not establish that a model trained on any of these datasets will transfer to a particular workstation. Fine fastener identity, lighting, protective equipment, tools, and procedural postconditions remain deployment-specific. Transfer must be measured on a held-out dataset representing the target conditions.

## 3.5 Splits that test the intended claim

Randomly splitting overlapping clips is especially dangerous. Adjacent clips can share most of their frames, and even nonoverlapping clips from one session can share clothing, background, camera geometry, and a particular assembly. A model evaluated on such a split may exploit session identity rather than the intended action distinction. [S, “The most important evaluation splits”]

Split sessions before generating windows. Then define additional experiments whose held-out groups correspond to the intended generalization claim:

| Claim being tested | Appropriate held-out grouping |
|:--|:--|
| New executions under similar conditions | Complete sessions. |
| New operators | Worker identities, with their sessions. |
| New camera or station | Station/camera configurations. |
| Time-dependent drift | Days or shifts. |
| New product configuration | Product variants and procedure versions. |
| Robustness to mistakes | Separately held-out error sessions. |

Not every project can support all these splits immediately. State which claims the available data can test and which remain untested. Small datasets do not become more informative by using a split that leaks information.

## 3.6 Feature caches are datasets too

A feature array without metadata is not a reproducible training input. Cache the encoder identifier, checkpoint digest, preprocessing version, crop policy, frame-sampling rule, feature stride, time interval, and missing-frame policy. A cache generated from centered clips cannot later be presented as a causal input merely because its file is read from left to right.

A useful cache record contains a matrix $E\in\mathbb R^{N\times d}$ and an array of $N$ feature timestamps or interval bounds. Labels should be aligned through those timestamps rather than by assuming equal frame rates. Keep the mapping from each feature to its source video interval so that an unexpected prediction can be reviewed visually.

**Implementation qualification.** Multi-camera and overlapping-window leakage should also be excluded from contrastive pretraining when an experiment claims strictly held-out-session generalization. Unlabeled exposure to test sessions is still exposure. A transductive experiment can be legitimate, but it must be named as such rather than silently mixed with an inductive evaluation.

## 3.7 Exercises

**Exercise 3.1.** A two-second clip is extracted every half second. Explain why assigning windows independently to train and test can leak video content, and state the correct order of splitting and extraction.

**Exercise 3.2.** An annotator enters `tool: null` for both “no tool” and “tool obscured.” Describe a failure this creates in wrong-tool detection and propose a replacement schema.

**Exercise 3.3.** A dataset contains synchronized front and side views of each build. The front view is used for training and the side view for testing. Which generalization claim is confounded, and what experiment would better isolate view transfer?

## 3.8 What follows

A temporal dataset is a versioned collection of observations and judgments, not merely a folder of videos and labels. Its split design determines which scientific claims are possible. The next chapter develops the mathematical tools used to turn those observations into probabilistic sequence estimates.

# 4. Mathematical tools for temporal inference {#ch04}

The models in this book combine vectors, probabilities, and discrete decisions. Confusion often arises when a quantity from one category is interpreted as another: a logit is called a probability, a normalized score is called a likelihood, or a most likely path is treated as a collection of marginal state estimates. This chapter establishes the distinctions needed to follow the later derivations and inspect their implementations.

## 4.1 Shapes and temporal indices

Let a decoded video contain $T$ frames. A clip encoder converts groups of frames into $N$ feature vectors of dimension $d$. Usually $N$ is much smaller than $T$. The feature matrix is

$$E=[e_1,\ldots,e_N]^\top\in\mathbb R^{N\times d}.$$

The temporal model produces one score for each of $K$ labels at every feature position:

$$L\in\mathbb R^{N\times K}.$$

A minibatch adds a batch dimension. Mathematical notation often uses $[B,N,d]$, while a one-dimensional convolution implementation may expect $[B,d,N]$. These arrays contain the same conceptual dimensions in a different order. A shape error that swaps time and channel axes can produce executable code that learns an unintended function.

This book uses $T$ for raw frames when both frame and feature sequences are present, and $N$ for feature positions. Within an isolated sequence-model derivation, $t$ indexes the sequence supplied to that model. A duration $d_s$ is a count of feature positions unless explicitly expressed in seconds. Appendix A collects the symbols.

At two feature positions per second, an eight-hour sequence has $57{,}600$ positions. A float32 matrix with 384 channels occupies $57{,}600\times384\times4=88{,}473{,}600$ bytes, or 84.375 MiB, before metadata. This is a calculation for the stated configuration, not a measured service footprint. Intermediate activations, caches, and attention matrices add separate memory costs.

## 4.2 Vectors, projections, and similarity

A vector $e\in\mathbb R^d$ is an ordered collection of numbers. A learned linear projection $W\in\mathbb R^{K\times d}$ maps it to $K$ scores:

$$l=We+b.$$

Each row of $W$ defines one weighted combination of the features. A linear probe trains only $W$ and $b$ while keeping the encoder fixed. It tests whether the representation makes the chosen label distinction available through a simple decision surface.

The Euclidean norm is $\|e\|_2=\sqrt{\sum_i e_i^2}$. For nonzero vectors, cosine similarity is

$$\operatorname{cos}(e,f)=\frac{e^\top f}{\|e\|_2\|f\|_2}.$$

For $e=(3,4)$, the normalized vector is $(0.6,0.8)$. Its cosine similarity with $(0,1)$ is 0.8. Multiplying $e$ by 10 does not change the cosine. The calculation deliberately removes magnitude information; whether that is desirable depends on how the encoder represents confidence and content.

Normalize with a defined treatment of zero or near-zero norms. Returning an arbitrary direction for a zero vector can turn missing or corrupt features into a plausible retrieval result. A production adapter should flag invalid embeddings rather than quietly inventing semantic similarity.

## 4.3 Probability, likelihood, and posterior

A probability distribution over discrete states satisfies $p_j\geq0$ and $\sum_j p_j=1$. A likelihood such as $p(e\mid z=j)$ describes how an observation is distributed conditional on a state. A posterior such as $p(z=j\mid e)$ describes uncertainty about the state after observing $e$.

Bayes' rule connects them:

$$p(z=j\mid e)=\frac{p(e\mid z=j)p(z=j)}{p(e)}.$$

The distinction matters when a neural classifier feeds an HMM. A classifier typically estimates a posterior over labels. An HMM's generative factorization requires observation likelihoods. Substituting one for the other can reuse prior information in an unintended way. Chapter 13 treats this as an explicit implementation qualification to the report's schematic neural-emission equation.

For continuous features, $p(e\mid z)$ may be a density rather than a discrete probability. A density value is not required to be at most one, and its numerical value depends on the coordinate system. Only a properly integrated probability has the familiar interval bound. The small HMM laboratory uses discrete observation probabilities to avoid this additional issue in the first worked example.

## 4.4 Logits and softmax

A logit vector contains unrestricted real-valued scores. Softmax normalizes them:

$$q_k=\frac{\exp(l_k)}{\sum_j\exp(l_j)}.$$

Adding the same constant to every logit leaves $q$ unchanged. In computation, subtracting the maximum logit before exponentiation improves numerical stability without changing the result. For $l=(0,\log 3)$, softmax produces $(0.25,0.75)$.

Normalization does not guarantee calibration. A model can produce a valid probability vector whose 0.9 predictions are correct much less often than 90 percent on a target population. Calibration requires an empirical comparison between reported confidence and outcomes; it is not a consequence of using softmax.

A temperature $\tau>0$ changes the distribution to $q_k=\operatorname{softmax}(l/\tau)_k$. A larger temperature flattens the distribution, while a smaller one sharpens it. Unless ties intervene, positive temperature scaling does not change the largest-logit class. It can still change a structured decoder's result because it changes the relative strength of observation evidence compared with transition and duration terms.

## 4.5 Why inference uses logarithms

Sequence models multiply many probabilities. If a typical factor is 0.1, multiplying 1,000 factors yields $10^{-1000}$, too small for common floating-point formats to represent directly. Logarithms turn products into sums:

$$\log\prod_t a_t=\sum_t\log a_t.$$

An impossible event with probability zero has log probability $-\infty$. Preserve that meaning when a transition is genuinely forbidden. Replacing every zero with a small positive number changes the model by making previously impossible paths possible.

Summing probabilities in log space requires the log-sum-exp operation:

$$\operatorname{LSE}(a_1,\ldots,a_m)
=c+\log\sum_i\exp(a_i-c),\qquad c=\max_i a_i.$$

This equation needs a special case when every $a_i=-\infty$. The result is $-\infty$, not an undefined subtraction of two infinities. The laboratory implementation includes this case because impossible paths are ordinary conditions in constrained procedures, not exotic numerical accidents.

## 4.6 Sum versus maximum

Suppose two paths end in the same state. One has probability 0.20 and the other 0.15. Their combined contribution to the probability of that state is 0.35. The best individual path has probability 0.20. Summation and maximization answer different questions.

Forward inference sums over possible histories. Viterbi inference retains the best history for each current state. Smoothing combines evidence before and after a position to estimate its marginal state distribution. Taking the most likely state independently at each position is not necessarily the same as selecting the most likely complete path.

This distinction explains why a single “confidence” field is often insufficient. Confidence in the label at one position, probability of an entire state path, margin between competing paths, and confidence that a procedure error occurred are not interchangeable quantities.

## 4.7 Losses and optimization

For a labeled example whose true class is $y$, cross-entropy contributes $-\log q_y$. A correct prediction with $q_y=0.9$ contributes about 0.105; a prediction with $q_y=0.1$ contributes about 2.303. The loss penalizes confident errors more strongly than uncertain ones.

Training changes parameters to reduce an average loss over training examples. The gradient indicates how a small parameter change affects that objective locally. It does not indicate whether the dataset split is appropriate, whether the labels match the operational definition, or whether the loss corresponds to the cost of an alarm. Those remain experimental and design questions.

The foundational formulas in this chapter elaborate the report's embedding, HMM, Transformer, and training-loss sections. The numerical examples are textbook constructions. [S, “Embeddings and visual representation”; S, “HMMs, HSMMs, TCNs, and Transformers”]

## 4.8 Exercises

**Exercise 4.1.** A feature cache has shape $[1200,256]$. A classifier has 18 output labels. Give the shapes of its weight matrix, bias, and output logits, and calculate the feature-cache size in float32 bytes.

**Exercise 4.2.** Compute softmax for logits $(0,\log 2,\log 3)$. Explain why adding 100 to all three logits does not change the answer.

**Exercise 4.3.** Two paths ending in state A have probabilities 0.18 and 0.17. One path ending in B has probability 0.30. Which state has more total probability, and which state ends the best individual path?

## 4.9 What follows

The same array can carry a feature vector, a logit, or a log probability, but those interpretations impose different rules. Keeping the interpretation explicit makes the sequence-model derivations shorter and the implementation failures easier to locate. The next chapter examines what a learned feature vector must preserve for procedural work.

# 5. Embeddings and representation learning {#ch05}

A temporal model cannot recover every distinction lost by its visual encoder. It can use context to infer likely actions, but inference from context is different from observing the distinguishing motion or object state. This chapter explains what embeddings represent, how they can be learned, and how to test whether they contain the evidence needed for a procedural task.

## 5.1 The encoder as an information interface

An encoder is a learned function $f_\theta:\mathcal X\rightarrow\mathbb R^d$. Its input may be an image, a short video clip, or several modalities. Its output is a compact feature vector. The temporal recognizer consumes the feature sequence rather than the original pixels:

$$c_t\xrightarrow{f_\theta}e_t\xrightarrow{g_\phi}h_t.$$

Compression is useful because video contains large amounts of irrelevant variation. The exact texture of a wall may not matter to recognizing insertion. The movement of a small fastener relative to a hole may matter greatly. The encoder must learn which information to preserve for the downstream task. [S, “What an embedding is mathematically”; S, “What the representation must preserve”]

A representation trained for broad semantic retrieval may reliably associate a clip with “assembling furniture” while discarding the timing needed to distinguish inserting from removing a screw. This is not a contradiction. The retrieval objective and the segmentation objective reward different distinctions.

## 5.2 Why single frames can be insufficient

A single image of a hand holding a part near a surface may occur during either pickup or placement. Two consecutive images provide direction information; a longer sequence may show contact, release, or the final object state. The informative unit is therefore often spatiotemporal rather than purely spatial.

Consider a deliberately simplified sequence of object positions: $(4,3,2,1)$ relative to a target. Its reverse $(1,2,3,4)$ represents the opposite direction of motion. Averaging positions gives 2.5 in both cases. A representation that averages away order cannot distinguish them from that statistic alone. A temporal encoder can preserve differences between successive positions or learn a richer order-sensitive function.

SlowFast uses distinct temporal sampling pathways to combine slower semantic processing with faster motion information. VideoMAE learns representations through masked video reconstruction. These are useful named examples of video representation learning, not evidence that either is automatically best for the workstation in this book. [R8; R9]

## 5.3 Supervised learning and frozen features

The simplest task-specific representation strategy trains an encoder and classifier together on labeled clips. The loss encourages the representation to separate the training labels. This can work well when the labels and available data support the desired distinctions, but it can also encourage shortcuts such as worker appearance or station layout.

A frozen-encoder baseline separates two questions. First, does a pretrained representation expose useful action information? Second, how much can a simple classifier use that information? Keep $f_\theta$ fixed and fit a linear head:

$$q_t=\operatorname{softmax}(We_t+b).$$

Evaluate fine step, verb, noun, and tool separately. Strong verb performance with weak noun performance suggests that motion is represented better than part identity. A poor result on both may indicate a more fundamental mismatch in sampling, cropping, pretraining, or labels.

The report recommends this representation check before investing in a large temporal model. Context can improve prediction, but it should not conceal that visually important classes are inseparable in the chosen representation. [S, “Evaluating the representation before the sequence model”]

## 5.4 Contrastive learning

Contrastive learning trains an embedding by specifying which inputs should be similar and which should compete. For an anchor $i$ and positive $j$, one common objective is

$$
\mathcal L_{i,j}=-\log
\frac{\exp(\operatorname{sim}(z_i,z_j)/\tau)}
{\sum_{k\ne i}\exp(\operatorname{sim}(z_i,z_k)/\tau)}.
$$

The numerator rewards similarity to the selected positive. The denominator compares that positive with the other candidates. The temperature $\tau$ controls how sharply score differences affect the normalized comparison. SimCLR is a foundational example emphasizing augmentation and a learned projection head. CLIP aligns images and text through a contrastive training approach. [R6; R7]

For procedural work, the positive-pair rule is a modeling decision. Two synchronized camera views may show the same underlying action, but one may hide the manipulated part. Two clips bearing the same verb can involve different objects and procedural outcomes. If all clips labeled `tighten` are positives, the objective may reduce distinctions needed for wrong-part detection.

A useful design can combine action-level positives with auxiliary object or location supervision. Another can keep separate representation streams for motion and identity. The correct choice is established by an experiment that measures the downstream distinction, not by assuming all invariance is beneficial.

## 5.5 Augmentation must preserve the label

An augmentation is valid only relative to the task. A modest brightness change may preserve the action and part identity. A crop that removes the tool does not preserve the information needed to label tool use. Horizontal reflection can exchange left and right locations. Temporal reversal can change insertion into removal rather than produce a second view of the same action.

Write the invariance assumption beside each augmentation. For example, “brightness adjustment preserves the fine-step label within this range” is a falsifiable statement about the data. “Augmentation improves robustness” does not specify what information may be altered.

**Implementation qualification.** When labels contain directional or instance-specific information, transform the label consistently or exclude the augmentation. This follows from the report's factorized action ontology but is an explicit training rule added in this textbook.

## 5.6 Retrieval as an inspection tool

Nearest-neighbor retrieval can reveal what an embedding emphasizes. Choose a query clip labeled `insert_left_fastener`, retrieve similar clips, and inspect whether the neighbors share motion, object, camera, worker, or background. A representation that retrieves only the same workstation may be capturing context more strongly than action.

Quantify retrieval with Recall@K when a valid relevance definition is available. The relevance definition matters: “same fine step,” “same verb,” and “same procedure phase” produce different measurements. Do not call a retrieval result correct without specifying which relation is being tested.

Inspect both successful and failed neighbors. A false neighbor showing removal rather than insertion identifies a directionality issue. A neighbor showing tightening a different fastener may indicate that motion is learned while instance identity is not. Such evidence helps choose a targeted change rather than increasing model size without a hypothesis.

## 5.7 Text and procedural language

Text-aligned embeddings can connect clips to action descriptions or work instructions. This is useful for semantic context and retrieval, particularly when the language describes broad phases. It does not make the written instruction an observation. A text prompt stating “the operator inserts the correct fastener” cannot establish that the visible part is correct.

The report proposes video–text pairs and synchronized multi-camera clips as potentially useful supervision. In this book those are design candidates, not measured improvements. The surrounding procedure can supply semantic structure, but evaluation must still isolate whether the model recognizes the action from evidence rather than simply predicts the expected next step. [S, “Contrastive learning”]

## 5.8 Exercises

**Exercise 5.1.** Show that averaging the scalar sequences $(1,2,3,4)$ and $(4,3,2,1)$ gives the same feature. Name one additional statistic that distinguishes their direction.

**Exercise 5.2.** A linear probe is accurate on verbs but weak on manipulated parts. Propose two targeted representation changes and an evaluation that would distinguish their effects.

**Exercise 5.3.** Explain why horizontal reflection and temporal reversal can invalidate labels in a procedural dataset. Give one action or label affected by each.

## 5.9 What follows

An embedding is useful only relative to the distinctions a later decision requires. Linear probes, retrieval, and controlled augmentation tests expose those distinctions before a temporal model complicates the diagnosis. The next chapter determines which frames and modalities should reach the encoder in the first place.

# 6. Sampling, perception, and feature fusion {#ch06}

Temporal precision begins with the observation schedule. A model that receives one representation for several distinct actions cannot be expected to recover every boundary precisely from that representation alone. This chapter connects clip span, sampling rate, feature stride, camera visibility, and multimodal fusion to the evidence available for segmentation.

## 6.1 Three clocks that should not be conflated

A camera frame rate determines how frequently raw frames are captured. An encoder sampling rate determines which frames are selected within a clip. A feature stride determines how frequently the clip window advances. These are separate quantities.

The report suggests an initial configuration of 16 sampled frames at 8 frames per second, a nominal two-second local window, and a 0.5-second feature stride. It presents these as starting values, not universal settings. [S, “A sensible first sampling configuration”]

```text
window 0: [0.0 ---------------- 2.0)
window 1:      [0.5 ---------------- 2.5)
window 2:           [1.0 ---------------- 3.0)
window 3:                [1.5 ---------------- 3.5)
feature interval between successive windows: 0.5 seconds
```

**Implementation qualification.** Sixteen samples spaced by $1/8$ second have 15 gaps, so their first-to-last timestamp span is $15/8=1.875$ seconds. A two-second acquisition window may contain those samples, but the nominal window duration and timestamp span should not be treated as identical. Store the actual selected timestamps. Endpoint and sampling conventions otherwise create small but systematic alignment errors.

## 6.2 Stride and boundary resolution

At feature stride $\Delta$, the model emits decisions on a grid. If a boundary is rounded to the nearest grid point, the quantization error is at most $\Delta/2$ under that rounding rule. This bound does not include visual ambiguity, clip smoothing, or model error. It is only the contribution from the chosen grid.

With $\Delta=0.5$ seconds, grid rounding alone can contribute up to 0.25 seconds. An action lasting 0.2 seconds may be poorly represented on that grid even when the surrounding clips contain its frames. Overlapping windows increase opportunities to observe it but do not automatically produce a separate, correctly localized segment.

Choose sampling relative to the shortest operationally meaningful action. A system whose purpose is to distinguish broad assembly phases can use a different stride from a system that must distinguish insertion from a brief corrective withdrawal. This is the report's most important sampling principle. [S, “Recommended starting configuration”]

## 6.3 Centered and causal clips

A centered clip at time $t$ may include frames from $t-r$ through $t+r$. A causal clip ends at $t$ and uses only earlier frames. The centered clip is suitable for offline segmentation or an explicitly delayed output. It is not strictly causal at its center timestamp.

For a causal two-second history, a feature emitted at 12 seconds can summarize the interval ending at 12 seconds. The first feature after stream start may require a warmup interval. Later features reuse most of the already observed history. It is therefore inaccurate to add the full two-second history as a fresh delay to every decision without specifying the event and timestamp being measured.

Chapter 16 distinguishes warmup, evidence acquisition, lookahead, computation, and queueing. The present design rule is simpler: every feature needs both an evidence interval and an availability time. A fusion layer must not attach a slow context feature to an earlier decision before that context feature was actually available.

## 6.4 What perception contributes

A full-frame encoder can be supplemented by object, hand, tool, and pose features. An object representation might include category probabilities, bounding box, confidence, track identity, and a relation to the work region. A tool head might estimate which tool is in use. A pose stream can expose motion that is difficult to represent consistently from full-scene appearance.

These features are estimates, not guaranteed facts. A missed detection may result from occlusion, scale, blur, or a detector vocabulary limitation. The report explicitly warns that a tool not detected is not necessarily a tool definitely absent. [S, “Fault handling”]

Use confidence and visibility fields rather than converting every undetected object into a zero-valued presence flag. Track identity should also be scoped to a session or tracking epoch. A track identifier reused after a restart must not silently inherit the earlier object's procedural role.

## 6.5 Early and late fusion

An early-fusion model concatenates projected feature streams before temporal modeling:

$$u_t=\operatorname{MLP}([P_r e_t^{RGB};P_o e_t^{object};P_p e_t^{pose};m_t]).$$

The projections align dimensional scales. The vector $m_t$ indicates which modalities are available and how recent their observations are. The temporal model then learns interactions among the fused streams.

A late-fusion design combines separate model scores or decisions. It can make the contribution of each stream easier to inspect and can accommodate different update rates. It may lose interactions that would be easier to learn before classification. Neither fusion location is universally superior; it creates a different hypothesis about where useful dependencies should be modeled.

**Implementation qualification.** Missing-modality masks are essential when zero is a valid feature value. Without a mask, the network cannot distinguish a genuinely small measurement from an absent measurement replaced by zeros. Training should include the availability patterns expected at deployment rather than evaluating only on fully observed samples.

## 6.6 Semantic embeddings and Cosmos-Embed1

The report identifies Cosmos-Embed1 as a possible semantic representation stream and proposes combining it with a shorter-window motion representation. The checked VSS model documentation describes a joint video–text embedding model using frame-level visual processing and temporal aggregation. The RT-Embedding service supports video files and live streams, with configurable chunking. [S, “NVIDIA Cosmos-Embed1”; R22; R23]

The engineering concern is temporal aggregation, not an asserted intrinsic inability of the model. If a ten-second chunk contains pickup, insertion, reaching for a driver, and tightening, a single chunk representation may summarize all four. A separate short-window stream preserves a finer time grid. Whether this combination helps is an ablation question.

The report mentions a particular eight-frame, 448-resolution, 768-dimensional configuration. This edition does not treat that dimensionality as a universal Cosmos contract. The checked documentation and serving interface are version-dependent, and the output dimension should be discovered and validated for the selected model. The report's 256–768 range remains an illustrative design range for the custom temporal representation, not an asserted fixed vendor output.

## 6.7 Telemetry and the limits of video

Some procedural postconditions are not reliably visible. A driver may appear to tighten a fastener without achieving the required torque. When available, tool telemetry can contribute direct evidence about a variable the image does not measure. The report uses this as a reason to consider cross-feature fusion. [S, “What does CFF mean?”]

A telemetry event still requires alignment and identity. A torque measurement must correspond to the correct tool operation, fastener, and build. Merely observing a torque value near the same time is insufficient when several tools or workpieces are present. The fusion design should state how those associations are established and what happens when they are ambiguous.

## 6.8 Exercises

**Exercise 6.1.** Compute the first-to-last timestamp span of 16 equally spaced samples at 8 frames per second. Explain how they can still be described as samples from a nominal two-second window.

**Exercise 6.2.** A five-second semantic feature becomes available at time 15 seconds and summarizes $[10,15)$. Can it be used in a strictly causal decision committed at time 12? Explain the difference between offline alignment and online availability.

**Exercise 6.3.** An object-feature vector is replaced with zeros during occlusion. Explain why a mask and observation-age field can be more informative than zeros alone.

## 6.9 What follows

Sampling and fusion determine both the information content and the timing of the temporal input. A model cannot be called causal without auditing those choices. The next three chapters introduce probabilistic sequence models that combine observation evidence with state transitions and explicit duration.

# 7. Hidden Markov models {#ch07}

A hidden Markov model combines uncertain observations with a model of how hidden states change over time. Its value here is not that worker behavior is exactly Markovian. Its value is that the assumptions are explicit, the inference is inspectable, and the model provides a baseline for understanding what procedural order contributes beyond visual classification.

## 7.1 Hidden states and observations

Let $z_t$ be a hidden state and $x_t$ an observation. In the simplest procedural example, the state names correspond to fine steps such as `align`, `insert`, or `tighten`. The observation may be a visual feature or a discrete symbol extracted from that feature. The state is hidden because the camera provides evidence about the action rather than its true label directly.

An HMM makes two conditional-independence assumptions:

$$p(z_t\mid z_{1:t-1})=p(z_t\mid z_{t-1}),$$

$$p(x_t\mid z_{1:t},x_{1:t-1})=p(x_t\mid z_t).$$

The first says that the current state summarizes the modeled influence of earlier states on the next state. The second says that, conditional on the current state, the current observation is independent of other states and observations. The report introduces the HMM through this factorization, with Rabiner's tutorial as its foundational reference. [S, “HMM fundamentals”; R10]

```text
z1 ------> z2 ------> z3 ------> z4
|          |          |          |
v          v          v          v
x1         x2         x3         x4
```

The arrows describe a probabilistic factorization, not the physical claim that a label causes pixels. A generative model specifies a joint distribution from which conditional estimates can be derived.

## 7.2 The parameters

An initial distribution $\pi_j=P(z_1=j)$ states which hidden states are possible at the start. The transition matrix $A$ has entries $A_{ij}=P(z_t=j\mid z_{t-1}=i)$. An emission model $b_j(x)=p(x\mid z=j)$ assigns observation likelihoods.

For discrete emissions, each state has a normalized distribution over observation symbols. For continuous emissions, it has a density. The joint distribution is

$$p(z_{1:N},x_{1:N})=
\pi_{z_1}b_{z_1}(x_1)
\prod_{t=2}^{N}A_{z_{t-1},z_t}b_{z_t}(x_t).$$

Every factor has an identifiable role. Initial probabilities encode the start condition. Transitions encode state evolution. Emissions encode observation evidence. The decomposition makes it possible to inspect whether a prediction changed because of the image evidence or because of a sequence prior.

## 7.3 Topology as a modeling decision

A left-to-right procedure model can allow self-transitions and a small set of forward transitions. A self-transition means that the same state continues for another time position. A forward transition means that the model enters a new state. A backward edge can represent an authorized rework path.

A zero entry has a stronger meaning than a small entry. Zero excludes a transition from the modeled process. A small positive value says that the transition is possible but unlikely. Use hard zeros only when that distinction is intentional.

For a normal-procedure decoder, a zero from `align` directly to `tighten` may encode that insertion is required. For an observation model intended to expose mistakes, that same zero can suppress the very transition the error detector needs to see. This is not a numerical issue; it is a conflict between two uses of the graph. The distinction is developed in Chapter 13 as an implementation qualification to the hybrid architecture.

## 7.4 A fully specified two-state example

For numerical inference, temporarily reduce the state space to A and B. These are abstract states; their topology is not the complete bracket procedure. Let

$$\pi=(0.9,0.1),\qquad
A=\begin{bmatrix}0.7&0.3\\0.1&0.9\end{bmatrix}.$$

Let the observation alphabet be $\{u,v,w\}$ with emissions:

| State | $u$ | $v$ | $w$ |
|:--|--:|--:|--:|
| A | 0.6 | 0.3 | 0.1 |
| B | 0.1 | 0.4 | 0.5 |

Each row sums to one. We observe the sequence $(u,v,w)$. A has stronger support at the first position; B has stronger support at the last. The middle observation is less decisive. This deliberately small example permits enumeration of all $2^3=8$ hidden paths.

The path $(A,B,B)$ has joint probability

$$0.9\cdot0.6\cdot0.3\cdot0.4\cdot0.9\cdot0.5=0.02916.$$

The product includes the initial state, three emissions, and two transitions. It is not the posterior probability of the path conditional on the observations. To obtain that posterior, divide by the total probability of observing $(u,v,w)$, calculated in Chapter 8.

## 7.5 Estimating a supervised baseline

When training state labels are available, transition counts provide a direct baseline. Count how often $i$ is followed by $j$, then normalize over allowed successors. A smoothing constant can reduce instability for rare allowed transitions:

$$\hat A_{ij}=
\frac{n_{ij}+\alpha}{\sum_{k\in\mathcal N(i)}n_{ik}+
\alpha|\mathcal N(i)|},\qquad j\in\mathcal N(i).$$

Here $\mathcal N(i)$ is the explicitly permitted successor set. Forbidden edges remain zero rather than receiving smoothing mass. This is a textbook estimation rule, not a parameter setting specified by the report.

With known state labels, discrete emissions can also be estimated from counts. With continuous features, one can fit a simple state-conditioned distribution or use neural evidence as a scored hybrid model. With unknown states, HMM learning can use expected state and transition counts from forward–backward inference. This book emphasizes the supervised and neural-evidence cases because the source problem already calls for labeled procedural data.

## 7.6 What the Markov assumption leaves out

If the model state is only the current action name, it does not directly remember that a particular fastener was installed many minutes ago. It also cannot distinguish two procedural situations that share the same action label but have different remaining prerequisites. A richer state can include those facts, but its state space may grow rapidly.

The report therefore recommends two timescales: a local neural action model and a separate procedure memory. An HMM is useful as a baseline or component, not as a requirement to encode the entire build in one small action-state variable. [S, “Use two timescales”]

The emission-independence assumption is also imperfect for overlapping video clips. Neighboring features share frames and neural context. Their errors may be strongly correlated. The HMM can still be used as an approximation, but its raw probability values should not automatically be interpreted as calibrated certainty about an entire procedure.

## 7.7 Implicit duration

If state $j$ continues with probability $a=A_{jj}$ and exits with probability $1-a$, then a completed dwell of length $d\geq1$ has probability

$$P(D=d)=a^{d-1}(1-a).$$

For $a=0.9$, the mean duration is $1/(1-a)=10$ positions. The exit probability on the next position is always 0.1, regardless of how long the state has lasted. This memoryless behavior is the main duration limitation developed in Chapter 9. An absorbing state with $a=1$ is a separate case: it never exits under the model and does not have the same finite completed-duration distribution.

## 7.8 Exercises

**Exercise 7.1.** Using the two-state example, calculate the joint probability of the path $(A,A,B)$ for observations $(u,v,w)$.

**Exercise 7.2.** A state has self-transition probability 0.8. Compute its mean duration in positions and in seconds at a 0.5-second feature stride.

**Exercise 7.3.** Why can setting an invalid procedural transition to zero be helpful for normal-path decoding but harmful for detecting that transition as an observed error?

## 7.9 What follows

An HMM makes state, observation, transition, and duration assumptions explicit. Those assumptions make efficient inference possible, but they also delimit what the result means. The next chapter derives the inference algorithms and verifies them on the fully specified example above.

# 8. Forward, backward, and Viterbi inference {#ch08}

Enumerating every hidden path is useful for a three-position example and infeasible for a long video. Dynamic programming replaces enumeration with reusable summaries. This chapter derives three summaries: forward messages for observation probability, backward messages for later evidence, and Viterbi scores for the single best path. The worked trace shows why these outputs differ.

## 8.1 The forward variable

Define

$$\alpha_t(j)=p(x_{1:t},z_t=j).$$

This is the joint probability of the observations through position $t$ and state $j$ at that position. At the first position, there is no earlier path to summarize:

$$\alpha_1(j)=\pi_j b_j(x_1).$$

At a later position, a path ending in $j$ must have come from some state $i$. For each possible predecessor, multiply its accumulated probability by the transition probability to $j$, sum those mutually exclusive predecessor cases, and multiply by the new observation likelihood:

$$\alpha_t(j)=b_j(x_t)\sum_i\alpha_{t-1}(i)A_{ij}.$$

The total observation probability is $p(x_{1:N})=\sum_j\alpha_N(j)$. The report gives this recurrence; the derivation here makes the role of the sum explicit. [S, “Forward inference”]

## 8.2 Forward calculation by hand

For the example in Chapter 7, the first row is

$$\alpha_1=(0.9\cdot0.6,\;0.1\cdot0.1)=(0.54,0.01).$$

At the second observation $v$:

$$\alpha_2(A)=0.3(0.54\cdot0.7+0.01\cdot0.1)=0.1137,$$

$$\alpha_2(B)=0.4(0.54\cdot0.3+0.01\cdot0.9)=0.0684.$$

At the third observation $w$:

$$\alpha_3(A)=0.1(0.1137\cdot0.7+0.0684\cdot0.1)=0.008643,$$

$$\alpha_3(B)=0.5(0.1137\cdot0.3+0.0684\cdot0.9)=0.047835.$$

| Position | Observation | $\alpha_t(A)$ | $\alpha_t(B)$ |
|--:|:--|--:|--:|
| 1 | $u$ | 0.540000 | 0.010000 |
| 2 | $v$ | 0.113700 | 0.068400 |
| 3 | $w$ | 0.008643 | 0.047835 |

Thus $p(u,v,w)=0.056478$. The laboratory independently enumerates the eight paths and verifies that their probabilities sum to this number. This is a test of the implementation against the stated model, not an empirical result about video recognition.

## 8.3 Filtering

Normalize a forward row to obtain the filtered state distribution:

$$p(z_t=j\mid x_{1:t})=
\frac{\alpha_t(j)}{\sum_k\alpha_t(k)}.$$

Filtering uses observations only through the current position. It is therefore compatible with causal operation when the observations themselves are causal. At position 2, the example's filtered estimate still favors A because its accumulated earlier support outweighs B's modest advantage for observation $v$.

That estimate may change when observation $w$ arrives. A live system must decide whether it is permitted to revise the label at position 2 or whether that earlier decision has already been committed. The probability calculation and the commitment policy are separate.

## 8.4 The backward variable

Define

$$\beta_t(i)=p(x_{t+1:N}\mid z_t=i).$$

At the last position there are no later observations, so $\beta_N(i)=1$. At an earlier position, sum over the next state:

$$\beta_t(i)=\sum_j A_{ij}b_j(x_{t+1})\beta_{t+1}(j).$$

Multiplying forward and backward messages accounts for observations on both sides of a position:

$$\gamma_t(j)=p(z_t=j\mid x_{1:N})=
\frac{\alpha_t(j)\beta_t(j)}{p(x_{1:N})}.$$

These are smoothed marginal probabilities. They use future evidence and should not be reported as an online result without a delay or revision policy. The recurrence and posterior combination follow the report's backward-inference section. [S, “Backward inference”]

For the synthetic example, the smoothed rows are:

```text
position 1: A = 0.969510, B = 0.030490
position 2: A = 0.442898, B = 0.557102
position 3: A = 0.153033, B = 0.846967
```

The middle position now favors B. The final observation makes histories that have already entered B more plausible. This is the concrete difference between filtering and smoothing.

## 8.5 Viterbi: replace the sum with a maximum

Define a best-path score ending in $j$:

$$\delta_t(j)=\max_{z_{1:t-1}}p(z_{1:t-1},z_t=j,x_{1:t}).$$

The probability-space recurrence is

$$\delta_t(j)=b_j(x_t)\max_i[\delta_{t-1}(i)A_{ij}].$$

Store the maximizing predecessor $\psi_t(j)$. At the end, choose the best terminal state and follow the stored predecessors backward. Without the backpointers, the score table does not contain enough information to reconstruct the whole maximizing path.

The example produces:

| Position | Best score ending A | Best score ending B |
|--:|--:|--:|
| 1 | 0.540000 | 0.010000 |
| 2 | 0.113400 | 0.064800 |
| 3 | 0.007938 | 0.029160 |

The best path is $(A,B,B)$, with joint probability 0.02916. Dividing by 0.056478 gives its posterior probability conditional on the observation sequence, approximately 0.5163. A best path can therefore be the largest individual path without carrying most of the total probability by a wide margin.

## 8.6 Stable log-space implementation

Let $\ell_t(j)=\log b_j(x_t)$. Then

$$\log\alpha_t(j)=\ell_t(j)+
\operatorname{LSE}_i[\log\alpha_{t-1}(i)+\log A_{ij}],$$

while Viterbi uses

$$\log\delta_t(j)=\ell_t(j)+
\max_i[\log\delta_{t-1}(i)+\log A_{ij}].$$

The only difference in the reduction operation is log-sum-exp versus maximum. Their interpretation remains different. A generic “sequence score” implementation should not swap these reductions without naming the resulting algorithm.

```python
for t in range(1, length):
    candidates = previous[:, None] + log_transition
    if mode == "forward":
        current = log_evidence[t] + logsumexp(candidates, axis=0)
    else:
        back[t] = candidates.argmax(axis=0)
        current = log_evidence[t] + candidates.max(axis=0)
    previous = current
```

This is explanatory pseudocode; Chapter 20 supplies complete functions and validation. In particular, an all-impossible terminal row must produce an explicit failure rather than a fabricated path chosen by `argmax` over identical negative infinities.

## 8.7 Complexity and memory

For $N$ positions and $K$ states, a dense transition recurrence costs $O(NK^2)$. A sparse procedure graph can reduce the transition work to the number of allowed edges per position. Filtering needs only the previous forward row, so its working memory can be $O(K)$ apart from outputs. Full Viterbi reconstruction stores predecessor information across positions, typically $O(NK)$.

An incremental Viterbi computation can update scores as observations arrive, but its best prefix is not automatically irrevocable. Future evidence can select a different earlier path. Online commitment requires a bounded-lag, beam, or explicit revision policy rather than simply calling the recurrence one row at a time.

## 8.8 Exercises

**Exercise 8.1.** Verify that the final forward values sum to 0.056478. Why is that sum greater than the best path's joint probability of 0.02916?

**Exercise 8.2.** Explain why the smoothed estimate at position 2 can favor B even when the filtered estimate at that position favors A.

**Exercise 8.3.** Construct a unit test for an HMM whose start distribution and transition structure make every complete path impossible. What should the decoder return or raise?

## 8.9 What follows

Forward inference totals compatible histories, smoothing conditions on later evidence, and Viterbi selects one history. Their shared dynamic-programming structure does not make their outputs interchangeable. The next chapter changes the state-duration assumption while retaining the same principle of reusing partial sequence scores.

# 9. Explicit duration with hidden semi-Markov models {#ch09}

A procedure step is an interval, and its duration can carry useful evidence. A brief tool contact and a long tightening attempt may have different interpretations even when their framewise action labels are similar. An HSMM models duration explicitly rather than obtaining it indirectly from a self-transition probability. This chapter derives segmental decoding and explains the extra care required for an unfinished live interval.

## 9.1 Why geometric duration is restrictive

In an HMM, a state continues with probability $a$ at every position and exits with probability $1-a$. Its completed duration distribution is geometric:

$$P(D=d)=a^{d-1}(1-a),\qquad d\geq1.$$

The conditional probability of exiting next does not depend on age. At age one or age twenty, it remains $1-a$. The report identifies this memorylessness as a poor fit for many procedural actions. A step often has a characteristic duration range, and elapsed time can change what should be expected next. [S, “The HMM duration problem”]

This is not an argument that every action has a narrow duration distribution. Pauses, tool difficulties, operator differences, and product variants can produce broad or multimodal durations. It is an argument for making the duration assumption explicit and testing it rather than accepting a geometric form by default.

## 9.2 The segment representation

Represent the sequence as segments $(s_m,e_m,z_m)$, with half-open index intervals $[s_m,e_m)$ and durations $d_m=e_m-s_m$. An explicit-duration model assigns each state a distribution $p_j(d)$. A transition occurs between segments rather than at every interior position.

Possible distributions include empirical histograms, discretized log-normal or gamma distributions, and other positive-duration models. The report lists these options; explicit-duration semi-Markov models provide the underlying alternative to HMM dwell times. [S, “HSMM: explicit duration”; R11]

If a continuous duration variable is measured in seconds but decoding uses positions, convert it consistently. One approach assigns mass to each duration bin by integrating the continuous density over that bin. Simply evaluating a density at integer points and treating the values as normalized probabilities is a different approximation and should be named.

## 9.3 A segment score

Let $\ell_t(j)$ be observation log evidence for state $j$. A segment beginning at $s$ and ending just before $e$ has score

$$B_j(s,e)=\log p_j(e-s)+\sum_{t=s}^{e-1}\ell_t(j).$$

The first term scores duration; the second accumulates observation support. In a generative model, the latter consists of log likelihoods. In a discriminative hybrid, it may consist of calibrated or weighted neural potentials. The dynamic program works with either, but the resulting total has a different probabilistic interpretation.

Precompute prefix sums $C_j(e)=\sum_{t=0}^{e-1}\ell_t(j)$. Then the observation sum is $C_j(e)-C_j(s)$. This makes each proposed segment's observation score constant-time after preprocessing.

**Implementation qualification.** Ordinary prefix sums require care when emissions can be $-\infty$: subtracting two infinite sums is undefined. The teaching implementation requires finite observation potentials and allows impossible transitions and durations separately. A production implementation supporting impossible emissions can keep both finite sums and counts of impossible entries.

## 9.4 Segmental Viterbi

Let $V(e,j)$ be the best score of a sequence whose last completed segment is state $j$ and ends at $e$. For a candidate duration $d$, its start is $s=e-d$. The recurrence is

$$V(e,j)=\max_{d,i}
\left[V(e-d,i)+\log A_{ij}+\log p_j(d)
+\sum_{t=e-d}^{e-1}\ell_t(j)\right].$$

When $e-d=0$, replace the predecessor term by $\log\pi_j$. Store both the predecessor state and the winning duration. Backtracking then moves from one segment boundary to the preceding boundary rather than one position at a time.

The duration distribution accounts for staying in a state. In the basic formulation, adjacent segments do not have the same label, so the segment-level transition matrix excludes self-transitions. Otherwise, a long dwell can be represented as several adjacent same-state segments, which changes the intended duration model. This is an explicit clarification of the report's schematic HSMM equations.

For a maximum duration $D_{\max}$, a straightforward dense implementation costs $O(NK^2D_{\max})$. Sparsity and precomputation can reduce work, but a claimed complexity should state exactly which terms have been cached or restricted.

## 9.5 A numerical segment example

Consider four positions with two state-evidence columns:

```text
          A      B
position 0  0.9    0.1
position 1  0.8    0.2
position 2  0.2    0.8
position 3  0.1    0.9
```

These are synthetic positive observation potentials, not a fully specified generative emission distribution. Start in A. Permit a transition from A to B, and assign each state duration probabilities $P(D=1)=0.2$ and $P(D=2)=0.8$. The segment sequence A for positions $[0,2)$ followed by B for $[2,4)$ has unnormalized weight

$$0.8(0.9\cdot0.8)\;1.0\;0.8(0.8\cdot0.9)=0.331776.$$

The laboratory also allows B-to-A transitions so that competing segment paths exist, but the maximizing result is the stated two-segment path. Its weight is not a calibrated probability that the real-world procedure is correct. It is the exponential of the score under the supplied potentials.

The example shows the separate effects of observation and duration. Changing the duration mass can move a boundary even without changing the evidence matrix. Such movement is useful when it corrects noisy evidence and harmful when it forces a real atypical action into a normal duration pattern.

## 9.6 Fitting and checking duration models

Fit duration parameters on training data created under a consistent boundary policy. Inspect durations by action and product variant before selecting a family. A distribution dominated by annotation inconsistency will not become reliable merely because it has a named parametric form.

A histogram makes few shape assumptions but needs enough observations per bin. A log-normal model uses fewer parameters and can represent positive right-skewed durations, but it can miss multimodal behavior. Conditioning on tool or product variant may explain some variation; conditioning on every incidental attribute can leave too little data to estimate anything reliably.

Duration anomalies are evidence for investigation, not proof of incorrect completion. A long tightening interval may be legitimate rework or a visibility-induced segmentation error. A short interval may be sufficient with one tool and incomplete with another. The report combines duration with expected postconditions for precisely this reason. [S, “Typed error detection”]

## 9.7 Completed duration versus ongoing duration

**Implementation qualification.** During a live step, the observed age $a$ is not yet its completed duration. The relevant event is often $D\geq a$, with survival function

$$S_j(a)=P(D\geq a)=\sum_{d=a}^{\infty}p_j(d).$$

The discrete hazard of ending at age $a$, given survival to that age, is

$$h_j(a)=P(D=a\mid D\geq a)=\frac{p_j(a)}{S_j(a)}.$$

A small value of $p_j(a)$ alone can be misleading early in a step: a duration may be unlikely to end now without the ongoing action being anomalous. For a long-duration candidate, a tail score such as $-\log S_j(a)$ is often the more relevant construction. It still needs calibration and an uncertainty policy.

Similarly, a recorded clip that ends while the worker is still tightening is right-censored. Treating the clip end as a completed action end biases duration estimates. A censored training contribution uses survival probability rather than completed-duration mass. The report does not specify this treatment; it is added here because deployment and dataset boundaries make censoring unavoidable.

## 9.8 Exercises

**Exercise 9.1.** A duration model has masses $p(1)=0.2$, $p(2)=0.5$, and $p(3)=0.3$. Compute $S(2)$ and the hazard $h(2)$.

**Exercise 9.2.** Explain why adjacent same-state segments can undermine an explicit-duration model when they are freely permitted.

**Exercise 9.3.** A video stops after six seconds of a step that is visibly still in progress. What is wrong with treating six seconds as its completed duration during training?

## 9.9 What follows

An HSMM assigns probability or score to complete intervals, making duration inspectable rather than implicit. Its offline decoding rule is not automatically a live censoring policy. The next chapters develop neural temporal evidence that can be combined with this structured interval model.

# 10. Temporal convolutional networks {#ch10}

A framewise classifier evaluates each feature vector largely in isolation. A temporal convolutional network learns how neighboring evidence changes the interpretation of a position. It can recognize that a brief ambiguous image belongs to an ongoing insertion rather than a new action, while preserving an explicit and computable temporal receptive field. This chapter develops convolution, dilation, residual blocks, and causality before introducing multi-stage refinement.

## 10.1 A convolution over time

For scalar inputs, a causal convolution with kernel size $k$ is

$$h_t=\sum_{r=0}^{k-1}w_r x_{t-r}+b.$$

For vector inputs, each $w_r$ becomes a matrix mapping input channels to output channels. The same parameters are applied at every temporal position. This sharing expresses the assumption that the local evidence for an action should not depend on its absolute position in a recording.

A kernel of size three can combine the current feature with the two preceding features. Multiple layers compose these local operations. Nonlinearities allow the composition to represent more than a single linear filter. The report introduces TCNs as efficient temporal models and cites the action-segmentation work of Lea and colleagues. [S, “Temporal convolutional networks”; R12]

Temporal convolution is not simply smoothing. Learned filters can detect changes, directional patterns, or combinations of channels that distinguish actions. A smoothing objective may later encourage stable outputs, but the convolution itself is a trainable transformation rather than a fixed averaging operation.

## 10.2 Dilation

A dilated convolution samples inputs at intervals of $d$ positions:

$$h_t=\sum_{r=0}^{k-1}W_r x_{t-dr}+b.$$

For kernel size three, dilations 1, 2, and 4 use progressively wider temporal neighborhoods:

```text
dilation 1:  t-2  t-1  t
              *    *   *
dilation 2:  t-4  t-2  t
              *    *   *
dilation 4:  t-8  t-4  t
              *    *   *
```

Stacking these layers lets information from many earlier positions influence the current output without requiring a large kernel at every layer. The arrangement of dilation rates is part of the architecture; it should be recorded alongside the number of layers and channels.

Dilation does not increase the temporal sampling resolution. A network operating at two feature positions per second still receives that grid, even when a receptive field extends over a minute. Long context and precise boundaries are different properties.

## 10.3 Deriving the receptive field

For stride-one convolutions with kernel sizes $k_\ell$ and dilations $d_\ell$, the receptive-field length is

$$R=1+\sum_{\ell=1}^{L}(k_\ell-1)d_\ell.$$

Each layer adds the maximum extra offset it can reach through its input. With kernel size three and dilations $1,2,4,\ldots,2^{L-1}$:

$$R=1+2\sum_{\ell=0}^{L-1}2^\ell=2^{L+1}-1.$$

For six layers, $R=127$ positions. At a 0.5-second stride, the first-to-last feature timestamp span is $(127-1)\cdot0.5=63$ seconds. The raw-video history also includes the span of the earliest clip used to construct those features. State whether a reported “context duration” refers to feature-grid span, occupied bins, or raw-video support.

**Implementation qualification.** The report lists 8–10 layers as a starting configuration and separately suggests local context on the order of 30–120 seconds. Those values should not be combined without calculating the resulting receptive field. Eight layers with the stated dilation rule yield 511 positions, or a 255-second feature timestamp span at a half-second stride. The examples are starting ranges, not a jointly validated configuration.

## 10.4 Residual blocks and channels

A residual block adds a transformed input back to the input:

$$h^{\ell+1}=h^\ell+F_\ell(h^\ell).$$

A common temporal block uses a dilated convolution, a nonlinearity, a pointwise channel projection, and dropout. The pointwise projection mixes channels at the same time position without expanding temporal support. The residual connection gives the block a direct path for preserving its input while learning a correction.

```text
h -------------------------------+
|                                |
+-> dilated conv -> ReLU -> 1x1 -> + -> next h
                         dropout
```

The number of channels controls representation capacity and compute. Increasing channels does not change the temporal receptive field unless the layer structure also changes. Increasing depth with growing dilation expands the receptive field rapidly and therefore changes the context assumption as well as capacity.

## 10.5 Causal padding

A causal convolution must not use future positions. In an implementation with kernel size three and dilation $d$, pad $2d$ values on the left and none on the right, then use a convolution with no additional symmetric padding. PyTorch's kernel-index ordering follows its cross-correlation convention; the dependence still covers only the current and earlier positions.

```python
left = 2 * dilation
h = conv(torch.nn.functional.pad(x, (left, 0)))
```

The teaching network in Chapter 21 uses this structure at every stage. It avoids temporal normalization that would mix current and future positions. Dropout is disabled for the causality test so that random masks do not obscure the comparison. PyTorch's convolution and padding interfaces are documented in [R33]; the architecture and tests are original teaching code.

A symmetric convolution may perform better offline because it receives later evidence. That is a legitimate experiment, but its advantage should not be reported as a live causal improvement. Train and evaluate the deployment variant rather than converting a bidirectional model to a causal one only at serving time.

## 10.6 Test causality instead of trusting a diagram

Choose a sequence and a cutoff $c$. Compute the model output. Change every input after $c$, leaving the prefix unchanged, and compute again. A strictly causal model in deterministic evaluation mode should produce identical outputs through $c$.

```text
original input:  prefix P | future F
modified input:  prefix P | future G
required output: same prefix predictions
```

Also compare a full-sequence evaluation with evaluation on a truncated prefix. Matching the prefix outputs checks that sequence length itself does not alter the earlier result through an unintended operation.

These tests cover the tested neural module. They do not establish that the video encoder, feature normalization, multimodal alignment, or downstream decoder is causal. A complete pipeline needs the same availability audit at every stage.

## 10.7 Windowed inference and caching

A stateless serving implementation can keep a rolling feature buffer and run the TCN over the available context. This is easy to inspect but recomputes many intermediate activations. A cached implementation stores the prior activations needed by each dilated layer and updates them incrementally.

The two implementations should agree numerically under the same padding, weights, and history. Treat that equivalence as a test before adopting the faster path. A caching bug can affect only boundary positions or a particular dilation and remain invisible in a broad accuracy average.

A shorter rolling buffer than the model's receptive field changes the function near the buffer boundary. It may be an acceptable approximation, but it is not equivalent to full-context inference. Record the actual buffer policy in the experiment manifest.

## 10.8 Exercises

**Exercise 10.1.** Calculate the receptive field for kernel size three and dilations $1,2,4,8$. Convert its first-to-last feature timestamp span to seconds at a 0.5-second stride.

**Exercise 10.2.** A convolution uses kernel size three, dilation eight, and symmetric padding of eight positions. Why is it not causal? What left-only padding preserves output length while removing future dependence?

**Exercise 10.3.** Design a prefix-perturbation test for a TCN. Which stochastic or sequence-wide operations should be controlled so that a failed comparison is interpretable?

## 10.9 What follows

A TCN gives temporal context a concrete implementation and an exact receptive-field calculation. Its causal behavior can be tested rather than inferred from its name. The next chapter uses several temporal stages to refine dense predictions and develops losses that balance label accuracy with segment quality.

# 11. Multi-stage refinement and training losses {#ch11}

High frame accuracy can coexist with a poor step timeline. A model may assign the correct label almost everywhere yet insert many short, spurious segments. Multi-stage temporal models address this by refining a sequence of predictions, while training losses determine how strongly the model values classification, continuity, and boundaries. This chapter explains both the benefit and the failure modes of that combination.

## 11.1 Over-segmentation

Consider a true sequence with three long actions:

```text
truth:       AAAAAAAA BBBBBBBB CCCCCCCC
prediction:  AAAABAAA BBBABBBB CCACCCCC
```

Only a few positions are wrong, but collapsing repeated labels produces several extra actions. A procedure monitor may interpret the fragments as repetitions, reversals, or wrong-order transitions. The error is therefore operationally larger than its frame count suggests.

The original MS-TCN uses multiple stages of temporal convolutions and a smoothing loss to reduce over-segmentation. The report recommends it as the first serious segmentation baseline, not as a guarantee of superiority on an unseen industrial dataset. [R13; S, “MS-TCN and over-segmentation”]

## 11.2 Refinement stages

A first stage maps features to class logits. Later stages consume the preceding stage's probability sequence and produce refined logits:

$$L^{(1)}=g_1(E),\qquad
L^{(s)}=g_s(\operatorname{softmax}(L^{(s-1)})).$$

```text
features -> stage 1 -> probabilities
                         |
                         v
                      stage 2 -> probabilities
                                    |
                                    v
                                 stage 3 -> final scores
```

The later stage sees a temporal pattern of beliefs rather than raw pixels. It can learn that a single-position label island surrounded by a stable action is often an error, or that a plausible boundary should be preserved. This is a learned refinement process, not a deterministic instruction to remove every short segment.

Attach supervision to each stage so that intermediate predictions remain meaningful. A common objective sums or averages per-stage losses. State which convention is used because changing the number of stages can otherwise change the total loss scale and effective optimization settings.

## 11.3 Classification and masking

For valid labeled positions $\mathcal V$, cross-entropy is

$$\mathcal L_{CE}=-\frac{1}{|\mathcal V|}
\sum_{t\in\mathcal V}\log q_t(y_t).$$

Training batches often contain right-padding so that sequences can share a tensor shape. Padded positions must not contribute to the loss. An uncertain or unannotated action position may also need to be excluded from a particular supervised head. Do not replace missing labels with `background` merely to satisfy an array shape.

Normalize by valid positions, not by padded length. Otherwise, a short sequence padded to a long batch length contributes less loss per genuine observation than a long sequence. The resulting weighting can change whenever batch composition changes.

## 11.4 Temporal smoothing

The report gives a truncated difference penalty on neighboring log probabilities:

$$\mathcal L_{smooth}=\frac{1}{K|\mathcal P|}
\sum_{(t-1,t)\in\mathcal P}\sum_{k=1}^{K}
\min\bigl(|\log q_{t,k}-\log q_{t-1,k}|,\eta\bigr)^2,$$

where $\mathcal P$ contains valid adjacent pairs. The truncation $\eta$ limits the contribution of a large difference. The combined loss is

$$\mathcal L=\mathcal L_{CE}+\lambda_s\mathcal L_{smooth}.$$

This formulation elaborates the report's generic smoothing objective. The laboratory uses a symmetric difference with gradients on both positions; it is a teaching variant rather than a claim to reproduce every optimization detail of the original MS-TCN implementation. [S, “MS-TCN and over-segmentation”]

A smoothing loss trades fragmentation against boundary sharpness and short-action recall. Raising $\lambda_s$ may improve edit score while removing a legitimate brief insertion. Evaluate that tradeoff directly. A smoother probability trace is not automatically a more correct procedural trace.

## 11.5 Class imbalance and focal loss

Weighted cross-entropy assigns different importance to classes:

$$\mathcal L_{weighted}=-\sum_t w_{y_t}\log q_t(y_t).$$

Focal loss reduces the relative contribution of easy examples:

$$\mathcal L_{focal}=-\alpha_y(1-q_y)^\gamma\log q_y.$$

Focal loss was introduced for dense object detection. The report proposes cautious adaptation when common steps or background overwhelm rare classes; this is a design possibility, not a demonstrated industrial-error result. [R19; S, “Training losses”]

Rare error events and rare action labels should not automatically be handled by the same loss. The visual head predicts actions, while a procedural error can depend on history and postconditions. Oversampling `tighten` clips does not create examples of omitted insertion unless the sequence and judgment annotations capture that condition.

## 11.6 Boundary supervision

Define a boundary target $b_t=\mathbf1[y_t\ne y_{t-1}]$. A boundary head can predict $r_t=P(b_t=1)$ and use binary cross-entropy:

$$\mathcal L_b=-\sum_t[b_t\log r_t+(1-b_t)\log(1-r_t)].$$

Boundary supervision makes changes explicit rather than relying only on class predictions. It also inherits annotation uncertainty. A boundary known only within a one-second range should not be treated as a perfectly measured instant without a policy for uncertain positions.

The report proposes combining step, verb, noun, boundary, smoothing, and duration terms. Adding all terms at once makes diagnosis difficult. Establish a step-classification baseline, then add a term to test a specific hypothesis. Record whether its improvement comes from better boundaries, less fragmentation, better rare-class recall, or a change in calibration. [S, “Training losses”]

## 11.7 Refinement expands temporal support

**Implementation qualification.** If stage $s$ has receptive-field length $R_s$, composing causal stages can yield

$$R_{total}=1+\sum_s(R_s-1),$$

assuming stride-one aligned stages and no additional temporal operations. Four stages of receptive field 31 can therefore depend on 121 input positions, not only 31. This matters when selecting a rolling buffer and explaining latency or context.

Refinement can also compound future dependence in noncausal variants. A later stage consumes earlier-stage outputs that already depend on future inputs. Limiting only the final stage's attention or convolution does not remove that upstream dependency.

## 11.8 A training trace that teaches something

The neural laboratory uses two causal stages, three dilated layers per stage, three classes, and a synthetic feature sequence. It checks output shape, prefix invariance, an all-masked loss, and whether a short optimizer run reduces loss on an intentionally easy input.

The recorded run reduces its synthetic objective from approximately 1.141251 to 0.059701 after 40 updates. This verifies that the implemented loss and gradients can support optimization on that constructed task. It says nothing about industrial accuracy, generalization, or the merit of a particular hyperparameter. Chapter 21 explains the trace and reproduces the code.

## 11.9 Exercises

**Exercise 11.1.** Explain how a prediction can have high frame accuracy and poor edit score. Construct a short label sequence illustrating the difference.

**Exercise 11.2.** Three causal refinement stages each have receptive field 15. What is the composed receptive field under the assumptions above?

**Exercise 11.3.** A larger smoothing weight reduces the number of segments but lowers recall for brief insertion actions. Which measurements and visual inspections would you use to decide whether the change is acceptable?

## 11.10 What follows

Refinement helps when its learned continuity assumptions match the task, and it harms when it erases real short actions or conceals boundaries. Training should expose those tradeoffs rather than optimize only a framewise score. The next chapter introduces attention and multiresolution alternatives while retaining the same causal and evaluation requirements.

# 12. Transformers and multiresolution temporal models {#ch12}

Attention lets a temporal position select information from other positions according to their content. This can represent dependencies that are awkward for a fixed convolutional neighborhood, but it also creates new choices about position, locality, memory, and future access. This chapter derives attention and relates generic Transformer operations to action-segmentation models without treating every model containing attention as the same architecture.

## 12.1 Queries, keys, and values

Let $H\in\mathbb R^{N\times d}$ contain temporal features. Linear projections produce queries, keys, and values:

$$Q=HW_Q,\qquad K=HW_K,\qquad V=HW_V.$$

For one attention head, the output is

$$O=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V.$$

The softmax acts along each query's key positions. The mask $M$ is zero for permitted interactions and $-\infty$ for forbidden ones. A causal mask forbids a query at $t$ from attending to keys after $t$.

Each output row is a weighted sum of value rows. Queries and keys determine the weights, while values determine the content combined. The original Transformer introduced this attention-centered sequence architecture; the report derives its main operations before discussing video-specific adaptations. [R14; S, “Transformer mathematics”]

## 12.2 A two-position calculation

Suppose the scaled compatibility scores for one query are $(0,\log3)$. Softmax gives weights $(0.25,0.75)$. Let the two value vectors be $(2,0)$ and $(0,4)$. The output is

$$0.25(2,0)+0.75(0,4)=(0.5,3).$$

This calculation shows exactly what attention does at that query. It does not prove that the weights explain a procedural decision or correspond to causal importance in the real world. A weight is part of a learned computation; its interpretation depends on the rest of the network.

Multiple heads use separate projections and can combine different relations. Their outputs are concatenated and projected. Increasing the number of heads changes the parameterization and interaction structure, but not the requirement to define which positions are available.

## 12.3 Position and order

Without positional information, a basic self-attention operation does not inherently encode that one input occurred before another. The original sinusoidal positional representation is

$$PE(pos,2i)=\sin\left(\frac{pos}{10000^{2i/d}}\right),$$

$$PE(pos,2i+1)=\cos\left(\frac{pos}{10000^{2i/d}}\right).$$

Learned or relative-position schemes provide alternatives. For procedural work, the essential requirement is not a particular formula but a representation of order and separation. Insertion followed by removal is different from removal followed by insertion, even if the same local appearances occur.

**Implementation qualification.** Index positions assume a sampling grid. If inputs have irregular timestamps because of dropped frames or variable feature availability, positional distance may no longer equal elapsed time. Preserve timestamp and gap information or resample under a declared policy. A position encoder cannot repair an undisclosed time mapping.

## 12.4 The cost of full attention

The score matrix $QK^\top$ contains $N^2$ entries. At two features per second over eight hours, $N=57{,}600$ and $N^2=3{,}317{,}760{,}000$. Materializing one such matrix in float16 requires about 6.64 billion bytes, before other activations or heads. The report uses this calculation to argue against dense attention over an entire shift. [S, “Why vanilla full attention is awkward for an eight-hour shift”]

Optimized attention implementations can avoid materializing the complete score matrix, so the figure is a memory calculation for a materialized implementation, not a universal memory requirement. The number of pairwise interactions remains the reason to consider locality. Remembering that an earlier prerequisite was completed does not require every current token to interact densely with every frame of the whole build.

## 12.5 Local attention and long-term procedure memory

A local causal attention window permits keys from $\max(1,t-w+1)$ through $t$. Its interaction work is proportional to $Nw$ rather than $N^2$ for fixed $w$. Several layers can expand effective temporal support beyond one layer's window, so calculate the complete model's dependencies.

The procedure memory can preserve durable facts outside this local window. A fact such as `inserted_left_fastener=true` is a compact state entry with an evidence reference. The temporal model need not retain all earlier visual tokens merely to access that fact. This is the same separation between local action context and procedure memory proposed in the research. [S, “Use two timescales”]

ASFormer adds local inductive structure, hierarchical temporal organization, and refinement for action segmentation. Its purpose is not simply to replace every convolution with unrestricted attention. ActionFormer uses local self-attention and multiscale temporal features for temporal action localization, a related but different output task. Their original task definitions and architectures should be respected when selecting an implementation. [R15; R16]

## 12.6 Coarse-to-fine representations

A fine temporal stream preserves rapid changes and boundary detail. A coarse stream summarizes longer intervals. Fusion can align the coarse representation back to the fine grid:

$$H^{fine}=f(E),\qquad H^{coarse}=g(\operatorname{Downsample}(E)),$$

$$H=\operatorname{Fuse}(H^{fine},
\operatorname{Upsample}(H^{coarse})).$$

The formula is an architectural pattern, not a specification of one named model. Downsampling, pooling, interpolation, and temporal alignment all affect what information is available at a boundary. A noncausal upsampling or pooling policy can introduce future evidence even when a later attention mask is causal.

C2F-TCN is a named coarse-to-fine temporal segmentation architecture. Coarse-Fine Networks are another named multiresolution design associated with temporal activity detection. They should not be treated as synonyms or cited as though they solve an identical output problem. [R17; R18]

## 12.7 The ambiguous abbreviation CFF

The supplied report does not identify one specific paper or implementation meant by “CFF.” It presents three possible interpretations: cross-frame fusion, coarse-to-fine fusion, and cross-feature fusion. This edition retains that uncertainty rather than assigning the abbreviation to an invented universal worker-action model. [S, “What does CFF mean?”]

Cross-frame fusion combines information across nearby frames or clips. Coarse-to-fine fusion combines temporal resolutions. Cross-feature fusion combines modalities such as RGB, pose, tools, parts, audio, or telemetry. A system can use all three patterns at once, but its design should name the actual operations and interfaces rather than relying on the abbreviation.

For an experiment, replace “add CFF” with a precise statement: “concatenate a causal two-second RGB feature with the most recently available semantic feature and its age mask,” or “fuse a fine stream with a downsampled stream using causal interpolation.” The precise description is testable and reproducible.

## 12.8 Choosing a comparison

Compare a local Transformer with the causal TCN under matched input features, data splits, permitted lookahead, and operational metrics. A larger model evaluated with unlimited future context is not an isolated test of attention versus convolution.

The report's model-family comparison is a qualitative engineering guide. Latency, data needs, and accuracy depend on sequence length, width, implementation, and hardware. Treat the table as a way to form hypotheses, not as a benchmark ranking. The simplest model that meets the actual accuracy, boundary, and latency contract remains a valid outcome.

## 12.9 Exercises

**Exercise 12.1.** Reproduce the attention output for weights $(0.25,0.75)$ and values $(2,0)$ and $(0,4)$. What changes if the second key is masked out?

**Exercise 12.2.** At 57,600 positions and a local window of 128, compare $Nw$ with $N^2$. What does this comparison count, and what does it not establish about measured runtime?

**Exercise 12.3.** Rewrite the requirement “use CFF to improve the model” as one precise, causal fusion experiment with a baseline and a measurable outcome.

## 12.10 What follows

Attention, convolution, and multiresolution fusion offer different ways to construct temporal evidence. None determines procedural correctness on its own. The next chapter connects that evidence to structured state while preserving the possibility of observing an invalid action sequence.

# 13. Hybrid recognition and procedure decoding {#ch13}

A hybrid system combines learned visual evidence with explicit procedure structure. The combination is useful only when it preserves the distinction between what was observed and what should have happened. This chapter develops a scored neural–HSMM decoder, clarifies the meaning of neural emissions, and addresses a consequential failure mode: a normal-procedure constraint can hide an actual procedural error by relabeling the evidence.

## 13.1 Combining complementary terms

Let a neural temporal model produce log evidence $\ell_t(k)$ for action $k$. Let a candidate segmentation contain labels $z_m$, durations $d_m$, and intervals $I_m$. A segmental hybrid score can be written

$$\begin{aligned}
S(\mathcal S)={}&\log\pi_{z_1}
+\sum_m\sum_{t\in I_m}\ell_t(z_m)\\
&+\lambda_A\sum_{m=2}^{M}\log A_{z_{m-1},z_m}
+\lambda_D\sum_{m=1}^{M}\log p_{z_m}(d_m).
\end{aligned}$$

The observation term describes how the video supports each action. The transition term describes sequence compatibility. The duration term describes interval plausibility. The report makes this decomposition the central reason to combine a temporal neural model with an HSMM or procedure graph. [S, “Neural model plus structured decoder”]

The transition sum here occurs at segment boundaries. Applying the same segment-level transition matrix at every interior position would mix an HMM-style dwell model with explicit duration and change the intended score. This is an implementation clarification, not a claim that the report supplied a complete production decoder.

## 13.2 Neural posteriors are not automatically emissions

A discriminative classifier estimates $q_t(k)\approx p(y_t=k\mid E)$. A generative HMM emission is $p(e_t\mid z_t=k)$. The report uses a schematic proportionality between neural logits and log emission evidence. That is a useful interface sketch but does not establish a generative likelihood model.

**Implementation qualification.** Under an idealized classifier with the appropriate training prior, Bayes' rule gives

$$\log p(e_t\mid k)=\log p(k\mid e_t)-\log p(k)+C(e_t),$$

where $C(e_t)$ does not depend on the candidate state. This suggests prior correction when interpreting posteriors as likelihood-related scores. The identity does not automatically apply unchanged when the classifier uses a long context, has shifted priors, or is miscalibrated.

A simpler and often more honest description is a **scored discriminative hybrid**: use neural log probabilities or logits as potentials, tune their relative weights with transition and duration potentials, and calibrate the resulting decisions on held-out data. Do not label the final score a calibrated joint probability unless the assumptions and normalization justify that label.

Temperature scaling and the weights $\lambda_A,\lambda_D$ affect the balance. An overly strong transition term can ignore convincing visual evidence. An overly strong observation term can produce fragmentation. Their values should be selected on validation or calibration data according to the operational objective, not on the final test set.

## 13.3 How a strict normal graph can erase a mistake

Suppose the normal sequence is A, B, C. The video strongly supports A followed directly by C. A decoder that permits only A-to-B-to-C paths cannot return A-to-C. It must reinterpret some observations as B, remain in A longer, or declare the sequence impossible.

```text
visual evidence:       A A A C C C
strict normal decode:  A A A B C C
actual question:       was B omitted before C?
```

If the error engine reads only the strict decoder's output, it sees B and may conclude that the prerequisite occurred. The model has converted a normative constraint into an asserted observation. This conflicts with the source's foundational distinction between recognition and correctness, so the implementation must resolve it explicitly.

**Implementation qualification.** Preserve an observation-driven path or score stream separately from the normal-procedure path. Alternatively, include labeled skip or violation transitions in an expanded observation model. A hard-constrained normal graph remains useful as a comparator or hypothesis, but it should not be the only account of what occurred when violations are the target of detection.

## 13.4 Three workable designs

One design uses two outputs: a temporal action estimate that permits unexpected transitions, and a normal-procedure decoder that expresses expectations. Their disagreement becomes structured evidence for the error engine. This is easy to inspect because the observed label and expected label remain distinct.

A second design expands the graph with explicit violation transitions. For example, A-to-C can be allowed as an observed transition annotated with `missing_B`. The model can then represent the error without rewriting C as B. This requires careful graph design so that error edges do not overwhelm normal evidence or become undocumented shortcuts.

A third design maintains several procedure hypotheses, including uncertainty about whether a prerequisite occurred during a gap. The monitor propagates those alternatives and delays a strong conclusion until later evidence resolves them. This is more complex but matches situations in which the camera does not continuously observe the relevant action.

The supplied research recommends hybrid inference but does not select among these specific implementations. They are alternatives developed here from its separation of observed action and procedural validity.

## 13.5 A score-gap diagnostic

With identical scoring conventions, let $S_{all}^*$ be the best score over an expanded set of observed paths and $S_{valid}^*$ the best score restricted to valid paths. If the valid set is a subset of the expanded set, then

$$\Delta=S_{all}^*-S_{valid}^*\geq0.$$

A large gap means that the best valid explanation fits the evidence worse under the chosen score. It is a useful diagnostic, not automatically an error probability. The gap can also grow because of unfamiliar motion, a wrong procedure version, poor observation quality, or a duration mismatch.

Compare score gaps only under matched evidence scaling and normalization. A score summed over a longer interval tends to have a different scale from one summed over a short interval. Normalizing or calibrating by context length may be appropriate, but it is another design choice to validate.

## 13.6 Factorized action compatibility

The report proposes combining verb and noun estimates with a compatibility function:

$$p(a_t=(v,n))\propto p(v_t\mid h_t)p(n_t\mid h_t)\psi(v,n).$$

The factor $\psi$ can suppress impossible combinations or express learned compatibility. The product is a modeling approximation; the heads share features and need not be statistically independent. The same approach can include tool and location factors. [S, “Verb/noun decoders”]

Use compatibility to describe plausible actions, not to erase an observed wrong tool. A compatibility table defining only “correct tool for action” belongs in a procedural judgment or comparative hypothesis. If it removes every wrong-tool combination from the observation vocabulary, wrong-tool detection faces the same suppression problem as strict normal-path decoding.

## 13.7 A trace with separate responsibilities

A useful trace makes the evidence sources visible:

```text
Action evidence
  observed action: tighten_left_fastener
  calibrated action confidence: 0.94

Procedure evidence
  required fact: inserted_left_fastener
  fact status: false under complete observation
  procedure version: bracket-v7

Decision
  candidate: wrong_order
  reason code: unmet_insertion_prerequisite
  observation path retained: align -> tighten
  normal-path hypothesis retained separately: align -> insert -> tighten
```

Changing the fact status to `unknown` after an observation gap should change the judgment to insufficient evidence without changing the action label. That is an invariant worth testing in every implementation.

## 13.8 Exercises

**Exercise 13.1.** Explain why applying a normal-only transition graph before error detection can conceal an omitted step. Propose one design that preserves the evidence.

**Exercise 13.2.** Under the idealized Bayes relation, a class posterior is 0.4 and its training prior is 0.1. Another class has posterior 0.5 and prior 0.5. Compare the posterior-to-prior ratios and explain why they are not normalized posterior probabilities.

**Exercise 13.3.** A best expanded-path score is -30 and the best valid-path score is -38. Interpret the gap of eight without calling it an error probability. Name two non-error causes of a large gap.

## 13.9 What follows

Structured constraints are valuable when their role is explicit. They can describe expectations, improve a hypothesis, or identify a violation, but they must not silently rewrite the only observation record. The next chapter turns these separate evidence streams into typed, persistent, reviewable error decisions.

# 14. Typed errors and incident state {#ch14}

An error label is useful when it names the violated condition and the evidence supporting that conclusion. A single normal-versus-anomalous score cannot explain whether a step was omitted, a tool was wrong, or the camera simply stopped observing. This chapter builds a typed error engine and distinguishes a momentary suspicion from a reportable incident.

## 14.1 An error ontology

The report recommends explicit error categories rather than beginning with an undifferentiated binary anomaly classifier. The categories require different evidence. [S, “Typed error detection”]

| Error type | Evidence needed for the judgment |
|:--|:--|
| Omitted step | A required opportunity has closed without supported completion. |
| Wrong order | An observed action conflicts with established prerequisite state. |
| Wrong part | The manipulated part is identified and incompatible with the step. |
| Wrong tool | Tool use is observed and violates the procedure's tool condition. |
| Excess duration | An ongoing or completed duration is unusual under the relevant model. |
| Incomplete step | Duration and/or a required postcondition indicate incomplete execution. |
| Repetition | An operation instance is repeated outside allowed procedure behavior. |
| Incorrect rework | A return or repair path conflicts with the authorized rework rules. |
| Unsafe region | A spatial observation violates a defined region rule. |
| Unknown anomaly | Evidence is unusual but not reliably assigned to a known error type. |

This table refines the report's short descriptions with evidential conditions. It does not establish a safety-certified monitoring system. In particular, a spatial alert or an unusual duration is not equivalent to proof of a harmful outcome.

## 14.2 Omission is not a continuously applicable label

At the beginning of a build, many required steps have not occurred. They are pending, not omitted. A step becomes an omission candidate when a defined opportunity closes: a dependent action begins, a phase is finalized, or the build is declared complete.

**Implementation qualification.** Let $r$ be a required step and $C_r$ the event that closes its opportunity. A useful rule is not merely “$r$ is absent from completed steps.” It is “$C_r$ has occurred, $r$ is not established, and the observation conditions support a negative conclusion.” When those conditions do not hold, the result is pending or uncertain.

For example, tightening may close the insertion opportunity. If insertion was continuously observable and no supported insertion occurred, the monitor can form a wrong-order or omission candidate. If a hand or tool obscured the entire insertion opportunity, the missing fact may remain unknown. Later telemetry or review may resolve it, but the immediate video record does not justify treating the two situations identically.

## 14.3 Three-valued prerequisite state

A prerequisite can be true, false, or unknown. True means that the required fact is established under the chosen evidence policy. False means that available evidence supports its absence in the relevant context. Unknown means that the system lacks enough evidence to choose between them.

For an action requiring several facts, all must be true for a supported valid transition. A known false prerequisite can support a candidate violation. Unknown prerequisites require an uncertainty policy. A mixture of false and unknown facts should preserve both rather than collapsing the whole record into a single confidence number.

```text
action = tighten
inserted = true     -> prerequisite supported
inserted = false    -> wrong-order candidate
inserted = unknown  -> insufficient-evidence judgment
```

This rule elaborates the report's distinction between missing observation and omitted action. It also prevents the phrase “not seen” from becoming a hidden synonym for “did not happen.”

## 14.4 Duration evidence and postconditions

A duration score can identify an unusual interval. It does not identify its cause. A long tightening action might indicate difficulty, rework, a mislabeled idle interval, or a real process issue. A short action might be correct under a different tool setting or incomplete under the current specification.

Use the duration model appropriate to the product, tool, and boundary definition. For an ongoing interval, use age and survival consistently, as developed in Chapter 9. For a completed interval, combine duration with observed postconditions when available. Do not infer a torque requirement was met solely because the visual action lasted a typical number of seconds.

A typed record might retain `duration_outlier` as evidence while leaving `incomplete_step` uncertain. This is more informative than immediately converting every low-likelihood duration into a confirmed procedural error.

## 14.5 Candidate, violation state, and incident

A noisy score can cross a threshold briefly. A stateful gate distinguishes this candidate condition from a persistent incident. The report points to VSS Behavior Analytics' separation between violations, tracked violation state, and incidents. The checked documentation supports this persistence pattern for its spatial-incident framework. [R25; S, “Error persistence and hysteresis”]

A simple application policy uses a high threshold to start an episode and a lower threshold to clear it:

```text
NORMAL -- score >= high --> POSSIBLE
POSSIBLE -- duration reached --> INCIDENT
POSSIBLE or INCIDENT -- score < low --> NORMAL
any state -- observation unavailable --> explicit gap handling
```

The lower clearing threshold creates hysteresis. It prevents a score fluctuating just below the start threshold from repeatedly opening and closing the same episode. The persistence interval is measured in elapsed time, not a fixed frame count, unless the frame timing is guaranteed.

## 14.6 A concrete persistence trace

For high threshold 0.8, low threshold 0.3, and one second of persistence:

| Time, seconds | Score | Gate output |
|--:|--:|:--|
| 0.0 | 0.10 | normal |
| 0.5 | 0.85 | possible |
| 1.0 | 0.90 | possible |
| 1.5 | 0.88 | incident |
| 2.0 | 0.20 | normal |

The incident begins one second after the episode starts at 0.5 seconds. In this policy the episode can remain open while the score lies between low and high. That is different from requiring every score throughout persistence to exceed the high threshold; either policy can be defined, but they should not share an undocumented implementation.

A missing sample must not silently contribute elapsed positive evidence. The laboratory cancels its small gate's persistence state and emits `observation_gap`. That simplification is not a complete production incident lifecycle. A production system should retain the existing incident record and mark its subsequent observation state rather than interpreting a gap as proof of recovery.

## 14.7 Persistence has a cost

Persistence can reduce false alerts from short score spikes, but it also delays detection and can suppress genuinely brief errors. Use error-specific policies. A transient but consequential wrong-part insertion may not be appropriately handled by the same duration threshold as a prolonged waiting condition.

The report's suggested 0.5–2-second persistence range is an engineering starting point. It is not an operational guarantee. Select persistence and hysteresis using held-out sequences and report both false alerts per operating hour and missed errors per completed build. The exact time at which an error becomes observable matters when interpreting the added delay. [S, “Recommended starting configuration”; S, “Error metrics”]

## 14.8 Evidence records and deduplication

An incident should preserve build identity, procedure version, involved parts or tracks, the candidate error type, evidence intervals, relevant state facts, model versions, and the decision rule. Give it a stable identifier so retries do not create duplicate operator alarms.

Keep observation evidence separate from workflow status. A reviewer acknowledging an alert does not make the error true; rejecting an alert does not change the recorded action probabilities. Preserve those distinctions so that later model evaluation can use adjudicated labels without overwriting the original decision trail.

## 14.9 Exercises

**Exercise 14.1.** Why is a required step not automatically omitted merely because it has not occurred yet? Define a closure event for insertion in the bracket procedure.

**Exercise 14.2.** Apply the gate policy to scores 0.85, 0.55, and 0.60 at times 0.0, 0.5, and 1.0 with high 0.8, low 0.3, and one-second persistence. Does an incident occur under this hysteretic policy?

**Exercise 14.3.** A tool disappears behind the worker's hand for two seconds. Explain why both “wrong tool” and “problem resolved” may be unsupported conclusions during that interval.

## 14.10 What follows

A typed error engine turns explicit procedural conditions into traceable decisions. Persistence changes when a decision becomes reportable, not what evidence the underlying claim requires. The next chapter adds a slower semantic verifier without allowing it to invent missing evidence or hide candidate-detector failures.

# 15. Vision-language verification {#ch15}

A vision-language model can inspect a selected clip and describe evidence relevant to a candidate error. That makes it useful as a verifier, especially when a fast detector produces cases that benefit from broader semantic interpretation. This chapter defines a verification contract that preserves the candidate, the available evidence, and the possibility that the clip cannot resolve the question.

## 15.1 Why verify selected candidates

The report recommends a fast temporal and procedural detector followed by optional VLM verification rather than repeatedly asking a VLM to determine every dense action label. The proposed division gives the fast path explicit timing and state behavior, while the slower path examines a focused evidence interval. [S, “The VLM should verify, not continuously adjudicate every frame”]

The checked VSS Alert Verification Microservice supports the corresponding infrastructure pattern: it accepts upstream incidents, obtains timestamped video through VIOS, and produces a verification result. This is a useful integration point, not evidence that the service already understands a custom fastening procedure. The application still defines the candidate, procedure context, prompt, and interpretation policy. [R24]

The verifier should answer a bounded question. “Is this worker doing everything correctly?” is broader than a short clip can establish. “Does the visible tool use in this interval contradict the required tool condition for this operation?” specifies the claim and the evidence being tested.

## 15.2 Constructing an evidence packet

An evidence packet should include the candidate type, time interval, observed action, relevant prerequisites, procedure version, available camera views, and known observation gaps. Keep factual fields distinct from hypotheses so the verifier is not encouraged to treat the candidate as established truth.

```json
{
  "candidate_id": "candidate-028",
  "candidate_type": "wrong_order",
  "observed_action": "tighten_left_fastener",
  "candidate_interval_s": [82.4, 85.75],
  "procedure_version": "bracket-v7",
  "required_prior_fact": "inserted_left_fastener",
  "prior_fact_status": "unknown",
  "evidence_interval_s": [77.4, 90.75],
  "observation_gaps_s": [[79.0, 81.0]],
  "claim_to_test": "Was tightening begun before insertion?"
}
```

The packet is a textbook application contract, not a direct vendor payload. A downstream adapter can translate it into the service's supported schema while retaining the richer domain record in the application store.

## 15.3 Absence in a clip is not proof of omission

The report gives an example verifier output confirming wrong order because insertion was not visible before tightening. That wording requires qualification. A short clip may start after insertion, may contain an occlusion, or may not show the relevant mounting point. Not seeing insertion in that clip does not, by itself, prove insertion did not happen.

**Implementation qualification.** A verifier should distinguish observed contradiction from insufficient coverage. Confirmation of an omission or wrong-order claim requires evidence that supports the relevant negative fact, not merely the absence of a depiction in a limited clip. This preserves the report's broader warning about unavailable observation.

A suitable result for the packet above is:

```json
{
  "candidate_id": "candidate-028",
  "judgment": "uncertain",
  "visible_facts": [
    "Tightening motion is visible near the left mounting point."
  ],
  "unresolved_facts": [
    "Insertion may have occurred during the observation gap."
  ],
  "evidence_adequacy": "insufficient_for_order_claim",
  "explanation": "The clip does not establish the prerequisite history."
}
```

This output still contributes useful information: it supports the action observation while limiting the procedural conclusion. Uncertainty is not an empty result when it identifies the missing evidence.

## 15.4 Prompting for evidence rather than agreement

State the procedure rule and candidate as separate fields. Ask for visible supporting facts, visible contradictions, and unresolved facts. Require the model to retain an uncertainty outcome when the evidence is inadequate. Ask for a concise explanation tied to the provided interval rather than an unrestricted narrative.

A prompt can say: “Assess whether the supplied evidence supports the candidate. Treat the candidate as a hypothesis. Do not infer an unobserved prerequisite from the expected procedure. Distinguish absence of visibility from evidence of absence.” This is a teaching prompt template and requires validation on the target error types.

When procedure documents are included, treat their content as task data rather than a source of executable instructions. The application should control output fields and allowed downstream actions. A description in a video frame or a retrieved document should not be able to change the incident-routing policy.

## 15.5 Service status and epistemic uncertainty

The VSS 3.1 documentation uses `confirmed`, `rejected`, and `unverified` as service verdicts, with `unverified` associated with incomplete verification due to errors. The report's application diagram uses an `uncertain` outcome. These concepts should not be silently equated. [R24; S, “The architecture I would build first”]

**Implementation qualification.** Preserve separate fields for service execution status and evidential judgment. A timeout is a service failure. A successfully processed clip that does not show the prerequisite is epistemically insufficient. Both may require review, but they have different causes and different implications for system reliability.

A schema adapter should store the original vendor verdict and response status, then derive an application judgment under a versioned mapping. An invalid or incomplete response should not be coerced into `rejected`, because “could not verify” is not evidence that the candidate is false.

## 15.6 Cascaded evaluation

A verifier can inspect only candidates it receives. If the upstream detector misses an error, candidate-only verification cannot recover it. Let $R_c$ be candidate recall and $R_v$ the verifier's probability of accepting a true candidate conditional on that candidate being generated. Then, for a policy that reports only accepted candidates,

$$R_{final}=R_cR_v.$$

This identity uses a conditional probability; it does not assume independent stages. With $R_c=0.90$ and $R_v=0.95$, final recall is 0.855. Precision may improve while recall falls. Report both changes, along with how uncertain and failed verifications are routed.

A reviewer policy can alter the final outcome, but its effect must be measured rather than assumed. Evaluate the candidate detector, verifier-on-candidates, and complete final policy separately. Also evaluate verification latency and backlog, because a useful judgment delivered too late may not support immediate assistance.

## 15.7 Evidence-window and capacity costs

Retrieving a clip extending several seconds after an event necessarily waits for those future seconds in live operation. This delay belongs in the verification latency budget. A wider interval may improve context while increasing retrieval and inference cost.

A verifier pool has finite capacity. If candidates arrive faster than they can be processed, the queue grows even if each individual inference is fast. Use bounded queues, a defined overload policy, and a way to preserve unresolved candidates. Silent dropping produces a misleading impression of low alert volume.

The report suggests short evidence clips around candidates as a starting approach. Actual margins, sampling, and concurrency should be selected through measurements on the deployed service and the kinds of evidence each error requires. [S, “Latency mathematics”; S, “Recommended starting configuration”]

## 15.8 Exercises

**Exercise 15.1.** A clip shows tightening but begins after the insertion opportunity. Can it independently confirm that insertion was omitted? What additional evidence would be required?

**Exercise 15.2.** Candidate recall is 0.92 and verifier acceptance of true candidates is 0.90. Calculate final recall for a confirmed-only policy.

**Exercise 15.3.** Design output fields that distinguish a successful but inconclusive verification from a timeout. Explain why mapping both to “candidate false” would corrupt evaluation.

## 15.9 What follows

Verification adds evidence and semantic interpretation; it does not grant access to events outside the observation record. Its benefit must be measured at the complete decision-policy level. The next chapter specifies the live timing, state, and failure behavior that determine which evidence is available in the first place.

# 16. Streaming inference and latency {#ch16}

A model that processes stored features can access information in a different order from a live service. Streaming deployment therefore requires more than a fast inference call. It needs a time model, an ownership model for state, a commitment policy for predictions, and explicit behavior under missing or late observations. This chapter makes those contracts concrete.

## 16.1 Event time and availability time

Event time describes when something occurred in the observed process. Availability time describes when the system had the required evidence or message. Processing time describes when a service performed its computation. These timestamps can differ substantially.

A clip covering $[100,102)$ cannot be fully observed at time 100. A feature representing that clip may become available after decoding and encoding. A temporal prediction attached to its midpoint may therefore be delayed even when the neural computation itself takes only milliseconds.

Store the evidence interval and availability time with each feature. A replay system intended to evaluate live behavior should reveal features according to availability, not simply make the entire recording accessible before the first decision. This is an implementation elaboration of the report's offline-versus-streaming distinction. [S, “What the model actually predicts”; S, “Latency mathematics”]

## 16.2 Latency is a path through the system

The report decomposes step latency into capture, decoding, window acquisition, embedding, temporal inference, and lookahead. It adds persistence, clip retrieval, and verification for alerts. These terms make clear why model inference latency alone is insufficient. [S, “Latency mathematics”]

A useful measurement is

$$L_{decision}=t_{decision\ emitted}-t_{relevant\ event\ observable}.$$

The reference event must be defined. For an omission, it may be the closing of an opportunity rather than the beginning of the build. For a wrong tool, it may be the first interval in which tool identity and use are distinguishable.

**Implementation qualification.** Add only nonoverlapping waiting and processing intervals on the decision's critical path. A past-looking two-second buffer has a startup acquisition cost, but it does not necessarily add a fresh two-second wait to every later decision. Similarly, waiting for a verifier's post-event context may overlap with candidate persistence. Summing both full intervals without considering overlap double-counts time.

## 16.3 A worked timing trace

Consider a synthetic event becoming observable at time 100.00 seconds. The chosen recognition policy requires one second of future evidence. Subsequent decode, encoder, queue, and temporal processing total 0.19 seconds. Candidate persistence adds one second. The evidence clip must be recorded through 103.00 seconds, retrieval takes 0.20 seconds, and verification takes 1.50 seconds.

| Milestone | Time, seconds |
|:--|--:|
| Event becomes observable | 100.00 |
| Required recognition evidence exists | 101.00 |
| Step decision emitted | 101.19 |
| Candidate persistence satisfied | 102.19 |
| Verification clip fully available | 103.00 |
| Clip retrieved | 103.20 |
| Verification emitted | 104.70 |

The step delay is 1.19 seconds and the final verification delay is 4.70 seconds. Only 0.81 seconds of the post-context wait remains after candidate generation. These values are a constructed timing example, not measured VSS performance.

Measure latency distributions on the deployed pipeline. The 95th percentile of a sum is not generally the sum of the individual 95th percentiles. Correlations, batching, and queueing can change the combined distribution. Report the end-to-end distribution as well as component timings.

## 16.4 State ownership

The report describes application-owned state and server-owned sequence state, recommending application-owned state for a first inspectable implementation. The application can keep a rolling feature buffer, call a stateless temporal model, and maintain a separate procedure record. [S, “Per-stream state”]

A state key should identify the procedure execution, not merely the camera. One camera may observe several workpieces, and one workpiece may move across cameras. The association mechanism is application-specific and not supplied by the research. When only one worker and one build occupy a station, the association can be simple; when that assumption fails, the system must not silently apply a single global step state to several subjects.

A record might contain:

```yaml
build_id: build-041
procedure_version: bracket-v7
stream_epoch: 3
last_feature_sequence: 184
committed_through_s: 90.0
active_segment:
  step: tighten_left_fastener
  provisional_start_s: 88.5
facts:
  inserted_left_fastener: true
pending_candidates: []
```

This is an application design, not a vendor state schema. Store evidence references with the facts so that later invalidation or review can explain their origin.

## 16.5 Provisional and committed output

A live segment often has a known or estimated start but no known end. Emit a provisional record or an explicit active-segment state rather than fabricating an end time. When later evidence establishes the boundary, create a revision or completion event.

A fixed-lag policy commits positions older than a declared delay. A revision policy permits later changes and requires consumers to process segment identifiers and revision numbers. An irrevocable policy forbids such changes and must be evaluated at the time of commitment. None is inherently the same as full offline Viterbi decoding.

For an HSMM, the current segment is unfinished and should be treated with an age or survival-aware rule. Repeatedly running an offline completed-segment decoder at every live prefix can create premature boundaries. It can be a prototype approximation, but its output semantics must acknowledge that approximation.

## 16.6 Ordering, retries, and recovery

Messages may be duplicated, delayed, or delivered out of event-time order. Give features a stream or execution identity, sequence number, evidence interval, and encoder version. Deduplicate using a stable identity rather than comparing floating-point timestamps alone.

Choose a bounded reordering policy. A watermark can state that events earlier than a time are considered complete under the service's lateness allowance. The term simply denotes a commitment boundary for event-time processing; it does not guarantee that no later message will arrive. Late messages need a documented correction, review, or rejection policy.

Checkpoint the procedure state together with the consumed-message position. On restart, replay should not create duplicate step completions or duplicate incident notifications. This is a textbook production requirement derived from stateful processing, not a behavior automatically supplied by using a particular broker.

## 16.7 Observation gaps

The report requires explicit unknown and observation-gap states. A missing camera interval means observation is unavailable, not that the worker stopped or omitted a step. [S, “Fault handling”]

A gap policy should specify the effect on the visual buffer, active segment, duration age, prerequisite facts, and open incidents. Some previously established facts remain valid; others may become uncertain because an unobserved removal or rework operation could invalidate them. Clearing all state or preserving all state without analysis can both be wrong.

When the stream returns, record a new stream epoch if identifiers or timestamps have reset. Reestablish the relation between the current workpiece and procedure state. A clean image after a gap does not automatically establish the missing procedural history.

## 16.8 Capacity and backpressure

With $C$ streams and feature stride $\Delta$, the nominal feature arrival rate is $C/\Delta$ per second. At 20 streams and a half-second stride, that is 40 feature requests per second before batching. The service rate must be measured under the actual model, batch policy, and hardware.

A bounded queue needs an overload policy. Dropping old action evidence can damage procedure state; dropping duplicate context features may have a different effect. The system should disclose any degraded coverage to downstream error logic rather than continue to issue confident judgments from an incomplete stream.

## 16.9 Exercises

**Exercise 16.1.** Reproduce the 4.70-second verification delay in the worked trace. Why would adding a separate full three-second post-context wait after candidate generation overcount latency?

**Exercise 16.2.** A service receives 12 streams with a 0.25-second feature stride. What is the nominal feature arrival rate, and why does that number alone not determine GPU capacity?

**Exercise 16.3.** A camera restarts and reuses track ID 17 for a different workpiece. Which identity and state fields can prevent the new track from inheriting the old build's prerequisites?

## 16.10 What follows

Streaming correctness depends on when evidence exists and how state survives time, revisions, and failures. These contracts should be tested through replay before operator-facing deployment. The next chapter maps the design onto VSS and Triton without confusing infrastructure capabilities with the custom procedure model.

# 17. NVIDIA VSS and model serving {#ch17}

The research assigns VSS a production infrastructure role: ingest video, run or coordinate perception and semantic services, transport metadata, retrieve evidence, and support downstream analytics. It does not identify VSS as a pretrained fine-grained worker-step classifier. This chapter preserves that boundary and defines the custom interfaces needed around a temporal model and procedure engine.

## 17.1 The documented infrastructure boundary

The checked VSS 3.1.0 architecture separates real-time video intelligence, downstream analytics, and agentic or offline processing. Its real-time services include computer vision, embeddings, and VLM processing; downstream components include behavior analytics and alert verification. VIOS provides the video input, storage, and retrieval layer. [R21; R26]

The report's proposed mapping is therefore architectural rather than a claim of an out-of-the-box assembly application. A custom short-window encoder, temporal segmenter, procedure-state service, and typed error engine remain application responsibilities. [S, “Where VSS fits”]

| Application responsibility | Infrastructure or custom component |
|:--|:--|
| Camera registration, recording, replay | VIOS integration. |
| Worker, part, and tool observations | RT-CV and/or custom perception. |
| Broad semantic video representation | RT-Embedding and selected embedding model. |
| Fine-motion features | Custom short-window video encoder. |
| Dense step probabilities | Custom TCN or local Transformer service. |
| Procedure and duration state | Custom HSMM and fact-state service. |
| Error candidates | Custom typed error engine. |
| Selected evidence verification | Alert-verification integration and a configured VLM. |
| GPU model execution | Triton where appropriate to the deployment. |
| Durable application records | Versioned event and state stores. |

This table is the book's proposed service assignment. It should not be read as a list of vendor guarantees about arbitrary custom models.

## 17.2 A service graph

```text
camera -> VIOS -> recorded evidence
             |
             +-> perception -> tracks, tools, parts
             |
             +-> short-window encoder ----+
             |                             |
             +-> semantic embeddings ------+-> temporal model
                                                   |
                                      action evidence + segments
                                                   |
                                        procedure-state service
                                                   |
                                           typed error engine
                                                   |
                                      candidate + evidence request
                                                   |
                                      selected VLM verification
                                                   |
                                         event store / review UI
```

Keep the step-event path independent of the optional verifier. A verifier outage should not stop all action recognition unless the operational contract explicitly requires that coupling. Conversely, continuing step events during a verifier outage does not justify labeling pending candidates as rejected.

The report's two-timescale design fits naturally here: short local feature history in the temporal service and durable procedural facts in the state service. The boundary makes each component easier to inspect and allows a model update without necessarily replacing the procedure representation.

## 17.3 Versioned embedding integration

The VSS 3.1 RT-Embedding documentation supports configurable video chunks and overlap, uploaded media or live streams, and optional Kafka output using `nv.VisionLLM`. Its documented default video-embedding topic is `vision-embed-messages`; the source report's `mdx-embed` should not be assumed to be that snapshot's default. [R22]

**Version qualification.** These are version-specific interface facts, not corrections to every possible VSS deployment. Read the configured topic and schema from the deployed service. The report's architectural proposal to consume embeddings remains unchanged.

An adapter should convert the vendor message into a stable application feature record. The adapter's contract can require sensor identity, evidence start and end, availability time, selected model, feature dimension, and a finite vector. Fields missing from the vendor message may need to be supplied by trusted ingestion metadata; they should not be guessed from a file name.

```yaml
application_feature:
  schema_version: 1
  build_id: build-041
  source_stream: cam-front
  evidence_start_s: 80.0
  evidence_end_s: 82.0
  available_at_s: 82.12
  encoder_id: local-video-encoder-v1
  vector_dimension: 384
  observation_status: available
```

The 384-dimensional value is an illustrative custom encoder setting. The adapter must validate the actual dimension rather than assume that every semantic model produces it.

## 17.4 Keep training data independent of runtime transport

VSS documents JSON and Protobuf schemas for runtime metadata and related objects. The report recommends keeping the canonical training annotations separate and writing adapters for runtime events. This avoids making a service's transport representation dictate the semantics of dense labels and adjudicated error judgments. [R27; R28; S, “How VSS fits the data layer”]

A training record needs annotation policy, boundary confidence, review provenance, and split identity. A runtime event needs delivery identity, timestamp semantics, schema version, and revision handling. Some fields overlap, but their purposes differ. Share definitions where useful; do not assume one serialized object is ideal for both tasks.

Application topics can be explicit and versioned:

```text
factory.step-features.v1
factory.step-probabilities.v1
factory.step-events.v1
factory.error-candidates.v1
factory.verified-errors.v1
```

These names are proposed application conventions, not NVIDIA defaults. A deployment manifest should record both the vendor topics and the application topics, including the adapter version between them.

## 17.5 Triton and model boundaries

Triton ensembles can connect component models such as preprocessing, encoding, projection, and postprocessing in a serving graph. Triton's documented batching mechanisms distinguish stateless dynamic batching from sequence-aware batching for stateful requests. [R29; R30]

Use a stateless clip encoder when requests from different cameras can be batched without sharing procedure state. Dynamic batching can improve hardware use but adds a batching wait, which belongs in the latency budget. The best batch policy depends on arrival patterns and the permitted delay.

For a first temporal deployment, application-owned rolling buffers keep state explicit while the inference endpoint remains stateless. Server-owned sequence state is an alternative when the model and backend contract support it. A sequence identifier does not, by itself, implement the application's prerequisite store, incident deduplication, or replay recovery.

## 17.6 Tensor and adapter tests

Define the temporal model contract independently of the deployment mechanism. The teaching TCN receives float features of shape $[B,d,N]$ and a Boolean validity mask of shape $[B,N]$, and returns stage logits of shape $[S,B,K,N]$. A production endpoint may expose only the final stage, but it should retain a documented axis order and class-index mapping.

Before integrating real streams, test mismatched dimensions, nonfinite features, incorrect class vocabularies, timestamp reversals, duplicated messages, and missing build associations. A service accepting malformed data without complaint can create errors that appear to be model failures but are actually adapter failures.

Use recorded vendor messages for adapter regression tests once an actual deployment exists. This edition does not include such recorded messages and does not claim that its teaching code has been deployed against VSS or Triton.

## 17.7 Security and access boundaries

The checked VSS known-limitations and secure-deployment documentation identifies security controls that must be supplied or strengthened by deployment infrastructure. It calls for a trusted, isolated environment rather than direct exposure of internal services to untrusted users, with controls such as authentication, TLS, rate limiting, and monitoring at the boundary. [R31; R32]

Apply the same reasoning to custom services. A feature consumer, evidence store, or procedure-state endpoint can expose sensitive video or operational information even when the neural model itself is protected. Restrict access to the data and control paths, not only to the GPU server.

Define retention and review access as application policies. Store the evidence needed to explain an incident while avoiding an assumption that every raw recording must remain accessible indefinitely. Those governance choices require the deployment organization's review; the research does not supply a jurisdiction-specific legal policy.

## 17.8 Exercises

**Exercise 17.1.** Which parts of the proposed system remain custom even when VSS is installed? Explain why an embedding service is not automatically a dense worker-step classifier.

**Exercise 17.2.** A consumer assumes the embedding dimension is 768 and silently truncates a longer vector. Why is this an interface failure, and what should the adapter do instead?

**Exercise 17.3.** Explain why using Triton sequence IDs does not eliminate the need for application-level build identity, procedure version, and incident deduplication.

## 17.9 What follows

The infrastructure should transport and execute well-defined application components, not obscure their semantics. Versioned adapters and explicit state ownership preserve the research's separation of responsibilities. The next chapter determines how to measure whether that complete system produces useful and trustworthy results.

# 18. Evaluation and calibration {#ch18}

A worker-action pipeline produces several outputs, so it needs several measurements. Frame accuracy tests label agreement, segment metrics test temporal structure, error metrics test procedural judgments, and latency and coverage metrics test whether those judgments are usable. This chapter defines those measurements and explains why confidence calibration and event-level evaluation cannot be replaced by one aggregate score.

## 18.1 Frame accuracy

For $N$ evaluated positions, frame or feature-position accuracy is

$$\operatorname{Accuracy}=\frac{1}{N}
\sum_{t=1}^{N}\mathbf1[\hat y_t=y_t].$$

State the sampling grid. Accuracy at feature positions is not automatically the same as accuracy over every raw frame. With irregular timestamps, a position-weighted average can differ from an elapsed-time-weighted average. Also state how background, unknown labels, and observation gaps are handled.

The report warns that high accuracy can coexist with severe fragmentation. Long, common actions can dominate the average while rare short actions are missed. Report class-level performance and segment-aware measures rather than interpreting the aggregate as a complete quality assessment. [S, “Frame accuracy is insufficient”]

## 18.2 Temporal intersection over union

For predicted interval $P=[s_p,e_p)$ and ground truth $G=[s_g,e_g)$, define intersection length

$$I=\max(0,\min(e_p,e_g)-\max(s_p,s_g)).$$

Then

$$\operatorname{tIoU}(P,G)=
\frac{I}{(e_p-s_p)+(e_g-s_g)-I}.$$

For $P=[2,6)$ and $G=[3,7)$, the intersection has length three and the union length five, giving tIoU 0.6. A higher threshold demands closer temporal agreement. The report discusses segmental F1 at thresholds 0.10, 0.25, and 0.50. [S, “Temporal IoU”]

Require the action classes to match as well as the overlap threshold. Matching must be one-to-one: two predicted segments cannot both count as true positives for the same ground-truth segment. Declare the matching algorithm and use the benchmark's reference scorer when reproducing a published comparison, because greedy and alternative matching rules can differ.

## 18.3 Segmental precision, recall, and F1

After matching, let TP count matched predictions, FP unmatched predictions, and FN unmatched truth segments. Then

$$P=\frac{TP}{TP+FP},\qquad R=\frac{TP}{TP+FN},\qquad
F_1=\frac{2TP}{2TP+FP+FN}.$$

If one true action is split into two overlapping predictions and only one can match, the other becomes a false positive. Frame accuracy may penalize the split only slightly; segmental precision penalizes the extra action explicitly.

Report whether counts are pooled across videos or scores are averaged per video. Micro-averaging weights examples through their counts, while macro-averaging gives equal weight to the chosen units or classes. A small set of very long sessions can otherwise dominate the result.

## 18.4 Edit score

Collapse consecutive duplicate labels to form symbolic action sequences. Compare the predicted and true sequences with Levenshtein distance $D$, the minimum number of insertions, deletions, and substitutions needed to transform one into the other. A common normalized similarity is

$$\operatorname{Edit}=100\left(1-
\frac{D(P,G)}{\max(|P|,|G|)}\right).$$

Define the both-empty case explicitly; the laboratory returns 100 when both collapsed sequences are empty. Declare whether background is removed and when it is removed. Removing background before or after collapse can merge actions differently.

```text
truth dense:      AAAABBBBCCCC
truth collapsed:  A B C
prediction:       AAAABABBBCCCC
pred collapsed:   A B A B C
```

Edit score tests ordering and fragmentation while largely ignoring small boundary shifts. It complements tIoU-based F1 rather than replacing it. The report uses precisely this distinction to explain why frame accuracy alone is insufficient. [S, “Edit score”]

## 18.5 Boundary quality

For matched segments, measure absolute start and end errors:

$$\Delta_s=|\hat s-s|,\qquad \Delta_e=|\hat e-e|.$$

Report median and tail quantiles, and the fraction within operationally meaningful tolerances such as half a second or one second when those tolerances match the application. The report recommends these timing summaries because they are easier to interpret operationally than frame accuracy alone. [S, “Boundary error”]

Boundary error on matched segments has selection bias: completely missed actions are absent from the matched set. Present the match rate and missed-segment counts beside timing statistics. Otherwise, a model can appear to have excellent boundaries simply because it detects only the easiest actions.

## 18.6 Error events and exposure

Evaluate each error category separately with event-level matching. Define the allowed time tolerance, build association, and deduplication policy. Repeated notifications about one mistake should not inflate true-positive counts.

The report emphasizes **false alerts per operating hour** and **missed errors per completed build**. These measures connect the detector to workload and consequences more directly than a frame-level anomaly score. Include valid-observation coverage: one false alert during one observed hour is not the same exposure as one false alert during eight hours of nominal operation with only one hour of usable video. [S, “Error metrics”]

A useful report distinguishes elapsed operating hours, valid-observation hours, completed builds, observable error opportunities, and adjudicated error events. The denominator is part of the measurement's meaning.

## 18.7 Rare-event precision

A detector can have a high true-positive rate and still produce many false alerts when errors are rare. Consider 10,000 independent illustrative decision opportunities, of which 100 contain an error. At 95 percent sensitivity and a 5 percent false-positive rate, there are 95 true positives and 495 false positives. Precision is

$$\frac{95}{95+495}\approx0.161.$$

Only about 16.1 percent of alerts are correct in this constructed example. This is not a performance estimate for the proposed system. It shows why class balance and false-alert exposure must be reported when selecting thresholds.

**Implementation qualification.** Observing zero false alerts in a small test does not establish a zero false-alert rate. Under a simple Poisson model with independent stationary events, zero alerts over $H$ hours gives a one-sided 95 percent upper rate bound of $-\log(0.05)/H\approx3/H$. The assumptions often need scrutiny in real correlated shifts; the calculation is a useful warning against overinterpreting a short clean pilot, not a universal confidence procedure.

## 18.8 Calibration

For a binary event with predicted probability $p_i$ and outcome $y_i\in\{0,1\}$, the Brier score is

$$\operatorname{Brier}=\frac1N\sum_i(p_i-y_i)^2.$$

For multiple classes, this book uses the mean over examples of the sum of squared errors across classes. Other normalizations differ by a constant; state the convention. Reliability bins compare average reported confidence with observed frequency, while a calibration plot shows whether those quantities agree.

Temperature scaling fits a positive scalar on held-out calibration data. Guo and colleagues study neural-network calibration and temperature scaling; the report also emphasizes using a held-out calibration set rather than tuning thresholds on test data. [R20; S, “Confidence calibration”]

Calibrate the quantity that drives the decision. Calibrated action probabilities do not automatically calibrate a wrong-order candidate derived from several actions, a duration model, and coverage rules. A VLM's verbal certainty is not a calibrated probability unless separately measured as such.

## 18.9 Thresholds and decision costs

For an illustrative binary policy, an alert on a non-error costs $C_{FP}$ and missing an error costs $C_{FN}$. Given a calibrated error probability $p$, the expected cost of alerting is $C_{FP}(1-p)$ and of remaining silent is $C_{FN}p$. Alerting is preferred when

$$p>\frac{C_{FP}}{C_{FP}+C_{FN}}.$$

This is a mathematical decision model, not a complete operational policy. It omits review capacity, severity, delay, uncertainty, and any requirements that cannot be represented by a simple average cost. Its value is to show why a threshold is not determined by classification accuracy alone.

## 18.10 Exercises

**Exercise 18.1.** Compute tIoU for $[2,6)$ and $[3,7)$. If two predictions both overlap one ground-truth action above threshold, how many can be true positives under one-to-one matching?

**Exercise 18.2.** In the rare-event example, reduce the false-positive rate from 5 percent to 1 percent while retaining 95 percent sensitivity. Calculate precision.

**Exercise 18.3.** A model has excellent boundary error on matched segments but misses half of the ground-truth actions. Why is the boundary statistic alone misleading, and which accompanying quantities are needed?

## 18.11 What follows

Evaluation must respect temporal structure, event exposure, observation coverage, and decision time. Calibration gives confidence scores empirical meaning but does not replace those measurements. The next chapter organizes experiments so that each added component answers a specific question rather than merely increasing architectural complexity.

# 19. An experimental program that answers questions {#ch19}

An architectural component is justified when an experiment shows what it contributes under the intended conditions. Building the entire multimodal hybrid at once makes it difficult to identify whether a gain came from better visual evidence, stronger procedure priors, additional future context, or an accidental change in evaluation. This chapter turns the report's implementation progression into a controlled experimental program.

## 19.1 Begin with a claim

An experiment should state the claim it tests. “Add object features” is an implementation action. “Object features improve wrong-part detection on held-out workers without increasing false alerts beyond the accepted range” is a testable claim. It names the target distinction, evaluation population, and operational constraint.

The report recommends progressing from annotation and embeddings through probabilistic and neural baselines to a structured hybrid, perception fusion, typed errors, verification, and production. This ordering reduces uncertainty one component at a time. [S, “Recommended implementation progression”]

| Stage | Implementation | Question answered |
|:--|:--|:--|
| Ground truth | Ontology and procedure specification. | Can reviewers label the task consistently? |
| Representation | Frozen encoder and linear head. | Is the action information present in the features? |
| Probabilistic baseline | HMM or HSMM. | What do order and duration contribute? |
| Local temporal model | Single causal TCN. | Does temporal context improve observation estimates? |
| Refinement | Causal multi-stage TCN. | Does refinement reduce harmful fragmentation? |
| Structured hybrid | Neural evidence plus procedure model. | Do constraints help without hiding mistakes? |
| Fusion | Tools, parts, pose, semantic features. | Which missing distinctions become observable? |
| Verification | Candidate-based VLM stage. | Does final precision improve at acceptable recall and delay? |
| Streaming | Availability-faithful replay and services. | Does deployment behavior match the evaluated policy? |

These are experimental stages, not promised outcomes.

## 19.2 Establish simple baselines

A linear head on frozen features establishes a visual baseline. A majority-class or simple duration-and-order baseline can reveal how predictable the dataset is without detailed visual evidence. Such baselines are not intended for deployment; they test whether an impressive aggregate score could arise from class imbalance or highly repetitive ordering.

An order-heavy model may perform well on correct executions yet fail precisely on the mistakes of interest. Evaluate normal and error sessions separately. The desired result is not only a plausible normal timeline but a faithful observation account when the execution is atypical.

A useful counterfactual test keeps the visible action evidence fixed while changing the procedure version or prerequisite state. The action estimate should remain stable, while the procedural judgment may change. Another keeps procedure state fixed while replacing the visible tool evidence. These tests inspect the intended separation of responsibilities.

## 19.3 Training protocol

Create the split manifest before fitting feature normalization, duration distributions, calibration parameters, or model weights. Statistics estimated from the test set can leak information even when no test label appears in a gradient update.

For an initial neural experiment, cache frozen features and train only the temporal model. This isolates the sequence architecture from encoder fine-tuning and reduces the cost of ablations. After establishing a stable baseline, fine-tune the encoder only when representation diagnostics identify a reason to do so.

Record random seeds, sampling rules, class mappings, optimizer settings, loss weights, mask semantics, sequence cropping, and effective context. The model checkpoint alone does not describe the experiment. In particular, a checkpoint trained with centered features cannot be reproduced as a causal experiment without changing the feature pipeline.

## 19.4 Ablations with matched conditions

The report proposes a progression from RGB alone through TCN, MS-TCN, HSMM, object and pose features, semantic embeddings, and VLM verification. [S, “Ablations you should insist on”]

Compare one change at a time where possible. Keep the same sessions, feature timestamps, annotation version, and allowed lookahead. When a larger context window is part of the proposed method, report that change explicitly rather than attributing all benefit to the model family.

For each ablation, record frame accuracy, edit score, segmental F1, important short-action recall, error precision and recall, false alerts per hour, coverage, and end-to-end delay. Not every metric will improve. A component can be valuable for one error type and unnecessary for another.

Ablating the VLM requires evaluating the complete policy. Comparing verifier accuracy only on easy hand-selected candidates does not establish that it improves the deployed cascade. Include ambiguous clips, missing prerequisites, service failures, and candidate-detector misses in the appropriate denominator.

## 19.5 Oracle tests isolate responsibility

An oracle test replaces one imperfect component with ground truth for diagnosis. Feed ground-truth action intervals into the procedure engine to test whether the rules detect annotated errors. Feed ground-truth object identities into the error engine to test whether wrong-part logic is correct. Feed the true procedure version into an otherwise uncertain execution association to test version-related failures.

These tests do not estimate deployable performance because the oracle information is unavailable at runtime. They estimate where improvement is possible and whether a downstream rule is wrong even when its inputs are correct. Label them as oracle or diagnostic results in every table.

A procedure engine that fails with gold actions should be repaired before investing in a larger video model. A perfect procedure engine with poor object evidence suggests a perception problem rather than a graph problem. This decomposition follows directly from the report's division of responsibilities.

## 19.6 Error analysis by mechanism

For each failure, identify the first point at which the evidence or interpretation became wrong. The cause may be an ambiguous annotation, missing camera visibility, a feature that discards motion direction, a temporal boundary error, a strict graph that hides a skip, a tool association mistake, a verifier overclaim, or a message arriving after commitment.

Use a structured failure record:

```yaml
failure_id: review-017
first_failed_component: procedure_decoder
observed_action_supported: tighten_left_fastener
error_judgment_expected: wrong_order
failure_mechanism: normal_only_graph_inserted_unobserved_step
supporting_interval_s: [80.0, 86.0]
proposed_test: preserve_observation_path_and_compare_valid_path
```

The record connects a diagnosis to a regression test. “Model confused” does not provide enough information to choose an intervention.

## 19.7 Threshold selection and held-out testing

Use training data to fit models, validation data to compare architecture and hyperparameters, and calibration data to fit probability adjustments or operational thresholds when the data volume permits separate sets. Keep a final test set untouched by these choices. When data are limited, document the cross-validation or nested selection procedure rather than pretending several roles are independent when they share examples.

Once a test set guides repeated model decisions, it is no longer an untouched final test. Maintain a later temporal holdout or a new deployment-like cohort for the next release. Version the evaluation protocol with the model so that comparisons remain interpretable.

## 19.8 Evidence required before a pilot

A pilot decision should be supported by more than a favorable average. It needs representative held-out sessions, error-type coverage, boundary and delay measurements, a demonstrated unknown/gap policy, adapter tests, replay recovery tests, and an explicit human-review workflow.

The research does not specify a universal sample count, accuracy threshold, GPU budget, or accepted false-alert rate. Those values depend on the procedure and intended use. This book therefore provides measurement and test structures rather than inventing numerical acceptance criteria.

## 19.9 Exercises

**Exercise 19.1.** A Transformer outperforms a TCN, but the Transformer uses ten seconds of future context and the TCN is causal. What claim does the comparison fail to isolate, and how would you redesign it?

**Exercise 19.2.** The procedure engine misses wrong-order errors even when supplied with ground-truth action intervals. Which component should be investigated first, and why is encoder fine-tuning unlikely to fix the immediate defect?

**Exercise 19.3.** Write an ablation hypothesis for adding tool telemetry. Specify the target error type, held-out grouping, baseline, and at least one operational metric.

## 19.10 What follows

A controlled experimental program converts architectural choices into evidence. Its intermediate baselines and oracle tests reveal where complexity is justified and where it hides unresolved assumptions. The next two chapters provide small executable implementations so that the central algorithms can be tested before they are embedded in a larger system.

# 20. Laboratory: sequence inference and error evidence {#ch20}

The numerical chapters become more useful when a reader can change one assumption and inspect the resulting path. This laboratory provides that opportunity without requiring video, a trained encoder, or a GPU. It implements log-space HMM inference, a bounded-duration HSMM decoder, two segment metrics, and small procedure and persistence monitors. Its purpose is to make the interfaces and failure conditions executable, not to supply a production worker-monitoring service.

## 20.1 The experiment and its contract

The first experiment reproduces the three-observation HMM from Chapters 7–8. The second reproduces the four-position HSMM from Chapter 9. The final examples show that identical observed actions can produce different procedural judgments when evidence coverage changes. These are synthetic, inspectable constructions based on the report's algorithms. No result in this chapter measures recognition performance on workers.

The code blocks in Sections 20.2–20.7, placed in order in `sequence_lab.py`, form the complete executable module. The companion contains the same module and a separate regression-test file. Run it in an environment with NumPy installed:

```sh
python sequence_lab.py
python -m unittest -v test_labs.py
```

The edition was tested with Python 3.13.5 and NumPy 2.3.5. These record the execution environment rather than a claim that other versions cannot work. Run the demonstrations without Python's `-O` option, which disables their assertions. The separate unit tests use the `unittest` framework.

The inference functions accept log evidence with shape `[time, states]`, a square transition-score matrix, and an initial-state vector. They do not infer whether their inputs form a normalized generative model. When the caller supplies valid HMM likelihoods, the forward total is an observation probability. When the caller supplies arbitrary finite potentials, the same recurrence sums unnormalized path weights. Naming that distinction is part of the interface.

## 20.2 Numerical helpers and validation

An impossible event has log score negative infinity, not a very large negative number chosen without explanation. The log-sum-exp helper handles a row of impossible candidates explicitly. The shared validator rejects empty sequences, inconsistent shapes, NaNs, and positive infinities. It permits negative infinity because excluding a transition is a legitimate model operation.


```python
"""Inspectable temporal-inference examples; not a production monitor.

Run: python sequence_lab.py
Requires NumPy. All demo inputs are synthetic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
import json
import math
import numpy as np


def log_prob(p: np.ndarray) -> np.ndarray:
    """Map nonnegative probabilities to logs, preserving impossible events."""
    p = np.asarray(p, dtype=float)
    if np.any(~np.isfinite(p)) or np.any(p < 0) or np.any(p > 1):
        raise ValueError("Probabilities must be finite and in [0, 1].")
    out = np.full_like(p, -np.inf)
    np.log(p, out=out, where=p > 0)
    return out


def logsumexp(a: np.ndarray, axis: int | None = None) -> np.ndarray:
    """Stable log sum, including an all-impossible slice."""
    a = np.asarray(a, dtype=float)
    m = np.max(a, axis=axis, keepdims=True)
    safe_m = np.where(np.isfinite(m), m, 0.0)
    total = np.exp(a - safe_m).sum(axis=axis, keepdims=True)
    out = np.full_like(total, -np.inf)
    np.log(total, out=out, where=total > 0)
    out = out + safe_m
    return np.squeeze(out, axis=axis) if axis is not None else out.squeeze()


def _check(log_e, log_a, log_pi):
    e = np.asarray(log_e, dtype=float)
    a = np.asarray(log_a, dtype=float)
    pi = np.asarray(log_pi, dtype=float)
    if e.ndim != 2 or min(e.shape) == 0:
        raise ValueError("Evidence must have nonempty shape [time, states].")
    k = e.shape[1]
    if a.shape != (k, k) or pi.shape != (k,):
        raise ValueError("Transition or initial-state shape mismatch.")
    for x in (e, a, pi):
        if np.isnan(x).any() or np.isposinf(x).any():
            raise ValueError("Scores may be finite or -inf, never NaN/+inf.")
    return e, a, pi
```

`log_prob` validates individual probabilities, but it does not check that rows sum to one. An emission slice contains the likelihood of the observed symbol under each state; its row over states need not sum to one. For a generative model, validate the complete initial, transition, and emission distributions when constructing that model, rather than imposing an incorrect normalization on the observation slice.

## 20.3 HMM inference

The forward and Viterbi routines have the same candidate matrix at each position. Forward sums predecessor support with log-sum-exp; Viterbi selects a predecessor and retains its index. Smoothing adds backward messages and normalizes by the total sequence support. Reading the functions together makes the difference between marginalization and path selection visible.


```python
def forward(log_e, log_a, log_pi):
    """Return log forward messages and total log likelihood/potential sum."""
    e, a, pi = _check(log_e, log_a, log_pi)
    alpha = np.empty_like(e)
    alpha[0] = pi + e[0]
    for t in range(1, len(e)):
        alpha[t] = e[t] + logsumexp(alpha[t - 1, :, None] + a, axis=0)
    return alpha, float(logsumexp(alpha[-1]))


def smooth(log_e, log_a, log_pi):
    """Offline state marginals. Reject a sequence with zero total support."""
    e, a, pi = _check(log_e, log_a, log_pi)
    alpha, log_z = forward(e, a, pi)
    if not np.isfinite(log_z):
        raise ValueError("No admissible path.")
    beta = np.zeros_like(e)
    for t in range(len(e) - 2, -1, -1):
        beta[t] = logsumexp(a + e[t + 1] + beta[t + 1], axis=1)
    return np.exp(alpha + beta - log_z), log_z


def viterbi(log_e, log_a, log_pi):
    """Most likely complete path; ties choose the first state index."""
    e, a, pi = _check(log_e, log_a, log_pi)
    score = np.empty_like(e)
    back = np.full(e.shape, -1, dtype=int)
    score[0] = pi + e[0]
    for t in range(1, len(e)):
        candidates = score[t - 1, :, None] + a
        back[t] = candidates.argmax(axis=0)
        score[t] = candidates.max(axis=0) + e[t]
    state = int(score[-1].argmax())
    best = float(score[-1, state])
    if not np.isfinite(best):
        raise ValueError("No admissible path.")
    path = np.empty(len(e), dtype=int)
    path[-1] = state
    for t in range(len(e) - 1, 0, -1):
        path[t - 1] = back[t, path[t]]
    return path, best
```

`forward` can legitimately return negative infinity when every path is impossible. `smooth` and `viterbi` cannot return a meaningful posterior or maximizing supported path in that case, so they raise an exception. A caller should route that exception to model-mismatch or insufficient-support handling; it should not silently emit state zero.

The tie policy chooses the first state index. Such a convention affects deterministic reproducibility, not the mathematical identity of the set of maximizers. A production event stream should not allow arbitrary tie behavior to create unstable incident IDs.

## 20.4 Explicit-duration decoding

The HSMM routine stores the best completed segmentation of every prefix ending in each state. It tries each allowed duration, uses a prefix sum to obtain the segment's observation score, and records both the predecessor state and chosen length. Adjacent segments of the same state are disallowed so that the duration model, rather than repeated segment boundaries, controls dwell time.


```python
def hsmm_viterbi(log_e, log_a, log_pi, log_duration):
    """Offline explicit-duration decoder with completed final segment.

    duration[k, d-1] scores duration d. Adjacent segments cannot share a
    state: the duration distribution, not a self-transition, models dwell.
    Finite emissions are required for prefix sums. Durations are bounded.
    Returns half-open (start, end, state) segments and a total score.
    """
    e, a, pi = _check(log_e, log_a, log_pi)
    duration = np.asarray(log_duration, dtype=float)
    n, k = e.shape
    if (duration.ndim != 2 or duration.shape[0] != k
            or duration.shape[1] == 0):
        raise ValueError("Duration scores need shape [states, max_duration].")
    if (not np.isfinite(e).all() or np.isnan(duration).any()
            or np.isposinf(duration).any()):
        raise ValueError("Finite emissions and valid log durations required.")
    a = a.copy()
    np.fill_diagonal(a, -np.inf)
    prefix = np.vstack([np.zeros(k), np.cumsum(e, axis=0)])
    dp = np.full((n + 1, k), -np.inf)
    prev = np.full((n + 1, k), -1, dtype=int)
    lengths = np.zeros((n + 1, k), dtype=int)
    for end in range(1, n + 1):
        for state in range(k):
            for d in range(1, min(end, duration.shape[1]) + 1):
                start = end - d
                if start == 0:
                    base, parent = pi[state], -1
                else:
                    incoming = dp[start] + a[:, state]
                    parent = int(incoming.argmax())
                    base = incoming[parent]
                candidate = (base + duration[state, d - 1]
                             + prefix[end, state] - prefix[start, state])
                if candidate > dp[end, state]:
                    dp[end, state] = candidate
                    prev[end, state] = parent
                    lengths[end, state] = d
    state = int(dp[n].argmax())
    best = float(dp[n, state])
    if not np.isfinite(best):
        raise ValueError("No admissible duration-constrained path.")
    segments = []
    end = n
    while end:
        d = int(lengths[end, state])
        if d <= 0:
            raise RuntimeError("Invalid backpointer.")
        segments.append((end - d, end, state))
        parent = int(prev[end, state])
        end -= d
        state = parent
    return list(reversed(segments)), best
```

There are three deliberate restrictions. The routine requires finite emission scores because subtracting two negative-infinite prefix sums is undefined. It bounds durations by the supplied duration table. It treats the final segment as completed at the end of the supplied sequence. This last assumption makes the routine appropriate for the chapter's completed toy sequences, not for an ongoing live action whose elapsed time is right-censored.

The example also allows any supported terminal state. Reaching the end of an input array therefore does not certify completion of a real assembly procedure. A procedure-completion contract would require an explicit terminal-state condition and evidence for its postconditions.

The nested loops are intentionally inspectable rather than maximally optimized. Their dense worst-case work is $O(NK^2D_{\max})$. Sparse predecessor lists and reuse of predecessor maxima can reduce unnecessary work, but optimization should follow correctness tests.

## 20.5 Segment metrics

These helpers convert dense labels to half-open intervals, calculate temporal overlap, and compare collapsed action sequences. Using the same interval convention in annotations, model output, and metrics prevents an endpoint from being counted in two adjacent segments.


```python
def collapse(labels):
    """Convert dense labels to half-open segments."""
    values = list(labels)
    if not values:
        return []
    out, start = [], 0
    for t in range(1, len(values) + 1):
        if t == len(values) or values[t] != values[start]:
            out.append((start, t, values[start]))
            start = t
    return out


def temporal_iou(p, g):
    if p[1] <= p[0] or g[1] <= g[0]:
        raise ValueError("Intervals must have positive length.")
    intersection = max(0.0, min(p[1], g[1]) - max(p[0], g[0]))
    union = (p[1] - p[0]) + (g[1] - g[0]) - intersection
    return intersection / union


def edit_score(prediction, truth):
    """Normalized Levenshtein similarity of collapsed label sequences."""
    p = [s[2] for s in collapse(prediction)]
    g = [s[2] for s in collapse(truth)]
    previous = list(range(len(g) + 1))
    for i, label in enumerate(p, 1):
        current = [i]
        for j, target in enumerate(g, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (label != target)))
        previous = current
    return 100.0 * (1 - previous[-1] / max(len(p), len(g), 1))
```

The edit score deliberately ignores exact segment lengths after collapsing consecutive duplicate labels. It complements, rather than replaces, timing measures. A correct symbolic order with badly shifted boundaries can receive an excellent edit score. Segment F1 additionally requires a specified one-to-one matching policy, discussed in Chapter 18; a full benchmark implementation is not hidden inside this small helper.

## 20.6 Procedure evidence and persistence

The prerequisite monitor separates what was observed from whether its prerequisites were supported. Its completed-step set is monotone: once a step has a supported postcondition, it remains completed. That is sufficient for this laboratory's no-rework example, but not for a procedure in which removing a fastener invalidates earlier insertion and tightening facts.

The coverage flag is equally conservative. Once a gap occurs, a missing prerequisite remains uncertain. It does not attempt interval-specific visibility reconstruction or automatically restore confidence when frames resume. A real implementation needs the richer fact and coverage records from Chapters 2 and 14.


```python
@dataclass
class PrerequisiteMonitor:
    """Minimal monotone procedure; rework invalidation is not modeled."""
    prerequisites: dict[str, set[str]]
    completed: set[str] = field(default_factory=set)
    coverage_complete: bool = True

    def gap(self):
        self.coverage_complete = False

    def observe(self, step: str, postcondition: bool | None):
        if step not in self.prerequisites:
            raise ValueError(f"Unknown step: {step}")
        missing = self.prerequisites[step] - self.completed
        status = "supported"
        if missing:
            status = "wrong_order" if self.coverage_complete else "uncertain"
        result = {"observed_step": step, "status": status,
                  "unmet_prerequisites": sorted(missing)}
        if postcondition is True:
            self.completed.add(step)
        return result


@dataclass
class PersistenceGate:
    """One incident per episode. A missing sample cancels persistence.

    The caller must route observation_gap to its own health/review path.
    This small example does not implement incident reconciliation.
    """
    high: float = 0.8
    low: float = 0.3
    persistence_s: float = 1.0
    max_gap_s: float = 0.75
    start: float | None = None
    last: float | None = None
    active: bool = False

    def __post_init__(self):
        if not (0 <= self.low < self.high <= 1):
            raise ValueError("Require 0 <= low < high <= 1.")
        if self.persistence_s < 0 or self.max_gap_s <= 0:
            raise ValueError("Invalid time parameters.")

    def update(self, time_s: float, score: float | None):
        if not math.isfinite(time_s):
            raise ValueError("Timestamp must be finite.")
        if self.last is not None and time_s <= self.last:
            raise ValueError("Timestamps must strictly increase.")
        if score is not None and (not math.isfinite(score) or not 0 <= score <= 1):
            raise ValueError("Score must be in [0, 1], or None.")
        gap = self.last is not None and time_s - self.last > self.max_gap_s
        self.last = time_s
        if score is None or gap:
            self.start, self.active = None, False
            return "observation_gap"
        if score < self.low:
            self.start, self.active = None, False
            return "normal"
        if self.start is None and score >= self.high:
            self.start = time_s
        if self.start is not None and not self.active:
            if time_s - self.start >= self.persistence_s:
                self.active = True
                return "incident"
        return "active" if self.active else ("possible" if self.start is not None else "normal")
```

A wrong-order observation can still establish a physical postcondition. For example, a supported tightening event does not cease to have happened merely because its order was invalid. The monitor therefore records a true postcondition independently of the validity judgment. It does not automatically establish missing prerequisites retroactively.

The persistence gate uses two thresholds. Crossing the high threshold starts an episode; remaining above the low threshold keeps it pending. This prevents a small fluctuation below the high threshold from resetting a continuing episode. A missing sample or excessive timestamp gap returns `observation_gap` and cancels this laboratory's internal persistence state.

That cancellation is not an incident-resolution policy. In a production service, the previously reported incident must remain in an auditable record, and the gap must be routed to health or review handling. The small gate returns an event label; it does not own those durable records. Invalid timestamps and scores are rejected before the gate mutates its state.

## 20.7 The executable experiment

The demonstration computes each numerical result, checks it against an independent small construction where feasible, and returns a machine-readable trace. Exhaustive enumeration is used only because there are eight HMM paths. It is a useful correctness check, not a scalable inference method.


```python
def demo():
    # Two-state generative HMM with abstract states A (0), B (1).
    a = np.array([[0.7, 0.3], [0.1, 0.9]])
    pi = np.array([0.9, 0.1])
    e = np.array([[0.6, 0.1], [0.3, 0.4], [0.1, 0.5]])
    logs = [log_prob(x) for x in (e, a, pi)]
    alpha, log_z = forward(*logs)
    marginals, _ = smooth(*logs)
    path, score = viterbi(*logs)
    # Independent exhaustive check, only for this tiny example.
    paths = list(product(range(2), repeat=3))
    probabilities = []
    for p in paths:
        prob = pi[p[0]] * e[0, p[0]]
        for t in range(1, 3):
            prob *= a[p[t - 1], p[t]] * e[t, p[t]]
        probabilities.append(prob)
    assert np.isclose(np.exp(log_z), sum(probabilities))
    assert np.isclose(np.exp(score), max(probabilities))
    assert tuple(path) == paths[int(np.argmax(probabilities))]
    assert np.allclose(marginals.sum(axis=1), 1)
    assert float(logsumexp(np.array([-np.inf, -np.inf]))) == -np.inf
    # Explicit-duration A -> B, each duration 1 or 2.
    he = log_prob(np.array([[0.9, 0.1], [0.8, 0.2],
                           [0.2, 0.8], [0.1, 0.9]]))
    ha = log_prob(np.array([[0.0, 1.0], [1.0, 0.0]]))
    hp = log_prob(np.array([1.0, 0.0]))
    hd = log_prob(np.array([[0.2, 0.8], [0.2, 0.8]]))
    segments, hs = hsmm_viterbi(he, ha, hp, hd)
    assert segments == [(0, 2, 0), (2, 4, 1)]
    assert np.isclose(np.exp(hs), 0.331776)
    prereq = {"align": set(), "insert": {"align"},
              "tighten": {"insert"}}
    monitor = PrerequisiteMonitor(prereq)
    monitor.observe("align", True)
    violation = monitor.observe("tighten", True)
    assert violation["status"] == "wrong_order"
    uncertain = PrerequisiteMonitor(prereq)
    uncertain.observe("align", True)
    uncertain.gap()
    assert uncertain.observe("tighten", True)["status"] == "uncertain"
    gate = PersistenceGate()
    gate_output = [gate.update(t, s) for t, s in
                   [(0, .1), (.5, .85), (1, .9), (1.5, .88), (2, .2)]]
    assert gate_output == ["normal", "possible", "possible", "incident", "normal"]
    assert np.isclose(temporal_iou((2, 6), (3, 7)), .6)
    assert edit_score("AAAABBBBCCCC", "AAAABBBBCCCC") == 100
    return {
        "hmm_forward_probability": round(float(np.exp(log_z)), 6),
        "hmm_forward_rows": np.exp(alpha).round(6).tolist(),
        "hmm_smoothed_marginals": marginals.round(6).tolist(),
        "hmm_best_path": path.tolist(),
        "hmm_best_path_probability": round(float(np.exp(score)), 6),
        "hsmm_segments": segments,
        "hsmm_path_weight": round(float(np.exp(hs)), 6),
        "procedure_violation": violation,
        "persistence_trace": gate_output,
        "temporal_iou": temporal_iou((2, 6), (3, 7)),
        "tests": "passed"
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
```

## 20.8 Reading the results

The tested execution produced the following central values:

| Quantity | Result | Interpretation |
|:--|--:|:--|
| HMM observation probability | 0.056478 | Sum over all eight hidden paths. |
| Best HMM path | A, B, B | Joint path probability 0.029160. |
| HSMM segments | A: [0, 2), B: [2, 4) | Both segments have duration two. |
| HSMM path weight | 0.331776 | Unnormalized weight for the stated potentials. |
| Temporal IoU | 0.600000 | Overlap of [2, 6) and [3, 7). |

The procedure trace reports `wrong_order` for tightening after alignment without a supported insertion, under the example's complete-coverage assumption. Introducing a gap before the same tightening observation changes the judgment to `uncertain`. The action is not rewritten into an insertion merely to make the sequence valid.

The persistence output is:

```text
0.0 s   score 0.10   normal
0.5 s   score 0.85   possible
1.0 s   score 0.90   possible
1.5 s   score 0.88   incident
2.0 s   score 0.20   normal
```

The incident appears one second after the threshold-crossing sample. The evidence is sampled, so this does not establish the exact continuous-time onset between samples. A production delay calculation should use the actual observability annotation and timestamp convention, not just the threshold index.

## 20.9 What the regression suite establishes

The companion suite includes exhaustive comparisons for small random HMMs and HSMMs, posterior normalization, impossible paths, invalid input, segment collapse, overlap, edit score, missing coverage, hysteresis, and timestamp validation. Its twenty test cases passed in the tested environment. That count describes tests, not twenty distinct industrial operating conditions.

The exhaustive HSMM check is especially useful because an apparently plausible segmentation can conceal an off-by-one error or an incorrect predecessor boundary. Enumerating short segmentations provides an independent reference. Once the implementation is embedded in a streaming service, additional tests must cover state restoration, duplicate messages, late evidence, procedure-version changes, and unfinished terminal segments.

## 20.10 Exercises

**Exercise 20.1.** Change the HMM transition matrix so that every transition after the first observation is impossible. Predict the outputs of `forward`, `smooth`, and `viterbi`, then run the change.

**Exercise 20.2.** The prerequisite monitor has observed alignment and then receives a gap. Tightening becomes visible afterward. Explain why setting `coverage_complete=True` merely because the camera has resumed would be incorrect.

**Exercise 20.3.** The HSMM receives an ongoing tightening action whose true endpoint is beyond the input boundary. Identify the assumption in `hsmm_viterbi` that is violated and the kind of duration term an online extension needs.

## 20.11 What follows

The laboratory exposes the central contract between observation scores, structured inference, and procedural evidence. The next laboratory supplies a small neural temporal recognizer whose causal behavior can also be tested directly. Keeping those implementations separate makes it possible to determine which component changed a result.

# 21. Laboratory: a causal multi-stage TCN {#ch21}

A temporal network should not be called causal merely because its class name contains the word. Its output must satisfy a testable dependency restriction: changing future inputs must not change earlier predictions. This laboratory implements a small multi-stage TCN, tests that restriction, checks a masked loss, and verifies that an optimizer can reduce a synthetic training objective.

## 21.1 Scope, shapes, and execution

This is a teaching variant of the multi-stage idea in Chapter 11, not an exact reproduction of the published MS-TCN implementation. It uses causal left padding, three dilated residual layers per stage, two stages, and a symmetric-gradient temporal smoothing term. The architecture is intentionally small enough to execute on a CPU. The original method remains the reference for paper-specific experimental replication. [R13]

The blocks in Sections 21.2–21.5, placed in order, form `neural_lab.py`. Run:

```sh
python neural_lab.py
```

The tested environment used PyTorch 2.10.0+cpu. The implementation uses documented one-dimensional convolution, explicit padding, and cross-entropy operations. Installation and accelerator choices should follow the PyTorch documentation for the intended environment; the code itself does not require CUDA. [R33]

Input features have shape $[B,d,N]$, valid-position masks have shape $[B,N]$, and the stacked outputs have shape $[S,B,K,N]$. Here $B$ is batch size, $d$ the embedding dimension, $N$ the number of positions, $S$ the number of stages, and $K$ the number of action classes. The labels are integer class indices at valid positions.

## 21.2 A causal residual block

A kernel of size three with dilation $r$ needs $2r$ positions of left context. Explicitly padding only the left side makes the output at position $t$ depend on positions no later than $t$. The pointwise convolution mixes channels without mixing time. A residual connection preserves the current representation while the dilated branch learns a correction.


```python
"""A small causal multi-stage TCN and deterministic CPU smoke tests.

Run: python neural_lab.py
Requires PyTorch. This is a teaching variant, not the original MS-TCN.
"""
from __future__ import annotations

import json
import torch
from torch import nn
from torch.nn import functional as F


class CausalBlock(nn.Module):
    def __init__(self, channels: int, dilation: int, dropout: float = 0.1):
        super().__init__()
        if channels < 1 or dilation < 1:
            raise ValueError("Channels and dilation must be positive.")
        self.left = 2 * dilation
        self.conv = nn.Conv1d(channels, channels, 3, dilation=dilation)
        self.mix = nn.Conv1d(channels, channels, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        h = self.conv(F.pad(x, (self.left, 0)))
        h = self.dropout(self.mix(F.relu(h)))
        return (x + h) * mask
```

The mask is multiplied after the residual update. This prevents a padded output from being treated as a valid feature downstream. The model later masks the input as well, because masking only at the end would permit arbitrary padded input values to affect nearby valid outputs.

These masks are designed for padding and explicitly excluded positions. They are not a complete treatment of a camera outage in the middle of a real sequence. Convolution can still connect valid observations on opposite sides of a masked gap through its receptive field. Resetting context or representing time and visibility explicitly remains an application decision.

## 21.3 Stages and refinement

The first stage sees the embedding channels. Later stages see the preceding stage's class probabilities. Each stage can therefore learn that a short isolated prediction is inconsistent with surrounding evidence, while remaining subject to the same causal dependency restriction.


```python
class Stage(nn.Module):
    def __init__(self, input_dim: int, classes: int, channels: int, layers: int):
        super().__init__()
        self.project = nn.Conv1d(input_dim, channels, 1)
        self.blocks = nn.ModuleList(
            CausalBlock(channels, 2**i) for i in range(layers)
        )
        self.head = nn.Conv1d(channels, classes, 1)

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        h = self.project(x) * mask
        for block in self.blocks:
            h = block(h, mask)
        return self.head(h) * mask


class CausalMultiStageTCN(nn.Module):
    def __init__(self, input_dim: int, classes: int, channels: int = 16,
                 layers: int = 3, stages: int = 2):
        super().__init__()
        if min(input_dim, classes, channels, layers, stages) < 1:
            raise ValueError("All dimensions and counts must be positive.")
        self.input_dim = input_dim
        self.stages = nn.ModuleList(
            Stage(input_dim if s == 0 else classes, classes, channels, layers)
            for s in range(stages)
        )

    def forward(self, x: torch.Tensor, valid: torch.Tensor) -> torch.Tensor:
        # x: [batch, features, time]; valid: [batch, time].
        if x.ndim != 3 or x.shape[1] != self.input_dim or x.shape[2] < 1:
            raise ValueError("Invalid input shape.")
        if valid.dtype != torch.bool or valid.shape != (x.shape[0], x.shape[2]):
            raise ValueError("valid must be Boolean [batch, time].")
        if not torch.isfinite(x).all():
            raise ValueError("Features must be finite; use an explicit gap policy.")
        mask = valid[:, None, :].to(x.dtype)
        inputs, outputs = x * mask, []
        for stage in self.stages:
            logits = stage(inputs, mask)
            outputs.append(logits)
            inputs = logits.softmax(dim=1) * mask
        return torch.stack(outputs)  # [stages, batch, classes, time]
```

Three kernel-three layers with dilations 1, 2, and 4 give one stage a receptive field of $1+2(1+2+4)=15$ positions. Composing two such stages yields up to $1+2(15-1)=29$ positions of original-input support. That is not twenty-nine seconds; the physical span depends on the feature stride. At a half-second stride, the earliest to latest supported feature positions are fourteen seconds apart.

The check for finite input values rejects NaNs rather than hoping they will disappear under a mask. Multiplication by zero does not make a NaN a valid number. An upstream adapter must convert unavailable evidence into a deliberate gap policy before calling the model.

## 21.4 A masked segmentation loss

Cross-entropy is averaged over valid positions. Smoothing is averaged only over adjacent pairs for which both positions are valid. The loss is calculated at every stage and then averaged across stages. The clipping threshold limits the penalty for large adjacent changes, reducing the influence of abrupt transitions without eliminating their classification supervision.


```python
def segmentation_loss(outputs: torch.Tensor, target: torch.Tensor,
                      valid: torch.Tensor, smooth_weight: float = 0.05,
                      clip: float = 4.0) -> torch.Tensor:
    if outputs.ndim != 4 or outputs.shape[-1] < 1:
        raise ValueError("outputs must be [stages, batch, classes, time].")
    _, batch, classes, time = outputs.shape
    if target.shape != (batch, time) or valid.shape != target.shape:
        raise ValueError("Target/mask shape mismatch.")
    if target.dtype != torch.long or valid.dtype != torch.bool:
        raise ValueError("Target must be long and mask Boolean.")
    if smooth_weight < 0 or clip <= 0:
        raise ValueError("Invalid loss weights.")
    if valid.any() and ((target[valid] < 0).any() or (target[valid] >= classes).any()):
        raise ValueError("A valid target is outside the class range.")
    if not valid.any():
        return outputs.sum() * 0.0
    safe_target = target.masked_fill(~valid, -100)
    pairs = valid[:, 1:] & valid[:, :-1]
    losses = []
    for logits in outputs:
        ce = F.cross_entropy(logits, safe_target, reduction="none")
        ce = ce[valid].mean()
        log_p = logits.log_softmax(dim=1)
        delta = (log_p[:, :, 1:] - log_p[:, :, :-1]).abs().clamp(max=clip)
        if pairs.any():
            smooth = (delta.square() * pairs[:, None, :]).sum()
            smooth = smooth / (pairs.sum() * classes)
        else:
            smooth = logits.sum() * 0.0
        losses.append(ce + smooth_weight * smooth)
    return torch.stack(losses).mean()
```

The target at an invalid position is replaced by the ignore index before cross-entropy is evaluated. This prevents an arbitrary placeholder label from causing an out-of-range error. The all-invalid case returns a differentiable zero, so an empty masked example does not create a division by zero.

This implementation deliberately allows gradients through both adjacent log-probability vectors in the smoothing term. It should therefore be described as the displayed objective, not asserted to match every implementation detail of the original paper. A reproducibility claim must name loss normalization, clipping, masking, and gradient-stop conventions as well as the architecture.

## 21.5 Causality and optimizer tests

The first test evaluates a full sequence, perturbs its second half, and compares the untouched prefix outputs. The second evaluates the prefix by itself and compares it with the corresponding full-sequence outputs. Both tests run in evaluation mode so that dropout does not introduce unrelated random differences.

The optimizer test uses deliberately easy synthetic features: a one-hot encoding of each target class plus five zero channels. This is not a realistic representation-learning problem. It checks that the forward computation, loss, gradients, and parameter updates are connected correctly.


```python
def demo():
    torch.set_num_threads(2)
    torch.manual_seed(7)
    model = CausalMultiStageTCN(8, 3)
    x = torch.randn(2, 8, 24)
    valid = torch.ones(2, 24, dtype=torch.bool)
    model.eval()
    with torch.no_grad():
        full = model(x, valid)
        altered = x.clone()
        altered[:, :, 12:] += 100.0
        changed = model(altered, valid)
        error = (full[:, :, :, :12] - changed[:, :, :, :12]).abs().max().item()
        assert error < 1e-6, "Future input changed a past prediction."
        prefix = model(x[:, :, :12], valid[:, :12])
        assert torch.allclose(full[:, :, :, :12], prefix, atol=1e-6)
    target = torch.arange(24)[None, :].repeat(2, 1) // 8
    # Easy synthetic features for an optimizer smoke test, not a benchmark.
    train_x = F.one_hot(target, 3).float().transpose(1, 2)
    train_x = torch.cat([train_x, torch.zeros(2, 5, 24)], dim=1)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    model.eval()
    initial = float(segmentation_loss(model(train_x, valid), target, valid).detach())
    model.train()
    for _ in range(40):
        optimizer.zero_grad()
        loss = segmentation_loss(model(train_x, valid), target, valid)
        loss.backward()
        optimizer.step()
    model.eval()
    final = float(segmentation_loss(model(train_x, valid), target, valid).detach())
    assert final < initial
    empty_mask = torch.zeros_like(valid)
    empty_loss = segmentation_loss(model(x, valid), target, empty_mask)
    assert empty_loss.item() == 0
    return {
        "output_shape": list(full.shape),
        "future_perturbation_max_prefix_error": error,
        "initial_synthetic_loss": round(initial, 6),
        "final_synthetic_loss": round(final, 6),
        "optimizer_steps": 40,
        "tests": "passed",
        "torch_version": torch.__version__
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
```

## 21.6 The tested trace

The CPU execution in this edition produced:

```json
{
  "output_shape": [2, 2, 3, 24],
  "future_perturbation_max_prefix_error": 0.0,
  "initial_synthetic_loss": 1.141251,
  "final_synthetic_loss": 0.059701,
  "optimizer_steps": 40,
  "tests": "passed",
  "torch_version": "2.10.0+cpu"
}
```

The output shape records two stages, two sequences, three classes, and twenty-four temporal positions. The zero prefix difference supports the causal dependency claim for the tested input and configuration. The loss decrease supports the optimizer smoke test. Neither result establishes accuracy on video, robustness to a new worker, suitable boundary timing, or production latency.

Exact floating-point losses can differ across software builds and hardware. The important test properties are the dependency invariants and the loss reduction, not matching every printed decimal on every platform. A deployment test should record tolerances and the actual runtime version.

## 21.7 Replacing the synthetic features

To use real data, construct features and labels with the contracts developed earlier. The feature extractor must preserve the timestamp at which its evidence became available. The label generator must use the agreed interval convention and mark ambiguous or excluded positions. Session-grouped splits must be established before overlapping clips are extracted.

For a first experiment, freeze the encoder and train the temporal model on saved features. This makes it possible to reproduce a sequence-model result without repeatedly decoding video. Store the encoder version and feature layout next to the arrays. A later joint-training experiment is a separate treatment, not a silent change to the same baseline.

The minimal training loop in this laboratory is not a dataset trainer. A real experiment also needs batching, held-out validation, checkpoint selection, class and boundary metrics, calibration, interrupted-run recovery, and a recorded configuration. The absence of those components is visible in the code rather than concealed behind a function named `train_production_model`.

## 21.8 Causality beyond this module

The prefix tests cannot detect future leakage that has already entered the feature vectors. A centered video encoder could summarize frames after the feature timestamp even though the TCN itself uses only left context. Likewise, a whole-sequence normalization step before the TCN could make every feature depend on later video.

Run dependency tests at multiple boundaries: raw frames to embeddings, embeddings to logits, logits to committed segments, and segments to incidents. Include evidence availability in the replay. When a component deliberately uses lookahead, test the permitted amount rather than requiring strict zero lookahead.

A causal network can still revise a previous estimate when it is rerun on a different window alignment or initialized with a different history. The prefix equality test here fixes initialization and alignment. A streaming cache implementation needs an additional full-versus-chunked equivalence test, including the cache state at each boundary.

## 21.9 Exercises

**Exercise 21.1.** Replace the left-only padding with equal left and right padding of one dilation unit. Which dependency test should fail, and why can the output length remain unchanged despite the error?

**Exercise 21.2.** A target array uses label 99 at a padded position even though there are only three classes. Explain why `safe_target` is created before cross-entropy rather than masking the resulting loss afterward.

**Exercise 21.3.** Add a third refinement stage with the same three-layer structure. Compute the total receptive field in feature positions and the earliest-to-latest feature span at a half-second stride.

## 21.10 What follows

The laboratory provides an executable temporal model and tests a property that live deployment depends on. The remaining task is not simply to place this model behind an endpoint. The capstone connects its evidence, procedure state, event semantics, evaluation, and recovery behavior into one releaseable design.

# 22. Capstone: from replay to a monitored pilot {#ch22}

A useful capstone is not a diagram with every available model attached. It is a constrained system whose evidence can be traced from a recorded action to a reported incident, including the cases in which the system should remain uncertain. This chapter specifies such a project for the bracket-assembly procedure. It combines the research's hybrid architecture with the implementation qualifications developed throughout the book. The result is a project specification, not a claim that an industrial installation has been completed.

## 22.1 Define one releaseable task

Begin with one workstation, one explicitly versioned procedure, one build identity mechanism, and a limited set of observable action classes. The initial error types are wrong order, wrong tool when the relevant tool is visible, and omission at an identified closure opportunity. Excess-duration events are initially review candidates rather than automatic proof of incorrect work.

Exclude claims the evidence cannot support. If insertion is frequently hidden behind a fixture, the initial release must either obtain another view, use an appropriate instrumented signal, or return an uncertainty judgment for that prerequisite. If the camera cannot measure achieved torque, the release must not claim that a visually recognized tightening motion certifies torque. These restrictions follow the report's separation of observed action, procedure logic, and additional object or machine evidence. [S, “Correctness should be separate from the observed action”; “Cross-feature fusion”]

A concise task contract might be:

```yaml
release: bracket-pilot-01
procedure: bracket-v7
action_scope:
  - pick_bracket
  - align_bracket
  - insert_fastener
  - tighten_fastener
  - inspect_assembly
error_scope:
  - wrong_order
  - wrong_tool_when_observable
  - omission_at_closure
unsupported_claims:
  - certified_torque_from_rgb
  - omission_during_unobserved_interval
  - individual_worker_intent
mode: shadow_review
```

The `mode` field matters. A shadow-review system records and compares predictions without treating them as operational instructions. Moving to an operator-facing pilot is a separate release decision requiring its own evidence and review.

## 22.2 Specify responsibilities and ownership

Use the encoder to represent local visual evidence, the causal temporal model to estimate actions, and an observation-driven decoder to construct segments. Maintain a separate procedure-state service that records completed and invalidated facts. Generate typed candidates from those facts and the observation history. Use a VLM only for supported verification questions that its available clip can address.

```text
video + timestamps + build identity
                 |
        causal feature service
                 |
        temporal model logits
                 |
      observation-driven segments
                 |
       procedure-state service ------ procedure version
                 |
          typed candidates
                 |
        evidence/coverage check
                 |
      optional semantic verification
                 |
       incident + review outcome
```

The normal procedure graph can contribute a comparison score or valid-path hypothesis, but it must not replace the observation-driven path used to assess deviations. Preserve both when they disagree. A candidate should be explainable as a relationship among evidence and a rule, not merely as an unexplained change in a global anomaly number.

Assign durable ownership. The video service owns clip availability. The feature service owns feature-version and availability metadata. The temporal service owns provisional and committed action estimates. The procedure service owns facts for each build instance. The incident service owns deduplication, verification status, and review history. Shared terminology does not require several services to mutate the same state.

## 22.3 Make every boundary inspectable

A feature record should identify what time interval contributed to the representation, when the representation became available, and which configuration produced it. A segment record should distinguish an estimated boundary from the time of commitment. An incident should refer to the relevant segments and rule version.

```json
{
  "schema": "factory.step-event.v1",
  "event_id": "build-041-step-003-rev-1",
  "build_id": "build-041",
  "stream_epoch": "cam2-epoch-008",
  "procedure_version": "bracket-v7",
  "model_version": "causal-tcn-pilot-01",
  "step": "tighten_fastener",
  "interval_s": [83.0, 86.0],
  "committed_at_s": 87.1,
  "evidence_refs": ["features-160:173", "clip-041-b"],
  "coverage": "complete_for_relevant_region",
  "revision": 1
}
```

These identifiers and fields are a capstone schema, not a claim that the same JSON is accepted unchanged by VSS. Vendor-facing adapters translate the application contract into the deployed transport schema. Keep the internal research data representation separate from runtime transport, as the report recommends. [S, “How VSS fits the data layer”]

An action confidence could be included with its calibration version, but it should not be reused as an error probability. The incident combines action evidence, prerequisites, coverage, tool identity, and rule semantics. Those are different uncertain quantities.

## 22.4 Construct four reference executions

The first reference execution is a normal build. Alignment is observed, insertion has a supported postcondition, tightening occurs, and inspection closes the procedure. The procedure service should advance without generating a wrong-order incident.

The second execution omits insertion under complete relevant coverage. Tightening is still recognized as tightening. At the closure opportunity, the system records an unmet insertion prerequisite. A normal-only decoder that invents an insertion to avoid the illegal transition fails this test, even if its final action sequence looks smooth.

The third execution has the same visible alignment and tightening events but includes an observation gap between them. The correct output is not a confident omission. The system records that insertion may have occurred during unavailable evidence and sends the case to uncertainty or review handling.

The fourth execution performs allowed rework. Inspection is followed by loosening or removal, renewed insertion, tightening, and inspection. The procedure state invalidates affected postconditions when the part is removed. It then rebuilds the supported facts through the rework path. A permanently monotone completed-step set fails this test.

| Execution | Required output | Failure exposed |
|:--|:--|:--|
| Normal | Supported step sequence; no wrong-order incident. | Spurious transitions or over-sensitive rules. |
| Observable omission | Tightening preserved; prerequisite violation recorded. | A normal graph rewriting the evidence. |
| Gap before tightening | Uncertain prerequisite judgment. | Missing evidence treated as absence. |
| Allowed rework | Facts invalidated and re-established. | A list model unable to represent valid repair. |

These are specifications, not measured accuracy results. Record example videos or synthetic event streams for them, label the intended outputs, and make them regression fixtures before increasing system scope.

## 22.5 Replay the live timing contract

A stored video contains information that a live system has not yet received. The replay must release each frame, feature, telemetry observation, and message according to its simulated availability time. Sorting by event time and immediately supplying the whole record would hide lookahead and lateness errors.

For each candidate, retain a trace such as:

```text
83.0   tightening becomes visually observable
83.5   first relevant feature position ends
83.8   feature becomes available
84.0   action evidence exceeds candidate threshold
85.0   persistence requirement is satisfied
87.0   requested evidence clip post-context ends
87.3   clip retrieval completes
88.1   verifier response is recorded
```

The illustrative end-to-end delay from first observability to verified response is 5.1 seconds. The service must also report the earlier candidate time because candidate assistance and verified quality review are different outputs. This trace does not prescribe an acceptable delay; it shows how to calculate the delay of the policy actually implemented.

Introduce late and duplicate messages deliberately. Replaying the same segment event twice should not create two incidents. Restarting a service should not attach an old completed-step set to a new product. A camera reconnect should change or validate the stream epoch before reusing tracking identities.

## 22.6 Build the evaluation package

The package should contain the split manifest, annotation guide, procedure version, model and feature configurations, calibration choices, and a replay record. Report segmentation quality and typed incident quality separately. Include frame accuracy, edit score, segment F1, matched-boundary error, false alerts per observed operating hour, missed errors, detection delay, and unknown or gap coverage.

A release with a low false-alert count because it abstains on most difficult footage is not equivalent to one that covers the full intended workload. Report the denominator for every metric. Excluded periods, no-build periods, camera failures, and unsupported product variants should be identifiable rather than silently removed from the report.

Compare the complete hybrid against the earlier baselines under the same evidence-availability constraint. The best architecture is the smallest one that satisfies the agreed task contract with demonstrated reliability, not the architecture with the most model families. The report's staged implementation plan is valuable precisely because it makes these comparisons possible. [S, “Recommended implementation progression”]

## 22.7 Decide how humans interact with the evidence

An operator or reviewer needs the observed action, expected prerequisite, relevant evidence interval, coverage status, and the reason for uncertainty. A label such as `error=1` is not enough. The interface should distinguish a candidate from a verified incident and a service failure from an uncertain visual judgment.

Review outcomes should be versioned annotations, not silent edits to earlier records. A reviewer may reject a candidate because the action was misrecognized, because the procedure specification was wrong, because evidence was missing, or because the verifier exceeded its clip context. These outcomes imply different changes to the system.

**Governance design guidance.** The report does not provide a legal assessment, employment policy, or safety certification. For this capstone, define the permitted purpose of video collection, retention boundaries, access roles, review procedures, and a process for contesting incorrect records. Do not infer intent or general competence from an uncertain procedural trace, and do not use the experimental system as the sole basis for disciplinary or safety-critical decisions. Appropriate organizational, legal, and safety review must be specific to the deployment. This paragraph describes a conservative design boundary, not jurisdiction-specific legal advice.

## 22.8 Stage the release and its rollback

Offline evaluation tests the model and labeling contract. Timed replay tests the complete event path. Shadow operation tests live conditions without acting on outputs. A monitored pilot introduces a limited operational audience and explicit review. Each stage should preserve enough evidence to explain a discrepancy with the preceding stage.

Release models, schemas, procedure definitions, and calibration settings as a compatible set. Rolling back only the neural checkpoint while retaining an incompatible feature encoder can produce a system that starts successfully but changes the meaning of every input vector. The rollback unit should include the contracts that determine interpretation.

A health failure should not be converted into a worker error. If clip retrieval fails, retain the candidate with an operational verification status. If feature dimensions change unexpectedly, reject or quarantine the input. If state cannot be restored reliably after a restart, open an unknown interval rather than assuming that the procedure has returned to its beginning.

## 22.9 The final design review

Before moving beyond shadow mode, answer three questions with artifacts rather than assurances. Can a reviewer trace a reported error to its evidence and rule? Can the replay reproduce when that evidence became available? Can the system demonstrate a correct uncertain output when the evidence is insufficient?

A negative answer identifies work that remains regardless of the average segmentation score. A positive answer does not guarantee generalization; it establishes that the system's claims are inspectable enough to evaluate and improve. New workers, stations, procedures, camera placements, and operating conditions still require the held-out tests defined earlier.

## 22.10 Exercises

**Exercise 22.1.** A service restarts and receives a duplicate tightening event for the previous build. Name the identifiers and state checks needed to prevent that event from changing the current build's procedure state.

**Exercise 22.2.** A pilot reports half as many false alerts after a new release, but its unknown-coverage fraction increases from 5% to 45%. What comparisons are required before claiming an improvement?

**Exercise 22.3.** Write the expected outputs for an observable omission, the same visible actions separated by a camera gap, and a valid rework sequence. Explain why a single normal/anomalous bit loses information needed for review.

## 22.11 The complete system

The book began by distinguishing an action from its procedural meaning. The completed design preserves that distinction at every level. Video produces evidence; a temporal model organizes that evidence into actions; explicit state and duration describe the procedure; typed rules identify supported deviations; verification addresses selected remaining questions; evaluation measures both useful decisions and uncertainty.

The resulting architecture does not depend on every component being perfect. It depends on components reporting what they observed, what they assumed, when they knew it, and what they could not establish. That is the basis for a procedural video system that can be tested, debugged, and improved without disguising missing evidence as certainty.

# Appendix A. Notation {#appendix-a}

The book distinguishes raw frames, sampled feature positions, action labels, and procedural facts. A duration measured in feature positions must be converted using the feature stride before it is compared with a duration in seconds. Local equations sometimes introduce additional symbols; those definitions take precedence within their immediate context.

## A.1 Observations and model outputs

| Symbol | Meaning | Typical shape or unit |
|:--|:--|:--|
| $X=(x_1,\ldots,x_T)$ | Raw video frames. | $T$ frames. |
| $c_t$ | Clip used to form a temporal feature. | Frames over a specified interval. |
| $e_t=f_\theta(c_t)$ | Learned clip embedding. | $\mathbb R^d$. |
| $E$ | Sequence of embeddings. | $[N,d]$ in mathematical notation. |
| $N$ | Number of temporal feature positions. | Positions, not seconds. |
| $d$ | Embedding dimension. | Channels. |
| $\Delta$ | Feature stride. | Seconds per position. |
| $\ell$ | Permitted future context. | Positions or seconds, explicitly stated. |
| $y_t$ | Observed-action label at a position. | One of $K$ labels. |
| $z_t$ | Hidden state in a probabilistic model. | One of $K$ states. |
| $h_t$ | Learned temporal hidden representation. | Channel vector. |
| $l_t(k)$ | Logit or stated score for class $k$. | Real-valued score. |
| $q_t(k)$ | Neural class probability. | Softmax distribution over classes. |
| $m_t$ | Validity or availability indicator. | Boolean, with explicit semantics. |

The code uses channel-first tensors for convolution: features are $[B,d,N]$ and stage outputs are $[S,B,K,N]$. This is an implementation layout, not a different definition of the temporal sequence. Convert layouts explicitly at the boundary.

## A.2 Probabilistic sequence models

| Symbol | Meaning |
|:--|:--|
| $\pi_j$ | Initial probability of hidden state $j$. |
| $A_{ij}$ | Transition probability or explicitly identified transition potential from $i$ to $j$. |
| $b_j(x_t)$ | Observation likelihood under state $j$ in a generative model. |
| $\alpha_t(j)$ | Forward joint probability of observations through $t$ and state $j$. |
| $\beta_t(j)$ | Backward likelihood of later observations given state $j$ at $t$. |
| $\gamma_t(j)$ | Smoothed state posterior. |
| $\delta_t(j)$ | Best-path score ending in $j$ at position $t$. |
| $\psi_t(j)$ | Stored maximizing predecessor for Viterbi reconstruction. |
| $D$ | State or segment duration. |
| $p_j(d)$ | Probability mass of completed duration $d$ in state $j$. |
| $S_j(a)$ | Survival probability $P(D\ge a\mid j)$ for the discrete convention used here. |
| $h_j(a)$ | Discrete hazard $P(D=a\mid D\ge a,j)$. |
| $V(t,j)$ | Best completed HSMM segmentation of a prefix ending at $t$ in state $j$. |
| $D_{\max}$ | Maximum duration considered by a bounded-duration decoder. |

A transition factor in an HMM is applied between neighboring positions, including self-transitions. A transition factor in the segmental HSMM formulation is applied between segments; the duration factor controls time spent within a segment. Mixing these conventions changes the model.

## A.3 Neural models, procedures, and metrics

| Symbol | Meaning |
|:--|:--|
| $Q,K,V$ | Query, key, and value matrices in attention; $K$ here is not a class count. |
| $W_Q,W_K,W_V$ | Learned attention projections. |
| $R$ | Receptive field in input positions. |
| $G=(V,E)$ | Procedure graph; these $V,E$ denote vertices and edges, not embeddings or attention values. |
| $\mathcal L$ | Training loss, with named component losses. |
| $\lambda$ | Weight of a loss or structured-score component. |
| $\tau$ | Temperature or clipping threshold, depending on the explicitly defined equation. |
| $[s,e)$ | Half-open interval including $s$ and excluding $e$. |
| $\operatorname{tIoU}$ | Temporal intersection over union of two intervals. |
| TP, FP, FN | True positives, false positives, and false negatives under a stated matching policy. |
| $t_{\rm observable}$ | Earliest time the relevant error evidence becomes observable. |
| $t_{\rm alert}$ | Time the application emits the specified alert state. |

For event traces, distinguish evidence time, availability time, processing time, and commitment time. An accurate event timestamp does not imply that the system knew the event at that time.

# Appendix B. Glossary {#appendix-b}

The terms below are defined for this book's procedural-video setting. Chapter references indicate where their consequences are developed rather than merely where the word first appears.

**Action recognition.** Predicting the identity of an action from visual evidence. In a trimmed-clip task, the action interval is provided; recognizing its label does not test whether the system can find its boundaries. Chapters 1 and 5.

**Action segmentation.** Assigning labels across a continuous sequence and grouping consecutive positions into action intervals. Boundary quality and fragmentation are part of the task. Chapters 1, 10–12, and 18.

**Action localization.** Predicting temporal intervals and action categories in an untrimmed video, often as a set of detections rather than a single dense label at every position. Chapters 1 and 12.

**Availability time.** The earliest time at which a piece of evidence is accessible to a downstream decision. It may be later than the interval the evidence describes. Chapters 6 and 16.

**Background.** An observed interval outside the defined action vocabulary or relevant work, according to the annotation policy. Background is not interchangeable with an unknown action or unavailable video. Chapters 2–3.

**Boundary confidence.** An annotation's recorded certainty about the location of an action start or end. It helps distinguish model timing errors from genuinely ambiguous reference boundaries. Chapter 3.

**Calibration.** Agreement between stated probabilities and observed frequencies for comparable predictions under the evaluated distribution. Calibration is not the same as ranking quality or accuracy. Chapter 18.

**Causal model.** A model whose output at a position does not depend on future evidence beyond the declared allowance. A causal temporal network does not make a noncausal encoder or retrospective decoder causal. Chapters 1, 10, 16, and 21.

**CFF.** An ambiguous abbreviation in the supplied research context. The book discusses cross-frame, coarse-to-fine, and cross-feature fusion as separate design ideas rather than claiming one universally defined CFF model. Chapter 12.

**Closure opportunity.** An event or point in a procedure after which a prerequisite's continued absence can support an omission judgment, provided the relevant evidence coverage is adequate. Chapter 14.

**Commitment.** The policy decision to publish a state or boundary as stable enough for downstream use. A provisional model estimate and a committed event may have different timestamps and revision rules. Chapter 16.

**Contrastive learning.** Learning representations by increasing compatibility for selected positive pairs relative to alternatives. What counts as a positive pair and which augmentations preserve labels determine what information the representation is encouraged to retain. Chapter 5.

**Duration model.** An explicit distribution over time spent in a state or segment. A completed-duration mass, survival probability, and hazard answer different questions. Chapter 9.

**Embedding.** A vector representation of an input such as a video clip. Its dimension does not by itself establish that it preserves motion direction, object identity, or fine action boundaries. Chapters 5–6.

**Emission likelihood.** In a generative HMM, the likelihood of an observation conditioned on the hidden state. A neural posterior over classes is not automatically this quantity. Chapters 7 and 13.

**Error candidate.** A potentially reportable deviation supported enough to enter persistence, verification, or review handling, but not necessarily a finalized incident. Chapters 14–15.

**Evidence coverage.** The extent to which the relevant action opportunity, object, and region were observable. Continuous recording alone does not guarantee visibility of a small manipulated part. Chapters 3, 14, and 22.

**Filtering.** Estimating the current hidden state using observations available through the current position. Unlike smoothing, it does not condition on later observations. Chapter 8.

**Frame accuracy.** The fraction of evaluated positions assigned the correct action label. Long actions can dominate it, and a few incorrect positions can create many spurious segments. Chapter 18.

**Hidden Markov model, HMM.** A model with a first-order hidden-state transition process and state-conditioned observations. Its ordinary self-transition mechanism implies a geometric dwell-time distribution. Chapters 7–8.

**Hidden semi-Markov model, HSMM.** A hidden-state sequence model with explicit segment-duration distributions. The formulation used here applies transitions between segments and duration factors within segments. Chapter 9.

**Hysteresis.** A stateful threshold policy using different entry and exit conditions. It reduces repeated state changes around a single threshold but must not be confused with an evidence-validity rule. Chapter 14.

**Incident.** A reportable episode under the application's persistence, verification, and reporting policy. One sustained violation should not automatically become many independent incidents. Chapter 14.

**Lookahead.** Future context used relative to a prediction's nominal position. Encoder windows, temporal processing, and commitment rules can each contribute to the total. Chapters 1 and 16.

**Multi-stage refinement.** Successive temporal models that refine an earlier stage's predictions. Later stages add temporal dependencies, so their receptive fields compose. Chapter 11.

**Observation gap.** An interval for which relevant evidence is unavailable. It should affect confidence and coverage rather than be interpreted automatically as inactivity or omission. Chapters 14 and 16.

**Omission.** Failure to perform a required step within the relevant opportunity under the procedure definition. A justified omission judgment requires more than the absence of a detected label. Chapter 14.

**Postcondition.** A fact expected to hold after an action, such as a fastener being inserted. Visual recognition of a motion and support for its postcondition are distinct pieces of evidence. Chapters 2 and 14.

**Prerequisite.** A fact or condition required before a procedural transition is valid. Multiple prerequisites may depend on history not represented by the immediately preceding action. Chapters 2 and 13.

**Procedure state.** The current collection of established, uncertain, and invalidated facts for a particular procedure instance. It is not necessarily identical to the current action label. Chapters 2, 13, and 22.

**Receptive field.** The input positions that can influence an output through a network's computation. Convert its position count to physical time using the actual stride and encoder interval. Chapters 10–11.

**Rework.** A permitted return to earlier operations to correct or repeat work. It can invalidate facts previously established during the same build. Chapters 2 and 22.

**Right censoring.** Observing that an action has lasted to a certain time without observing its completion. Treating that elapsed time as its final duration biases duration estimation. Chapter 9.

**Smoothing.** Estimating hidden states using observations both before and after the position of interest. Its retrospective information can improve an estimate but changes the online timing contract. Chapter 8.

**Temporal convolutional network, TCN.** A network applying convolutions across temporal features. Dilation expands its temporal support; padding determines whether that support includes future positions. Chapters 10–11.

**Unknown.** A supported statement that the system cannot assign a reliable known action or fact value under the current evidence. It is not a synonym for background, wrong, or absent. Chapters 2 and 14.

**Verification.** Additional assessment of a candidate using selected evidence and a defined question. It may confirm, reject, remain uncertain, or fail operationally. Chapters 15 and 17.

**Viterbi decoding.** Dynamic programming that finds the best complete hidden path under the specified scores. It differs from selecting the largest marginal state probability at each position. Chapter 8.

**Vision-language model, VLM.** A model relating visual inputs and language. In this architecture, its primary assigned role is selected evidence verification rather than dense, authoritative adjudication of every video position. Chapter 15.

**VSS.** NVIDIA's Video Search and Summarization infrastructure discussed in the supplied report and checked documentation. The book uses it as a video and analytics substrate around custom procedural models, not as a pre-trained solution to the entire task. Chapter 17.

# Appendix C. Exercise solutions {#appendix-c}

The numerical exercises have definite results under their stated assumptions. Design exercises can have several defensible answers; the solutions identify the evidence and distinctions a satisfactory answer must preserve. None of the hypothetical thresholds or probabilities below is a measured factory-performance result.

## C.1 From video to procedural decisions

**Solution 1.1.** The evaluation is trimmed action recognition. It does not test discovery of action start and end boundaries, or the organization of an untrimmed continuous stream into an appropriate action sequence, including background and interruptions. High label accuracy with supplied intervals does not establish either ability.

**Solution 1.2.** Four positions at 0.5 seconds contribute two seconds. Adding the encoder's one second gives a maximum input lookahead of three seconds under the stated additive dependency assumption. Processing and queueing delays are additional quantities.

**Solution 1.3.** Both records can contain the same observed step, boundary estimate, and calibrated action confidence. The continuously observed case can record an unmet insertion prerequisite and a wrong-order or omission candidate at the relevant closure opportunity. The obstructed case should record incomplete coverage and an uncertain prerequisite judgment. The model should not lower action confidence merely to encode uncertainty about a different procedural question.

## C.2 Labels, procedure graphs, and state

**Solution 2.1.** The Cartesian product has $8\times20=160$ pairs, but some verbs cannot meaningfully apply to some nouns and others may be valid but absent from the training data. A compatibility matrix $\psi(v,n)$ can mask impossible pairs or supply a learned score. Keep “unseen but possible” separate from “not allowed by the ontology.”

**Solution 2.2.** A last action of `tighten_right` does not establish whether `tighten_left` occurred earlier, was omitted, or was later undone. Maintain separate facts such as `left_tightened` and `right_tightened`, each with evidence and an instance association. The cover transition requires both facts to be supported.

**Solution 2.3.** Removal can invalidate insertion, tightening, and inspection facts for that fastener. Depending on the fixture and procedure, it may also invalidate alignment. Reinsertion should establish a new insertion fact; it should not restore tightening or inspection automatically. Invalidation rules are part of the procedure specification, not inferred from a generic completed-step list.

## C.3 Building the dataset

**Solution 3.1.** Consecutive two-second windows at a half-second stride overlap by 1.5 seconds, so independent assignment can place nearly identical video content in both sets. Assign sessions or builds to splits first, then extract all their windows within the assigned split. Group synchronized views of the same build together unless the experiment explicitly studies a different, carefully delimited question.

**Solution 3.2.** An obscured correct tool could be interpreted as absent or wrong, creating false incidents. Use a tool identity field plus an observation state such as “visible,” “none observed under adequate coverage,” or “unobserved”, and retain confidence or visibility metadata as needed. A null identity alone cannot distinguish those meanings.

**Solution 3.3.** Training and testing on the same physical builds confounds view transfer with session and action-instance familiarity. Use session-disjoint builds while holding out the target view, and compare matched protocols for familiar and held-out views. Report separately any experiment that intentionally permits synchronized training views of the test actions.

## C.4 Mathematical tools for temporal inference

**Solution 4.1.** Under $L=EW^\top+b$, the weights have shape $[18,256]$, the bias $[18]$, and the logits $[1200,18]$. The feature cache occupies $1200\times256\times4=1{,}228{,}800$ float32 bytes, excluding metadata and array overhead.

**Solution 4.2.** Exponentiation gives $(1,2,3)$ and the sum is six, so the probabilities are $(1/6,1/3,1/2)$. Adding a shared constant multiplies numerator and denominator by the same factor, which cancels. A stable implementation subtracts the largest logit rather than evaluating unnecessarily large exponentials.

**Solution 4.3.** State A has total probability $0.18+0.17=0.35$, greater than B's 0.30. The best individual path ends in B because $0.30>0.18$. This is the distinction between summing compatible histories and choosing one history.

## C.5 Embeddings and representation learning

**Solution 5.1.** Both averages equal $10/4=2.5$. The last-minus-first statistic equals 3 for the first sequence and -3 for the second. A representation retaining this statistic distinguishes the direction lost by the mean, although it is not a general solution to video understanding.

**Solution 5.2.** One intervention is higher-resolution, object-centered crops; another is adding explicit part detections or a synchronized alternative view. Hold the temporal model, splits, and training budget fixed while testing each intervention separately. Measure noun accuracy, per-part confusion, and relevant wrong-part error performance on held-out workers or sessions, not only aggregate verb accuracy.

**Solution 5.3.** Horizontal reflection may exchange left and right locations or invalidate handed geometry in the procedure. Temporal reversal can turn insertion into removal or pickup into placement. These transformations are valid only when labels and semantics are transformed appropriately, or when the task is invariant to the transformation.

## C.6 Sampling, perception, and feature fusion

**Solution 6.1.** There are fifteen intervals between sixteen samples, giving $15/8=1.875$ seconds between the first and last timestamps. A half-open two-second acquisition window can contain those samples without placing a sample exactly at its excluded right endpoint.

**Solution 6.2.** No. The feature contains evidence through time 15 and does not exist for the decision committed at 12. Offline alignment can associate a representation with an earlier interval, but a streaming replay must respect when the representation becomes available. Backdating its timestamp does not remove the future information.

**Solution 6.3.** A zero vector might also be a valid encoded value or mean “no detected object.” A mask explicitly records unavailability, while observation age distinguishes a fresh detection from stale carried-forward evidence. The fusion model can then learn or implement a policy appropriate to those cases.

## C.7 Hidden Markov models

**Solution 7.1.** The joint path probability is $0.9\times0.6\times0.7\times0.3\times0.3\times0.5=0.01701$. The factors are the initial state, first emission, first transition, second emission, second transition, and third emission.

**Solution 7.2.** The mean geometric duration is $1/(1-0.8)=5$ positions. At 0.5 seconds per position, that is 2.5 seconds. This uses the duration convention in which the first occupied position counts as one.

**Solution 7.3.** A zero transition prevents a valid-path decoder from selecting an impermissible history. If the worker actually made that transition, the same zero can force the decoder to relabel or insert actions. Preserve an observation-driven or expanded-path hypothesis for error detection and use the normal graph as a separate validity model.

## C.8 Forward, backward, and Viterbi inference

**Solution 8.1.** $0.008643+0.047835=0.056478$. This sum includes the probability of every supported path. The best path contributes 0.02916 to that total, while the other supported paths contribute the remainder.

**Solution 8.2.** Filtering at position 2 uses only $u,v$. Smoothing also uses the later observation $w$, which is more likely under B and changes the relative support of histories passing through the middle position. A live estimate cannot use that information before it arrives unless the output is delayed or revised.

**Solution 8.3.** Supply a sequence of length at least two, a valid initial distribution, finite emissions, and an all-zero transition matrix represented as negative infinity in log space. `forward` should report negative-infinite total support. A decoder that promises a supported path or posterior should raise an explicit exception. Returning an arbitrary all-zero state path would conceal the impossible model.

## C.9 Explicit duration

**Solution 9.1.** With the book's convention $S(a)=P(D\ge a)$, $S(2)=0.5+0.3=0.8$. The hazard is $h(2)=p(2)/S(2)=0.5/0.8=0.625$. Always state the survival convention because a strict $P(D>a)$ convention shifts discrete indices.

**Solution 9.2.** A long run of A could be represented either as one long A segment or as several short A segments. Those alternatives apply different numbers of duration and transition factors while describing the same dense labels. Disallowing adjacent equal-state segments avoids that ambiguity in the displayed formulation; another formulation must define explicitly how such renewals are interpreted.

**Solution 9.3.** Six seconds is a lower bound on duration, not the observed completion time. Treating it as a completed duration adds false evidence for short steps. Use a censored likelihood based on survival beyond the observed elapsed time, with the endpoint convention matched to the observations.

## C.10 Temporal convolutional networks

**Solution 10.1.** $R=1+2(1+2+4+8)=31$ positions. The first-to-last feature timestamp span is $(31-1)\times0.5=15$ seconds. Encoder windows can extend the raw-frame evidence interval further.

**Solution 10.2.** Symmetric padding allows the output at $t$ to use inputs at $t-8$, $t$, and $t+8$. The last dependency is future information. Pad sixteen positions on the left and zero on the right to preserve length with a causal kernel-three, dilation-eight convolution.

**Solution 10.3.** Evaluate a sequence, perturb only inputs after a cutoff, and compare outputs through the cutoff. Disable dropout or control randomness, inspect normalization for sequence-wide statistics, and hold initialization and alignment fixed. Also compare a standalone prefix with the same prefix of the full evaluation. Test the encoder separately because leakage can precede the TCN.

## C.11 Multi-stage refinement and training losses

**Solution 11.1.** Take truth `AAAAAABBBBBB` and prediction `AABAAABBBBBB`. Eleven of twelve positions are correct, but the collapsed sequences are `AB` and `ABAB`. Their edit distance is two and the displayed normalized edit score is 50. One incorrect position creates extra action segments despite frame accuracy of about 91.7 percent.

**Solution 11.2.** The composed receptive field is $1+3(15-1)=43$ positions, assuming stride-one stages, the stated support, and no additional temporal operations.

**Solution 11.3.** Compare brief-action recall, segment F1, edit score, start/end error, and detection delay, then inspect examples where an insertion disappears or merges into its neighbors. Fewer segments is not inherently better. The acceptable tradeoff depends on whether the lost short action is essential to the operational error task.

## C.12 Transformers and multiresolution models

**Solution 12.1.** The output is $0.25(2,0)+0.75(0,4)=(0.5,3)$. Masking the second key leaves the first key with normalized weight one, producing $(2,0)$.

**Solution 12.2.** $Nw=57{,}600\times128=7{,}372{,}800$, whereas $N^2=3{,}317{,}760{,}000$. Their ratio is 450. These count potential pairwise temporal interactions in the simplified dense-versus-local comparison, not end-to-end runtime, memory use of a particular optimized implementation, or achieved hardware throughput.

**Solution 12.3.** One precise experiment is to concatenate causal tool-state features, with masks and ages, to fixed RGB embeddings before the same TCN. Compare against RGB-only features under identical session splits, lookahead, and training budget. Measure wrong-tool precision, recall, false alerts per hour, and segmentation changes. Calling this cross-feature fusion identifies the intended mechanism instead of relying on an ambiguous abbreviation.

## C.13 Hybrid recognition and procedure decoding

**Solution 13.1.** A normal-only decoder cannot represent an illegal skip, so it may assign some tightening evidence to an invented insertion. Preserve an expanded or observation-driven path and evaluate its prerequisites separately, optionally comparing its score with the best normal path. Do not erase the action evidence before asking whether it violates the procedure.

**Solution 13.2.** The ratios are $0.4/0.1=4$ and $0.5/0.5=1$. Under the idealized relation, these are proportional to class-conditioned likelihoods up to an observation-dependent factor. They are not normalized posteriors, and applying the relation to context-dependent, miscalibrated neural scores requires additional care.

**Solution 13.3.** The expanded hypothesis exceeds the valid hypothesis by eight score units under the chosen scoring system. That is a compatibility discrepancy, not a calibrated probability. Poor visual evidence, an incorrect procedure version, unmodeled legitimate rework, or badly scaled duration terms can also produce a large gap.

## C.14 Typed errors and incident state

**Solution 14.1.** A required future action may simply not be due yet. A closure event for insertion is the onset of tightening when insertion is required beforehand, or a procedure-specific completion checkpoint. A confident omission judgment also requires adequate evidence coverage of the opportunity in which insertion could have occurred.

**Solution 14.2.** The first score crosses the high threshold and starts the pending episode at 0.0 seconds. Both later scores remain above the low threshold, so the episode is not cleared. At 1.0 seconds the elapsed persistence reaches one second and an incident occurs. Requiring every score to exceed the high threshold would be a different policy.

**Solution 14.3.** Occlusion removes tool evidence. It does not establish that a different tool is present, nor that an earlier wrong-tool episode has resolved. Preserve the uncertainty and apply the explicit gap policy to the open incident and review state.

## C.15 Vision-language verification

**Solution 15.1.** No. The clip does not cover the opportunity in which insertion might have occurred. Confirmation would need adequate earlier video, supported object-state or telemetry evidence, or a trustworthy prerequisite record with its own coverage provenance. The absence of insertion in a late clip is not evidence of its earlier omission.

**Solution 15.2.** Final recall is $0.92\times0.90=0.828$, or 82.8 percent. Here 0.90 is acceptance conditional on a true error reaching the verifier, so the multiplication follows the conditional decomposition. A confirmed-only verifier cannot recover errors that never become candidates.

**Solution 15.3.** Use a verification judgment such as `uncertain` with an operational status `completed`, versus no completed judgment with status `timeout` or `unverified`. Retain reasons and evidence coverage separately. Treating both as false candidates would count operational and epistemic failures as correct rejections and distort precision, recall, and availability analysis.

## C.16 Streaming inference and latency

**Solution 16.1.** The trace starts at observability time 100.00 and records the verification result at 104.70, giving 4.70 seconds. The post-context endpoint is tied to the event interval and some of that context is acquired while earlier stages process and persist the candidate. Adding a new full wait after candidate generation would count overlapping elapsed time twice.

**Solution 16.2.** The nominal rate is $12/0.25=48$ feature arrivals per second. GPU demand also depends on encoder computation, tensor sizes, batch formation, concurrent services, hardware, data movement, and latency constraints. Arrival rate is an input to a capacity experiment, not the experiment's result.

**Solution 16.3.** Use camera or stream identity, a new stream epoch, a build or workpiece instance ID, and an explicit mapping from tracks to that instance. Validate procedure version and restored state before processing new events. A bare reused track ID is not a durable build identifier.

## C.17 NVIDIA VSS and model serving

**Solution 17.1.** The custom responsibilities include the appropriate fine-motion representation, dense step model, procedure and duration state, typed error rules, training data, and application adapters. An embedding service produces representations; it does not automatically supply the application's label ontology, boundary model, procedure constraints, or calibrated incident policy.

**Solution 17.2.** The vector dimension is part of the encoder-consumer contract. Silent truncation changes the representation without a validated transformation. Reject or quarantine the mismatched message, report the contract error, and use a versioned adapter or retrained compatible model when the representation changes.

**Solution 17.3.** Serving sequence IDs relate inference requests to model state. They do not define which physical build is being processed, which procedure is applicable, which facts survived rework, or whether an incident has already been reported. Those remain application-level responsibilities.

## C.18 Evaluation and calibration

**Solution 18.1.** The intersection has length three and the union length five, giving tIoU 0.6. Under one-to-one matching, at most one of the two predictions can be a true positive for that ground-truth action; the additional prediction is unmatched and counts as a false positive under the stated detection protocol.

**Solution 18.2.** There are 95 true positives and $0.01\times9{,}900=99$ false positives. Precision is $95/(95+99)=95/194\approx0.4897$, or 48.97 percent. A substantial false-positive-rate improvement still does not make most alerts overwhelmingly reliable in this rare-event example.

**Solution 18.3.** Boundary error is conditional on obtaining a match. Missing the difficult half of the actions can make the surviving boundary estimates look excellent. Report action recall, the number and proportion of matched segments, per-class coverage, and the full segment F1 protocol alongside the conditional timing errors.

## C.19 An experimental program

**Solution 19.1.** The comparison does not isolate architecture from access to future information. Compare both models with matched causal or bounded-lookahead inputs, matched feature representations, and comparable training protocols. A separate experiment can measure the value of lookahead, clearly labeled as such.

**Solution 19.2.** Investigate the procedure graph, fact updates, closure conditions, coverage assumptions, and rule implementation first. Ground-truth actions have already removed recognition error from the test, so changing the visual encoder cannot directly repair the defect demonstrated by this oracle experiment.

**Solution 19.3.** A suitable hypothesis is that tool telemetry improves detection of incomplete tightening that RGB motion alone cannot resolve. Compare RGB plus TCN and procedure state against the same system with aligned telemetry, using held-out sessions or workers. Measure typed-error recall, false alerts per hour, and detection delay, while controlling for missing telemetry and workpiece association.

## C.20 Sequence laboratory

**Solution 20.1.** For a sequence with at least two observations, the forward total becomes negative infinity because no transition supports a complete path. The smoothing and Viterbi routines raise `ValueError`. The initial forward row can remain finite because the first observation still has support.

**Solution 20.2.** Resumed visibility does not reveal what happened during the gap. Insertion might have occurred and a later action might have invalidated another fact. Restore confidence only with additional evidence or a procedure-specific reconciliation rule; merely receiving another frame is insufficient.

**Solution 20.3.** The routine treats its final segment as completed at the input boundary. An ongoing action violates that assumption. An online extension needs elapsed-duration state and survival or hazard treatment for the unfinished segment, with a clearly defined censoring convention and commitment policy.

## C.21 Causal TCN laboratory

**Solution 21.1.** The future-perturbation test should detect changed prefix predictions near the cutoff, and the full-versus-prefix test can also fail. Symmetric padding preserves the output length but permits future inputs, so shape correctness does not establish causal correctness.

**Solution 21.2.** Cross-entropy validates or indexes target classes before a later mask could discard the resulting loss. An invalid label can therefore raise an error first. Replacing excluded targets with the ignore index before the operation makes their exclusion explicit and safe.

**Solution 21.3.** Three stages give $R=1+3(15-1)=43$ feature positions. The first-to-last feature span is $(43-1)\times0.5=21$ seconds, before accounting for the raw-frame support of each embedding.

## C.22 Capstone

**Solution 22.1.** Check a durable event ID and revision for deduplication, the build or workpiece ID for instance association, the stream epoch and track mapping for identity reuse, and the procedure/model compatibility metadata. State restoration must know the last processed event or equivalent idempotency record. Rejecting or routing a stale event is preferable to mutating the current build's facts.

**Solution 22.2.** Compare false alerts over the same intended workload, report coverage and abstention explicitly, inspect recall on difficult cases, and evaluate matched subsets as well as total operating exposure. The new system may have reduced alerts by declining to judge much of the footage. Whether that tradeoff is useful depends on the intended coverage requirement; it is not automatically an accuracy improvement.

**Solution 22.3.** Observable omission should preserve the observed tightening action and report a supported unmet prerequisite at closure. The gap case should preserve the same action but record an uncertain history and incomplete coverage. Valid rework should invalidate and re-establish the affected facts without treating the permitted return as an error. A binary anomaly bit loses the distinction between a supported violation, unavailable evidence, and a legitimate repair, all of which require different review and operational responses.

# Appendix D. Source map and implementation qualifications {#appendix-d}

This appendix identifies how the textbook develops the supplied research and where it adds a qualification needed for a complete implementation. The book is an expansion of that research, not a report of a new industrial experiment. Original numerical examples, code, exercises, and project schemas are teaching constructions.

## D.1 Mapping the research to the textbook

| Research section | Textbook development |
|:--|:--|
| Executive summary | Chapters 1 and 22 preserve the hybrid architecture and the separation of recognition from procedural validity. |
| Defining the problem and the training data | Chapters 1–3 develop the ontology, procedure graph, data contracts, datasets, and annotation policy. |
| Embeddings and visual representation | Chapters 4–6 develop vector mathematics, contrastive learning, video representation, sampling, and fusion. |
| HMMs, HSMMs, TCNs, and Transformers | Chapters 7–12 derive the model families and their inference or training operations. |
| Hybrid models, CFF, and error detection | Chapters 12–15 separate fusion meanings, hybrid scoring, procedural facts, typed errors, and verification. |
| NVIDIA VSS and real-time deployment | Chapters 16–17 develop availability, latency, state ownership, adapters, serving, and deployment boundaries. |
| Evaluation, implementation strategy, and learning path | Chapters 18–22 develop metrics, experiments, executable labs, and a staged pilot specification. |

The writing guidance informs the presentation: foundations precede implementation, prose explains the design consequences, and code and traces make assumptions inspectable. Its Systemlab-specific widgets are not implemented in a static Markdown or PDF book. Instead, local runnable laboratories and adjacent trace explanations provide the relevant interactive learning mechanism. [W]

## D.2 Consequential qualifications

**Observation paths versus normal paths.** The report proposes both a structured procedure decoder and detection of invalid transitions. A strictly normal decoder can erase the evidence of those transitions. Chapters 7, 13, and 22 explicitly preserve observation-driven hypotheses and use normal-path compatibility as a separate question. This is an implementation qualification of the combined proposal, not a claim that the report supplied a complete dual-decoder algorithm.

**Posterior scores versus emission likelihoods.** The report sketches neural logits as calibrated state evidence. Chapter 13 distinguishes a generative emission likelihood from a discriminative posterior or general potential. It presents prior correction only under its stated idealized assumptions. The teaching code names an unnormalized path weight as such rather than calling every exponentiated score a probability.

**Segment transitions and durations.** The report gives an explicit-duration recurrence. Chapters 9 and 20 specify half-open boundaries, initial conditions, duration bounds, completed terminal segments, and the exclusion of adjacent equal-state segments. These conventions are necessary to obtain the executable decoder shown in the laboratory.

**Ongoing durations and censoring.** A completed-duration mass is not the appropriate likelihood for an unfinished action at the end of a live window. Chapter 9 adds survival, hazard, and censored-duration discussion. The laboratory deliberately does not claim to implement a complete online HSMM filter.

**Action absence and observability.** The report warns that missing evidence is not omission. Chapters 2, 14, and 22 make that distinction operational with evidence coverage, closure opportunities, unknown facts, and rework invalidation. The small monotone monitor in Chapter 20 is explicitly narrower than the full procedure design.

**Feature sampling and receptive fields.** The report offers initial sample rates, clip spans, and network sizes. Chapters 6 and 10–11 derive the timestamp span of sixteen samples at eight frames per second and the composed support of refinement stages. Those calculations prevent a nominal two-second clip, a position count, and a physical context interval from being conflated.

**Causality and latency.** The report separates offline from real-time prediction and includes latency components. Chapters 6, 16, and 21 extend that treatment to the complete pipeline: evidence availability, centered encoder leakage, commitment, startup context, and overlapping waits. These are explicit timing interpretations, not measured deployment latencies.

**VLM judgments and service outcomes.** The report recommends selected VLM verification. Chapters 15 and 17 distinguish a successful but uncertain judgment from an unverified result caused by an operational failure. They also constrain verification claims to the context actually supplied. A short evidence clip cannot independently establish what occurred before it began.

**Vendor defaults and dimensions.** The VSS discussion uses a checked 3.1.0 documentation snapshot, not an assertion about the latest release. Chapter 17 records `vision-embed-messages` as that snapshot's documented embedding-topic default. The report's topic names and embedding dimensions are not treated as universal interfaces. Validate configured schemas, model dimensions, and availability semantics against the deployed version. [R21–R28]

**Matching, coverage, and rare-event metrics.** Chapter 18 adds explicit one-to-one matching, empty-case conventions, coverage reporting, calibration-set separation, and an illustrative zero-event upper-rate calculation. These details make the report's evaluation recommendations operational without inventing an industrial benchmark.

## D.3 What has and has not been tested

The edition's Python sequence laboratory was executed, its regression suite passed twenty tests, and the neural laboratory passed the printed causality, shape, masked-loss, and optimizer checks. The test inputs are synthetic. The Markdown embeds the same central code as the companion modules.

No video encoder was trained or evaluated on the user's factory footage, because none was supplied. No VSS, Kafka, VIOS, or Triton deployment was executed for this edition. No throughput, industrial accuracy, false-alert rate, or operator-outcome claim is derived from the laboratory results. The capstone is a specification for obtaining that evidence.

The source does not resolve a particular factory's camera geometry, smallest relevant action, hardware budget, annotation volume, acceptable delay, or alert tolerance. The book retains those as measured project decisions instead of presenting illustrative starting values as established requirements.

## D.4 Using the references

[S] identifies the supplied research report, and [W] the supplied writing guidance. References R1–R20 identify primary dataset, representation, sequence-model, loss, or calibration sources. R21–R32 identify official NVIDIA documentation, with version-pinned URLs where available. R33 identifies the PyTorch operations used in the neural laboratory.

The bibliography is a source map rather than a claim that every named method has been reproduced. Follow a paper to replicate its experiments; follow the lab to reproduce this edition's teaching example. When those implementations differ, the text names the difference rather than treating them as interchangeable.

# References {#references}

The references below identify the supplied basis and independently checked primary sources. Links point to publisher, author, project, or official documentation pages. Vendor documentation was checked on 4 September 2026; version numbers refer to the documentation snapshot, not a claim about the newest available release.

## Supplied materials

**[S] Building a Video-Recognition Pipeline for Stepwise Worker Actions and Error Detection.** User-supplied research report, file `deep-research-report(3).md`. This is the book's requested basis. Citations with section names identify the relevant passage in that report.

**[W] Textbook Authoring.** User-supplied writing guidance, file `SKILL(20260905-021324).md`. Used for its foundations-first structure, developed technical prose, concrete examples, code, diagrams, and evidence-oriented exercises.

## Datasets and annotation

**[R1] EPIC-KITCHENS.** Official task and challenge descriptions, including action recognition and action detection. [Project and task documentation](https://epic-kitchens.github.io/2025). Used for the verb–noun formulation and the distinction between trimmed recognition and temporal detection.

**[R2] Sener, F., et al. (2022).** *Assembly101: A Large-Scale Multi-View Video Dataset for Understanding Procedural Activities.* [Primary paper, arXiv:2203.14712](https://arxiv.org/abs/2203.14712). Relevant to multi-view assembly, procedural actions, mistakes, and corrections.

**[R3] Ben-Shabat, Y., et al. (2021).** *The IKEA ASM Dataset: Understanding People Assembling Furniture through Actions, Objects and Pose.* WACV. [Publisher paper page](https://openaccess.thecvf.com/content/WACV2021/html/Ben-Shabat_The_IKEA_ASM_Dataset_Understanding_People_Assembling_Furniture_Through_Actions_WACV_2021_paper.html). Relevant to assembly actions and supporting object and pose information.

**[R4] Zhang, J., et al. (2023).** *Aligning Step-by-Step Instructional Diagrams to Video Demonstrations.* [Primary paper, arXiv:2303.13800](https://arxiv.org/abs/2303.13800). Source for instruction-to-video alignment and IKEA assembly in less controlled settings.

**[R5] CVAT.** *CVAT format.* [Official format documentation](https://docs.cvat.ai/docs/dataset_management/formats/format-cvat/). Reference for supported annotation representations and video tracks; it does not prescribe this book's complete procedural timeline schema.

## Representation learning

**[R6] Chen, T., et al. (2020).** *A Simple Framework for Contrastive Learning of Visual Representations.* ICML. [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v119/chen20j.html). SimCLR reference.

**[R7] Radford, A., et al. (2021).** *Learning Transferable Visual Models From Natural Language Supervision.* ICML. [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v139/radford21a.html). CLIP reference.

**[R8] Feichtenhofer, C., et al. (2019).** *SlowFast Networks for Video Recognition.* ICCV. [Primary paper, arXiv:1812.03982](https://arxiv.org/abs/1812.03982). Reference for video pathways with different temporal sampling rates.

**[R9] Tong, Z., et al. (2022).** *VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training.* NeurIPS. [Primary paper, arXiv:2203.12602](https://arxiv.org/abs/2203.12602). Reference for masked video pretraining.

## Sequence models, objectives, and calibration

**[R10] Rabiner, L. R. (1989).** *A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition.* Proceedings of the IEEE, 77(2), 257–286. DOI: 10.1109/5.18626. [University-hosted paper](https://www.cs.ubc.ca/~murphyk/Bayes/rabiner.pdf). Foundational HMM formulation and inference reference.

**[R11] Johnson, M. J., and Willsky, A. S. (2013).** *Bayesian Nonparametric Hidden Semi-Markov Models.* Journal of Machine Learning Research, 14, 673–701. [Journal paper page](https://www.jmlr.org/papers/v14/johnson13a.html). Reference for explicit-duration semi-Markov modeling; the laboratory is a small finite-state teaching decoder, not a reproduction of the full Bayesian model.

**[R12] Lea, C., et al. (2017).** *Temporal Convolutional Networks for Action Segmentation and Detection.* CVPR. [Primary paper, arXiv:1611.05267](https://arxiv.org/abs/1611.05267). Temporal convolution reference.

**[R13] Abu Farha, Y., and Gall, J. (2019).** *MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation.* CVPR. [Publisher paper page](https://openaccess.thecvf.com/content_CVPR_2019/html/Abu_Farha_MS-TCN_Multi-Stage_Temporal_Convolutional_Network_for_Action_Segmentation_CVPR_2019_paper.html). Reference for multi-stage refinement and temporal smoothing. The book's causal code is explicitly a teaching variant.

**[R14] Vaswani, A., et al. (2017).** *Attention Is All You Need.* [Primary paper, arXiv:1706.03762](https://arxiv.org/abs/1706.03762). Reference for scaled dot-product attention and the original Transformer formulation.

**[R15] Yi, F., Wen, H., and Jiang, T. (2021).** *ASFormer: Transformer for Action Segmentation.* [Primary paper, arXiv:2110.08568](https://arxiv.org/abs/2110.08568). Reference for temporal segmentation with specialized attention and refinement.

**[R16] Zhang, C., Wu, J., and Li, Y. (2022).** *ActionFormer: Localizing Moments of Actions with Transformers.* ECCV. [Primary paper, arXiv:2202.07925](https://arxiv.org/abs/2202.07925). Reference for multiscale features and local attention in temporal action localization.

**[R17] Singhania, D., Rahaman, R., and Yao, A. (2023).** *C2F-TCN: A Framework for Semi- and Fully-Supervised Temporal Action Segmentation.* IEEE Transactions on Pattern Analysis and Machine Intelligence. DOI: 10.1109/TPAMI.2023.3284080. [Publisher record](https://www.computer.org/csdl/journal/tp/2023/10/10147035/1NOB8RwiPEQ). Reference for coarse-to-fine temporal segmentation.

**[R18] Kahatapitiya, K., and Ryoo, M. S. (2021).** *Coarse-Fine Networks for Temporal Activity Detection in Videos.* CVPR. [Primary paper, arXiv:2103.01302](https://arxiv.org/abs/2103.01302). A related multiresolution design; it is not presented as a universal meaning of “CFF.”

**[R19] Lin, T.-Y., et al. (2017).** *Focal Loss for Dense Object Detection.* ICCV. [Primary paper, arXiv:1708.02002](https://arxiv.org/abs/1708.02002). Original focal-loss reference; adapting it to procedural imbalance is an experimental choice.

**[R20] Guo, C., et al. (2017).** *On Calibration of Modern Neural Networks.* ICML. [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v70/guo17a.html). Calibration and temperature-scaling reference.

## NVIDIA documentation

**[R21] NVIDIA.** *Video Search and Summarization, version 3.1.0: Introduction and architecture.* [Versioned documentation](https://docs.nvidia.com/vss/3.1.0/index.html).

**[R22] NVIDIA.** *VSS 3.1.0: Real-Time Embedding.* [Versioned documentation](https://docs.nvidia.com/vss/3.1.0/real-time-embedding.html). Checked reference for chunking, optional Kafka publication, and the documented video-embedding topic.

**[R23] NVIDIA.** *VSS 3.1.0: Cosmos-Embed1.* [Versioned model documentation](https://docs.nvidia.com/vss/3.1.0/models/cosmos-embed1.html). Model architecture reference; validate the actual deployed configuration and output shape.

**[R24] NVIDIA.** *VSS 3.1.0: Alert Verification Service.* [Versioned documentation](https://docs.nvidia.com/vss/3.1.0/alert-verification-service.html). Reference for candidate verification, VIOS clip retrieval, and verification outcomes.

**[R25] NVIDIA.** *VSS 3.1.0: Behavior Analytics.* [Versioned documentation](https://docs.nvidia.com/vss/3.1.0/behavior-analytics.html). Reference for violation state, persistence, incident promotion, and expiration concepts.

**[R26] NVIDIA.** *VSS 3.1.0: Video I/O and Storage, VIOS.* [Versioned documentation](https://docs.nvidia.com/vss/3.1.0/vss-vios.html).

**[R27] NVIDIA.** *VSS 3.1.0: JSON Schema.* [Versioned schema documentation](https://docs.nvidia.com/vss/3.1.0/JSON-Schema.html).

**[R28] NVIDIA.** *VSS 3.1.0: Protobuf Schema.* [Versioned schema documentation](https://docs.nvidia.com/vss/3.1.0/Protobuf-Schema.html).

**[R29] NVIDIA.** *Triton Inference Server: Ensemble Models.* [Official documentation](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/ensemble_models.html). Unpinned documentation URL, checked for this edition; match the serving documentation to the deployed release.

**[R30] NVIDIA.** *Triton Inference Server: Batcher.* [Official documentation](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html). Reference for dynamic and sequence batching.

**[R31] NVIDIA.** *VSS 3.1.0: Known Limitations.* [Versioned documentation](https://docs.nvidia.com/vss/3.1.0/Known-Limitations.html).

**[R32] NVIDIA.** *VSS: Secure Deployment.* [Official secure-deployment guidance](https://docs.nvidia.com/vss/latest/secure-deployment.html). This is a current-documentation URL rather than a version-pinned snapshot; its contents may change after the edition's access date.

## Laboratory operations

**[R33] PyTorch.** Official documentation for [Conv1d, version 2.10](https://docs.pytorch.org/docs/2.10/generated/torch.nn.Conv1d.html), [cross-entropy](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html), and [explicit padding](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.pad.html). The latter two are rolling documentation URLs. The tested laboratory runtime is recorded independently as PyTorch 2.10.0+cpu.
