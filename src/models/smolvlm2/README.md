# SmolVLM2-500M-Video-Instruct Model

A state-of-the-art 500M parameter vision-language model with video understanding capabilities, optimized for Apple Silicon.

## 🎯 Model Overview

SmolVLM2-500M-Video-Instruct is the recommended model in our system, offering the best balance of accuracy, speed, and video understanding capabilities. It features enhanced image analysis with temporal understanding for video content.

## 📁 File Structure

The SmolVLM2 implementation follows our standard dual-approach pattern:

### Server Implementations
- **`run_smolvlm2_500m_video.py`** - Standard Flask server with MLX-VLM fallback to transformers
- **`run_smolvlm2_500m_video_optimized.py`** - Optimized version (if available)
- **`smolvlm2_500m_video.py`** - Core model implementation with BaseVisionModel interface

### Model Files Directory
- **`SmolVLM2-500M-Video-Instruct/`** - Contains the actual model files
  - `model.safetensors` - Main model weights (1.9GB)
  - `config.json` - Model configuration
  - `processor_config.json` - Image/text processor configuration
  - `tokenizer.json` - Tokenizer configuration
  - **`project_workspace/`** - Development workspace with documentation

## 🚀 Quick Start

### Starting the Server

```bash
# Activate the environment
source ai_vision_env/bin/activate

# Navigate to SmolVLM2 directory
cd src/models/smolvlm2

# Start the standard server (recommended)
python run_smolvlm2_500m_video.py
```

The server will start on **port 8080** by default.

### Verifying the Server

```bash
# Health check
curl http://localhost:8080/health

# Test inference
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "max_tokens": 150,
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "Describe this image in detail"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }]
  }'
```

## ⚙️ Configuration

### Model Configuration
Located at: `src/config/model_configs/smolvlm2_500m_video_optimized.json`

Key configuration options:
```json
{
  "model_name": "SmolVLM2-500M-Video-Instruct",
  "model_path": "./SmolVLM2-500M-Video-Instruct",
  "device": "mps",
  "max_tokens": 150,
  "timeout": 60,
  "image_processing": {
    "size": [512, 512],
    "quality": 95,
    "smart_crop": true
  }
}
```

### Setting as Active Model
```bash
# Through backend API
curl -X PATCH http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"active_model": "smolvlm2_500m_video_optimized"}'
```

## 🔧 Technical Specifications

### Model Architecture
- **Parameters**: ~500 million
- **Architecture**: SmolVLMForConditionalGeneration (Idefics3-based)
- **Vision Encoder**: SigLIP-based (512px, 16x16 patches, 12 heads)
- **Text Decoder**: SmolLM2-360M-based (960 hidden, 15 heads, 32 layers)

### Capabilities
- **Image Understanding**: Up to 2048px input, 512px processing
- **Video Processing**: Max 64 frames @ 1 FPS, 512px resolution
- **Multi-modal**: Text + image + video combinations
- **Formats**: MP4, JPEG, PNG, WebP, URLs, file paths

### Performance Benchmarks
| Metric | Score | Context |
|--------|-------|---------|
| **VQA 2.0 Accuracy** | 66.0% | Best in our system |
| **Video-MME** | 42.2 | Video understanding |
| **MLVU** | 47.3 | Long video understanding |
| **MVBench** | 39.73 | Multi-modal video tasks |
| **Inference Time** | 6.61s | Average per image |
| **Memory Usage** | 2.08GB | During inference |

## 🏗️ Implementation Details

### Server Architecture
The implementation uses a Flask server with the following components:

1. **Model Loading Strategy**:
   - Primary: MLX-VLM for Apple Silicon optimization
   - Fallback: Transformers library for cross-platform compatibility

2. **Image Processing Pipeline**:
   ```python
   # SmolVLM2 requires specific format with image token
   mlx_prompt = f"<image>\n{prompt}"
   
   # For transformers, use proper message structure
   messages = [{
       "role": "user",
       "content": [
           {"type": "image", "image": image},
           {"type": "text", "text": prompt}
       ]
   }]
   ```

3. **Memory Management**:
   - MPS cache cleanup after each inference
   - Temporary file management for MLX processing
   - Request tracking for debugging

### Integration with Base System
```python
# Follows BaseVisionModel interface
class SmolVLM2Model(BaseVisionModel):
    def load_model(self) -> bool:
        # Model loading implementation
        
    def predict(self, image, prompt, options=None):
        # Inference implementation
        
    def cleanup(self):
        # Resource cleanup
```

## 📊 Performance Comparison

| Feature | SmolVLM2-500M-Video | SmolVLM-500M | Phi-3.5-Vision |
|---------|-------------------|--------------|----------------|
| **VQA Accuracy** | 🥇 66.0% | 64.0% | 60.0% |
| **Inference Speed** | 6.61s | 5.98s | 13.61s |
| **Memory Usage** | 2.08GB | 1.58GB | 1.53GB |
| **Video Support** | ✅ Native | ❌ No | ❌ No |
| **Apple Silicon** | ✅ MLX Optimized | ✅ MLX | ✅ MLX |

## 🔍 Troubleshooting

### Common Issues

1. **Model Loading Fails**
   ```bash
   # Check if model files exist
   ls -la src/models/smolvlm2/SmolVLM2-500M-Video-Instruct/
   
   # Verify model.safetensors exists and is ~1.9GB
   ```

2. **MLX Import Error**
   ```bash
   # Install MLX-VLM
   pip install mlx-vlm
   
   # Verify MLX installation
   python -c "import mlx.core as mx; print('MLX available')"
   ```

3. **Memory Issues**
   ```bash
   # Check available memory
   python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
   ```

4. **Port Conflicts**
   ```bash
   # Check if port 8080 is in use
   lsof -i :8080
   
   # Kill processes using the port
   sudo lsof -ti:8080 | xargs sudo kill -9
   ```

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
export LOG_LEVEL=DEBUG
python run_smolvlm2_500m_video.py
```

## 🎯 Use Cases

### Recommended For
- **Production deployments** - Best accuracy/performance balance
- **Video analysis tasks** - Native video understanding
- **Real-time applications** - Good inference speed
- **Apple Silicon systems** - MLX optimization available

### Example Applications
- Video content analysis and summarization
- Real-time camera feed processing
- Educational content analysis
- Accessibility applications (image/video descriptions)

## 🔄 Model Updates

### Switching to SmolVLM2
If currently using another model:

1. **Stop current model server**
2. **Update configuration**:
   ```bash
   # Edit src/config/app_config.json
   {
     "active_model": "smolvlm2_500m_video_optimized"
   }
   ```
3. **Start SmolVLM2 server**
4. **Restart backend** (optional - will auto-detect)

### Performance Tuning
Optimize for your use case by adjusting:
- `max_tokens`: Response length (50-300)
- `image_processing.size`: Input resolution ([384,384] to [1024,1024])
- `temperature`: Response creativity (0.1-1.0)

## 📚 Additional Resources

- **[Model Card](https://huggingface.co/HuggingFaceTB/SmolVLM2-500M-Video-Instruct)** - Official model documentation
- **[System Architecture](../../docs/ARCHITECTURE.md)** - Overall system design
- **[API Documentation](../../docs/API.md)** - Complete API reference
- **[Testing Results](./SmolVLM2-500M-Video-Instruct/project_workspace/docs/TODOLIST.md)** - Comprehensive testing documentation

---

**Status**: ✅ **Production Ready** | **Recommended**: ✅ **Yes** | **Last Updated**: January 2025
