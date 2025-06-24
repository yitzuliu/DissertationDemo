# AI Manual Assistant - System Architecture

## Overview

The AI Manual Assistant is a real-time visual guidance system that uses advanced Vision-Language Models (VLMs) to provide contextual assistance for various tasks. This document outlines the complete system architecture and component interactions.

## System Components

### 1. Three-Layer Architecture

```ascii
┌─────────────────┐
│    Frontend     │ Port 5500
│  (Web Client)   │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│    Backend      │ Port 8000
│   (FastAPI)     │
└────────┬────────┘
         │ Internal API
         ▼
┌─────────────────┐
│  Model Server   │ Port 8080
│  (VLM Engine)   │
└─────────────────┘
```

### 2. Component Responsibilities

#### Frontend Layer (Port 5500)
- Camera input handling
- Real-time video streaming
- User interface and controls
- Response visualization
- Error handling and user feedback

#### Backend Layer (Port 8000)
- Request routing and load balancing
- Image preprocessing and optimization
- Model selection and switching
- Response post-processing
- Session management
- Error handling and logging

#### Model Server Layer (Port 8080)
- Model loading and initialization
- Inference execution
- Context management
- Response generation
- Model-specific optimizations

## Data Flow

### 1. Image Processing Pipeline

```ascii
Raw Image
   ↓
Preprocessing
   ↓
Quality Optimization
   ↓
Model-Specific Formatting
   ↓
Inference
   ↓
Response Generation
```

### 2. Request-Response Flow

1. **Image Capture**
   - Frontend captures camera frame
   - Performs client-side optimization
   - Sends to backend via HTTP

2. **Backend Processing**
   - Receives image data
   - Validates and preprocesses
   - Routes to appropriate model
   - Handles response formatting

3. **Model Processing**
   - Executes inference
   - Generates structured response
   - Maintains context memory

4. **Response Delivery**
   - Backend formats response
   - Sends to frontend
   - Frontend renders guidance

## Integration Points

### 1. Frontend-Backend Integration
- REST API endpoints
- WebSocket connections for real-time updates
- Error handling protocols
- Authentication/Authorization

### 2. Backend-Model Integration
- Model API interface
- Response format standardization
- Error handling and recovery
- Resource management

## Supported Models

| Model | Purpose | Input Size | Memory Req. |
|-------|---------|------------|-------------|
| SmolVLM | Primary VLM | 640x480 | 4GB |
| Phi-3 Vision | High Accuracy | 336x336 | 8GB |
| YOLO8 | Object Detection | 640x640 | 2GB |
| LLaVA | Specialized Tasks | 224x224 | 6GB |

## Configuration Management

### 1. Configuration Hierarchy
```ascii
app_config.json
   ├── global_settings
   ├── frontend_config
   ├── backend_config
   └── model_configs/
       ├── smolvlm.json
       ├── phi3_vision.json
       └── yolo8.json
```

### 2. Environment Variables
- `MODEL_SERVER_PORT`: Model server port (default: 8080)
- `BACKEND_PORT`: Backend service port (default: 8000)
- `FRONTEND_PORT`: Frontend service port (default: 5500)
- `LOG_LEVEL`: Logging verbosity
- `MODEL_TYPE`: Active model selection

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
- Horizontal scaling of model servers
- Load balancer integration
- Distributed caching
- Multi-region deployment

### 2. Feature Expansion
- Multi-model ensemble
- Advanced context management
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

## References

- [API Documentation](./API.md)
- [Model Comparison Guide](./MODEL_COMPARISON.md)
- [Developer Setup Guide](./DEVELOPER_SETUP.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [FAQ](./FAQ.md)
- [Developer Setup Guide](./DEVELOPER_SETUP.md)
- [Model Comparison Guide](./MODEL_COMPARISON.md)
