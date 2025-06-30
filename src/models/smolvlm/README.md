# SmolVLM Model

**Fast and efficient Vision-Language Model implementation for the AI Manual Assistant**

## 🆕 Recent Updates and Improvements

### Enhanced Image Processing (June 2025)
We've implemented advanced image processing features to improve visual analysis quality:

1. **LAB Color Space Enhancement**
   - Improved color processing using LAB color space
   - Better matches human visual perception
   - Configuration:
     ```json
     "advanced_color": {
       "enabled": true,
       "lab_enhancement": true,
       "l_channel_boost": 1.2,
       "ab_channel_boost": 1.2
     }
     ```

2. **Adaptive Contrast Enhancement**
   - Smart contrast adjustment based on image characteristics
   - Different processing for dark and light images
   - Configuration:
     ```json
     "adaptive_enhancement": {
       "enabled": true,
       "auto_contrast": true,
       "dark_boost": 1.4,
       "light_boost": 1.2
     }
     ```

3. **HDR Effect Simulation**
   - Enhanced dynamic range through exposure blending
   - Better detail preservation in highlights and shadows
   - Configuration:
     ```json
     "hdr_simulation": {
       "enabled": true,
       "strength": 0.5,
       "under_exposure": 0.7,
       "over_exposure": 1.3
     }
     ```

### Key Improvements from Previous Version
- **Image Quality**: Increased maximum image size to 1024x1024 (previously 512x512)
- **Color Processing**: Added LAB color space processing for better color accuracy
- **Dynamic Range**: New HDR simulation for better detail preservation
- **Adaptive Processing**: Smart contrast enhancement based on image content
- **Performance**: Optimized image processing pipeline for local processing

### Configuration Changes
The updated configuration can be found in `src/config/model_configs/smolvlm.json`. Key changes include:
- New image processing parameters
- Enhanced quality settings
- Improved default values for better visual results

## 🚀 Quick Start Commands

Complete system startup commands - execute in sequence to start the entire AI Manual Assistant system:

### 1. Environment Check
```bash
source ai_vision_env/bin/activate && python --version
# Expected output: Python 3.13.3
```

### 2. Start SmolVLM Model Server (Port 8080)
```bash
# Execute in first terminal
source ai_vision_env/bin/activate && cd src/models/smolvlm && python -m llama_cpp.server --model ./smolvlm-instruct-v0_2-q4_k_m.gguf --port 8080 --chat_format chatml-llava --clip_model_path ./smolvlm-instruct-v0_2-mmproj-f16.gguf
```

### 3. Start Backend Server (Port 8000)
```bash
# Execute in second terminal
source ai_vision_env/bin/activate && cd src/backend && python main.py
```

### 4. Start Frontend Server (Port 5500)
```bash
# Execute in third terminal
source ai_vision_env/bin/activate && cd src/frontend && python -m http.server 5500
```

### 5. Health Check
```bash
# Check SmolVLM server status
source ai_vision_env/bin/activate && sleep 10 && curl -s http://localhost:8080/health

# Check backend server status
curl -s http://localhost:8000/status

# Access frontend interface
open http://localhost:5500
```

### 6. Stop All Servers
```bash
# One-command stop all services
pkill -f "python main.py" && pkill -f "http.server 5500" && pkill -f "llama-server"
```

---

## 📖 Detailed Documentation

SmolVLM is a lightweight vision-language model optimized for real-time image analysis and instruction generation. This implementation uses `llama-server` with OpenAI API compatibility.

### System Architecture
- **SmolVLM Model Server (Port 8080)** - Handles vision-language model inference
- **Backend API Server (Port 8000)** - Handles image preprocessing and API proxy
- **Frontend Web Server (Port 5500)** - Provides user interface

### Main Features
- **Real-time image analysis** - Fast processing for live camera feeds
- **Step-by-step guidance** - Generating detailed instructions for manual tasks
- **Object detection and description** - Identifying and describing objects in images
- **Resource efficiency** - Optimized for edge deployment with minimal memory footprint

### Key Features
- 🚀 **High Performance**: Optimized inference with llama.cpp backend
- 🔧 **Easy Integration**: OpenAI-compatible API for seamless integration
- 💾 **Memory Efficient**: Quantized models for reduced memory usage
- 🔄 **Auto-scaling**: Automatic server management and health monitoring
- 📊 **Real-time Processing**: Low latency for interactive applications

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- llama.cpp with `llama-server` installed
- Sufficient system memory (4GB+ recommended)
- GPU with CUDA support (optional but recommended)

### Quick Setup
1. **Install llama.cpp**:
   ```bash
   # Download and build llama.cpp
   git clone https://github.com/ggerganov/llama.cpp.git
   cd llama.cpp
   make llama-server
   
   # Add to PATH or use absolute path
   export PATH=$PATH:/path/to/llama.cpp
   ```

2. **Verify Installation**:
   ```bash
   which llama-server
   llama-server --help
   ```

## 📡 API Reference

### SmolVLMModel Class
Main interface for the SmolVLM model.

#### Constructor
```python
SmolVLMModel(model_name: str, config: Dict[str, Any])
```

**Parameters:**
- `model_name`: Model instance identifier
- `config`: Configuration dictionary

**Configuration Options:**
- `smolvlm_version`: Model variant (default: "ggml-org/SmolVLM-500M-Instruct-GGUF")
- `port`: Server port (default: 8080)
- `manage_server`: Auto-manage server lifecycle (default: True)
- `timeout`: Request timeout in seconds (default: 60)

#### Main Methods

##### `load_model() -> bool`
Initialize and start the model server.
**Returns:** True if successful, False otherwise

##### `predict(image, prompt, options=None) -> Dict[str, Any]`
Generate model predictions for image and text input.

**Parameters:**
- `image`: PIL Image or numpy array
- `prompt`: Text prompt for the model
- `options`: Optional parameters (temperature, max_tokens)

**Returns:** Dictionary with prediction results

##### `unload_model() -> bool`
Stop the model server and free resources.
**Returns:** True if successful, False otherwise

### HTTP API Endpoints

When the server is running, these endpoints are available:

#### Health Check
```http
GET http://localhost:8080/health
```

#### Chat Completion
```http
POST http://localhost:8080/v1/chat/completions
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Describe this image"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }
  ],
  "max_tokens": 512,
  "temperature": 0.0
}
```

## 🎯 Use Cases

### Object Detection and Description
```python
result = model.predict(image, "List all objects in this image with their positions")
# Returns detailed object descriptions and locations
```

### Step-by-Step Instructions
```python
result = model.predict(image, "How do I repair this device? Provide step-by-step instructions")
# Returns detailed repair instructions based on visual analysis
```

### Safety Assessment
```python
result = model.predict(image, "Identify any safety hazards in this workspace")
# Returns safety warnings and recommendations
```

### Progress Monitoring
```python
result = model.predict(image, "What step of the assembly process is shown here?")
# Returns current progress and next steps
```

## ⚙️ Configuration

### Model Variants
- **SmolVLM-500M-Instruct**: Fastest inference, good for real-time applications
- **SmolVLM-1.7B-Instruct**: Better accuracy, higher resource requirements

### Performance Tuning

#### GPU Configuration
```bash
# Use all GPU layers (fastest)
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99 --port 8080

# Partial GPU offload
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 20 --port 8080

# CPU only
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 0 --port 8080
```

#### Memory Optimization
```python
config = {
    "max_tokens": 256,  # Reduce output length
    "temperature": 0.0,  # More deterministic
    "timeout": 30  # Faster timeout
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. `llama-server` Not Found
```bash
# Check installation
which llama-server

# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp && make llama-server

# Add to PATH
export PATH=$PATH:/path/to/llama.cpp
```

#### 2. Out of Memory Error
```bash
# Reduce GPU layers
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 10 --port 8080

# Use CPU only
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 0 --port 8080
```

#### 3. Server Connection Failed
```python
# Check server status
import requests
response = requests.get("http://localhost:8080/health")
print(response.status_code)

# Wait for server startup
time.sleep(10)
```

#### 4. Slow Inference
- Use GPU acceleration (`-ngl 99`)
- Reduce `max_tokens` in requests
- Use smaller model variant
- Enable model quantization

### Performance Metrics

Typical performance on modern hardware (with enhanced image processing):

| Hardware | Model Size | Image Size | Processing Time | Inference Time | Total Time |
|----------|------------|------------|-----------------|----------------|------------|
| RTX 4090 | 500M | 1024x1024 | ~100ms | ~200ms | ~300ms |
| RTX 3080 | 500M | 1024x1024 | ~150ms | ~300ms | ~450ms |
| CPU (16 cores) | 500M | 1024x1024 | ~500ms | ~2s | ~2.5s |

Notes:
- Processing Time: Includes LAB color processing, HDR simulation, and adaptive enhancement
- Inference Time: Model inference only
- Total Time: Complete pipeline including all processing steps

#### Memory Usage
| Configuration | VRAM Usage | RAM Usage |
|--------------|------------|-----------|
| Full Pipeline | 2.5GB VRAM | 4GB RAM |
| CPU Only | N/A | 6GB RAM |

#### Image Processing Options Impact
| Feature | Quality Impact | Performance Impact |
|---------|---------------|-------------------|
| LAB Enhancement | High | Low (~50ms) |
| Adaptive Contrast | Medium | Very Low (~20ms) |
| HDR Simulation | High | Medium (~100ms) |

## 📊 Monitoring & Logging

### Enable Debug Logging
```python
import logging
logging.getLogger('src.models.smolvlm').setLevel(logging.DEBUG)
```

### Health Monitoring
```python
# Check server health
health = requests.get(f"http://localhost:{port}/health")
if health.status_code == 200:
    print("Server healthy")
```

### Performance Tracking
```python
# The model tracks processing time automatically
result = model.predict(image, prompt)
print(f"Processing time: {result.get('processing_time', 0):.2f}s")
```

## 📄 Files Overview

- **`smolvlm_model.py`** - Main model implementation with BaseVisionModel interface
- **`run_smolvlm.py`** - Standalone server launcher script
- **`__init__.py`** - Module exports and initialization
- **`README.md`** - This documentation file
- **`LICENSE`** - License information

## 🔗 Integration

This SmolVLM implementation integrates with:

- **AI Manual Assistant Backend** - Via the BaseVisionModel interface
- **Configuration System** - Through model_configs/smolvlm.json
- **Image Processing Pipeline** - Using shared preprocessing utilities
- **API Gateway** - Through standardized response formats

## 📝 License

See [LICENSE](LICENSE) file for details.

---

For more information about the AI Manual Assistant project, see the main [documentation](../../../docs/README.md).