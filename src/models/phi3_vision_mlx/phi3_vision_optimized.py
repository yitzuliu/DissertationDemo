"""
Optimized Phi-3.5-Vision Model Implementation

This module provides the optimized Phi-3.5-Vision model implementation
with MLX acceleration, caching, and performance optimizations.
"""

from pathlib import Path
import sys
import os
import tempfile
import base64
import gc
import torch
from io import BytesIO
from PIL import Image
from typing import Dict, Any, Optional

# Add project root to path for module imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.models.base_model import BaseVisionModel

class OptimizedPhi3VisionModel(BaseVisionModel):
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name=model_name, config=config)
        self.model_id = self.config.get("model_path", "mlx-community/Phi-3.5-vision-instruct-4bit")
        
        print(f"🔧 Optimized Phi-3 Vision Model initialized with model_path: {self.model_id}")
        
        self.model = None
        self.processor = None
        self.loaded = False
        self.stats = {"requests": 0, "total_time": 0.0}
        self.use_mlx = False

    def load_model(self):
        """Load optimized Phi-3.5-Vision model with MLX and fallbacks"""
        print(f"Loading optimized Phi-3.5-Vision model: {self.model_id}...")
        
        # Strategy 1: Try MLX-VLM first (參考 run_phi3_vision.py 的成功策略)
        try:
            from mlx_vlm import load, generate
            print(f"🚀 Attempting MLX-VLM load: {self.model_id}")
            
            self.model, self.processor = load(self.model_id, trust_remote_code=True)
            self.use_mlx = True
            self.loaded = True
            print("✅ MLX Phi-3.5-Vision model loaded successfully")
            return True
            
        except ImportError as e:
            print(f"⚠️ MLX-VLM not available: {e}, trying transformers fallback")
        except Exception as e:
            print(f"⚠️ MLX loading failed: {e}, trying transformers fallback")
        
        # Strategy 2: Fallback to transformers (參考成功的 run_phi3_vision.py)
        try:
            from transformers import AutoProcessor, AutoModelForVision2Seq
            
            print("🔄 Falling back to transformers implementation")
            
            # Use standard microsoft model as fallback
            fallback_model = "microsoft/Phi-3.5-vision-instruct"
            
            self.processor = AutoProcessor.from_pretrained(
                fallback_model, 
                trust_remote_code=True
            )
            
            self.model = AutoModelForVision2Seq.from_pretrained(
                fallback_model,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto",
                trust_remote_code=True
            )
            
            self.use_mlx = False
            self.loaded = True
            print("✅ Transformers Phi-3.5-Vision model loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ All loading strategies failed: {e}")
            return False

    def predict(self, image: Any, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimized prediction with MLX and transformers support"""
        if not self.loaded:
            return {"success": False, "error": "Model not loaded", "response": {"text": "Model not available"}}
        
        try:
            max_tokens = options.get("max_tokens", 100) if options else 100
            
            if self.use_mlx:
                return self._predict_mlx(image, prompt, max_tokens)
            else:
                return self._predict_transformers(image, prompt, max_tokens)
                
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return {"success": False, "error": str(e), "response": {"text": f"Error: {str(e)}"}}

    def _predict_mlx(self, image: Image.Image, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """MLX prediction implementation (參考 run_phi3_vision.py 的成功實現)"""
        try:
            from mlx_vlm import generate
            
            # Save image to temp file for MLX
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            try:
                # Ensure RGB format
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(temp_path, 'JPEG', quality=95)
                
                # Format prompt for Phi-3 Vision (參考成功的格式)
                mlx_prompt = f"<|image_1|>\nUser: {prompt}\nAssistant:"
                
                # Generate with MLX
                response = generate(
                    model=self.model,
                    processor=self.processor,
                    image=temp_path,
                    prompt=mlx_prompt,
                    max_tokens=max_tokens,
                    temp=0.7
                )
                
                # Process response (參考 run_phi3_vision.py 的成功處理)
                if isinstance(response, tuple):
                    text_response = response[0]
                else:
                    text_response = str(response)
                
                # Clean response text
                text_response = text_response.replace("<|end|>", "").replace("<|endoftext|>", "").strip()
                
                return {
                    "success": True,
                    "response": {"text": text_response}
                }
                
            finally:
                # Cleanup temp file
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ MLX inference error: {e}")
            return {"success": False, "error": str(e), "response": {"text": f"MLX error: {str(e)}"}}

    def _predict_transformers(self, image: Image.Image, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Transformers prediction implementation (參考成功的 run_phi3_vision.py)"""
        try:
            # Format messages for Phi-3 Vision
            messages = [{"role": "user", "content": f"<|image_1|>\n{prompt}"}]
            
            # Apply chat template
            prompt_text = self.processor.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Process inputs
            inputs = self.processor(prompt_text, [image], return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=False,
                    temperature=0.7,
                    top_p=0.9
                )
            
            # Decode response
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up the response text
            if "Assistant:" in response:
                response = response.split("Assistant:")[-1].strip()
            
            return {
                "success": True,
                "response": {"text": response}
            }
            
        except Exception as e:
            print(f"❌ Transformers inference error: {e}")
            return {"success": False, "error": str(e), "response": {"text": f"Transformers error: {str(e)}"}}

    def preprocess_image(self, image: Any) -> Any:
        """Preprocess image for optimized Phi-3 Vision model"""
        if isinstance(image, Image.Image):
            # Ensure RGB format
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (optimization)
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def format_response(self, raw_response: Any) -> Dict[str, Any]:
        """Format response for API compatibility"""
        return {"response": raw_response} if not isinstance(raw_response, dict) else raw_response

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
            
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Clear MPS cache if available
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            
            return True
        except Exception as e:
            print(f"Error unloading model: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "model_id": self.model_id,
            "loaded": self.loaded,
            "framework": "MLX-VLM" if self.use_mlx else "Transformers",
            "device": "Apple Silicon (M1/M2/M3)" if self.use_mlx else "Auto",
            "optimization": "INT4 Quantization" if self.use_mlx else "Standard",
            "stats": self.stats
        }

if __name__ == '__main__':
    print("This script is not meant to be run directly. Use a runner script.")