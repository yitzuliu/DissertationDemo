"""
Moondream2 Optimized Model Implementation

Optimized version of Moondream2 with performance improvements:
- MPS acceleration for Apple Silicon
- Optimized memory management
- Image caching
- Special API handling for Moondream2's unique interface
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
import hashlib

logger = logging.getLogger(__name__)

# Add parent directories to path for imports
import sys
import os

# Get current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Method 1: Try direct relative import to base_model.py
BaseVisionModel = None

try:
    # Add the models directory to path
    models_dir = os.path.dirname(current_dir)  # src/models/
    if models_dir not in sys.path:
        sys.path.insert(0, models_dir)
    
    from base_model import BaseVisionModel as ImportedBaseVisionModel
    BaseVisionModel = ImportedBaseVisionModel
    print("✅ Successfully imported BaseVisionModel")
    
except ImportError:
    # Method 2: Try adding project root to path
    try:
        # Go up to project root: src/models/moondream2 -> src/models -> src -> project_root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from src.models.base_model import BaseVisionModel as ImportedBaseVisionModel
        BaseVisionModel = ImportedBaseVisionModel
        print("✅ Successfully imported BaseVisionModel via project root")
        
    except ImportError:
        # Method 3: Create a minimal BaseVisionModel replacement if all else fails
        print("⚠️ Could not import BaseVisionModel, creating minimal replacement")
        
        class BaseVisionModel:
            """Minimal BaseVisionModel replacement for standalone operation"""
            
            def __init__(self, model_name: str, config: dict):
                self.model_name = model_name
                self.config = config
                self.loaded = False
            
            def load_model(self) -> bool:
                """Override in subclass"""
                return False
            
            def predict(self, image, prompt: str, options=None) -> dict:
                """Override in subclass"""
                return {"error": "Not implemented", "success": False}
            
            def unload_model(self) -> bool:
                """Override in subclass"""
                return True
            
            def get_model_info(self) -> dict:
                """Override in subclass"""
                return {
                    "name": self.model_name,
                    "loaded": self.loaded,
                    "config": self.config
                }

# Skip image processing import for now - not essential for basic functionality
# from src.backend.utils.image_processing import preprocess_for_model

class OptimizedMemoryManager:
    """
    Lightweight memory manager for Moondream2
    """
    
    def __init__(self):
        self.last_cleanup = 0
        self.cleanup_interval = 8  # Cleanup every 8 inferences for Moondream2
        self.inference_count = 0
    
    def smart_cleanup(self, force=False):
        """Intelligent memory cleanup"""
        self.inference_count += 1
        
        if force or (self.inference_count % self.cleanup_interval == 0):
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            elif torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            self.last_cleanup = time.time()
    
    def quick_check(self) -> bool:
        """Quick memory check"""
        try:
            if torch.backends.mps.is_available():
                test_tensor = torch.zeros(100, 100, device='mps')
                del test_tensor
                return True
            elif torch.cuda.is_available():
                test_tensor = torch.zeros(100, 100, device='cuda')
                del test_tensor
                return True
        except Exception:
            self.smart_cleanup(force=True)
            return False
        return True

class ImageCache:
    """
    Image preprocessing cache for Moondream2
    """
    
    def __init__(self, max_size=8):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get_cache_key(self, image: Image.Image) -> str:
        """Generate cache key from image"""
        pixels = list(image.getdata())[:8]  # First 8 pixels
        key_data = f"{image.size}_{pixels}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, image: Image.Image):
        """Get cached processed image"""
        key = self.get_cache_key(image)
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, image: Image.Image, processed_image: Image.Image):
        """Cache processed image"""
        key = self.get_cache_key(image)
        
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = processed_image
        if key not in self.access_order:
            self.access_order.append(key)

class OptimizedMoondream2Server:
    """
    High-performance Moondream2 server with optimizations
    """
    
    def __init__(self, model_id: str = "vikhyatk/moondream2", device: str = "auto"):
        self.model_id = model_id
        self.device = self._get_optimal_device(device)
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.memory_manager = OptimizedMemoryManager()
        self.image_cache = ImageCache()
        
        # Response cache for identical requests
        self.response_cache = {}
        self.cache_lock = threading.Lock()
        
    def _get_optimal_device(self, device: str) -> str:
        """Determine optimal device for Moondream2"""
        if device == "auto":
            if torch.backends.mps.is_available():
                return "mps"
            elif torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        return device
    
    def start(self) -> bool:
        """Load Moondream2 model with optimizations"""
        if self.loaded:
            logger.info("Moondream2 model already loaded")
            return True
            
        logger.info(f"Loading OPTIMIZED Moondream2 model: {self.model_id}")
        
        try:
            start_time = time.time()
            
            # Quick memory check
            if not self.memory_manager.quick_check():
                logger.error("Memory check failed")
                return False
            
            # Load model with trust_remote_code (required for Moondream2)
            logger.info("Loading Moondream2 model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id, 
                trust_remote_code=True
            )
            
            # Load tokenizer
            logger.info("Loading Moondream2 tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            
            # Move model to appropriate device
            if self.device != "cpu":
                logger.info(f"Moving model to {self.device}...")
                self.model = self.model.to(self.device)
            
            # Set model to evaluation mode
            self.model.eval()
            
            total_time = time.time() - start_time
            logger.info(f"OPTIMIZED Moondream2 loaded in {total_time:.2f}s")
            logger.info(f"Device: {self.device}")
            
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading optimized Moondream2: {e}")
            return False
    
    def _initialize_if_needed(self):
        """Lazy initialization of model and tokenizer"""
        if not self.loaded:
            self.start()
    
    def generate_response_fast(self, image: Image.Image, prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Optimized response generation for Moondream2"""
        try:
            self._initialize_if_needed()
            
            if not self.loaded:
                return {"error": "Model not loaded"}
            
            start_time = time.time()
            
            # Generate cache key
            image_hash = self.image_cache.get_cache_key(image)
            cache_key = f"{image_hash}_{prompt}_{max_tokens}"
            
            # Check cache first
            with self.cache_lock:
                if cache_key in self.response_cache:
                    cached_result = self.response_cache[cache_key]
                    cached_result["cache_hit"] = True
                    cached_result["processing_time"] = 0.001  # Almost instant
                    return cached_result
            
            # Preprocess image (with caching)
            processed_image = self.image_cache.get(image)
            if processed_image is None:
                processed_image = self._preprocess_image_fast(image)
                self.image_cache.put(image, processed_image)
            
            # Moondream2 specific inference using its special API
            if self.model is None:
                raise RuntimeError("Model not loaded")
                
            device = next(self.model.parameters()).device
            
            # Encode image using Moondream2's encode_image method
            enc_image = self.model.encode_image(processed_image)
            if hasattr(enc_image, 'to'):
                enc_image = enc_image.to(device)
            
            # Use Moondream2's answer_question method
            # Note: max_tokens cannot be controlled in Moondream2 API
            response = self.model.answer_question(enc_image, prompt, self.tokenizer)
            
            processing_time = time.time() - start_time
            
            result = {
                "response": {
                    "text": response,
                    "processing_time": processing_time
                },
                "success": True,
                "cache_hit": False,
                "processing_time": processing_time,
                "model": "Moondream2-Optimized"
            }
            
            # Cache result
            with self.cache_lock:
                if len(self.response_cache) < 20:  # Limit cache size
                    self.response_cache[cache_key] = result.copy()
            
            # Smart memory cleanup
            self.memory_manager.smart_cleanup()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Moondream2 inference: {e}")
            return {
                "error": str(e),
                "success": False,
                "processing_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    def _preprocess_image_fast(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """Fast image preprocessing optimized for Moondream2"""
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Moondream2 optimal size
            target_size = (384, 384)
            
            # Resize efficiently
            if image.size != target_size:
                image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            raise
    
    def stop(self):
        """Stop and cleanup the model"""
        try:
            self.model = None
            self.tokenizer = None
            self.loaded = False
            self.memory_manager.smart_cleanup(force=True)
            logger.info("Moondream2 server stopped and cleaned up")
        except Exception as e:
            logger.error(f"Error stopping Moondream2 server: {e}")

class OptimizedMoondream2Model(BaseVisionModel):
    """
    Optimized Moondream2 model implementing BaseVisionModel interface
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        self.model_id = config.get("huggingface_model_id", "vikhyatk/moondream2")
        self.device = config.get("device", "auto")
        self.server = None
        
        # Performance tracking
        self.total_inference_time = 0
        self.total_inferences = 0
        
    def load_model(self) -> bool:
        """Load Moondream2 model"""
        try:
            start_time = time.time()
            
            self.server = OptimizedMoondream2Server(
                model_id=self.model_id,
                device=self.device
            )
            
            if self.server.start():
                self.loaded = True
                self.load_time = time.time() - start_time
                self.device = self.server.device
                logger.info(f"Moondream2 model {self.model_name} loaded in {self.load_time:.2f}s")
                return True
            else:
                logger.error(f"Failed to load Moondream2 model {self.model_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading Moondream2 model {self.model_name}: {str(e)}")
            return False
    
    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """Preprocess image for Moondream2"""
        if self.server:
            return self.server._preprocess_image_fast(image)
        else:
            # Fallback preprocessing
            if isinstance(image, np.ndarray):
                return Image.fromarray(image)
            return image
    
    def format_response(self, raw_response: str) -> Dict[str, Any]:
        """Format Moondream2 response"""
        return {
            "text": raw_response,
            "model": self.model_name,
            "type": "text_response"
        }
    
    def _update_stats(self, processing_time: float):
        """Update performance statistics"""
        self.total_inferences += 1
        self.total_inference_time += processing_time
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and statistics"""
        avg_time = self.total_inference_time / max(self.total_inferences, 1)
        
        return {
            "name": self.model_name,
            "loaded": self.loaded,
            "model_id": self.model_id,
            "device": self.device,
            "load_time": getattr(self, 'load_time', 0),
            "total_inferences": self.total_inferences,
            "total_inference_time": self.total_inference_time,
            "avg_inference_time": avg_time,
            "optimized": True
        }
    
    def predict(self, 
                image: Union[Image.Image, np.ndarray], 
                prompt: str, 
                options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate prediction using Moondream2"""
        try:
            if not self.loaded or not self.server:
                return {
                    "error": "Model not loaded",
                    "success": False,
                    "response": {"text": "Model not available"}
                }
            
            # Get options
            if options is None:
                options = {}
            
            max_tokens = options.get("max_tokens", 100)
            
            # Preprocess image to ensure it's PIL Image
            if isinstance(image, np.ndarray):
                processed_image = Image.fromarray(image)
            else:
                processed_image = image
            
            # Generate response
            result = self.server.generate_response_fast(
                image=processed_image,
                prompt=prompt,
                max_tokens=max_tokens
            )
            
            # Update statistics
            if result.get("success") and "processing_time" in result:
                self._update_stats(result["processing_time"])
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Moondream2 prediction: {e}")
            return {
                "error": str(e),
                "success": False,
                "response": {"text": f"Error: {str(e)}"}
            }
    
    def unload_model(self) -> bool:
        """Unload Moondream2 model"""
        try:
            if self.server:
                self.server.stop()
                self.server = None
            
            self.loaded = False
            logger.info(f"Moondream2 model {self.model_name} unloaded")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading Moondream2 model: {e}")
            return False 