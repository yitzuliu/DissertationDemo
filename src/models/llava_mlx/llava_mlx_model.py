from pathlib import Path
import sys
import os
import tempfile
import base64
from io import BytesIO
from PIL import Image
from typing import Dict, Any, cast
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
        # The load_model call is deferred to the server runner

    def load_model(self):
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

    def generate_response(self, image: Image.Image, prompt: str):
        if not self.loaded or self.model is None or self.processor is None:
            raise RuntimeError("Model is not loaded.")
        
        print("Generating response with LLaVA MLX...")
        
        # mlx-vlm's generate function expects an image file path
        # We save the PIL image to a temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
        os.close(temp_fd)
        image.save(temp_path, 'JPEG')

        try:
            from mlx_vlm import generate
            inference_params = self.config.get("inference_params", {})
            
            # The 'processor' from mlx-vlm can be a tuple, so we handle it gracefully.
            # We pass it to `generate` which knows how to handle it internally.
            response = generate(
                model=self.model,
                processor=cast(PreTrainedTokenizer, self.processor),
                prompt=prompt,
                image=temp_path,
                max_tokens=inference_params.get("max_tokens", 100),
                temp=inference_params.get("temperature", 0.0),
                verbose=False
            )

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

    def process_messages(self, messages):
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

    # The abstract methods from BaseVisionModel need to be implemented
    def predict(self, image: Any, prompt: str, options: Dict[str, Any] | None = None) -> Dict[str, Any]:
        pil_image = Image.fromarray(image) if not isinstance(image, Image.Image) else image
        response = self.generate_response(pil_image, prompt)
        return {"response": response}
    
    def preprocess_image(self, image: Any) -> Any:
        # MLX-VLM handles preprocessing internally via file path, so we just pass the image through.
        return image
    
    def format_response(self, raw_response: Any) -> Dict[str, Any]:
        return raw_response # The response is already a dictionary

if __name__ == '__main__':
    print("This script is not meant to be run directly. Use a runner script.") 