# AI Manual Assistant - API Documentation

## Overview

This document describes the API endpoints for the AI Manual Assistant system. The API is designed around a unified, OpenAI-compatible interface to provide maximum flexibility and interoperability.

The system is composed of:
1. **Backend API (Port 8000):** Acts as a smart gateway that receives requests, preprocesses data, and routes them to the appropriate model server.
2. **Model Server API (Port 8080):** The core inference engine that runs the VLM models.
3. **Frontend (Port 5500):** The web client for user interaction.

## API Endpoints

### Backend API (Port 8000)

The backend exposes a single, primary endpoint for all visual analysis tasks, adhering to the OpenAI `chat.completions` format. This allows for easy integration with a wide range of existing tools.

#### 1. Unified Chat Completions (Image and Text Analysis)
This is the main endpoint for sending image and text prompts for analysis. The backend server receives this request, performs necessary image preprocessing based on the active model, and then forwards a request to the Model Server on port 8080.

```http
POST /v1/chat/completions
Content-Type: application/json
```

**Request Body:**
```json
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
The response is passed through directly from the model server.
```json
{
  "id": "chatcmpl-123456789",
  "object": "chat.completion",
  "created": 1686579553,
  "model": "phi3_vision",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "In the image, I can see a screwdriver and several screws on a wooden surface."
      },
      "finish_reason": "stop",
      "index": 0
    }
  ],
  "usage": {
    "prompt_tokens": 85,
    "completion_tokens": 25,
    "total_tokens": 110
  }
}
```

#### 2. Model Selection
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

#### 3. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "active_model": "phi3_vision",
  "timestamp": "...",
  "version": "1.0.0"
}
```

#### 4. Configuration Retrieval
```http
GET /api/v1/config
```
Returns the complete merged configuration.

#### 5. Configuration Update
```http
PATCH /api/v1/config
```
Updates configuration values based on the request body.


### Model Server API (Port 8080)

The model server exposes an OpenAI-compatible API that the backend communicates with. It is not typically accessed directly by the end-user client.

#### 1. OpenAI-Compatible Chat Completions
```http
POST /v1/chat/completions
```
The request and response formats are identical to the backend's `chat/completions` endpoint.

#### 2. Model Server Health Check
```http
GET /health
```
(Note: This endpoint may not be implemented on all model servers.)


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

## Client Examples

### cURL
```bash
# Analyze an image using the chat completions endpoint
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Describe this image."},
          {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,'$(base64 -i my_image.jpg)'"}}
        ]
      }
    ],
    "max_tokens": 512
  }'
```

### Python
```python
import requests
import base64

def analyze_image_with_chat_api(image_path: str, prompt: str):
    url = "http://localhost:8000/v1/chat/completions"
    
    # Encode the image to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 512
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Example usage:
# result = analyze_image_with_chat_api("photo.jpg", "What's in this image?")
# print(result)
```

### JavaScript
```javascript
// Send an image for analysis using the chat completions endpoint
async function analyzeImage(imageFile, prompt) {
  const reader = new FileReader();
  reader.readAsDataURL(imageFile);
  
  return new Promise((resolve, reject) => {
    reader.onload = async () => {
      const base64Image = reader.result;

      const response = await fetch('http://localhost:8000/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [
            {
              role: 'user',
              content: [
                { type: 'text', text: prompt },
                { type: 'image_url', image_url: { url: base64Image } }
              ]
            }
          ],
          max_tokens: 512
        })
      });
      
      resolve(await response.json());
    };
    reader.onerror = (error) => reject(error);
  });
}
```

## Websocket API
The WebSocket API remains available for real-time streaming applications.
```
WebSocket URL: ws://localhost:8000/ws/analyze
```
(See original documentation for message formats)

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

## API Versioning

All API endpoints include a version number (v1) in the URL. Breaking changes will be introduced in new API versions (e.g., v2) while maintaining backward compatibility with previous versions.

## Cross-Origin Resource Sharing (CORS)

The API server has CORS enabled and allows requests from any origin for development purposes. In production, we recommend restricting allowed origins.

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
