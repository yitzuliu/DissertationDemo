"""
Phi-3.5-Vision Optimized Model Implementation

This is an optimized version of Phi-3.5-Vision with MLX framework for Apple Silicon:
- MLX-VLM for Apple Silicon optimization
- INT4 quantization for memory efficiency
- Fallback to transformers if MLX fails
- Image path processing (MLX requirement)
- Significant performance improvements on M1/M2/M3
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
import threading
import gc
from pathlib import Path
import hashlib
import tempfile
import os

# Add parent directories to path for imports
import sys
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
            def __init__(self, model_name: str, config: dict):
                self.model_name = model_name
                self.config = config
                self.loaded = False
                self.load_time = 0
                self.stats = {"requests": 0, "total_time": 0.0}
            
            def load_model(self) -> bool:
                return True
                
            def predict(self, image, prompt: str, options=None) -> dict:
                return {"error": "Base model not available"}
                
            def unload_model(self) -> bool:
                return True
                
            def get_model_info(self) -> dict:
                return {}
            
            def _update_stats(self, processing_time: float):
                self.stats["requests"] = self.stats.get("requests", 0) + 1
                self.stats["total_time"] = self.stats.get("total_time", 0.0) + processing_time

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

class OptimizedMemoryManager:
    """
    Lightweight memory manager for MLX optimization
    """
    
    def __init__(self):
        self.last_cleanup = 0
        self.cleanup_interval = 5  # Cleanup every 5 inferences
        self.inference_count = 0
    
    def smart_cleanup(self, force=False):
        """Intelligent memory cleanup - only when needed"""
        self.inference_count += 1
        
        if force or (self.inference_count % self.cleanup_interval == 0):
            try:
                gc.collect()
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()
                self.last_cleanup = time.time()
            except Exception as e:
                logger.warning(f"Memory cleanup warning: {e}")
    
    def quick_check(self) -> bool:
        """Quick memory check without expensive operations"""
        try:
            # Simple heuristic: if we can allocate a small tensor, we're OK
            if torch.backends.mps.is_available():
                test_tensor = torch.zeros(100, 100, device='mps')
                del test_tensor
                return True
        except Exception:
            self.smart_cleanup(force=True)
            return False
        return True

class ImageCache:
    """
    Simple image preprocessing cache for Phi-3.5-Vision
    """
    
    def __init__(self, max_size=8):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get_cache_key(self, image: Image.Image) -> str:
        """Generate cache key from image"""
        # Use image size and first few pixels as key
        pixels = list(image.getdata())[:10]  # First 10 pixels
        key_data = f"{image.size}_{pixels}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, image: Image.Image):
        """Get cached processed image"""
        key = self.get_cache_key(image)
        if key in self.cache:
            # Move to end (most recent)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, image: Image.Image, processed_image: str):
        """Cache processed image path"""
        key = self.get_cache_key(image)
        
        # Remove oldest if cache full
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            # Clean up old temp file
            old_path = self.cache[oldest_key]
            try:
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception:
                pass
            del self.cache[oldest_key]
        
        self.cache[key] = processed_image
        if key not in self.access_order:
            self.access_order.append(key)

class OptimizedPhi3VisionServer:
    """
    High-performance Phi-3.5-Vision server with MLX optimization
    """
    
    def __init__(self, model_id: str = "lokinfey/Phi-3.5-vision-mlx-int4", device: str = "auto"):
        self.model_id = model_id
        self.device = self._get_optimal_device(device)
        self.model = None
        self.processor = None
        self.loaded = False
        self.memory_manager = OptimizedMemoryManager()
        self.image_cache = ImageCache()
        
        # MLX flags
        self.use_mlx = True
        self.mlx_available = False
        
        # Response cache
        self.response_cache = {}
        self.cache_lock = threading.Lock()
        
    def _get_optimal_device(self, device: str) -> str:
        """Get optimal device for Phi-3.5-Vision"""
        if device == "auto":
            if torch.backends.mps.is_available():
                return "mps"
            elif torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        return device
        
    def start(self) -> bool:
        """Load Phi-3.5-Vision model with MLX optimization"""
        if self.loaded:
            logger.info("Phi-3.5-Vision MLX model already loaded")
            return True
            
        logger.info(f"Loading OPTIMIZED Phi-3.5-Vision MLX model: {self.model_id}")
        
        try:
            start_time = time.time()
            
            # Try MLX-VLM first (primary optimization)
            try:
                import mlx.core as mx
                from mlx_vlm import load, generate
                from mlx_vlm.utils import load_config
                
                logger.info("🚀 Loading MLX-optimized Phi-3.5-Vision model...")
                self.model, self.processor = load(self.model_id, trust_remote_code=True)
                self.mlx_available = True
                self.use_mlx = True
                
                total_time = time.time() - start_time
                logger.info(f"✅ MLX Phi-3.5-Vision loaded in {total_time:.2f}s")
                logger.info(f"🍎 Apple Silicon optimization active")
                
                self.loaded = True
                return True
                
            except ImportError as e:
                logger.warning("MLX-VLM not installed. Installing: pip install mlx-vlm")
                logger.warning("Falling back to transformers approach...")
                self.use_mlx = False
                
            except Exception as e:
                logger.warning(f"MLX loading failed: {e}")
                logger.warning("Falling back to transformers approach...")
                self.use_mlx = False
            
            # Fallback to transformers if MLX fails
            if not self.use_mlx:
                from transformers import AutoModelForCausalLM, AutoProcessor
                
                logger.info("📥 Loading transformers Phi-3.5-Vision (fallback)...")
                
                self.processor = AutoProcessor.from_pretrained(
                    "microsoft/Phi-3.5-vision-instruct", 
                    trust_remote_code=True
                )
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    "microsoft/Phi-3.5-vision-instruct",
                    torch_dtype=torch.float16,
                    device_map="cpu",  # Force CPU for stability
                    trust_remote_code=True,
                    _attn_implementation="eager",
                    low_cpu_mem_usage=True
                )
                
                total_time = time.time() - start_time
                logger.info(f"⚠️ Transformers fallback loaded in {total_time:.2f}s")
                
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading optimized Phi-3.5-Vision: {e}")
            return False
    
    def _initialize_if_needed(self):
        """Lazy initialization of model and processor"""
        if not self.loaded:
            self.start()
    
    def generate_response_fast(self, image: Image.Image, prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Optimized response generation with MLX or fallback"""
        try:
            self._initialize_if_needed()
            
            if not self.loaded:
                return {"error": "Model not loaded"}
            
            start_time = time.time()
            
            # Generate cache key
            cache_key = str(hash(str(prompt) + str(image.size) + str(max_tokens)))
            
            # Check cache
            with self.cache_lock:
                if cache_key in self.response_cache:
                    logger.debug("Using cached response")
                    cached_response = self.response_cache[cache_key]
                    cached_response["from_cache"] = True
                    cached_response["processing_time"] = time.time() - start_time
                    return cached_response
            
            # Primary MLX inference
            if self.use_mlx and self.mlx_available:
                try:
                    from mlx_vlm import generate
                    logger.debug("🚀 Using MLX inference for Phi-3.5-Vision")
                    
                    # MLX requires image paths, save to temp file
                    image_path = self._prepare_image_for_mlx(image)
                    
                    # Simple prompt format for quantized models
                    mlx_prompt = f"<|image_1|>\nUser: {prompt}\nAssistant:"
                    
                    response = generate(
                        model=self.model,
                        processor=self.processor,
                        image=image_path,
                        prompt=mlx_prompt,
                        max_tokens=max_tokens,
                        temp=0.7,
                        repetition_penalty=1.2,
                        top_p=0.9,
                        verbose=False
                    )
                    
                    # Handle MLX response format
                    if isinstance(response, tuple) and len(response) >= 2:
                        text_response = response[0]
                    elif isinstance(response, list) and len(response) > 0:
                        text_response = response[0] if isinstance(response[0], str) else str(response[0])
                    else:
                        text_response = str(response)
                    
                    # Clean up response
                    text_response = text_response.replace("<|end|><|endoftext|>", " ").replace("<|end|>", " ").replace("<|endoftext|>", " ")
                    if "1. What is meant by" in text_response:
                        text_response = text_response.split("1. What is meant by")[0].strip()
                    text_response = ' '.join(text_response.split())
                    
                    # Cleanup temp file
                    try:
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    except Exception:
                        pass
                    
                    inference_time = time.time() - start_time
                    
                    result = {
                        "success": True,
                        "response": text_response,
                        "inference_time": inference_time,
                        "from_cache": False,
                        "method": "MLX"
                    }
                    
                    # Cache the response
                    with self.cache_lock:
                        self.response_cache[cache_key] = result.copy()
                        if len(self.response_cache) > 50:
                            oldest_key = next(iter(self.response_cache))
                            del self.response_cache[oldest_key]
                    
                    return result
                    
                except Exception as e:
                    logger.warning(f"MLX inference failed: {e}, falling back to transformers")
                    self.use_mlx = False
            
            # Fallback transformers inference
            logger.debug("📥 Using transformers inference (fallback)")
            
            # Phi-3.5-Vision special format
            messages = [
                {"role": "user", "content": f"<|image_1|>\n{prompt}"}
            ]
            
            prompt_text = self.processor.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.processor(prompt_text, [image], return_tensors="pt")
            
            # Move to device
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
            
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            inference_time = time.time() - start_time
            
            # Cleanup
            del inputs, outputs
            self.memory_manager.smart_cleanup()
            
            result = {
                "success": True,
                "response": response,
                "inference_time": inference_time,
                "from_cache": False,
                "method": "Transformers"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Optimized inference error: {e}")
            self.memory_manager.smart_cleanup(force=True)
            return {"error": f"Fast inference failed: {str(e)}"}
    
    def _prepare_image_for_mlx(self, image: Image.Image) -> str:
        """Prepare image for MLX (requires file path)"""
        try:
            # Check cache first
            cached_path = self.image_cache.get(image)
            if cached_path and os.path.exists(cached_path):
                return cached_path
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Save image
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(temp_path, 'JPEG', quality=95)
            
            # Cache the path
            self.image_cache.put(image, temp_path)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Image preparation error: {e}")
            raise e
    
    def stop(self):
        """Stop and cleanup"""
        logger.info("Stopping optimized Phi-3.5-Vision server...")
        try:
            if hasattr(self, 'model') and self.model is not None:
                del self.model
                self.model = None
            if hasattr(self, 'processor') and self.processor is not None:
                del self.processor
                self.processor = None
            
            # Cleanup temp files
            for temp_path in self.image_cache.cache.values():
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass
            
            self.memory_manager.smart_cleanup(force=True)
            self.loaded = False
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

class OptimizedPhi3VisionModel(BaseVisionModel):
    """
    High-performance Phi-3.5-Vision implementation with MLX optimization
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        
        # Get model configuration
        self.model_id = config.get("model_path", "lokinfey/Phi-3.5-vision-mlx-int4")
        self.device = config.get("device", "auto")
        self.timeout = config.get("timeout", 60)  # Shorter timeout for optimized
        self.max_tokens = config.get("max_tokens", 100)
        
        logger.info(f"🔧 Model ID: {self.model_id}")
        logger.info(f"🔧 Device: {self.device} (optimized MLX version)")
        
        # Create optimized server
        self.server = OptimizedPhi3VisionServer(self.model_id, self.device)
        
        # Image preprocessing cache
        self.image_cache = ImageCache(max_size=15)
    
    def load_model(self) -> bool:
        """Load optimized model"""
        try:
            start_time = time.time()
            
            logger.info(f"Loading OPTIMIZED Phi-3.5-Vision: {self.model_name}")
            if not self.server.start():
                return False
                
            self.loaded = True
            self.load_time = time.time() - start_time
            
            logger.info(f"OPTIMIZED Phi-3.5-Vision ready in {self.load_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Optimized model loading error: {e}")
            return False
    
    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """Required by BaseVisionModel - redirects to optimized version"""
        return self.preprocess_image_fast(image)

    def format_response(self, raw_response: str) -> Dict[str, Any]:
        """Required by BaseVisionModel - formats the raw model response"""
        try:
            clean_text = raw_response.strip()
            
            # Try to parse as JSON
            try:
                parsed_json = json.loads(clean_text)
                return {
                    "success": True,
                    "response": parsed_json,
                    "raw_response": raw_response
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "response": {
                        "text": clean_text
                    },
                    "raw_response": raw_response
                }
                
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return {
                "success": False,
                "error": "Failed to format model response",
                "raw_response": raw_response
            }
    
    def _update_stats(self, processing_time: float):
        """Update performance statistics"""
        if not hasattr(self, 'stats'):
            self.stats = {"requests": 0, "total_time": 0.0}
        self.stats["requests"] += 1
        self.stats["total_time"] += processing_time
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "model_id": self.model_id,
            "device": self.device,
            "loaded": self.loaded,
            "load_time": getattr(self, 'load_time', 0),
            "stats": getattr(self, 'stats', {}),
            "version": "optimized_mlx",
            "mlx_available": getattr(self.server, 'mlx_available', False),
            "use_mlx": getattr(self.server, 'use_mlx', False)
        }
    
    def preprocess_image_fast(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """Fast image preprocessing with caching"""
        try:
            # Convert to PIL if needed
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # Check cache first
            cached = self.image_cache.get(image)
            if cached is not None:
                logger.debug("Using cached preprocessed image")
                return cached
            
            # Get size from config
            image_config = self.config.get("image_processing", {})
            max_size = image_config.get("max_size", 1024)
            
            if max(image.size) > max_size:
                scale = max_size / max(image.size)
                new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
                processed = image.resize(new_size, Image.Resampling.BILINEAR)
            else:
                processed = image
            
            # Ensure RGB
            if processed.mode != 'RGB':
                processed = processed.convert('RGB')
            
            return processed
            
        except Exception as e:
            logger.error(f"Fast preprocessing error: {e}")
            raise e
    
    def predict(self, 
                image: Union[Image.Image, np.ndarray], 
                prompt: str, 
                options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fast prediction with MLX optimization"""
        if not self.loaded:
            if not self.load_model():
                return {"error": "Model unavailable"}
        
        try:
            start_time = time.time()
            
            if options is None:
                options = {}
            
            # Optimized parameters
            max_tokens = min(options.get("max_tokens", self.max_tokens), 150)
            
            # Fast preprocessing
            processed_image = self.preprocess_image_fast(image)
            
            # Generate response
            result = self.server.generate_response_fast(processed_image, prompt, max_tokens)
            
            if "error" in result:
                return result
            
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            # Format response using the required method
            formatted_response = self.format_response(result["response"])
            
            # Add performance metrics
            formatted_response["processing_time"] = processing_time
            formatted_response["inference_time"] = result.get("inference_time", 0)
            formatted_response["optimized"] = True
            formatted_response["method"] = result.get("method", "Unknown")
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Fast prediction error: {e}")
            return {
                "error": f"Fast prediction failed: {str(e)}",
                "details": str(e)
            }
    
    def unload_model(self) -> bool:
        """Unload optimized model"""
        try:
            if self.server:
                self.server.stop()
                
            self.loaded = False
            logger.info(f"Model {self.model_name} unloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error unloading model: {e}")
            return False 