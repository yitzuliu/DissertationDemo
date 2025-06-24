# SmolVLM Server

This directory contains startup scripts and documentation for the SmolVLM model.

## 🚀 Quick Start

### Using Python Start Script (Recommended)

```bash
cd src/models/smolvlm
python start_server.py
```

### Direct llama-server Command

```bash
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99 --port 8080
```

## 📡 API Usage

After server startup, you can access the API at these endpoints:

- **Health Check**: `GET http://localhost:8080/health`
- **Chat Completion**: `POST http://localhost:8080/v1/chat/completions`

### Example Request

```python
import requests

response = requests.post("http://localhost:8080/v1/chat/completions", json={
    "messages": [
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "Describe this image"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
            ]
        }
    ],
    "max_tokens": 512
})
```

## 🏗️ Architecture Overview

This implementation uses a streamlined architecture:

1. **llama-server** - Handles model inference
2. **main.py** (in src/backend/) - Handles API proxy and image preprocessing
3. **start_server.py** - Convenient startup script

## 📊 System Requirements

- llama.cpp with llama-server installed
- Sufficient GPU memory (4GB+ recommended)
- Python 3.8+

## 🔄 Version History

- **v2.0** - Simplified architecture using llama-server
- **v1.0** - Complex transformers implementation (removed)

## 🛠️ Troubleshooting

### llama-server Not Found
```bash
# Check if llama-server is in PATH
which llama-server

# Or use absolute path
/path/to/llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99 --port 8080
```

### Out of Memory
```bash
# Reduce GPU layers
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 50 --port 8080

# Or use CPU only
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 0 --port 8080
```

## 📄 License

Please see the [LICENSE](LICENSE) file.