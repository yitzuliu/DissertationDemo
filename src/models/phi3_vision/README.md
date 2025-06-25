# Phi-3 Vision Model

**Microsoft's advanced Vision-Language Model implementation for the AI Manual Assistant**

## 🚀 Quick Start Commands

Complete system startup commands - execute in sequence to start the entire AI Manual Assistant system:

### 1. Environment Check
```bash
source ai_vision_env/bin/activate && python --version
# Expected output: Python 3.8+ (3.13.3 recommended)
```

### 2. Start Phi-3 Vision Model Server (Port 8080)
```bash
# Execute in first terminal - PRIMARY METHOD using uvicorn
source ai_vision_env/bin/activate && cd src/models/phi3_vision && uvicorn main:app --host 0.0.0.0 --port 8080
```
```bash
# Execute in first terminal - PRIMARY METHOD using uvicorn
source ai_vision_env_311/bin/activate && cd src/models/phi3_vision && uvicorn main:app --host 0.0.0.0 --port 8080
```

**Alternative startup methods:**
```bash
# Method 2: Using Python main.py
source ai_vision_env/bin/activate && cd src/models/phi3_vision && python main.py

# Method 3: Standalone camera application
source ai_vision_env/bin/activate && cd src/models/phi3_vision && python run_phi3_vision.py
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
# Check Phi-3 Vision server status
source ai_vision_env/bin/activate && sleep 15 && curl -s http://localhost:8080
# Expected: {"status":"AI Manual Assistant Backend (Phi-3) is running."}

# Check backend server status
curl -s http://localhost:8000
# Expected: {"message":"Vision Models Unified API","active_model":"phi3_vision","version":"1.0.0"}

# Access frontend interface
open http://localhost:5500
```

### 6. Stop All Servers
```bash
# One-command stop all services
pkill -f "uvicorn main:app" && pkill -f "python main.py" && pkill -f "http.server 5500"
```

---

## 📖 Detailed Documentation

Phi-3 Vision is Microsoft's cutting-edge multimodal language model optimized for real-time image understanding and contextual analysis. This implementation provides FastAPI-based server with comprehensive vision-language capabilities.

### System Architecture
- **Phi-3 Vision Model Server (Port 8080)** - Handles vision-language model inference using uvicorn/FastAPI
- **Backend API Server (Port 8000)** - Handles image preprocessing and API proxy
- **Frontend Web Server (Port 5500)** - Provides user interface

### Main Features
- **Advanced image understanding** - State-of-the-art vision-language processing
- **Contextual activity recognition** - Understanding user actions and workspace context
- **Structured JSON responses** - Consistent output format for integration
- **FastAPI integration** - Modern async API server with automatic documentation

### Key Features
- 🧠 **Advanced Vision Intelligence**: Microsoft's state-of-the-art Phi-3-vision-128k-instruct model
- ⚡ **FastAPI Performance**: High-performance async server with uvicorn
- 🔧 **Flexible Deployment**: Multiple startup modes (server, standalone, programmatic)
- 💾 **Memory Optimized**: Supports GPU acceleration and quantization
- 📊 **Real-time Analysis**: Low latency for interactive applications
- 🔄 **Auto Documentation**: Swagger/OpenAPI documentation built-in

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+ (3.13.3 recommended)
- GPU with CUDA support (recommended, 4GB+ VRAM)
- CPU: 8GB+ RAM (CPU mode fallback)
- Disk space: 10GB+ (model download ~8GB)
- Webcam (for standalone mode)

### Quick Setup
1. **Create Virtual Environment**:
   ```bash
   python3 -m venv ai_vision_env
   source ai_vision_env/bin/activate  # Linux/Mac
   # or
   ai_vision_env\Scripts\activate     # Windows
   ```

2. **Install Dependencies**:
   ```bash
   # Install core dependencies
   pip install torch torchvision transformers
   pip install fastapi uvicorn
   pip install pillow requests numpy
   
   # Install Phi-3 Vision specific dependencies
   pip install accelerate bitsandbytes
   ```

3. **Verify Installation**:
   ```bash
   python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
   uvicorn --version
   ```

## 📡 API Reference

### Phi3VisionModel Class
Main interface for the Phi-3 Vision model.

#### Constructor
```python
Phi3VisionModel(model_name: str, config: Dict[str, Any])
```

**Parameters:**
- `model_name`: Model instance identifier
- `config`: Configuration dictionary from `model_configs/phi3_vision.json`

**Configuration Options:**
- `model_name`: "microsoft/Phi-3-vision-128k-instruct"
- `device`: "auto" (auto-detect GPU/CPU)
- `torch_dtype`: "auto" 
- `trust_remote_code`: true
- `max_length`: 2048
- `temperature`: 0.7
- `do_sample`: true

#### Main Methods

##### `load_model() -> bool`
Initialize and load the Phi-3 Vision model.
**Returns:** True if successful, False otherwise

##### `predict(image, prompt, options=None) -> Dict[str, Any]`
Generate model predictions for image and text input.

**Parameters:**
- `image`: PIL Image, numpy array, or base64 string
- `prompt`: Text prompt for the model
- `options`: Optional parameters (temperature, max_tokens)

**Returns:** Dictionary with prediction results

##### `unload_model() -> bool`
Unload the model and free GPU/CPU memory.
**Returns:** True if successful, False otherwise

### HTTP API Endpoints (uvicorn server)

When the server is running with uvicorn, these endpoints are available:

#### Root Status
```http
GET http://localhost:8080/
```
**Response:**
```json
{"status":"AI Manual Assistant Backend (Phi-3) is running."}
```

#### Health Check
```http
GET http://localhost:8080/health
```

#### Model Information
```http
GET http://localhost:8080/model/info
```

#### Image Analysis
```http
POST http://localhost:8080/analyze
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
  "prompt": "Describe this image in detail"
}
```

#### Interactive Documentation
```http
GET http://localhost:8080/docs
# Automatic Swagger/OpenAPI documentation
```

## 🎯 Use Cases

### Workspace Analysis
```python
result = model.predict(image, """
Analyze this workspace image and respond with a JSON object containing:
- "primary_tool": The main tool being used
- "key_objects": List of important objects visible
- "user_action": Description of what the user is doing
- "is_safe": Safety assessment (true/false)
""")
```

### Step-by-Step Task Guidance
```python
result = model.predict(image, """
You are an expert manual assistant. Analyze this image and provide:
- Current assembly step
- Next recommended action
- Required tools
- Safety considerations
""")
```

### Object Detection and Context
```python
result = model.predict(image, """
Identify all objects in this image and their relationships.
Focus on tools, materials, and user interactions.
""")
```

### Safety Assessment
```python
result = model.predict(image, """
Analyze this workspace for safety hazards.
Identify potential risks and provide safety recommendations.
""")
```

## ⚙️ Configuration

### Model Configuration File
Edit `src/config/model_configs/phi3_vision.json`:
```json
{
  "model_name": "microsoft/Phi-3-vision-128k-instruct",
  "device": "auto",
  "torch_dtype": "auto",
  "trust_remote_code": true,
  "max_length": 2048,
  "temperature": 0.7,
  "do_sample": true,
  "load_in_4bit": false,
  "load_in_8bit": false
}
```

### Environment Variables
```bash
# GPU settings
export CUDA_VISIBLE_DEVICES=0

# Model cache directory
export TRANSFORMERS_CACHE=/path/to/cache

# Logging level
export LOG_LEVEL=INFO

# Debug mode
export DEBUG=1
```

### Performance Tuning

#### GPU Acceleration
```bash
# Full GPU usage (recommended)
cd src/models/phi3_vision && uvicorn main:app --host 0.0.0.0 --port 8080

# With memory optimization
python -c "
import torch
print(f'GPU available: {torch.cuda.is_available()}')
print(f'GPU count: {torch.cuda.device_count()}')
"
```

#### Memory Optimization
```python
# Enable quantization in config
{
  "load_in_4bit": true,  # Saves ~75% memory
  "load_in_8bit": true   # Saves ~50% memory (alternative)
}
```

#### uvicorn Server Options
```bash
# Development mode with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Production mode with workers
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4

# Debug mode with detailed logging
uvicorn main:app --host 0.0.0.0 --port 8080 --log-level debug
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Model Loading Failed
```bash
# Check network connection
ping huggingface.co

# Manual model download
python -c "from transformers import AutoModel; AutoModel.from_pretrained('microsoft/Phi-3-vision-128k-instruct')"

# Check disk space
df -h
```

#### 2. Out of Memory Error
```python
# Use CPU mode
config["device"] = "cpu"

# Enable quantization
config["load_in_4bit"] = True

# Reduce max length
config["max_length"] = 1024
```

#### 3. uvicorn Port Conflict
```bash
# Check port usage
lsof -i :8080
netstat -an | grep 8080

# Kill existing process
pkill -f "uvicorn main:app"
kill -9 <PID>

# Use different port
uvicorn main:app --host 0.0.0.0 --port 8081
```

#### 4. Camera Permission Issues (Standalone Mode)
- **macOS**: System Preferences → Security & Privacy → Camera
- **Windows**: Settings → Privacy → Camera
- **Linux**: Check `/dev/video0` permissions

#### 5. Dependencies Conflict
```bash
# Reinstall dependencies
pip uninstall torch transformers
pip install torch transformers --upgrade

# Clean pip cache
pip cache purge
```

### Debug Mode
```bash
# Enable detailed logging
DEBUG=1 uvicorn main:app --host 0.0.0.0 --port 8080 --log-level debug

# Check model loading
python -c "
from src.models.phi3_vision.phi3_vision_model import Phi3VisionModel
model = Phi3VisionModel('phi3_vision', {})
print(model.load_model())
"
```

### Performance Metrics

Typical performance on modern hardware:

| Hardware | Model Mode | Inference Time | Memory Usage |
|----------|------------|----------------|--------------|
| RTX 4090 | FP16 | ~500ms | 8GB VRAM |
| RTX 3080 | 4-bit | ~800ms | 4GB VRAM |
| RTX 3060 | 8-bit | ~1200ms | 6GB VRAM |
| CPU (16 cores) | FP32 | ~5-10s | 16GB RAM |

## 📊 Monitoring & Logging

### Enable Debug Logging
```python
import logging
logging.getLogger('src.models.phi3_vision').setLevel(logging.DEBUG)
```

### Health Monitoring
```python
import requests

# Check server health
health = requests.get("http://localhost:8080/health")
if health.status_code == 200:
    print("Phi-3 Vision server healthy")

# Check model status
info = requests.get("http://localhost:8080/model/info")
print(info.json())
```

### Performance Tracking
```bash
# Monitor GPU usage
nvidia-smi -l 1

# Monitor memory usage
htop

# Monitor network connections
netstat -tulpn | grep :8080

# View server logs
tail -f logs/phi3_vision.log
```

## 🎨 Customization

### Custom Prompts
Edit the structured prompt in `run_phi3_vision.py`:

**Cooking Assistant Example:**
```python
structured_prompt = """
You are an expert cooking assistant. Analyze the kitchen image.
Respond ONLY with a valid JSON object with these keys:
- "ingredients_visible": List of ingredients you can identify
- "utensils_in_use": Primary utensil the user is holding
- "current_cooking_step": What the user is doing (e.g., "chopping onions")
- "safety_notes": Any safety observations
"""
```

**Repair Assistant Example:**
```python
structured_prompt = """
You are a repair technician expert. Analyze the workspace image.
Respond ONLY with a valid JSON object containing:
- "tools_identified": List of tools visible
- "repair_item": Item being repaired
- "current_step": Current repair step
- "safety_check": Safety assessment (true/false)
- "next_action": Recommended next step
"""
```

## 📱 Mobile Implementation (Conceptual)

### iPhone Implementation Path
Running Phi-3 Vision on iPhone requires significant optimization:

#### Challenges
1. **Model Size**: 8GB model exceeds typical iOS app bundle limits
2. **Memory Constraints**: iPhone RAM limitations
3. **Performance**: Real-time inference requirements

#### Solution Steps
```swift
// 1. Model Conversion & Quantization
// Use coremltools to convert PyTorch to Core ML
// Apply aggressive quantization (4-bit/8-bit)

// 2. iOS App Development
import CoreML
import Vision

// Load converted Core ML model
let model = try Phi3VisionModel(configuration: .init())

// Create Vision request
let request = VNCoreMLRequest(model: try VNCoreMLModel(for: model.model)) { request, error in
    guard let results = request.results as? [VNCoreMLFeatureValueObservation] else { return }
    // Process results...
}

// Camera integration
let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, options: [:])
try? handler.perform([request])
```

## 🔗 Integration

This Phi-3 Vision implementation integrates with:

- **AI Manual Assistant Backend** - Via unified API interface
- **Configuration System** - Through `model_configs/phi3_vision.json`
- **Image Processing Pipeline** - Using shared preprocessing utilities
- **FastAPI Framework** - Modern async web framework with automatic documentation

## 📄 Files Overview

- **`main.py`** - FastAPI server application with uvicorn integration
- **`run_phi3_vision.py`** - Standalone camera application for development
- **`phi3_vision_model.py`** - Core model implementation
- **`utils.py`** - Utility functions and helpers
- **`requirements.txt`** - Python dependencies
- **`README.md`** - This documentation file

## 🚀 Development Tips

### One-Click Startup Script
Create `start_phi3.sh`:
```bash
#!/bin/bash
source ai_vision_env/bin/activate
cd src/models/phi3_vision
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### API Testing
```bash
# Test basic endpoint
curl http://localhost:8080/

# Test with image
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/jpeg;base64,...", "prompt": "Describe this image"}'

# Interactive API documentation
open http://localhost:8080/docs
```

## 📝 License

See [LICENSE](../../../../LICENSE) file for details.

---

For more information about the AI Manual Assistant project, see the main [documentation](../../../docs/README.md).