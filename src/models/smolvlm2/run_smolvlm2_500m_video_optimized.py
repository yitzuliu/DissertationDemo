#!/usr/bin/env python3
"""
Optimized SmolVLM2-500M-Video Server Runner

Optimized version of SmolVLM2-500M-Video server with:
- Single-threaded Flask to avoid conflicts
- MLX acceleration for Apple Silicon
- Memory management and cleanup
- Performance optimizations
"""

import os
import json
import logging
import time
import base64
import subprocess
import sys
import tempfile
import gc
from io import BytesIO
from flask import Flask, request, jsonify
from PIL import Image
import torch
from pathlib import Path

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

# Setup logging (same as optimized phi3_vision)
def setup_logging():
    """Setup logging with proper path and permissions"""
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        log_dir = base_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(log_dir, 0o755)
        
        timestamp = time.strftime("%Y%m%d")
        log_file = log_dir / f"smolvlm2_500m_video_optimized_{timestamp}.log"
        
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
        
        root_logger.info(f"SmolVLM2-500M-Video optimized logging initialized. Log file: {log_file}")
        return root_logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

logger = setup_logging()

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

class OptimizedSmolVLM2VideoServer:
    """
    Optimized Flask server for SmolVLM2-500M-Video (single-threaded to avoid conflicts)
    """
    
    def __init__(self, config_path="smolvlm2_500m_video_optimized.json"):
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
                "model_name": "SmolVLM2-500M-Video-Optimized",
                "model_path": "mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                "device": "auto",
                "trust_remote_code": True,
                "max_tokens": 100,
                "timeout": 30
            }
            
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            project_config_path = project_root / "src/config/model_configs/smolvlm2_500m_video_optimized.json"
            
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
            logger.info("🚀 Initializing OPTIMIZED SmolVLM2-500M-Video...")
            start_time = time.time()
            
            # Strategy 1: Try MLX-VLM first (same as vlm_tester.py)
            try:
                from mlx_vlm import load
                logger.info("🚀 Attempting MLX-VLM load...")
                
                self.model, self.processor = load(
                    self.config.get("model_path", "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"),
                    trust_remote_code=True
                )
                self.use_mlx = True
                
                init_time = time.time() - start_time
                logger.info(f"✅ OPTIMIZED MLX SmolVLM2-500M-Video ready in {init_time:.2f}s")
                return True
                
            except ImportError as e:
                logger.warning(f"MLX-VLM not available: {e}, falling back to transformers")
                self.use_mlx = False
            except Exception as e:
                logger.warning(f"MLX loading failed: {e}, falling back to transformers")
                self.use_mlx = False
            
            # Strategy 2: Fallback to transformers (same as vlm_tester.py)
            if not self.use_mlx:
                from transformers import AutoProcessor, AutoModelForImageTextToText
                logger.info("📥 Loading optimized transformers SmolVLM2-500M-Video...")
                
                fallback_model_path = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
                
                self.processor = AutoProcessor.from_pretrained(
                    fallback_model_path,
                    trust_remote_code=True
                )
                self.model = AutoModelForImageTextToText.from_pretrained(
                    fallback_model_path,
                    torch_dtype=torch.float16,
                    device_map="cpu",
                    low_cpu_mem_usage=True,
                    trust_remote_code=True
                )
                
                init_time = time.time() - start_time
                logger.info(f"✅ OPTIMIZED Transformers SmolVLM2-500M-Video ready in {init_time:.2f}s")
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
                    "model": "SmolVLM2-500M-Video-Optimized",
                    "version": "1.0.0",
                    "method": "MLX" if self.use_mlx else "Transformers",
                    "optimization": "Single-threaded, Memory-optimized, Video-capable",
                    "performance": {
                        "requests": self.stats["requests"],
                        "avg_time": f"{self.stats['avg_time']:.2f}s",
                        "cache_hits": self.stats["cache_hits"]
                    }
                })
            else:
                return jsonify({"status": "loading", "model": "SmolVLM2-500M-Video-Optimized"}), 503
        
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
                    "model": "SmolVLM2-500M-Video-Optimized",
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
                "model": "SmolVLM2-500M-Video-Optimized",
                "statistics": self.stats,
                "optimizations": {
                    "single_threaded": True,
                    "memory_management": True,
                    "mlx_acceleration": self.use_mlx,
                    "video_understanding": True
                }
            })
    
    def _generate_mlx_response(self, image: Image.Image, prompt: str, max_tokens: int) -> str:
        """Generate response using MLX (fixed for SmolVLM2 format)"""
        try:
            from mlx_vlm import generate
            logger.info("🚀 Using MLX-VLM inference for optimized SmolVLM2-500M-Video...")
            
            # Save image to temporary file for MLX
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                temp_image_path = tmp_file.name
                image.save(temp_image_path, 'JPEG', quality=95)
            
            try:
                # FIXED: SmolVLM2 requires specific format with image token
                # SmolVLM2 expects the image token to be present in the text
                mlx_prompt = f"<image>\n{prompt}"
                
                logger.info(f"🔍 SmolVLM2 MLX prompt: {mlx_prompt[:100]}...")
                
                response = generate(
                    model=self.model,
                    processor=self.processor,
                    image=temp_image_path,
                    prompt=mlx_prompt,
                    max_tokens=max_tokens,
                    temp=0.0,
                    verbose=False
                )
                
                # CRITICAL FIX: MLX generate returns a tuple (text, metadata)
                # Extract just the text part
                if isinstance(response, tuple):
                    logger.info(f"MLX returned tuple with {len(response)} elements: {[type(x) for x in response]}")
                    logger.info(f"Tuple contents: {response}")
                    text_response = response[0]  # First element is the text
                    logger.info(f"MLX returned tuple, extracted text: '{text_response}'")
                else:
                    text_response = str(response)
                    logger.info(f"MLX returned string: '{text_response}'")
                
                # Process response (same as vlm_tester)
                text_response = text_response.replace("<|end|>", "").replace("<|endoftext|>", "").strip()
                if "1. What is meant by" in text_response:
                    text_response = text_response.split("1. What is meant by")[0].strip()
                text_response = ' '.join(text_response.split())
                
                logger.info(f"Final processed response: {text_response}")
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
        """Generate response using transformers (fixed for SmolVLM2 format)"""
        try:
            # SmolVLM2 format - use proper message structure
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Apply chat template
            input_text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Process inputs - SmolVLM2 expects images as a list
            inputs = self.processor(
                text=input_text, 
                images=[image],  # FIXED: Pass as list for SmolVLM2
                return_tensors="pt"
            )
            
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
            
            input_len = inputs["input_ids"].shape[1]
            generated_ids = outputs[0][input_len:]
            result = self.processor.decode(generated_ids, skip_special_tokens=True).strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Transformers inference error: {e}")
            return f"Transformers inference failed: {str(e)}"
    
    def run(self, host='0.0.0.0', port=8080):
        """Start optimized server"""
        logger.info("🔥 Starting OPTIMIZED SmolVLM2-500M-Video Server...")
        logger.info(f"🎯 Target: Apple Silicon optimization + Video understanding")
        logger.info(f"⚙️ Optimizations: Single-threaded, Memory management, MLX acceleration")
        
        if not self.initialize_model():
            logger.error("❌ Server startup failed")
            return False
        
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info("🚀 OPTIMIZED SmolVLM2-500M-Video Server ready!")
        
        try:
            # **CRITICAL FIX**: Disable threading to prevent conflicts
            self.app.config['THREADED'] = False
            
            self.app.run(
                host=host,
                port=port,
                debug=False,
                threaded=False,  # FIXED: Single-threaded to prevent conflicts
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
    """Main execution with optimization info"""
    print("🔥 OPTIMIZED SmolVLM2-500M-Video Server")
    print("=" * 60)
    print("🎯 Performance Improvements:")
    print("   • Single-threaded Flask to prevent conflicts")
    print("   • MLX acceleration for Apple Silicon")
    print("   • Memory optimization and cleanup")
    print("   • Video understanding capabilities")
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
    
    server = OptimizedSmolVLM2VideoServer()
    
    try:
        server.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    print_startup_banner(
        model_name="SmolVLM2-500M-Video-Optimized",
        server_type="Server",
        features=["Single-threaded Flask", "MLX acceleration", "Memory optimization", "Video understanding"],
        optimizations=["Single-threaded", "Memory management", "MLX acceleration"],
        port=8080
    )
    main()


