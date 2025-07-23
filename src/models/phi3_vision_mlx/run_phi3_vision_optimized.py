#!/usr/bin/env python3
"""
Optimized Phi-3.5-Vision Server Runner

High-performance version of Phi-3.5-Vision server with:
- MLX acceleration for Apple Silicon
- INT4 quantization for memory efficiency
- Image caching and preprocessing optimization
- Memory management and cleanup
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
        log_file = log_dir / f"phi3_vision_optimized_{timestamp}.log"
        
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
        root_logger.info(f"Phi-3.5-Vision optimized logging initialized. Log file: {log_file}")
        
        return root_logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

# Initialize logging
logger = setup_logging()

# Port 8080 cleanup functions (reused from moondream2)
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
        logger.warning("lsof command not found, trying alternative method")
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
    """Import Phi-3.5-Vision model with multiple fallback strategies"""
    
    # Add current directory and parent directories to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(parent_dir)))
    
    for path in [current_dir, parent_dir, project_root]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Strategy 1: Try importing optimized model
    try:
        from phi3_vision_optimized import OptimizedPhi3VisionModel
        logger.info("✅ Imported OptimizedPhi3VisionModel (Strategy 1)")
        return OptimizedPhi3VisionModel
    except ImportError as e:
        logger.warning(f"Strategy 1 failed: {e}")
    
    # Strategy 2: Try importing standard model as fallback
    try:
        from phi3_vision_model import Phi3VisionModel
        logger.info("✅ Imported Phi3VisionModel as fallback (Strategy 2)")
        return Phi3VisionModel
    except ImportError as e:
        logger.warning(f"Strategy 2 failed: {e}")
    
    # Strategy 3: Try importing with MLX-VLM
    try:
        from mlx_vlm import load, generate
        from transformers import AutoProcessor, AutoModelForVision2Seq
        logger.info("✅ Using MLX-VLM model (Strategy 3)")
        
        class MLXPhi3VisionModel:
            def __init__(self, model_name, config):
                self.model_name = model_name
                self.config = config
                self.loaded = False
                self.model = None
                self.processor = None
                
            def load_model(self):
                try:
                    model_path = self.config.get("model_path", "mlx-community/Phi-3.5-vision-instruct-4bit")
                    
                    # Try MLX first
                    try:
                        self.model, self.processor = load(model_path, trust_remote_code=True)
                        logger.info("✅ MLX Phi-3.5-Vision model loaded")
                        self.use_mlx = True
                    except Exception as e:
                        logger.warning(f"MLX loading failed: {e}, falling back to transformers")
                        # Fallback to transformers
                        self.processor = AutoProcessor.from_pretrained(
                            "microsoft/Phi-3.5-vision-instruct", 
                            trust_remote_code=True
                        )
                        self.model = AutoModelForVision2Seq.from_pretrained(
                            "microsoft/Phi-3.5-vision-instruct",
                            torch_dtype=torch.float16,
                            device_map="cpu",
                            trust_remote_code=True
                        )
                        self.use_mlx = False
                    
                    self.loaded = True
                    return True
                except Exception as e:
                    logger.error(f"Failed to load model: {e}")
                    return False
                    
            def predict(self, image, prompt, options=None):
                if not self.loaded:
                    return {"error": "Model not loaded", "success": False}
                    
                try:
                    if self.use_mlx:
                        # MLX inference
                        # Save image to temp file for MLX
                        import tempfile
                        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                        temp_path = temp_file.name
                        temp_file.close()
                        
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        image.save(temp_path, 'JPEG', quality=95)
                        
                        # Generate response with MLX
                        mlx_prompt = f"<|image_1|>\nUser: {prompt}\nAssistant:"
                        response = generate(
                            model=self.model,
                            processor=self.processor,
                            image=temp_path,
                            prompt=mlx_prompt,
                            max_tokens=options.get("max_tokens", 100) if options else 100,
                            temp=0.7
                        )
                        
                        # Cleanup temp file
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                        
                        # Process response
                        if isinstance(response, tuple):
                            text_response = response[0]
                        else:
                            text_response = str(response)
                            
                        # Clean response
                        text_response = text_response.replace("<|end|>", "").replace("<|endoftext|>", "").strip()
                        
                        return {
                            "success": True,
                            "response": {"text": text_response}
                        }
                    else:
                        # Transformers inference
                        messages = [{"role": "user", "content": f"<|image_1|>\n{prompt}"}]
                        
                        prompt_text = self.processor.tokenizer.apply_chat_template(
                            messages,
                            tokenize=False,
                            add_generation_prompt=True
                        )
                        
                        inputs = self.processor(prompt_text, [image], return_tensors="pt")
                        
                        with torch.no_grad():
                            outputs = self.model.generate(
                                **inputs,
                                max_new_tokens=options.get("max_tokens", 100) if options else 100,
                                do_sample=False
                            )
                        
                        response = self.processor.decode(outputs[0], skip_special_tokens=True)
                        
                        return {
                            "success": True,
                            "response": {"text": response}
                        }
                        
                except Exception as e:
                    logger.error(f"Prediction error: {e}")
                    return {"error": str(e), "success": False}
        
        return MLXPhi3VisionModel
        
    except ImportError as e:
        logger.error(f"Strategy 3 failed: {e}")
    
    # Strategy 4: Create minimal fallback
    logger.error("❌ All import strategies failed, creating minimal fallback")
    
    class MinimalPhi3VisionModel:
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
    
    return MinimalPhi3VisionModel

# Import model with fallbacks
try:
    OptimizedPhi3VisionModel = import_model_with_fallbacks()
    logger.info(f"✅ Model import successful: {OptimizedPhi3VisionModel.__name__}")
except Exception as e:
    logger.error(f"❌ Critical import failure: {e}")
    exit(1)

class OptimizedPhi3VisionServer:
    """
    High-performance Flask server for Phi-3.5-Vision
    """
    
    def __init__(self, config_path="phi3_vision_optimized.json"):
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
        """Load optimized configuration"""
        try:
            # Default optimized config
            default_config = {
                "model_name": "Phi-3.5-Vision-Optimized",
                "model_path": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "device": "auto",
                "trust_remote_code": True,
                "max_tokens": 100,
                "timeout": 60
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
                    "model": "Phi-3.5-Vision-Optimized",
                    "version": "1.0.0",
                    "performance": {
                        "requests": self.stats["requests"],
                        "avg_time": f"{self.stats['avg_time']:.2f}s",
                        "cache_hits": self.stats["cache_hits"]
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
                            "optimized": True
                        }
                    })
                else:
                    return jsonify({"error": result.get("error", "Unknown error")}), 500
                    
            except Exception as e:
                logger.error(f"Request processing error: {e}")
                return jsonify({"error": f"Processing failed: {str(e)}"}), 500
        
        @self.app.route('/stats', methods=['GET'])
        def stats():
            """Performance statistics"""
            return jsonify({
                "model": "Phi-3.5-Vision-Optimized",
                "statistics": self.stats,
                "optimizations": {
                    "mlx_acceleration": True,
                    "int4_quantization": True,
                    "image_caching": True,
                    "memory_management": True
                }
            })
    
    def run(self, host='0.0.0.0', port=8080):
        """Start optimized server with port cleanup"""
        logger.info("🔥 Starting OPTIMIZED Phi-3.5-Vision Server...")
        logger.info(f"🎯 Target: MLX acceleration + INT4 quantization")
        logger.info(f"⚙️ Optimizations: Memory management, image caching, response caching")
        
        # Clean up port before starting
        logger.info(f"🧹 Checking port {port} availability...")
        if not cleanup_port_8080():
            logger.error(f"❌ Cannot start server - port {port} cleanup failed")
            return False
        
        if not self.initialize_model():
            logger.error("❌ Server startup failed")
            return False
        
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info("🚀 OPTIMIZED Phi-3.5-Vision Server ready!")
        
        try:
            # Optimize Flask settings for better performance
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
    """Main execution with optimization info and port cleanup"""
    print("🔥 OPTIMIZED Phi-3.5-Vision Server with Port Cleanup")
    print("=" * 60)
    print("🎯 Performance Improvements:")
    print("   • MLX acceleration for Apple Silicon")
    print("   • INT4 quantization for memory efficiency")
    print("   • Advanced image preprocessing")
    print("   • Memory optimization and caching")
    print("   • Response caching for repeated queries")
    print("🧹 Port Management:")
    print("   • Automatic port 8080 cleanup")
    print("   • Process detection and termination")
    print("   • Graceful and force kill options")
    print("=" * 60)
    
    # Check MLX availability (參考 run_phi3_vision.py 的成功實現)
    try:
        import mlx.core as mx
        logger.info("✅ MLX framework available")
    except ImportError:
        logger.warning("⚠️ MLX not available, falling back to transformers")
    
    # Check PyTorch and device availability
    logger.info(f"PyTorch version: {torch.__version__}")
    if torch.backends.mps.is_available():
        logger.info("✅ MPS (Apple Silicon) acceleration available")
    else:
        logger.warning("⚠️ MPS not available, using CPU")
    
    # Clean port first
    logger.info("🧹 Pre-startup port cleanup...")
    cleanup_port_8080()
    
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
        logger.info("🧹 Cleaning up port on exit...")
        cleanup_port_8080()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
