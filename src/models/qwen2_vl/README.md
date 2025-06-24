# Qwen2-VL-2B Model Deployment Guide

This directory contains scripts for downloading, using, and optimizing the Qwen2-VL-2B model, specifically designed for the AI Manual Assistant project, with a particular focus on efficient operation on edge devices (such as laptops and mobile devices).

## Directory Contents

- `download_model.py`: Downloads the Qwen2-VL-2B model from Hugging Face and optionally converts it to GGUF format
- `demo.py`: Standard model usage demonstration script
- `edge_optimized.py`: Lightweight implementation optimized for edge devices

## System Requirements

- Python 3.8+
- 8GB+ RAM (16GB recommended)
- Disk space: ~5GB
- Hardware acceleration support: Apple Silicon (recommended) or CUDA GPU

## Alternative VLM Models

In addition to Qwen2-VL-2B, you might consider these powerful alternatives:

### MiniCPM-Llama3-V 2.5
- **Developer**: CaptainAI Research Team (Shanghai AI Lab and Chinese universities collaboration)
- **Key Features**: 
  - Based on Llama3 architecture
  - Exceptional performance on Apple Silicon
  - Strong visual reasoning capabilities
  - Lightweight (2.5B parameters)
- **Best For**: Projects prioritizing Apple devices and efficiency

### Phi-3-vision
- **Developer**: Microsoft Research
- **Key Features**:
  - Based on Microsoft's Phi-3 architecture
  - Advanced visual reasoning with small model size
  - Very efficient on high-end mobile devices
  - Strong zero-shot performance
- **Best For**: Projects requiring strong performance at smaller scale

The current implementation focuses on Qwen2-VL-2B due to its balance of performance, size, and edge device compatibility, but both alternatives above can be integrated using similar patterns.

## Installation Steps

### 1. Install Dependencies

```bash
# Basic dependencies
pip install torch transformers huggingface_hub pillow numpy psutil

# Edge device optimization dependencies
pip install llama-cpp-python
```

For Apple Silicon Mac users, use the following command to install llama-cpp-python optimized for Metal:
```bash
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
```

### 2. Download Model

```bash
# Download original model
python download_model.py --output_dir ./model

# Download and convert to GGUF format (recommended for edge devices)
python download_model.py --output_dir ./model --convert_to_gguf --quantize int4
```

## Usage

### Standard Demo

```bash
python demo.py --model_dir ./model --image path/to/your/image.jpg --prompt "Describe the content in this image"
```

### Edge Device Optimized Version

```bash
python edge_optimized.py --model_path ./model/qwen2vl-2b-q4_k_m.gguf --image path/to/your/image.jpg --prompt "Describe the content in this image" --optimization_level medium
```

Optimization level options:
- `low`: Quality priority, slower processing
- `medium`: Balance quality and speed (recommended)
- `high`: Speed priority, slightly reduced quality

## Integration with AI Manual Assistant

To integrate this model into the main project, follow these steps:

1. Make sure you have downloaded the model and converted it to GGUF format (recommended for edge devices)
2. The architecture design in `integration_plan.md` has set this model as a core component
3. Use the code pattern in `edge_optimized.py` to build your application

Example integration code:

```python
from PIL import Image
import sys
sys.path.append("src/Qwen2-VL-2B")
from edge_optimized import load_optimized_model, preprocess_image, process_with_edge_model

# Load model (only load once at program startup)
model = load_optimized_model("src/Qwen2-VL-2B/model/qwen2vl-2b-q4_k_m.gguf", cpu_threads=4)

# Process images in real-time
def process_camera_frame(frame, prompt="Describe the objects and activities in this scene"):
    # Preprocess image
    processed_image = preprocess_image(frame, "medium")
    
    # Generate response
    answer, _ = process_with_edge_model(model, processed_image, prompt)
    
    return answer
```

## Alternative VLM Models

While Qwen2-VL-2B is our primary recommended model, these alternative VLMs are also excellent choices for edge devices:

### MiniCPM-Llama3-V 2.5

Developed by the CaptainAI Research Team, MiniCPM-Llama3-V 2.5 offers:
- 2.5B parameters with strong performance-to-size ratio
- Built on Llama3 architecture for enhanced efficiency
- Strong multi-lingual capabilities
- Excellent edge device performance with quantization

### Phi-3-vision

Developed by Microsoft Research, Phi-3-vision offers:
- Lightweight model design optimized for resource-constrained environments
- Strong visual reasoning capabilities
- Good performance on general visual tasks
- Optimized for real-time applications

For integration of these alternative models, similar patterns can be used with appropriate modifications to the model loading and preprocessing steps.

## Performance Optimization Notes

- **Memory Usage**: GGUF model quantized to int4 requires approximately 1-2GB RAM
- **Processing Speed**: On a MacBook M3, typical processing time for one image is 1-3 seconds
- **Quality vs. Speed Trade-off**: Use the `--optimization_level` parameter to adjust

## Selective Integration with YOLO

As recommended in `integration_plan.md`, this VLM model is the core component, with YOLO used only for auxiliary purposes:

1. YOLO can be used for quick initial screening to determine areas of focus
2. Verifying VLM recognition results
3. Providing more precise bounding boxes for specific objects

## Troubleshooting

- **Memory Errors**: Try using a lower quantization level (int4) or increase system swap space
- **Slow Speed**: Increase optimization level, reduce image resolution, use more CPU threads
- **Device Overheating**: Reduce processing frequency, increase intervals between tasks

## Reference Resources

- [Qwen2-VL Official Documentation](https://huggingface.co/Qwen/Qwen2-VL-2B)
- [llama-cpp-python Documentation](https://github.com/abetlen/llama-cpp-python)
- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/)
