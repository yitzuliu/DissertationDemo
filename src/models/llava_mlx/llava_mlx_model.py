from pathlib import Path
import sys
import os
import tempfile
import base64
import gc
import torch
from io import BytesIO
from PIL import Image
from typing import Dict, Any, cast, Optional
from transformers.tokenization_utils import PreTrainedTokenizer

# Add project root to path for module imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.models.base_model import BaseVisionModel

class LlavaMlxModel(BaseVisionModel):
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name=model_name, config=config)
        self.model_id = self.config.get("model_id", "mlx-community/llava-v1.6-mistral-7b-4bit")
        self.model = None
        self.processor = None
        self.loaded = False
        self.stats = {"requests": 0, "total_time": 0.0}
        # The load_model call is deferred to the server runner

    def load_model(self):
        """Load LLaVA MLX model using MLX-VLM framework (same as testing framework)"""
        print(f"Loading LLaVA MLX model: {self.model_id}...")
        try:
            from mlx_vlm import load
            self.model, self.processor = load(self.model_id)
            self.loaded = True
            print("LLaVA MLX model loaded successfully.")
            return True
        except ImportError:
            raise RuntimeError("MLX-VLM is not installed. Please run: pip install mlx-vlm")
        except Exception as e:
            raise RuntimeError(f"Failed to load LLaVA MLX model: {e}")

    def generate_response(self, image: Image.Image, prompt: str, max_tokens: int = 100) -> str:
        """Generate response with LLaVA MLX using MLX-VLM framework (same as testing framework)"""
        if not self.loaded or self.model is None or self.processor is None:
            raise RuntimeError("Model is not loaded.")
        
        print("Generating response with LLaVA MLX...")
        
        # Unified image preprocessing (same as testing framework)
        original_size = image.size
        unified_image_size = 1024
        if max(image.size) > unified_image_size:
            ratio = unified_image_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # mlx-vlm's generate function expects an image file path
        # We save the PIL image to a temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
        os.close(temp_fd)
        image.save(temp_path, 'JPEG')

        try:
            from mlx_vlm import generate
            
            # Use unified generation parameters (same as testing framework)
            unified_generation_params = {
                "max_new_tokens": max_tokens,
                "do_sample": False
            }
            
            # Generate response using MLX-VLM (same as testing framework)
            response = generate(
                model=self.model,
                processor=cast(PreTrainedTokenizer, self.processor),
                prompt=prompt,
                image=temp_path,
                max_tokens=unified_generation_params["max_new_tokens"],
                temp=0.0,  # Use 0.0 for deterministic output
                verbose=False
            )

            # Handle MLX-VLM response format (tuple with text and metadata) - same as testing framework
            if isinstance(response, tuple) and len(response) >= 1:
                text_response = response[0] if response[0] else ""
            else:
                text_response = str(response) if response else ""
            
            return text_response.strip()

        except Exception as e:
            print(f"Error during LLaVA MLX inference: {e}")
            return f"Inference failed: {e}"
        finally:
            # Clean up the temporary file
            os.remove(temp_path)
            # Clear the model's KV cache to prevent errors on subsequent runs
            self.clear_cache()

    def clear_cache(self):
        """
        Workaround to manually reset the KV cache in the model's layers.
        The mlx-vlm library appears to retain state, causing errors on subsequent calls.
        This method attempts to find and delete the cache attributes from the attention layers.
        """
        if self.model is None:
            return

        try:
            # Try to clear MLX cache if available
            if hasattr(self.model, 'language_model') and hasattr(self.model.language_model, 'model'):
                layers = self.model.language_model.model.layers
                for layer in layers:
                    if hasattr(layer, "self_attn"):
                        # The cache is not a documented attribute, so we speculatively
                        # try to delete common names for it.
                        if hasattr(layer.self_attn, "cache"):
                            del layer.self_attn.cache
                        if hasattr(layer.self_attn, "kv_cache"):
                            del layer.self_attn.kv_cache
        except AttributeError:
            # If the model structure is not as expected, do nothing.
            pass
        
        # Force garbage collection
        gc.collect()

    def process_messages(self, messages):
        """Process messages in the format expected by the API"""
        prompt = "Describe the image."
        image_data_url = None

        user_content = messages[0].get("content", [])
        for item in user_content:
            if item.get("type") == "text":
                prompt = item.get("text", prompt)
            elif item.get("type") == "image_url":
                image_data_url = item["image_url"]["url"]

        if not image_data_url:
            raise ValueError("No image provided in the message content.")
        
        # Manually decode the base64 image data
        if image_data_url.startswith('data:image/'):
            base64_data = image_data_url.split(',')[1]
            image_bytes = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            return image, prompt
        else:
            raise ValueError("Unsupported image URL format. Please use base64 data URI.")

    def predict(self, image: Any, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Predict method for compatibility with BaseVisionModel"""
        pil_image = Image.fromarray(image) if not isinstance(image, Image.Image) else image
        response = self.generate_response(pil_image, prompt)
        return {"response": response}
    
    def preprocess_image(self, image: Any) -> Any:
        """Preprocess image for LLaVA MLX model (unified preprocessing)"""
        # Unified image preprocessing (same as testing framework)
        if isinstance(image, Image.Image):
            original_size = image.size
            unified_image_size = 1024
            if max(image.size) > unified_image_size:
                ratio = unified_image_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
        return image
    
    def format_response(self, raw_response: Any) -> Dict[str, Any]:
        """Format response for API compatibility"""
        return raw_response if isinstance(raw_response, dict) else {"response": raw_response}

    def unload_model(self) -> bool:
        """Unload model and clean up memory"""
        try:
            if self.model is not None:
                del self.model
                self.model = None
            if self.processor is not None:
                del self.processor
                self.processor = None
            
            self.loaded = False
            gc.collect()
            return True
        except Exception as e:
            print(f"Error unloading LLaVA MLX model: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "model_id": self.model_id,
            "loaded": self.loaded,
            "framework": "MLX-VLM",
            "device": "Apple Silicon (M1/M2/M3)",
            "stats": self.stats
        }

if __name__ == '__main__':
    print("This script is not meant to be run directly. Use a runner script.") 