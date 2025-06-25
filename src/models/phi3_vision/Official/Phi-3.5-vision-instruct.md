# Phi-3.5-vision-instruct

## How to use from the Transformers library

### Use a pipeline as a high-level helper

```python
from transformers import pipeline

pipe = pipeline("image-text-to-text", model="microsoft/Phi-3.5-vision-instruct", trust_remote_code=True)
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG"},
            {"type": "text", "text": "What animal is on the candy?"}
        ]
    },
]
pipe(text=messages)
```

### Load model directly

```python
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3.5-vision-instruct", trust_remote_code=True)
```

### Clone this model repository

```bash
# Make sure git-lfs is installed (https://git-lfs.com)
git lfs install

git clone https://huggingface.co/microsoft/Phi-3.5-vision-instruct

# If you want to clone without large files - just their pointers
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/microsoft/Phi-3.5-vision-instruct
```

## Model Summary

Phi-3.5-vision is a lightweight, state-of-the-art open multimodal model built upon datasets which include - synthetic data and filtered publicly available websites - with a focus on very high-quality, reasoning dense data both on text and vision. The model belongs to the Phi-3 model family, and the multimodal version comes with 128K context length (in tokens) it can support. The model underwent a rigorous enhancement process, incorporating both supervised fine-tuning and direct preference optimization to ensure precise instruction adherence and robust safety measures.

### Resources

- 🏡 [Phi-3 Portal](https://www.microsoft.com/en-us/research/project/phi-3/)
- 📰 [Phi-3 Microsoft Blog](https://blogs.microsoft.com/blog/2024/03/21/meet-phi-3-microsofts-most-advanced-small-language-model/)
- 📖 [Phi-3 Technical Report](https://arxiv.org/abs/2404.14219)
- 👩‍🍳 [Phi-3 Cookbook](https://github.com/microsoft/Phi-3)
- 🖥️ [Try It](https://huggingface.co/microsoft/Phi-3.5-vision-instruct)

**Phi-3.5 Family:** [mini-instruct](https://huggingface.co/microsoft/Phi-3.5-mini-instruct) ; [MoE-instruct](https://huggingface.co/microsoft/Phi-3.5-MoE-instruct) ; [vision-instruct](https://huggingface.co/microsoft/Phi-3.5-vision-instruct)

## Intended Uses

### Primary Use Cases

The model is intended for broad commercial and research use in English. The model provides uses for general purpose AI systems and applications with visual and text input capabilities which require:

- Memory/compute constrained environments
- Latency bound scenarios
- General image understanding
- Optical character recognition
- Chart and table understanding
- Multiple image comparison
- Multi-image or video clip summarization

Our model is designed to accelerate research on language and multimodal models, for use as a building block for generative AI powered features.

### Use Case Considerations

Our models are not specifically designed or evaluated for all downstream purposes. Developers should consider common limitations of language models as they select use cases, and evaluate and mitigate for accuracy, safety, and fairness before using within a specific downstream use case, particularly for high risk scenarios. Developers should be aware of and adhere to applicable laws or regulations (including privacy, trade compliance laws, etc.) that are relevant to their use case.

Nothing contained in this Model Card should be interpreted as or deemed a restriction or modification to the license the model is released under.

## Release Notes

In this release, the model enables multi-frame image understanding and reasoning which is based on valuable customer feedback. The hero example multi-frame capabilities include detailed image comparison, multi-image summarization/storytelling and video summarization, which have broad applications in Office scenarios. We also observed performance improvement on most single image benchmarks, e.g., boost MMMU performance from 40.2 to 43.0, MMBench performance from 80.5 to 81.9, document understanding benchmark TextVQA from 70.9 to 72.0. We believe most use cases will benefit from this release, but we encourage users to test the new model in their AI applications. We appreciate the enthusiastic adoption of the Phi-3 model family and continue to welcome all the feedback from the community.

Below are the comparison results on existing multi-image benchmarks. On average, our model outperforms competitor models on the same size and competitive with much bigger models on multi-frame capabilities and video summarization.

### BLINK: A benchmark with 14 visual tasks that humans can solve very quickly but are still hard for current multimodal LLMs

| Benchmark | Phi-3.5-vision-instruct | LlaVA-Interleave-Qwen-7B | InternVL-2-4B | InternVL-2-8B | Gemini-1.5-Flash | GPT-4o-mini | Claude-3.5-Sonnet | Gemini-1.5-Pro | GPT-4o |
|-----------|-------------------------|---------------------------|---------------|---------------|------------------|-------------|------------------|-----------------|--------|
| Art Style | 87.2 | 62.4 | 55.6 | 52.1 | 64.1 | 70.1 | 59.8 | 70.9 | 73.3 |
| Counting | 54.2 | 56.7 | 54.2 | 66.7 | 51.7 | 55.0 | 59.2 | 65.0 | 65.0 |
| Forensic Detection | 92.4 | 31.1 | 40.9 | 34.1 | 54.5 | 38.6 | 67.4 | 60.6 | 75.8 |
| Functional Correspondence | 29.2 | 34.6 | 24.6 | 24.6 | 33.1 | 26.9 | 33.8 | 31.5 | 43.8 |
| IQ Test | 25.3 | 26.7 | 26.0 | 30.7 | 25.3 | 29.3 | 26.0 | 34.0 | 19.3 |
| Jigsaw | 68.0 | 86.0 | 55.3 | 52.7 | 71.3 | 72.7 | 57.3 | 68.0 | 67.3 |
| Multi-View Reasoning | 54.1 | 44.4 | 48.9 | 42.9 | 48.9 | 48.1 | 55.6 | 49.6 | 46.6 |
| Object Localization | 49.2 | 54.9 | 53.3 | 54.1 | 44.3 | 57.4 | 62.3 | 65.6 | 68.0 |
| Relative Depth | 69.4 | 77.4 | 63.7 | 67.7 | 57.3 | 58.1 | 71.8 | 76.6 | 71.0 |
| Relative Reflectance | 37.3 | 34.3 | 32.8 | 38.8 | 32.8 | 27.6 | 36.6 | 38.8 | 40.3 |
| Semantic Correspondence | 36.7 | 31.7 | 31.7 | 22.3 | 32.4 | 31.7 | 45.3 | 48.9 | 54.0 |
| Spatial Relation | 65.7 | 75.5 | 78.3 | 78.3 | 55.9 | 81.1 | 60.1 | 79.0 | 84.6 |
| Visual Correspondence | 53.5 | 40.7 | 34.9 | 33.1 | 29.7 | 52.9 | 72.1 | 81.4 | 86.0 |
| Visual Similarity | 83.0 | 91.9 | 48.1 | 45.2 | 47.4 | 77.8 | 84.4 | 81.5 | 88.1 |
| **Overall** | **57.0** | **53.1** | **45.9** | **45.4** | **45.8** | **51.9** | **56.5** | **61.0** | **63.2** |

### Video-MME: Comprehensively assess the capabilities of MLLMs in processing video data, covering a wide range of visual domains, temporal durations, and data modalities

| Benchmark | Phi-3.5-vision-instruct | LlaVA-Interleave-Qwen-7B | InternVL-2-4B | InternVL-2-8B | Gemini-1.5-Flash | GPT-4o-mini | Claude-3.5-Sonnet | Gemini-1.5-Pro | GPT-4o |
|-----------|-------------------------|---------------------------|---------------|---------------|------------------|-------------|------------------|-----------------|--------|
| short (<2min) | 60.8 | 62.3 | 60.7 | 61.7 | 72.2 | 70.1 | 66.3 | 73.3 | 77.7 |
| medium (4-15min) | 47.7 | 47.1 | 46.4 | 49.6 | 62.7 | 59.6 | 54.7 | 61.2 | 68.0 |
| long (30-60min) | 43.8 | 41.2 | 42.6 | 46.6 | 52.1 | 53.9 | 46.6 | 53.2 | 59.6 |
| **Overall** | **50.8** | **50.2** | **49.9** | **52.6** | **62.3** | **61.2** | **55.9** | **62.6** | **68.4** |

## Usage

### Requirements

The current transformers version can be verified with: 
```bash
pip list | grep transformers
```

### Required Packages

```
flash_attn==2.5.8
numpy==1.24.4
Pillow==10.3.0
Requests==2.31.0
torch==2.3.0
torchvision==0.18.0
transformers==4.43.0
accelerate==0.30.0
```

Phi-3.5-vision-Instruct is also available in [Azure AI Studio](https://ai.azure.com/).

### Input Formats

Given the nature of the training data, the Phi-3.5-vision model is best suited for prompts using the chat format as follows:

**Single image:**

```
<|user|>\n<|image_1|>\n{prompt}<|end|>\n<|assistant|>\n
```

**Multi-turn conversations:**

```
<|user|>\n<|image_1|>\n{prompt_1}<|end|>\n<|assistant|>\n{response_1}<|end|>\n<|user|>\n{prompt_2}<|end|>\n<|assistant|>\n
```

For multi-image usage, add multiple image placeholders in the front of the prompts. `<|image_{}|>` index should start from 1. One example of prompt is shown as follows:

```
<|user|>\n<|image_1|>\n<|image_2|>\n<|image_3|>\n<|image_4|>\n{prompt}<|end|>\n<|assistant|>\n
```

### Loading the model locally

After obtaining the Phi-3.5-vision-instruct model checkpoints, users can use this sample code for inference.

```python
from PIL import Image 
import requests 
from transformers import AutoModelForCausalLM 
from transformers import AutoProcessor 

model_id = "microsoft/Phi-3.5-vision-instruct" 

# Note: set _attn_implementation='eager' if you don't have flash_attn installed
model = AutoModelForCausalLM.from_pretrained(
  model_id, 
  device_map="cuda", 
  trust_remote_code=True, 
  torch_dtype="auto", 
  _attn_implementation='flash_attention_2'    
)

# for best performance, use num_crops=4 for multi-frame, num_crops=16 for single-frame.
processor = AutoProcessor.from_pretrained(model_id, 
  trust_remote_code=True, 
  num_crops=4
) 

images = []
placeholder = ""

# Note: if OOM, you might consider reduce number of frames in this example.
for i in range(1,20):
    url = f"https://image.slidesharecdn.com/azureintroduction-191206101932/75/Introduction-to-Microsoft-Azure-Cloud-{i}-2048.jpg" 
    images.append(Image.open(requests.get(url, stream=True).raw))
    placeholder += f"<|image_{i}|>\n"

messages = [
    {"role": "user", "content": placeholder+"Summarize the deck of slides."},
]

prompt = processor.tokenizer.apply_chat_template(
  messages, 
  tokenize=False, 
  add_generation_prompt=True
)

inputs = processor(prompt, images, return_tensors="pt").to("cuda:0") 

generation_args = { 
    "max_new_tokens": 1000, 
    "temperature": 0.0, 
    "do_sample": False, 
} 

generate_ids = model.generate(**inputs, 
  eos_token_id=processor.tokenizer.eos_token_id, 
  **generation_args
)

# remove input tokens 
generate_ids = generate_ids[:, inputs['input_ids'].shape[1]:]
response = processor.batch_decode(generate_ids, 
  skip_special_tokens=True, 
  clean_up_tokenization_spaces=False)[0] 

print(response)
```

**Notes:**
- To achieve best performances we suggest to set `num_crops=4` for multi-frame and `num_crops=16` for single-frame.
- To turn off flash_attention users can set `_attn_implementation='eager'`

## Responsible AI Considerations

Like other models, the Phi family of models can potentially behave in ways that are unfair, unreliable, or offensive. Some of the limiting behaviors to be aware of include:

- **Quality of Service**: The Phi models are trained primarily on English text. Languages other than English will experience worse performance. English language varieties with less representation in the training data might experience worse performance than standard American English.

- **Representation of Harms & Perpetuation of Stereotypes**: These models can over- or under-represent groups of people, erase representation of some groups, or reinforce demeaning or negative stereotypes. Despite safety post-training, these limitations may still be present due to differing levels of representation of different groups or prevalence of examples of negative stereotypes in training data that reflect real-world patterns and societal biases.

- **Inappropriate or Offensive Content**: These models may produce other types of inappropriate or offensive content, which may make it inappropriate to deploy for sensitive contexts without additional mitigations that are specific to the use case.

- **Information Reliability**: Language models can generate nonsensical content or fabricate content that might sound reasonable but is inaccurate or outdated.

- **Limited Scope for Code**: Majority of Phi-3 training data is based in Python and use common packages such as "typing, math, random, collections, datetime, itertools". If the model generates Python scripts that utilize other packages or scripts in other languages, we strongly recommend users manually verify all API uses.

Developers should apply responsible AI best practices and are responsible for ensuring that a specific use case complies with relevant laws and regulations (e.g. privacy, trade, etc.). Important areas for consideration include:

- **Allocation**: Models may not be suitable for scenarios that could have consequential impact on legal status or the allocation of resources or life opportunities (ex: housing, employment, credit, etc.) without further assessments and additional debiasing techniques.

- **High-Risk Scenarios**: Developers should assess suitability of using models in high-risk scenarios where unfair, unreliable or offensive outputs might be extremely costly or lead to harm. This includes providing advice in sensitive or expert domains where accuracy and reliability are critical (ex: legal or health advice). Additional safeguards should be implemented at the application level according to the deployment context.

- **Misinformation**: Models may produce inaccurate information. Developers should follow transparency best practices and inform end-users they are interacting with an AI system. At the application level, developers can build feedback mechanisms and pipelines to ground responses in use-case specific, contextual information, a technique known as Retrieval Augmented Generation (RAG).

- **Generation of Harmful Content**: Developers should assess outputs for their context and use available safety classifiers or custom solutions appropriate for their use case.

- **Misuse**: Other forms of misuse such as fraud, spam, or malware production may be possible, and developers should ensure that their applications do not violate applicable laws and regulations.

- **Identification of individuals**: Models with vision capabilities may have the potential to uniquely identify individuals in images. Safety post-training steers the model to refuse such requests, but developers should consider and implement, as appropriate, additional mitigations or user consent flows as required in their respective jurisdiction, (e.g., building measures to blur faces in image inputs before processing).

## Training

### Models

- **Architecture**: Phi-3.5-vision has 4.2B parameters and contains image encoder, connector, projector, and Phi-3 Mini language model.
- **Inputs**: Text and Image. It's best suited for prompts using the chat format.
- **Context length**: 128K tokens
- **GPUs**: 256 A100-80G
- **Training time**: 6 days
- **Training data**: 500B tokens (vision tokens + text tokens)
- **Outputs**: Generated text in response to the input
- **Dates**: Trained between July and August 2024
- **Status**: This is a static model trained on an offline text dataset with cutoff date March 15, 2024. Future versions of the tuned models may be released as we improve models.
- **Release date**: August 2024

### Data Overview

Our training data includes a wide variety of sources, and is a combination of:

- Publicly available documents filtered rigorously for quality, selected high-quality educational data and code;
- Selected high-quality image-text interleave data;
- Newly created synthetic, "textbook-like" data for the purpose of teaching math, coding, common sense reasoning, general knowledge of the world (science, daily activities, theory of mind, etc.), newly created image data, e.g., chart/table/diagram/slides, newly created multi-image and video data, e.g., short video clips/pair of two similar images;
- High quality chat format supervised data covering various topics to reflect human preferences on different aspects such as instruct-following, truthfulness, honesty and helpfulness.

The data collection process involved sourcing information from publicly available documents, with a meticulous approach to filtering out undesirable documents and images. To safeguard privacy, we carefully filtered various image and text data sources to remove or scrub any potentially personal data from the training data. More details about data can be found in the Phi-3 Technical Report.

### How to finetune?

We recommend user to take a look at the [Phi-3 CookBook finetuning recipe for Vision](https://github.com/microsoft/Phi-3/blob/main/CookBook/Recipe-Guide-Phi-3-Vision-Finetuning.ipynb)

## Benchmarks

To understand the capabilities, we compare Phi-3.5-vision with a set of models over a variety of zero-shot benchmarks using our internal benchmark platform. At the high-level overview of the model quality on representative benchmarks:

| Category | Benchmark | Phi-3.5-vision-instruct | Intern-VL-2-4B | Intern-VL-2-8B | Gemini-1.5-Flash | GPT-4o-mini 2024-7-18 | Claude-3.5-Sonnet | Gemini-1.5-Pro | GPT-4o 2024-5-13 |
|----------|-----------|-------------------------|-----------------|-----------------|------------------|----------------------|------------------|-----------------|------------------|
| Popular aggregated benchmark | MMMU (val) | 43.0 | 44.22 | 46.33 | 49.33 | 52.1 | 52.67 | 54.11 | 61.78 |
| | MMBench (dev-en) | 81.9 | 83.4 | 87.0 | 85.7 | 83.8 | 82.3 | 87.9 | 88.4 |
| Visual scientific knowledge reasoning | ScienceQA (img-test) | 91.3 | 94.9 | 95.9 | 84.5 | 84.0 | 73.8 | 86.0 | 88.5 |
| Visual math reasoning | MathVista (testmini) | 43.9 | 53.7 | 51.1 | 55.3 | 38.8 | 54.0 | 57.4 | 54.4 |
| | InterGPS (test) | 36.3 | 45.6 | 53.2 | 39.4 | 39.9 | 45.6 | 58.2 | 46.9 |
| Chart reasoning | AI2D (test) | 78.1 | 77.3 | 81.4 | 78.4 | 75.2 | 68.9 | 75.6 | 82.8 |
| | ChartQA (test) | 81.8 | 78.8 | 80.4 | 57.6 | 54.5 | 73.2 | 68.2 | 64.0 |
| Document Intelligence | TextVQA (val) | 72.0 | 66.2 | 68.8 | 67.4 | 70.9 | 70.5 | 64.5 | 75.6 |
| Object visual presence verification | POPE (test) | 86.1 | 83.3 | 84.2 | 86.1 | 83.6 | 76.6 | 89.3 | 87.0 |

## Safety Evaluation and Red-Teaming

### Approach

The Phi-3 family of models has adopted a robust safety post-training approach. This approach leverages a variety of both open-source and in-house generated datasets. The overall technique employed to do the safety alignment is a combination of SFT (Supervised Fine-Tuning) and RLHF (Reinforcement Learning from Human Feedback) approaches by utilizing human-labeled and synthetic English-language datasets, including publicly available datasets focusing on helpfulness and harmlessness as well as various questions and answers targeted to multiple safety categories.

### Safety Evaluation

We leveraged various evaluation techniques including red teaming, adversarial conversation simulations, and safety evaluation benchmark datasets to evaluate Phi-3.5 models' propensity to produce undesirable outputs across multiple risk categories. Several approaches were used to compensate for the limitations of one approach alone. Please refer to the technical report for more details of our safety alignment.

## Software

- PyTorch
- Transformers
- Flash-Attention

## Hardware

Note that by default, the Phi-3.5-vision-instruct model uses flash attention, which requires certain types of GPU hardware to run. We have tested on the following GPU types:

- NVIDIA A100
- NVIDIA A6000
- NVIDIA H100

## License

The model is licensed under the MIT license.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow Microsoft's Trademark & Brand Guidelines. Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.