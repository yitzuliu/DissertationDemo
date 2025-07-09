"""
Moondream2 Model Implementation

This module implements the BaseVisionModel interface for the Moondream2 model.
Standard version without optimizations for maximum compatibility.
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
from transformers import AutoModelForCausalLM, AutoTokenizer
import threading
import gc
from pathlib import Path

# Add parent directories to path for imports
import sys
import os
# Add the project root to the path (go up 3 levels: file -> moondream2 -> models -> src -> root)
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
    def preprocess_for_model(image, model_type="moondream2", config=None, return_format="pil"):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image

logger = logging.getLogger(__name__)

class Moondream2MemoryManager:
    """
    Memory management utilities for Moondream2
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
    def check_memory_availability(required_gb=2.0):
        """Check if enough memory is available for operation"""
        try:
            if torch.backends.mps.is_available():
                current_memory = torch.mps.current_allocated_memory() / 1024**3
                max_memory = 18.0  # Typical M1/M2 unified memory
                available = max_memory - current_memory
                
                if available < required_gb:
                    logger.warning(f"Low memory: {available:.2f} GB available, {required_gb:.2f} GB required")
                    Moondream2MemoryManager.cleanup_memory(aggressive=True)
                    return False
                else:
                    logger.debug(f"Memory OK: {available:.2f} GB available")
                    return True
            return True  # Assume OK if MPS not available
                
        except Exception as e:
            logger.warning(f"Memory check failed: {e}")
            return True  # Assume OK if can't check

class Moondream2Server:
    """
    Manages the Moondream2 model in-process (standard version)
    """
    
    def __init__(self, model_path: str, device: str = "mps"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.memory_manager = Moondream2MemoryManager()
        
    def start(self) -> bool:
        """Load Moondream2 model into memory"""
        if self.loaded:
            logger.info("Moondream2 model already loaded")
            return True
            
        logger.info(f"Loading Moondream2 model from: {self.model_path}")
        
        try:
            start_time = time.time()
            
            # Check memory before loading
            if not self.memory_manager.check_memory_availability(required_gb=4.0):
                logger.error("Insufficient memory for Moondream2 model")
                return False
            
            # Load tokenizer
            tokenizer_start = time.time()
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            tokenizer_time = time.time() - tokenizer_start
            
            # Load model
            model_start = time.time()
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float32,  # Standard precision
                device_map=None,
                trust_remote_code=True
            )
            self.model = self.model.to(self.device)
            model_time = time.time() - model_start
            
            total_time = time.time() - start_time
            
            logger.info(f"Tokenizer loaded: {tokenizer_time:.2f}s")
            logger.info(f"Model loaded: {model_time:.2f}s")
            logger.info(f"Total loading time: {total_time:.2f}s")
            logger.info(f"Device: {self.device}")
            
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading Moondream2 model: {e}")
            self.loaded = False
            return False
    
    def stop(self) -> bool:
        """Unload model from memory"""
        if not self.loaded:
            return True
            
        logger.info("Unloading Moondream2 model...")
        try:
            if hasattr(self, 'model') and self.model is not None:
                del self.model
                self.model = None
            if hasattr(self, 'tokenizer') and self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
            
            self.memory_manager.cleanup_memory(aggressive=True)
            self.loaded = False
            logger.info("Moondream2 model unloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading Moondream2 model: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if model is loaded and ready"""
        return self.loaded and self.model is not None and self.tokenizer is not None
    
    def generate_response(self, image: Image.Image, prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate response from Moondream2 model using its specific API"""
        if not self.is_running():
            return {"error": "Model not loaded"}
        
        try:
            # Pre-check memory availability
            if not self.memory_manager.check_memory_availability(required_gb=2.0):
                return {"error": "Insufficient memory for inference"}
            
            start_time = time.time()
            
            # Moondream2 specific API: encode_image + answer_question
            # First encode the image
            image_embeds = self.model.encode_image(image)
            
            # Then answer the question
            response = self.model.answer_question(
                image_embeds, 
                prompt, 
                self.tokenizer,
                max_new_tokens=max_tokens
            )
            
            inference_time = time.time() - start_time
            
            # Memory cleanup
            del image_embeds
            self.memory_manager.cleanup_memory()
            
            return {
                "success": True,
                "response": response,
                "inference_time": inference_time
            }
            
        except Exception as e:
            logger.error(f"Error during Moondream2 inference: {e}")
            # Cleanup on error
            self.memory_manager.cleanup_memory(aggressive=True)
            return {"error": f"Inference failed: {str(e)}"}


class Moondream2Model(BaseVisionModel):
    """
    Standard implementation of the Moondream2 model.
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the Moondream2 model.
        
        Args:
            model_name: The name of the model
            config: A dictionary containing model configuration
        """
        super().__init__(model_name, config)
        
        # Get model path from config, with proper path resolution
        model_path = config.get("model_path", "vikhyatk/moondream2")
        if not os.path.isabs(model_path):
            # If it's a Hugging Face model ID, use it directly
            if "/" in model_path and not model_path.startswith("../"):
                self.model_path = model_path
            else:
                # Get project root and resolve relative path
                project_root = Path(__file__).resolve().parent.parent.parent.parent
                self.model_path = str(project_root / model_path)
        else:
            self.model_path = model_path
            
        self.device = config.get("device", "mps")
        self.timeout = config.get("timeout", 60)
        self.max_tokens = config.get("max_tokens", 100)
        
        logger.info(f"🔧 Model path resolved to: {self.model_path}")
        
        # Create server
        self.server = Moondream2Server(self.model_path, self.device)
    
    def load_model(self) -> bool:
        """
        Load the Moondream2 model.
        
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            start_time = time.time()
            
            logger.info(f"Loading Moondream2 model: {self.model_name}")
            if not self.server.start():
                logger.error("Failed to start Moondream2 server")
                return False
                
            self.loaded = True
            self.load_time = time.time() - start_time
            
            logger.info(f"Moondream2 model {self.model_name} ready")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Moondream2 model: {str(e)}")
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
                model_type="moondream2",
                config=self.config,
                return_format="pil"
            )
            
            # Apply Moondream2-specific preprocessing
            image_config = self.config.get("image_processing", {})
            size = image_config.get("size", [384, 384])
            max_size = max(size) if isinstance(size, list) else size
            
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
            logger.error(f"Error preprocessing image for Moondream2: {str(e)}")
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