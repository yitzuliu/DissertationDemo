#!/usr/bin/env python3
"""
LLaVA MLX Server Runner

High-performance LLaVA server with:
- MLX framework optimization for Apple Silicon
- Flask server for OpenAI-compatible API
- INT4 quantization for memory efficiency
- Robust error handling and fallbacks
- Port 8080 cleanup functionality
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
from flask import Flask, request, jsonify
from PIL import Image
import torch
from pathlib import Path

# Print startup banner
def print_startup_banner(
    model_name: str,
    server_type: str,
    features: list,
    optimizations: list = None,
    port: int = None):

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
    if port:
        print(f"🌐 Server will start on port {port}")
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
        
        # Ensure proper directory permissions
        os.chmod(log_dir, 0o755)
        
        # Setup log file path with timestamp
        timestamp = time.strftime("%Y%m%d")
        log_file = log_dir / f"llava_mlx_{timestamp}.log"
        
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
        root_logger.info(f"LLaVA MLX logging initialized. Log file: {log_file}")
        
        return root_logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

# Initialize logging
logger = setup_logging()

# Port 8080 cleanup functions
def check_port_availability(port=8080):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0  # True if port is available
    except Exception as e:
        logger.warning(f"Port check error: {e}")
        return False

def find_process_on_port(port=8080):
    """Find process using the specified port"""
    try:
        # Use lsof to find process on port
        result = subprocess.run(
            ['lsof', '-i', f':{port}', '-t'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            return [int(pid) for pid in pids if pid.isdigit()]
        return []
        
    except subprocess.TimeoutExpired:
        logger.warning("lsof command timed out")
        return []
    except FileNotFoundError:
        logger.warning("lsof command not found")
        return []
    except Exception as e:
        logger.error(f"Error finding process on port {port}: {e}")
        return []

def kill_process_on_port(port=8080, force=False):
    """Kill process(es) using the specified port"""
    pids = find_process_on_port(port)
    
    if not pids:
        logger.info(f"✅ No processes found on port {port}")
        return True
    
    logger.info(f"🔍 Found {len(pids)} process(es) on port {port}: {pids}")
    
    for pid in pids:
        try:
            # Try graceful termination first
            if not force:
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                
                # Check if process is still running
                try:
                    os.kill(pid, 0)  # Check if process exists
                    logger.warning(f"⚠️ Process {pid} still running, using SIGKILL...")
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    logger.info(f"✅ Process {pid} terminated gracefully")
            else:
                os.kill(pid, signal.SIGKILL)
                
            time.sleep(1)
            
        except ProcessLookupError:
            logger.info(f"✅ Process {pid} already terminated")
        except PermissionError:
            logger.error(f"❌ Permission denied to kill process {pid}")
            return False
        except Exception as e:
            logger.error(f"❌ Error killing process {pid}: {e}")
            return False
    
    return True

def cleanup_port_8080():
    """Comprehensive port 8080 cleanup"""
    logger.info("🧹 Cleaning up port 8080...")
    
    # Check if port is available
    if check_port_availability(8080):
        logger.info("✅ Port 8080 is already available")
        return True
    
    logger.info("🔄 Port 8080 is in use, attempting cleanup...")
    
    # Try graceful cleanup first
    if kill_process_on_port(8080, force=False):
        time.sleep(2)
        if check_port_availability(8080):
            logger.info(f"✅ Port 8080 is now available")
            return True
    
    # If graceful cleanup failed, try force cleanup
    logger.warning("⚠️ Graceful cleanup failed, trying force cleanup...")
    if kill_process_on_port(8080, force=True):
        time.sleep(2)
        if check_port_availability(8080):
            logger.info(f"✅ Port 8080 is now available")
            return True
    
    logger.error("❌ Failed to clean up port 8080")
    return False

# Import model with fallbacks
def import_model_with_fallbacks():
    """Import LLaVA MLX model with multiple fallback strategies"""
    
    # Add current directory and parent directories to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(parent_dir)))
    
    for path in [current_dir, parent_dir, project_root]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Strategy 1: Try importing LLaVA MLX model
    try:
        from llava_mlx_model import LlavaMlxModel
        logger.info("✅ Imported LlavaMlxModel (Strategy 1)")
        return LlavaMlxModel
    except ImportError as e:
        logger.warning(f"Strategy 1 failed: {e}")
    
    # Strategy 2: Try creating MLX-VLM wrapper
    try:
        from mlx_vlm import load, generate
        logger.info("✅ Using MLX-VLM directly (Strategy 2)")
        
        class MLXVLMWrapper:
            def __init__(self, model_name, config):
                self.model_name = model_name
                self.config = config
                self.loaded = False
                self.model = None
                self.processor = None
                
            def load_model(self):
                try:
                    model_path = self.config.get("model_path", "mlx-community/llava-v1.6-mistral-7b-4bit")
                    logger.info(f"Loading MLX-VLM model: {model_path}")
                    
                    self.model, self.processor = load(model_path)
                    self.loaded = True
                    logger.info("✅ MLX-VLM LLaVA model loaded successfully")
                    return True
                except Exception as e:
                    logger.error(f"Failed to load MLX-VLM model: {e}")
                    return False
                    
            def predict(self, image, prompt, options=None):
                if not self.loaded:
                    return {"error": "Model not loaded", "success": False}
                    
                try:
                    # Save image to temp file for MLX-VLM
                    import tempfile
                    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                    temp_path = temp_file.name
                    temp_file.close()
                    
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image.save(temp_path, 'JPEG', quality=95)
                    
                    try:
                        # Get generation parameters
                        max_tokens = options.get("max_tokens", 150) if options else 150
                        temperature = self.config.get("inference_params", {}).get("temperature", 0.7)
                        
                        # Generate response with MLX-VLM
                        response = generate(
                            model=self.model,
                            processor=self.processor,
                            image=temp_path,
                            prompt=prompt,
                            max_tokens=max_tokens,
                            temp=temperature,
                            verbose=False
                        )
                        
                        # Handle MLX-VLM response format
                        if isinstance(response, tuple) and len(response) >= 1:
                            text_response = response[0] if response[0] else ""
                        else:
                            text_response = str(response) if response else ""
                        
                        return {
                            "success": True,
                            "response": {"text": text_response.strip()}
                        }
                        
                    finally:
                        # Cleanup temp file
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                        
                except Exception as e:
                    logger.error(f"Prediction error: {e}")
                    return {"error": str(e), "success": False}
        
        return MLXVLMWrapper
        
    except ImportError as e:
        logger.error(f"Strategy 2 failed: {e}")
    
    # Strategy 3: Create minimal fallback
    logger.error("❌ All import strategies failed, creating minimal fallback")
    
    class MinimalLLaVAModel:
        def __init__(self, model_name, config):
            self.model_name = model_name
            self.config = config
            self.loaded = False
            
        def load_model(self):
            logger.error("❌ Minimal fallback model - no actual functionality")
            logger.error("❌ Please install mlx-vlm: pip install mlx-vlm")
            return False
            
        def predict(self, image, prompt, options=None):
            return {
                "error": "MLX-VLM not available. Please install: pip install mlx-vlm",
                "success": False,
                "response": {"text": "Model not available"}
            }
    
    return MinimalLLaVAModel

# Import model with fallbacks
try:
    LLaVAModel = import_model_with_fallbacks()
    logger.info(f"✅ Model import successful: {LLaVAModel.__name__}")
except Exception as e:
    logger.error(f"❌ Critical import failure: {e}")
    exit(1)

class LLaVAMLXServer:
    """
    High-performance Flask server for LLaVA MLX
    """
    
    def __init__(self, config_path="llava_mlx.json"):
        self.app = Flask(__name__)
        self.model = None
        self.config = self.load_config(config_path)
        self.setup_routes()
        
        # Performance tracking
        self.stats = {
            "requests": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "cache_hits": 0
        }
    
    def load_config(self, config_path):
        """Load LLaVA MLX configuration with better debugging"""
        try:
            # Default configuration
            default_config = {
                "model_name": "LLaVA-MLX",
                "model_path": "mlx-community/llava-v1.6-mistral-7b-4bit",
                "device": "auto",
                "timeout": 180,
                "inference_params": {
                    "max_tokens": 150,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "repetition_penalty": 1.2
                }
            }
            
            # Try to load from the project's config directory first
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            project_config_path = project_root / "src/config/model_configs/llava_mlx.json"
            
            logger.info(f"🔍 Looking for config at: {project_config_path}")
            logger.info(f"🔍 Config file exists: {project_config_path.exists()}")
            
            if project_config_path.exists():
                with open(project_config_path, 'r') as f:
                    file_config = json.load(f)
                
                logger.info(f"📁 Loaded config keys: {list(file_config.keys())}")
                logger.info(f"📁 Model path in config: {file_config.get('model_path', 'NOT FOUND')}")
                
                # combine config with default config
                default_config.update(file_config)
                logger.info(f"📁 Final model_path after merge: {default_config.get('model_path')}")
                
            elif os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
                logger.info(f"📁 Loaded config from {config_path}")
            else:
                logger.info("⚙️ Using default LLaVA MLX config")
            
            # Validate and fix model_path
            if "model_path" not in default_config or not default_config["model_path"]:
                default_config["model_path"] = "mlx-community/llava-v1.6-mistral-7b-4bit"
                logger.info("🔧 Set default model_path: mlx-community/llava-v1.6-mistral-7b-4bit")
            
            # avoid using model_id as path
            if default_config.get("model_path") == "llava_mlx":
                default_config["model_path"] = "mlx-community/llava-v1.6-mistral-7b-4bit"
                logger.warning("🔧 Fixed incorrect model_path, was set to model_id")
            
            logger.info(f"🔧 Final config model_path: {default_config['model_path']}")
            logger.info(f"🔧 Complete config: {json.dumps(default_config, indent=2)}")
            
            return default_config
            
        except Exception as e:
            logger.error(f"Config loading error: {e}")
            return {
                "model_name": "LLaVA-MLX",
                "model_path": "mlx-community/llava-v1.6-mistral-7b-4bit",
                "device": "auto",
                "timeout": 180,
                "inference_params": {
                    "max_tokens": 150,
                    "temperature": 0.7
                }
            }
    
    def initialize_model(self):
        """Initialize LLaVA MLX model with error handling"""
        try:
            logger.info("🚀 Initializing LLaVA MLX...")
            start_time = time.time()
            
            # ensure passing correct config
            model_config = self.config.copy()
            logger.info(f"🔧 Initializing with model_path: {model_config.get('model_path')}")
            
            self.model = LLaVAModel(
                model_name=model_config.get("model_name", "LLaVA-MLX"),
                config=model_config
            )
            
            if self.model.load_model():
                init_time = time.time() - start_time
                logger.info(f"✅ LLaVA MLX ready in {init_time:.2f}s")
                return True
            else:
                logger.error("❌ Failed to load LLaVA MLX model")
                return False
                
        except Exception as e:
            logger.error(f"❌ Model initialization error: {e}")
            return False
    
    def setup_routes(self):
        """Setup Flask routes for LLaVA MLX"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            if self.model and self.model.loaded:
                return jsonify({
                    "status": "healthy",
                    "model": "LLaVA-MLX",
                    "version": "1.0.0",
                    "framework": "MLX-VLM",
                    "performance": {
                        "requests": self.stats["requests"],
                        "avg_time": f"{self.stats['avg_time']:.2f}s",
                        "cache_hits": self.stats["cache_hits"]
                    }
                })
            else:
                return jsonify({"status": "loading", "model": "LLaVA-MLX"}), 503
        
        @self.app.route('/v1/chat/completions', methods=['POST'])
        def chat_completions():
            """OpenAI-compatible chat completions endpoint"""
            try:
                start_time = time.time()
                
                if not self.model or not self.model.loaded:
                    return jsonify({"error": "Model not ready"}), 503
                
                data = request.get_json()
                messages = data.get('messages', [])
                max_tokens = min(data.get('max_tokens', 150), 300)  # Cap for performance
                
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
                    return jsonify({
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": "Error: No image provided"
                            },
                            "finish_reason": "error"
                        }],
                        "error": "No image provided"
                    }), 400
                
                # reference test framework image processing
                try:
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    
                    # ensure image is RGB format (reference test framework)
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                        logger.info("🔧 Converted image to RGB format")
                    
                    # reference test framework unified image preprocessing (1024px)
                    unified_image_size = 1024
                    original_size = image.size
                    if max(image.size) > unified_image_size:
                        ratio = unified_image_size / max(image.size)
                        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                        image = image.resize(new_size, Image.Resampling.LANCZOS)
                        logger.info(f"🔧 Resized image: {original_size} → {new_size} (test framework method)")
                    
                    # check image size is reasonable
                    if image.size[0] < 32 or image.size[1] < 32:
                        logger.warning(f"⚠️ Image too small: {image.size}, using minimum size")
                        image = image.resize((224, 224), Image.Resampling.LANCZOS)
                    
                    # check image size is too large
                    if image.size[0] > 2048 or image.size[1] > 2048:
                        logger.warning(f"⚠️ Image too large: {image.size}, reducing size")
                        max_dim = max(image.size)
                        ratio = 1024 / max_dim
                        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                        image = image.resize(new_size, Image.Resampling.LANCZOS)
                    
                    logger.info(f"🔧 Final image size: {image.size}")
                    
                except Exception as e:
                    logger.error(f"❌ Image processing failed: {e}")
                    return jsonify({
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": f"Image processing failed: {str(e)}"
                            },
                            "finish_reason": "error"
                        }],
                        "error": f"Image processing failed: {str(e)}"
                    }), 400
                
                # Generate response with LLaVA MLX
                try:
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
                    
                    # ensure result format is correct (reference previous fix)
                    if result.get("success"):
                        response_text = result.get("response", {}).get("text", "No response")
                        
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
                            "model": "LLaVA-MLX",
                            "performance": {
                                "processing_time": f"{processing_time:.2f}s",
                                "framework": "MLX-VLM",
                                "image_size": f"{image.size[0]}x{image.size[1]}"
                            }
                        })
                    else:
                        # error should return correct format
                        error_msg = result.get("error", "Unknown error")
                        return jsonify({
                            "choices": [{
                                "message": {
                                    "role": "assistant",
                                    "content": f"Error: {error_msg}"
                                },
                                "finish_reason": "error"
                            }],
                            "error": error_msg
                        }), 500
                        
                except Exception as e:
                    logger.error(f"Model prediction error: {e}")
                    # even if error occurs, return correct format
                    return jsonify({
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": f"Model error: {str(e)}"
                            },
                            "finish_reason": "error"
                        }],
                        "error": str(e)
                    }), 500
                    
            except Exception as e:
                logger.error(f"Request processing error: {e}")
                # final error handling should return correct format
                return jsonify({
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": f"Server error: {str(e)}"
                        },
                        "finish_reason": "error"
                    }],
                    "error": str(e)
                }), 500

        @self.app.route('/stats', methods=['GET'])
        def stats():
            """Performance statistics"""
            return jsonify({
                "model": "LLaVA-MLX",
                "statistics": self.stats,
                "framework": "MLX-VLM",
                "optimizations": {
                    "mlx_acceleration": True,
                    "apple_silicon": True,
                    "int4_quantization": True,
                    "unified_preprocessing": True
                }
            })
    
    def run(self, host='0.0.0.0', port=8080):
        """Start LLaVA MLX server with port cleanup"""
        logger.info("🚀 Starting LLaVA MLX Server...")
        logger.info(f"🎯 Target: MLX acceleration for Apple Silicon")
        logger.info(f"🔧 Model: mlx-community/llava-v1.6-mistral-7b-4bit")
        
        # Clean up port before starting
        logger.info(f"🧹 Checking port {port} availability...")
        if not cleanup_port_8080():
            logger.error(f"❌ Cannot start server - port {port} cleanup failed")
            return False
        
        if not self.initialize_model():
            logger.error("❌ Server startup failed")
            return False
        
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info("🚀 LLaVA MLX Server ready!")
        
        try:
            # Optimize Flask settings
            self.app.config['THREADED'] = True
            
            self.app.run(
                host=host,
                port=port,
                debug=False,
                threaded=True,
                processes=1,
                use_reloader=False
            )
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
            return False
        
        return True

def main():
    print_startup_banner(
        model_name="LLaVA-MLX",
        server_type="Standard Server",
        features=[
            "OpenAI-compatible API",
            "MLX acceleration for Apple Silicon",
            "Transformers fallback",
            "Robust error handling"
        ],
        optimizations=[
            "Single-threaded Flask",
            "Memory management",
            "Port cleanup"
        ],
        port=8080
    )
    
    # Check MLX availability
    try:
        import mlx.core as mx
        logger.info("✅ MLX framework available")
    except ImportError:
        logger.error("❌ MLX not available - Apple Silicon required")
        print("❌ MLX framework not found!")
        print("💡 Install with: pip install mlx-vlm")
        return
    
    # Clean port first
    logger.info("🧹 Pre-startup port cleanup...")
    cleanup_port_8080()
    
    server = LLaVAMLXServer()
    
    try:
        success = server.run(host='0.0.0.0', port=8080)
        if success:
            logger.info("✅ Server shutdown completed")
        else:
            logger.error("❌ Server encountered errors")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        logger.info("🧹 Cleaning up port on exit...")
        cleanup_port_8080()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
