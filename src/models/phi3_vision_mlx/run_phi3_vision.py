#!/usr/bin/env python3
"""
Standard Phi-3.5-Vision Server Runner

Standard version of Phi-3.5-Vision server with:
- FastAPI server for compatibility
- MLX-VLM with transformers fallback
- Cross-platform support
- Robust error handling
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
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from PIL import Image
import torch

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

# Import model with fallbacks
def import_model_with_fallbacks():
    """Import Phi-3.5-Vision model with multiple fallback strategies"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(parent_dir)))
    
    for path in [current_dir, parent_dir, project_root]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Strategy 1: Try importing standard model
    try:
        from phi3_vision_model import Phi3VisionModel
        logger.info("✅ Imported Phi3VisionModel (Strategy 1)")
        return Phi3VisionModel
    except ImportError as e:
        logger.warning(f"Strategy 1 failed: {e}")
    
    # Strategy 2: Create minimal implementation
    logger.error("❌ Model import failed, creating minimal implementation")
    
    class MinimalPhi3VisionModel:
        def __init__(self, model_name, config):
            self.model_name = model_name
            self.config = config
            self.loaded = False
            
        def load_model(self):
            logger.error("❌ Minimal model - no actual functionality")
            return False
            
        def predict(self, image, prompt, options=None):
            return {
                "error": "Model import failed - check dependencies",
                "success": False,
                "response": {"text": "Model not available"}
            }
    
    return MinimalPhi3VisionModel

Phi3VisionModel = import_model_with_fallbacks()

class ChatCompletionRequest(BaseModel):
    max_tokens: Optional[int] = None
    messages: List[Dict[str, Any]]

class StandardPhi3VisionServer:
    """Standard Phi-3.5-Vision Server"""
    
    def __init__(self, config_path="phi3_vision.json"):
        self.app = FastAPI(title="Phi-3.5-Vision Standard API")
        self.model = None
        self.config = self.load_config(config_path)
        self.setup_middleware()
        self.setup_routes()
        
        self.stats = {
            "requests": 0,
            "total_time": 0.0,
            "avg_time": 0.0
        }
    
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
                # 正確處理配置文件合併
                default_config.update(file_config)
                logger.info(f"📁 Loaded config from {project_config_path}")
            elif os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
                logger.info(f"📁 Loaded config from {config_path}")
            else:
                logger.info("⚙️ Using default standard config")
            
            # 確保 model_path 正確設定並避免使用 model_id 作為路徑
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
        """Initialize standard model"""
        try:
            logger.info("🚀 Initializing STANDARD Phi-3.5-Vision...")
            start_time = time.time()
            
            # 確保傳遞正確的配置
            model_config = self.config.copy()
            # 確保 model_path 不是 model_id
            if model_config.get("model_path") == "phi3_vision":
                model_config["model_path"] = "mlx-community/Phi-3.5-vision-instruct-4bit"
                logger.warning("🔧 Fixed model_path that was incorrectly set to model_id")
            
            logger.info(f"🔧 Initializing with model_path: {model_config.get('model_path')}")
            
            self.model = Phi3VisionModel(
                model_name=model_config.get("model_name", "Phi-3.5-Vision"),
                config=model_config
            )
            
            if self.model.load_model():
                init_time = time.time() - start_time
                logger.info(f"✅ STANDARD Phi-3.5-Vision ready in {init_time:.2f}s")
                return True
            else:
                logger.error("❌ Failed to load standard model")
                return False
                
        except Exception as e:
            logger.error(f"❌ Model initialization error: {e}")
            return False
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            if self.model and hasattr(self.model, 'loaded') and self.model.loaded:
                return {
                    "status": "healthy",
                    "model": "Phi-3.5-Vision",
                    "version": "1.0.0",
                    "framework": "FastAPI",
                    "performance": {
                        "requests": self.stats["requests"],
                        "avg_time": f"{self.stats['avg_time']:.2f}s"
                    }
                }
            else:
                return {"status": "loading", "model": "Phi-3.5-Vision"}
        
        @self.app.post("/v1/chat/completions")
        async def chat_completions(request: ChatCompletionRequest):
            """OpenAI-compatible chat completions endpoint"""
            try:
                start_time = time.time()
                
                if not self.model or not hasattr(self.model, 'loaded') or not self.model.loaded:
                    raise HTTPException(status_code=503, detail="Model not ready")
                
                messages = request.messages
                max_tokens = min(request.max_tokens or 100, 200)
                
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
                
                if not image_data:
                    raise HTTPException(status_code=400, detail="No image provided")
                
                # Process image
                try:
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Image processing failed: {e}")
                
                # Generate response
                result = self.model.predict(
                    image=image,
                    prompt=text_content,
                    options={"max_tokens": max_tokens}
                )
                
                processing_time = time.time() - start_time
                
                # Update stats
                self.stats["requests"] += 1
                self.stats["total_time"] += processing_time
                self.stats["avg_time"] = self.stats["total_time"] / self.stats["requests"]
                
                if result.get("success"):
                    response_text = result.get("response", {}).get("text", "")
                    
                    return {
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
                            "framework": "FastAPI"
                        }
                    }
                else:
                    raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Request processing error: {e}")
                raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
        
        @self.app.get("/stats")
        async def stats():
            """Performance statistics"""
            return {
                "model": "Phi-3.5-Vision",
                "statistics": self.stats,
                "framework": "FastAPI",
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
    print("🔥 STANDARD Phi-3.5-Vision Server")
    print("=" * 50)
    print("🎯 Features:")
    print("   • FastAPI server for maximum compatibility")
    print("   • MLX-VLM with transformers fallback")
    print("   • Cross-platform support")
    print("   • Robust error handling")
    print("=" * 50)
    
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
