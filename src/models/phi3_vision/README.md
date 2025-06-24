# Phi-3 Vision Server

This directory contains startup scripts and documentation for Microsoft Phi-3 Vision models.

## 🎯 Model Overview

**Phi-3 Vision** is a 4.2B parameter multimodal large language model developed by Microsoft, featuring:

- **📸 Image Understanding**: High-precision visual analysis capabilities
- **💬 Dialogue Generation**: Fluent multi-turn conversations
- **🔍 OCR Functionality**: Text recognition in images
- **📊 Chart Analysis**: Support for charts, tables, and complex visual content
- **🚀 High Performance**: Optimized inference speed using vLLM engine

## 🚀 Quick Start

### Using Python Start Script (Recommended)

```bash
cd src/models/phi3_vision
python start_server.py
```

### Direct vLLM Command

```bash
python -m vllm.entrypoints.openai.api_server \
    --model microsoft/Phi-3-vision-128k-instruct \
    --trust-remote-code \
    --port 8080
```

## 📦 Installation Requirements

### Install vLLM

```bash
# Install vLLM (GPU version recommended)
pip install vllm

# Or if you don't have GPU
pip install vllm-cpu
```

### System Requirements

- **GPU**: Recommended 8GB+ VRAM (NVIDIA GPU)
- **RAM**: Recommended 16GB+ system memory
- **Python**: 3.8 or higher
- **CUDA**: 11.8 or higher (for GPU version)

## 📡 API Usage

After server startup, you can access the API at these endpoints:

- **Health Check**: `GET http://localhost:8080/health`
- **Chat Completion**: `POST http://localhost:8080/v1/chat/completions`
- **API Documentation**: `GET http://localhost:8080/docs`

### Basic Request Example

```python
import requests
import base64

# Read image and convert to base64
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = requests.post("http://localhost:8080/v1/chat/completions", json={
    "model": "microsoft/Phi-3-vision-128k-instruct",
    "messages": [
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "Please describe this image in detail"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        }
    ],
    "max_tokens": 500,
    "temperature": 0.7
})

print(response.json())
```

### Advanced Parameter Settings

```python
response = requests.post("http://localhost:8080/v1/chat/completions", json={
    "model": "microsoft/Phi-3-vision-128k-instruct",
    "messages": [...],
    "max_tokens": 1000,        # Maximum generation tokens
    "temperature": 0.3,        # Control creativity (0.0-1.0)
    "top_p": 0.9,             # Nucleus sampling parameter
    "frequency_penalty": 0.1,  # Reduce repetition
    "presence_penalty": 0.1,   # Encourage new topics
    "stop": ["[END]"]         # Stop tokens
})
```

## 🏗️ Architecture Overview

This implementation uses a modern, streamlined architecture:

```
Request → main.py (preprocessing) → vLLM Server → Response
           ↑                          ↑
    Image optimization+API proxy   Phi-3 Vision inference
```

### Component Description

1. **vLLM Server** - High-performance model inference engine
2. **main.py** (in src/backend/) - API proxy and image preprocessing
3. **start_server.py** - Convenient server startup script

## 📊 Performance Optimization

### GPU Memory Optimization

```bash
# If encountering OOM (Out of Memory)
python -m vllm.entrypoints.openai.api_server \
    --model microsoft/Phi-3-vision-128k-instruct \
    --trust-remote-code \
    --port 8080 \
    --gpu-memory-utilization 0.8
```

### Batch Processing Settings

```bash
# Adjust batch size
python -m vllm.entrypoints.openai.api_server \
    --model microsoft/Phi-3-vision-128k-instruct \
    --trust-remote-code \
    --port 8080 \
    --max-num-batched-tokens 4096
```

## 🔄 Model Switching

### Flexible Model Switching Options

The Phi-3 Vision server now supports **5 different ways** to switch between model variants:

#### **Method 1: Command Line Arguments (Recommended)**
```bash
# Switch between variants easily
python start_server.py --model phi3        # 128K version (default)
python start_server.py --model phi3.5      # Enhanced version
python start_server.py --model phi3-128k   # Explicit 128K version
python start_server.py --list              # See all available models
```

#### **Method 2: Environment Variables**
```bash
# Set model variant via environment
PHI3_MODEL=phi3.5 python start_server.py
PHI3_PORT=8081 python start_server.py
PHI3_GPU_MEMORY=0.6 python start_server.py
```

#### **Method 3: Universal Model Switcher**
```bash
# From project root
python model_switcher.py switch phi3_vision     # Switch to 128K
python model_switcher.py switch phi3.5_vision   # Switch to 3.5
python model_switcher.py list                   # See all project models
```

#### **Method 4: Configuration Files**
```bash
# Edit model-specific configs
src/config/model_configs/phi3_vision.json      # For 128K version
src/config/model_configs/phi3.5_vision.json    # For 3.5 version
```

#### **Method 5: Interactive Help**
```bash
python start_server.py --help    # See all options
python start_server.py --list    # List available models
```

### Model Comparison

| Feature | Phi-3-vision-128k | Phi-3.5-vision |
|---------|------------------|----------------|
| **Release Date** | April 2024 | August 2024 |
| **Multi-image Support** | Basic | Enhanced |
| **Video Understanding** | Limited | Improved |
| **Performance** | MMMU: 40.2 | MMMU: 43.0 |
| **Reasoning** | Standard | Enhanced |
| **Command** | `--model phi3` | `--model phi3.5` |
| **Config File** | `phi3_vision.json` | `phi3.5_vision.json` |

## 🔄 Comparison with Other Models

| Feature | Phi-3 Vision | SmolVLM |
|---------|-------------|---------|
| **Parameters** | 4.2B | 0.5B |
| **Inference Engine** | vLLM | llama-server |
| **Image Understanding** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Accuracy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Memory Requirements** | 8GB+ | 2GB+ |

## 🛠️ Troubleshooting

### vLLM Installation Issues

```bash
# Check CUDA version
nvidia-smi

# Reinstall vLLM
pip uninstall vllm
pip install vllm --no-cache-dir
```

### Memory Insufficient

```bash
# Method 1: Reduce GPU memory usage
--gpu-memory-utilization 0.6

# Method 2: Use CPU (slower)
pip install vllm-cpu
export VLLM_USE_CPU=1
```

### Slow Model Download

```bash
# Set Hugging Face mirror
export HF_ENDPOINT=https://hf-mirror.com

# Or manually download model
huggingface-cli download microsoft/Phi-3-vision-128k-instruct
```

### Common Error Solutions

1. **OutOfMemoryError**: Reduce `gpu-memory-utilization`
2. **ModuleNotFoundError**: Confirm vLLM is properly installed
3. **CUDA errors**: Check CUDA version compatibility

## 📈 Usage Recommendations

### Image Input Best Practices

- **Resolution**: Recommended 336x336 to 1344x1344
- **Format**: JPEG, PNG both supported
- **Size**: Single image recommended < 5MB
- **Quality**: Clear images work better

### Prompt Design Tips

```python
# Good prompt example
"Please analyze this image in detail, including: 1) main objects, 2) color scheme, 3) spatial layout"

# Avoid vague prompts
"Look at image"
```

## 📄 License

This project follows the MIT License. Phi-3 Vision model follows Microsoft's license terms.

## 🔗 Related Links

- [Phi-3 Vision Official Documentation](https://huggingface.co/microsoft/Phi-3-vision-128k-instruct)
- [Phi-3.5 Vision Documentation](https://huggingface.co/microsoft/Phi-3.5-vision-instruct)
- [vLLM Official Documentation](https://docs.vllm.ai/)
- [Microsoft Phi-3 Research Paper](https://arxiv.org/abs/2404.14219) 