# Phi-3-mini-128k-instruct

## How to use from the Transformers library

### Use a pipeline as a high-level helper

```python
from transformers import pipeline

pipe = pipeline("text-generation", model="microsoft/Phi-3-mini-128k-instruct", trust_remote_code=True)
messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe(messages)
```

### Load model directly

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-128k-instruct", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3-mini-128k-instruct", trust_remote_code=True)
```

### Clone this model repository

```bash
# Make sure git-lfs is installed (https://git-lfs.com)
git lfs install

git clone https://huggingface.co/microsoft/Phi-3-mini-128k-instruct

# If you want to clone without large files - just their pointers
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/microsoft/Phi-3-mini-128k-instruct
```

## Model Summary

The Phi-3-Mini-128K-Instruct is a 3.8 billion-parameter, lightweight, state-of-the-art open model trained using the Phi-3 datasets. This dataset includes both synthetic data and filtered publicly available website data, with an emphasis on high-quality and reasoning-dense properties. The model belongs to the Phi-3 family with the Mini version in two variants 4K and 128K which is the context length (in tokens) that it can support.

After initial training, the model underwent a post-training process that involved supervised fine-tuning and direct preference optimization to enhance its ability to follow instructions and adhere to safety measures. When evaluated against benchmarks that test common sense, language understanding, mathematics, coding, long-term context, and logical reasoning, the Phi-3 Mini-128K-Instruct demonstrated robust and state-of-the-art performance among models with fewer than 13 billion parameters.

### Resources and Technical Documentation

- 🏡 [Phi-3 Portal](https://www.microsoft.com/en-us/research/project/phi-3/)
- 📰 [Phi-3 Microsoft Blog](https://blogs.microsoft.com/blog/2024/03/21/meet-phi-3-microsofts-most-advanced-small-language-model/)
- 📖 [Phi-3 Technical Report](https://arxiv.org/abs/2404.14219)
- 🛠️ [Phi-3 on Azure AI Studio](https://ai.azure.com/)
- 👩‍🍳 [Phi-3 Cookbook](https://github.com/microsoft/Phi-3)
- 🖥️ [Try It](https://huggingface.co/microsoft/Phi-3-mini-128k-instruct)

### Available Models

| Model | Short Context | Long Context |
|-------|--------------|-------------|
| Mini | [4K HF](https://huggingface.co/microsoft/phi-3-mini-4k-instruct) ; [ONNX](https://huggingface.co/microsoft/phi-3-mini-4k-instruct-onnx) ; [GGUF](https://huggingface.co/microsoft/phi-3-mini-4k-instruct-gguf) | [128K HF](https://huggingface.co/microsoft/phi-3-mini-128k-instruct) ; [ONNX](https://huggingface.co/microsoft/phi-3-mini-128k-instruct-onnx) |
| Small | [8K HF](https://huggingface.co/microsoft/phi-3-small-8k-instruct) ; [ONNX](https://huggingface.co/microsoft/phi-3-small-8k-instruct-onnx) | [128K HF](https://huggingface.co/microsoft/phi-3-small-128k-instruct) ; [ONNX](https://huggingface.co/microsoft/phi-3-small-128k-instruct-onnx) |
| Medium | [4K HF](https://huggingface.co/microsoft/phi-3-medium-4k-instruct) ; [ONNX](https://huggingface.co/microsoft/phi-3-medium-4k-instruct-onnx) | [128K HF](https://huggingface.co/microsoft/phi-3-medium-128k-instruct) ; [ONNX](https://huggingface.co/microsoft/phi-3-medium-128k-instruct-onnx) |
| Vision | - | [128K HF](https://huggingface.co/microsoft/Phi-3-vision-128k-instruct) ; [ONNX](https://huggingface.co/microsoft/Phi-3-vision-128k-instruct-onnx) |

## Intended Uses

### Primary use cases

The model is intended for commercial and research use in English. The model provides uses for applications which require:

- Memory/compute constrained environments
- Latency bound scenarios
- Strong reasoning (especially code, math and logic)

Our model is designed to accelerate research on language and multimodal models, for use as a building block for generative AI powered features.

### Use case considerations

Our models are not specifically designed or evaluated for all downstream purposes. Developers should consider common limitations of language models as they select use cases, and evaluate and mitigate for accuracy, safety, and fairness before using within a specific downstream use case, particularly for high risk scenarios. Developers should be aware of and adhere to applicable laws or regulations (including privacy, trade compliance laws, etc.) that are relevant to their use case.

Nothing contained in this Model Card should be interpreted as or deemed a restriction or modification to the license the model is released under.

## Release Notes

This is an update over the original instruction-tuned Phi-3-mini release based on valuable customer feedback. The model used additional post-training data leading to substantial gains on long-context understanding, instruction following, and structure output. We also improve multi-turn conversation quality, explicitly support `<|system|>` tag, and significantly improve reasoning capability. We believe most use cases will benefit from this release, but we encourage users to test in their particular AI applications. We appreciate the enthusiastic adoption of the Phi-3 model family, and continue to welcome all feedback from the community.

These tables below highlights improvements on instruction following, structure output, reasoning, and long-context understanding of the new release on our public and internal benchmark datasets.

### Instruction Following and Output Structure

| Benchmarks | Original | June 2024 Update |
|------------|----------|-----------------|
| Instruction Extra Hard | 5.7 | 5.9 |
| Instruction Hard | 5.0 | 5.2 |
| JSON Structure Output | 1.9 | 60.1 |
| XML Structure Output | 47.8 | 52.9 |
| GPQA | 25.9 | 29.7 |
| MMLU | 68.1 | 69.7 |
| Average | 25.7 | 37.3 |

### RULER: A Retrieval-based Benchmark for Long Context Understanding

| Model | 4K | 8K | 16K | 32K | 64K | 128K | Average |
|-------|-----|-----|------|------|------|-------|---------|
| Original | 86.7 | 78.1 | 75.6 | 70.3 | 58.9 | 43.3 | 68.8 |
| June 2024 Update | 92.4 | 91.1 | 90.8 | 87.9 | 79.8 | 65.6 | 84.6 |

### RepoQA: A Benchmark for Long Context Code Understanding

| Model | Python | C++ | Rust | Java | TypeScript | Average |
|-------|--------|-----|------|------|------------|---------|
| Original | 27 | 29 | 40 | 33 | 33 | 32.4 |
| June 2024 Update | 85 | 63 | 72 | 93 | 72 | 77 |

**Notes:** If users would like to check out the previous version, use the git commit id `bb5bf1e4001277a606e11debca0ef80323e5f824`. For the model conversion, e.g. GGUF and other formats, we invite the community to experiment with various approaches and share your valuable feedback. Let's innovate together!

## How to Use

Phi-3 Mini-128K-Instruct has been integrated in the development version (4.41.3) of transformers. Until the official version is released through pip, ensure that you are doing one of the following:

- When loading the model, ensure that `trust_remote_code=True` is passed as an argument of the `from_pretrained()` function.

- Update your local transformers to the development version: 
  ```bash
  pip uninstall -y transformers && pip install git+https://github.com/huggingface/transformers
  ```
  The previous command is an alternative to cloning and installing from the source.

- The current transformers version can be verified with: 
  ```bash
  pip list | grep transformers
  ```

### Required Packages

```
flash_attn==2.5.8
torch==2.3.1
accelerate==0.31.0
transformers==4.41.2
```

Phi-3 Mini-128K-Instruct is also available in [Azure AI Studio](https://ai.azure.com/)

## Tokenizer

Phi-3 Mini-128K-Instruct supports a vocabulary size of up to 32064 tokens. The tokenizer files already provide placeholder tokens that can be used for downstream fine-tuning, but they can also be extended up to the model's vocabulary size.

## Chat Format

Given the nature of the training data, the Phi-3 Mini-128K-Instruct model is best suited for prompts using the chat format as follows. You can provide the prompt as a question with a generic template as follow:

```
<|system|>
You are a helpful assistant.<|end|>
<|user|>
Question?<|end|>
<|assistant|>
```

### Example

```
<|system|>
You are a helpful assistant.<|end|>
<|user|>
How to explain Internet for a medieval knight?<|end|>
<|assistant|> 
```

Where the model generates the text after `<|assistant|>`. 

### Few-Shot Example

In case of few-shots prompt, the prompt can be formatted as the following:

```
<|system|>
You are a helpful travel assistant.<|end|>
<|user|>
I am going to Paris, what should I see?<|end|>
<|assistant|>
Paris, the capital of France, is known for its stunning architecture, art museums, historical landmarks, and romantic atmosphere. Here are some of the top attractions to see in Paris:

1. The Eiffel Tower: The iconic Eiffel Tower is one of the most recognizable landmarks in the world and offers breathtaking views of the city.
2. The Louvre Museum: The Louvre is one of the world's largest and most famous museums, housing an impressive collection of art and artifacts, including the Mona Lisa.
3. Notre-Dame Cathedral: This beautiful cathedral is one of the most famous landmarks in Paris and is known for its Gothic architecture and stunning stained glass windows.

These are just a few of the many attractions that Paris has to offer. With so much to see and do, it's no wonder that Paris is one of the most popular tourist destinations in the world.<|end|>
<|user|>
What is so great about #1?<|end|>
<|assistant|>
```

## Sample Inference Code

This code snippet shows how to get quickly started with running the model on a GPU:

```python
import torch 
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline 

torch.random.manual_seed(0) 
model = AutoModelForCausalLM.from_pretrained( 
    "microsoft/Phi-3-mini-128k-instruct",  
    device_map="cuda",  
    torch_dtype="auto",  
    trust_remote_code=True,  
) 

tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-128k-instruct") 

messages = [ 
    {"role": "system", "content": "You are a helpful AI assistant."}, 
    {"role": "user", "content": "Can you provide ways to eat combinations of bananas and dragonfruits?"}, 
    {"role": "assistant", "content": "Sure! Here are some ways to eat bananas and dragonfruits together: 1. Banana and dragonfruit smoothie: Blend bananas and dragonfruits together with some milk and honey. 2. Banana and dragonfruit salad: Mix sliced bananas and dragonfruits together with some lemon juice and honey."}, 
    {"role": "user", "content": "What about solving an 2x + 3 = 7 equation?"}, 
] 

pipe = pipeline( 
    "text-generation", 
    model=model, 
    tokenizer=tokenizer, 
) 

generation_args = { 
    "max_new_tokens": 500, 
    "return_full_text": False, 
    "temperature": 0.0, 
    "do_sample": False, 
} 

output = pipe(messages, **generation_args) 
print(output[0]['generated_text']) 
```

**Note:** If you want to use flash attention, call `AutoModelForCausalLM.from_pretrained()` with `attn_implementation="flash_attention_2"`

## Responsible AI Considerations

Like other language models, the Phi series models can potentially behave in ways that are unfair, unreliable, or offensive. Some of the limiting behaviors to be aware of include:

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

## Training

### Model

- **Architecture**: Phi-3 Mini-128K-Instruct has 3.8B parameters and is a dense decoder-only Transformer model. The model is fine-tuned with Supervised fine-tuning (SFT) and Direct Preference Optimization (DPO) to ensure alignment with human preferences and safety guidelines.
- **Inputs**: Text. It is best suited for prompts using chat format.
- **Context length**: 128K tokens
- **GPUs**: 512 H100-80G
- **Training time**: 10 days
- **Training data**: 4.9T tokens
- **Outputs**: Generated text in response to the input
- **Dates**: Our models were trained between May and June 2024
- **Status**: This is a static model trained on an offline dataset with cutoff date October 2023. Future versions of the tuned models may be released as we improve models.
- **Release dates**: June, 2024.

### Datasets

Our training data includes a wide variety of sources, totaling 4.9 trillion tokens, and is a combination of:

- Publicly available documents filtered rigorously for quality, selected high-quality educational data, and code;
- Newly created synthetic, "textbook-like" data for the purpose of teaching math, coding, common sense reasoning, general knowledge of the world (science, daily activities, theory of mind, etc.);
- High quality chat format supervised data covering various topics to reflect human preferences on different aspects such as instruct-following, truthfulness, honesty and helpfulness.

We are focusing on the quality of data that could potentially improve the reasoning ability for the model, and we filter the publicly available documents to contain the correct level of knowledge. As an example, the result of a game in premier league in a particular day might be good training data for frontier models, but we need to remove such information to leave more model capacity for reasoning for the small size models. More details about data can be found in the Phi-3 Technical Report.

### Fine-tuning

A basic example of multi-GPUs supervised fine-tuning (SFT) with TRL and Accelerate modules is provided [here](https://github.com/microsoft/Phi-3/blob/main/fine-tuning/sft.py).

## Benchmarks

We report the results under completion format for Phi-3-Mini-128K-Instruct on standard open-source benchmarks measuring the model's reasoning ability (both common sense reasoning and logical reasoning). We compare to Mistral-7b-v0.1, Mixtral-8x7b, Gemma 7B, Llama-3-8B-Instruct, and GPT-3.5.

All the reported numbers are produced with the exact same pipeline to ensure that the numbers are comparable. These numbers might differ from other published numbers due to slightly different choices in the evaluation.

As is now standard, we use few-shot prompts to evaluate the models, at temperature 0. The prompts and number of shots are part of a Microsoft internal tool to evaluate language models, and in particular we did no optimization to the pipeline for Phi-3. More specifically, we do not change prompts, pick different few-shot examples, change prompt format, or do any other form of optimization for the model.

The number of k–shot examples is listed per-benchmark.

| Category | Benchmark | Phi-3-Mini-128K-Ins | Gemma-7B | Mistral-7B | Mixtral-8x7B | Llama-3-8B-Ins | GPT3.5-Turbo-1106 |
|----------|-----------|-------------------|----------|------------|--------------|---------------|-------------------|
| Popular aggregated benchmark | AGI Eval 5-shot | 39.5 | 42.1 | 35.1 | 45.2 | 42 | 48.4 |
| | MMLU 5-shot | 69.7 | 63.6 | 61.7 | 70.5 | 66.5 | 71.4 |
| | BigBench Hard 3-shot | 72.1 | 59.6 | 57.3 | 69.7 | 51.5 | 68.3 |
| Language Understanding | ANLI 7-shot | 52.3 | 48.7 | 47.1 | 55.2 | 57.3 | 58.1 |
| | HellaSwag 5-shot | 70.5 | 49.8 | 58.5 | 70.4 | 71.1 | 78.8 |
| Reasoning | ARC Challenge 10-shot | 85.5 | 78.3 | 78.6 | 87.3 | 82.8 | 87.4 |
| | BoolQ 0-shot | 77.1 | 66 | 72.2 | 76.6 | 80.9 | 79.1 |
| | MedQA 2-shot | 56.4 | 49.6 | 50 | 62.2 | 60.5 | 63.4 |
| | OpenBookQA 10-shot | 78.8 | 78.6 | 79.8 | 85.8 | 82.6 | 86 |
| | PIQA 5-shot | 80.1 | 78.1 | 77.7 | 86 | 75.7 | 86.6 |
| | GPQA 0-shot | 29.7 | 2.9 | 15 | 6.9 | 32.4 | 29.9 |
| | Social IQA 5-shot | 74.7 | 65.5 | 74.6 | 75.9 | 73.9 | 68.3 |
| | TruthfulQA (MC2) 10-shot | 64.8 | 52.1 | 53 | 60.1 | 63.2 | 67.7 |
| | WinoGrande 5-shot | 71.0 | 55.6 | 54.2 | 62 | 65 | 68.8 |
| Factual Knowledge | TriviaQA 5-shot | 57.8 | 72.3 | 75.2 | 82.2 | 67.7 | 85.8 |
| Math | GSM8K CoTT 8-shot | 85.3 | 59.8 | 46.4 | 64.7 | 77.4 | 78.1 |
| Code Generation | HumanEval 0-shot | 60.4 | 34.1 | 28.0 | 37.8 | 60.4 | 62.2 |
| | MBPP 3-shot | 70.0 | 51.5 | 50.8 | 60.2 | 67.7 | 77.8 |
| **Average** | | **66.4** | **56.0** | **56.4** | **64.4** | **65.5** | **70.3** |

### Long Context

Phi-3 Mini-128K-Instruct supports 128K context length, therefore the model is capable of several long context tasks including long document/meeting summarization, long document QA.

| Benchmark | Phi-3 Mini-128K-Instruct | Mistral-7B | Mixtral 8x7B | LLaMA-3-8B-Instruct |
|-----------|--------------------------|------------|--------------|---------------------|
| GovReport | 25.3 | 4.9 | 20.3 | 10.3 |
| QMSum | 21.9 | 15.5 | 20.6 | 2.9 |
| Qasper | 41.6 | 23.5 | 26.6 | 8.1 |
| SQuALITY | 24.1 | 14.7 | 16.2 | 25 |
| SummScreenFD | 16.8 | 9.3 | 11.3 | 5.1 |
| **Average** | **25.9** | **13.6** | **19.0** | **10.3** |

We take a closer look at different categories across 100 public benchmark datasets at the table below:

| Category | Phi-3-Mini-128K-Instruct | Gemma-7B | Mistral-7B | Mixtral 8x7B | Llama-3-8B-Instruct | GPT-3.5-Turbo |
|----------|--------------------------|----------|------------|--------------|-----------------|----------------|
| Popular aggregated benchmark | 60.6 | 59.4 | 56.5 | 66.2 | 59.9 | 67.0 |
| Reasoning | 69.4 | 60.3 | 62.8 | 68.1 | 69.6 | 71.7 |
| Language understanding | 57.5 | 57.6 | 52.5 | 66.1 | 63.2 | 67.7 |
| Code generation | 61.0 | 45.6 | 42.9 | 52.7 | 56.4 | 70.4 |
| Math | 51.6 | 35.8 | 25.4 | 40.3 | 41.1 | 52.8 |
| Factual knowledge | 35.8 | 46.7 | 49.8 | 58.6 | 43.1 | 63.4 |
| Multilingual | 56.4 | 66.5 | 57.4 | 66.7 | 66.6 | 71.0 |
| Robustness | 61.1 | 38.4 | 40.6 | 51.0 | 64.5 | 69.3 |

Overall, the model with only 3.8B-param achieves a similar level of language understanding and reasoning ability as much larger models. However, it is still fundamentally limited by its size for certain tasks. The model simply does not have the capacity to store too much world knowledge, which can be seen for example with low performance on TriviaQA. However, we believe such weakness can be resolved by augmenting Phi-3-Mini with a search engine.

## Cross Platform Support

ONNX runtime now supports Phi-3 mini models across platforms and hardware.

Optimized phi-3 models are also published here in ONNX format, to run with ONNX Runtime on CPU and GPU across devices, including server platforms, Windows, Linux and Mac desktops, and mobile CPUs, with the precision best suited to each of these targets. DirectML GPU acceleration is supported for Windows desktops GPUs (AMD, Intel, and NVIDIA).

Along with DML, ONNX Runtime provides cross platform support for Phi3 mini across a range of devices CPU, GPU, and mobile.

Here are some of the optimized configurations we have added:

- ONNX models for int4 DML: Quantized to int4 via AWQ
- ONNX model for fp16 CUDA
- ONNX model for int4 CUDA: Quantized to int4 via RTN
- ONNX model for int4 CPU and Mobile: Quantized to int4 via RTN

### Software

- PyTorch
- Transformers
- Flash-Attention

### Hardware

Note that by default, the Phi-3 Mini-128K-Instruct model uses flash attention, which requires certain types of GPU hardware to run. We have tested on the following GPU types:

- NVIDIA A100
- NVIDIA A6000
- NVIDIA H100

If you want to run the model on:

- NVIDIA V100 or earlier generation GPUs: call `AutoModelForCausalLM.from_pretrained()` with `attn_implementation="eager"`
- Optimized inference on GPU, CPU, and Mobile: use the ONNX models 128K

## License

The model is licensed under the MIT license.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow Microsoft's Trademark & Brand Guidelines. Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.