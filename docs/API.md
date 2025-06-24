# AI Manual Assistant - API Documentation

## Overview

This document describes the API endpoints available in the AI Manual Assistant system. The API is organized into three main components:
1. Frontend API (Port 5500)
2. Backend API (Port 8000)
3. Model Server API (Port 8080)

## API Endpoints

### Backend API (Port 8000)

#### 1. Image Analysis
```http
POST /api/v1/analyze
Content-Type: multipart/form-data

Parameters:
- image: binary (required) - The image file to analyze
- prompt: string (optional) - Custom instruction for analysis
- model: string (optional) - Specific model to use (defaults to active_model in config)
```

**Response:**
```json
{
  "analysis": {
    "objects": [
      {
        "name": "screwdriver",
        "position": "center",
        "confidence": 0.95
      },
      {
        "name": "screw",
        "position": "top-right",
        "confidence": 0.87
      }
    ],
    "scene": "Workshop table with tools",
    "guidance": "You are currently holding a Phillips screwdriver. The screw you need to tighten is located on the top-right corner of the frame.",
    "safety_concerns": []
  },
  "model_used": "smolvlm",
  "processing_time": 0.45
}
```

#### 2. OpenAI-Compatible Chat Completions
```http
POST /v1/chat/completions
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What tools do you see in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJ..."
          }
        }
      ]
    }
  ],
  "max_tokens": 512
}
```

**Response:**
```json
{
  "id": "chatcmpl-123456789",
  "object": "chat.completion",
  "created": 1686579553,
  "model": "smolvlm",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "In the image, I can see several tools: 1) A red screwdriver with a Phillips head, 2) A hammer with a black handle, 3) A measuring tape, and 4) What appears to be a pair of pliers in the background."
      },
      "finish_reason": "stop",
      "index": 0
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 42,
    "total_tokens": 67
  }
}
```

#### 3. Model Selection
```http
PUT /api/v1/config/model
Content-Type: application/json

{
  "model": "phi3_vision"
}
```

**Response:**
```json
{
  "status": "success",
  "model": "phi3_vision",
  "message": "Model switched successfully"
}
```

#### 4. Health Check
```http
GET /health

No parameters
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.2.3",
  "active_model": "smolvlm",
  "backend_uptime": 1543.2,
  "model_server_status": "connected"
}
```

#### 5. Configuration Retrieval
```http
GET /api/v1/config

No parameters
```

**Response:**
```json
{
  "active_model": "smolvlm",
  "server": {
    "host": "localhost",
    "port": 8000
  },
  "frontend": {
    "video_width": 640,
    "video_height": 480,
    "api_base_url": "http://localhost:8000"
  },
  "model_config": {
    "image_processing": {
      "size": [512, 512],
      "contrast_factor": 1.2,
      "brightness_factor": 1.05,
      "sharpness_factor": 1.3
    }
  }
}
```

#### 6. Configuration Update
```http
PATCH /api/v1/config
Content-Type: application/json

{
  "frontend": {
    "video_width": 1280,
    "video_height": 720
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Configuration updated",
  "updated_keys": ["frontend.video_width", "frontend.video_height"]
}
```

### Model Server API (Port 8080)

#### 1. OpenAI-Compatible Chat Completions
```http
POST /v1/chat/completions
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What tools do you see in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJ..."
          }
        }
      ]
    }
  ],
  "max_tokens": 512
}
```

**Response:**
Same format as the backend chat completions endpoint.

#### 2. Model Server Health Check
```http
GET /health

No parameters
```

**Response:**
```json
{
  "status": "ok",
  "model": "smolvlm",
  "version": "1.0.0",
  "uptime": 384.5,
  "gpu_memory_used": "2.1GB"
}
```

## Error Responses

All API endpoints use standard HTTP status codes and return error details in the following format:

```json
{
  "error": {
    "code": "model_not_found",
    "message": "The requested model 'invalid_model' was not found",
    "details": "Available models: smolvlm, phi3_vision, yolo8"
  }
}
```

### Common Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | invalid_request | The request was malformed or missing required parameters |
| 404 | not_found | The requested resource was not found |
| 415 | unsupported_media_type | The image format is not supported |
| 422 | unprocessable_content | The image could not be processed |
| 500 | internal_error | An internal server error occurred |
| 503 | model_unavailable | The requested model is currently unavailable |

## Rate Limiting

The API implements rate limiting to prevent abuse:

- 20 requests per minute per IP address for `/api/v1/analyze`
- 60 requests per minute per IP address for other endpoints

When rate limits are exceeded, the API returns a 429 Too Many Requests response with a Retry-After header.

## Authentication

Currently, the API does not require authentication for local development. For production deployments, token-based authentication is recommended using the Authorization header:

```http
Authorization: Bearer <api_token>
```

## Websocket API

### Real-time Analysis Stream

```
WebSocket URL: ws://localhost:8000/ws/analyze
```

**Connection Parameters:**
- `model`: (optional) Model to use for analysis
- `token`: (optional) Authentication token

**Client Messages:**
```json
{
  "type": "image",
  "data": "base64_encoded_image_data",
  "settings": {
    "prompt": "Identify tools and guide me",
    "interval": 1000
  }
}
```

**Server Messages:**
```json
{
  "type": "analysis",
  "data": {
    "objects": [...],
    "scene": "...",
    "guidance": "..."
  },
  "timestamp": 1686579553
}
```

**Control Messages:**
```json
// Pause streaming
{ "type": "control", "action": "pause" }

// Resume streaming
{ "type": "control", "action": "resume" }

// Change settings
{ 
  "type": "settings", 
  "data": { 
    "interval": 2000,
    "prompt": "New instruction"
  }
}
```

## API Versioning

All API endpoints include a version number (v1) in the URL. Breaking changes will be introduced in new API versions (e.g., v2) while maintaining backward compatibility with previous versions.

## Cross-Origin Resource Sharing (CORS)

The API server has CORS enabled and allows requests from any origin for development purposes. In production, we recommend restricting allowed origins.

## Client Examples

### cURL

```bash
# Analyze an image
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "image=@photo.jpg" \
  -F "prompt=Identify tools in this image"
```

### JavaScript

```javascript
// Send an image for analysis
async function analyzeImage(imageBlob) {
  const formData = new FormData();
  formData.append('image', imageBlob);
  formData.append('prompt', 'Identify tools in this image');
  
  const response = await fetch('http://localhost:8000/api/v1/analyze', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}
```

### Python

```python
import requests

def analyze_image(image_path, prompt=None):
    url = "http://localhost:8000/api/v1/analyze"
    
    files = {"image": open(image_path, "rb")}
    data = {}
    if prompt:
        data["prompt"] = prompt
        
    response = requests.post(url, files=files, data=data)
    return response.json()
```

## Notes for Model Developers

When implementing a new model integration, adhere to these API interfaces. The model server must implement at minimum:

1. The OpenAI-compatible chat completions endpoint
2. The health check endpoint

For detailed implementation guidelines, refer to the [Developer Setup Guide](./DEVELOPER_SETUP.md).

## Support

For API support:
- **GitHub Issues**: [Create an issue](https://github.com/yitzuliu/DissertationDemo/issues)
- **Documentation**: See [docs directory](../)
- **FAQ**: [Frequently Asked Questions](./FAQ.md)
- **Troubleshooting**: [Troubleshooting Guide](./TROUBLESHOOTING.md)
