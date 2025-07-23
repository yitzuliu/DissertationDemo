#!/usr/bin/env python3
"""
Moondream2 Server Launcher
Launch Moondream2 model server with FastAPI (Standard Version)
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
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Add the project root to the path for base imports
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
    model: str = "Moondream2"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7

class ChatCompletionResponse(BaseModel):
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

app = FastAPI(title="Moondream2 Server", version="1.0.0")

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
        "message": "Moondream2 Server (Standard Version)",
        "version": "1.0.0",
        "status": "running" if model_instance else "not loaded"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if model_instance:
        return {"status": "healthy", "model": "Moondream2-Standard"}
    else:
        raise HTTPException(status_code=503, detail="Model not loaded")

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    global model_instance
    
    if not model_instance:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    # Model is loaded during startup, no need to check .loaded attribute
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
        
        # Generate prediction using Moondream2 API (same as testing)
        try:
            device = next(model_instance.parameters()).device
            enc_image = model_instance.encode_image(image)
            if hasattr(enc_image, 'to'):
                enc_image = enc_image.to(device)
            
            response_text = model_instance.answer_question(enc_image, text_content, processor)
            
            # Clean up response
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
            "model": "Moondream2-Standard"
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
    
    logger.info("🚀 Starting Moondream2 server (Standard Version)...")
    
    try:
        # Load model configuration from config system
        config = config_manager.load_model_config("moondream2")
        model_path = config.get("model_path", "vikhyatk/moondream2")
        
        logger.info(f"Loading Moondream2 model: {model_path}")
        
        # Load model using the same pattern as testing
        model_instance = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True)
        processor = AutoTokenizer.from_pretrained(model_path)
        
        # Move model to appropriate device
        if torch.backends.mps.is_available():
            model_instance = model_instance.to('mps')
            logger.info("✅ Model moved to MPS device")
        
        logger.info("✅ Moondream2 model loaded successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize model: {e}")
        model_instance = None
        processor = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model_instance, processor
    
    logger.info("🛑 Shutting down Moondream2 server...")
    
    if model_instance:
        try:
            del model_instance, processor
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            logger.info("✅ Model unloaded successfully")
        except Exception as e:
            logger.error(f"❌ Error unloading model: {e}")

def signal_handler(signum, frame):
    """Handle system signals"""
    logger.info("\n🛑 Received stop signal, shutting down server...")
    sys.exit(0)

class Moondream2Server:
    """Moondream2 Server wrapper"""
    
    def __init__(self, port=8080, host="0.0.0.0"):
        self.port = port
        self.host = host
        
    def start_server(self):
        """Start Moondream2 server"""
        print("🌙 Moondream2 Server (Standard Version)")
        print("=" * 50)
        print(f"🚀 Starting server...")
        print(f"📦 Model: Moondream2-Standard")
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
    
    server = Moondream2Server()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped")
    finally:
        logger.info("👋 Goodbye!")

if __name__ == "__main__":
    main() 