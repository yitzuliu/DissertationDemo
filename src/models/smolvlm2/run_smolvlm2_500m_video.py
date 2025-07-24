#!/usr/bin/env python3
"""
SmolVLM2-500M-Video Standard Server Runner

Standard version of SmolVLM2-500M-Video server with:
- MLX-VLM with transformers fallback (same pattern as phi3_vision)
- Flask server for compatibility
- Proper configuration integration
"""

import os
import json
import logging
import time
import base64
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from flask import Flask, request, jsonify
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
        log_file = log_dir / f"smolvlm2_500m_video_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"SmolVLM2-500M-Video standard logging initialized. Log file: {log_file}")
        return logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        raise

logger = setup_logging()

class SmolVLM2VideoServer:
    """Standard SmolVLM2-500M-Video Server (same pattern as phi3_vision)"""
    
    def __init__(self, config_path="smolvlm2_500m_video.json"):
        self.app = Flask(__name__)
        self.model = None
        self.processor = None
        self.config = self.load_config(config_path)
        self.use_mlx = False
        self.setup_routes()
        
        self.stats = {
            "requests": 0,
            "total_time": 0.0,
            "avg_time": 0.0
        }
    
    def load_config(self, config_path):
        """Load standard configuration (same pattern as phi3_vision)"""
        try:
            default_config = {
                "model_name": "SmolVLM2-500M-Video",
                "model_path": "mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                "device": "auto",
                "trust_remote_code": True,
                "max_tokens": 100,
                "timeout": 60
            }
            
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            project_config_path = project_root / "src/config/model_configs/smolvlm2_500m_video.json"
            
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
            
            return default_config
            
        except Exception as e:
            logger.error(f"Config loading error: {e}")
            return {
                "model_name": "SmolVLM2-500M-Video",
                "model_path": "mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                "device": "auto",
                "trust_remote_code": True,
                "max_tokens": 100,
                "timeout": 60
            }
    
    def initialize_model(self):
        """Initialize model with MLX and transformers fallback (same as phi3_vision)"""
        try:
            logger.info("🚀 Initializing SmolVLM2-500M-Video...")
            start_time = time.time()
            
            # Strategy 1: Try MLX-VLM first (same as phi3_vision and vlm_tester)
            try:
                from mlx_vlm import load
                logger.info("🚀 Attempting MLX-VLM load...")
                
                self.model, self.processor = load(
                    self.config.get("model_path", "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"),
                    trust_remote_code=True
                )
                self.use_mlx = True
                
                init_time = time.time() - start_time
                logger.info(f"✅ MLX SmolVLM2-500M-Video loaded in {init_time:.2f}s")
                return True
                
            except ImportError as e:
                logger.warning(f"MLX-VLM not available: {e}, falling back to transformers")
                self.use_mlx = False
            except Exception as e:
                logger.warning(f"MLX loading failed: {e}, falling back to transformers")
                self.use_mlx = False
            
            # Strategy 2: Fallback to transformers (same as phi3_vision)
            if not self.use_mlx:
                from transformers import AutoProcessor, AutoModelForImageTextToText
                logger.info("📥 Loading transformers SmolVLM2-500M-Video...")
                
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
                logger.info(f"✅ Transformers SmolVLM2-500M-Video loaded in {init_time:.2f}s")
                return True
                
        except Exception as e:
            logger.error(f"❌ Model initialization error: {e}")
            return False
    
    def setup_routes(self):
        """Setup Flask routes (same pattern as phi3_vision)"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            if self.model and self.processor:
                return jsonify({
                    "status": "healthy",
                    "model": "SmolVLM2-500M-Video",
                    "version": "1.0.0",
                    "framework": "Flask",
                    "method": "MLX" if self.use_mlx else "Transformers",
                    "performance": {
                        "requests": self.stats["requests"],
                        "avg_time": f"{self.stats['avg_time']:.2f}s"
                    }
                })
            else:
                return jsonify({"status": "loading", "model": "SmolVLM2-500M-Video"}), 503
        
        @self.app.route('/v1/chat/completions', methods=['POST'])
        def chat_completions():
            """OpenAI-compatible chat completions endpoint"""
            try:
                start_time = time.time()
                
                if not self.model or not self.processor:
                    return jsonify({"error": "Model not ready"}), 503
                
                data = request.get_json()
                messages = data.get('messages', [])
                max_tokens = min(data.get('max_tokens', 100), 200)
                
                if not messages:
                    return jsonify({"error": "No messages provided"}), 400
                
                # Extract user message (same pattern as phi3_vision)
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
                
                # Process image
                try:
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                except Exception as e:
                    return jsonify({"error": f"Image processing failed: {e}"}), 400
                
                # Generate response using same logic as phi3_vision
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
                    "model": "SmolVLM2-500M-Video",
                    "performance": {
                        "processing_time": f"{processing_time:.2f}s",
                        "framework": "Flask",
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
                "model": "SmolVLM2-500M-Video",
                "statistics": self.stats,
                "framework": "Flask",
                "method": "MLX" if self.use_mlx else "Transformers",
                "features": {
                    "mlx_support": True,
                    "transformers_fallback": True,
                    "video_understanding": True
                }
            })
    
    def _generate_mlx_response(self, image: Image.Image, prompt: str, max_tokens: int) -> str:
        """Generate response using MLX (fixed for SmolVLM2 format)"""
        try:
            from mlx_vlm import generate
            logger.info("🚀 Using MLX-VLM inference for SmolVLM2-500M-Video...")
            
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
                
                # Process response (same as vlm_tester)
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
        """Start standard server"""
        logger.info("🚀 Starting SmolVLM2-500M-Video Server...")
        logger.info(f"🎯 Target: Video understanding with MLX optimization")
        logger.info(f"🔧 Framework: Flask with MLX-VLM + Transformers")
        
        if not self.initialize_model():
            logger.error("❌ Server startup failed")
            return False
        
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info("🚀 SmolVLM2-500M-Video Server ready!")
        
        try:
            self.app.run(
                host=host,
                port=port,
                debug=False,
                threaded=True,
                use_reloader=False
            )
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
            return False
        
        return True

def main():
    """Main execution"""
    print("🔥 SmolVLM2-500M-Video Standard Server")
    print("=" * 50)
    print("🎯 Features:")
    print("   • Video understanding capabilities")
    print("   • MLX-VLM with transformers fallback")
    print("   • Flask server for compatibility")
    print("   • Robust error handling")
    print("=" * 50)
    
    # Check MLX availability
    try:
        import mlx.core as mx
        logger.info("✅ MLX framework available")
    except ImportError:
        logger.warning("⚠️ MLX not available, will use transformers fallback")
    
    server = SmolVLM2VideoServer()
    
    try:
        server.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
