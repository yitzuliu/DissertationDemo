# LLaVA MLX Model

A high-performance multimodal vision-language model optimized for Apple Silicon using MLX framework with INT4 quantization for efficient inference.

## 🎯 Model Overview

LLaVA MLX provides state-of-the-art vision-language understanding capabilities with Apple Silicon optimization. This implementation uses the MLX framework for superior performance on M1/M2/M3 chips with quantized weights for memory efficiency.

## ⚠️ Requirements

### Hardware Requirements
- **Apple Silicon (M1/M2/M3) REQUIRED** - This model will not run on Intel or other architectures
- **Minimum 16GB RAM** recommended for stable operation
- **macOS Monterey 12.0+** for optimal MLX performance

### Software Requirements
- **MLX-VLM package** - Core MLX vision-language model support
- **MLX Framework** - Apple's machine learning framework
- **Python 3.9+** - Required for MLX compatibility

## 📁 File Structure

### Core Implementation
- **`run_llava_mlx.py`** - Flask server with OpenAI-compatible API endpoints
- **`llava_mlx_model.py`** - Core model class with MLX inference optimization
- **`src/config/model_configs/llava_mlx.json`** - Complete model configuration

### Documentation
- **`README.md`** - This comprehensive guide
- **Testing logs** - Available in `../../logs/` directory

## 🚀 Quick Start

### 1. Installation

```bash
# Activate your virtual environment
source ai_vision_env/bin/activate

# Install MLX-VLM and dependencies
pip install mlx-vlm>=0.0.9
pip install mlx>=0.11.0

# Install Flask for the server
pip install Flask>=2.3.0
pip install Pillow>=9.0.0
```

### 2. Verify MLX Installation

```bash
# Test MLX availability
python -c "import mlx.core as mx; print('MLX available:', mx.default_device())"

# Test MLX-VLM installation
python -c "import mlx_vlm; print('MLX-VLM version:', mlx_vlm.__version__)"
```

### 3. Start the Server

```bash
# Navigate to LLaVA MLX directory
cd src/models/llava_mlx

# Run the server
python run_llava_mlx.py
```

The server will start on **port 8080** by default.

### 4. Verify Server Status

```bash
# Health check
curl http://localhost:8080/health

# Expected response: {"status": "healthy", "model": "LLaVA-MLX", ...}
```

## ⚙️ Configuration

### Model Configuration
Located at: `src/config/model_configs/llava_mlx.json`

Key configuration options:
```json
{
  "model_name": "LLaVA-MLX",
  "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit",
  "device": "mps",
  "quantization": "int4",
  "max_tokens": 150,
  "image_processing": {
    "max_size": 1024,
    "min_size": 224,
    "format": "RGB",
    "quality": 95
  }
}
```

### Setting as Active Model
```bash
# Through backend API
curl -X PATCH http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"active_model": "llava_mlx"}'
```

## 🔧 Technical Specifications

### Model Architecture
- **Base Model**: LLaVA-v1.6-Mistral-7B
- **Quantization**: INT4 for memory efficiency
- **Framework**: MLX with Apple Silicon optimization
- **Context Length**: 4096 tokens
- **Vision Encoder**: CLIP-based with high-resolution support

### Capabilities
- **Image Understanding**: Detailed visual analysis and description
- **Question Answering**: Accurate responses about image content
- **Multi-turn Conversation**: Context-aware dialog about images
- **High Resolution**: Supports up to 1024px images efficiently
- **Fast Inference**: Optimized for Apple Silicon performance

### Performance Characteristics
| Metric | Value | Context |
|--------|-------|---------|
| **Model Size** | ~4GB (quantized) | INT4 quantization |
| **Memory Usage** | 6-8GB peak | During inference |
| **Inference Speed** | ~2-4s per image | On Apple M3 |
| **Supported Formats** | JPEG, PNG, WebP | Auto-conversion to RGB |

## 🏗️ Implementation Details

### MLX Integration
LLaVA MLX uses native MLX operations for optimal Apple Silicon performance:

```python
# MLX-optimized inference
from mlx_vlm import load, generate

# Model loading with quantization
model, processor = load(
    "mlx-community/llava-v1.6-mistral-7b-4bit",
    trust_remote_code=True
)

# Efficient inference
response = generate(
    model=model,
    processor=processor,
    image=image,
    prompt=prompt,
    max_tokens=max_tokens
)
```

### Image Processing Pipeline
1. **Input Validation**: Verify image format and size
2. **Preprocessing**: Resize and normalize for model input
3. **MLX Conversion**: Convert to MLX tensor format
4. **Inference**: Process through quantized model
5. **Post-processing**: Extract and clean response text

### API Compatibility
Provides OpenAI-compatible chat completions endpoint:
- Standard message format with image_url support
- Proper error handling and status codes
- Streaming response support (planned)

## 📊 Performance Comparison

| Feature | LLaVA MLX | Phi-3.5-Vision | SmolVLM2 |
|---------|-----------|----------------|----------|
| **Model Size** | ~4GB | ~3GB | ~2GB |
| **Accuracy** | ✅ High | ✅ High | ✅ Good |
| **Speed** | ⚡ Fast | ⚡ Fast | 🏆 Fastest |
| **Memory** | 6-8GB | 4-6GB | 2-4GB |
| **Apple Silicon** | 🏆 Native MLX | ✅ MLX | ✅ MPS |
| **Image Quality** | 🏆 Excellent | ✅ Good | ✅ Good |

## 🎯 Use Cases

### Recommended For
- **High-accuracy image analysis** - When detail and accuracy are paramount
- **Professional applications** - Medical imaging, technical documentation
- **Research and development** - Academic and scientific image analysis
- **Content creation** - Detailed image descriptions for accessibility
- **Apple Silicon systems** - Leverages native MLX optimization

### Example Applications
- Medical image analysis with detailed descriptions
- Art and photography critique and analysis
- Technical documentation with image explanations
- Educational content with visual learning support
- Accessibility applications requiring detailed alt-text

### Not Ideal For
- **Real-time applications** - Consider SmolVLM2 for speed-critical tasks
- **Memory-constrained environments** - Higher memory requirements
- **Synthetic images** - May struggle with certain synthetic/generated content

## ⚠️ Known Issues and Limitations

### Current Known Issues
1. **Synthetic Image Performance** - May fail on certain synthetic, square images
2. **Memory Requirements** - Requires substantial RAM for optimal performance
3. **Platform Dependency** - Only works on Apple Silicon hardware

### Limitations
- **Apple Silicon Only** - Cannot run on Intel or other architectures
- **Memory Intensive** - Requires 16GB+ RAM for stable operation
- **Model Loading Time** - Initial model load can take 30-60 seconds

### Troubleshooting Common Issues

1. **"MLX not available" Error**
   ```bash
   # Install MLX framework
   pip install mlx>=0.11.0
   
   # Verify installation
   python -c "import mlx.core as mx; print(mx.default_device())"
   ```

2. **"Model loading failed" Error**
   ```bash
   # Check available memory
   python -c "import psutil; print(f'Available RAM: {psutil.virtual_memory().available/1024**3:.1f}GB')"
   
   # Free up memory if needed
   ```

3. **"Image preprocessing failed" Error**
   ```bash
   # Check image format and size
   # Ensure image is valid JPEG/PNG and under 10MB
   ```

## 🔍 Testing and Validation

### Test Results Summary
Based on comprehensive testing (see `../../logs/` for detailed results):

- **✅ Natural Images**: Excellent performance on photographs and real-world images
- **✅ Text Recognition**: Good OCR capabilities for text in images
- **✅ Scene Analysis**: Detailed and accurate scene descriptions
- **⚠️ Synthetic Images**: Variable performance on generated/synthetic content
- **✅ Multi-turn Dialog**: Maintains context across conversation turns

### Performance Benchmarks
- **Average Inference Time**: 2.8s (Apple M3 MacBook Air)
- **Peak Memory Usage**: 7.2GB during inference
- **Model Loading Time**: 42s (first time)
- **Success Rate**: 92% on natural images, 76% on synthetic images

## 🔧 Advanced Configuration

### Memory Optimization
```json
{
  "mlx_config": {
    "memory_pool_size": "8GB",
    "cache_size": 512,
    "batch_size": 1
  }
}
```

### Image Processing Tuning
```json
{
  "image_processing": {
    "max_size": 768,
    "preprocessing_quality": "high",
    "maintain_aspect_ratio": true,
    "padding_color": [255, 255, 255]
  }
}
```

## 📚 Additional Resources

- **[MLX-VLM Documentation](https://github.com/Blaizzy/mlx-vlm)** - Official MLX-VLM documentation
- **[LLaVA Project](https://llava-vl.github.io/)** - Original LLaVA research project
- **[MLX Framework](https://ml-explore.github.io/mlx/)** - Apple's MLX machine learning framework
- **[Model Card](https://huggingface.co/mlx-community/llava-v1.6-mistral-7b-4bit)** - Hugging Face model documentation
- **[System Architecture](../../docs/ARCHITECTURE.md)** - Overall system design
- **[Performance Benchmarks](../../logs/)** - Detailed testing results

---

**Status**: ✅ **Production Ready** | **Recommended**: ✅ **For High-Accuracy Tasks** | **Last Updated**: January 2025

**🏆 Accuracy Champion**: Choose LLaVA MLX when maximum accuracy and detail are required for image analysis tasks.