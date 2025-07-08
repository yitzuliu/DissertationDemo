#!/usr/bin/env python3
"""
SmolVLM2 Server Launcher
Launch SmolVLM2-500M-Video-Instruct model server with FastAPI
"""

import sys
import time
import signal
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import base64
import io
from PIL import Image
import logging
from pathlib import Path

# Import the model
import sys
import os
# Add the project root to the path for base imports (go up 6 levels)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.append(project_root)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from smolvlm2_500m_video import SmolVLM2Model

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
model_instance = None

class ChatMessage(BaseModel):
    role: str
    content: List[Dict[str, Any]]

class ChatCompletionRequest(BaseModel):
    model: str = "SmolVLM2"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7

class ChatCompletionResponse(BaseModel):
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

app = FastAPI(title="SmolVLM2 Server", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def decode_base64_image(image_url: str) -> Image.Image:
    """Decode base64 image from URL"""
    try:
        if image_url.startswith('data:image/'):
            # Extract base64 data
            base64_data = image_url.split(',')[1]
        else:
            base64_data = image_url
            
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        return image
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SmolVLM2-500M-Video-Instruct Server",
        "version": "1.0.0",
        "status": "running" if model_instance and model_instance.loaded else "not loaded"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if model_instance and model_instance.loaded:
        return {"status": "healthy", "model": "SmolVLM2-500M-Video-Instruct"}
    else:
        raise HTTPException(status_code=503, detail="Model not loaded")

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    global model_instance
    
    if not model_instance:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    if not model_instance.loaded:
        logger.info("Model not loaded, attempting to load...")
        if not model_instance.load_model():
            raise HTTPException(status_code=503, detail="Failed to load model")
    
    try:
        # Extract the user message
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        user_message = None
        for message in request.messages:
            if message.role == "user":
                user_message = message
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Extract text and image from content
        text_content = ""
        image = None
        
        for content_item in user_message.content:
            if content_item.get("type") == "text":
                text_content = content_item.get("text", "")
            elif content_item.get("type") == "image_url":
                image_url = content_item.get("image_url", {}).get("url", "")
                if image_url:
                    image = decode_base64_image(image_url)
        
        if not image:
            raise HTTPException(status_code=400, detail="No image provided")
        
        if not text_content:
            text_content = "Describe what you see in this image."
        
        # Generate prediction
        options = {
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        result = model_instance.predict(image, text_content, options)
        
        # Debug logging
        logger.info(f"Model prediction result: {result}")
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Format response in OpenAI format with proper error handling
        response_data = result.get("response", {})
        
        # Handle different response formats
        if isinstance(response_data, dict):
            response_text = response_data.get("text", "")
        elif isinstance(response_data, str):
            response_text = response_data
        else:
            response_text = str(response_data)
        
        # Ensure we have a valid response
        if not response_text:
            response_text = "No response generated"
        
        return {
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 100,  # Estimated
                "completion_tokens": len(response_text.split()),
                "total_tokens": 100 + len(response_text.split())
            },
            "model": "SmolVLM2-500M-Video-Instruct",
            "processing_time": result.get("processing_time", 0),
            "inference_time": result.get("inference_time", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    global model_instance
    
    logger.info("🚀 Starting SmolVLM2 server...")
    
    # Load model configuration
    # Get project root (6 levels up from current file to get to destination_code)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
    model_path = os.path.join(project_root, "src/models/smolvlm2/SmolVLM2-500M-Video-Instruct")
    
    config = {
        "model_path": model_path,  # Use correct absolute path
        "device": "mps",
        "max_tokens": 150,
        "timeout": 60,
        "image_processing": {
            "max_size": 512
        }
    }
    
    try:
        model_instance = SmolVLM2Model("SmolVLM2-Video", config)
        logger.info("✅ SmolVLM2 model initialized")
        
        # Pre-load the model
        if model_instance.load_model():
            logger.info("✅ SmolVLM2 model loaded successfully")
        else:
            logger.warning("⚠️ Failed to pre-load model, will load on first request")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize model: {e}")
        model_instance = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model_instance
    
    logger.info("🛑 Shutting down SmolVLM2 server...")
    
    if model_instance:
        try:
            model_instance.unload_model()
            logger.info("✅ Model unloaded successfully")
        except Exception as e:
            logger.error(f"❌ Error unloading model: {e}")

def signal_handler(signum, frame):
    """Handle system signals"""
    logger.info("\n🛑 Received stop signal, shutting down server...")
    sys.exit(0)

class SmolVLM2Server:
    """SmolVLM2 Server wrapper"""
    
    def __init__(self, port=8080, host="0.0.0.0"):
        self.port = port
        self.host = host
        
    def start_server(self):
        """Start SmolVLM2 server"""
        print("🎬 SmolVLM2-500M-Video-Instruct Server")
        print("=" * 50)
        print(f"🚀 Starting server...")
        print(f"📦 Model: SmolVLM2-500M-Video-Instruct")
        print(f"🌐 Host: {self.host}")
        print(f"🌐 Port: {self.port}")
        print(f"🍎 Device: MPS (Apple Silicon)")
        print("-" * 50)
        
        try:
            uvicorn.run(
                app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
        except KeyboardInterrupt:
            logger.info("\n🛑 Received stop signal...")
            return True
        except Exception as e:
            logger.error(f"❌ Server startup failed: {e}")
            return False

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server = SmolVLM2Server()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped")
    finally:
        logger.info("👋 Goodbye!")

if __name__ == "__main__":
    main() 