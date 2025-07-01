# SmolVLM Model

**Vision-Language Model Implementation with Enhanced Image Processing Pipeline**

## Overview

SmolVLM is our implementation of a vision-language model that combines advanced image processing with efficient inference. The model is specifically designed to handle various image analysis tasks with a focus on quality and performance.

## Image Processing Pipeline

### 1. Frontend Processing
- Initial image capture and validation
- Real-time preview with 16:9 aspect ratio
- Thumbnail generation (120x90px)
- Basic format validation and size checks

### 2. Backend Processing (`main.py`)
- Base64 image data extraction and validation
- Smart cropping and resizing
- Configurable image enhancement:
  ```json
  {
    "smart_crop": true,
    "size": [1024, 1024],
    "min_size": 512,
    "preserve_aspect_ratio": true,
    "jpeg_quality": 95,
    "optimize": true
  }
  ```

### 3. Advanced Image Enhancement
- **Noise Reduction**
  ```json
  {
    "enabled": true,
    "method": "bilateral",
    "diameter": 9,
    "sigma_color": 75,
    "sigma_space": 75
  }
  ```

- **Color Balance**
  ```json
  {
    "enabled": true,
    "method": "lab",
    "l_channel_boost": 1.2,
    "ab_channel_boost": 1.1
  }
  ```

## Model Configuration

### Default Settings
```json
{
  "model_name": "SmolVLM2-500M-Video",
  "model_id": "smolvlm2_500m_video",
  "inference": {
    "batch_size": 1,
    "expected_response_time": 10.0,
    "max_image_size": 1024
  }
}
```

## API Endpoints

### Chat Completion
```http
POST /v1/chat/completions
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
  ]
}
```

### Health Check
```http
GET /health
Response: {"status": "healthy", "active_model": "smolvlm", "timestamp": "..."}
```

## Setup and Running

### 1. Environment Setup
```bash
source ai_vision_env/bin/activate
python --version  # Should be 3.13.3
```

### 2. Start Services
```bash
# Start backend server (Port 8000)
cd src/backend && python main.py

# Start frontend server (Port 5500)
cd src/frontend && python -m http.server 5500
```

## Error Handling

The system includes robust error handling at multiple levels:

1. **Frontend**
   - Image format validation
   - Size limit checks
   - Real-time feedback

2. **Backend**
   - Type validation for image processing
   - Fallback to safe defaults
   - Comprehensive logging

3. **Model**
   - Memory management
   - Timeout handling
   - Format conversion safety

## Performance Considerations

- Image processing optimized for 1024x1024 resolution
- Automatic format conversion and validation
- Memory-efficient processing pipeline
- Graceful degradation for resource constraints

## Troubleshooting

### Common Issues

1. **Image Processing Errors**
   - Check image format and size
   - Verify base64 encoding
   - Ensure proper MIME type

2. **Performance Issues**
   - Monitor memory usage
   - Check processing logs
   - Verify configuration settings

## Monitoring

### Logging
```python
# Backend logs location
log_dir = Path(__file__).parent.parent.parent / "logs"
log_file = log_dir / f"app_{timestamp}.log"
```

### Health Monitoring
- Regular health checks
- Performance metrics logging
- Error rate tracking

## License

This project is licensed under the terms specified in the LICENSE file.

---

For more detailed technical documentation, please refer to the `docs/` directory.