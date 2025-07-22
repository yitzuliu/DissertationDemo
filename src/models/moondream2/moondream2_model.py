"""
Moondream2 Model Implementation

This module implements the BaseVisionModel interface for the Moondream2 model.
Updated to align with testing framework patterns and performance optimizations.
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
            
            # Moondream2 special API (same as testing framework)
            device = next(self.model.parameters()).device
            enc_image = self.model.encode_image(image)
            if hasattr(enc_image, 'to'):
                enc_image = enc_image.to(device)
            
            # Use unified generation parameters (same as testing framework)
            response = self.model.answer_question(enc_image, prompt, self.tokenizer)
            
            processing_time = time.time() - start_time
            
            return {
                "response": response,
                "processing_time": processing_time,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error during Moondream2 inference: {e}")
            return {
                "error": f"Inference failed: {str(e)}",
                "success": False
            }

class Moondream2Model(BaseVisionModel):
    """
    Moondream2 Model Implementation
    
    Updated to align with testing framework patterns and performance optimizations.
    Best VQA accuracy: 53.0%, Simple accuracy: 60.0%
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name=model_name, config=config)
        self.model_id = self.config.get("model_id", "vikhyatk/moondream2")
        self.device = self.config.get("device", "mps")
        self.server = None
        self.loaded = False
        self.load_time = 0
        self.stats = {"requests": 0, "total_time": 0.0}
        
        # Performance tracking
        self.last_cleanup = time.time()
        self.cleanup_interval = self.config.get("memory", {}).get("cleanup_interval", 10)
        
    def load_model(self) -> bool:
        """Load Moondream2 model"""
        if self.loaded:
            return True
            
        try:
            start_time = time.time()
            
            # Initialize server
            self.server = Moondream2Server(self.model_id, self.device)
            
            # Load model
            success = self.server.start()
            
            if success:
                self.loaded = True
                self.load_time = time.time() - start_time
                logger.info(f"Moondream2 model loaded successfully in {self.load_time:.2f}s")
                return True
            else:
                logger.error("Failed to load Moondream2 model")
                return False
                
        except Exception as e:
            logger.error(f"Error loading Moondream2 model: {e}")
            return False

    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """Preprocess image for Moondream2 model"""
        try:
            # Convert numpy array to PIL if needed
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # Ensure RGB format
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Unified image preprocessing (same as testing framework)
            unified_image_size = 1024
            if max(image.size) > unified_image_size:
                ratio = unified_image_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise RuntimeError(f"Image preprocessing failed: {e}")

    def predict(self, 
                image: Union[Image.Image, np.ndarray], 
                prompt: str, 
                options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Predict method for Moondream2 model"""
        if not self.loaded or self.server is None:
            raise RuntimeError("Model is not loaded")
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Get generation parameters
            max_tokens = 100  # Default
            if options and "max_tokens" in options:
                max_tokens = options["max_tokens"]
            elif self.config.get("api", {}).get("max_tokens"):
                max_tokens = self.config["api"]["max_tokens"]
            
            # Generate response
            start_time = time.time()
            result = self.server.generate_response(processed_image, prompt, max_tokens)
            processing_time = time.time() - start_time
            
            # Update stats
            self._update_stats(processing_time)
            
            # Periodic memory cleanup
            if time.time() - self.last_cleanup > self.cleanup_interval:
                Moondream2MemoryManager.cleanup_memory()
                self.last_cleanup = time.time()
            
            if result.get("success", False):
                return {
                    "response": result["response"],
                    "processing_time": result["processing_time"],
                    "model": self.model_name,
                    "success": True
                }
            else:
                return {
                    "error": result.get("error", "Unknown error"),
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"Error during Moondream2 prediction: {e}")
            return {
                "error": f"Prediction failed: {str(e)}",
                "success": False
            }

    def format_response(self, raw_response: str) -> Dict[str, Any]:
        """Format response for API compatibility"""
        return {
            "response": raw_response,
            "model": self.model_name,
            "framework": "Transformers",
            "device": self.device
        }

    def unload_model(self) -> bool:
        """Unload model and clean up memory"""
        try:
            if self.server is not None:
                success = self.server.stop()
                self.server = None
                self.loaded = False
                return success
            return True
        except Exception as e:
            logger.error(f"Error unloading Moondream2 model: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "model_id": self.model_id,
            "loaded": self.loaded,
            "framework": "Transformers",
            "device": self.device,
            "load_time": self.load_time,
            "stats": self.stats,
            "performance": {
                "vqa_accuracy": "53.0%",
                "simple_accuracy": "60.0%",
                "avg_inference_time": "3.89s"
            }
        }

if __name__ == '__main__':
    print("This script is not meant to be run directly. Use a runner script.") 