# AI Manual Assistant - Vision Models Directory

This directory contains all vision-language model implementations for the AI Manual Assistant system. Each model is organized in its own subdirectory with complete implementation, documentation, and testing capabilities.

## 📁 Directory Structure

```
src/models/
├── base_model.py                    # Core abstract class and factory pattern
├── smolvlm2/                        # SmolVLM2-500M-Video-Instruct (Recommended)
├── smolvlm/                         # SmolVLM-500M-Instruct (Refactored)
├── moondream2/                      # Moondream2 (Speed Optimized)
├── llava_mlx/                       # LLaVA MLX (Apple Silicon Optimized)
├── phi3_vision_mlx/                 # Phi-3.5-Vision MLX
└── yolo8/                           # YOLOv8 (Object Detection)
```

## 🎯 Quick Model Overview

| Model | Status | Best For | Location |
|-------|--------|----------|----------|
| **SmolVLM2** | ✅ Production Ready | General purpose + Video | `smolvlm2/` |
| **SmolVLM** | ✅ Production Ready | Server deployment | `smolvlm/` |
| **Moondream2** | ✅ Production Ready | Real-time applications | `moondream2/` |
| **LLaVA MLX** | ✅ Production Ready | High accuracy | `llava_mlx/` |
| **Phi-3.5-Vision** | ⚠️ Has Issues | Research/Testing | `phi3_vision_mlx/` |
| **YOLOv8** | ✅ Production Ready | Object detection | `yolo8/` |

## 🔧 Core Architecture

### Base Model System (`base_model.py`)

The foundation of all model implementations:

- **`BaseVisionModel`**: Abstract base class defining the standard interface
- **`VLMFactory`**: Factory pattern for creating model instances
- **Common utilities**: Statistics tracking, health monitoring, resource management

**Key Interface Methods:**
```python
class BaseVisionModel(ABC):
    def load_model(self) -> bool: pass      # Model initialization
    def predict(self, image, prompt, options=None) -> Dict: pass  # Inference
    def preprocess_image(self, image) -> Any: pass  # Image preparation
    def format_response(self, raw_response) -> Dict: pass  # Response formatting
```

### Model Implementation Pattern

Each model subdirectory follows a consistent structure:

```
model_name/
├── __init__.py              # Package initialization
├── run_model.py             # Server startup script
├── model_model.py           # Core model implementation
├── README.md                # Model-specific documentation
└── [model_files/]           # Model weights and configuration
```

## 🚀 Getting Started

### 1. Choose Your Model

Navigate to the specific model directory for detailed information:

```bash
# For SmolVLM2 (Recommended)
cd src/models/smolvlm2/
cat README.md

# For SmolVLM (Refactored)
cd src/models/smolvlm/
cat README.md

# For Moondream2 (Fast)
cd src/models/moondream2/
cat README.md
```

### 2. Start a Model Server

Each model has its own startup script:

```bash
# SmolVLM2
cd src/models/smolvlm2/
python run_smolvlm2_500m_video.py

# SmolVLM
cd src/models/smolvlm/
python run_smolvlm.py

# Moondream2
cd src/models/moondream2/
python run_moondream2_optimized.py
```

### 3. Use the Model

All models provide the same API interface:

```python
from src.models.base_model import VLMFactory

# Create model instance
model = VLMFactory.create_model("smolvlm2", config)

# Load and use
model.load_model()
result = model.predict(image, prompt)
```

## 📊 Model Selection Guide

### For Production Use
- **SmolVLM2**: Best overall performance and video capabilities
- **SmolVLM**: Excellent reliability with refactored codebase
- **Moondream2**: Fastest inference for real-time applications

### For Development/Testing
- **LLaVA MLX**: High accuracy for detailed analysis
- **YOLOv8**: Object detection tasks
- **Phi-3.5-Vision**: Research purposes (has known issues)

## 🔄 Model Switching

The system supports hot-swapping between models:

1. **Stop current model**: `Ctrl+C` in the model server terminal
2. **Start new model**: Run the appropriate startup script
3. **Backend auto-connects**: System automatically detects the new model

## 🧪 Testing Models

### Individual Model Testing
Each model directory contains its own testing capabilities:

```bash
# SmolVLM testing
cd src/models/smolvlm/
python test_refactored_smolvlm.py

# SmolVLM2 testing
cd src/models/smolvlm2/
# Check README.md for testing instructions
```

### System-wide Testing
Use the unified testing framework:

```bash
# From project root
python src/testing/vqa/vqa_test.py --models smolvlm2 smolvlm moondream2
```

## 🔨 Adding New Models

### 1. Create Model Directory
```bash
mkdir src/models/my_new_model/
cd src/models/my_new_model/
```

### 2. Implement Required Files
- **`__init__.py`**: Package initialization
- **`run_my_new_model.py`**: Server startup script
- **`my_new_model_model.py`**: Model implementation (extends `BaseVisionModel`)
- **`README.md`**: Comprehensive documentation

### 3. Update Factory
Add to `src/models/base_model.py` in the `VLMFactory.create_model()` method:

```python
elif "my_new_model" in model_type:
    return MyNewModelModel(model_name, config)
```

### 4. Add Configuration
Create `src/config/model_configs/my_new_model.json`

## 📚 Detailed Documentation

For comprehensive information about each model, visit the specific model directories:

- **[SmolVLM2 Documentation](./smolvlm2/README.md)** - Video understanding capabilities
- **[SmolVLM Documentation](./smolvlm/README.md)** - Refactored server architecture
- **[Moondream2 Documentation](./moondream2/README.md)** - Speed optimization
- **[LLaVA MLX Documentation](./llava_mlx/README.md)** - Apple Silicon optimization
- **[Phi-3.5-Vision Documentation](./phi3_vision_mlx/README.md)** - Research model
- **[YOLOv8 Documentation](./yolo8/README.md)** - Object detection

## 🔧 Technical Details

### Configuration Files
All model configurations are stored in `src/config/model_configs/`:
- `smolvlm2_500m_video_optimized.json`
- `smolvlm.json`
- `moondream2_optimized.json`
- `llava_mlx.json`
- `phi3_vision_optimized.json`
- `yolo8.json`

### Server Architecture
Each model provides:
- **Health check endpoint**: `/health`
- **OpenAI-compatible API**: `/v1/chat/completions`
- **Performance statistics**: `/stats`
- **Standardized response format**

### Memory Management
- **Automatic cleanup**: Memory management utilities in base class
- **Resource monitoring**: Health check and statistics tracking
- **Graceful shutdown**: Proper resource cleanup on exit

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd src/models/specific_model/
   python run_model.py
   ```

2. **Port Conflicts**
   ```bash
   # Check if port 8080 is in use
   lsof -i :8080
   # Kill conflicting processes
   sudo lsof -ti:8080 | xargs sudo kill -9
   ```

3. **Model Loading Issues**
   ```bash
   # Check model files exist
   ls -la model_directory/
   # Verify configuration
   cat src/config/model_configs/model_name.json
   ```

### Getting Help

1. **Check model-specific README**: Each model has detailed documentation
2. **Review logs**: Check `logs/` directory for error messages
3. **Test individual components**: Use model-specific test scripts
4. **Verify configuration**: Ensure all paths and settings are correct

## 📈 Performance Monitoring

### Built-in Statistics
Each model tracks:
- **Request count**: Total number of processed requests
- **Processing time**: Average and last processing time
- **Memory usage**: Current memory consumption
- **Health status**: Model availability and status

### Monitoring Endpoints
```bash
# Health check
curl http://localhost:8080/health

# Performance statistics
curl http://localhost:8080/stats
```

## 🔄 Recent Updates

### ✅ **Code Organization (January 2025)**
- **SmolVLM**: Complete refactoring with unified server management
- **SmolVLM2**: Clean structure with dual implementation
- **All Models**: Proper package initialization with `__init__.py`
- **Import Paths**: Fixed for better compatibility

### ✅ **Documentation Improvements**
- **README Files**: Updated to reflect current implementation status
- **Structure Clarity**: Clear file organization and purpose
- **User Guidance**: Better navigation to specific model details

---

**For detailed information about specific models, please visit their respective directories and read their README.md files.**

**Last Updated**: January 2025 | **Status**: ✅ **All Models Organized & Production Ready**