# Visual Logger (VisualLogger)

## Overview

VisualLogger is the visual processing component of the AI Manual Assistant logging system, responsible for recording all backend events related to VLM (Visual Language Model) processing.

## Main Features

### 1. Backend Receive Logging (BACKEND_RECEIVE)
Records VLM requests received by the backend:
- **Observation ID**: Unique observation event identifier
- **Request ID**: Unique request identifier
- **Request Data**: Sanitized request data (removes sensitive image content)
- **Model Information**: VLM model name being used

### 2. Image Processing Logging
Records image preprocessing process:
- **Processing Start**: `IMAGE_PROCESSING_START` - Records start time, image count, model
- **Processing Result**: `IMAGE_PROCESSING_RESULT` - Records processing time, success status, detailed information

### 3. VLM Model Interaction Logging
Records interactions with VLM models:
- **VLM Request**: `VLM_REQUEST` - Records model name, prompt length, image count
- **VLM Response**: `VLM_RESPONSE` - Records response length, processing time, success status

### 4. RAG System Data Transfer Logging (RAG_DATA_TRANSFER)
Records data transfer from VLM output to RAG system:
- **Transfer Status**: Success or failure
- **Text Length**: Length of VLM output text
- **Text Preview**: Truncated text content preview

### 5. State Tracker Integration Logging (STATE_TRACKER_INTEGRATION)
Records integration with state tracker:
- **State Update**: Whether state update was successful
- **Processing Time**: Time required for state processing

### 6. Performance Metric Logging (VISUAL_PERFORMANCE)
Records various performance metrics:
- **Total Processing Time**: Complete request processing time
- **Image Processing Time**: Image preprocessing time
- **Model Inference Time**: VLM model inference time
- **State Processing Time**: State tracker processing time

### 7. Error Handling (VISUAL_ERROR)
Records errors during visual processing:
- **Error Type**: Exception type
- **Error Message**: Detailed error message
- **Error Context**: Context where error occurred

## Usage

### Basic Usage

```python
from logging.visual_logger import get_visual_logger

# Get visual logger
visual_logger = get_visual_logger()

# Generate observation ID and request ID
observation_id = f"obs_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
request_id = f"req_{int(time.time() * 1000)}"

# Log backend receive
visual_logger.log_backend_receive(observation_id, request_id, request_data)

# Log image processing
visual_logger.log_image_processing_start(observation_id, request_id, image_count, model)
visual_logger.log_image_processing_result(observation_id, request_id, processing_time, success, details)

# Log VLM interaction
visual_logger.log_vlm_request(observation_id, request_id, model, prompt_length, image_count)
visual_logger.log_vlm_response(observation_id, request_id, response_length, processing_time, success, model)

# Log RAG data transfer
visual_logger.log_rag_data_transfer(observation_id, vlm_text, transfer_success)

# Log state tracker integration
visual_logger.log_state_tracker_integration(observation_id, state_updated, processing_time)

# Log performance metrics
visual_logger.log_performance_metric(observation_id, "total_processing_time", 1.25, "s")

# Log errors
visual_logger.log_error(observation_id, request_id, "ConnectionError", "Failed to connect", "model_server")
```

### Integration in Backend API

```python
@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: ChatCompletionRequest):
    request_start_time = time.time()
    request_id = f"req_{int(request_start_time * 1000)}"
    observation_id = f"obs_{int(request_start_time * 1000)}_{uuid.uuid4().hex[:8]}"
    
    visual_logger = get_visual_logger()
    
    try:
        # Log backend receive
        visual_logger.log_backend_receive(observation_id, request_id, {
            "model": ACTIVE_MODEL,
            "messages": request.messages,
            "max_tokens": getattr(request, 'max_tokens', None)
        })
        
        # Image processing
        visual_logger.log_image_processing_start(observation_id, request_id, image_count, ACTIVE_MODEL)
        # ... image processing logic ...
        visual_logger.log_image_processing_result(observation_id, request_id, processing_time, True, details)
        
        # VLM request
        visual_logger.log_vlm_request(observation_id, request_id, ACTIVE_MODEL, prompt_length, image_count)
        # ... VLM request logic ...
        visual_logger.log_vlm_response(observation_id, request_id, response_length, model_time, True, ACTIVE_MODEL)
        
        # RAG and state tracker integration
        visual_logger.log_rag_data_transfer(observation_id, vlm_text, True)
        visual_logger.log_state_tracker_integration(observation_id, state_updated, state_time)
        
        # Performance metrics
        total_time = time.time() - request_start_time
        visual_logger.log_performance_metric(observation_id, "total_processing_time", total_time, "s")
        
        return model_response
        
    except Exception as e:
        # Error logging
        visual_logger.log_error(observation_id, request_id, type(e).__name__, str(e), "vlm_processing")
        raise
```

## Log Format

All visual logs use a unified format, recorded to `logs/visual_YYYYMMDD.log` files:

```
2025-07-30 21:17:49,139 [INFO] [BACKEND_RECEIVE] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 data={"model": "smolvlm", "messages": [...], "max_tokens": 150}

2025-07-30 21:17:49,240 [INFO] [IMAGE_PROCESSING_START] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 image_count=1 model=smolvlm

2025-07-30 21:17:49,441 [INFO] [IMAGE_PROCESSING_RESULT] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 status=SUCCESS processing_time=0.200s image_count=1 model=smolvlm

2025-07-30 21:17:49,442 [INFO] [VLM_REQUEST] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 model=smolvlm prompt_length=45 image_count=1

2025-07-30 21:17:50,243 [INFO] [VLM_RESPONSE] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 model=smolvlm status=SUCCESS response_length=180 processing_time=0.800s

2025-07-30 21:17:50,243 [INFO] [RAG_DATA_TRANSFER] observation_id=obs_flow_1753906669 status=SUCCESS text_length=226 text_preview="I can see coffee brewing equipment..."

2025-07-30 21:17:50,294 [INFO] [STATE_TRACKER_INTEGRATION] observation_id=obs_flow_1753906669 state_updated=True processing_time=0.050s

2025-07-30 21:17:50,294 [INFO] [VISUAL_PERFORMANCE] observation_id=obs_flow_1753906669 metric=total_processing_time value=1.050s
```

## Log Event Types

- `[BACKEND_RECEIVE]`: Backend receives VLM request
- `[IMAGE_PROCESSING_START]`: Image processing starts
- `[IMAGE_PROCESSING_RESULT]`: Image processing result
- `[VLM_REQUEST]`: VLM model request
- `[VLM_RESPONSE]`: VLM model response
- `[RAG_DATA_TRANSFER]`: RAG system data transfer
- `[STATE_TRACKER_INTEGRATION]`: State tracker integration
- `[VISUAL_PERFORMANCE]`: Visual processing performance metrics
- `[VISUAL_ERROR]`: Visual processing errors

## Data Security and Privacy

### Sensitive Data Handling
1. **Image Data**: Complete base64 image data is replaced with `[IMAGE_DATA_REMOVED]`
2. **Long Text**: Text exceeding 200 characters is truncated and marked with `...`
3. **Text Preview**: Long text in RAG transfer only records first 100 character preview

### Data Sanitization Function
```python
def _sanitize_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize request data, remove sensitive or oversized content"""
    # Automatically remove image data
    # Truncate overly long text content
    # Preserve important metadata
```

## Performance Considerations

- **Asynchronous Logging**: All log recording is asynchronous, won't block main processing flow
- **Data Truncation**: Automatically truncate large data to control log file size
- **Observation ID Tracking**: Use unique observation ID to maintain consistency throughout processing flow
- **Performance Overhead**: Log recording impact on system performance < 1%

## Testing

Run test script to verify functionality:

```bash
python src/logging/test_visual_logger.py
```

Tests include:
- Basic functionality testing
- Error handling testing
- Data sanitization testing
- Performance monitoring testing
- Complete VLM flow testing

## Configuration

Visual logger automatically:
- Uses unified log manager
- Records to `logs/visual_YYYYMMDD.log` files
- Rotates log files by date
- Uses unified timestamp format

## Dependencies

- `log_manager`: Unified log manager
- `uuid`: Unique ID generation
- `json`: JSON data processing
- `time`: Timestamp and performance measurement

## Notes

1. **Observation ID Consistency**: Use same observation ID throughout VLM processing flow
2. **Data Privacy**: Sensitive data is automatically sanitized and truncated
3. **Performance Monitoring**: Record detailed performance metrics for analysis and optimization
4. **Error Tracking**: Complete error context recording for debugging
5. **Timestamp Precision**: Use millisecond-level timestamps to ensure accurate event ordering