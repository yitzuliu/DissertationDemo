# AI Manual Assistant - API Documentation

## Overview

This document describes the API endpoints for the AI Manual Assistant system. The architecture consists of three main components: a frontend client, a backend gateway, and a standalone model server.

- **Frontend (Port 5500)**: The web client that captures images and displays results.
- **Backend API (Port 8000)**: A gateway that receives requests from the frontend and forwards them to the model server.
- **Model Server API (Port 8080)**: The core VLM inference engine, running as a separate process.

This design decouples the UI and core logic from the specific AI model being used.

## Backend API (Port 8000)

The backend exposes a single, primary endpoint for visual analysis. Its main job is to act as a stable proxy for the frontend, forwarding requests to whichever model server is currently active.

### 1. Unified Chat Completions

This is the main endpoint for sending an image and a text prompt for analysis. The backend server receives this request and forwards it to the active Model Server on port 8080.

```http
POST /api/v1/chat
Content-Type: application/json
```

**Request Body:**
The request body should contain a `prompt` and a base64-encoded `image`.
```json
{
  "prompt": "What tools do you see in this image?",
  "image": "/9j/4AAQSkZJ..."
}
```

**Response:**
The response is the direct pass-through from the model server. The format is OpenAI-compatible.
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1686579553,
  "model": "llava-mlx",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "In the image, I can see a screwdriver and several screws on a wooden surface."
      },
      "finish_reason": "stop"
    }
  ]
}
```

### 2. Health Check
A simple endpoint to verify that the backend server is running.
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Model Server API (Port 8080)

Each model runs as its own standalone server, but they all expose the same OpenAI-compatible API. This allows the backend to communicate with any model without needing to change its code.

### 1. OpenAI-Compatible Chat Completions
```http
POST /v1/chat/completions
```

**Request Body:**
```json
{
  "model": "llava-mlx",
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
  ]
}
```

**Response:**
The response format is identical to the one described in the Backend API section.

### 2. Model Server Health Check
```http
GET /health
```
Most model servers implement this endpoint to indicate that they have successfully loaded the model.

## Error Responses

All API endpoints use standard HTTP status codes and return error details in a JSON format.

```json
{
  "error": "Model is not available"
}
```

## Client Examples

### cURL

```bash
# This example calls the backend, which then calls the model server.
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Describe this image.",
    "image": "'$(base64 -i my_image.jpg)'"
  }'
```

### Python
```python
import requests
import base64

def analyze_image(image_path: str, prompt: str):
    # This function calls the backend API gateway.
    url = "http://localhost:8000/api/v1/chat"
    
    # Encode the image to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "prompt": prompt,
        "image": base64_image
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Example usage:
# result = analyze_image("photo.jpg", "What's in this image?")
# print(result)
```
