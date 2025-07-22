# AI Manual Assistant - Vision Models

This directory contains all Vision-Language Model (VLM) implementations for the AI Manual Assistant project. Each model runs as a standalone server with OpenAI-compatible APIs.

## 🏗️ Current Model Structure

```
src/models/
├── base_model.py                    # Base abstract class and factory
├── smolvlm2/                        # SmolVLM2-500M-Video-Instruct (🏆 Best Overall)
│   ├── run_smolvlm2.py             # Model server startup script
│   ├── smolvlm2_model.py           # Model implementation
│   └── SmolVLM2-500M-Video-Instruct/  # Model files
├── smolvlm/                         # SmolVLM-500M-Instruct (Excellent Alternative)
│   ├── run_smolvlm.py              # Model server startup script
│   └── smolvlm_model.py            # Model implementation
├── moondream2/                      # Moondream2 (⚡ Speed Champion)
│   ├── run_moondream2_optimized.py # Optimized server script
│   └── moondream2_model.py         # Model implementation
├── llava_mlx/                       # LLaVA-v1.6 MLX (⚠️ Underperforming)
│   ├── run_llava_mlx.py            # MLX-optimized server
│   └── llava_mlx_model.py          # Model implementation
├── Phi_3.5_Vision MLX/              # Phi-3.5-Vision MLX (High Accuracy)
│   ├── run_phi3_vision_optimized.py # MLX-optimized server
│   └── phi3_vision_model.py        # Model implementation
└── yolo8/                           # YOLOv8 (Object Detection)
    ├── run_yolo8.py                # YOLO server script
    └── yolo8_model.py              # Detection implementation
```

## 🎯 Model Performance Summary

Based on VQA 2.0 testing results:

| Model | VQA Accuracy | Inference Time | Memory Usage | Status |
|-------|:------------:|:--------------:|:------------:|:------:|
| **SmolVLM2-500M-Video** | 🥇 66.0% | 6.61s | 2.08GB | ✅ **Recommended** |
| **SmolVLM-500M** | 🥈 64.0% | 5.98s | 1.58GB | ✅ **Excellent** |
| **Moondream2** | 56.0% | 🏆 4.06s | 🏆 0.10GB | ✅ **Fastest** |
| **Phi-3.5-Vision (MLX)** | 60.0% | 13.61s | 1.53GB | ✅ **Detailed** |
| **LLaVA-v1.6 (MLX)** | ⚠️ 34.0% | 17.86s | 1.16GB | 🔧 **Issues** |

For detailed performance analysis, see [Model Comparison Guide](../../docs/MODEL_COMPARISON.md).

## 🚀 Quick Start

### Starting a Model Server

Each model runs as a standalone server. Choose one model to run:

```bash
# Recommended: SmolVLM2 (Best Overall Performance)
python src/models/smolvlm2/run_smolvlm2.py

# Alternative: SmolVLM (Excellent Alternative)
python src/models/smolvlm/run_smolvlm.py

# Speed: Moondream2 (Fastest Inference)
python src/models/moondream2/run_moondream2_optimized.py

# Accuracy: Phi-3.5-Vision (Detailed Analysis)
python "src/models/Phi_3.5_Vision MLX/run_phi3_vision_optimized.py"
```

### Model Server API

All models expose OpenAI-compatible endpoints:

```bash
# Health check
curl http://localhost:8080/health

# Image analysis
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "smolvlm2",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Describe this image"},
          {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
        ]
      }
    ],
    "max_tokens": 150
  }'
```

## ⚙️ Model Configuration

Each model has its own configuration file in `src/config/model_configs/`:

- `smolvlm2_500m_video_optimized.json` - SmolVLM2 configuration
- `smolvlm.json` - SmolVLM configuration  
- `moondream2_optimized.json` - Moondream2 configuration
- `phi3_vision_optimized.json` - Phi-3.5-Vision configuration
- `llava_mlx.json` - LLaVA MLX configuration

## 🔧 Model Implementation

### Base Model Interface

All models implement the `BaseVisionModel` abstract base class:

```python
from models.base_model import BaseVisionModel

class MyModel(BaseVisionModel):
    def load_model(self):
        # Load model implementation
        pass
    
    def predict(self, image, prompt, options=None):
        # Inference implementation
        return result
    
    def cleanup(self):
        # Resource cleanup
        pass
```

### Model Factory

Use the factory pattern to create model instances:

```python
from models.base_model import VLMFactory

# Create model instance
model = VLMFactory.create_model(model_name, config)

# Load and use model
model.load_model()
result = model.predict(image, prompt)
```

## 📊 Model Selection Guide

### For Production Use
1. **SmolVLM2-500M-Video-Instruct** - Best accuracy/speed balance (66.0% VQA accuracy)
2. **SmolVLM-500M-Instruct** - Excellent reliability (64.0% VQA accuracy)

### For Speed-Critical Applications
1. **Moondream2** - Fastest inference (4.06s, minimal memory)

### For Resource-Constrained Environments
1. **Moondream2** - Lowest memory usage (0.10GB)
2. **SmolVLM** - Good balance (1.58GB)

### For Detailed Analysis
1. **Phi-3.5-Vision (MLX)** - Comprehensive descriptions (60.0% accuracy)

### ⚠️ Models to Avoid
- **LLaVA-v1.6 (MLX)** - Performance issues due to model reloading overhead

## 🔄 Model Switching

To switch between models:

1. **Stop current model server** (Ctrl+C)
2. **Start new model server** using appropriate run script
3. **Backend automatically connects** to the new model on port 8080

The system supports hot-swapping between models without restarting the backend or frontend.

## 🧪 Testing Models

Use the VQA 2.0 testing framework to evaluate model performance:

```bash
# Test single model
python src/testing/vqa/vqa_test.py --questions 10 --models smolvlm2

# Compare multiple models
python src/testing/vqa/vqa_test.py --questions 10 --models smolvlm2 smolvlm moondream2
```

## 🔨 Adding New Models

To integrate a new model:

1. **Create model directory**: `src/models/my_model/`
2. **Implement model class**: Extend `BaseVisionModel`
3. **Create run script**: `run_my_model.py` with FastAPI server
4. **Add configuration**: `src/config/model_configs/my_model.json`
5. **Update factory**: Add to `VLMFactory.create_model()`

### Model Directory Template
```
src/models/my_model/
├── run_my_model.py          # FastAPI server script
├── my_model_model.py        # Model implementation
├── __init__.py              # Package initialization
└── README.md                # Model-specific documentation
```

## 📋 TODO: Future Model Integrations

### Planned Model Additions
- [ ] **Qwen2-VL-2B-Instruct** - Enhanced temporal reasoning
- [ ] **MiniCPM-V-2.6** - Apple Silicon optimized efficiency
- [ ] **InternVL2** - Advanced multimodal understanding
- [ ] **CogVLM2** - Improved reasoning capabilities

### Optimization Tasks
- [ ] **Model quantization** - 4-bit/8-bit optimization for faster inference
- [ ] **Batch processing** - Support for multiple image processing
- [ ] **Model caching** - Persistent model loading to reduce startup time
- [ ] **GPU acceleration** - CUDA support for non-Apple Silicon systems

### Infrastructure Improvements
- [ ] **Model health monitoring** - Advanced health check endpoints
- [ ] **Performance profiling** - Detailed inference time breakdown
- [ ] **Memory optimization** - Better memory management across models
- [ ] **API versioning** - Support for different API versions

## 📚 Additional Resources

- **[System Architecture](../../docs/ARCHITECTURE.md)** - Overall system design
- **[Model Comparison](../../docs/MODEL_COMPARISON.md)** - Detailed performance analysis
- **[API Documentation](../../docs/API.md)** - Complete API reference
- **[Test Results](../../TEST_RESULTS_SUMMARY.md)** - Latest performance benchmarks

---

**For model-specific documentation, see the README.md file in each model's directory.**

**Last Updated**: January 2025