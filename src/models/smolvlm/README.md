# SmolVLM Model

A robust and efficient vision-language model using llama-server architecture, offering excellent reliability and performance for production deployments.

## 🎯 Model Overview

SmolVLM is an excellent alternative model in our system, providing strong performance with reliable server-based architecture. It uses llama.cpp's server implementation for robust, production-ready deployment with comprehensive testing and documentation.

## 📁 File Structure

### Server Implementation
- **`run_smolvlm.py`** - Main server launcher for manual management
- **`smolvlm_model.py`** - Core SmolVLM model implementation
- **`comprehensive_smolvlm_test.py`** - Full-featured testing suite with detailed analysis
- **`unified_smolvlm_test.py`** - Simplified testing suite for quick validation
- **`TESTING_README.md`** - Comprehensive testing documentation

### Configuration
- **`src/config/model_configs/smolvlm.json`** - Model configuration file

## 🚀 Quick Start

### Starting the Server

#### Option 1: Manual Server Management
```bash
# Activate environment
source ai_vision_env/bin/activate

# Navigate to SmolVLM directory
cd src/models/smolvlm

# Start server
python run_smolvlm.py
```

#### Option 2: Integrated Testing
```bash
# Quick testing with automatic server management
python unified_smolvlm_test.py
# Choose option 2 for quick testing

# Comprehensive testing with detailed analysis
python comprehensive_smolvlm_test.py
# Choose option 1 for full testing
```

The server runs on **port 8080** by default.

### Verifying the Server

```bash
# Health check
curl http://localhost:8080/health

# Test inference
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "SmolVLM",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "Describe this image"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }],
    "max_tokens": 150
  }'
```

## ⚙️ Configuration

### Model Configuration
Located at: `src/config/model_configs/smolvlm.json`

Key configuration options:
```json
{
  "model_name": "SmolVLM",
  "model_id": "ggml-org/SmolVLM-500M-Instruct-GGUF",
  "server": {
    "port": 8080,
    "api_endpoint": "http://localhost:8080/v1/chat/completions",
    "health_check": "http://localhost:8080/health",
    "timeout": 60
  },
  "image_processing": {
    "max_size": 512,
    "format": "JPEG",
    "quality": 90
  }
}
```

### Setting as Active Model
```bash
# Through backend API
curl -X PATCH http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"active_model": "smolvlm"}'
```

## 🔧 Technical Specifications

### Architecture
- **Base Model**: SmolVLM-500M-Instruct
- **Server**: llama.cpp with server support
- **Format**: GGUF optimized for inference
- **API**: OpenAI-compatible endpoints

### Capabilities
- **Image Understanding**: Strong visual analysis capabilities
- **Text Generation**: Coherent and contextual responses
- **Server Architecture**: Robust production deployment
- **Formats**: JPEG, PNG, WebP support with automatic resizing
- **Processing**: Up to 512px with quality optimization

### Performance Benchmarks (Latest VQA 2.0 Results - 2025-07-29)
| Metric | Score | Context |
|--------|-------|---------|
| **VQA 2.0 Accuracy** | **36.0%** | Consistent performance |
| **Simple Accuracy** | **35.0%** | Reliable results |
| **⚡ Inference Time** | **0.39s** | **Fastest in system** |
| **Memory Usage** | **+0.001GB** | **Most efficient** |
| **Loading Time** | **4.05s** | Quick startup |
| **Context Understanding** | ❌ **0%** | **Critical limitation** |
| **Reliability** | ✅ High | Server-based architecture |

## 🏗️ Implementation Details

### Server-Based Architecture
SmolVLM uses llama-server for robust deployment:

1. **Automatic Server Management**:
   ```python
   # Both test suites automatically:
   # - Start server if not running
   # - Stop server when tests complete
   # - Handle graceful shutdown on Ctrl+C
   ```

2. **Image Processing Pipeline**:
   ```python
   # Automatic resizing to max 512px for optimization
   # JPEG conversion with 90% quality
   # Base64 encoding for API transmission
   ```

3. **Health Monitoring**:
   ```python
   # Continuous server status monitoring
   # Automatic retry on connection failures
   # Performance metrics tracking
   ```

### Testing Infrastructure
SmolVLM includes comprehensive testing tools:

#### Test Suite Options
1. **Comprehensive Test** - All categories with detailed analysis
2. **Quick Test** - Basic functionality check
3. **Image Analysis Only** - Focus on image understanding
4. **Prompt Variations Only** - Test different prompt types
5. **Performance Analysis Only** - Speed and configuration testing
6. **Server Connectivity Test Only** - Network and API testing

#### Performance Monitoring
- **Inference time** for each request
- **Token usage** statistics (when available)
- **Success/failure rates**
- **Server status** monitoring

## 📊 Performance Comparison (Latest VQA 2.0 Results - 2025-07-29)

| Feature | SmolVLM-GGUF | Moondream2 | SmolVLM2-MLX | Phi-3.5-MLX |
|---------|--------------|------------|--------------|-------------|
| **VQA Accuracy** | **36.0%** | 🥇 **62.5%** | 🥈 **52.5%** | **35.0%** |
| **Simple Accuracy** | **35.0%** | 🥇 **65.0%** | 🥈 **55.0%** | **35.0%** |
| **Speed** | 🏆 **0.39s** | **8.35s** | **8.41s** | **5.29s** |
| **Memory** | 🏆 **+0.001GB** | **-0.09GB** | **+0.13GB** | **+0.05GB** |
| **Context Understanding** | ❌ **0%** | ❌ **0%** | ❌ **0%** | ❌ **0%** |
| **Architecture** | llama-server | Direct | MLX | MLX |
| **Reliability** | ✅ High | ✅ High | ✅ Good | ✅ Good |
| **Testing** | ✅ Comprehensive | ⚡ Basic | ⚡ Basic | ⚡ Basic |

### 🚨 Universal Context Understanding Crisis
**ALL MODELS have 0% true context understanding capability** - comprehensive testing reveals no model can maintain conversation memory or recall previous image information.

## 🧪 Testing and Validation

### Running Tests

#### Quick Testing
```bash
cd src/models/smolvlm/
python unified_smolvlm_test.py
# Choose option 2: Quick Test
```

#### Comprehensive Testing
```bash
cd src/models/smolvlm/
python comprehensive_smolvlm_test.py
# Choose option 1: Comprehensive Test
```

### Test Categories
1. **Server Connectivity** - API and health check validation
2. **Image Analysis** - Multiple images with various prompts
3. **Prompt Variations** - Different question types and formats
4. **Performance Analysis** - Speed and configuration testing

### Expected Performance
- **Startup time**: 30-60 seconds (model download + loading)
- **Inference time**: 2-10 seconds per image (depending on complexity)
- **Memory usage**: ~2-4GB RAM

## 🔍 Troubleshooting

### Common Issues

1. **"llama-server command not found"**
   ```bash
   # Install llama.cpp from source or binary
   # Ensure it's in your PATH
   export PATH=$PATH:/path/to/llama.cpp/build/bin
   ```

2. **"Server failed to start"**
   ```bash
   # Check if port is already in use
   lsof -i :8080
   # Kill existing process or use different port
   sudo lsof -ti:8080 | xargs sudo kill -9
   ```

3. **"No test images found"**
   ```bash
   # Create the debug directory structure
   mkdir -p src/debug/images/
   # Add test images to the directory
   ```

4. **"Memory out of error"**
   ```bash
   # The tests automatically resize images to 512px max
   # Reduce model context size if needed
   ```

### Debug Mode
Use debug option in unified test suite:
```bash
python unified_smolvlm_test.py
# Choose option 5: Debug Server Status
```

### Manual Server Management
```bash
# Start server manually
python run_smolvlm.py

# Check server status
curl http://localhost:8080/health

# Stop server (Ctrl+C in server terminal)
```

## 🎯 Use Cases

### Recommended For
- **Production deployments** - Server-based architecture provides reliability
- **Batch processing** - Efficient handling of multiple images
- **Development and testing** - Comprehensive testing infrastructure
- **Quality assurance** - Reliable performance baseline

### Example Applications
- Production image analysis services
- Batch processing of image datasets
- Quality assurance and testing frameworks
- Educational and research applications

### Integration Examples
```python
# Custom integration example
from unified_smolvlm_test import start_server, send_request, image_to_base64

# Start server
if start_server():
    # Your custom testing logic
    image_b64 = image_to_base64("your_image.jpg")
    result = send_request("Your prompt", image_b64)
    print(result)
```

## 🔧 Advanced Configuration

### Server Customization
Edit configuration variables at the top of test files:
```python
MODEL_NAME = "ggml-org/SmolVLM-500M-Instruct-GGUF"
PORT = 8080
TIMEOUT = 60
```

### Image Processing Optimization
```python
# Automatic resizing to max 512px for optimization
# JPEG conversion with 90% quality
# Base64 encoding for API transmission
```

### CI/CD Integration
```yaml
# Example GitHub Actions
- name: Test SmolVLM
  run: |
    cd src/models/smolvlm/
    python unified_smolvlm_test.py << EOF
    2
    EOF
```

## 📚 Additional Resources

- **[TESTING_README.md](./TESTING_README.md)** - Comprehensive testing documentation
- **[Model Card](https://huggingface.co/ggml-org/SmolVLM-500M-Instruct-GGUF)** - Official model documentation
- **[llama.cpp](https://github.com/ggerganov/llama.cpp)** - Server implementation
- **[System Architecture](../../docs/ARCHITECTURE.md)** - Overall system design

---

**Status**: ✅ **Production Ready** | **Recommended**: ✅ **For Reliable Deployments** | **Last Updated**: January 2025

**🛡️ Reliability Champion**: Choose SmolVLM for production deployments requiring proven server architecture and comprehensive testing.