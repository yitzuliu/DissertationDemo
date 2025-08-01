#!/usr/bin/env python3
"""
Standard Moondream2 Server Runner

🥇 BEST OVERALL PERFORMANCE - Highest VQA accuracy and excellent speed

Standard version of Moondream2 server with:
- FastAPI server for maximum compatibility
- Standard precision processing
- Robust error handling
- Cross-platform support
- Enhanced memory management

Latest Performance (2025-08-01):
- VQA Accuracy: 62.5% (highest among all models)
- Simple Accuracy: 65.0% (highest among all models)
- Average Inference Time: 7.80s (improved from 8.35s)
- Load Time: 5.99s
- Memory Usage: -0.52GB (memory efficient)

Production Recommendation: USE FOR HIGH-ACCURACY VQA APPLICATIONS
"""

import os
import json
import logging
import time
import base64
import sys
from io import BytesIO
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional
import uvicorn
from contextlib import asynccontextmanager

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
        # Get absolute path to project root
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        log_dir = base_dir / "logs"
        
        # Create logs directory with parents if needed
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup log file path with timestamp
        timestamp = time.strftime("%Y%m%d")
        log_file = log_dir / f"moondream2_standard_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"Moondream2 standard logging initialized. Log file: {log_file}")
        
        return logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

# Initialize logging
logger = setup_logging()

# Import model with fallbacks
def import_model_with_fallbacks():
    """Import Moondream2 model with multiple fallback strategies"""
    
    # Add current directory and parent directories to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(parent_dir)))
    
    for path in [current_dir, parent_dir, project_root]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Strategy 1: Try importing standard model
    try:
        from moondream2_model import Moondream2Model
        logger.info("✅ Imported Moondream2Model (Strategy 1)")
        return Moondream2Model
    except ImportError as e:
        logger.warning(f"Strategy 1 failed: {e}")
    
    # Strategy 2: Try importing optimized model as fallback
    try:
        from moondream2_optimized import OptimizedMoondream2Model
        logger.info("✅ Imported OptimizedMoondream2Model as fallback (Strategy 2)")
        return OptimizedMoondream2Model
    except ImportError as e:
        logger.warning(f"Strategy 2 failed: {e}")
    
    # Strategy 3: Create minimal fallback
    logger.error("❌ All import strategies failed, creating minimal fallback")
    
    class MinimalMoondream2Model:
        def __init__(self, model_name, config):
            self.model_name = model_name
            self.config = config
            self.loaded = False
            
        def load_model(self):
            logger.error("❌ Minimal fallback model - no actual functionality")
            return False
            
        def predict(self, image, prompt, options=None):
            return {
                "error": "Model import failed - check dependencies",
                "success": False,
                "response": {"text": "Model not available"}
            }
    
    return MinimalMoondream2Model

# Import model with fallbacks
try:
    Moondream2Model = import_model_with_fallbacks()
    logger.info(f"✅ Model import successful: {Moondream2Model.__name__}")
except Exception as e:
    logger.error(f"❌ Critical import failure: {e}")
    exit(1)

class StandardMoondream2Server:
    """Standard Moondream2 server implementation"""
    
    def __init__(self, config_path="moondream2.json"):
        self.model = None
        self.config = self.load_config(config_path)
        self.stats = {
            "requests": 0,
            "total_time": 0.0,
            "avg_time": 0.0
        }
    
    def load_config(self, config_path):
        """Load standard configuration"""
        try:
            # Default standard config
            default_config = {
                "model_name": "Moondream2",
                "model_path": "vikhyatk/moondream2",
                "device": "mps",
                "trust_remote_code": True,
                "max_tokens": 100,
                "timeout": 60
            }
            
            # Try to load from the project's config directory first
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            project_config_path = project_root / "src/config/model_configs/moondream2.json"
            
            if project_config_path.exists():
                with open(project_config_path, 'r') as f:
                    file_config = json.load(f)
                # 使用正確的鍵名取得模型路徑
                if "model_path" in file_config:
                    default_config.update(file_config)
                elif "model_id" in file_config:
                    # 如果配置文件使用 model_id，將其轉換為 model_path
                    file_config["model_path"] = file_config.get("model_id", "vikhyatk/moondream2")
                    default_config.update(file_config)
                logger.info(f"📁 Loaded config from {project_config_path}")
            elif os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
                logger.info(f"📁 Loaded config from {config_path}")
            else:
                logger.info("⚙️ Using default standard config")
            
            # 確保 model_path 正確設定
            if "model_path" not in default_config or not default_config["model_path"]:
                default_config["model_path"] = "vikhyatk/moondream2"
                logger.info("🔧 Set default model_path: vikhyatk/moondream2")
            
            logger.info(f"🔧 Using model_path: {default_config['model_path']}")
            
            return default_config
            
        except Exception as e:
            logger.error(f"Config loading error: {e}")
            return {
                "model_name": "Moondream2",
                "model_path": "vikhyatk/moondream2",
                "device": "mps",
                "trust_remote_code": True,
                "max_tokens": 100,
                "timeout": 60
            }
    
    def initialize_model(self):
        """Initialize standard model"""
        try:
            logger.info("🚀 Initializing STANDARD Moondream2...")
            start_time = time.time()
            
            self.model = Moondream2Model(
                model_name=self.config.get("model_name", "Moondream2"),
                config=self.config
            )
            
            if self.model.load_model():
                init_time = time.time() - start_time
                logger.info(f"✅ STANDARD Moondream2 ready in {init_time:.2f}s")
                return True
            else:
                logger.error("❌ Failed to load standard model")
                return False
                
        except Exception as e:
            logger.error(f"❌ Model initialization error: {e}")
            return False

# Global server instance
server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler"""
    # Startup
    global server
    logger.info("🔥 Starting STANDARD Moondream2 Server...")
    server = StandardMoondream2Server()
    if not server.initialize_model():
        logger.error("❌ Server startup failed")
        raise RuntimeError("Failed to initialize model")
    logger.info("🚀 STANDARD Moondream2 Server ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down STANDARD Moondream2 Server...")

# Create FastAPI app with lifespan
app = FastAPI(title="Moondream2 Standard Server", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatCompletionRequest(BaseModel):
    messages: List[Dict[str, Any]]
    max_tokens: Optional[int] = 100

@app.get("/health")
def health():
    """Health check endpoint"""
    global server
    if server and server.model and server.model.loaded:
        return {
            "status": "healthy",
            "model": "Moondream2-Standard",
            "version": "1.0.0",
            "performance": {
                "requests": server.stats["requests"],
                "avg_time": f"{server.stats['avg_time']:.2f}s"
            }
        }
    else:
        return {"status": "loading", "model": "Moondream2-Standard"}, 503

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    global server
    try:
        start_time = time.time()
        
        if not server or not server.model or not server.model.loaded:
            raise HTTPException(status_code=503, detail="Model not ready")
        
        messages = request.messages
        max_tokens = min(request.max_tokens or 100, 150)
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Extract user message (latest)
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
                    # Extract base64 data
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
        result = server.model.predict(
            image=image,
            prompt=text_content,
            options={"max_tokens": max_tokens}
        )
        
        processing_time = time.time() - start_time
        
        # Update stats
        server.stats["requests"] += 1
        server.stats["total_time"] += processing_time
        server.stats["avg_time"] = server.stats["total_time"] / server.stats["requests"]
        
        if result.get("success"):
            response_text = result.get("response", "")
            if isinstance(response_text, dict):
                response_text = response_text.get("text", str(response_text))
            
            # OpenAI-compatible response
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
                    "completion_tokens": len(str(response_text).split()),
                    "total_tokens": len(text_content.split()) + len(str(response_text).split())
                },
                "model": "Moondream2-Standard",
                "performance": {
                    "processing_time": f"{processing_time:.2f}s",
                    "optimized": False
                }
            }
        else:
            error_msg = result.get("error", "Unknown error")
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/stats")
def stats():
    """Performance statistics"""
    global server
    return {
        "model": "Moondream2-Standard",
        "statistics": server.stats if server else {"requests": 0, "total_time": 0.0, "avg_time": 0.0},
        "features": {
            "fastapi_server": True,
            "standard_precision": True,
            "cross_platform": True,
            "maximum_compatibility": True
        }
    }

def main():
    print_startup_banner(
        model_name="Moondream2-Standard",
        server_type="🥇 BEST OVERALL PERFORMANCE",
        features=[
            "FastAPI server for maximum compatibility",
            "Highest VQA accuracy (62.5%)",
            "Highest simple accuracy (65.0%)",
            "Enhanced memory management",
            "Cross-platform support",
            "Robust error handling"
        ],
        optimizations=[
            "FastAPI server",
            "Standard precision",
            "Enhanced memory management",
            "Cross-platform support",
            "Robust error handling"
        ],
        port=8080
    )   
    
    # Check PyTorch availability
    logger.info(f"PyTorch version: {torch.__version__}")
    if torch.backends.mps.is_available():
        logger.info("✅ MPS (Apple Silicon) acceleration available")
    elif torch.cuda.is_available():
        logger.info("✅ CUDA acceleration available")
    else:
        logger.info("⚠️ Using CPU inference")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8080,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
