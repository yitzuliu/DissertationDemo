# AI Manual Assistant - System Architecture

## Overview

The AI Manual Assistant is a real-time visual guidance system that uses advanced Vision-Language Models (VLMs) to provide contextual assistance for hands-on tasks. The system is currently in a testing phase, evaluating two approaches: continuous video understanding and intelligent image analysis to determine the optimal solution for reliable real-time guidance. This document outlines the complete system architecture supporting both approaches.

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
- **Dual Input Support**: Camera input for both video recording and image capture
- **Testing Interface**: Switch between video segments and intelligent image capture
- User interface and controls
- Response visualization
- Real-time guidance visualization
- Error handling and user feedback

#### Backend Layer (Port 8000)
- **Adaptive Processing**: Image or video processing based on active model
- **Model Routing**: Routes requests to the single active model (port 8080)
- Context management and history tracking
- Response post-processing and guidance formatting  
- Session management and progress tracking
- Error handling and logging

#### Model Server Layer (Port 8080)
- **Single Active Model**: One model active at a time (memory considerations)
- **Model Switching**: Support for switching between SmolVLM and SmolVLM2-Video
- **Adaptive Configuration**: Model-specific optimizations based on active model
- Response generation optimized for the currently active model

## Data Flow

### 🧪 Testing Phase: Dual Processing Approaches

### 1. Video Understanding Pipeline (Testing)

```ascii
Live Video Stream
   ↓
Segment Capture (5-10s clips)
   ↓
Temporal Analysis & Context Integration
   ↓
Video-Aware Model Processing (SmolVLM2-Video)
   ↓
Activity Understanding & Progress Tracking
   ↓
Continuous Guidance Generation
```

### 2. Intelligent Image Processing Pipeline (Current Working)

```ascii
Camera Stream
   ↓
Smart Frame Capture (1-2s intervals)
   ↓
Image Enhancement & Context Integration
   ↓
Image-Optimized Model Processing (SmolVLM)
   ↓
Context-Aware Analysis & Memory
   ↓
Contextual Guidance Generation
```

### 3. Processing Flow Comparison
1. **Image Capture**
   - Frontend captures camera frame
   - Performs client-side optimization
   - Sends to backend via HTTP
2. **Backend Processing**
   - Receives image data
   - Validates and preprocesses
   - Routes to appropriate model
   - Handles response formatting
**Video Approach (Testing):**
1. **Video Stream Capture**
   - Frontend continuously records 5-10 second segments
   - Overlapping segments maintain temporal continuity
   - Optimized for activity understanding and temporal reasoning

2. **Temporal Processing**  
   - Backend processes video segments with context history
   - Routes to SmolVLM2-Video for temporal inference
   - Maintains continuous narrative and progress tracking

**Image Approach (Current Working):**
1. **Intelligent Frame Capture**
   - Frontend captures frames at optimized intervals (1-2s)
   - Smart timing based on activity detection
   - Enhanced image preprocessing for maximum clarity

2. **Context-Enhanced Processing**
   - Backend maintains frame history and context memory
   - Routes to SmolVLM for reliable image analysis
   - Builds understanding through accumulated observations

**Both Approaches Deliver:**
3. **Context-Aware Analysis**
   - Model processing with historical context integration
   - Activity recognition and progress understanding
   - Reliable guidance generation optimized for real-time use

4. **Real-time Guidance**
   - Backend formats responses for natural interaction
   - Frontend provides seamless mentoring experience
   - User receives contextual help that feels intuitive and helpful

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
| Model | Purpose | Input Type | Memory Req. | Capability |
|-------|---------|------------|-------------|------------|
| SmolVLM2-Video | Primary Continuous Vision | Video Segments | 6GB | Temporal Understanding |
| SmolVLM | Fallback Image Analysis | Single Frame | 4GB | Fast Response |
| Phi-3 Vision | High Accuracy Analysis | Single Frame | 8GB | Detailed Recognition |
| YOLO8 | Object Detection | Single Frame | 2GB | Real-time Detection |
| LLaVA | Specialized Tasks | Single Frame | 6GB | Conversational |

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
