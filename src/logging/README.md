# AI Manual Assistant Logging System

## LogManager Usage Guide

### Basic Usage

```python
from logging.log_manager import LogManager, get_log_manager

# Method 1: Create instance directly
log_manager = LogManager("logs")

# Method 2: Use global instance
log_manager = get_log_manager()
```

### Unique ID Generation

```python
# Generate various types of unique IDs
observation_id = log_manager.generate_observation_id()  # obs_1753891534519_db0775ed
query_id = log_manager.generate_query_id()            # query_1753891534519_987f9c84
request_id = log_manager.generate_request_id()        # req_1753891534519_b70f3798
state_update_id = log_manager.generate_state_update_id()  # state_1753891534519_00ac8f4e
flow_id = log_manager.generate_flow_id()              # flow_1753891534519_5d551d89
```

### System Logging

```python
# System startup
log_manager.log_system_start("sys_001", "localhost", 8000, "smolvlm")

# Memory usage
log_manager.log_memory_usage("sys_001", "22.1MB")

# Endpoint call
log_manager.log_endpoint_call(request_id, "POST", "/v1/chat/completions", 200, 2.31)

# System shutdown
log_manager.log_system_shutdown("sys_001", "22.5MB", "30min")
```

### Visual Processing Logging

```python
# Image capture
log_manager.log_eyes_capture(observation_id, request_id, "MacBook FaceTime HD", 
                            "1920x1080", 0.9, "JPEG", "1.2MB")

# Visual prompt
log_manager.log_eyes_prompt(observation_id, "Describe the steps for making coffee...", 48)

# Backend transfer
log_manager.log_eyes_transfer(observation_id, {"question": "How to make coffee?", "tokens": 100})

# RAG matching process
log_manager.log_rag_matching(observation_id, "There are coffee filters and drip coffee maker on the table.", 
                           ["step1", "step2", "step3"], [0.82, 0.65, 0.12])

# RAG matching result
log_manager.log_rag_result(observation_id, "step2", "Rinse the filter paper", 0.82)

# State tracker decision
log_manager.log_state_tracker(observation_id, state_update_id, 0.82, "UPDATE", 
                            {"task": "brewing_coffee", "step": 2})
```

### User Query Logging

```python
# User query
log_manager.log_user_query(query_id, request_id, "What tools do I need?", "en", observation_id)

# Query classification
log_manager.log_query_classify(query_id, "required_tools", 0.95)

# Query processing
log_manager.log_query_process(query_id, {"task": "brewing_coffee", "step": 2})

# Query response
log_manager.log_query_response(query_id, "You need: filter paper, drip coffee maker, hot water, cup.", 1.2)
```

### Flow Tracking Logging

```python
# Flow start
log_manager.log_flow_start(flow_id, "EYES_OBSERVATION")

# Flow steps
log_manager.log_flow_step(flow_id, "image_capture", observation_id=observation_id)
log_manager.log_flow_step(flow_id, "backend_transfer", request_id=request_id)
log_manager.log_flow_step(flow_id, "user_query", query_id=query_id)

# Flow end
log_manager.log_flow_end(flow_id, "SUCCESS", 5.0)
```

## Log File Format

### File Naming Rules
- System logs: `logs/system_YYYYMMDD.log`
- Visual logs: `logs/visual_YYYYMMDD.log`
- User logs: `logs/user_YYYYMMDD.log`
- Flow tracking: `logs/flow_tracking_YYYYMMDD.log`

### Log Format
```
YYYY-MM-DD HH:MM:SS,mmm [INFO] [EVENT_TYPE] key1=value1 key2=value2 ...
```

### Example Log Content
```
2025-07-30 17:05:34,519 [INFO] [SYSTEM_START] system_id=sys_001 host=localhost port=8000 model=smolvlm
2025-07-30 17:05:34,519 [INFO] [EYES_CAPTURE] observation_id=obs_1753891534519_db0775ed request_id=req_1753891534519_b70f3798 device=MacBook FaceTime HD resolution=1920x1080 quality=0.9 format=JPEG size=1.2MB
2025-07-30 17:05:34,519 [INFO] [USER_QUERY] query_id=query_1753891534519_987f9c84 request_id=req_1753891534519_b70f3798 question="What tools do I need?" language=en used_observation_id=obs_1753891534519_db0775ed
```

## Features

- ✅ Unified timestamp format (`YYYY-MM-DD HH:MM:SS,mmm`)
- ✅ Unique ID tracking mechanism (observation_id, query_id, request_id, state_update_id, flow_id)
- ✅ Multiple log type support (system, visual, user, flow_tracking)
- ✅ Structured log format (key=value pairs)
- ✅ Automatic log file management (daily rotation)
- ✅ Global instance management
- ✅ Complete traceability support