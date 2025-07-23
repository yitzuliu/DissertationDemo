# Phi-3.5-Vision MLX Model

Microsoft's Phi-3.5-Vision multimodal model with dual implementation for performance and compatibility.

## File Structure

Phi-3.5-Vision follows the project's standard dual-implementation pattern:

### Optimized Version (Recommended for Apple Silicon)
- **`run_phi3_vision_optimized.py`** - Flask server with MLX optimization
- **`phi3_vision_optimized.py`** - MLX-optimized model implementation with INT4 quantization
- **`phi3_vision_optimized.json`** - Configuration for optimized version

### Standard Version (Maximum Compatibility)
- **`run_phi3_vision.py`** - FastAPI server for universal compatibility
- **`phi3_vision_model.py`** - Standard transformers implementation
- **`phi3_vision.json`** - Configuration for standard version

## Quick Start

### Optimized Version (Better Performance on Apple Silicon)

```bash
# Install MLX dependencies first
pip install mlx-vlm mlx>=0.11.0

# Run optimized server
cd "src/models/Phi_3.5_Vision MLX"
python run_phi3_vision_optimized.py
```

**Features:**
- 🍎 MLX optimization for Apple Silicon (M1/M2/M3)
- ⚡ INT4 quantization for memory efficiency
- 🗄️ Image preprocessing cache
- 🚀 Flask server with threading
- 📉 Significant memory and speed improvements
- 🔄 Automatic fallback to transformers

### Standard Version (Universal Compatibility)

```bash
# Run standard server
cd "src/models/Phi_3.5_Vision MLX"
python run_phi3_vision.py
```

**Features:**
- 🌐 FastAPI server with full async support
- 🛡️ Maximum compatibility across platforms
- 💻 CPU inference for stability
- 📡 Full transformers integration
- 🔧 Standard precision (float32)

## Performance Comparison

| Version | Framework | Device | Load Time | Inference | Memory | Quantization |
|---------|-----------|---------|-----------|-----------|---------|--------------|
| **Optimized** | MLX + Flask | Apple Silicon | ~8-12s | ~3-5s | 4-6GB | INT4 |
| **Standard** | Transformers + FastAPI | CPU/MPS | ~15-25s | ~8-15s | 8-12GB | float32 |

## API Usage

Both versions provide OpenAI-compatible endpoints:

### Health Check
```bash
curl http://localhost:8080/health
```

### Chat Completions
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-3.5-vision",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What do you see in this image?"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64,..."
            }
          }
        ]
      }
    ],
    "max_tokens": 100
  }'
```

### Performance Stats
```bash
curl http://localhost:8080/stats
```

## MLX Optimization Details

The optimized version uses several performance enhancements:

### 1. MLX Framework
- **Apple Silicon optimization** - Native M1/M2/M3 acceleration
- **INT4 quantization** - Reduces memory usage by ~75%
- **Unified memory** - Efficient GPU/CPU memory sharing

### 2. Caching System
- **Image preprocessing cache** - Avoid repeated processing
- **Response cache** - Cache recent predictions
- **Temporary file management** - Automatic cleanup

### 3. Fallback Strategy
```python
try:
    # Primary: MLX inference
    result = mlx_generate(image, prompt)
except:
    # Fallback: Transformers inference
    result = transformers_generate(image, prompt)
```

## Installation Requirements

### Optimized Version
```bash
pip install mlx-vlm>=0.0.9 mlx>=0.11.0
pip install transformers>=4.40.0 torch>=2.0.0
pip install Pillow>=9.0.0 flask>=2.3.0
```

### Standard Version
```bash
pip install transformers>=4.40.0 torch>=2.0.0
pip install Pillow>=9.0.0 fastapi>=0.100.0 uvicorn>=0.22.0
```

## Model Information

- **Base Model**: microsoft/Phi-3.5-vision-instruct
- **MLX Model**: lokinfey/Phi-3.5-vision-mlx-int4
- **Context Length**: 2048 tokens
- **Image Size**: Up to 1024x1024
- **Supported Formats**: JPEG, PNG, WebP

## Common Issues & Solutions

### MLX Not Available
```
⚠️ MLX not available, install with: pip install mlx-vlm
```
**Solution**: Install MLX dependencies or use standard version

### Memory Issues
```
❌ CUDA out of memory / MPS allocation failed
```
**Solution**: Use CPU device or reduce image size

### Long Loading Times
```
⏳ Model loading takes 15+ seconds
```
**Solution**: Pre-load model or use optimized version

## Version Selection Guide

| Use Case | Recommended Version | Reason |
|----------|-------------------|---------|
| **Apple Silicon (M1/M2/M3)** | Optimized | 3-4x faster, less memory |
| **Development/Testing** | Standard | Better debugging, more stable |
| **Production (Mac)** | Optimized | Best performance |
| **Production (Linux/Windows)** | Standard | Better compatibility |
| **Limited Memory (<8GB)** | Optimized | INT4 quantization |
| **Maximum Stability** | Standard | Mature transformers backend |

## Configuration

Models can be configured via JSON files in `src/config/model_configs/`:

- `phi3_vision.json` - Standard version settings
- `phi3_vision_optimized.json` - Optimized version settings

Key configuration options:
- `max_tokens`: Response length limit
- `device`: Target device (auto/cpu/mps)
- `image_processing.max_size`: Maximum image resolution
- `cache_settings.image_cache_size`: Cache size

## Testing

Both implementations can be tested with the unified test framework:

```python
from src.testing.vlm_tester import VLMTester

# Test optimized version
tester = VLMTester()
results = tester.test_model("Phi-3.5-Vision-Optimized")

# Test standard version  
results = tester.test_model("Phi-3.5-Vision")
```

## Project Integration

Phi-3.5-Vision integrates with the broader vision language model framework:

- **Base Model**: Inherits from `BaseVisionModel`
- **Config Manager**: Uses `src/backend/utils/config_manager.py`
- **Image Processing**: Uses `src/backend/utils/image_processing.py`
- **Testing**: Compatible with `src/testing/vlm_tester.py`

## License

This implementation follows the license terms of the base Phi-3.5-Vision model from Microsoft. 