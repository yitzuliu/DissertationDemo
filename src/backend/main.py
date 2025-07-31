from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import base64
import io
import re
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import logging
import json
import os
from pathlib import Path
from utils.config_manager import config_manager
from utils.image_processing import (
    preprocess_for_model, 
    enhance_image_clahe, 
    convert_to_pil_image,
    convert_to_cv2_image,
    smart_crop_and_resize,
    reduce_noise,
    enhance_color_balance
)
import time
import sys
import uuid

# Import State Tracker and Loggers
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from state_tracker import get_state_tracker
from app_logging.system_logger import get_system_logger, initialize_system_logger
from app_logging.visual_logger import get_visual_logger
from app_logging.log_manager import get_log_manager
from app_logging.flow_tracker import get_flow_tracker, FlowType, FlowStep, FlowStatus

def setup_logging():
    """Setup logging with proper path and permissions"""
    try:
        # Get absolute path to project root
        base_dir = Path(__file__).resolve().parent.parent.parent
        log_dir = base_dir / "logs"
        
        # Create logs directory with parents if needed
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure proper directory permissions (readable and writable)
        os.chmod(log_dir, 0o755)
        
        # Setup log file path with timestamp
        timestamp = time.strftime("%Y%m%d")
        log_file = log_dir / f"app_{timestamp}.log"
        
        # Configure file handler with UTF-8 encoding
        file_handler = logging.FileHandler(
            filename=log_file,
            mode='a',
            encoding='utf-8'
        )
        
        # Ensure proper file permissions (readable and writable)
        os.chmod(log_file, 0o644)
        
        # Configure console handler with reduced output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only show warnings and errors in terminal
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'  # Simplified console output
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set logging level for file (INFO) and console (WARNING)
        root_logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        
        # Add handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log initialization success (this will only go to file due to level)
        root_logger.info(f"Logging initialized. Log file: {log_file}")
        
        return root_logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

# Initialize logging
logger = setup_logging()
logger.info("Backend server starting...")

# Initialize and load configuration
config_manager.load_app_config()
logger.info("Configuration loaded successfully")

# 確保使用正確的 ACTIVE_MODEL
ACTIVE_MODEL = config_manager.get_active_model()
logger.info(f"Using active model: {ACTIVE_MODEL}")

app = FastAPI(title="Vision Models Unified API")

# Initialize system logger
system_logger = initialize_system_logger()

# Initialize log manager
log_manager = get_log_manager()

# Initialize flow tracker
flow_tracker = get_flow_tracker()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get model server URL from configuration
def get_model_server_url():
    """Get the model server URL from configuration"""
    active_model_config = config_manager.get_active_model_config()
    server_config = active_model_config.get("server", {})
    port = server_config.get("port", 8080)
    return f"http://localhost:{port}"

MODEL_SERVER_URL = get_model_server_url()

def preprocess_image(image_url):
    """Enhanced image preprocessing with quality improvements"""
    try:
        # Extract base64 data
        base64_pattern = r'data:image\/[^;]+;base64,([^"]+)'
        match = re.search(base64_pattern, image_url)
        if not match:
            logger.warning("Image URL format not recognized, returning original")
            return image_url
        
        try:
            # Decode and validate image
            base64_data = match.group(1)
            image_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(image_data))
            
            # Get model configuration
            model_config = config_manager.load_model_config(ACTIVE_MODEL)
            image_config = model_config.get("image_processing", {})
            
            # 統一配置存取：優先使用 model_path，fallback 到 model_id
            model_identifier = model_config.get("model_path", model_config.get("model_id", ACTIVE_MODEL))
            logger.info(f"Processing image for model: {model_identifier}")
            
            # Unified handling of different configuration formats
            # Support both "size": [1024, 1024] and "max_size": 512 formats
            if "size" in image_config:
                size_config = image_config["size"]
                if isinstance(size_config, (list, tuple)) and len(size_config) >= 2:
                    try:
                        # Convert each element to string first to handle various numeric types
                        width = int(float(str(size_config[0])))
                        height = int(float(str(size_config[1])))
                        target_size = (width, height)
                    except (ValueError, TypeError, AttributeError):
                        logger.warning("Invalid size config values, using defaults")
                        target_size = (1024, 1024)
                else:
                    try:
                        # Convert to string first to handle various numeric types
                        size_value = int(float(str(size_config)))
                        target_size = (size_value, size_value)
                    except (ValueError, TypeError, AttributeError):
                        logger.warning("Invalid size config value, using defaults")
                        target_size = (1024, 1024)
            elif "max_size" in image_config:
                try:
                    # Convert to string first to handle various numeric types
                    max_size = int(float(str(image_config["max_size"])))
                    target_size = (max_size, max_size)
                except (ValueError, TypeError, AttributeError):
                    logger.warning("Invalid max_size value, using defaults")
                    target_size = (1024, 1024)
            else:
                target_size = (1024, 1024)  # Default value
            
            min_size = image_config.get("min_size", 512)
            
            # Apply smart cropping
            if image_config.get("smart_crop", True):
                image = smart_crop_and_resize(
                    image,
                    target_size=target_size,
                    min_size=min_size,
                    preserve_aspect_ratio=True
                )
            
            # Apply noise reduction (only if enabled)
            if image_config.get("noise_reduction", {}).get("enabled", False):
                noise_config = image_config.get("noise_reduction", {})
                image = reduce_noise(
                    image,
                    method=noise_config.get("method", "bilateral"),
                    config=noise_config
                )
            
            # Apply color enhancement (only if enabled)
            if image_config.get("color_balance", {}).get("enabled", False):
                color_config = image_config.get("color_balance", {})
                image = enhance_color_balance(
                    image,
                    method=color_config.get("method", "lab"),
                    config=color_config
                )
            
            # Save processed image
            buffer = io.BytesIO()
            
            # Unified quality parameter handling
            quality = image_config.get("jpeg_quality", image_config.get("quality", 95))
            
            save_params = {
                "format": "JPEG",
                "quality": int(quality),
                "optimize": image_config.get("optimize", True)
            }
            image.save(buffer, **save_params)
            
            # Return processed base64 image
            processed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/jpeg;base64,{processed_base64}"
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return image_url
    
    except Exception as e:
        logger.error(f"Error in image preprocessing: {str(e)}")
        return image_url

class ChatCompletionRequest(BaseModel):
    max_tokens: Optional[int] = None
    messages: List[Dict[str, Any]]

@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: ChatCompletionRequest):
    """Enhanced chat completion endpoint with improved image processing"""
    request_start_time = time.time()
    request_id = f"req_{int(request_start_time * 1000)}"  # Unique request ID
    
    # 生成觀察ID用於追蹤整個視覺處理流程
    observation_id = f"obs_{int(request_start_time * 1000)}_{uuid.uuid4().hex[:8]}"
    
    # 獲取視覺日誌記錄器
    visual_logger = get_visual_logger()
    
    try:
        logger.info(f"[{request_id}] Processing request with model: {ACTIVE_MODEL}")
        
        # 記錄後端接收VLM請求
        visual_logger.log_backend_receive(observation_id, request_id, {
            "model": ACTIVE_MODEL,
            "messages": request.messages,
            "max_tokens": getattr(request, 'max_tokens', None),
            "temperature": getattr(request, 'temperature', None)
        })
        
        # 更新支援的模型清單，確保包含所有配置的模型
        supported_models = [
            "smolvlm", 
            "phi3_vision", 
            "phi3_vision_optimized", 
            "smolvlm2_500m_video", 
            "smolvlm2_500m_video_optimized", 
            "moondream2", 
            "moondream2_optimized", 
            "llava_mlx",
            "qwen2_vl",
            "yolo8"
        ]
        
        if ACTIVE_MODEL in supported_models:
            image_count = 0
            image_processing_start = time.time()
            
            # 記錄圖像處理開始
            visual_logger.log_image_processing_start(observation_id, request_id, 0, ACTIVE_MODEL)
            
            # Create a sanitized copy of messages for logging
            sanitized_messages = []
            for message in request.messages:
                sanitized_message = message.copy() if isinstance(message, dict) else message
                if isinstance(sanitized_message.get('content'), list):
                    sanitized_content = []
                    for content_item in sanitized_message['content']:
                        if content_item.get('type') == 'image_url':
                            # Replace image data with placeholder
                            sanitized_content.append({
                                'type': 'image_url',
                                'image_processed': True,
                                'original_format': content_item.get('image_url', {}).get('url', '').split(';')[0].replace('data:', '') if 'image_url' in content_item else 'unknown'
                            })
                        else:
                            sanitized_content.append(content_item)
                    sanitized_message['content'] = sanitized_content
                sanitized_messages.append(sanitized_message)
            
            # Log sanitized messages
            logger.info(f"[{request_id}] Received messages: {json.dumps(sanitized_messages, indent=2)}")
            
            # Process images
            for message in request.messages:
                if isinstance(message.get('content'), list):
                    for content_item in message['content']:
                        if content_item.get('type') == 'image_url' and 'image_url' in content_item:
                            # Log image processing start without the URL
                            logger.info(f"[{request_id}] Processing image {image_count + 1}")
                            
                            # Apply enhanced image processing
                            original_url = content_item['image_url']['url']
                            content_item['image_url']['url'] = preprocess_image(original_url)
                            image_count += 1
            
            image_processing_time = time.time() - image_processing_start
            logger.info(f"[{request_id}] Image processing completed in {image_processing_time:.2f}s")
            logger.info(f"[{request_id}] Processed {image_count} images for {ACTIVE_MODEL}")
            
            # 記錄圖像處理結果
            visual_logger.log_image_processing_result(
                observation_id, request_id, image_processing_time, True,
                {"image_count": image_count, "model": ACTIVE_MODEL}
            )
            
            # Format messages
            format_start = time.time()
            for message in request.messages:
                message = format_message_for_model(message, image_count, ACTIVE_MODEL)
            format_time = time.time() - format_start
            logger.info(f"[{request_id}] Message formatting completed in {format_time:.2f}s")
            
            # Prepare request for model
            request_data = request.dict()
            logger.info(f"[{request_id}] Sending request to model server")
            
            # 計算提示詞長度用於日誌記錄
            prompt_length = 0
            for message in request.messages:
                if isinstance(message.get('content'), str):
                    prompt_length += len(message['content'])
                elif isinstance(message.get('content'), list):
                    for item in message['content']:
                        if item.get('type') == 'text':
                            prompt_length += len(item.get('text', ''))
            
            # 記錄VLM請求
            visual_logger.log_vlm_request(observation_id, request_id, ACTIVE_MODEL, prompt_length, image_count)
            
            # Send to model and measure time
            model_request_start = time.time()
            vlm_success = False
            response_length = 0
            
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        f"{MODEL_SERVER_URL}/v1/chat/completions",
                        json=request_data
                    )
                    model_response = response.json()
                    model_request_time = time.time() - model_request_start
                    vlm_success = True
                    
                    # 計算回應長度
                    if 'choices' in model_response and len(model_response['choices']) > 0:
                        content = model_response['choices'][0]['message']['content']
                        if isinstance(content, str):
                            response_length = len(content)
                        elif isinstance(content, list):
                            response_length = sum(len(str(item)) for item in content)
                        else:
                            response_length = len(str(content))
                    
                    # 記錄VLM回應
                    visual_logger.log_vlm_response(
                        observation_id, request_id, response_length, 
                        model_request_time, vlm_success, ACTIVE_MODEL
                    )
                    
            except Exception as e:
                model_request_time = time.time() - model_request_start
                visual_logger.log_vlm_response(
                    observation_id, request_id, 0, 
                    model_request_time, False, ACTIVE_MODEL
                )
                visual_logger.log_error(observation_id, request_id, type(e).__name__, str(e), "vlm_request")
                raise
                
                # Sanitize model response for logging
                sanitized_response = model_response.copy()
                if 'choices' in sanitized_response:
                    for choice in sanitized_response['choices']:
                        if 'message' in choice and isinstance(choice['message'].get('content'), list):
                            sanitized_content = []
                            for content_item in choice['message']['content']:
                                if content_item.get('type') == 'image_url':
                                    sanitized_content.append({
                                        'type': 'image_url',
                                        'processed': True
                                    })
                                else:
                                    sanitized_content.append(content_item)
                            choice['message']['content'] = sanitized_content
                
                logger.info(f"[{request_id}] Received response from model in {model_request_time:.2f}s")
                logger.info(f"[{request_id}] Model response: {json.dumps(sanitized_response, indent=2)}")
                
                # State Tracker Integration: Process VLM response
                try:
                    if 'choices' in model_response and len(model_response['choices']) > 0:
                        content = model_response['choices'][0]['message']['content']
                        
                        # Handle different VLM response formats
                        vlm_text = None
                        
                        if isinstance(content, str):
                            # Simple string response
                            vlm_text = content
                            logger.info(f"[{request_id}] VLM returned string content (length: {len(content)})")
                            logger.info(f"[{request_id}] VLM full response: {vlm_text}")
                        
                        elif isinstance(content, list):
                            # List format (some models return structured content)
                            text_parts = []
                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'text':
                                    text_parts.append(item.get('text', ''))
                                elif isinstance(item, str):
                                    text_parts.append(item)
                            vlm_text = ' '.join(text_parts)
                            logger.info(f"[{request_id}] VLM returned list content, extracted text (length: {len(vlm_text)})")
                            logger.info(f"[{request_id}] VLM full response: {vlm_text}")
                        
                        elif isinstance(content, dict):
                            # Dictionary format
                            vlm_text = content.get('text', str(content))
                            logger.info(f"[{request_id}] VLM returned dict content, extracted: {vlm_text[:50]}...")
                            logger.info(f"[{request_id}] VLM full response: {vlm_text}")
                        
                        else:
                            # Fallback: convert to string
                            vlm_text = str(content)
                            logger.warning(f"[{request_id}] VLM returned unexpected format ({type(content)}), converted to string")
                            logger.info(f"[{request_id}] VLM full response: {vlm_text}")
                        
                        # Process with State Tracker if we have valid text
                        if vlm_text and len(vlm_text.strip()) > 0:
                            # 記錄RAG資料傳遞
                            visual_logger.log_rag_data_transfer(observation_id, vlm_text, True)
                            
                            # 處理狀態追蹤器整合
                            state_tracker_start = time.time()
                            state_tracker = get_state_tracker()
                            state_updated = await state_tracker.process_vlm_response(vlm_text, observation_id)
                            state_tracker_time = time.time() - state_tracker_start
                            
                            # 記錄狀態追蹤器整合結果
                            visual_logger.log_state_tracker_integration(
                                observation_id, state_updated, state_tracker_time
                            )
                            
                            logger.info(f"[{request_id}] State Tracker processed VLM response: updated={state_updated}")
                            logger.info(f"[{request_id}] State Tracker full response: {vlm_text}")
                        else:
                            # 記錄RAG資料傳遞失敗
                            visual_logger.log_rag_data_transfer(observation_id, "", False)
                            visual_logger.log_state_tracker_integration(observation_id, False)
                            logger.warning(f"[{request_id}] No valid text extracted from VLM response")
                            
                except Exception as e:
                    # 記錄狀態追蹤器處理錯誤
                    visual_logger.log_error(observation_id, request_id, type(e).__name__, str(e), "state_tracker_integration")
                    logger.warning(f"[{request_id}] State Tracker processing failed: {e}")
                
                # Calculate total processing time
                total_time = time.time() - request_start_time
                logger.info(f"[{request_id}] Total request processing time: {total_time:.2f}s")
                logger.info(f"[{request_id}] Timing breakdown:")
                logger.info(f"  - Image processing: {image_processing_time:.2f}s")
                logger.info(f"  - Message formatting: {format_time:.2f}s")
                logger.info(f"  - Model inference: {model_request_time:.2f}s")
                
                # 記錄性能指標
                visual_logger.log_performance_metric(observation_id, "total_processing_time", total_time, "s")
                visual_logger.log_performance_metric(observation_id, "image_processing_time", image_processing_time, "s")
                visual_logger.log_performance_metric(observation_id, "model_inference_time", model_request_time, "s")
                
                return model_response
                
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model: {ACTIVE_MODEL}")
            
    except httpx.RequestError as e:
        error_time = time.time() - request_start_time
        logger.error(f"[{request_id}] Error communicating with model server after {error_time:.2f}s: {e}", exc_info=True)
        
        # 記錄視覺處理錯誤
        visual_logger.log_error(observation_id, request_id, "RequestError", str(e), "model_server_communication")
        visual_logger.log_performance_metric(observation_id, "error_time", error_time, "s")
        
        raise HTTPException(status_code=500, detail=f"Error communicating with model server: {str(e)}")
    except Exception as e:
        error_time = time.time() - request_start_time
        logger.error(f"[{request_id}] An unexpected error occurred after {error_time:.2f}s: {e}", exc_info=True)
        
        # 記錄視覺處理錯誤
        visual_logger.log_error(observation_id, request_id, type(e).__name__, str(e), "unexpected_error")
        visual_logger.log_performance_metric(observation_id, "error_time", error_time, "s")
        
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Vision Models Unified API", 
        "active_model": ACTIVE_MODEL,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    import datetime
    return {
        "status": "healthy",
        "active_model": ACTIVE_MODEL,
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/v1/state")
async def get_current_state():
    """Get current state from State Tracker"""
    try:
        state_tracker = get_state_tracker()
        current_state = state_tracker.get_current_state()
        summary = state_tracker.get_state_summary()
        
        return {
            "status": "success",
            "current_state": current_state,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting state: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting state: {str(e)}")

@app.get("/api/v1/state/metrics")
async def get_processing_metrics():
    """Get quantifiable processing metrics"""
    try:
        state_tracker = get_state_tracker()
        metrics = state_tracker.get_processing_metrics()
        summary = state_tracker.get_metrics_summary()
        
        return {
            "status": "success",
            "metrics": metrics,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")

@app.get("/api/v1/state/memory")
async def get_memory_stats():
    """Get sliding window memory management statistics"""
    try:
        state_tracker = get_state_tracker()
        memory_stats = state_tracker.get_memory_stats()
        sliding_window_data = state_tracker.get_sliding_window_data()
        history_analysis = state_tracker.get_state_history_analysis()
        
        return {
            "status": "success",
            "memory_stats": {
                "total_records": memory_stats.total_records,
                "memory_usage_bytes": memory_stats.memory_usage_bytes,
                "memory_usage_mb": memory_stats.memory_usage_bytes / (1024 * 1024),
                "cleanup_count": memory_stats.cleanup_count,
                "max_size_reached": memory_stats.max_size_reached,
                "avg_record_size_bytes": memory_stats.avg_record_size
            },
            "sliding_window": sliding_window_data,
            "history_analysis": history_analysis
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting memory stats: {str(e)}")

@app.post("/api/v1/state/process")
async def process_vlm_text(request: dict):
    """Manually process VLM text for testing"""
    request_start_time = time.time()
    request_id = f"req_manual_{int(request_start_time * 1000)}"
    observation_id = f"obs_manual_{int(request_start_time * 1000)}_{uuid.uuid4().hex[:8]}"
    
    visual_logger = get_visual_logger()
    
    try:
        vlm_text = request.get("text", "")
        if not vlm_text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # 記錄手動VLM文本處理
        visual_logger.log_rag_data_transfer(observation_id, vlm_text, True)
        
        state_tracker_start = time.time()
        state_tracker = get_state_tracker()
        result = await state_tracker.process_vlm_response(vlm_text, observation_id)
        state_tracker_time = time.time() - state_tracker_start
        current_state = state_tracker.get_current_state()
        
        # 記錄狀態追蹤器處理結果
        visual_logger.log_state_tracker_integration(observation_id, result, state_tracker_time)
        
        total_time = time.time() - request_start_time
        visual_logger.log_performance_metric(observation_id, "manual_processing_time", total_time, "s")
        
        return {
            "status": "success",
            "updated": result,
            "current_state": current_state
        }
    except Exception as e:
        error_time = time.time() - request_start_time
        logger.error(f"Error processing VLM text: {e}")
        
        # 記錄錯誤
        visual_logger.log_error(observation_id, request_id, type(e).__name__, str(e), "manual_vlm_processing")
        visual_logger.log_performance_metric(observation_id, "error_time", error_time, "s")
        
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/api/v1/logging/user")
async def receive_user_log(request: dict):
    """Receive user query logs from frontend"""
    try:
        # Validate request
        if not request:
            raise HTTPException(status_code=400, detail="Request body is required")
        
        event_type = request.get("event_type")
        query_id = request.get("query_id")
        request_id = request.get("request_id")
        question = request.get("question")
        language = request.get("language")
        
        if event_type == "USER_QUERY" and query_id and request_id and question:
            # Log user query using log manager
            log_manager.log_user_query(
                query_id=query_id,
                request_id=request_id,
                question=question,
                language=language or "en"
            )
            
            return {"status": "success", "message": "User query logged successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid log data format")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging user query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/state/query")
async def process_instant_query(request: dict):
    """Process instant user query for immediate response with comprehensive logging and flow tracking"""
    try:
        # Validate request
        if not request:
            raise HTTPException(status_code=400, detail="Request body is required")
        
        query = request.get("query", "").strip()
        query_id = request.get("query_id")
        request_id = request.get("request_id")
        flow_id = request.get("flow_id")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        if len(query) > 500:  # Reasonable limit
            raise HTTPException(status_code=400, detail="Query too long (max 500 characters)")
        
        # Generate IDs if not provided by frontend
        if not query_id:
            query_id = log_manager.generate_query_id()
        if not request_id:
            request_id = log_manager.generate_request_id()
        if not flow_id:
            flow_id = flow_tracker.start_flow(FlowType.USER_QUERY)
        else:
            flow_tracker.add_flow_step(flow_id, FlowStep.QUERY_RECEIVED, related_ids={"query_id": query_id, "request_id": request_id})
        
        # Log query processing start
        start_time = time.time()
        flow_tracker.add_flow_step(flow_id, FlowStep.QUERY_CLASSIFICATION, related_ids={"query_id": query_id})
        
        state_tracker = get_state_tracker()
        result = state_tracker.process_instant_query(query, query_id, request_id)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Validate result
        if not result or not hasattr(result, 'response_text'):
            flow_tracker.end_flow(flow_id, FlowStatus.FAILED)
            raise HTTPException(status_code=500, detail="Invalid response from query processor")
        
        # Log query response
        log_manager.log_query_response(
            query_id=query_id,
            response=result.response_text,
            duration=processing_time_ms
        )
        flow_tracker.add_flow_step(flow_id, FlowStep.RESPONSE_SENT, related_ids={"query_id": query_id})
        flow_tracker.end_flow(flow_id, FlowStatus.SUCCESS)
        
        return {
            "status": "success",
            "query": result.raw_query,
            "query_type": result.query_type.value,
            "response": result.response_text,
            "processing_time_ms": result.processing_time_ms,
            "confidence": result.confidence,
            "flow_id": flow_id
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error processing instant query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/state/query/capabilities")
async def get_query_capabilities():
    """Get query processing capabilities and examples"""
    try:
        state_tracker = get_state_tracker()
        capabilities = state_tracker.get_query_capabilities()
        
        return {
            "status": "success",
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting query capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting capabilities: {str(e)}")

@app.get("/api/v1/config")
async def get_full_config():
    """Return the complete merged configuration including app config and active model config"""
    return config_manager.get_merged_config()

class ConfigUpdate(BaseModel):
    """Model for configuration updates"""
    active_model: Optional[str] = None
    server: Optional[Dict[str, Any]] = None
    frontend: Optional[Dict[str, Any]] = None

@app.patch("/api/v1/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration values"""
    updates = config_update.dict(exclude_unset=True)
    
    # Special handling for active_model to validate it exists
    if "active_model" in updates:
        model_name = updates.pop("active_model")
        success = config_manager.set_active_model(model_name)
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Model '{model_name}' not found or invalid"
            )
        # Update the global ACTIVE_MODEL variable
        global ACTIVE_MODEL
        ACTIVE_MODEL = config_manager.get_active_model()
    
    # Apply other updates
    if updates:
        config_manager.update_config(updates)
    
    return {
        "status": "success",
        "message": "Configuration updated successfully",
        "config": config_manager.get_merged_config()
    }

@app.get("/status")
async def get_status():
    """Return system status"""
    try:
        # Get current model configuration
        model_config = config_manager.load_model_config(ACTIVE_MODEL)
        display_name = model_config.get("model_name", ACTIVE_MODEL)
        model_id = model_config.get("model_id", ACTIVE_MODEL)
        
        return {
            "active_model": display_name,
            "model_id": model_id,
            # 更新可用模型清單，確保包含所有模型
            "available_models": [
                "smolvlm", 
                "phi3_vision", 
                "phi3_vision_optimized", 
                "smolvlm2_500m_video", 
                "smolvlm2_500m_video_optimized", 
                "moondream2", 
                "moondream2_optimized", 
                "llava_mlx",
                "qwen2_vl",
                "yolo8"
            ],
            "config": config_manager.get_config(),
            "model_status": {
                "name": display_name,
                "description": model_config.get("description", ""),
                "version": model_config.get("version", "1.0.0")
            }
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail="Error getting system status")

@app.get("/config")
async def get_config():
    """Return frontend configuration with current model's default prompt"""
    try:
        # 強制重新載入配置
        config_manager.load_app_config()
        
        # Load model-specific configuration
        model_config = config_manager.load_model_config(ACTIVE_MODEL)
        
        logger.info(f"🔧 Loading frontend config for model: {ACTIVE_MODEL}")
        logger.info(f"🔧 Model config loaded: {bool(model_config)}")
        logger.info(f"🔧 Model config keys: {list(model_config.keys()) if model_config else 'None'}")
        
        # Start with main configuration
        frontend_config = config_manager.get_config("frontend", {}).copy()
        
        # Add model-specific default prompt
        if "ui" in model_config and "default_instruction" in model_config["ui"]:
            frontend_config["default_instruction"] = model_config["ui"]["default_instruction"]
            logger.info(f"✅ Added default instruction from model config")
        else:
            logger.warning(f"⚠️ No default instruction found in model config")
        
        # Add model-specific capture intervals
        if "ui" in model_config and "capture_intervals" in model_config["ui"]:
            frontend_config["capture_intervals"] = model_config["ui"]["capture_intervals"]
            if "default_interval" in model_config["ui"]:
                frontend_config["capture_interval"] = model_config["ui"]["default_interval"]
            logger.info(f"✅ Added capture intervals from model config")
        else:
            # 提供默認值
            frontend_config["capture_intervals"] = [1000, 2000, 5000, 10000]
            frontend_config["capture_interval"] = 5000
            logger.info(f"⚠️ Using default capture intervals")
        
        # Add model-specific help message
        if ACTIVE_MODEL == "llava_mlx":
            frontend_config["model_help"] = "LLaVA MLX is active. MLX-optimized multimodal model for Apple Silicon with INT4 quantization. Best for photographic images."
        elif ACTIVE_MODEL == "smolvlm":
            frontend_config["model_help"] = "SmolVLM is active. System automatically handles image tags, just input your instructions."
        elif ACTIVE_MODEL in ["phi3_vision", "phi3_vision_optimized"]:
            frontend_config["model_help"] = "Phi-3 Vision is active. MLX-optimized for Apple Silicon with <|image_1|> format. Images are automatically processed for optimal results."
        elif ACTIVE_MODEL in ["smolvlm2", "smolvlm2-500", "smolvlm2_500m_video", "smolvlm2_500m_video_optimized"]:
            frontend_config["model_help"] = "SmolVLM2-500M-Video is active. Enhanced image analysis with video understanding capabilities. Optimized for Apple Silicon."
        elif ACTIVE_MODEL in ["moondream2", "moondream2_optimized"]:
            frontend_config["model_help"] = "Moondream2 is active. Compact vision language model with strong VQA performance. Uses special encode_image + answer_question API."
        else:
            frontend_config["model_help"] = ""
        
        # Add other required configurations
        frontend_config["active_model"] = ACTIVE_MODEL
        
        logger.info(f"🔧 Final frontend config: {json.dumps(frontend_config, indent=2)}")
        
        return frontend_config
        
    except Exception as e:
        logger.error(f"Error loading frontend config: {e}")
        # 返回最小配置以避免前端錯誤
        return {
            "active_model": ACTIVE_MODEL,
            "model_help": f"{ACTIVE_MODEL} is active",
            "capture_intervals": [1000, 2000, 5000, 10000],
            "capture_interval": 5000,
            "default_instruction": "Describe what you see in this image."
        }

def format_message_for_model(message, image_count, model_name):
    """Unified message formatting handler"""
    if isinstance(message.get('content'), list):
        # Extract text and images
        text_content = ""
        images = []
        
        for content_item in message['content']:
            if content_item.get('type') == 'text':
                text_content = content_item.get('text', '')
            elif content_item.get('type') == 'image_url':
                images.append(content_item)
        
        # Format text based on model type
        if model_name in ["smolvlm", "smolvlm2_500m_video", "smolvlm2_500m_video_optimized"]:
            # FIXED: SmolVLM doesn't need ANY special image tags - it handles images automatically
            formatted_text = text_content
        elif model_name in ["phi3_vision", "phi3_vision_optimized"]:
            # Don't add <|image_1|> here - let model server handle it
            formatted_text = text_content  # Remove the prefix addition
        elif model_name in ["moondream2", "moondream2_optimized"]:
            # Moondream2 doesn't need special image tags
            formatted_text = text_content
        elif model_name == "llava_mlx":
            # LLaVA MLX doesn't need special image tags
            formatted_text = text_content
        elif model_name == "qwen2_vl":
            # Qwen2-VL doesn't need special image tags
            formatted_text = text_content
        elif model_name == "yolo8":
            # YOLO8 for object detection
            formatted_text = text_content or "Detect objects in this image"
        else:
            formatted_text = text_content
        
        # Reconstruct content
        new_content = [{"type": "text", "text": formatted_text}]
        new_content.extend(images)
        message['content'] = new_content
        
        logger.info(f"Formatted message for {model_name}: images={image_count}, text='{formatted_text[:50]}...'")
    
    return message

if __name__ == "__main__":
    # 確保在啟動時正確配置
    host = config_manager.get_config("server.host", "localhost")
    port = config_manager.get_config("server.port", 8000)
    
    logger.info(f"Starting backend server with model: {ACTIVE_MODEL}")
    
    # 記錄系統啟動
    system_logger.log_system_startup(
        host=host,
        port=port,
        model=ACTIVE_MODEL,
        server_url=MODEL_SERVER_URL
    )
    
    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        system_logger.log_system_shutdown()
    except Exception as e:
        system_logger.log_error("server_startup", str(e))
        raise