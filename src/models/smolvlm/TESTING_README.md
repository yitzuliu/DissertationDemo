# SmolVLM Testing Suite

This directory contains comprehensive testing tools for the SmolVLM model using server-based architecture with llama-server.

## 📁 Test Files

### 1. `comprehensive_smolvlm_test.py`
- **Full-featured testing suite** with detailed analysis
- Server management and monitoring
- Multiple test categories:
  - Server connectivity testing
  - Image analysis with multiple prompts
  - Prompt variation testing
  - Performance analysis with different configurations
- Comprehensive error handling and statistics
- **Use for**: Detailed testing, research, development

### 2. `unified_smolvlm_test.py`
- **Simplified testing suite** for quick validation
- Clean server management
- Basic test categories:
  - Image analysis
  - Prompt variations
  - Server debugging
- **Use for**: Quick testing, daily validation, CI/CD

### 3. `run_smolvlm.py`
- **Server launcher** for manual server management
- Direct server control
- **Use for**: Running server independently

## 🚀 Prerequisites

### Required Dependencies
```bash
# Install Python requirements
pip install pillow requests

# Install llama.cpp with server support
# Follow instructions at: https://github.com/ggerganov/llama.cpp
```

### Required Files
- Ensure `llama-server` is in your PATH
- Test images should be available in `../../debug/images/`
- SmolVLM model will be downloaded automatically on first run

## 🎯 Quick Start

### Option 1: Comprehensive Testing
```bash
cd src/models/smolvlm/
python comprehensive_smolvlm_test.py
# Choose option 1 for full testing
```

### Option 2: Quick Testing
```bash
cd src/models/smolvlm/
python unified_smolvlm_test.py
# Choose option 2 for quick testing
```

### Option 3: Manual Server Management
```bash
cd src/models/smolvlm/
python run_smolvlm.py  # Start server
# In another terminal:
python unified_smolvlm_test.py  # Run tests
```

## 📊 Testing Options

### Comprehensive Test Suite
1. **Comprehensive Test** - All categories with detailed analysis
2. **Quick Test** - Basic functionality check
3. **Image Analysis Only** - Focus on image understanding
4. **Prompt Variations Only** - Test different prompt types
5. **Performance Analysis Only** - Speed and configuration testing
6. **Server Connectivity Test Only** - Network and API testing

### Unified Test Suite
1. **Comprehensive Test** - All categories
2. **Quick Test** - Basic functionality
3. **Image Analysis Only** - Image testing
4. **Prompt Variations Only** - Prompt testing
5. **Debug Server Status** - Server diagnostics

## 🔧 Configuration

### Default Settings
- **Model**: `ggml-org/SmolVLM-500M-Instruct-GGUF`
- **Port**: `8080`
- **API Endpoint**: `http://localhost:8080/v1/chat/completions`
- **Health Check**: `http://localhost:8080/health`
- **Timeout**: `60 seconds`

### Customization
Edit the configuration variables at the top of each test file:
```python
MODEL_NAME = "ggml-org/SmolVLM-500M-Instruct-GGUF"
PORT = 8080
TIMEOUT = 60
```

## 🖼️ Test Images

The tests expect images in:
```
src/debug/images/
├── IMG_0119.JPG
├── test_image.png
├── sample.jpg
└── test.jpg
```

### Image Processing
- Automatic resizing to max 512px for optimization
- JPEG conversion with 90% quality
- Base64 encoding for API transmission

## 📈 Performance Monitoring

Both test suites provide:
- **Inference time** for each request
- **Token usage** statistics (when available)
- **Success/failure rates**
- **Server status** monitoring

### Expected Performance
- **Startup time**: 30-60 seconds (model download + loading)
- **Inference time**: 2-10 seconds per image (depending on complexity)
- **Memory usage**: ~2-4GB RAM

## 🐛 Troubleshooting

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
   ```

3. **"No test images found"**
   ```bash
   # Create the debug directory structure
   mkdir -p src/debug/images/
   # Add test images to the directory
   ```

4. **"Memory out of error"**
   ```bash
   # Reduce model context size or use smaller images
   # The tests automatically resize images to 512px max
   ```

### Debug Mode
Use option 5 in unified test suite for server diagnostics:
```bash
python unified_smolvlm_test.py
# Choose option 5: Debug Server Status
```

## 🔄 Server Management

### Automatic Management
Both test suites automatically:
- Start server if not running
- Stop server when tests complete
- Handle graceful shutdown on Ctrl+C

### Manual Management
```bash
# Start server manually
python run_smolvlm.py

# Check server status
curl http://localhost:8080/health

# Stop server
# Press Ctrl+C in server terminal
```

## 📝 Example Output

```
🎯 SmolVLM Testing Suite
==================================================
🔧 Server-based architecture with llama-server

🚀 Starting SmolVLM server...
📦 Model: ggml-org/SmolVLM-500M-Instruct-GGUF
🌐 Port: 8080
✅ SmolVLM server running at http://localhost:8080

🖼️ IMAGE ANALYSIS TESTING
----------------------------------------
📸 Image 1: test_image.png
📊 Original size: (1024, 768), 245.3KB
🔄 Resized image to (512, 384)
⚡ Time: 3.45s
🤖 Response: This image shows a beautiful landscape...
📊 Tokens - Prompt: 45, Completion: 67

✅ ALL TESTS COMPLETE
📊 Server Status: Running
```

## 🤝 Integration

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

### Custom Integration
```python
from unified_smolvlm_test import start_server, send_request, image_to_base64

# Start server
if start_server():
    # Your custom testing logic
    image_b64 = image_to_base64("your_image.jpg")
    result = send_request("Your prompt", image_b64)
    print(result)
```

## 📚 Related Files

- `smolvlm_model.py` - Core SmolVLM model implementation
- `run_smolvlm.py` - Server launcher
- `README.md` - Main SmolVLM documentation
- `requirements.txt` - Python dependencies

---

**Happy Testing! 🎉** 