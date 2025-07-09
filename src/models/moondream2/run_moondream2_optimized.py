#!/usr/bin/env python3
"""
Optimized Moondream2 Server Runner

High-performance version of Moondream2 server with:
- MPS acceleration for Apple Silicon
- Optimized memory management
- Image caching
- Special API handling for Moondream2's unique interface
- OpenAI-compatible endpoints
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
        log_file = log_dir / f"moondream2_{timestamp}.log"
        
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
        root_logger.info(f"Moondream2 logging initialized. Log file: {log_file}")
        
        return root_logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

# Initialize logging
logger = setup_logging()

# Import optimized model
try:
    import sys
    import os
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from moondream2_optimized import OptimizedMoondream2Model
    logger.info("✅ Imported optimized Moondream2 model")
except ImportError as e:
    logger.error(f"❌ Failed to import optimized model: {e}")
    exit(1)

class OptimizedMoondream2Server:
    """
    High-performance Flask server for Moondream2
    """
    
    def __init__(self, config_path="moondream2_optimized_config.json"):
        self.app = Flask(__name__)
        self.model = None
        self.config = self.load_config(config_path)
        self.setup_routes()
        
        # Performance tracking
        self.stats = {
            "requests": 0,  # type: int
            "total_time": 0.0,  # type: float
            "avg_time": 0.0,  # type: float
            "cache_hits": 0  # type: int
        }
    
    def load_config(self, config_path):
        """Load optimized configuration"""
        try:
            # Default optimized config
            default_config = {
                "model_name": "Moondream2-Optimized",
                "huggingface_model_id": "vikhyatk/moondream2",
                "device": "auto",
                "max_tokens": 100,
                "timeout": 30,
                "trust_remote_code": True
            }
            
            # Try to load from the project's config directory first
            # Get project root (4 levels up from current file)
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            project_config_path = project_root / "src/config/model_configs/moondream2_optimized.json"
            
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
            logger.info("🚀 Initializing OPTIMIZED Moondream2...")
            start_time = time.time()
            
            self.model = OptimizedMoondream2Model(
                model_name=self.config.get("model_name", "Moondream2-Optimized"),
                config=self.config
            )
            
            if self.model.load_model():
                init_time = time.time() - start_time
                logger.info(f"✅ OPTIMIZED Moondream2 ready in {init_time:.2f}s")
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
                return jsonify({
                    "status": "healthy",
                    "model": "Moondream2-Optimized",
                    "version": "1.0.0",
                    "device": getattr(self.model, 'device', 'unknown'),
                    "performance": {
                        "requests": self.stats["requests"],
                        "avg_time": f"{self.stats['avg_time']:.2f}s",
                        "cache_hits": self.stats["cache_hits"]
                    }
                })
            else:
                return jsonify({"status": "loading", "model": "Moondream2-Optimized"}), 503
        
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
                
                # Track cache hits
                if result.get("cache_hit"):
                    self.stats["cache_hits"] = int(self.stats["cache_hits"] + 1)
                
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
                        "model": "Moondream2-Optimized",
                        "performance": {
                            "processing_time": f"{processing_time:.2f}s",
                            "cache_hit": result.get("cache_hit", False),
                            "optimized": True
                        }
                    })
                else:
                    return jsonify({"error": result.get("error", "Unknown error")}), 500
                    
            except Exception as e:
                logger.error(f"Request processing error: {e}")
                return jsonify({"error": f"Processing failed: {str(e)}"}), 500
        
        @self.app.route('/v1/models', methods=['GET'])
        def list_models():
            """List available models (OpenAI-compatible)"""
            return jsonify({
                "data": [{
                    "id": "moondream2-optimized",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "moondream2",
                    "permission": [],
                    "root": "moondream2-optimized",
                    "parent": None
                }],
                "object": "list"
            })
        
        @self.app.route('/stats', methods=['GET'])
        def stats():
            """Performance statistics"""
            model_info = self.model.get_model_info() if self.model else {}
            return jsonify({
                "model": "Moondream2-Optimized",
                "statistics": self.stats,
                "model_info": model_info,
                "optimizations": {
                    "mps_acceleration": torch.backends.mps.is_available(),
                    "image_caching": True,
                    "response_caching": True,
                    "memory_management": True,
                    "special_api": "Moondream2 encode_image + answer_question"
                }
            })
        
        @self.app.route('/predict', methods=['POST'])
        def predict():
            """Direct prediction endpoint"""
            try:
                if not self.model or not self.model.loaded:
                    return jsonify({"error": "Model not ready"}), 503
                
                # Handle file upload or base64 data
                if 'image' in request.files:
                    image_file = request.files['image']
                    image = Image.open(image_file.stream)
                elif request.json and 'image_data' in request.json:
                    image_data = request.json['image_data']
                    if image_data.startswith('data:image/'):
                        image_data = image_data.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                else:
                    return jsonify({"error": "No image provided"}), 400
                
                prompt = request.json.get('prompt', 'Describe this image') if request.json else request.form.get('prompt', 'Describe this image')
                max_tokens = int(request.json.get('max_tokens', 100) if request.json else request.form.get('max_tokens', 100))
                
                result = self.model.predict(
                    image=image,
                    prompt=prompt,
                    options={"max_tokens": max_tokens}
                )
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def run(self, host='0.0.0.0', port=8080):
        """Start optimized server"""
        logger.info("🔥 Starting OPTIMIZED Moondream2 Server...")
        logger.info(f"🎯 Features: MPS acceleration, image caching, response caching")
        logger.info(f"⚙️ Special: Moondream2 unique API (encode_image + answer_question)")
        
        if not self.initialize_model():
            logger.error("❌ Server startup failed")
            return False
        
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info("🚀 OPTIMIZED Moondream2 Server ready!")
        
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
    print("🔥 OPTIMIZED Moondream2 Server")
    print("=" * 50)
    print("🎯 Performance Improvements:")
    print("   • MPS acceleration (Apple Silicon)")
    print("   • Optimized memory management")
    print("   • Image preprocessing cache")
    print("   • Response caching")
    print("   • Special API optimization")
    print("   • OpenAI-compatible endpoints")
    print("=" * 50)
    
    # Check PyTorch and MPS availability
    logger.info(f"PyTorch version: {torch.__version__}")
    if torch.backends.mps.is_available():
        logger.info("✅ MPS (Apple Silicon) acceleration available")
    elif torch.cuda.is_available():
        logger.info("✅ CUDA acceleration available")
    else:
        logger.info("⚠️ Using CPU (GPU acceleration not available)")
    
    server = OptimizedMoondream2Server()
    
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