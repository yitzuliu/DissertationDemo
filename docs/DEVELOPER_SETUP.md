# AI Manual Assistant - Developer Setup Guide

This guide provides step-by-step instructions for setting up the development environment for the AI Manual Assistant project. Follow these instructions carefully to ensure a proper setup.

## Prerequisites

### System Requirements
- macOS (M1/M2/M3 recommended) or Linux
- Python 3.8+ (3.10 recommended)
- 16GB RAM minimum (32GB recommended)
- 50GB free disk space
- CUDA-capable GPU (optional, but recommended)

### Required Software
- Git
- Python 3.10
- pip (latest version)
- Node.js 18+ (for frontend development)
- Docker (optional, for containerized development)

## Setup Process

### 1. Clone the Repository

```bash
# Clone the main repository
git clone https://github.com/yourusername/ai-manual-assistant.git

# Navigate to the project directory
cd ai-manual-assistant
```

### 2. Python Environment Setup

#### Option A: Using venv (Recommended)

```bash
# Create a virtual environment
python -m venv ai_vision_env

# Activate the virtual environment
# On macOS/Linux:
source ai_vision_env/bin/activate
# On Windows:
# ai_vision_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using Conda

```bash
# Create a conda environment
conda create -n ai_vision_env python=3.10

# Activate the conda environment
conda activate ai_vision_env

# Install dependencies
pip install -r requirements.txt
```

### 3. Model Setup

Each model requires specific setup steps. Follow the model-specific instructions below:

#### SmolVLM (Primary Model)

```bash
# Install llama-cpp-python with appropriate backend
pip install llama-cpp-python

# For Metal (Apple Silicon) acceleration:
CMAKE_ARGS="-DLLAMA_METAL=on" pip install --force-reinstall llama-cpp-python

# Download model weights (they will be cached automatically)
python -c "from transformers import AutoProcessor; AutoProcessor.from_pretrained('ggml-org/SmolVLM-500M-Instruct-GGUF', trust_remote_code=True)"
```

#### Phi-3 Vision

```bash
# Install required packages
pip install accelerate bitsandbytes

# Download model weights (they will be cached automatically)
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('microsoft/Phi-3-vision-128k-instruct', trust_remote_code=True)"
```

#### YOLO8

```bash
# Install ultralytics
pip install ultralytics

# Download YOLOv8 weights
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### 4. Backend Setup

```bash
# Navigate to the backend directory
cd src/backend

# Create logs directory
mkdir -p ../../logs

# Set up configuration (if not already present)
cp config_template.json ../config/app_config.json
```

### 5. Frontend Setup

```bash
# Navigate to the frontend directory
cd ../frontend

# Install http-server for local development (if needed)
npm install -g http-server
```

## Starting the Development Environment

### 1. Start the Model Server

```bash
# From the project root
source ai_vision_env/bin/activate  # If not already activated

# Start the model server based on the active model in app_config.json
python src/models/start_model_server.py
```

### 2. Start the Backend Server

```bash
# From the project root, in a new terminal
source ai_vision_env/bin/activate

# Start the FastAPI backend
python src/backend/main.py
```

### 3. Start the Frontend Server

```bash
# From the project root, in a new terminal
cd src/frontend

# Start a basic HTTP server
http-server -p 5500
```

## Testing the Setup

1. Open your web browser and navigate to `http://localhost:5500`
2. Grant camera permissions when prompted
3. You should see the camera feed and analysis results below

If you encounter any issues, check the troubleshooting section below.

## Environment Validation

To validate your environment is set up correctly, run the following test script:

```bash
# From the project root
python src/backend/utils/validate_environment.py
```

This will check:
- Python version
- Required dependencies
- Model availability
- GPU/Metal acceleration
- Network connectivity between components

## Docker Setup (Alternative)

For containerized development, Docker files are provided:

```bash
# Build and start all containers
docker-compose up --build

# Or start individual components
docker-compose up model-server
docker-compose up backend
docker-compose up frontend
```

## GPU Acceleration Setup

### NVIDIA GPUs

```bash
# Install CUDA toolkit (if not already installed)
# Visit https://developer.nvidia.com/cuda-downloads and follow instructions

# Install PyTorch with CUDA support
pip install torch==2.0.1+cu117 torchvision==0.15.2+cu117 --extra-index-url https://download.pytorch.org/whl/cu117

# Test CUDA availability
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

### Apple Silicon (M1/M2/M3)

```bash
# Install PyTorch with Metal support
pip install torch torchvision

# Enable Metal acceleration for llama-cpp
CMAKE_ARGS="-DLLAMA_METAL=on" pip install --force-reinstall llama-cpp-python

# Test Metal availability
python -c "import torch; print('MPS available:', torch.backends.mps.is_available())"
```

## Troubleshooting

### Common Issues

#### 1. Model Loading Errors

**Symptom:** `Error: Could not load model` or similar messages.

**Solution:**
```bash
# Check model cache directory
ls -la ~/.cache/huggingface/hub/

# Clear cache and re-download if needed
rm -rf ~/.cache/huggingface/hub/models--ggml-org--SmolVLM-500M-Instruct-GGUF
python -c "from transformers import AutoProcessor; AutoProcessor.from_pretrained('ggml-org/SmolVLM-500M-Instruct-GGUF', trust_remote_code=True, force_download=True)"
```

#### 2. Memory Issues

**Symptom:** `CUDA out of memory` or system crashes when loading models.

**Solution:**
- Use lower-precision models (4-bit quantization)
- Split model across CPU and GPU
- Lower batch sizes in configuration
- Close other memory-intensive applications

```bash
# Use 4-bit quantization for Phi-3 Vision
python src/models/phi3_vision/run_phi3_vision.py --bits 4
```

#### 3. Camera Access Issues

**Symptom:** Camera not working in browser.

**Solution:**
- Ensure your browser has camera permissions
- Try a different browser (Chrome recommended)
- Check if camera is being used by another application
- Use HTTPS for local development (required by some browsers)

```bash
# Generate self-signed certificate and start HTTPS server
openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout key.pem -out cert.pem
http-server -p 5500 --ssl --cert cert.pem --key key.pem
```

#### 4. API Connection Issues

**Symptom:** Frontend can't connect to backend.

**Solution:**
- Ensure backend is running on the correct port
- Check CORS settings in backend
- Verify network connectivity
- Check browser console for error messages

```bash
# Test backend connectivity
curl -X GET http://localhost:8000/health
```

## Development Workflow

### Code Style and Linting

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linter
flake8 src/

# Run type checking
mypy src/

# Format code
black src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_backend.py

# Run with coverage
pytest --cov=src
```

### Updating Dependencies

```bash
# Update all dependencies
pip install -r requirements.txt --upgrade

# Generate updated requirements file
pip freeze > requirements.txt
```

## Additional Resources

- [Architecture Documentation](./ARCHITECTURE.md)
- [API Documentation](./API.md)
- [Model Comparison Guide](./MODEL_COMPARISON.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [FAQ](./FAQ.md)

## Support and Contact

If you encounter any issues not covered by this guide, please reach out to the development team at [dev@example.com](mailto:dev@example.com) or open an issue on our GitHub repository.
