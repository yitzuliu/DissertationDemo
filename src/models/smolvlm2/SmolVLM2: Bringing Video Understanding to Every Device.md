# SmolVLM2: Bringing Video Understanding to Every Device

**Authors:** Orr Zohar, Miquel Farré, Andres Marafioti, Merve Noyan, Pedro Cuenca, Cyril Zakka, Joshua Lochner

---

## TL;DR: SmolVLM can now watch 📺 with even better visual understanding

SmolVLM2 represents a fundamental shift in how we think about video understanding - moving from massive models that require substantial computing resources to efficient models that can run anywhere. Our goal is simple: **make video understanding accessible across all devices and use cases**, from phones to servers.

### Key Highlights:
- 🎯 **Three model sizes**: 2.2B, 500M, and 256M parameters
- 🚀 **MLX ready**: Python and Swift APIs from day zero  
- 📱 **Device-optimized**: Runs on everything from phones to servers
- 🎬 **Video-first**: Advanced video understanding capabilities
- 💾 **Memory efficient**: Requires only 1.8GB GPU memory for video inference

Want to try SmolVLM2 right away? Check out our interactive chat interface where you can test visual and video understanding capabilities of SmolVLM2 2.2B through a simple, intuitive interface.

---

## Table of Contents

- [TL;DR: SmolVLM can now watch 📺 with even better visual understanding](#tldr-smolvlm-can-now-watch--with-even-better-visual-understanding)
- [Technical Details](#technical-details)
- [SmolVLM2 2.2B: Our New Star Player for Vision and Video](#smolvlm2-22b-our-new-star-player-for-vision-and-video)
- [Going Even Smaller: Meet the 500M and 256M Video Models](#going-even-smaller-meet-the-500m-and-256m-video-models)
- [Suite of SmolVLM2 Demo applications](#suite-of-smolvlm2-demo-applications)
  - [iPhone Video Understanding](#iphone-video-understanding)
  - [VLC media player integration](#vlc-media-player-integration)
  - [Video Highlight Generator](#video-highlight-generator)
- [Using SmolVLM2 with Transformers and MLX](#using-smolvlm2-with-transformers-and-mlx)
  - [Transformers](#transformers)
  - [Video Inference](#video-inference)
  - [Multiple Image Inference](#multiple-image-inference)
  - [Inference with MLX](#inference-with-mlx)
  - [Swift MLX](#swift-mlx)
- [Fine-tuning SmolVLM2](#fine-tuning-smolvlm2)
- [Citation Information](#citation-information)

---

## Technical Details

We are introducing **three new models** with different parameter counts optimized for various use cases:

| Model Size | Parameters | Use Case | Memory Requirements |
|------------|------------|----------|-------------------|
| **SmolVLM2-2.2B** | 2.2B | Primary choice for vision/video tasks | Standard GPU |
| **SmolVLM2-500M** | 500M | Smallest video language model | 1.8GB GPU memory |
| **SmolVLM2-256M** | 256M | Experimental ultra-compact model | Mobile/edge devices |

### Performance Highlights:
- 🏆 **Best-in-class efficiency**: Outperform existing models per memory consumption
- 📊 **Video-MME benchmark**: Joins frontier model families in the 2B range
- 🥇 **Leading small models**: Best performance in the sub-1B parameter space

![SmolVLM2 Performance](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/smolvlm2-videomme2.png)

*SmolVLM2 Performance Comparison*

**About Video-MME Benchmark:**
Video-MME stands out as a comprehensive benchmark due to its extensive coverage across diverse video types, varying durations (11 seconds to 1 hour), multiple data modalities (including subtitles and audio), and high-quality expert annotations spanning 900 videos totaling 254 hours.

---

## SmolVLM2 2.2B: Our New Star Player for Vision and Video

Compared with the previous SmolVLM family, our new 2.2B model got better at solving math problems with images, reading text in photos, understanding complex diagrams, and tackling scientific visual questions. This shows in the model performance across different benchmarks:

![SmolVLM2 Vision Score Gains](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/smolvlm2-score-gains.png)

*SmolVLM2 Vision Score Gains*

When it comes to video tasks, 2.2B is a good bang for the buck. Across the various scientific benchmarks we evaluated it on, we want to highlight its performance on Video-MME where it outperforms all existing 2B models.

We were able to achieve a good balance on video/image performance thanks to the data mixture learnings published in Apollo: An Exploration of Video Understanding in Large Multimodal Models

It's so memory efficient, that you can run it even in a free Google Colab.

Python Code

---

## Going Even Smaller: Meet the 500M and 256M Video Models

Nobody dared to release such small video models until today.

Our new SmolVLM2-500M-Video-Instruct model has video capabilities very close to SmolVLM 2.2B, but at a fraction of the size: we're getting the same video understanding capabilities with less than a quarter of the parameters 🤯.

And then there's our little experiment, the SmolVLM2-256M-Video-Instruct. Think of it as our "what if" project - what if we could push the boundaries of small models even further? Taking inspiration from what IBM achieved with our base SmolVLM-256M-Instruct a few weeks ago, we wanted to see how far we could go with video understanding. While it's more of an experimental release, we're hoping it'll inspire some creative applications and specialized fine-tuning projects.

---

## Suite of SmolVLM2 Demo applications

To demonstrate our vision in small video models, we've built three practical applications that showcase the versatility of these models.

### iPhone Video Understanding

We've created an iPhone app running SmolVLM2 completely locally. Using our 500M model, users can analyze and understand video content directly on their device - no cloud required. Interested in building iPhone video processing apps with AI models running locally? We're releasing it very soon - fill this form to test and build with us!

### VLC media player integration

Working in collaboration with VLC media player, we're integrating SmolVLM2 to provide intelligent video segment descriptions and navigation. This integration allows users to search through video content semantically, jumping directly to relevant sections based on natural language descriptions. While this is work in progress, you can experiment with the current playlist builder prototype in this space.

### Video Highlight Generator

Available as a Hugging Face Space, this application takes long-form videos (1+ hours) and automatically extracts the most significant moments. We've tested it extensively with soccer matches and other lengthy events, making it a powerful tool for content summarization. Try it yourself in our demo space.

---

## Using SmolVLM2 with Transformers and MLX

We make SmolVLM2 available to use with transformers and MLX from day zero. In this section, you can find different inference alternatives and tutorials for video and multiple images.

### Transformers

The easiest way to run inference with the SmolVLM2 models is through the **conversational API** – applying the chat template takes care of preparing all inputs automatically.

#### Installation

```bash
# Install transformers from main branch with SmolVLM2 support
pip install git+https://github.com/huggingface/transformers@v4.49.0-SmolVLM-2
```

#### Loading the Model

```python
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch

# Choose your model size
model_path = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"  # or 2.2B, 256M

# Load processor and model
processor = AutoProcessor.from_pretrained(model_path)
model = AutoModelForImageTextToText.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    _attn_implementation="flash_attention_2"  # Optional: for better performance
).to("cuda")  # or "mps" for Apple Silicon
```

### Video Inference

SmolVLM2 supports direct video processing through the chat template. Simply specify the video path and your question.

#### Supported Video Formats:
- **MP4, AVI, MOV** (most common formats)
- **Max duration**: Up to 5 minutes recommended
- **Frame sampling**: 64 frames @ 1 FPS automatically
- **Resolution**: Up to 2048px (automatically resized to 512px for processing)

#### Example:

```python
# Video analysis example
messages = [
    {
        "role": "user",
        "content": [
            {"type": "video", "path": "path_to_video.mp4"},
            {"type": "text", "text": "Describe this video in detail"}
        ]
    },
]

# Process the video and generate response
inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(model.device, dtype=torch.bfloat16)

# Generate response
generated_ids = model.generate(
    **inputs, 
    do_sample=False, 
    max_new_tokens=128
)

# Decode and print result
generated_texts = processor.batch_decode(
    generated_ids,
    skip_special_tokens=True,
)

print(generated_texts[0])
```

### Multiple Image Inference

In addition to video, SmolVLM2 supports multi-image conversations. You can use the same API through the chat template, providing each image using a filesystem path, an URL, or a PIL.Image object:

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What are the differences between these two images?"},
          {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"},
          {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/0052a70beed5bf71b92610a43a52df6d286cd5f3/diffusers/rabbit.jpg"},            
        ]
    },
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(model.device, dtype=torch.bfloat16)

generated_ids = model.generate(**inputs, do_sample=False, max_new_tokens=64)
generated_texts = processor.batch_decode(
    generated_ids,
    skip_special_tokens=True,
)

print(generated_texts[0])
```

### Inference with MLX

To run SmolVLM2 with MLX on Apple Silicon devices using Python, you can use the excellent mlx-vlm library. First, you need to install mlx-vlm from this branch using the following command:

```bash
pip install git+https://github.com/pcuenca/mlx-vlm.git@smolvlm
```

Then you can run inference on a single image using the following one-liner, which uses the unquantized 500M version of SmolVLM2:

```bash
python -m mlx_vlm.generate \
  --model mlx-community/SmolVLM2-500M-Video-Instruct-mlx \
  --image https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg \
  --prompt "Can you describe this image?"
```

We also created a simple script for video understanding. You can use it as follows:

```bash
python -m mlx_vlm.smolvlm_video_generate \
  --model mlx-community/SmolVLM2-500M-Video-Instruct-mlx \
  --system "Focus only on describing the key dramatic action or notable event occurring in this video segment. Skip general context or scene-setting details unless they are crucial to understanding the main action." \
  --prompt "What is happening in this video?" \
  --video /Users/pedro/Downloads/IMG_2855.mov \
  --prompt "Can you describe this image?"
```

Note that the system prompt is important to bend the model to the desired behaviour. You can use it to, for example, describe all scenes and transitions, or to provide a one-sentence summary of what's going on.

### Swift MLX

The Swift language is also supported through the mlx-swift-examples repo, which is what we used to build our iPhone app.

Until our in-progress PR is finalized and merged, you have to compile the project from this fork, and then you can use the llm-tool CLI on your Mac as follows.

For image inference:

```bash
./mlx-run --debug llm-tool \
    --model mlx-community/SmolVLM2-500M-Video-Instruct-mlx \
    --prompt "Can you describe this image?" \
    --image https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg \
    --temperature 0.7 --top-p 0.9 --max-tokens 100
```

Video analysis is also supported, as well as providing a system prompt. We found system prompts to be particularly helpful for video understanding, to drive the model to the desired level of detail we are interested in. This is a video inference example:

```bash
./mlx-run --debug llm-tool \
    --model mlx-community/SmolVLM2-500M-Video-Instruct-mlx \
    --system "Focus only on describing the key dramatic action or notable event occurring in this video segment. Skip general context or scene-setting details unless they are crucial to understanding the main action." \
    --prompt "What is happening in this video?" \
    --video /Users/pedro/Downloads/IMG_2855.mov \
    --temperature 0.7 --top-p 0.9 --max-tokens 100
```

If you integrate SmolVLM2 in your apps using MLX and Swift, we'd love to know about it! Please, feel free to drop us a note in the comments section below!

---

## Fine-tuning SmolVLM2

You can fine-tune SmolVLM2 on videos using transformers 🤗 We have fine-tuned the 500M variant in Colab on video-caption pairs in VideoFeedback dataset for demonstration purposes. Since the 500M variant is small, it's better to apply full fine-tuning instead of QLoRA or LoRA, meanwhile you can try to apply QLoRA on cB variant. You can find the fine-tuning notebook here.

---

## Citation Information

You can cite us in the following way:

```bibtex
@article{marafioti2025smolvlm,
  title={SmolVLM: Redefining small and efficient multimodal models}, 
  author={Andrés Marafioti and Orr Zohar and Miquel Farré and Merve Noyan and Elie Bakouch and Pedro Cuenca and Cyril Zakka and Loubna Ben Allal and Anton Lozhkov and Nouamane Tazi and Vaibhav Srivastav and Joshua Lochner and Hugo Larcher and Mathieu Morlon and Lewis Tunstall and Leandro von Werra and Thomas Wolf},
  journal={arXiv preprint arXiv:2504.05299},
  year={2025}
}
```