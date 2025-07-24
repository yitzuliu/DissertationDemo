"""
SmolVLM2-500M-Video Model Server

Standard implementation of SmolVLM2 500M Video model with enhanced video understanding capabilities.
Uses Flask framework for API serving.
"""

import os
import sys
import logging
import json
import base64
import io
import time
from pathlib import Path
from flask import Flask, request, jsonify
from PIL import Image
import torch
from transformers import AutoTokenizer, AutoProcessor, LlavaForConditionalGeneration
import warnings

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
MODEL_ID = "smolvlm2_500m_video"  # This matches the config file name
MODEL_NAME = "SmolVLM2-500M-Video"  # This is the display name

class SmolVLM2VideoModel:
    """SmolVLM2 500M Video model handler"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.tokenizer = None
        self.device = None
        self.config = None
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
                "device": "auto",
                "model_config": {
                    "torch_dtype": "float16",
                    "device_map": "auto", 
                    "trust_remote_code": True,
                    "low_cpu_mem_usage": True
                },
                "generation_config": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": False,
                    "repetition_penalty": 1.1
                }
            }
    
    def load_model(self):
        """Load the SmolVLM2 model and processor"""
        try:
            logger.info(f"Loading {MODEL_NAME} model...")
            start_time = time.time()
            
            model_path = self.config.get("model_path", "HuggingFaceTB/SmolVLM2-500M-Video-Instruct")
            model_config = self.config.get("model_config", {})
            
            # Determine device
            device_setting = self.config.get("device", "auto")
            if device_setting == "auto":
                if torch.cuda.is_available():
                    self.device = "cuda"
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self.device = "mps"
                else:
                    self.device = "cpu"
            else:
                self.device = device_setting
            
            logger.info(f"Using device: {self.device}")
            
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
            
            # Configure torch dtype
            torch_dtype = model_config.get("torch_dtype", "float16")
            if torch_dtype == "float16":
                dtype = torch.float16
            elif torch_dtype == "float32":
                dtype = torch.float32
            else:
                dtype = torch.float16  # Default
            
            # Load SmolVLM2 model
            self.model = AutoModelForImageTextToText.from_pretrained(
                model_path,
                torch_dtype=dtype,
                device_map=model_config.get("device_map", "auto"),
                trust_remote_code=model_config.get("trust_remote_code", True),
                low_cpu_mem_usage=model_config.get("low_cpu_mem_usage", True)
            )
            
            # Move to device if needed
            if self.device != "auto" and self.device != "cuda":
                self.model = self.model.to(self.device)
            
            load_time = time.time() - start_time
            logger.info(f"{MODEL_NAME} loaded successfully in {load_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Failed to load {MODEL_NAME}: {e}")
            raise
    
    def preprocess_image(self, image_data):
        """Preprocess image for the model"""
        try:
            # Decode base64 image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Get image processing config
            img_config = self.config.get("image_processing", {})
            
            # Resize if needed
            if "size" in img_config:
                target_size = img_config["size"]
                if isinstance(target_size, (list, tuple)) and len(target_size) >= 2:
                    width, height = int(target_size[0]), int(target_size[1])
                    if img_config.get("preserve_aspect_ratio", True):
                        image.thumbnail((width, height), Image.Resampling.LANCZOS)
                    else:
                        image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise
    
    def generate_response(self, image, text_input):
        """Generate response using SmolVLM2"""
        try:
            # Get generation config
            gen_config = self.config.get("generation_config", {})
            
            # Process inputs for SmolVLM2
            inputs = self.processor(
                text=text_input,
                images=image,
                return_tensors="pt"
            )
            
            # Move inputs to device
            if self.device and self.device != "cpu":
                inputs = {k: v.to(self.device) if hasattr(v, 'to') else v for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=gen_config.get("max_new_tokens", 150),
                    temperature=gen_config.get("temperature", 0.7),
                    top_p=gen_config.get("top_p", 0.9),
                    do_sample=gen_config.get("do_sample", False),
                    repetition_penalty=gen_config.get("repetition_penalty", 1.1),
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Decode response
            generated_text = self.processor.batch_decode(
                outputs, 
                skip_special_tokens=True
            )[0].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

# Initialize model
model_handler = SmolVLM2VideoModel()

# Create Flask app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": MODEL_NAME,
        "model_id": MODEL_ID,
        "device": getattr(model_handler, 'device', 'unknown')
    })

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint"""
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
        
        # Process image and generate response
        image = model_handler.preprocess_image(image_data)
        response_text = model_handler.generate_response(image, text_input)
        
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
        "status": "running"
    })

def main():
    """Main function to start the server"""
    try:
        # Load model
        model_handler.load_model()
        
        # Get server config
        server_config = model_handler.config.get("server", {})
        host = server_config.get("host", "0.0.0.0")
        port = server_config.get("port", 8080)
        
        logger.info(f"Starting {MODEL_NAME} server on {host}:{port}")
        
        # Start Flask server
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=server_config.get("threaded", True)
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
