"""
Phi-3.5-Vision Model Implementation

This module implements the BaseVisionModel interface for the Phi-3.5-Vision model.
Standard version using transformers for maximum compatibility.
"""

import time
import json
import base64
import numpy as np
from typing import Dict, Any, Optional, Union, List
from PIL import Image
import logging
import io
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
import threading
import gc
from pathlib import Path

# Add parent directories to path for imports
import sys
import os
# Add the project root to the path (go up 4 levels: file -> Phi_3.5_Vision MLX -> models -> src -> root)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

# Import with fallback strategy
try:
    from src.models.base_model import BaseVisionModel
except ImportError:
    try:
        from models.base_model import BaseVisionModel
    except ImportError:
        # Minimal replacement if imports fail
        class BaseVisionModel:
            def __init__(self, model_name: str, config: Dict[str, Any]):
                self.model_name = model_name
                self.config = config
                self.loaded = False
                self.load_time = 0
                self.stats = {"requests": 0, "total_time": 0.0}
            
            def _update_stats(self, processing_time: float):
                self.stats["requests"] += 1
                self.stats["total_time"] += processing_time

try:
    from src.backend.utils.image_processing import preprocess_for_model
except ImportError:
    # Fallback image preprocessing
    def preprocess_for_model(image, model_type="phi3_vision", config=None, return_format="pil"):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image

logger = logging.getLogger(__name__)

class Phi3VisionMemoryManager:
    """
    Memory management utilities for Phi-3.5-Vision
    """
    
    @staticmethod
    def cleanup_memory(aggressive=False):
        """Clean up memory with optional aggressive mode"""
        try:
            if aggressive:
                gc.collect()  # Force Python garbage collection
                logger.debug("Python garbage collected")
            
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
                logger.debug("MPS cache cleared")
            elif torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.debug("CUDA cache cleared")
                
        except Exception as e:
            logger.warning(f"Memory cleanup warning: {e}")
    
    @staticmethod
    def check_memory_availability(required_gb=8.0):
        """Check if enough memory is available for operation"""
        try:
            if torch.backends.mps.is_available():
                current_memory = torch.mps.current_allocated_memory() / 1024**3
                max_memory = 18.0  # Typical M1/M2 unified memory
                available = max_memory - current_memory
                
                if available < required_gb:
                    logger.warning(f"Low memory: {available:.2f} GB available, {required_gb:.2f} GB required")
                    Phi3VisionMemoryManager.cleanup_memory(aggressive=True)
                    return False
                else:
                    logger.debug(f"Memory OK: {available:.2f} GB available")
                    return True
            return True  # Assume OK if MPS not available
                
        except Exception as e:
            logger.warning(f"Memory check failed: {e}")
            return True  # Assume OK if can't check

class Phi3VisionServer:
    """
    Manages the Phi-3.5-Vision model in-process (standard version)
    """
    
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.processor = None
        self.loaded = False
        self.memory_manager = Phi3VisionMemoryManager()
        
    def start(self) -> bool:
        """Load Phi-3.5-Vision model into memory"""
        if self.loaded:
            logger.info("Phi-3.5-Vision model already loaded")
            return True
            
        logger.info(f"Loading Phi-3.5-Vision model from: {self.model_path}")
        
        try:
            start_time = time.time()
            
            # Check memory before loading
            if not self.memory_manager.check_memory_availability(required_gb=8.0):
                logger.error("Insufficient memory for Phi-3.5-Vision model")
                return False
            
            # Load processor
            processor_start = time.time()
            self.processor = AutoProcessor.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            processor_time = time.time() - processor_start
            
            # Load model with CPU-optimized settings for compatibility
            model_start = time.time()
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,  # Use float16 to save memory
                device_map="cpu",  # Force CPU for maximum compatibility
                trust_remote_code=True,
                _attn_implementation="eager",  # Disable FlashAttention2 for compatibility
                low_cpu_mem_usage=True  # Use less CPU memory
            )
            model_time = time.time() - model_start
            
            total_time = time.time() - start_time
            
            logger.info(f"Processor loaded: {processor_time:.2f}s")
            logger.info(f"Model loaded: {model_time:.2f}s")
            logger.info(f"Total loading time: {total_time:.2f}s")
            logger.info(f"Device: {self.device}")
            logger.info("⚠️ Using CPU for maximum compatibility (may be slower)")
            
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading Phi-3.5-Vision model: {e}")
            self.loaded = False
            return False
    
    def stop(self) -> bool:
        """Unload model from memory"""
        if not self.loaded:
            return True
            
        logger.info("Unloading Phi-3.5-Vision model...")
        try:
            if hasattr(self, 'model') and self.model is not None:
                del self.model
                self.model = None
            if hasattr(self, 'processor') and self.processor is not None:
                del self.processor
                self.processor = None
            
            self.memory_manager.cleanup_memory(aggressive=True)
            self.loaded = False
            logger.info("Phi-3.5-Vision model unloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading Phi-3.5-Vision model: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if model is loaded and ready"""
        return self.loaded and self.model is not None and self.processor is not None
    
    def generate_response(self, image: Image.Image, prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate response from Phi-3.5-Vision model using MLX-VLM"""
        if not self.is_running():
            return {"error": "Model not loaded"}
        
        try:
            # Pre-check memory availability
            if not self.memory_manager.check_memory_availability(required_gb=4.0):
                return {"error": "Insufficient memory for inference"}
            
            start_time = time.time()
            
            # Try MLX-VLM inference first (same as vlm_tester.py)
            try:
                from mlx_vlm import generate
                logger.debug("🚀 Using MLX-VLM inference for Phi-3.5-Vision-Instruct...")
                
                # Save image to temporary file for MLX-VLM
                temp_image_path = "temp_mlx_image.jpg"
                image.save(temp_image_path)
                
                try:
                    # Use simple prompt format for MLX-VLM
                    mlx_prompt = f"<|image_1|>\nUser: {prompt}\nAssistant:"
                    
                    # Check if model and processor are loaded
                    if self.model is None or self.processor is None:
                        raise ValueError("Model or processor not loaded")
                    
                    response = generate(
                        model=self.model, 
                        processor=self.processor, 
                        prompt=mlx_prompt,
                        image=temp_image_path,
                        max_tokens=max_tokens,
                        temp=0.0,  # Use 0.0 for deterministic output
                        verbose=False
                    )
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
                
                # MLX-VLM returns string directly, not tuple
                text_response = str(response)
                
                # Clean up response
                text_response = text_response.replace("<|end|><|endoftext|>", " ").replace("<|end|>", " ").replace("<|endoftext|>", " ")
                if "1. What is meant by" in text_response:
                    text_response = text_response.split("1. What is meant by")[0].strip()
                text_response = ' '.join(text_response.split())
                
                inference_time = time.time() - start_time
                
                return {
                    "success": True,
                    "response": text_response,
                    "inference_time": inference_time,
                    "method": "MLX-VLM"
                }
                
            except (ImportError, AttributeError, TypeError, Exception) as e:
                logger.warning(f"MLX-VLM inference failed ({e}), loading transformers model...")
                
                # Load transformers model for fallback (MLX model can't be used with transformers)
                from transformers import AutoModelForCausalLM, AutoProcessor
                logger.debug("📥 Loading transformers Phi-3.5-Vision for fallback...")
                
                fallback_model = AutoModelForCausalLM.from_pretrained(
                    "microsoft/Phi-3.5-vision-instruct", 
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    _attn_implementation="eager",  # Disable FlashAttention2
                    device_map="cpu",  # Force CPU to avoid memory issues
                    low_cpu_mem_usage=True  # Use less CPU memory
                )
                fallback_processor = AutoProcessor.from_pretrained(
                    "microsoft/Phi-3.5-vision-instruct", 
                    trust_remote_code=True,
                    num_crops=4  # For single-frame images
                )
                
                # Phi-3.5 Vision special format (model compatibility requirement)
            messages = [
                    {"role": "user", "content": f"<|image_1|>\\n{prompt}"}
            ]
            
                prompt_text = fallback_processor.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
                inputs = fallback_processor(prompt_text, [image], return_tensors="pt")
            
                # Move to correct device
                device = next(fallback_model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
                # Technical fix: avoid DynamicCache error
            with torch.no_grad():
                    outputs = fallback_model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=False,
                    use_cache=False,  # Disable cache to avoid DynamicCache error
                        pad_token_id=fallback_processor.tokenizer.eos_token_id
                )
            
                result = fallback_processor.decode(outputs[0], skip_special_tokens=True)
                
                # Clean up fallback model
                del fallback_model, fallback_processor
                gc.collect()
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()
            
            inference_time = time.time() - start_time
            
            return {
                "success": True,
                    "response": result,
                    "inference_time": inference_time,
                    "method": "Transformers-Fallback"
            }
            
        except Exception as e:
            logger.error(f"Error during Phi-3.5-Vision inference: {e}")
            # Cleanup on error
            self.memory_manager.cleanup_memory(aggressive=True)
            return {"error": f"Inference failed: {str(e)}"}


class Phi3VisionModel(BaseVisionModel):
    """
    Standard implementation of the Phi-3.5-Vision model using transformers.
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the Phi-3.5-Vision model.
        
        Args:
            model_name: The name of the model
            config: A dictionary containing model configuration
        """
        super().__init__(model_name, config)
        
        # Get model path from config
        self.model_path = config.get("model_path", "mlx-community/Phi-3.5-vision-instruct-4bit")
        self.device = config.get("device", "auto")  # Default to auto for MLX optimization
        self.timeout = config.get("timeout", 180)  # Longer timeout for MLX inference
        self.max_tokens = config.get("max_tokens", 100)
        
        logger.info(f"🔧 Model path: {self.model_path}")
        logger.info(f"🔧 Device: {self.device} (MLX-optimized version)")
        
        # Create server
        self.server = Phi3VisionServer(self.model_path, self.device)
    
    def load_model(self) -> bool:
        """
        Load the Phi-3.5-Vision model.
        
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            start_time = time.time()
            
            logger.info(f"Loading Phi-3.5-Vision model: {self.model_name}")
            if not self.server.start():
                logger.error("Failed to start Phi-3.5-Vision server")
                return False
                
            self.loaded = True
            self.load_time = time.time() - start_time
            
            logger.info(f"Phi-3.5-Vision model {self.model_name} ready")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Phi-3.5-Vision model: {str(e)}")
            self.loaded = False
            return False
    
    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """
        Preprocess the input image for the model.
        
        Args:
            image: The input image, either as PIL Image or numpy array
            
        Returns:
            PIL Image ready for the model
        """
        try:
            # Process the image to get a PIL image
            pil_image = preprocess_for_model(
                image=image,
                model_type="phi3_vision",
                config=self.config,
                return_format="pil"
            )
            
            # Apply Phi-3.5-Vision-specific preprocessing
            image_config = self.config.get("image_processing", {})
            max_size = image_config.get("max_size", 1024)
            
            if max(pil_image.size) > max_size:
                scale = max_size / max(pil_image.size)
                new_size = (int(pil_image.size[0] * scale), int(pil_image.size[1] * scale))
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                logger.debug(f"Resized image to {new_size}")
            
            # Ensure RGB
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            return pil_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image for Phi-3.5-Vision: {str(e)}")
            raise e
    
    def predict(self, 
                image: Union[Image.Image, np.ndarray], 
                prompt: str, 
                options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a prediction from the model.
        
        Args:
            image: The input image
            prompt: The text prompt to guide the model
            options: Additional model-specific options
            
        Returns:
            A dictionary containing the model's response
        """
        if not self.loaded:
            if not self.load_model():
                return {"error": "Model is not available"}
        
        try:
            start_time = time.time()
            
            # Apply default options if not provided
            if options is None:
                options = {}
                
            # Get generation parameters
            max_tokens = options.get("max_tokens", self.max_tokens)
            
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Generate response using the server
            result = self.server.generate_response(processed_image, prompt, max_tokens)
            
            if "error" in result:
                return result
            
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            # Format the response in standard format
            formatted_result = self.format_response(result["response"])
            formatted_result["processing_time"] = processing_time
            formatted_result["inference_time"] = result.get("inference_time", 0)
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error during prediction with {self.model_name}: {str(e)}")
            return {
                "error": f"Failed to analyze image with {self.model_name}",
                "details": str(e)
            }
    
    def format_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Format the raw model response into a standardized format.
        
        Args:
            raw_response: The raw text output from the model
            
        Returns:
            A standardized response dictionary
        """
        try:
            # Clean up response
            clean_text = raw_response.strip()
            
            # Try to parse as JSON if it looks like JSON
            if clean_text.startswith('{') and clean_text.endswith('}'):
                try:
                    parsed_json = json.loads(clean_text)
                    return {
                        "success": True,
                        "response": parsed_json,
                        "raw_response": raw_response
                    }
                except json.JSONDecodeError:
                    pass
            
            # Return as text response
            return {
                "success": True,
                "response": {
                    "text": clean_text
                },
                "raw_response": raw_response
            }
                
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return {
                "success": False,
                "error": "Failed to format model response",
                "raw_response": raw_response
            }
    
    def unload_model(self) -> bool:
        """
        Unload the model from memory to free resources.
        
        Returns:
            True if unloading was successful, False otherwise
        """
        try:
            if self.server:
                self.server.stop()
                
            self.loaded = False
            logger.info(f"Model {self.model_name} unloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error unloading model {self.model_name}: {str(e)}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "device": self.device,
            "loaded": self.loaded,
            "load_time": getattr(self, 'load_time', 0),
            "stats": getattr(self, 'stats', {}),
            "version": "standard"
        } 