#!/usr/bin/env python3
"""
Optimized Phi-3.5-Vision Server Runner

Optimized version of Phi-3.5-Vision server with:
- Single-threaded Flask to avoid Metal GPU conflicts
- MLX acceleration for Apple Silicon
- Memory management and cleanup
- Performance optimizations
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
import gc
from io import BytesIO
from flask import Flask, request, jsonify
from PIL import Image
import torch
from pathlib import Path

# Setup logging
def setup_logging():
    """Setup logging with proper path and permissions"""
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        log_dir = base_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(log_dir, 0o755)
        
        timestamp = time.strftime("%Y%m%d")
        log_file = log_dir / f"phi3_vision_optimized_{timestamp}.log"
        
        file_handler = logging.FileHandler(
            filename=log_file,
            mode='a',
            encoding='utf-8'
        )
        os.chmod(log_file, 0o644)
        
        console_handler = logging.StreamHandler()
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        root_logger.info(f"Phi-3.5-Vision optimized logging initialized. Log file: {log_file}")
        return root_logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

logger = setup_logging()

# Port cleanup functions (prevent Metal conflicts)
def check_port_availability(port=8080):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0
    except Exception as e:
        logger.warning(f"Port check error: {e}")
        return False

def find_process_on_port(port=8080):
    """Find process using the specified port"""
    try:
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
            if not force:
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                
                try:
                    os.kill(pid, 0)
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
    
    if check_port_availability(8080):
        logger.info("✅ Port 8080 is already available")
        return True
    
    logger.info("🔄 Port 8080 is in use, attempting cleanup...")
    
    if kill_process_on_port(8080, force=False):
        time.sleep(2)
        if check_port_availability(8080):
            logger.info(f"✅ Port 8080 is now available")
            return True
    
    logger.warning("⚠️ Graceful cleanup failed, trying force cleanup...")
    if kill_process_on_port(8080, force=True):
        time.sleep(2)
        if check_port_availability(8080):
            logger.info(f"✅ Port 8080 is now available")
            return True
    
    logger.error("❌ Failed to clean up port 8080")
    return False

class OptimizedPhi3VisionServer:
    """
    Optimized Flask server for Phi-3.5-Vision (single-threaded to avoid Metal conflicts)
    """
    
    def __init__(self, config_path="phi3_vision_optimized.json"):
        self.app = Flask(__name__)
        self.model = None
        self.processor = None
        self.config = self.load_config(config_path)
        self.use_mlx = False
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
            default_config = {
                "model_name": "Phi-3.5-Vision-Optimized",
                "model_path": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "device": "auto",
                "trust_remote_code": True,
                "max_tokens": 100,
                "timeout": 60
            }
            
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
            
            # Strategy 1: Try MLX-VLM first (same as vlm_tester.py)
            try:
                from mlx_vlm import load
                logger.info("🚀 Attempting MLX-VLM load...")
                
                self.model, self.processor = load(
                    self.config.get("model_path", "mlx-community/Phi-3.5-vision-instruct-4bit"),
                    trust_remote_code=True
                )
                self.use_mlx = True
                
                init_time = time.time() - start_time
                logger.info(f"✅ OPTIMIZED MLX Phi-3.5-Vision ready in {init_time:.2f}s")
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
                logger.info("📥 Loading optimized transformers Phi-3.5-Vision...")
                
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
                logger.info(f"✅ OPTIMIZED Transformers Phi-3.5-Vision ready in {init_time:.2f}s")
                return True
                
        except Exception as e:
            logger.error(f"❌ Model initialization error: {e}")
            return False
    
    def setup_routes(self):
        """Setup Flask routes with optimization"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Fast health check"""
            if self.model and self.processor:
                return jsonify({
                    "status": "healthy",
                    "model": "Phi-3.5-Vision-Optimized",
                    "version": "1.0.0",
                    "method": "MLX" if self.use_mlx else "Transformers",
                    "optimization": "Single-threaded, Memory-optimized",
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
                
                if not self.model or not self.processor:
                    return jsonify({"error": "Model not ready"}), 503
                
                data = request.get_json()
                messages = data.get('messages', [])
                max_tokens = min(data.get('max_tokens', 100), 150)  # Cap for speed
                
                if not messages:
                    return jsonify({"error": "No messages provided"}), 400
                
                # Extract user message (same as standard version)
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
                            image_data = image_url.split(',')[1]
                
                if not image_data:
                    return jsonify({"error": "No image provided"}), 400
                
                # Fast image processing
                try:
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                except Exception as e:
                    return jsonify({"error": f"Image processing failed: {e}"}), 400
                
                # Generate response with optimized model (same logic as vlm_tester.py)
                if self.use_mlx:
                    response_text = self._generate_mlx_response(image, text_content, max_tokens)
                else:
                    response_text = self._generate_transformers_response(image, text_content, max_tokens)
                
                processing_time = time.time() - start_time
                
                # Update stats
                self.stats["requests"] += 1
                self.stats["total_time"] += processing_time
                self.stats["avg_time"] = self.stats["total_time"] / self.stats["requests"]
                
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
                        "method": "MLX" if self.use_mlx else "Transformers"
                    }
                })
                    
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
                    "single_threaded": True,
                    "memory_management": True,
                    "mlx_acceleration": self.use_mlx,
                    "port_cleanup": True
                }
            })
    
    def _generate_mlx_response(self, image: Image.Image, prompt: str, max_tokens: int) -> str:
        """Generate response using MLX (same as vlm_tester.py)"""
        try:
            from mlx_vlm import generate
            logger.info("🚀 Using MLX-VLM inference for optimized Phi-3.5-Vision...")
            
            # Save image to temporary file for MLX
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                temp_image_path = tmp_file.name
                image.save(temp_image_path, 'JPEG', quality=95)
            
            try:
                # Use same prompt format as vlm_tester.py
                mlx_prompt = f"<|image_1|>\nUser: {prompt}\nAssistant:"
                logger.info(f"🔍 Final MLX prompt: {mlx_prompt[:100]}...")  # Debug the actual prompt
                
                response = generate(
                    model=self.model,
                    processor=self.processor,
                    image=temp_image_path,
                    prompt=mlx_prompt,
                    max_tokens=max_tokens,
                    temp=0.0,
                    verbose=False
                )
                
                # Process response (same as vlm_tester.py)
                text_response = str(response)
                text_response = text_response.replace("<|end|>", "").replace("<|endoftext|>", "").strip()
                if "1. What is meant by" in text_response:
                    text_response = text_response.split("1. What is meant by")[0].strip()
                text_response = ' '.join(text_response.split())
                
                return text_response
                
            finally:
                # Clean up temporary file
                try:
                    os.remove(temp_image_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"MLX inference error: {e}")
            return f"MLX inference failed: {str(e)}"
    
    def _generate_transformers_response(self, image: Image.Image, prompt: str, max_tokens: int) -> str:
        """Generate response using transformers (same as vlm_tester.py)"""
        try:
            # Same format as vlm_tester.py
            messages = [{"role": "user", "content": f"<|image_1|>\n{prompt}"}]
            
            prompt_text = self.processor.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            inputs = self.processor(prompt_text, [image], return_tensors="pt")
            
            # Move to correct device
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs, 
                    max_new_tokens=max_tokens,
                    do_sample=False,
                    use_cache=False,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            result = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            # Clean response
            if "Assistant:" in result:
                result = result.split("Assistant:")[-1].strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Transformers inference error: {e}")
            return f"Transformers inference failed: {str(e)}"
    
    def run(self, host='0.0.0.0', port=8080):
        """Start optimized server with port cleanup"""
        logger.info("🔥 Starting OPTIMIZED Phi-3.5-Vision Server...")
        logger.info(f"🎯 Target: Apple Silicon optimization + Metal conflict prevention")
        logger.info(f"⚙️ Optimizations: Single-threaded, Memory management, Port cleanup")
        
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
            # **CRITICAL FIX**: Disable threading to prevent Metal GPU conflicts
            self.app.config['THREADED'] = False
            
            self.app.run(
                host=host,
                port=port,
                debug=False,
                threaded=False,  # FIXED: Single-threaded to prevent Metal conflicts
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
    print("🔥 OPTIMIZED Phi-3.5-Vision Server with Metal Conflict Prevention")
    print("=" * 60)
    print("🎯 Performance Improvements:")
    print("   • Single-threaded Flask to prevent Metal GPU conflicts")
    print("   • MLX acceleration for Apple Silicon")
    print("   • Memory optimization and cleanup")
    print("   • Port management and cleanup")
    print("🧹 Port Management:")
    print("   • Automatic port 8080 cleanup")
    print("   • Process detection and termination")
    print("   • Graceful and force kill options")
    print("=" * 60)
    
    # Check MLX availability
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
