# Moondream2 Model

A compact and efficient vision-language model optimized for speed and low memory usage, perfect for resource-constrained environments and real-time applications.

## 🎯 Model Overview

Moondream2 is the speed champion in our system, offering the fastest inference times with minimal memory usage. While it may not match the accuracy of larger models, it excels in scenarios where responsiveness and efficiency are prioritized over detailed analysis.

## 📁 File Structure

Moondream2 follows the project's standard dual-implementation pattern:

### Optimized Version (Recommended)
- **`run_moondream2_optimized.py`** - Flask server with MPS acceleration, caching, and port cleanup
- **`moondream2_optimized.py`** - Optimized model implementation with memory management
- **`moondream2_optimized.json`** - Configuration for optimized version

### Standard Version  
- **`run_moondream2.py`** - FastAPI server for maximum compatibility
- **`moondream2_model.py`** - Standard model implementation
- **`moondream2.json`** - Configuration for standard version

## 🚀 Quick Start

### Starting the Server

#### Optimized Version (Better Performance)
```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Navigate to Moondream2 directory
cd src/models/moondream2

# Run optimized server
python run_moondream2_optimized.py
```

#### Standard Version (Better Compatibility)
```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Run standard server
python run_moondream2.py
```

Both servers run on **port 8080** by default.

### Verifying the Server

```bash
# Health check
curl http://localhost:8080/health

# Test inference
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Moondream2",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "What do you see in this image?"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }],
    "max_tokens": 100
  }'
```

## ⚙️ Configuration

### Model Configurations

#### Optimized Version (`moondream2_optimized.json`)
```json
{
  "model_name": "Moondream2-Optimized",
  "model_path": "vikhyatk/moondream2",
  "device": "mps",
  "max_tokens": 100,
  "performance": {
    "mps_acceleration": true,
    "image_caching": true,
    "memory_management": true,
    "special_api": true
  }
}
```

#### Standard Version (`moondream2.json`)
```json
{
  "model_name": "Moondream2",
  "model_path": "vikhyatk/moondream2",
  "device": "mps",
  "max_tokens": 100,
  "server": {
    "framework": "fastapi",
    "cors_enabled": true
  }
}
```

### Setting as Active Model
```bash
# Through backend API
curl -X PATCH http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"active_model": "moondream2_optimized"}'
```

## 🔧 Technical Specifications

### Model Architecture
- **Base Model**: vikhyatk/moondream2
- **Size**: Compact (~2B parameters)
- **Vision Encoder**: Optimized for efficiency
- **Text Decoder**: Lightweight language model

### Capabilities
- **Image Understanding**: Efficient visual analysis
- **Fast Inference**: Optimized for speed
- **Low Memory**: Minimal resource requirements
- **Formats**: JPEG, PNG, WebP support
- **Resolution**: Optimized for 384x384 processing

### Performance Benchmarks
| Metric | Score | Context |
|--------|-------|---------|
| **VQA 2.0 Accuracy** | 56.0% | Good for size |
| **Inference Time** | 🏆 4.06s | Fastest in system |
| **Memory Usage** | 🏆 0.10GB | Most efficient |
| **Loading Time** | ~6-7s | Quick startup |

## 🏗️ Implementation Details

### Moondream2 Special API
Moondream2 uses a unique two-step inference process:

1. **Image Encoding**:
   ```python
   enc_image = model.encode_image(image)
   ```

2. **Question Answering**:
   ```python
   response = model.answer_question(enc_image, prompt, tokenizer)
   ```

Both implementations handle this API automatically and provide OpenAI-compatible endpoints.

### Server Architectures

#### Optimized Flask Server
- **MPS acceleration** for Apple Silicon
- **Image preprocessing cache** for repeated queries
- **Response caching** for performance
- **Memory optimization** with smart cleanup
- **Automatic port 8080 cleanup** on startup
- **Process detection and termination**

#### Standard FastAPI Server
- **Maximum compatibility** across platforms
- **Full async support**
- **Standard memory management**
- **Comprehensive error handling**

### Memory Management
```python
# Optimized version includes
- MPS cache cleanup after inference
- Temporary file management
- Memory usage monitoring
- Automatic garbage collection
```

## 📊 Performance Comparison

| Feature | Optimized | Standard | Notes |
|---------|-----------|----------|--------|
| **Load Time** | ~6.2s | ~7.0s | Optimized is faster |
| **Inference Time** | ~5.5s | ~6.5s | Optimized uses caching |
| **Memory Usage** | Lower | Standard | Half precision vs float32 |
| **Server Type** | Flask | FastAPI | Different frameworks |
| **Caching** | ✅ Yes | ❌ No | Performance boost |
| **Port Cleanup** | ✅ Auto | ❌ Manual | Convenience feature |

## 🎯 Use Cases

### Recommended For
- **Real-time applications** - Fastest inference in our system
- **Resource-constrained environments** - Minimal memory usage
- **High-volume processing** - Efficient batch processing
- **Embedded systems** - Lightweight deployment
- **Development and testing** - Quick iterations

### Example Applications
- Real-time camera feed analysis
- Mobile and edge device deployment
- High-throughput image processing pipelines
- Development and prototyping
- Baseline performance testing

### Not Ideal For
- **Detailed analysis requirements** - Consider SmolVLM2 or Phi-3.5-Vision
- **High accuracy needs** - Accuracy is good but not best-in-class
- **Complex reasoning tasks** - Better suited for simple Q&A

## 🔍 Troubleshooting

### Common Issues

1. **Port 8080 Already in Use**
   ```bash
   # Optimized version handles this automatically
   # For standard version:
   lsof -i :8080
   sudo lsof -ti:8080 | xargs sudo kill -9
   ```

2. **Model Import Issues**
   ```bash
   # Check if model files are accessible
   python -c "from transformers import AutoModelForCausalLM; print('Model accessible')"
   ```

3. **MPS Not Available**
   ```bash
   # Check MPS support
   python -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
   ```

4. **Memory Issues**
   ```bash
   # Moondream2 should work even on limited memory
   # If issues persist, check system resources
   ```

### Debug Mode
Enable verbose logging:
```bash
export LOG_LEVEL=DEBUG
python run_moondream2_optimized.py
```

## 🔧 Advanced Configuration

### Performance Tuning

#### For Speed Priority
```json
{
  "image_processing": {
    "size": [256, 256],
    "quality": 85
  },
  "generation_config": {
    "max_new_tokens": 50,
    "do_sample": false
  }
}
```

#### For Quality Priority
```json
{
  "image_processing": {
    "size": [384, 384],
    "quality": 95
  },
  "generation_config": {
    "max_new_tokens": 150,
    "temperature": 0.7
  }
}
```

### Optimized Version Features
- **Image Caching**: Repeated images processed faster
- **Response Caching**: Common queries cached
- **Memory Monitoring**: Automatic cleanup
- **Port Management**: Automatic conflict resolution

## 📈 Performance Metrics

### Benchmark Results (Apple M3 MacBook Air)
- **Cold Start**: 6.2s (optimized) / 7.0s (standard)
- **Warm Inference**: 4.06s average
- **Memory Peak**: ~0.10GB during inference
- **Throughput**: ~15 images/minute
- **Cache Hit Benefit**: ~30% speed improvement

### Comparison with Other Models