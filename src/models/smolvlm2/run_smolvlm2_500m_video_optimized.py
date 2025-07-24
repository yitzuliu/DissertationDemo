"""
SmolVLM2-500M-Video-Optimized Model Server

Optimized implementation of SmolVLM2 500M Video model with Apple Silicon MPS acceleration,
memory optimizations, image caching, and performance enhancements.
"""

import os
import sys
import logging
import json
import base64
import io
import time
import gc
from pathlib import Path
from flask import Flask, request, jsonify
from PIL import Image
import torch
from transformers import AutoTokenizer, AutoProcessor, LlavaForConditionalGeneration
import warnings
from functools import lru_cache
import hashlib

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from backend.utils.config_manager import config_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configuration
MODEL_ID = "smolvlm2_500m_video_optimized"  # This matches the config file name
MODEL_NAME = "SmolVLM2-500M-Video-Optimized"  # This is the display name

class ImageCache:
    """Simple image cache for optimization"""
    
    def __init__(self, max_size=15):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def _generate_key(self, image_data):
        """Generate cache key from image data"""
        return hashlib.md5(image_data.encode() if isinstance(image_data, str) else image_data).hexdigest()
    
    def get(self, image_data):
        """Get cached image"""
        key = self._generate_key(image_data)
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, image_data, processed_image):
        """Cache processed image"""
        key = self._generate_key(image_data)
        
        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = processed_image
        if key not in self.access_order:
            self.access_order.append(key)
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_order.clear()

class SmolVLM2VideoOptimizedModel:
    """Optimized SmolVLM2 500M Video model handler with Apple Silicon optimizations"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.tokenizer = None
        self.device = None
        self.config = None
        self.image_cache = ImageCache()
        self.load_config()
        
    def load_config(self):
        """Load model configuration"""
        try:
            self.config = config_manager.load_model_config(MODEL_ID)
            if not self.config:
                raise ValueError(f"No configuration found for model {MODEL_ID}")
            logger.info(f"Loaded configuration for {MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Fallback configuration with correct model path
            self.config = {
                "model_path": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct",
                "device": "mps",
                "model_config": {
                    "torch_dtype": "float16",
                    "device_map": "mps",
                    "trust_remote_code": True,
                    "low_cpu_mem_usage": True,
                    "use_cache": True
                },
                "generation_config": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": False,
                    "repetition_penalty": 1.1,
                    "use_cache": True
                },
                "image_processing": {
                    "cache_enabled": True,
                    "smart_crop": True
                },
                "performance": {
                    "mps_acceleration": True,
                    "memory_optimization": True,
                    "image_caching": True
                }
            }
    
    def load_model(self):
        """Load the SmolVLM2 model and processor with optimizations"""
        try:
            logger.info(f"Loading {MODEL_NAME} model with optimizations...")
            start_time = time.time()
            
            model_path = self.config.get("model_path", "HuggingFaceTB/SmolVLM2-500M-Video-Instruct")
            model_config = self.config.get("model_config", {})
            
            # Determine device with MPS preference for Apple Silicon
            device_setting = self.config.get("device", "auto")
            if device_setting == "auto":
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self.device = "mps"
                    logger.info("Apple Silicon MPS acceleration enabled")
                elif torch.cuda.is_available():
                    self.device = "cuda"
                else:
                    self.device = "cpu"
            else:
                self.device = device_setting
            
            logger.info(f"Using device: {self.device}")
            
            # Enable memory optimizations for MPS
            if self.device == "mps":
                torch.mps.empty_cache()
                # Set memory fraction for MPS
                os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.8'
            
            # Load processor and tokenizer for SmolVLM2
            from transformers import AutoProcessor, AutoTokenizer, AutoModelForImageTextToText
            
            self.processor = AutoProcessor.from_pretrained(
                model_path,
                trust_remote_code=model_config.get("trust_remote_code", True)
            )
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=model_config.get("trust_remote_code", True)
            )
            
            # Configure torch dtype for optimization
            torch_dtype = model_config.get("torch_dtype", "float16")
            if torch_dtype == "float16" and self.device == "mps":
                dtype = torch.float16  # MPS supports float16
            elif torch_dtype == "float32":
                dtype = torch.float32
            else:
                dtype = torch.float16  # Default
            
            # Load SmolVLM2 model with optimized configuration
            self.model = AutoModelForImageTextToText.from_pretrained(
                model_path,
                torch_dtype=dtype,
                device_map=model_config.get("device_map", "auto") if self.device != "mps" else None,
                trust_remote_code=model_config.get("trust_remote_code", True),
                low_cpu_mem_usage=model_config.get("low_cpu_mem_usage", True)
            )
            
            # Move to MPS device
            if self.device == "mps":
                self.model = self.model.to(self.device)
            
            # Enable model optimizations
            if hasattr(self.model, 'eval'):
                self.model.eval()
            
            # Memory cleanup
            gc.collect()
            if self.device == "mps":
                torch.mps.empty_cache()
            
            load_time = time.time() - start_time
            logger.info(f"{MODEL_NAME} loaded successfully in {load_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Failed to load {MODEL_NAME}: {e}")
            raise
    
    def preprocess_image(self, image_data):
        """Optimized image preprocessing with caching"""
        try:
            # Check cache first
            img_config = self.config.get("image_processing", {})
            if img_config.get("cache_enabled", True):
                cached_image = self.image_cache.get(image_data)
                if cached_image is not None:
                    logger.debug("Using cached preprocessed image")
                    return cached_image
            
            # Decode base64 image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Apply smart cropping and resizing
            if "size" in img_config:
                target_size = img_config["size"]
                if isinstance(target_size, (list, tuple)) and len(target_size) >= 2:
                    width, height = int(target_size[0]), int(target_size[1])
                    
                    # Smart crop for better image quality
                    if img_config.get("smart_crop", True):
                        # Calculate aspect ratio
                        img_ratio = image.width / image.height
                        target_ratio = width / height
                        
                        if img_ratio > target_ratio:
                            # Image is wider, crop horizontally
                            new_width = int(image.height * target_ratio)
                            left = (image.width - new_width) // 2
                            image = image.crop((left, 0, left + new_width, image.height))
                        elif img_ratio < target_ratio:
                            # Image is taller, crop vertically
                            new_height = int(image.width / target_ratio)
                            top = (image.height - new_height) // 2
                            image = image.crop((0, top, image.width, top + new_height))
                    
                    # Resize with high quality
                    if img_config.get("preserve_aspect_ratio", True):
                        image.thumbnail((width, height), Image.Resampling.LANCZOS)
                    else:
                        image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Cache the processed image
            if img_config.get("cache_enabled", True):
                self.image_cache.set(image_data, image)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise
    
    def generate_response(self, image, text_input):
        """Optimized response generation with MPS acceleration"""
        try:
            start_time = time.time()
            
            # Get generation config
            gen_config = self.config.get("generation_config", {})
            
            # Process inputs for SmolVLM2
            inputs = self.processor(
                text=text_input,
                images=image,
                return_tensors="pt"
            )
            
            # Move inputs to device with optimization
            if self.device and self.device != "cpu":
                inputs = {k: v.to(self.device, non_blocking=True) if hasattr(v, 'to') else v 
                         for k, v in inputs.items()}
            
            # Generate response with optimizations
            with torch.no_grad():
                if self.device == "mps":
                    # MPS-specific optimizations
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=gen_config.get("max_new_tokens", 150),
                        temperature=gen_config.get("temperature", 0.7),
                        top_p=gen_config.get("top_p", 0.9),
                        do_sample=gen_config.get("do_sample", False),
                        repetition_penalty=gen_config.get("repetition_penalty", 1.1),
                        pad_token_id=self.processor.tokenizer.eos_token_id,
                        use_cache=gen_config.get("use_cache", True)
                    )
                else:
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=gen_config.get("max_new_tokens", 150),
                        temperature=gen_config.get("temperature", 0.7),
                        top_p=gen_config.get("top_p", 0.9),
                        do_sample=gen_config.get("do_sample", False),
                        repetition_penalty=gen_config.get("repetition_penalty", 1.1),
                        pad_token_id=self.processor.tokenizer.eos_token_id,
                        use_cache=gen_config.get("use_cache", True)
                    )
            
            # Decode response
            generated_text = self.processor.batch_decode(
                outputs, 
                skip_special_tokens=True
            )[0].strip()
            
            # Memory cleanup for MPS
            if self.device == "mps":
                del inputs, outputs
                torch.mps.empty_cache()
            
            generation_time = time.time() - start_time
            logger.debug(f"Response generated in {generation_time:.2f} seconds")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            # Cleanup on error
            if self.device == "mps":
                torch.mps.empty_cache()
            raise
    
    def cleanup_memory(self):
        """Perform memory cleanup"""
        gc.collect()
        if self.device == "mps":
            torch.mps.empty_cache()
        
        # Clear image cache periodically
        cache_size = len(self.image_cache.cache)
        if cache_size > self.image_cache.max_size * 0.8:  # Clear when 80% full
            logger.debug(f"Clearing image cache ({cache_size} items)")
            self.image_cache.clear()

# Initialize model
model_handler = SmolVLM2VideoOptimizedModel()

# Create Flask app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": MODEL_NAME,
        "model_id": MODEL_ID,
        "device": getattr(model_handler, 'device', 'unknown'),
        "optimizations": {
            "mps_acceleration": model_handler.config.get("performance", {}).get("mps_acceleration", False),
            "image_caching": model_handler.config.get("performance", {}).get("image_caching", False),
            "memory_optimization": model_handler.config.get("performance", {}).get("memory_optimization", False)
        }
    })

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint with optimizations"""
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({"error": "Invalid request format"}), 400
        
        messages = data['messages']
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
        
        # Extract the last user message
        user_message = None
        for message in reversed(messages):
            if message.get('role') == 'user':
                user_message = message
                break
        
        if not user_message:
            return jsonify({"error": "No user message found"}), 400
        
        # Process content
        content = user_message.get('content', [])
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        
        text_input = ""
        image_data = None
        
        for item in content:
            if item.get('type') == 'text':
                text_input = item.get('text', '')
            elif item.get('type') == 'image_url':
                image_url = item.get('image_url', {}).get('url', '')
                if image_url:
                    image_data = image_url
        
        if not text_input:
            return jsonify({"error": "No text input provided"}), 400
        
        if not image_data:
            return jsonify({"error": "No image provided"}), 400
        
        # Process image and generate response with optimizations
        image = model_handler.preprocess_image(image_data)
        response_text = model_handler.generate_response(image, text_input)
        
        # Periodic memory cleanup
        model_handler.cleanup_memory()
        
        # Return OpenAI-compatible response
        return jsonify({
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(text_input.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(text_input.split()) + len(response_text.split())
            }
        })
        
    except Exception as e:
        logger.error(f"Error in chat completions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": f"{MODEL_NAME} API Server",
        "model": MODEL_NAME,
        "model_id": MODEL_ID,
        "status": "running",
        "optimizations": "Apple Silicon MPS, Image Caching, Memory Management"
    })

@app.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Cache statistics endpoint"""
    return jsonify({
        "image_cache_size": len(model_handler.image_cache.cache),
        "cache_max_size": model_handler.image_cache.max_size,
        "cache_utilization": f"{len(model_handler.image_cache.cache) / model_handler.image_cache.max_size * 100:.1f}%"
    })

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache endpoint"""
    model_handler.image_cache.clear()
    model_handler.cleanup_memory()
    return jsonify({"status": "Cache cleared successfully"})

def main():
    """Main function to start the optimized server"""
    try:
        # Load model
        model_handler.load_model()
        
        # Get server config
        server_config = model_handler.config.get("server", {})
        host = server_config.get("host", "0.0.0.0")
        port = server_config.get("port", 8080)
        
        logger.info(f"Starting {MODEL_NAME} server on {host}:{port}")
        logger.info("Optimizations enabled: MPS acceleration, Image caching, Memory management")
        
        # Start Flask server with threading optimization
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=server_config.get("threaded", True),
            processes=server_config.get("processes", 1)
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        # Cleanup on exit
        model_handler.cleanup_memory()
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
