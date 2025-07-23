#!/usr/bin/env python3
"""
SmolVLM2-500M-Video Server Launcher
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
    model: str = "SmolVLM2-500M-Video"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7

app = FastAPI(title="SmolVLM2-500M-Video Server", version="1.0.0")

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
        "message": "SmolVLM2-500M-Video Server",
        "version": "1.0.0",
        "status": "running" if model_instance else "not loaded"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if model_instance:
        return {"status": "healthy", "model": "SmolVLM2-500M-Video"}
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
        
        # Generate prediction using SmolVLM2 (same as testing)
        try:
            # Check if it's an MLX model
            if hasattr(model_instance, '_is_mlx_model'):
                # MLX version SmolVLM2 inference
                try:
                    logger.info("Using MLX-VLM command line for SmolVLM2...")
                    
                    # Create temporary image file
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                        temp_image_path = tmp_file.name
                        image.save(temp_image_path)
                    
                    try:
                        # Use MLX-VLM command line tool
                        cmd = [
                            sys.executable, '-m', 'mlx_vlm.generate',
                            '--model', 'mlx-community/SmolVLM2-500M-Video-Instruct-mlx',
                            '--image', temp_image_path,
                            '--prompt', text_content,
                            '--max-tokens', str(request.max_tokens or 150),
                            '--temperature', '0.0'
                        ]
                        
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=60
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
                    logger.error(f"MLX-VLM SmolVLM2 inference failed: {e}")
                    raise HTTPException(status_code=500, detail=f"MLX-VLM inference failed: {str(e)}")
            else:
                # Standard SmolVLM2 inference method
                from transformers import AutoProcessor, AutoModelForImageTextToText
                
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": image},
                            {"type": "text", "text": text_content}
                        ]
                    }
                ]
                input_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=input_text, images=image, return_tensors="pt")
                
                with torch.no_grad():
                    outputs = model_instance.generate(**inputs, max_new_tokens=request.max_tokens or 150, do_sample=False)
                
                response_text = processor.decode(outputs[0], skip_special_tokens=True)
                
                # Clean up response
                if input_text in response_text:
                    response_text = response_text.replace(input_text, "").strip()
            
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
                "prompt_tokens": 100,  # Estimated
                "completion_tokens": len(response_text.split()),
                "total_tokens": 100 + len(response_text.split())
            },
            "model": "SmolVLM2-500M-Video"
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
    
    logger.info("🚀 Starting SmolVLM2-500M-Video server...")
    
    try:
        # Load model configuration from config system
        config = config_manager.load_model_config("smolvlm2_500m_video")
        model_path = config.get("model_path", "mlx-community/SmolVLM2-500M-Video-Instruct-mlx")
        
        logger.info(f"Loading SmolVLM2-500M-Video model: {model_path}")
        
        # Try MLX-VLM first (same as testing)
        try:
            from mlx_vlm import load
            logger.info("Loading MLX-VLM optimized SmolVLM2 model...")
            model_instance, processor = load(model_path)
            logger.info("✅ MLX-VLM SmolVLM2 loaded successfully!")
            
            # Mark as MLX model for special inference
            model_instance._is_mlx_model = True
            
        except ImportError as e:
            logger.warning("MLX-VLM not installed, using original SmolVLM2 model...")
            logger.info("Please run: pip install mlx-vlm")
            # Fallback to original SmolVLM2 model
            from transformers import AutoProcessor, AutoModelForImageTextToText
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model_instance = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            logger.info("✅ Fallback SmolVLM2 model loaded successfully")
            
        except Exception as e:
            logger.error(f"MLX-VLM loading failed: {str(e)}")
            logger.info("Using original SmolVLM2 model as fallback...")
            # Fallback to original SmolVLM2 model
            from transformers import AutoProcessor, AutoModelForImageTextToText
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model_instance = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            logger.info("✅ Fallback SmolVLM2 model loaded successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize model: {e}")
        model_instance = None
        processor = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model_instance, processor
    
    logger.info("🛑 Shutting down SmolVLM2-500M-Video server...")
    
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

class SmolVLM2Server:
    """SmolVLM2-500M-Video Server wrapper"""
    
    def __init__(self, port=8080, host="0.0.0.0"):
        self.port = port
        self.host = host
        
    def start_server(self):
        """Start SmolVLM2-500M-Video server"""
        print("🎬 SmolVLM2-500M-Video Server")
        print("=" * 50)
        print(f"🚀 Starting server...")
        print(f"📦 Model: SmolVLM2-500M-Video")
        print(f"🌐 Host: {self.host}")
        print(f"🌐 Port: {self.port}")
        print(f"🍎 Device: MLX/MPS (Apple Silicon)")
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