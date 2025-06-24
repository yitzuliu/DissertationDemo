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

# Load configuration
def load_config():
    config_path = Path(__file__).parent.parent / "config" / "app_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        raise
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in configuration file at {config_path}")
        raise

config = load_config()

def load_model_config(model_name):
    """Load model-specific configuration file"""
    model_config_path = Path(__file__).parent.parent / "config" / "model_configs" / f"{model_name}.json"
    try:
        with open(model_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Model configuration file not found at {model_config_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in model configuration file at {model_config_path}")
        return {}

# Set up logging
# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file_path = log_dir / "app.log"

# Configure logging to write to both console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Backend logging configured. Log file at: {log_file_path}")


app = FastAPI(title="Vision Models Unified API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine which model to use based on configuration
ACTIVE_MODEL = config.get("active_model", "smolvlm")
MODEL_SERVER_URL = "http://localhost:8080"  # Unified model server URL

def preprocess_image(image_url):
    """Image preprocessing based on active model"""
    try:
        # Extract base64 data
        base64_pattern = r'data:image\/[^;]+;base64,([^"]+)'
        match = re.search(base64_pattern, image_url)
        if not match:
            logger.warning("Image URL format not recognized, returning original")
            return image_url
        
        base64_data = match.group(1)
        image_data = base64.b64decode(base64_data)
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Model-specific image processing
        if ACTIVE_MODEL == "smolvlm":
            # SmolVLM: 512x512 with image enhancement (restored from backup for better recognition)
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.05)
            
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.3)
            
            quality = 95
            
        elif ACTIVE_MODEL == "phi3_vision":
            # Phi-3 Vision: 336x336 with high quality, no enhancement for best accuracy
            img = img.resize((336, 336), Image.Resampling.LANCZOS)
            quality = 95
            
        else:
            # Fallback: use original size and medium quality
            quality = 85
        
        # Convert back to base64
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        processed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        logger.info(f"Successfully preprocessed image for {ACTIVE_MODEL}")
        return f"data:image/jpeg;base64,{processed_base64}"
    
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        return image_url

class ChatCompletionRequest(BaseModel):
    max_tokens: Optional[int] = None
    messages: List[Dict[str, Any]]

def format_message_for_model(message, image_count, model_name):
    """統一的消息格式化處理"""
    if isinstance(message.get('content'), list):
        # 提取文字和圖片
        text_content = ""
        images = []
        
        for content_item in message['content']:
            if content_item.get('type') == 'text':
                text_content = content_item.get('text', '')
            elif content_item.get('type') == 'image_url':
                images.append(content_item)
        
        # Format text based on model type
        if model_name == "smolvlm":
            # SmolVLM doesn't need special image tags, keep original text
            formatted_text = text_content
        elif model_name == "phi3_vision":
            # Phi-3 Vision uses <|image_1|> format for image references
            if image_count > 0:
                formatted_text = f"<|image_1|>\n{text_content}"
            else:
                formatted_text = text_content
        else:
            formatted_text = text_content
        
        # 重構 content
        new_content = [{"type": "text", "text": formatted_text}]
        new_content.extend(images)
        message['content'] = new_content
        
        logger.info(f"Formatted message for {model_name}: images={image_count}, text='{formatted_text[:50]}...'")
    
    return message

@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: ChatCompletionRequest):
    """Unified chat completion endpoint for supported models"""
    try:
        logger.info(f"Processing request with model: {ACTIVE_MODEL}")
        
        if ACTIVE_MODEL in ["smolvlm", "phi3_vision"]:
            # Count and preprocess images
            image_count = 0
            for message in request.messages:
                if isinstance(message.get('content'), list):
                    for content_item in message['content']:
                        if content_item.get('type') == 'image_url' and 'image_url' in content_item:
                            original_url = content_item['image_url']['url']
                            content_item['image_url']['url'] = preprocess_image(original_url)
                            image_count += 1
                            
            logger.info(f"Detected {image_count} images for {ACTIVE_MODEL}")
            
            # Format all messages
            for message in request.messages:
                message = format_message_for_model(message, image_count, ACTIVE_MODEL)
            
            request_data = request.dict()
            
            # Forward to the model server (always port 8080)
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{MODEL_SERVER_URL}/v1/chat/completions",
                    json=request_data
                )
                return response.json()
                
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model: {ACTIVE_MODEL}")
            
    except httpx.RequestError as e:
        logger.error(f"Error communicating with model server: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error communicating with model server: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Vision Models Unified API", 
        "active_model": ACTIVE_MODEL,
        "version": "1.0.0"
    }

@app.get("/config")
async def get_config():
    """Return frontend configuration with current model's default prompt"""
    # Load model-specific configuration
    model_config = load_model_config(ACTIVE_MODEL)
    
    # Start with main configuration
    frontend_config = config.get("frontend", {}).copy()
    
    # Add model-specific default prompt
    if "ui" in model_config and "default_instruction" in model_config["ui"]:
        frontend_config["default_instruction"] = model_config["ui"]["default_instruction"]
    
    # Add model-specific capture intervals
    if "ui" in model_config and "capture_intervals" in model_config["ui"]:
        frontend_config["capture_intervals"] = model_config["ui"]["capture_intervals"]
        if "default_interval" in model_config["ui"]:
            frontend_config["capture_interval"] = model_config["ui"]["default_interval"]
    
    # Add model-specific help message
    if ACTIVE_MODEL == "smolvlm":
        frontend_config["model_help"] = "SmolVLM is active. System automatically handles image tags, just input your instructions."
    elif ACTIVE_MODEL == "phi3_vision":
        frontend_config["model_help"] = "Phi-3 Vision is active. Images are automatically resized to 336x336 for optimal processing."
    else:
        frontend_config["model_help"] = ""
    
    # Add other required configurations
    frontend_config["active_model"] = ACTIVE_MODEL
    
    return frontend_config

@app.get("/status")
async def get_status():
    """Return system status"""
    return {
        "active_model": ACTIVE_MODEL,
        "available_models": ["smolvlm", "phi3_vision"],
        "config": config
    }

# Start frontend separately: cd ../frontend && python -m http.server 5500

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=config["server"]["host"], 
        port=config["server"]["port"]
    )