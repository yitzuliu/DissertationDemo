"""
Phi-3.5-Vision Model Implementation

This module implements the BaseVisionModel interface for the Phi-3.5-Vision model.
Updated to align with testing framework patterns and MLX-VLM optimization.
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
    Manages the Phi-3.5-Vision model in-process (MLX-VLM optimized)
    """
    
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.processor = None
        self.loaded = False
        self.memory_manager = Phi3VisionMemoryManager()
        self.use_mlx = False
        
    def start(self) -> bool:
        """Load Phi-3.5-Vision model into memory"""
        if self.loaded:
            logger.info("Phi-3.5-Vision model already loaded")
            return True
            
        logger.info(f"Loading Phi-3.5-Vision model from: {self.model_path}")
        
        try:
            start_time = time.time()
            
            # Try MLX-VLM first (Apple Silicon optimization)
            try:
                from mlx_vlm import load
                logger.info("Loading MLX-VLM optimized Phi-3.5-Vision-Instruct model...")
                self.model, self.processor = load(self.model_path, trust_remote_code=True)
                self.use_mlx = True
                logger.info("MLX-VLM model loaded successfully!")
            except ImportError:
                logger.info("MLX-VLM not available, using transformers fallback...")
                self.use_mlx = False
            except Exception as e:
                logger.warning(f"MLX-VLM loading failed: {e}, using transformers fallback...")
                self.use_mlx = False
            
            # Fallback to transformers if MLX-VLM failed
            if not self.use_mlx:
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
                
                logger.info(f"Processor loaded: {processor_time:.2f}s")
                logger.info(f"Model loaded: {model_time:.2f}s")
                logger.info("⚠️ Using CPU for maximum compatibility (may be slower)")
            
            total_time = time.time() - start_time
            logger.info(f"Total loading time: {total_time:.2f}s")
            logger.info(f"Device: {self.device}")
            logger.info(f"Framework: {'MLX-VLM' if self.use_mlx else 'Transformers'}")
            
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
        """Generate response from Phi-3.5-Vision model using MLX-VLM or transformers"""
        if not self.is_running():
            return {"error": "Model not loaded"}
        
        try:
            start_time = time.time()
            
            if self.use_mlx:
                # MLX-VLM inference (same as testing framework)
                try:
                    from mlx_vlm import generate
                    logger.debug("Using MLX-VLM inference for Phi-3.5-Vision-Instruct...")
                    
                    # Save image to temporary file for MLX-VLM
                    import tempfile
                    temp_image_path = "temp_mlx_image.jpg"
                    image.save(temp_image_path)
                    
                    try:
                        # Use simple prompt format for MLX-VLM (same as testing framework)
                        mlx_prompt = f"<|image_1|>\nUser: {prompt}\nAssistant:"
                        
                        response = generate(
                            self.model, 
                            self.processor, 
                            mlx_prompt,
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
                    
                except Exception as e:
                    logger.error(f"MLX-VLM inference failed: {e}")
                    return {"error": f"MLX-VLM inference failed: {str(e)}"}
            else:
                # Transformers inference (fallback)
                try:
                    # Phi-3.5 Vision special format (model compatibility requirement)
                    messages = [
                        {"role": "user", "content": f"<|image_1|>\\n{prompt}"}
                    ]
                    
                    prompt_text = self.processor.tokenizer.apply_chat_template(
                        messages, 
                        tokenize=False, 
                        add_generation_prompt=True
                    )
                    
                    inputs = self.processor(prompt_text, [image], return_tensors="pt")
                    
                    # Move to correct device
                    device = next(self.model.parameters()).device
                    inputs = {k: v.to(device) for k, v in inputs.items()}
                    
                    # Technical fix: avoid DynamicCache error
                    with torch.no_grad():
                        outputs = self.model.generate(
                            **inputs, 
                            max_new_tokens=max_tokens,
                            do_sample=False,
                            use_cache=False,  # Disable cache to avoid DynamicCache error
                            pad_token_id=self.processor.tokenizer.eos_token_id
                        )
                    
                    text_response = self.processor.decode(outputs[0], skip_special_tokens=True)
                    
                except Exception as e:
                    logger.error(f"Transformers inference failed: {e}")
                    return {"error": f"Transformers inference failed: {str(e)}"}
            
            processing_time = time.time() - start_time
            
            return {
                "response": text_response,
                "processing_time": processing_time,
                "success": True,
                "framework": "MLX-VLM" if self.use_mlx else "Transformers"
            }
            
        except Exception as e:
            logger.error(f"Error during Phi-3.5-Vision inference: {e}")
            return {
                "error": f"Inference failed: {str(e)}",
                "success": False
            }

class Phi3VisionModel(BaseVisionModel):
    """
    Phi-3.5-Vision Model Implementation
    
    Updated to align with testing framework patterns and MLX-VLM optimization.
    VQA accuracy: 52.0%, Simple accuracy: 50.0%
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name=model_name, config=config)
        self.model_id = self.config.get("model_id", "mlx-community/Phi-3.5-vision-instruct-4bit")
        self.device = self.config.get("device", "cpu")
        self.server = None
        self.loaded = False
        self.load_time = 0
        self.stats = {"requests": 0, "total_time": 0.0}
        
        # Performance tracking
        self.last_cleanup = time.time()
        self.cleanup_interval = self.config.get("memory", {}).get("cleanup_interval", 10)
        
    def load_model(self) -> bool:
        """Load Phi-3.5-Vision model"""
        if self.loaded:
            return True
            
        try:
            start_time = time.time()
            
            # Initialize server
            self.server = Phi3VisionServer(self.model_id, self.device)
            
            # Load model
            success = self.server.start()
            
            if success:
                self.loaded = True
                self.load_time = time.time() - start_time
                logger.info(f"Phi-3.5-Vision model loaded successfully in {self.load_time:.2f}s")
                return True
            else:
                logger.error("Failed to load Phi-3.5-Vision model")
                return False
                
        except Exception as e:
            logger.error(f"Error loading Phi-3.5-Vision model: {e}")
            return False

    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """Preprocess image for Phi-3.5-Vision model"""
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
        """Predict method for Phi-3.5-Vision model"""
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
                Phi3VisionMemoryManager.cleanup_memory()
                self.last_cleanup = time.time()
            
            if result.get("success", False):
                return {
                    "response": result["response"],
                    "processing_time": result["processing_time"],
                    "model": self.model_name,
                    "framework": result.get("framework", "Unknown"),
                    "success": True
                }
            else:
                return {
                    "error": result.get("error", "Unknown error"),
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"Error during Phi-3.5-Vision prediction: {e}")
            return {
                "error": f"Prediction failed: {str(e)}",
                "success": False
            }

    def format_response(self, raw_response: str) -> Dict[str, Any]:
        """Format response for API compatibility"""
        return {
            "response": raw_response,
            "model": self.model_name,
            "framework": "MLX-VLM" if self.server and self.server.use_mlx else "Transformers",
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
            logger.error(f"Error unloading Phi-3.5-Vision model: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        framework = "MLX-VLM" if self.server and self.server.use_mlx else "Transformers"
        return {
            "model_name": self.model_name,
            "model_id": self.model_id,
            "loaded": self.loaded,
            "framework": framework,
            "device": self.device,
            "load_time": self.load_time,
            "stats": self.stats,
            "performance": {
                "vqa_accuracy": "52.0%",
                "simple_accuracy": "50.0%",
                "avg_inference_time": "9.64s"
            }
        }

if __name__ == '__main__':
    print("This script is not meant to be run directly. Use a runner script.") 