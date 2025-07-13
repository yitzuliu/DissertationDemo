# LLaVA MLX Model

This directory contains the implementation for running the `mlx-community/llava-v1.6-mistral-7b-4bit` model, which is optimized for Apple Silicon using the MLX framework.

## ⚠️ Requirements

- **Apple Silicon (M1/M2/M3) is required.** This model will not run on other architectures.
- The `mlx-vlm` package must be installed.

## File Structure

- **`run_llava_mlx.py`**: A Flask server that provides an OpenAI-compatible API endpoint for the model.
- **`llava_mlx_model.py`**: The core model class responsible for loading the MLX model and handling inference.
- **`src/config/model_configs/llava_mlx.json`**: The configuration file for the model, server, and inference parameters.

## Quick Start

### 1. Installation
First, ensure you have the necessary packages installed.

```bash
# Activate your virtual environment
source ai_vision_env/bin/activate

# Install mlx-vlm and its dependencies
pip install mlx-vlm

# Install Flask for the server
pip install Flask
```

### 2. Run the Server
Navigate to this directory and run the server script. The script automatically loads its configuration from `src/config/model_configs/llava_mlx.json`.

```bash
# From the project root directory:
cd src/models/llava_mlx

# Run the server
python run_llava_mlx.py
```
The server will start on the host and port specified in the configuration file (default: `http://localhost:8080`).

## API Usage

You can interact with the model using the `/v1/chat/completions` endpoint.

### Example `curl` Request

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llava-mlx",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "What do you see in this image?"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }]
  }'
```
Replace the base64 string with your own image data.

### Health Check
You can check if the server is running and the model is loaded by accessing the `/health` endpoint.
```bash
curl http://localhost:8080/health
```

## Known Limitations
As noted in the project's testing documentation, this model may fail on certain types of synthetic, square images. It performs best with natural, photographic images. 