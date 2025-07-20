#!/usr/bin/env python3
"""
Optimized Phi-3.5-Vision Server Runner

High-performance version of Phi-3.5-Vision server with:
- MLX optimization for Apple Silicon
- INT4 quantization
- Fast inference pipeline
- Image caching
- Fallback to transformers
"""

import os
import json
import logging
import time
import base64
from io import BytesIO
from flask import Flask, request, jsonify
from PIL import Image
import torch
from pathlib import Path

# Setup logging
def setup_logging():
    """Setup logging with proper path and permissions"""
    try:
        # Get absolute path to project root (4 levels up from current file)
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        log_dir = base_dir / "logs"
        
        # Create logs directory with parents if needed
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure proper directory permissions
        os.chmod(log_dir, 0o755)
        
        # Setup log file path with timestamp
        timestamp = time.strftime("%Y%m%d")
        log_file = log_dir / f"model_{timestamp}.log"
        
        # Configure file handler with UTF-8 encoding
        file_handler = logging.FileHandler(
            filename=log_file,
            mode='a',
            encoding='utf-8'
        )
        
        # Ensure proper file permissions
        os.chmod(log_file, 0o644)
        
        # Configure console handler
        console_handler = logging.StreamHandler()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set logging level
        root_logger.setLevel(logging.INFO)
        
        # Add handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log initialization success
        root_logger.info(f"Model logging initialized. Log file: {log_file}")
        
        return root_logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

# Initialize logging
logger = setup_logging()

# Import optimized model
try:
    from phi3_vision_optimized import OptimizedPhi3VisionModel
    logger.info("✅ Imported optimized Phi-3.5-Vision model")
except ImportError as e:
    logger.error(f"❌ Failed to import optimized model: {e}")
    exit(1)

class OptimizedPhi3VisionServer:
    """
    High-performance Flask server for Phi-3.5-Vision with MLX
    """
    
    def __init__(self, config_path="phi3_vision_optimized_config.json"):
        self.app = Flask(__name__)
        self.model = None
        self.config = self.load_config(config_path)
        self.setup_routes()
        
        # Performance tracking
        self.stats = {
            "requests": 0,  # type: int
            "total_time": 0.0,  # type: float
            "avg_time": 0.0,  # type: float
            "cache_hits": 0,  # type: int
            "mlx_requests": 0,  # type: int
            "transformers_requests": 0  # type: int
        }
    
    def load_config(self, config_path):
        """Load optimized configuration"""
        try:
            # Default optimized config
            default_config = {
                "model_name": "Phi-3.5-Vision-Optimized",
                "model_path": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "device": "auto",
                "max_tokens": 100,
                "timeout": 60,
                "use_mlx": True,
                "image_processing": {
                    "max_size": 1024
                }
            }
            
            # Try to load from the project's config directory first
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            project_config_path = project_root / "src/config/model_configs/phi3_vision_optimized.json"
            
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
                logger.info("⚙️ Using default optimized config")
            
            return default_config
            
        except Exception as e:
            logger.error(f"Config loading error: {e}")
            return {}
    
    def initialize_model(self):
        """Initialize optimized model with error handling"""
        try:
            logger.info("🚀 Initializing OPTIMIZED Phi-3.5-Vision...")
            start_time = time.time()
            
            self.model = OptimizedPhi3VisionModel(
                model_name=self.config.get("model_name", "Phi-3.5-Vision-Optimized"),
                config=self.config
            )
            
            if self.model.load_model():
                init_time = time.time() - start_time
                logger.info(f"✅ OPTIMIZED Phi-3.5-Vision ready in {init_time:.2f}s")
                
                # Log MLX status
                model_info = self.model.get_model_info()
                if model_info.get("mlx_available"):
                    logger.info("🍎 MLX optimization ACTIVE")
                else:
                    logger.warning("⚠️ MLX not available, using transformers fallback")
                
                return True
            else:
                logger.error("❌ Failed to load optimized model")
                return False
                
        except Exception as e:
            logger.error(f"❌ Model initialization error: {e}")
            return False
    
    def setup_routes(self):
        """Setup Flask routes with optimization"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Fast health check"""
            if self.model and self.model.loaded:
                model_info = self.model.get_model_info()
                return jsonify({
                    "status": "healthy",
                    "model": "Phi-3.5-Vision-Optimized",
                    "version": "2.0.0",
                    "mlx_available": model_info.get("mlx_available", False),
                    "use_mlx": model_info.get("use_mlx", False),
                    "performance": {
                        "requests": self.stats["requests"],
                        "avg_time": f"{self.stats['avg_time']:.2f}s",
                        "cache_hits": self.stats["cache_hits"],
                        "mlx_requests": self.stats["mlx_requests"],
                        "transformers_requests": self.stats["transformers_requests"]
                    }
                })
            else:
                return jsonify({"status": "loading", "model": "Phi-3.5-Vision-Optimized"}), 503
        
        @self.app.route('/v1/chat/completions', methods=['POST'])
        def chat_completions():
            """Optimized OpenAI-compatible endpoint"""
            try:
                start_time = time.time()
                
                if not self.model or not self.model.loaded:
                    return jsonify({"error": "Model not ready"}), 503
                
                data = request.get_json()
                messages = data.get('messages', [])
                max_tokens = min(data.get('max_tokens', 100), 150)  # Cap for speed
                
                if not messages:
                    return jsonify({"error": "No messages provided"}), 400
                
                # Extract user message (latest)
                user_message = None
                for message in reversed(messages):
                    if message.get('role') == 'user':
                        user_message = message
                        break
                
                if not user_message:
                    return jsonify({"error": "No user message found"}), 400
                
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
                    return jsonify({"error": "No image provided"}), 400
                
                # Fast image processing
                try:
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                except Exception as e:
                    return jsonify({"error": f"Image processing failed: {e}"}), 400
                
                # Generate response with optimized model
                result = self.model.predict(
                    image=image,
                    prompt=text_content,
                    options={"max_tokens": max_tokens}
                )
                
                processing_time = time.time() - start_time
                
                # Update stats
                self.stats["requests"] = int(self.stats["requests"] + 1)
                self.stats["total_time"] = float(self.stats["total_time"] + processing_time)
                self.stats["avg_time"] = float(self.stats["total_time"] / self.stats["requests"])
                
                # Track method used
                method = result.get("method", "Unknown")
                if method == "MLX":
                    self.stats["mlx_requests"] += 1
                elif method == "Transformers":
                    self.stats["transformers_requests"] += 1
                
                if result.get("success"):
                    response_text = result.get("response", {}).get("text", "")
                    
                    # OpenAI-compatible response
                    return jsonify({
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
                        "model": "Phi-3.5-Vision-Optimized",
                        "performance": {
                            "processing_time": f"{processing_time:.2f}s",
                            "optimized": True,
                            "method": method,
                            "mlx_active": method == "MLX"
                        }
                    })
                else:
                    return jsonify({"error": result.get("error", "Unknown error")}), 500
                    
            except Exception as e:
                logger.error(f"Request processing error: {e}")
                return jsonify({"error": f"Processing failed: {str(e)}"}), 500
        
        @self.app.route('/v1/models', methods=['GET'])
        def list_models():
            """List available models"""
            return jsonify({
                "data": [{
                    "id": "phi-3.5-vision-optimized",
                    "object": "model",
                    "owned_by": "optimized",
                    "permission": []
                }]
            })
        
        @self.app.route('/stats', methods=['GET'])
        def stats():
            """Performance statistics"""
            model_info = self.model.get_model_info() if self.model else {}
            return jsonify({
                "model": "Phi-3.5-Vision-Optimized",
                "statistics": self.stats,
                "model_info": model_info,
                "optimizations": {
                    "mlx_optimization": model_info.get("mlx_available", False),
                    "int4_quantization": True,
                    "image_caching": True,
                    "apple_silicon": torch.backends.mps.is_available()
                }
            })
        
        @self.app.route('/predict', methods=['POST'])
        def predict():
            """Direct prediction endpoint"""
            try:
                if not self.model or not self.model.loaded:
                    return jsonify({"error": "Model not ready"}), 503
                
                data = request.get_json()
                prompt = data.get('prompt', 'Describe what you see in this image.')
                image_data = data.get('image')
                
                if not image_data:
                    return jsonify({"error": "No image provided"}), 400
                
                # Decode image
                try:
                    if image_data.startswith('data:image/'):
                        image_data = image_data.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                except Exception as e:
                    return jsonify({"error": f"Image decoding failed: {e}"}), 400
                
                # Predict
                result = self.model.predict(image, prompt)
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def run(self, host='0.0.0.0', port=8080):
        """Start optimized server"""
        logger.info("🔥 Starting OPTIMIZED Phi-3.5-Vision Server...")
        logger.info(f"🎯 Target: MLX acceleration for Apple Silicon")
        logger.info(f"⚙️ Optimizations: INT4 quantization, image caching, fast inference")
        
        if not self.initialize_model():
            logger.error("❌ Server startup failed")
            return False
        
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info("🚀 OPTIMIZED Phi-3.5-Vision Server ready!")
        
        try:
            # Optimize Flask settings for better performance
            import threading
            self.app.config['THREADED'] = True
            
            self.app.run(
                host=host,
                port=port,
                debug=False,  # Disable debug for performance
                threaded=True,  # Enable threading
                processes=1,    # Single process with threading
                use_reloader=False,  # Disable reloader for performance
                request_handler=None  # Use default
            )
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
            return False
        
        return True

def main():
    """Main execution with optimization info"""
    print("🔥 OPTIMIZED Phi-3.5-Vision Server")
    print("=" * 50)
    print("🎯 Performance Improvements:")
    print("   • MLX optimization for Apple Silicon")
    print("   • INT4 quantization (mlx-community/Phi-3.5-vision-instruct-4bit)")
    print("   • Image preprocessing cache")
    print("   • Fast inference pipeline")
    print("   • Fallback to transformers")
    print("=" * 50)
    
    # Check MLX availability
    try:
        import mlx.core as mx
        logger.info("✅ MLX framework available")
    except ImportError:
        logger.warning("⚠️ MLX not available, install with: pip install mlx-vlm")
    
    # Check PyTorch and MPS availability
    logger.info(f"PyTorch version: {torch.__version__}")
    if torch.backends.mps.is_available():
        logger.info("✅ MPS (Apple Silicon) acceleration available")
    else:
        logger.warning("⚠️ MPS not available")
    
    server = OptimizedPhi3VisionServer()
    
    try:
        success = server.run(host='0.0.0.0', port=8080)
        if success:
            logger.info("✅ Server shutdown completed")
        else:
            logger.error("❌ Server encountered errors")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main() 