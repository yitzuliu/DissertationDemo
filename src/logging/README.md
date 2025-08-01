# Logging System - Vision Intelligence Hub

## Overview

The logging system is a core component of Vision Intelligence Hub, providing comprehensive system monitoring, visual processing tracking, user query recording, and flow tracking capabilities. The system uses unified log formats and ID tracking mechanisms to ensure all events are completely recorded and traceable.

## System Architecture

### Core Components

1. **LogManager** (`log_manager.py`) - Unified log manager
   - Provides unique ID generation functionality
   - Manages multiple types of log files
   - Unified log format and timestamps

2. **VisualLogger** (`visual_logger.py`) - Visual processing log recorder
   - Records VLM model interactions
   - Tracks image processing procedures
   - Monitors RAG system integration

3. **SystemLogger** (`system_logger.py`) - System log recorder
   - Records system lifecycle events
   - Monitors resource usage
   - Tracks API requests and errors

### Log Types

- **System Logs** (`system_YYYYMMDD.log`) - System-level events and resource monitoring
- **Visual Logs** (`visual_YYYYMMDD.log`) - VLM processing and image analysis
- **User Logs** (`user_YYYYMMDD.log`) - User queries and responses
- **Flow Tracking** (`flow_tracking_YYYYMMDD.log`) - Complete flow tracking

## Quick Start

### Basic Usage

```python
from logging.log_manager import get_log_manager
from logging.visual_logger import get_visual_logger
from logging.system_logger import get_system_logger

# Get log manager
log_manager = get_log_manager()

# Generate unique IDs
observation_id = log_manager.generate_observation_id()  # obs_1753891534519_db0775ed
query_id = log_manager.generate_query_id()            # query_1753891534519_987f9c84
request_id = log_manager.generate_request_id()        # req_1753891534519_b70f3798

# Log system events
log_manager.log_system_start("sys_001", "localhost", 8000, "smolvlm")
log_manager.log_memory_usage("sys_001", "22.1MB")
log_manager.log_endpoint_call(request_id, "POST", "/v1/chat/completions", 200, 2.31)
```

### Visual Processing Logs

```python
# Get visual log recorder
visual_logger = get_visual_logger()

# Log backend receive
visual_logger.log_backend_receive(observation_id, request_id, request_data)

# Log image processing
visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
visual_logger.log_image_processing_result(observation_id, request_id, 0.15, True, {"image_count": 1})

# Log VLM interactions
visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 25, 1)
visual_logger.log_vlm_response(observation_id, request_id, 150, 0.8, True, "smolvlm")

# Log RAG integration
visual_logger.log_rag_data_transfer(observation_id, vlm_text, True)
visual_logger.log_state_tracker_integration(observation_id, True, 0.05)
```

### System Monitoring

```python
# Get system log recorder
system_logger = get_system_logger()

# Log system startup
system_logger.log_system_startup(
    host="0.0.0.0",
    port=8000,
    model="smolvlm",
    framework="FastAPI"
)

# Log API request
system_logger.log_endpoint_call(
    method="POST",
    path="/api/process",
    status_code=200,
    duration=0.125,
    request_id="req_123456"
)

# Log error
system_logger.log_error(
    error_type="ValidationError",
    error_message="Invalid input format",
    context={"expected": "image", "received": "text"},
    request_id="req_123456"
)
```

## Log Format

### Unified Format

```
YYYY-MM-DD HH:MM:SS,mmm [INFO] [EVENT_TYPE] key1=value1 key2=value2 ...
```

### Example Logs

```
2025-07-30 17:05:34,519 [INFO] [SYSTEM_START] system_id=sys_001 host=localhost port=8000 model=smolvlm
2025-07-30 17:05:34,519 [INFO] [EYES_CAPTURE] observation_id=obs_1753891534519_db0775ed request_id=req_1753891534519_b70f3798 device=MacBook FaceTime HD resolution=1920x1080 quality=0.9 format=JPEG size=1.2MB
2025-07-30 17:05:34,519 [INFO] [USER_QUERY] query_id=query_1753891534519_987f9c84 request_id=req_1753891534519_b70f3798 question="What tools do I need?" language=en used_observation_id=obs_1753891534519_db0775ed
```

## Unique ID System

### ID Types

- **observation_id**: Visual observation event identifier (`obs_1753891534519_db0775ed`)
- **query_id**: User query identifier (`query_1753891534519_987f9c84`)
- **request_id**: API request identifier (`req_1753891534519_b70f3798`)
- **state_update_id**: State update identifier (`state_1753891534519_00ac8f4e`)
- **flow_id**: Flow tracking identifier (`flow_1753891534519_5d551d89`)

### ID Format

```
{prefix}_{timestamp}_{random_hex}
```

- `prefix`: Event type prefix
- `timestamp`: Unix timestamp (milliseconds)
- `random_hex`: 8-digit random hexadecimal string

## Features

### ✅ Core Features

- **Unified timestamp format** (`YYYY-MM-DD HH:MM:SS,mmm`)
- **Unique ID tracking mechanism** (observation_id, query_id, request_id, state_update_id, flow_id)
- **Multiple log type support** (system, visual, user, flow_tracking)
- **Structured log format** (key=value pairs)
- **Automatic log file management** (daily rotation)
- **Global instance management**
- **Complete traceability support**

### 🔍 Visual Processing Tracking

- **VLM interaction recording**: Model request/response
- **Image processing recording**: Preprocessing procedures and results
- **RAG system integration**: Data transfer recording
- **Performance metrics**: Processing time tracking
- **Error handling**: Detailed error recording

### 📊 System Monitoring

- **System lifecycle**: Startup/shutdown recording
- **Resource monitoring**: Memory, CPU usage
- **API tracking**: Request/response recording
- **Connection status**: Service connection monitoring
- **Health checks**: Component health status

### 🛡️ Security Features

- **Data sanitization**: Automatic removal of sensitive information
- **Error isolation**: Errors don't affect normal flow
- **Concurrent safety**: Support for multi-threaded/asynchronous operations
- **File rotation**: Automatic log file size management

## Testing

### Run Test Suite

```bash
# Run unified logging system tests
python src/logging/unified_test_suite.py
```

### Test Content

1. **Basic logging functions** - Test all logging methods
2. **Data sanitization** - Test sensitive data cleaning
3. **ID consistency** - Test unique ID generation and format
4. **System logger** - Test system monitoring functionality
5. **Log manager** - Test unified management functionality
6. **Concurrent logging** - Test multi-threading safety
7. **Log file check** - Verify file generation and format

### Backend Integration Tests

```bash
# Test backend VLM logging (requires VLM server)
python src/logging/test_backend_vlm_logging.py

# Test RAG logging integration
python src/logging/test_rag_logging_integration.py

# Validate backend integration
python src/logging/validate_backend_integration.py
```

## Configuration

### Log Directory

Default log directory is `logs/`, can be modified as follows:

```python
# Custom log directory
log_manager = LogManager("custom_logs")
```

### Log Levels

Supports standard log levels:
- `DEBUG` - Debug information
- `INFO` - General information
- `WARNING` - Warning information
- `ERROR` - Error information
- `CRITICAL` - Critical errors

## Troubleshooting

### Common Issues

1. **Log files not found**
   - Check if `logs/` directory exists
   - Confirm log manager is properly initialized
   - Check file permissions

2. **Log format errors**
   - Confirm timestamp format is correct
   - Check key=value format
   - Validate ID format

3. **Performance issues**
   - Check log file sizes
   - Consider enabling log rotation
   - Monitor disk space

### Debugging Tips

```python
# Enable detailed debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check log files
import os
log_files = os.listdir("logs")
print(f"Log files: {log_files}")

# View latest logs
with open("logs/visual_20250730.log", "r") as f:
    last_lines = f.readlines()[-10:]
    for line in last_lines:
        print(line.strip())
```

## Performance Optimization

### Best Practices

1. **Batch writing**: Avoid frequent small writes
2. **Asynchronous logging**: Use async methods to avoid blocking
3. **File rotation**: Regularly clean old log files
4. **Compressed storage**: Compress old logs
5. **Size monitoring**: Regularly check log file sizes

### Performance Metrics

- **Write latency**: < 1ms
- **Concurrent support**: 100+ concurrent writes
- **File size**: Auto-rotation, single file < 100MB
- **Memory usage**: < 10MB

## Integration Guide

### Integration with FastAPI

```python
from fastapi import FastAPI, Request
from logging.system_logger import initialize_system_logger
import time

app = FastAPI()
system_logger = initialize_system_logger("my_app")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        system_logger.log_endpoint_call(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration=duration,
            request_id=f"req_{int(start_time * 1000)}"
        )
        
        return response
    except Exception as e:
        system_logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={"path": str(request.url.path)},
            request_id=f"req_{int(start_time * 1000)}"
        )
        raise
```

### Integration with VLM Processing

```python
from logging.visual_logger import get_visual_logger

async def process_vlm_request(request_data, observation_id, request_id):
    visual_logger = get_visual_logger()
    
    try:
        # Log backend receive
        visual_logger.log_backend_receive(observation_id, request_id, request_data)
        
        # Process image
        visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
        # ... image processing logic ...
        visual_logger.log_image_processing_result(observation_id, request_id, 0.15, True, {})
        
        # VLM inference
        visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 25, 1)
        # ... VLM inference logic ...
        visual_logger.log_vlm_response(observation_id, request_id, 150, 0.8, True, "smolvlm")
        
        # RAG integration
        visual_logger.log_rag_data_transfer(observation_id, vlm_text, True)
        visual_logger.log_state_tracker_integration(observation_id, True, 0.05)
        
    except Exception as e:
        visual_logger.log_error(observation_id, request_id, type(e).__name__, str(e), "vlm_processing")
        raise
```

## File Structure

```
src/logging/
├── README.md                           # Main documentation (this file)
├── log_manager.py                      # Unified log manager
├── visual_logger.py                    # Visual processing log recorder
├── system_logger.py                    # System log recorder
├── unified_test_suite.py               # Unified logging system test suite
├── test_backend_vlm_logging.py         # Backend VLM logging test
├── test_rag_logging_integration.py     # RAG logging integration test
└── validate_backend_integration.py     # Backend integration validation
```

## Update Log

- **2025-Aug-01**: Integrated documentation, created unified logging system test suite, cleaned up unnecessary files, converted all content to English
- **2025-Jul-30**: Completed visual logger development and testing
- **2025-Jul-29**: Completed system logger development
- **2025-Jul-28**: Completed log manager core functionality

## Related Documents

- [Backend API Documentation](../backend/README.md)
- [Configuration System Documentation](../config/README.md)
- [State Tracker Documentation](../state_tracker/README.md)
- [RAG System Documentation](../memory/rag/README.md)