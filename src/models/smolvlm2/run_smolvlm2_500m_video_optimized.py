#!/usr/bin/env python3
"""
SmolVLM2-500M-Video Optimized Server Launcher
Launch SmolVLM2-500M-Video-Instruct optimized model server with FastAPI
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
import tempfile
import os
import subprocess

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
    model: str = "SmolVLM2-500M-Video-Optimized"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7

app = FastAPI(title="SmolVLM2-500M-Video Optimized Server", version="1.0.0")

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
        "message": "SmolVLM2-500M-Video Optimized Server",
        "version": "1.0.0",
        "status": "running" if model_instance else "not loaded"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if model_instance:
        return {"status": "healthy", "model": "SmolVLM2-500M-Video-Optimized"}
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
        
        # Generate prediction using optimized SmolVLM2 (MLX-VLM preferred)
        try:
            # MLX version SmolVLM2 inference (optimized)
            try:
                logger.info("Using MLX-VLM command line for optimized SmolVLM2...")
                
                # Create temporary image file
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                    temp_image_path = tmp_file.name
                    image.save(temp_image_path)
                
                try:
                    # Use MLX-VLM command line tool with optimized settings
                    cmd = [
                        sys.executable, '-m', 'mlx_vlm.generate',
                        '--model', 'mlx-community/SmolVLM2-500M-Video-Instruct-mlx',
                        '--image', temp_image_path,
                        '--prompt', text_content,
                        '--max-tokens', str(request.max_tokens or 100),  # Optimized: lower default
                        '--temperature', '0.1'  # Optimized: lower temperature for consistency
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=45  # Optimized: shorter timeout
                    )
                    
                    if result.returncode == 0:
                        # Parse output, extract generated text
                        output_lines = result.stdout.split('\n')
                        response_text = ""
                        
                        # Keep full Assistant response
                        for i, line in enumerate(output_lines):
                            line = line.strip()
                            if line.startswith('Assistant:'):
                                # Find Assistant line
                                response_text = line
                                # Check if next line has content
                                if i + 1 < len(output_lines):
                                    next_line = output_lines[i + 1].strip()
                                    if next_line and not next_line.startswith('==========') and not next_line.startswith('Files:') and not next_line.startswith('Prompt:') and not next_line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
                                        # Next line has content, combine two lines
                                        response_text = f"{line} {next_line}"
                                break
                            elif line and not line.startswith('==========') and not line.startswith('Files:') and not line.startswith('Prompt:') and not line.startswith('Generation:') and not line.startswith('Peak memory:'):
                                # Find other non-system content lines
                                if not response_text:
                                    response_text = line
                    else:
                        logger.error(f"MLX-VLM command failed: {result.stderr}")
                        raise Exception(f"MLX-VLM command failed: {result.stderr}")
                        
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
            
            except Exception as e:
                logger.error(f"MLX-VLM SmolVLM2 optimized inference failed: {e}")
                raise HTTPException(status_code=500, detail=f"Optimized MLX-VLM inference failed: {str(e)}")
            
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
                "prompt_tokens": 50,  # Optimized: lower estimate
                "completion_tokens": len(response_text.split()),
                "total_tokens": 50 + len(response_text.split())
            },
            "model": "SmolVLM2-500M-Video-Optimized"
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
    
    logger.info("🚀 Starting SmolVLM2-500M-Video Optimized server...")
    
    try:
        # Load model configuration from config system
        config = config_manager.load_model_config("smolvlm2_500m_video_optimized")
        model_path = config.get("model_path", "mlx-community/SmolVLM2-500M-Video-Instruct-mlx")
        
        logger.info(f"Loading SmolVLM2-500M-Video Optimized model: {model_path}")
        
        # Use MLX-VLM for optimized performance (required for optimized version)
        try:
            from mlx_vlm import load
            logger.info("Loading MLX-VLM optimized SmolVLM2 model...")
            model_instance, processor = load(model_path)
            logger.info("✅ MLX-VLM SmolVLM2 Optimized loaded successfully!")
            
            # Mark as MLX model for special inference
            model_instance._is_mlx_model = True
            
        except ImportError as e:
            logger.error("MLX-VLM not installed. Optimized version requires MLX-VLM.")
            logger.error("Please run: pip install mlx-vlm")
            model_instance = None
            processor = None
            
        except Exception as e:
            logger.error(f"❌ Failed to load optimized model: {str(e)}")
            model_instance = None
            processor = None
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize optimized model: {e}")
        model_instance = None
        processor = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model_instance, processor
    
    logger.info("🛑 Shutting down SmolVLM2-500M-Video Optimized server...")
    
    if model_instance:
        try:
            del model_instance, processor
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            logger.info("✅ Optimized model unloaded successfully")
        except Exception as e:
            logger.error(f"❌ Error unloading optimized model: {e}")

def signal_handler(signum, frame):
    """Handle system signals"""
    logger.info("\n🛑 Received stop signal, shutting down server...")
    sys.exit(0)

class SmolVLM2OptimizedServer:
    """SmolVLM2-500M-Video Optimized Server wrapper"""
    
    def __init__(self, port=8080, host="0.0.0.0"):
        self.port = port
        self.host = host
        
    def start_server(self):
        """Start SmolVLM2-500M-Video Optimized server"""
        print("🎬⚡ SmolVLM2-500M-Video Optimized Server")
        print("=" * 50)
        print(f"🚀 Starting optimized server...")
        print(f"📦 Model: SmolVLM2-500M-Video-Optimized")
        print(f"🌐 Host: {self.host}")
        print(f"🌐 Port: {self.port}")
        print(f"🍎⚡ Device: MLX (Apple Silicon Optimized)")
        print(f"⚡ Features: Faster inference, lower memory usage")
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
            logger.error(f"❌ Optimized server startup failed: {e}")
            return False

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server = SmolVLM2OptimizedServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Optimized server stopped")
    finally:
        logger.info("👋 Goodbye!")

if __name__ == "__main__":
    main()