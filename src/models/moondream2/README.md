# Moondream2 Model

A compact vision language model with strong performance on visual question answering tasks.

## File Structure

Moondream2 follows the project's standard dual-implementation pattern:

### Optimized Version (Recommended)
- **`run_moondream2_optimized.py`** - Flask server with performance optimizations
- **`moondream2_optimized.py`** - Optimized model implementation with MPS acceleration and caching
- **`moondream2_optimized.json`** - Configuration for optimized version

### Standard Version  
- **`run_moondream2.py`** - FastAPI server for maximum compatibility
- **`moondream2_model.py`** - Standard model implementation without optimizations
- **`moondream2.json`** - Configuration for standard version

## Quick Start

### Optimized Version (Better Performance)
```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Run optimized server
cd src/models/moondream2
python run_moondream2_optimized.py
```

### Standard Version (Better Compatibility)
```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Run standard server
cd src/models/moondream2
python run_moondream2.py
```

Both servers run on **port 8080** by default.

## API Endpoints

### Health Check
```bash
curl http://localhost:8080/health
```

### Chat Completion
```bash
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

## Performance Comparison

| Version | Load Time | Inference Time | Memory Usage | Features |
|---------|-----------|----------------|--------------|----------|
| **Optimized** | ~6.2s | ~5.5s | Lower | MPS acceleration, caching, half precision |
| **Standard** | ~7.0s | ~6.5s | Standard | Maximum compatibility, float32 |

## Configuration Options

### Optimized Version (`moondream2_optimized.json`)
- **MPS acceleration** enabled
- **Half precision** (float16) for better performance
- **Image caching** for repeated queries
- **Memory optimization** with smart cleanup

### Standard Version (`moondream2.json`)
- **Full precision** (float32) for accuracy
- **FastAPI server** with full async support
- **Standard memory management**
- **Maximum compatibility**

## Moondream2 API Specifics

Moondream2 uses a unique two-step API:
1. **`encode_image(image)`** - Encode image to embeddings
2. **`answer_question(embeddings, prompt, tokenizer)`** - Generate response

Both implementations handle this automatically and provide OpenAI-compatible endpoints.

## Device Support

- **macOS**: MPS (Apple Silicon) acceleration
- **Linux/Windows**: CUDA support (when available)
- **CPU**: Fallback support

## Memory Requirements

- **Optimized**: ~3-4 GB RAM
- **Standard**: ~4-5 GB RAM

## Troubleshooting

### Import Issues
Both versions include fallback import strategies to handle path resolution issues.

### Memory Issues
```bash
# Check available memory
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

### Port Conflicts
If port 8080 is in use, modify the port in the respective configuration file or use:
```bash
python run_moondream2_optimized.py --port 8081
```

## Model Information

- **Model**: vikhyatk/moondream2
- **Type**: Vision Language Model
- **Architecture**: Image encoder + Language model
- **Input**: Images + Text prompts
- **Output**: Natural language responses

## Integration

Both versions integrate with the project's unified model architecture:
- Inherit from `BaseVisionModel`
- Use standardized image preprocessing
- Provide consistent API responses
- Support the VLMFactory pattern 