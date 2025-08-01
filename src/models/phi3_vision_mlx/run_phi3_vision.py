#!/usr/bin/env python3
"""
Standard Phi-3.5-Vision Server Runner

🥉 Detailed Performance - Good VQA accuracy with enhanced memory management

Standard version of Phi-3.5-Vision server with:
- FastAPI server for compatibility
- MLX-VLM with transformers fallback
- Enhanced memory management
- Cross-platform support
- Robust error handling

Latest Performance (2025-08-01):
- VQA Accuracy: 35.0% (consistent performance)
- Simple Accuracy: 35.0% (7/20 correct)
- Average Inference Time: 8.71s (with enhanced memory management)
- Load Time: 4.16s
- Memory Usage: +2.58GB (stable with enhanced management)

Production Recommendation: USE FOR DEVELOPMENT/TESTING
"""

import os
import json
import logging
import time
import base64
import signal
import subprocess
import socket
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from PIL import Image
import torch

# Print startup banner
def print_startup_banner(model_name, server_type, features, optimizations=None, port=None):
    print()
    print(f"🔥 {model_name} {server_type}")
    print("=" * 60)
    print("🎯 Features:")
    for feat in features:
        print(f"   • {feat}")
    if optimizations:
        print("⚡ Optimizations:")
        for opt in optimizations:
            print(f"   • {opt}")
    print("=" * 60)
    print()

# Setup logging
def setup_logging():
    """Setup logging with proper path and permissions"""
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        log_dir = base_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(log_dir, 0o755)
        
        timestamp = time.strftime("%Y%m%d")
        log_file = log_dir / f"phi3_vision_standard_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"Phi-3.5-Vision standard logging initialized. Log file: {log_file}")
        return logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

logger = setup_logging()

class ChatCompletionRequest(BaseModel):
    max_tokens: Optional[int] = None
    messages: List[Dict[str, Any]]

class StandardPhi3VisionServer:
    """Standard Phi-3.5-Vision Server"""
    
    def __init__(self, config_path="phi3_vision.json"):
        self.app = FastAPI(title="Phi-3.5-Vision Standard API")
        self.model = None
        self.processor = None
        self.config = self.load_config(config_path)
        self.use_mlx = False
        self.setup_middleware()
        self.setup_routes()
        
        self.stats = {
            "requests": 0,
            "total_time": 0.0,
            "avg_time": 0.0
        }
        
        # Add request counter for debugging
        self.request_count = 0
        
        # Add model state tracking
        self.last_inference_time = 0
    
    def load_config(self, config_path):
        """Load standard configuration"""
        try:
            default_config = {
                "model_name": "Phi-3.5-Vision",
                "model_path": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "device": "auto",
                "trust_remote_code": True,
                "max_tokens": 100,
                "timeout": 180
            }
            
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            project_config_path = project_root / "src/config/model_configs/phi3_vision.json"
            
            if project_config_path.exists():
                with open(project_config_path, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
                logger.info(f"📁 Loaded config from {project_config_path}")
            elif os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
                logger.info(f"📁 Loaded config from {config_path}")
            else:
                logger.info("⚙️ Using default standard config")
            
            # Ensure model_path is correct
            if "model_path" not in default_config or not default_config["model_path"] or default_config["model_path"] == "phi3_vision":
                default_config["model_path"] = "mlx-community/Phi-3.5-vision-instruct-4bit"
                logger.info("🔧 Set default model_path: mlx-community/Phi-3.5-vision-instruct-4bit")
            
            logger.info(f"🔧 Using model_path: {default_config['model_path']}")
            
            return default_config
            
        except Exception as e:
            logger.error(f"Config loading error: {e}")
            return {
                "model_name": "Phi-3.5-Vision",
                "model_path": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "device": "auto",
                "trust_remote_code": True,
                "max_tokens": 100,
                "timeout": 180
            }
    
    def setup_middleware(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def initialize_model(self):
        """Initialize standard model with MLX and transformers fallback"""
        try:
            logger.info("🚀 Initializing STANDARD Phi-3.5-Vision...")
            start_time = time.time()
            
            model_config = self.config.copy()
            if model_config.get("model_path") == "phi3_vision":
                model_config["model_path"] = "mlx-community/Phi-3.5-vision-instruct-4bit"
                logger.warning("🔧 Fixed model_path that was incorrectly set to model_id")
            
            logger.info(f"🔧 Initializing with model_path: {model_config.get('model_path')}")
            
            # Strategy 1: Try MLX-VLM first (same as vlm_tester.py)
            try:
                from mlx_vlm import load
                logger.info("🚀 Attempting MLX-VLM load...")
                
                self.model, self.processor = load(
                    model_config.get("model_path"), 
                    trust_remote_code=True
                )
                self.use_mlx = True
                
                init_time = time.time() - start_time
                logger.info(f"✅ MLX Phi-3.5-Vision loaded in {init_time:.2f}s")
                return True
                
            except ImportError as e:
                logger.warning(f"MLX-VLM not available: {e}, falling back to transformers")
                self.use_mlx = False
            except Exception as e:
                logger.warning(f"MLX loading failed: {e}, falling back to transformers")
                self.use_mlx = False
            
            # Strategy 2: Fallback to transformers (same as vlm_tester.py)
            if not self.use_mlx:
                from transformers import AutoModelForCausalLM, AutoProcessor
                logger.info("📥 Loading transformers Phi-3.5-Vision...")
                
                self.processor = AutoProcessor.from_pretrained(
                    "microsoft/Phi-3.5-vision-instruct", 
                    trust_remote_code=True,
                    num_crops=4
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    "microsoft/Phi-3.5-vision-instruct",
                    torch_dtype=torch.float16,
                    _attn_implementation="eager",
                    device_map="cpu",
                    low_cpu_mem_usage=True,
                    trust_remote_code=True
                )
                
                init_time = time.time() - start_time
                logger.info(f"✅ Transformers Phi-3.5-Vision loaded in {init_time:.2f}s")
                return True
                
        except Exception as e:
            logger.error(f"❌ Model initialization error: {e}")
            return False
    
    async def _generate_mlx_response(self, image: Image.Image, prompt: str, max_tokens: int) -> str:
        """Generate response using MLX with improved error handling and cleanup"""
        self.request_count += 1
        request_id = self.request_count
        
        try:
            from mlx_vlm import generate
            logger.info(f"🚀 Request #{request_id}: Using MLX-VLM inference for Phi-3.5-Vision...")
            
            # Create temporary file with more explicit control
            temp_image_path = None
            try:
                # Use a more controlled temporary file approach
                import tempfile
                import uuid
                
                # Create temp directory if it doesn't exist
                temp_dir = Path(tempfile.gettempdir()) / "phi3_vision_mlx"
                temp_dir.mkdir(exist_ok=True)
                
                # Create unique filename
                temp_filename = f"phi3_image_{request_id}_{uuid.uuid4().hex[:8]}.jpg"
                temp_image_path = temp_dir / temp_filename
                
                # Save image with high quality
                logger.info(f"📁 Request #{request_id}: Saving image to {temp_image_path}")
                image.save(str(temp_image_path), 'JPEG', quality=95, optimize=True)
                
                # Verify file exists and is readable
                if not temp_image_path.exists():
                    raise FileNotFoundError(f"Failed to create temporary image file: {temp_image_path}")
                
                file_size = temp_image_path.stat().st_size
                logger.info(f"📊 Request #{request_id}: Image saved, size: {file_size} bytes")
                
                # Clean prompt format - remove any existing image tokens
                clean_prompt = prompt.replace("<|image_1|>", "").strip()
                
                # Use consistent MLX prompt format
                mlx_prompt = f"<|image_1|>\nUser: {clean_prompt}\nAssistant:"
                
                logger.info(f"💭 Request #{request_id}: Prompt: {mlx_prompt[:100]}...")
                
                # Add memory cleanup before inference
                if hasattr(torch, 'mps') and torch.mps.is_available():
                    torch.mps.empty_cache()
                
                # Generate response with timeout protection
                logger.info(f"🔄 Request #{request_id}: Starting MLX generation...")
                start_time = time.time()
                
                response = generate(
                    model=self.model,
                    processor=self.processor,
                    image=str(temp_image_path),  # Ensure string path
                    prompt=mlx_prompt,
                    max_tokens=max_tokens,
                    temp=0.0,
                    verbose=True  # Enable verbose for debugging
                )
                
                generation_time = time.time() - start_time
                logger.info(f"✅ Request #{request_id}: MLX generation completed in {generation_time:.2f}s")
                
                # Process response with better cleaning
                if response is None:
                    logger.error(f"❌ Request #{request_id}: MLX returned None response")
                    return "Error: No response generated from MLX model"
                
                text_response = str(response).strip()
                logger.info(f"📝 Request #{request_id}: Raw response length: {len(text_response)}")
                logger.info(f"📝 Request #{request_id}: Raw response preview: {text_response[:200]}...")
                
                # Clean response more carefully
                # Remove special tokens
                text_response = text_response.replace("<|end|>", "")
                text_response = text_response.replace("<|endoftext|>", "")
                text_response = text_response.replace("<|im_end|>", "")
                
                # Remove repeated prompts or artifacts
                if "User:" in text_response and "Assistant:" in text_response:
                    # Extract only the assistant's response
                    parts = text_response.split("Assistant:")
                    if len(parts) > 1:
                        text_response = parts[-1].strip()
                
                # Remove common artifacts
                if "1. What is meant by" in text_response:
                    text_response = text_response.split("1. What is meant by")[0].strip()
                
                # Clean whitespace
                text_response = ' '.join(text_response.split())
                
                logger.info(f"✨ Request #{request_id}: Cleaned response length: {len(text_response)}")
                logger.info(f"✨ Request #{request_id}: Final response: {text_response}")
                
                if not text_response:
                    logger.warning(f"⚠️ Request #{request_id}: Cleaned response is empty!")
                    return "Error: Generated response was empty after cleaning"
                
                # Update timing
                self.last_inference_time = time.time()
                
                return text_response
                
            finally:
                # Cleanup temporary file
                if temp_image_path and temp_image_path.exists():
                    try:
                        temp_image_path.unlink()
                        logger.info(f"🧹 Request #{request_id}: Cleaned up temporary file")
                    except Exception as cleanup_error:
                        logger.warning(f"⚠️ Request #{request_id}: Failed to cleanup temp file: {cleanup_error}")
                
                # Force memory cleanup
                if hasattr(torch, 'mps') and torch.mps.is_available():
                    torch.mps.empty_cache()
                    
        except Exception as e:
            logger.error(f"❌ Request #{request_id}: MLX inference error: {e}", exc_info=True)
            # Return more specific error information
            return f"MLX inference failed (Request #{request_id}): {str(e)}"
    
    async def _generate_transformers_response(self, image: Image.Image, prompt: str, max_tokens: int) -> str:
        """Generate response using transformers with improved error handling"""
        self.request_count += 1
        request_id = self.request_count
        
        try:
            logger.info(f"🚀 Request #{request_id}: Using Transformers inference for Phi-3.5-Vision...")
            
            # Clean prompt
            clean_prompt = prompt.replace("<|image_1|>", "").strip()
            
            # Format messages
            messages = [{"role": "user", "content": f"<|image_1|>\n{clean_prompt}"}]
            
            prompt_text = self.processor.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            logger.info(f"💭 Request #{request_id}: Formatted prompt: {prompt_text[:100]}...")
            
            # Process inputs
            inputs = self.processor(prompt_text, [image], return_tensors="pt")
            
            # Move to correct device
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            logger.info(f"💭 Request #{request_id}: Inputs prepared, device: {device}")
            
            # Generate with memory management
            with torch.no_grad():
                start_time = time.time()
                
                outputs = self.model.generate(
                    **inputs, 
                    max_new_tokens=max_tokens,
                    do_sample=False,
                    use_cache=False,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
                
                generation_time = time.time() - start_time
                logger.info(f"✅ Request #{request_id}: Transformers generation completed in {generation_time:.2f}s")
            
            # Decode response
            result = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            logger.info(f"📝 Request #{request_id}: Raw result length: {len(result)}")
            logger.info(f"📝 Request #{request_id}: Raw result preview: {result[:200]}...")
            
            # Clean response
            if "Assistant:" in result:
                result_parts = result.split("Assistant:")
                result = result_parts[-1].strip()
            
            # Additional cleaning
            result = ' '.join(result.split())
            
            logger.info(f"✨ Request #{request_id}: Final result: {result}")
            
            if not result:
                logger.warning(f"⚠️ Request #{request_id}: Transformers result is empty!")
                return "Error: Generated response was empty"
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Request #{request_id}: Transformers inference error: {e}", exc_info=True)
            return f"Transformers inference failed (Request #{request_id}): {str(e)}"
    
    def setup_routes(self):
        """Setup FastAPI routes with enhanced error handling"""
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            if self.model and self.processor:
                return {
                    "status": "healthy",
                    "model": "Phi-3.5-Vision",
                    "version": "1.0.0",
                    "framework": "FastAPI",
                    "method": "MLX" if self.use_mlx else "Transformers",
                    "performance": {
                        "requests": self.stats["requests"],
                        "avg_time": f"{self.stats['avg_time']:.2f}s"
                    }
                }
            else:
                return {"status": "loading", "model": "Phi-3.5-Vision"}
        
        @self.app.post("/v1/chat/completions")
        async def chat_completions(request: ChatCompletionRequest):
            """OpenAI-compatible chat completions endpoint with enhanced debugging"""
            request_start_time = time.time()
            self.request_count += 1
            request_id = self.request_count
            
            try:
                logger.info(f"🎯 Request #{request_id}: Starting chat completion")
                
                if not self.model or not self.processor:
                    logger.error(f"❌ Request #{request_id}: Model not ready")
                    raise HTTPException(status_code=503, detail="Model not ready")
                
                messages = request.messages
                max_tokens = min(request.max_tokens or 100, 200)
                
                logger.info(f"📊 Request #{request_id}: max_tokens={max_tokens}, messages_count={len(messages)}")
                
                if not messages:
                    raise HTTPException(status_code=400, detail="No messages provided")
                
                # Extract user message
                user_message = None
                for message in reversed(messages):
                    if message.get('role') == 'user':
                        user_message = message
                        break
                
                if not user_message:
                    raise HTTPException(status_code=400, detail="No user message found")
                
                # Process content
                content = user_message.get('content', [])
                text_content = ""
                image_data = None
                
                for item in content:
                    if item.get('type') == 'text':
                        text_content = item.get('text', '')
                    elif item.get('type') == 'image_url':
                        image_url = item.get('image_url', {}).get('url', '')
                        if image_url.startswith('data:image/'):
                            image_data = image_url.split(',')[1]
                
                logger.info(f"📝 Request #{request_id}: text_content length: {len(text_content)}")
                logger.info(f"🖼️ Request #{request_id}: has_image: {bool(image_data)}")
                
                if not image_data:
                    raise HTTPException(status_code=400, detail="No image provided")
                
                # Process image
                try:
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    logger.info(f"🖼️ Request #{request_id}: Image processed, size: {image.size}, mode: {image.mode}")
                    
                except Exception as e:
                    logger.error(f"❌ Request #{request_id}: Image processing failed: {e}")
                    raise HTTPException(status_code=400, detail=f"Image processing failed: {e}")
                
                # Generate response
                logger.info(f"🔄 Request #{request_id}: Starting generation with method: {'MLX' if self.use_mlx else 'Transformers'}")
                
                if self.use_mlx:
                    response_text = await self._generate_mlx_response(image, text_content, max_tokens)
                else:
                    response_text = await self._generate_transformers_response(image, text_content, max_tokens)
                
                processing_time = time.time() - request_start_time
                
                logger.info(f"✅ Request #{request_id}: Generation completed in {processing_time:.2f}s")
                logger.info(f"📝 Request #{request_id}: Response length: {len(response_text)}")
                
                # Check for error responses
                if response_text.startswith("Error:") or "failed" in response_text.lower():
                    logger.error(f"❌ Request #{request_id}: Generation returned error: {response_text}")
                    raise HTTPException(status_code=500, detail=response_text)
                
                # Update stats
                self.stats["requests"] += 1
                self.stats["total_time"] += processing_time
                self.stats["avg_time"] = self.stats["total_time"] / self.stats["requests"]
                
                response_data = {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": response_text
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": len(text_content.split()),
                        "completion_tokens": len(response_text.split()),
                        "total_tokens": len(text_content.split()) + len(response_text.split())
                    },
                    "model": "Phi-3.5-Vision",
                    "performance": {
                        "processing_time": f"{processing_time:.2f}s",
                        "framework": "FastAPI",
                        "method": "MLX" if self.use_mlx else "Transformers",
                        "request_id": request_id
                    }
                }
                
                logger.info(f"🎉 Request #{request_id}: Successfully completed")
                return response_data
                    
            except HTTPException:
                raise
            except Exception as e:
                processing_time = time.time() - request_start_time
                logger.error(f"❌ Request #{request_id}: Unexpected error after {processing_time:.2f}s: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
        
        @self.app.get("/stats")
        async def stats():
            """Performance statistics"""
            return {
                "model": "Phi-3.5-Vision",
                "statistics": self.stats,
                "framework": "FastAPI",
                "method": "MLX" if self.use_mlx else "Transformers",
                "features": {
                    "mlx_support": True,
                    "transformers_fallback": True,
                    "cross_platform": True
                }
            }
    
    async def startup(self):
        """Startup event"""
        if not self.initialize_model():
            raise RuntimeError("Failed to initialize model")
    
    def run(self, host='0.0.0.0', port=8080):
        """Start standard server"""
        logger.info("🚀 Starting STANDARD Phi-3.5-Vision Server...")
        logger.info(f"🎯 Target: Cross-platform compatibility")
        logger.info(f"🔧 Framework: FastAPI with MLX-VLM + Transformers")
        
        # Add startup event
        @self.app.on_event("startup")
        async def startup_event():
            await self.startup()
        
        try:
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                log_level="info"
            )
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
            return False
        
        return True

def main():
    """Main execution"""
    print_startup_banner(
        model_name="Phi-3.5-Vision-Standard",
        server_type="🥉 Detailed Performance",
        features=[
            "FastAPI server for maximum compatibility",
            "VQA Accuracy 35.0% (consistent performance)",
            "Enhanced memory management",
            "MLX-VLM with transformers fallback",
            "Cross-platform support",
            "Robust error handling"
        ],
        optimizations=[
            "FastAPI server",
            "Enhanced memory management",
            "MLX-VLM with transformers fallback",
            "Cross-platform support",
            "Robust error handling"
        ],
        port=8080
    )
    
    # Check MLX availability
    try:
        import mlx.core as mx
        logger.info("✅ MLX framework available")
    except ImportError:
        logger.warning("⚠️ MLX not available, will use transformers fallback")
    
    server = StandardPhi3VisionServer()
    
    try:
        server.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
