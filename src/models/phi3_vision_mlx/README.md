# Phi-3.5-Vision MLX Model

Microsoft's Phi-3.5-Vision model optimized for Apple Silicon with MLX framework integration and transformers fallback.

## 🎯 Model Overview

Phi-3.5-Vision is a high-accuracy vision-language model that excels at detailed image analysis and reasoning tasks. While not the fastest model in our system, it provides comprehensive and accurate descriptions, making it ideal for applications requiring detailed visual understanding.

## 📁 File Structure

### Server Implementations
- **`run_phi_vision.py`** - Standard FastAPI server with MLX-VLM and transformers fallback
- **`run_phi_vision_optimized.py`** - Optimized Flask server (if available)

### Configuration Files
- **`src/config/model_configs/phi3_vision.json`** - Standard configuration
- **`src/config/model_configs/phi3_vision_optimized.json`** - Optimized configuration

## ⚠️ Known Issues

### Critical Issue: Empty Responses After First Request
**Status**: Under Investigation

**Symptoms**:
- First inference request works correctly
- Subsequent requests return empty responses
- Issue appears to be related to MLX temporary file handling

**Current Workaround**:
- Restart the model server between sessions
- Use shorter inference sessions
- Monitor logs for MLX-related errors

**Technical Details**:
- MLX temporary file cleanup timing issue
- Model state not properly reset between requests
- Request tracking shows successful processing but empty output

## 🚀 Quick Start

### Starting the Server

```bash
# Activate the environment
source ai_vision_env/bin/activate

# Navigate to Phi-3.5-Vision directory
cd src/models/phi3_vision_mlx

# Start the standard server
python run_phi_vision.py
```

The server will start on **port 8080** by default.

### Verifying the Server

```bash
# Health check
curl http://localhost:8080/health

# Test single inference (first request should work)
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "max_tokens": 100,
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "What do you see in this image?"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }]
  }'
```

## ⚙️ Configuration

### Model Configuration
Located at: `src/config/model_configs/phi3_vision.json`

Key configuration options:
```json
{
  "model_name": "Phi-3.5-Vision",
  "model_path": "mlx-community/Phi-3.5-vision-instruct-4bit",
  "device": "auto",
  "timeout": 180,
  "max_tokens": 100,
  "image_processing": {
    "size": [512, 512],
    "quality": 95,
    "preserve_aspect_ratio": true
  },
  "mlx_config": {
    "use_mlx": true,
    "quantization_bits": 4,
    "fallback_to_transformers": true
  }
}
```

### Setting as Active Model
```bash
# Through backend API
curl -X PATCH http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"active_model": "phi3_vision"}'
```

## 🔧 Technical Specifications

### Model Architecture
- **Base Model**: microsoft/Phi-3.5-vision-instruct
- **MLX Version**: mlx-community/Phi-3.5-vision-instruct-4bit
- **Quantization**: INT4 for MLX, Float16 for transformers
- **Context Length**: 2048 tokens
- **Vision Encoder**: Integrated with language model

### Capabilities
- **Image Understanding**: High-accuracy visual analysis
- **Detailed Descriptions**: Comprehensive scene analysis
- **Reasoning**: Strong logical reasoning about visual content
- **Formats**: JPEG, PNG, WebP support
- **Resolution**: Up to 1024px input

### Performance Benchmarks (Latest VQA 2.0 Results - 2025-07-29)
| Metric | Score | Context |
|--------|-------|---------|
| **VQA 2.0 Accuracy** | **35.0%** | Consistent performance |
| **Simple Accuracy** | **35.0%** | Balanced results |
| **Inference Time** | **5.29s** | Fast processing |
| **Memory Usage** | **+0.05GB** | Efficient |
| **Loading Time** | **1.71s** | Quick startup |
| **Context Understanding** | ❌ **0%** | **Critical limitation** |

## 🏗️ Implementation Details

### Dual Strategy Loading
1. **Primary: MLX-VLM**
   ```python
   from mlx_vlm import load
   self.model, self.processor = load(
       "mlx-community/Phi-3.5-vision-instruct-4bit",
       trust_remote_code=True
   )
   ```

2. **Fallback: Transformers**
   ```python
   from transformers import AutoModelForCausalLM, AutoProcessor
   self.processor = AutoProcessor.from_pretrained(
       "microsoft/Phi-3.5-vision-instruct",
       trust_remote_code=True
   )
   ```

### Image Token Format
Phi-3.5-Vision uses specific image token formatting:
```python
# MLX format
mlx_prompt = f"<|image_1|>\nUser: {prompt}\nAssistant:"

# Transformers format
messages = [{"role": "user", "content": f"<|image_1|>\n{prompt}"}]
```

### Enhanced Error Handling and Debugging
The current implementation includes:
- Request ID tracking for debugging
- Detailed logging of each processing step
- Memory cleanup after each inference
- Temporary file management for MLX

## 📊 Performance Comparison (Latest VQA 2.0 Results - 2025-07-29)

| Feature | Phi-3.5-Vision | SmolVLM2-MLX | Moondream2 | SmolVLM-GGUF |
|---------|----------------|--------------|------------|--------------|
| **VQA Accuracy** | **35.0%** | **52.5%** | **62.5%** | **36.0%** |
| **Simple Accuracy** | **35.0%** | **55.0%** | **65.0%** | **35.0%** |
| **Speed** | **5.29s** | **8.41s** | **8.35s** | **0.39s** |
| **Memory** | **+0.05GB** | **+0.13GB** | **-0.09GB** | **+0.001GB** |
| **Context Understanding** | ❌ **0%** | ❌ **0%** | ❌ **0%** | ❌ **0%** |
| **Apple Silicon** | ✅ MLX | ✅ MLX | ✅ MPS | ✅ GGUF |

### 🚨 Universal Context Understanding Crisis
**ALL MODELS have 0% true context understanding capability** - comprehensive testing reveals no model can maintain conversation memory or recall previous image information.

## 🔍 Troubleshooting

### Known Issues and Solutions

1. **Empty Responses After First Request**
   ```bash
   # Current workaround: Restart server
   # Kill existing process
   pkill -f "run_phi3_vision"
   
   # Restart server
   python run_phi3_vision.py
   ```

2. **MLX Loading Fails**
   ```bash
   # Check MLX installation
   pip install mlx-vlm>=0.0.9
   
   # Verify MLX availability
   python -c "import mlx.core as mx; print('MLX available')"
   ```

3. **Transformers Fallback Issues**
   ```bash
   # Ensure transformers version
   pip install transformers>=4.40.0
   
   # Check model download
   python -c "from transformers import AutoProcessor; AutoProcessor.from_pretrained('microsoft/Phi-3.5-vision-instruct')"
   ```

4. **Memory Issues on Apple Silicon**
   ```bash
   # Check MPS availability
   python -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
   ```

### Debug Mode
Enable enhanced debugging:
```bash
export LOG_LEVEL=DEBUG
python run_phi3_vision.py
```

Monitor logs for:
- Request ID tracking
- MLX generation steps
- Temporary file operations
- Memory cleanup operations

## 🎯 Use Cases

### Recommended For
- **Detailed image analysis** - When accuracy is more important than speed
- **Educational applications** - Comprehensive descriptions
- **Research and development** - High-quality baseline model
- **Quality benchmarking** - Reference implementation

### Not Recommended For
- **Real-time applications** - Due to slower inference speed
- **Production systems** - Until empty response issue is resolved
- **High-volume processing** - Consider faster alternatives

### Example Applications
- Educational content analysis with detailed explanations
- Research applications requiring high accuracy
- Baseline comparisons for other models
- Quality assessment tasks

## 🔧 Development Status

### Current Priorities
1. **🔴 High Priority**: Fix empty response issue after first request
2. **🟡 Medium Priority**: Optimize MLX inference speed
3. **🟢 Low Priority**: Implement response caching

### Recent Changes
- Enhanced request tracking and debugging
- Improved memory management
- Better error handling and logging
- Temporary file cleanup improvements

### Contributing
If working on Phi-3.5-Vision improvements:
1. Focus on the empty response issue
2. Test memory cleanup thoroughly
3. Monitor MLX temporary file handling
4. Ensure cross-platform compatibility

## 📚 Additional Resources

- **[Model Card](https://huggingface.co/microsoft/Phi-3.5-vision-instruct)** - Official model documentation
- **[MLX Community Model](https://huggingface.co/mlx-community/Phi-3.5-vision-instruct-4bit)** - MLX optimized version
- **[System Architecture](../../docs/ARCHITECTURE.md)** - Overall system design
- **[Known Issues Tracking](../../docs/KNOWN_ISSUES.md)** - Detailed issue documentation

---

**Status**: ⚠️ **Has Issues** | **Recommended**: ❌ **Not for Production** | **Last Updated**: January 2025

**⚠️ Important**: This model has known issues with consecutive requests. Use SmolVLM2 for production deployments.