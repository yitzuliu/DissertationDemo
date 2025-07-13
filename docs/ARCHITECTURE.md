# AI Manual Assistant - System Architecture

## Overview

The AI Manual Assistant is a real-time visual guidance system that uses advanced Vision-Language Models (VLMs) to provide contextual assistance for hands-on tasks. The architecture is designed to be modular and flexible, allowing different VLMs to be swapped in and out to test their performance and capabilities for various use cases.

## System Components

### 1. Three-Layer Architecture

```ascii
┌─────────────────┐
│    Frontend     │ Port 5500
│  (Web Client)   │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│    Backend      │ Port 8000
│   (API Gateway) │
└────────┬────────┘
         │ Model API Call
         ▼
┌─────────────────┐
│  Model Server   │ Port 8080
│ (Standalone VLM)│
└─────────────────┘
```

### 2. Component Responsibilities

#### Frontend Layer (Port 5500)
- **Camera Interface**: Captures and displays the real-time video stream.
- **Image Capture**: Periodically sends still frames from the video to the backend.
- **User Interaction**: Manages user prompts and displays the AI's guidance.
- **Responsive UI**: Renders the conversation and guidance in a clear, interactive format.

#### Backend Layer (Port 8000)
- **API Gateway**: Provides a single, stable endpoint for the frontend.
- **Image Preprocessing**: Enhances and standardizes images before sending them to the model.
- **Model Routing**: Forwards requests to the currently active model server (running on port 8080).
- **Session Management**: Can be extended to manage conversation history and context.

#### Model Server Layer (Port 8080)
- **Standalone Model**: Each supported VLM runs as a separate, standalone web server.
- **OpenAI-Compatible API**: Exposes a `/v1/chat/completions` endpoint for easy integration with the backend.
- **Resource Management**: Encapsulates the memory and compute resources for a single model.
- **Flexibility**: To switch models, the user stops the current model server and starts another.

## Data Flow

The data flow is a straightforward request-response cycle for image analysis.

1.  **Frame Capture (Frontend)**: The web client captures a frame from the user's webcam and encodes it as a base64 string.
2.  **API Request (Frontend -> Backend)**: The frame, along with a text prompt, is sent to the backend's API endpoint (e.g., `/api/v1/chat`).
3.  **Preprocessing & Routing (Backend)**: The backend receives the request, preprocesses the image if necessary, and forwards it to the model server's API endpoint (`http://localhost:8080/v1/chat/completions`).
4.  **Inference (Model Server)**: The active VLM processes the image and prompt and generates a text response.
5.  **Response Delivery (Model -> Backend -> Frontend)**: The response travels back through the backend to the frontend, where it is displayed to the user.

This architecture decouples the core application logic from the AI models, allowing for independent development and testing.

## Supported Models

The system supports a variety of models, each with its own strengths. Models optimized with MLX are recommended for users on Apple Silicon for significantly better performance.

| Model | Key Strengths | Recommended Use Case |
|-----------------------------|--------------------------------------------|---------------------------------|
| **LLaVA-v1.6 (MLX)** | Excellent conversational ability | Multi-turn, interactive guidance for photographic images. Fails on synthetic images. |
| **Phi-3.5-Vision (MLX)** | High accuracy, strong reasoning | Detailed single-image analysis |
| **Moondream2** | Extremely fast and lightweight | Quick, general-purpose analysis |
| **SmolVLM / SmolVLM2** | Efficient and balanced performance | Reliable, all-around use |
| **YOLOv8** | Specialized for object detection | High-speed object localization |

## Configuration Management

### 1. Configuration Hierarchy

The system uses a centralized configuration approach.

```ascii
/src
├── config/
│   ├── app_config.json        # Main backend settings (e.g., model server URL)
│   └── model_configs/
│       ├── llava_mlx.json     # Config for LLaVA MLX model
│       ├── moondream2.json    # Config for Moondream2 model
│       └── ... (etc.)
└── models/
    └── [model_name]/
        └── run_[model_name].py # This script loads the corresponding config
```

- **`app_config.json`**: Configures the main backend, telling it where to find the active model server.
- **`model_configs/*.json`**: Each file contains the specific parameters for a single model, such as its Hugging Face ID, inference settings, and server port.
- **`run_*.py` Scripts**: Each model's server script is responsible for loading its own configuration file from `model_configs`.

### 2. Environment Variables
While JSON files are primary, the system can be enhanced to allow environment variables to override settings for flexible deployment.
- `MODEL_SERVER_URL`: URL of the active model server (e.g., `http://localhost:8080`)
- `LOG_LEVEL`: Logging verbosity.

## Error Handling

### 1. Error Categories
- Network connectivity issues
- Model loading failures
- Inference errors
- Resource constraints
- Client-side errors

### 2. Recovery Mechanisms
- Automatic model fallback
- Connection retry logic
- Resource cleanup
- User notification system

## Performance Considerations

### 1. Optimization Strategies
- Image quality adaptation
- Model quantization
- Response caching
- Load balancing

### 2. Resource Management
- Memory usage monitoring
- GPU utilization optimization
- Connection pooling
- Cache management

## Security Measures

### 1. Data Protection
- Input validation
- Output sanitization
- Rate limiting
- Access control

### 2. System Security
- API authentication
- CORS policies
- Input size limits
- Resource quotas

## Monitoring and Logging

### 1. System Metrics
- Response times
- Model performance
- Resource utilization
- Error rates

### 2. Logging Strategy
- Structured logging
- Log levels
- Error tracking
- Performance monitoring

## Deployment Architecture

### 1. Development Environment
```ascii
Local Development
   ├── Frontend (localhost:5500)
   ├── Backend (localhost:8000)
   └── Model Server (localhost:8080)
```

### 2. Production Environment
```ascii
Production Deployment
   ├── Frontend (Nginx/Static Hosting)
   ├── Backend (FastAPI/Gunicorn)
   └── Model Server (Docker Container)
```

## Future Considerations

### 1. Scalability
- Optimized model switching
- Faster model loading/unloading
- Distributed caching
- Multi-region deployment

### 2. Feature Expansion
- Advanced model switching automation
- Enhanced context management
- Offline mode support
- Mobile optimization

## Component Diagrams

### Image Processing Pipeline
```ascii
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  Raw Image    │─────▶│ Preprocessing │─────▶│ Enhancement   │
└───────────────┘      └───────────────┘      └───────┬───────┘
                                                     │
┌───────────────┐      ┌───────────────┐      ┌──────▼────────┐
│    Result     │◀─────│ VLM Inference │◀─────│ Model Format  │
└───────────────┘      └───────────────┘      └───────────────┘
```

### Error Handling Flow
```ascii
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ Error Occurs  │─────▶│   Logging     │─────▶│ Notification  │
└───────┬───────┘      └───────────────┘      └───────────────┘
        │
        │              ┌───────────────┐      ┌───────────────┐
        └─────────────▶│ Recovery Plan │─────▶│   Fallback    │
                       └───────────────┘      └───────────────┘
```

## Architecture Constraints

**Memory Management:** The system is designed around single-model operation to ensure optimal performance and memory usage. Model switching is supported but requires stopping one model before starting another.

## References

- [API Documentation](./API.md)
- [Model Comparison Guide](./MODEL_COMPARISON.md)
- [Developer Setup Guide](./DEVELOPER_SETUP.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [FAQ](./FAQ.md)
