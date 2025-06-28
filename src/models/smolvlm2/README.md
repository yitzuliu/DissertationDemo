# 🎬 SmolVLM2-500M-Video-Instruct Model

**Enhanced Video Understanding with Image Analysis Capabilities**

SmolVLM2-500M-Video-Instruct implementation for the AI Manual Assistant system, featuring optimized memory management for Apple Silicon and OpenAI-compatible API interface.

## 🌟 **Key Features**

- **🎯 Image Analysis**: High-quality single image understanding
- **📹 Video Capability**: Native video understanding with temporal reasoning (future enhancement)
- **🍎 Apple Silicon Optimized**: MPS acceleration with aggressive memory management
- **🔄 API Compatible**: OpenAI-compatible `/v1/chat/completions` endpoint
- **⚡ In-Process Server**: Direct transformers integration without external dependencies
- **🧠 Memory Efficient**: Advanced memory cleanup and monitoring

## 🏗️ **Architecture Overview**

### **Server Structure**
```
SmolVLM2 Server:
├── SmolVLM2Model       # Main model interface (BaseVisionModel)
├── SmolVLM2Server      # In-process model management  
├── SmolVLM2MemoryManager # MPS memory optimization
└── FastAPI Server      # OpenAI-compatible API endpoints
```

### **Key Differences from SmolVLM**
| Aspect | SmolVLM | SmolVLM2 |
|--------|---------|----------|
| **Backend** | llama-server (external) | FastAPI + transformers (in-process) |
| **Model Loading** | GGUF format | HuggingFace transformers |
| **Memory Management** | Automatic | Manual with MPS optimization |
| **Speed** | 0.4-0.9s | 3-11s (optimizable) |
| **Capabilities** | Image only | Image + Video understanding |

## 🚀 **Quick Start**

### **1. Start SmolVLM2 Server**
```bash
# Method 1: Direct script
python src/models/smolvlm2/run_smolvlm2.py

# Method 2: Module execution  
python -m src.models.smolvlm2.run_smolvlm2
```

### **2. API Usage**
```bash
# Health check
curl http://localhost:8080/health

# Image analysis
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "SmolVLM2",
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

### **3. Integration with Backend**
The model automatically integrates with the main backend when `active_model` is set to `"smolvlm2"` in `app_config.json`.

## ⚙️ **Configuration**

### **Model Configuration** (`/src/config/model_configs/smolvlm2.json`)
```json
{
  "model_name": "SmolVLM2-Video",
  "model_path": "SmolVLM2-500M-Video-Instruct",
  "device": "mps",
  "memory": {
    "required_gb": 6.0,
    "cleanup_aggressive": true,
    "max_memory_gb": 18.0
  },
  "inference": {
    "max_tokens": 150,
    "temperature": 0.7,
    "torch_dtype": "float32"
  }
}
```

### **Memory Management Settings**
- **required_gb**: Minimum memory needed for inference (6.0 GB)
- **cleanup_aggressive**: Enable aggressive memory cleanup between requests
- **max_memory_gb**: Maximum unified memory available (18.0 GB typical for M1/M2)

## 🧠 **Memory Optimization**

### **Memory Management Strategy**
```python
# Pre-inference memory check
SmolVLM2MemoryManager.check_memory_availability(required_gb=3.0)

# Post-inference cleanup
SmolVLM2MemoryManager.cleanup_memory(aggressive=True)

# MPS cache management
torch.mps.empty_cache()
```

### **Memory Usage Patterns**
- **Model Loading**: ~6.0 GB (processor + model)
- **Inference Peak**: ~8-9 GB (inputs + generation)
- **Post-Cleanup**: ~6.0 GB (model only)

## 📊 **Performance Comparison**

| Metric | SmolVLM | SmolVLM2 | Optimization Potential |
|--------|---------|----------|----------------------|
| **Inference Time** | 0.4-0.9s | 3-11s | 5-10x with optimization |
| **Memory Usage** | 4GB | 6GB | Stable |
| **Model Loading** | 2-5s | 8-15s | 2-3x with caching |
| **API Compatibility** | ✅ | ✅ | Maintained |

## 🔧 **Development & Testing**

### **Local Testing**
```bash
# Test the model directly
cd src/models/smolvlm2
python -c "
from smolvlm2_model import SmolVLM2Model
import json
from PIL import Image

config = json.load(open('../../config/model_configs/smolvlm2.json'))
model = SmolVLM2Model('SmolVLM2-Video', config)

if model.load_model():
    img = Image.open('../../debug/images/test_image.png')
    result = model.predict(img, 'Describe this image')
    print(json.dumps(result, indent=2))
"
```

### **Memory Monitoring**
```python
# Check current memory usage
import torch
current_memory = torch.mps.current_allocated_memory() / 1024**3
print(f"Current MPS memory: {current_memory:.2f} GB")
```

## 🎯 **API Endpoints**

### **GET /**
Returns server status and model information.

### **GET /health**
Health check endpoint for monitoring.

### **POST /v1/chat/completions**
OpenAI-compatible chat completions with image support.

**Request Format:**
```json
{
  "model": "SmolVLM2",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Your prompt"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }
  ],
  "max_tokens": 150,
  "temperature": 0.7
}
```

**Response Format:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant", 
        "content": "Generated response"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {"prompt_tokens": 100, "completion_tokens": 45},
  "processing_time": 3.2,
  "inference_time": 2.8
}
```

## 🚦 **Status & Roadmap**

### **Current Status** 🧪
- ✅ Basic image analysis working
- ✅ OpenAI API compatibility
- ✅ Memory management optimized
- 🔄 Performance optimization in progress
- 🔄 Video understanding capabilities (future)

### **Optimization Roadmap**
1. **Short-term** (5-10x improvement):
   - Model quantization (int8/4bit)
   - torch.compile optimization
   - Batch processing support

2. **Medium-term** (10-20x improvement):
   - TensorRT/ONNX Runtime integration
   - Async processing pipelines
   - Smart caching mechanisms

3. **Long-term** (20-50x improvement):
   - Custom inference engine
   - Hybrid architecture with SmolVLM
   - Hardware-specific optimizations

## 🔗 **Integration Points**

### **With Main Backend**
```python
# Backend automatically routes to SmolVLM2 when configured
ACTIVE_MODEL = "smolvlm2"  # Set in app_config.json

# Image preprocessing handled by backend
preprocessed_image = preprocess_image(image_url, model_type="smolvlm2")
```

### **With Frontend**
- Same API interface as SmolVLM
- Transparent switching via configuration
- Compatible with existing UI controls

## 📝 **Notes**

- **Memory Constraint**: Designed for single-model operation due to memory limits
- **Apple Silicon Only**: Optimized specifically for MPS acceleration  
- **API Compatibility**: Maintains full compatibility with SmolVLM API
- **Testing Phase**: Currently under evaluation vs SmolVLM approach

## 🤝 **Contributing**

When working with SmolVLM2:
1. Always test memory usage on different image sizes
2. Monitor MPS memory allocation during development
3. Ensure API compatibility is maintained
4. Test with various image formats and resolutions

---

**Built for the AI Manual Assistant project with ❤️ and optimized for Apple Silicon.** 