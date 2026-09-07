---
license: other
license_name: nvidia-open-model-license
license_link: >-
  https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license
library_name: cosmos
tags:
- nvidia
- cosmos
- conversational
extra_gated_prompt: >-
  # NVIDIA Open Model License Agreement

  Version Release Date: September 23, 2025

  This NVIDIA Open Model License Agreement (the “Agreement”) is a legal
  agreement between the Legal Entity You represent, or if no  entity is
  identified, You and NVIDIA Corporation and its Affiliates (“NVIDIA”) and
  governs Your use of the Models that NVIDIA provides  to You under this
  Agreement. NVIDIA and You are each a “party” and collectively the “parties.”  

  NVIDIA models released under this Agreement are intended to be used
  permissively and enable the further development of AI  technologies. Subject
  to the terms of this Agreement, NVIDIA confirms that: 

  - Models are commercially usable.  - You are free to create and distribute
  Derivative Models.  - NVIDIA does not claim ownership to any outputs generated
  using the Models or Model Derivatives. 

  By using, reproducing, modifying, distributing, performing or displaying any
  portion or element of the Model or Derivative Model, or  otherwise accepting
  the terms of this Agreement, you agree to be bound by this Agreement.  

  ## 1. Definitions

  1.1. **Derivative Model** means all (a) modifications to the Model, (b) works
  based on the Model, and (c) any other derivative  works of the Model. An
  output is not a Derivative Model.  

  1.2. **Legal Entity** means the union of the acting entity and all other
  entities that control, are controlled by, or are under common  control with
  that entity. For the purposes of this definition, “control” means (a) the
  power, direct or indirect, to cause the  direction or management of such
  entity, whether by contract or otherwise, or (b) ownership of fifty percent
  (50%) or more  of the outstanding shares, or (c) beneficial ownership of such
  entity. 

  1.3. **Model** means the machine learning model, software, checkpoints, learnt
  weights, algorithms, parameters, configuration  files and documentation shared
  under this Agreement. 

  1.4. **NVIDIA Cosmos Model** means a multimodal Model shared under this
  Agreement.  

  1.5. **Special-Purpose Model** means a Model that is only competent in a
  narrow set of purpose-specific tasks and should not be  used for unintended or
  general-purpose applications. 

  1.6. **You** or **Your** means an individual or Legal Entity exercising
  permissions granted by this Agreement. 

  ## 2. Conditions for Use, License Grant, AI Ethics and IP Ownership

  ### 2.1. Conditions for Use - The Model and any Derivative Model are subject
  to additional terms as described in Section 2 and Section 3 of this
  Agreement.   - If You institute copyright or patent litigation against any
  entity alleging that the Model or a Derivative Model constitutes infringement,
  then any licenses granted will terminate as of the date such litigation is
  filed.   - If You bypass or disable any technical limitation, safety
  guardrail, encryption, DRM, or authentication mechanism contained in the Model
  without a substantially similar Guardrail, your rights will terminate.   -
  NVIDIA may designate a Model as a Special-Purpose Model.   - NVIDIA may update
  this Agreement to comply with legal and regulatory requirements.  

  ### 2.2. License Grant NVIDIA grants You a perpetual, worldwide,
  non-exclusive, no-charge, royalty-free, revocable license to publicly perform,
  publicly display, reproduce, use, create derivative works of, make, have made,
  sell, offer for sale, distribute, and import the Model.  

  ### 2.3. AI Ethics Use of the Models must be consistent with NVIDIA’s
  [Trustworthy AI
  terms](https://www.nvidia.com/en-us/agreements/trustworthy-ai/terms/).  

  ### 2.4. IP Ownership - NVIDIA owns the Model and any Model Derivatives it
  creates.   - You own your Model Derivatives.   - NVIDIA claims no ownership
  rights in outputs.   - Except as expressly granted, NVIDIA reserves all
  rights.  

  ## 3. Redistribution

  You may reproduce and distribute copies of the Model or Derivative Models in
  any medium, with or without modifications, provided that:  

  - **3.1.** You must provide recipients with a copy of this Agreement and
  include this attribution in a “Notice” text file:  
    *“Licensed by NVIDIA Corporation under the NVIDIA Open Model License”*  

  - **3.2.** If distributing or making available a NVIDIA Cosmos Model, or
  products/services derived from it, you must include:  
    *“Built on NVIDIA Cosmos”*  

  - **3.3.** You may add your own copyright statements and license terms for
  your modifications, provided use still complies with this Agreement.  

  ## 4. Separate Components The Models may include components licensed under
  separate legal notices (e.g., Open Source Software Licenses). These terms
  apply, except where overridden by this Agreement unless required by
  third-party license terms.  

  ## 5. Trademarks No permission is granted to use NVIDIA’s trade names,
  trademarks, or product names, except for reasonable descriptive use.  

  ## 6. Disclaimer of Warranty The Model is provided **“AS IS”**, without
  warranties of any kind, including title, non-infringement, merchantability, or
  fitness for purpose. You assume risks associated with its use.  

  ## 7. Limitation of Liability NVIDIA is not liable for damages (direct,
  indirect, incidental, or consequential) arising from use of the Model, unless
  required by law.  

  ## 8. Indemnity You will indemnify and hold NVIDIA harmless against claims
  from third parties arising from your use or distribution of the Model,
  derivatives, or outputs.  

  ## 9. Feedback NVIDIA may use any feedback you provide without restriction or
  compensation.  

  ## 10. Governing Law This Agreement is governed by U.S. and Delaware law.
  Courts in Santa Clara County, California, have exclusive jurisdiction, except
  for urgent injunctive relief.  

  ## 11. Trade and Compliance You must comply with all export, import, trade,
  and sanctions laws, including U.S. Export Administration Regulations and OFAC
  rules.
extra_gated_fields:
  By clicking Submit below, I accept the terms of the NVIDIA Open Model License Agreement and acknowledge that I am an adult of legal age of majority in the country in which the Cosmos Models will be used and have authority to accept this Agreement: checkbox
extra_gated_description: >-
  The information you provide will be collected, stored, processed and shared in
  accordance with the [NVIDIA Privacy
  Policy](https://www.nvidia.com/en-us/about-nvidia/privacy-policy/).
extra_gated_button_content: Submit
base_model:
- Qwen/Qwen3-VL-8B-Instruct
pipeline_tag: image-text-to-text
---

# **Cosmos-Reason2: Physical AI Common Sense and Embodied Reasoning Models**

[**Cosmos**](https://huggingface.co/collections/nvidia/cosmos-reason2) | [**Code**](https://github.com/nvidia-cosmos/cosmos-reason2)

# Model Overview

## Description:

NVIDIA Cosmos Reason 2 is an open, customizable, 8B-parameter reasoning vision language model (VLM) for physical AI and robotics that enables robots and vision AI agents to reason like humans, using prior knowledge, physics understanding and common sense to understand and act in the real world. This model understands space, time, and fundamental physics, and can serve as a planning model to reason what steps an embodied agent might take next.

New features with Cosmos Reason 2:

* Enhanced physical AI reasoning with improved spatio-temporal understanding and timestamp precision.
* Supports object detection with 2D/3D point localization and bounding box coordinates with reasoning explanations and labels.
* Improved long-context understanding up to 256K input tokens.

Use cases:

* Video analytics AI agents — Extract valuable insights and perform root-cause analysis on massive volumes of video data. These agents can be used to analyze and understand recorded or live video streams across city and industrial operations. Jumpstart your development of video analytics AI agents by using the [NVIDIA Blueprint for video search and summarization (VSS)](https://build.nvidia.com/nvidia/video-search-and-summarization) with Cosmos Reason as the VLM.
* Data curation and annotation — Enable developers to automate high-quality curation and annotation of massive, diverse training datasets. Experience [NVIDIA Cosmos Curator](https://github.com/nvidia-cosmos/cosmos-curate), powered by Cosmos Reason, a framework that enables developers to quickly filter, annotate, and deduplicate large amounts of sensor data necessary for physical AI development.
* Robot planning and reasoning — Act as the brain for deliberate, methodical decision-making in a robot vision language action (VLA) model. Now robots such as humanoids and autonomous vehicles (AV) can interpret environments and complex commands, break them down into tasks and execute them using common sense, even in unfamiliar environments. Explore the [NVIDIA Isaac GR00T-Dreams blueprint](https://github.com/nvidia/gr00t-dreams), which generates vast amounts of synthetic trajectory data using NVIDIA Cosmos world foundation models.

Explore the [Cosmos Cookbook](https://nvidia-cosmos.github.io/cosmos-cookbook/index.html), a technical guide that delivers end-to-end workflows, implementation recipes, and detailed examples for building, fine-tuning, and deploying Cosmos Reason in production-ready environments.

The model is ready for commercial use.

**Model Developer**: NVIDIA

## Model Versions

The Cosmos-Reason2 includes the following model:

- [Cosmos-Reason2-2B](https://huggingface.co/nvidia/Cosmos-Reason2-2B): Given a text prompt and an input video, think and generate the answer with respect to the input text prompt and video.
- [Cosmos-Reason2-8B](https://huggingface.co/nvidia/Cosmos-Reason2-8B): Given a text prompt and an input video, think and generate the answer with respect to the input text prompt and video.
- [Cosmos-Reason2-32B](https://huggingface.co/nvidia/Cosmos-Reason2-32B): Given a text prompt and an input video, think and generate the answer with respect to the input text prompt and video.

## Model Quality Performance
[04/28/2026] For comparative evaluation, we present benchmark scores using the [Physical AI Bench Leaderboard](https://huggingface.co/spaces/shi-labs/physical-ai-bench-leaderboard).

![PAI Bench Leaderboard](PAI_Bench_Leaderboard.png)

We also evaluated Cosmos-Reason2 against Qwen3-VL across the following domains and categories: General, Robotics, Self-Driving, and Smart Spaces.

| Category | Benchmark | Cosmos-Reason2-32B | Qwen3-VL-32B-Instruct | Cosmos-Reason2-8B | Qwen3-VL-8B-Instruct | Cosmos-Reason2-2B | Qwen3-VL-2B-Instruct |
|----------|-----------|:-------------------:|:----------------------:|:-------------------:|:----------------------:|:-------------------:|:----------------------:|
| General  | Overall   | **75.85** | 73.07 | **73.73** | 71.98 | **62.21** | 59.60 |
|          | [BlinkDepth](https://huggingface.co/datasets/BLINK-Benchmark/BLINK) | **84.68** | 82.26 | **87.90** | 87.10 | **82.26** | 74.19 |
|          | [BlinkSpatial](https://huggingface.co/datasets/BLINK-Benchmark/BLINK) | **86.71** | **86.71** | 84.62 | **87.41** | 75.52 | **77.62** |
|          | [CVBench](https://huggingface.co/datasets/nyu-visionx/CV-Bench) | **88.01** | 86.74 | **85.60** | 85.17 | **78.74** | 78.67 |
|          | [VideoPhy2](https://arxiv.org/pdf/2503.06800) | **43.98** | 36.57 | **36.80** | 28.24 | **12.33** | 7.92 |
| Robotics | Overall   | **60.60** | 55.06 | **56.90** | 53.08 | **45.52** | 42.07 |
|          | [ERQA](https://github.com/embodiedreasoning/ERQA) | 45.25 | **46.50** | **44.00** | **44.00** | **37.75** | **37.75** |
|          | [CR Common](https://huggingface.co/spaces/shi-labs/physical-ai-bench-leaderboard) | **65.89** | 63.41 | **64.24** | 58.44 | **54.30** | 49.67 |
|          | [CR Embodied](https://huggingface.co/spaces/shi-labs/physical-ai-bench-leaderboard) | **75.25** | 59.34 | **69.34** | 56.89 | **58.03** | 48.85 |
|          | [Where2Place](https://arxiv.org/pdf/2406.10721) | **56.00** | 51.00 | 50.00 | **53.00** | **32.00** | **32.00** |
| Self-Driving | Overall | **70.15** | 48.08 | **67.85** | 46.38 | **57.37** | 42.73 |
|          | [AV Collision](https://arxiv.org/pdf/2603.18178) | **72.06** | 37.67 | **74.00** | 34.00 | **74.33** | 36.33 |
|          | [AV Stop](https://arxiv.org/pdf/2603.18178) | **69.39** | 38.78 | **57.14** | 36.73 | **38.78** | 32.65 |
|          | [LingoQA](https://huggingface.co/papers/2312.14115) | **69.00** | 67.80 | **72.40** | 68.40 | 59.00 | **59.20** |
| Smart Spaces | Overall | **77.79** | 47.55 | **69.96** | 42.66 | **64.14** | 36.63 |
|          | [Warehouse AI](https://huggingface.co/datasets/nvidia/PhysicalAI-Spatial-Intelligence-Warehouse) | **77.79** | 47.55 | **69.96** | 42.66 | **64.14** | 36.63 |

![PAI Bench Leaderboard](CR2%20Performance%20by%20Category.png)

### License:

This model is released under the  [NVIDIA Open Model License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license). Additional Information: [Apache License 2.0](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md).

For a custom license, please contact [cosmos-license@nvidia.com](mailto:cosmos-license@nvidia.com).

Under the NVIDIA Open Model License, NVIDIA confirms:

* Models are commercially usable.
* You are free to create and distribute Derivative Models.
* NVIDIA does not claim ownership to any outputs generated using the Models or Derivative Models.

**Important Note**: If You bypass, disable, reduce the efficacy of, or circumvent any technical limitation, safety guardrail or associated safety guardrail hyperparameter, encryption, security, digital rights management, or authentication mechanism (collectively “Guardrail”) contained in the Model without a substantially similar Guardrail appropriate for your use case, your rights under this Agreement [NVIDIA Open Model License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license) will automatically terminate.

### Deployment Geography:

Global

### Use Case:

Physical AI: Space, time, fundamental physics understanding and embodied reasoning, encompassing robotics, and autonomous vehicles (AV).

### Release Date:

* Github: [12/19/2025](https://github.com/nvidia-cosmos/cosmos-reason2)
* Huggingface:
  * [03/10/2026](https://huggingface.co/nvidia/Cosmos-Reason2-8B/commit/07642cfd7b202fbaec08276336f3c0adfc3d9ef). Improved benchmark performance and reduced hallucinations.
  * [12/19/2025](https://huggingface.co/nvidia/Cosmos-Reason2-8B/commit/7892adeffd094f7954c18f7e471868b8475409fd). Initial release.

## Model Architecture:

Architecture Type: A Multi-modal LLM consists of a Vision Transformer (ViT) for vision encoder and a Dense Transformer model for LLM.
Network Architecture: Qwen3-VL-8B-Instruct.

Cosmos-Reason2-8B is post-trained based on [Qwen3-VL-8B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct) and follows the same model architecture.

**Number of model parameters:**

Cosmos-Reason2-8B: 8,767,123,696

## Input

  **Input Type(s)**: Text+Video/Image

   **Input Format(s)**:

* Text: String
* Video: mp4
* Image: jpg

  **Input Parameters**:
* Text: One-dimensional (1D)
* Video: Three-dimensional (3D)
* Image: Two-dimensional (2D)

  **Other Properties Related to Input**:
* Use `FPS=4` for input video to match the training setup.
* Append `Answer the question in the following format: <think>\nyour reasoning\n</think>\n\n<answer>\nyour answer\n</answer>.` in the system prompt to encourage long chain-of-thought reasoning response.

## Output

 **Output Type(s)**: Text

 **Output Format**: String

 **Output Parameters**: Text: One-dimensional (1D)

 **Other Properties Related to Output**:

* Recommend using 4096 or more output max tokens to avoid truncation of long chain-of-thought response.
* Our AI model recognizes timestamps added at the bottom of each frame for accurate temporal localization.
* Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA’s hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions. `<br>`

## Software Integration

**Runtime Engine(s):**

* [Transformers](https://github.com/huggingface/transformers)

**Supported Hardware Microarchitecture Compatibility:**

* NVIDIA Blackwell
* NVIDIA Hopper

**Note**: We have only tested doing inference with BF16 precision.

**Operating System(s):**

* Linux (We have not tested on other operating systems.)

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment.

# Usage

See [Cosmos-Reason2](https://github.com/nvidia-cosmos/cosmos-reason2) for details.

* Post Training: [Cosmos-Reason2](https://github.com/nvidia-cosmos/cosmos-reason2) provides examples of supervised fine-tuning and reinforcement learning on embodied reasoning datasets.

## Training and Evaluation Sections:

Cosmos-Reason2-8B model was trained and evaluated on the same datasets used for [Cosmos-Reason1-7B](https://huggingface.co/nvidia/Cosmos-Reason1-7B#training-datasets), in addition to the following newly added datasets.

## Training Datasets:

**Data Collection Method**:

[12/19/2025]
* EgoExo4D:  Hybrid:  Automatic/Sensors
* PerceptionTest: Hybrid:  Automatic/Sensors
* Language Table: Hybrid:  Automatic/Sensors
* IntPhys: Hybrid:  Automatic/Sensors
* InfLevel: Hybrid:  Automatic/Sensors
* CLEVRER: Hybrid:  Automatic/Sensors

[03/10/2026]
* VideoPhy2: Hybrid:  Automatic/Sensors
* NVIDIA Physical AI AV: Hybrid:  Automatic/Sensors
* NVIDIA Physical AI Metropolis: Hybrid:  Automatic/Sensors
* Hyperism: Hybrid:  Automatic/Sensors
* EgoExOR: Hybrid:  Automatic/Sensors

**Labeling Method**:

[12/19/2025]
* EgoExo4D:  Hybrid:  Automatic/Sensors
* PerceptionTest: Hybrid:  Automatic/Sensors
* Language Table: Hybrid:  Automatic/Sensors
* IntPhys: Hybrid:  Automatic/Sensors
* InfLevel: Hybrid:  Automatic/Sensors
* CLEVRER: Hybrid:  Automatic/Sensors

[03/10/2026]
* VideoPhy2: Hybrid:  Automatic/Sensors
* NVIDIA Physical AI AV: Hybrid:  Automatic/Sensors
* NVIDIA Physical AI Metropolis: Hybrid:  Automatic/Sensors
* Hyperism: Hybrid:  Automatic/Sensors
* EgoExOR: Hybrid:  Automatic/Sensors

The combined datasets span multimodal video, sensor signals, and structured physical-reasoning tasks, providing broad coverage for training world-model reasoning capabilities.

# Evaluation Datasets:

**Data Collection Method**:

[12/19/2025]
* EgoExo4D:  Hybrid:  Automatic/Sensors
* PerceptionTest: Hybrid:  Automatic/Sensors
* Language Table: Hybrid:  Automatic/Sensors
* IntPhys: Hybrid:  Automatic/Sensors
* InfLevel: Hybrid:  Automatic/Sensors
* CLEVRER: Hybrid:  Automatic/Sensors

[03/10/2026]
* VideoPhy2: Hybrid:  Automatic/Sensors
* NVIDIA Physical AI AV: Hybrid:  Automatic/Sensors
* NVIDIA Physical AI Metropolis: Hybrid:  Automatic/Sensors
* Hyperism: Hybrid:  Automatic/Sensors
* EgoExOR: Hybrid:  Automatic/Sensors

**Labeling Method**:

[12/19/2025]
* EgoExo4D:  Hybrid:  Automatic/Sensors
* PerceptionTest: Hybrid:  Automatic/Sensors
* Language Table: Hybrid:  Automatic/Sensors
* IntPhys: Hybrid:  Automatic/Sensors
* InfLevel: Hybrid:  Automatic/Sensors
* CLEVRER: Hybrid:  Automatic/Sensors

[03/10/2026]
* VideoPhy2: Hybrid:  Automatic/Sensors
* NVIDIA Physical AI AV: Hybrid:  Automatic/Sensors
* NVIDIA Physical AI Metropolis: Hybrid:  Automatic/Sensors
* Hyperism: Hybrid:  Automatic/Sensors
* EgoExOR: Hybrid:  Automatic/Sensors

The combined datasets span multimodal video, sensor signals, and structured physical-reasoning tasks, providing broad coverage for training world-model reasoning capabilities.

## Dataset Format

Modality: Video (mp4) and Text

## Inference:

**Test Hardware:** H100, A100

> [!NOTE]
> We suggest using `fps=4` for the input video and `max_tokens=4096` to avoid truncated response.

```python
import transformers
import torch

model_name = "nvidia/Cosmos-Reason2-2B"
model = transformers.Qwen3VLForConditionalGeneration.from_pretrained(
    model_name, dtype=torch.float16, device_map="auto", attn_implementation="sdpa"
)
processor: transformers.Qwen3VLProcessor = (
    transformers.AutoProcessor.from_pretrained(model_name)
)

video_messages = [
    {
        "role": "system",
        "content": [{"type": "text", "text": "You are a helpful assistant."}],
    },
    {"role": "user", "content": [
            {
                "type": "video", 
                "video": "file:///path/to/your/video.mp4",
                "fps": 4,
            },
            {"type": "text", "text": (
                    "Is it safe to turn right? Answer the question using the following format:\n\n<think>\nYour reasoning.\n</think>\n\nWrite your final answer immediately after the </think> tag."
                )
            },
        ]
    },
]

# Process inputs
inputs = processor.apply_chat_template(
    video_messages,
    tokenize=True,
    add_generation_prompt=True,
    return_dict=True,
    return_tensors="pt",
    fps=4,
)
inputs = inputs.to(model.device)

# Run inference
generated_ids = model.generate(**inputs, max_new_tokens=4096)
generated_ids_trimmed = [
    out_ids[len(in_ids) :]
    for in_ids, out_ids in zip(inputs.input_ids, generated_ids, strict=False)
]
output_text = processor.batch_decode(
    generated_ids_trimmed,
    skip_special_tokens=True,
    clean_up_tokenization_spaces=False,
)

```

#### System Requirements and Performance

This model requires a minimum of 32 GB of GPU memory. Inference latency for a single generation across different NVIDIA GPU platforms will be published shortly.

## Ethical Considerations

NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

Users are responsible for model inputs and outputs. Users are responsible for ensuring safe integration of this model, including implementing guardrails as well as other safety mechanisms, prior to deployment.

For more detailed information on ethical considerations for this model, please see the subcards of Explainability, Bias, Safety & Security, and Privacy below.

Please report security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

### Plus Plus (++) Promise

We value you, the datasets, the diversity they represent, and what we have been entrusted with. This model and its associated data have been:

* Verified to comply with current applicable disclosure laws, regulations, and industry standards.
* Verified to comply with applicable privacy labeling requirements.
* Annotated to describe the collector/source (NVIDIA or a third-party).
* Characterized for technical limitations.
* Reviewed to ensure proper disclosure is accessible to, maintained for, and in compliance with NVIDIA data subjects and their requests.
* Reviewed before release.
* Tagged for known restrictions and potential safety implications.

### Bias

| Field                                                                                                                                                           | Response                                                                                                                                                                                                                                                                                                                                                     |
| :-------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Participation considerations from adversely impacted groups [protected classes](https://www.senate.ca.gov/content/protected-classes) in model design and testing: | None                                                                                                                                                                                                                                                                                                                                                         |
| Measures taken to mitigate against unwanted bias:                                                                                                               | The training video sources contain multiple physical embodiments and environments including human, car, single arm robot, bimanual robot in indoor and outdoor environments. By training on numerous and various physical interactions and curated datasets, we strive to provide a model that mitigates biases towards certain embodiments or environments. |

### Explainability

| Field                                                     | Response                                                                                                                                                                                                                                                                                                                                                                                |
| :-------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Intended Application & Domain:                            | Physical AI Reasoning                                                                                                                                                                                                                                                                                                                                                                   |
| Model Type:                                               | Transformer                                                                                                                                                                                                                                                                                                                                                                             |
| Intended Users:                                           | Physical AI developers                                                                                                                                                                                                                                                                                                                                                                  |
| Output:                                                   | Text                                                                                                                                                                                                                                                                                                                                                                                    |
| Describe how the model works:                             | Given a video/image and a text prompt, the model first converts the video/image into tokens using a vision encoder and a special translator called a projector. These video tokens are combined with the text prompt and fed into the core model, which uses a mix of LLM modules and techniques. This enables the model to think step-by-step and provide detailed, logical responses. |
| Technical Limitations:                                    | The model may not follow the video or text input accurately in challenging cases, where the input video shows complex scene composition and temporal dynamics. Examples of challenging scenes include: fast camera movements, overlapping human-object interactions, low lighting with high motion blur, and multiple people performing different actions simultaneously.               |
| Verified to have met prescribed NVIDIA quality standards: | Yes                                                                                                                                                                                                                                                                                                                                                                                     |
| Performance Metrics:                                      | Quantitative and Qualitative Evaluation. Cosmos-Reason2 proposes the embodied reasoning benchmark and physical common sense benchmark to evaluate accuracy with visual question answering.                                                                                                                                                                                             |
| Potential Known Risks:                                    | The model's output can generate all forms of texts, including what may be considered toxic, offensive, or indecent.                                                                                                                                                                                                                                                                     |
| Licensing:                                                | [NVIDIA Open Model License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license). Additional Information: [Apache License 2.0](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md).                                                                                                                                   |

### Privacy

| Field                                                               | Response                                                                       |
| :------------------------------------------------------------------ | :----------------------------------------------------------------------------- |
| Generatable or reverse engineerable personal data?                  | No                                                                             |
| Personal data used to create this model?                            | None Known                                                                     |
| Was consent obtained for any personal data used?                    | None Known                                                                     |
| How often is dataset reviewed?                                      | Before Release                                                                 |
| Is there provenance for all datasets used in training?              | Yes                                                                            |
| Does data labeling (annotation, metadata) comply with privacy laws? | Yes                                                                            |
| Applicable Privacy Policy                                           | [NVIDIA Privacy Policy](https://www.nvidia.com/en-us/about-nvidia/privacy-policy) |

### Safety

| Field                                           | Response                                                                                                                                                                                                                                                                                                                             |
| :---------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model Application(s):                           | Physical AI common sense understanding and embodied reasoning                                                                                                                                                                                                                                                                        |
| Describe the life critical impact (if present). | Because this model is designed for robot planning and serves as a Vision-Language-Action (VLA) model, its outputs directly influence physical actuation. Planning errors or misinterpretations of the environment carry inherent life-safety risks, including physical collisions, unsafe object manipulation, or unintended interactions with humans and property.|
| Use Case Restrictions:                          | [NVIDIA Open Model License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license). Additional Information: [Apache License 2.0](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md).                                                                                |
| Model and dataset restrictions:                 | The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development.  Restrictions enforce dataset access during training, and dataset license constraints adhered to. Model checkpoints are made available on Hugging Face, and may become available on cloud providers' model catalog. |