# AI Manual Assistant - API Documentation

## Overview

This document describes the API endpoints for the AI Manual Assistant system. The architecture consists of three main components: a frontend client, a backend gateway, and a standalone model server.

- **Frontend (Port 5500)**: The web client that captures images and displays results.
- **Backend API (Port 8000)**: A gateway that receives requests from the frontend and forwards them to the model server.
- **Model Server API (Port 8080)**: The core VLM inference engine, running as a separate process.

This design decouples the UI and core logic from the specific AI model being used.

## Model Performance Context

Based on our latest VQA 2.0 testing (July 19, 2025), here are the performance characteristics of supported models:

| Model | VQA Accuracy (10題) | Avg Inference Time | Memory Usage | Status |
|-------|---------------------|-------------------|--------------|--------|
| **SmolVLM2-500M-Video-Instruct** | 🏆 66.0% | 6.61s | 2.08GB | ✅ **Best Overall** |
| **SmolVLM-500M-Instruct** | 64.0% | 5.98s | 1.58GB | ✅ Excellent |
| **Moondream2** | 56.0% | 🏆 4.06s | 0.10GB | ✅ Fastest |
| **Phi-3.5-Vision (MLX)** | 60.0% | 19.02s | 1.53GB | ✅ Good |
| **LLaVA-v1.6 (MLX)** | ⚠️ 34.0% | 17.86s | 1.16GB | 🔧 Underperforming |

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
  "model": "smolvlm_v2_instruct",
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

**Performance Notes:**
- **SmolVLM2**: Expected response time ~6.61s, 66.0% VQA accuracy
- **Moondream2**: Expected response time ~4.06s, 56.0% VQA accuracy
- **LLaVA-MLX**: Expected response time ~17.86s, 34.0% VQA accuracy (not recommended)

### 2. Health Check
A simple endpoint to verify that the backend server is running.
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "active_model": "smolvlm_v2_instruct",
  "model_performance": {
    "vqa_accuracy": "66.0%",
    "avg_inference_time": "6.61s"
  }
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
  "model": "smolvlm_v2_instruct",
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

**Response:**
```json
{
  "status": "healthy",
  "model": "smolvlm_v2_instruct",
  "model_id": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct",
  "performance": {
    "vqa_accuracy": "66.0%",
    "avg_inference_time": "6.61s",
    "memory_usage": "2.08GB"
  }
}
```

## Error Responses

All API endpoints use standard HTTP status codes and return error details in a JSON format.

```json
{
  "error": "Model is not available",
  "recommended_model": "smolvlm_v2_instruct",
  "performance_comparison": {
    "current_model": "llava_mlx",
    "current_accuracy": "34.0%",
    "recommended_accuracy": "66.0%"
  }
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
import time

def analyze_image(image_path: str, prompt: str, expected_time: float = 6.61):
    """
    Analyze an image using the AI Manual Assistant API.
    
    Args:
        image_path: Path to the image file
        prompt: Text prompt for analysis
        expected_time: Expected response time based on model (default: SmolVLM2)
    
    Returns:
        API response with analysis results
    """
    url = "http://localhost:8000/api/v1/chat"
    
    # Encode the image to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "prompt": prompt,
        "image": base64_image
    }
    
    print(f"Sending request to {url}...")
    print(f"Expected response time: ~{expected_time}s")
    
    start_time = time.time()
    response = requests.post(url, headers=headers, json=payload)
    end_time = time.time()
    
    actual_time = end_time - start_time
    print(f"Actual response time: {actual_time:.2f}s")
    
    return response.json()

# Example usage with different models:
# SmolVLM2 (recommended)
result = analyze_image("photo.jpg", "What's in this image?", 6.61)
print(result)

# Moondream2 (fastest)
# result = analyze_image("photo.jpg", "What's in this image?", 4.06)
# print(result)
```

### JavaScript
```javascript
async function analyzeImage(imageFile, prompt) {
    const url = 'http://localhost:8000/api/v1/chat';
    
    // Convert image to base64
    const base64Image = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.readAsDataURL(imageFile);
    });
    
    const payload = {
        prompt: prompt,
        image: base64Image
    };
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });
    
    return await response.json();
}

// Example usage
const fileInput = document.getElementById('imageInput');
const prompt = "What tools do you see in this image?";

fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        try {
            const result = await analyzeImage(file, prompt);
            console.log('Analysis result:', result);
        } catch (error) {
            console.error('Error analyzing image:', error);
        }
    }
});
```

## Performance Testing API

### VQA 2.0 Testing Endpoint
```http
POST /api/v1/test/vqa
Content-Type: application/json
```

**Request Body:**
```json
{
  "questions": 10,
  "models": ["smolvlm_v2_instruct", "moondream2"],
  "verbose": true
}
```

**Response:**
```json
{
  "test_id": "vqa2_results_coco_20250719_192734",
  "results": {
    "smolvlm_v2_instruct": {
      "vqa_accuracy": 66.0,
      "avg_inference_time": 6.61,
      "total_time": 66.0
    },
    "moondream2": {
      "vqa_accuracy": 56.0,
      "avg_inference_time": 4.06,
      "total_time": 41.0
    }
  },
  "recommendations": {
    "best_overall": "smolvlm_v2_instruct",
    "fastest": "moondream2",
    "avoid": "llava_mlx"
  }
}
```

## Model Selection Guidelines

### For Production Use
1. **Primary Choice**: SmolVLM2-500M-Video-Instruct (66.0% accuracy, 6.61s)
2. **Backup Option**: SmolVLM-500M-Instruct (64.0% accuracy, 5.98s)
3. **Speed Option**: Moondream2 (56.0% accuracy, 4.06s)
4. **⚠️ Avoid**: LLaVA-MLX (34.0% accuracy, 17.86s)

### For Different Scenarios
- **Quick Analysis**: Moondream2 (~4.06s response time)
- **Detailed Analysis**: SmolVLM2 (~6.61s response time)
- **Resource-Constrained**: Moondream2 (0.10GB memory usage)

## Rate Limiting and Best Practices

### Rate Limiting
- **Default**: 10 requests per minute per client
- **Burst**: Up to 20 requests in a 5-second window
- **Model-specific**: Some models may have additional limits

### Best Practices
1. **Use appropriate models** for your use case
2. **Monitor response times** and switch models if needed
3. **Handle errors gracefully** with fallback options
4. **Cache results** when possible to reduce API calls
5. **Use health checks** to verify model availability

### Error Handling
```python
def robust_analyze_image(image_path: str, prompt: str):
    """Robust image analysis with fallback options."""
    
    # Try primary model first
    try:
        return analyze_image(image_path, prompt, 6.61)  # SmolVLM2
    except Exception as e:
        print(f"Primary model failed: {e}")
        
        # Fallback to fastest model
        try:
            return analyze_image(image_path, prompt, 4.06)  # Moondream2
        except Exception as e2:
            print(f"Fallback model also failed: {e2}")
            raise Exception("All models unavailable")
```

---

**Last Updated**: July 19, 2025  
**Test Framework**: VQA 2.0 Standard Evaluation  
**Hardware**: MacBook Air M3, 16GB RAM
