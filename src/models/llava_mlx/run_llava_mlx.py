#!/usr/bin/env python3
"""
LLaVA MLX Server Launcher
Launch LLaVA MLX model server with FastAPI
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
import tempfile
import os

# Add project root to path for module imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

# Import configuration manager
from src.backend.utils.config_manager import config_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
model_instance = None
processor = None

class ChatMessage(BaseModel):
    role: str
    content: List[Dict[str, Any]]

class ChatCompletionRequest(BaseModel):
    model: str = "LLaVA-MLX"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7

app = FastAPI(title="LLaVA MLX Server", version="1.0.0")

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
        "message": "LLaVA MLX Server",
        "version": "1.0.0",
        "status": "running" if model_instance else "not loaded"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if model_instance:
        return {"status": "healthy", "model": "LLaVA-MLX"}
    else:
        raise HTTPException(status_code=503, detail="Model not loaded")

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    global model_instance, processor
    
    if not model_instance:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
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
        
        # Generate prediction using LLaVA MLX (same as testing)
        try:
            from mlx_vlm import generate
            
            # Save the PIL Image to a temporary file for MLX-VLM
            temp_image_path = "temp_mlx_image.png"
            image.save(temp_image_path)
            
            try:
                response_text = generate(
                    model_instance, processor, text_content, image=temp_image_path,
                    max_tokens=request.max_tokens or 100, verbose=False
                )
            finally:
                # Clean up temp file
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
            
            # Process MLX response
            if isinstance(response_text, tuple) and len(response_text) >= 2:
                response_text = response_text[0]
            elif isinstance(response_text, list) and len(response_text) > 0:
                response_text = response_text[0] if isinstance(response_text[0], str) else str(response_text[0])
            else:
                response_text = str(response_text)

            # Clean up stop tokens
            stop_tokens = ["<|end|>", "<|endoftext|>", "ASSISTANT:", "USER:", "<|im_end|>"]
            for token in stop_tokens:
                response_text = response_text.replace(token, "")
            
            response_text = response_text.replace("<|end|><|endoftext|>", " ")
            
            if "1. What is meant by" in response_text:
                response_text = response_text.split("1. What is meant by")[0].strip()
            
            response_text = ' '.join(response_text.split()).strip()
            
            # Ensure we have a valid response
            if not response_text:
                response_text = "No response generated"
                
        except Exception as e:
            logger.error(f"Model inference error: {e}")
            raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")
        
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
                "prompt_tokens": 50,  # Estimated
                "completion_tokens": len(response_text.split()),
                "total_tokens": 50 + len(response_text.split())
            },
            "model": "LLaVA-MLX"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    global model_instance, processor
    
    logger.info("🚀 Starting LLaVA MLX server...")
    
    try:
        # Load model configuration from config system
        config = config_manager.load_model_config("llava_mlx")
        model_path = config.get("model_path", "mlx-community/llava-v1.6-mistral-7b-4bit")
        
        logger.info(f"Loading LLaVA MLX model: {model_path}")
        
        # Load model using MLX-VLM (same as testing)
        from mlx_vlm import load
        logger.info("Loading MLX optimized LLaVA model...")
        model_instance, processor = load(model_path)
        logger.info("✅ MLX-LLaVA loaded successfully!")
            
    except ImportError as e:
        logger.error("MLX-VLM not installed. Please run: pip install mlx-vlm")
        model_instance = None
        processor = None
    except Exception as e:
        logger.error(f"❌ Failed to initialize model: {e}")
        model_instance = None
        processor = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model_instance, processor
    
    logger.info("🛑 Shutting down LLaVA MLX server...")
    
    if model_instance:
        try:
            del model_instance, processor
            logger.info("✅ Model unloaded successfully")
        except Exception as e:
            logger.error(f"❌ Error unloading model: {e}")

def signal_handler(signum, frame):
    """Handle system signals"""
    logger.info("\n🛑 Received stop signal, shutting down server...")
    sys.exit(0)

class LLaVAMLXServer:
    """LLaVA MLX Server wrapper"""
    
    def __init__(self, port=8080, host="0.0.0.0"):
        self.port = port
        self.host = host
        
    def start_server(self):
        """Start LLaVA MLX server"""
        print("🦙 LLaVA MLX Server")
        print("=" * 50)
        print(f"🚀 Starting server...")
        print(f"📦 Model: LLaVA-MLX")
        print(f"🌐 Host: {self.host}")
        print(f"🌐 Port: {self.port}")
        print(f"🍎 Device: MLX (Apple Silicon)")
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
    
    server = LLaVAMLXServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped")
    finally:
        logger.info("👋 Goodbye!")

if __name__ == "__main__":
    main()

 