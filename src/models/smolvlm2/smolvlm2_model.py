"""
SmolVLM2 Model Implementation

This module implements the BaseVisionModel interface for the SmolVLM2-500M-Video-Instruct model.
Unlike SmolVLM which uses llama-server, this runs the transformers model directly with 
optimized memory management for Apple Silicon MPS.
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
from transformers import AutoProcessor, AutoModelForImageTextToText
import threading
import gc
from pathlib import Path

# Add parent directories to path for imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from src.models.base_model import BaseVisionModel
from src.backend.utils.image_processing import preprocess_for_model

logger = logging.getLogger(__name__)

class SmolVLM2MemoryManager:
    """
    Memory management utilities for SmolVLM2 with MPS optimization
    """
    
    @staticmethod
    def cleanup_memory(aggressive=False):
        """Clean up MPS memory with optional aggressive mode"""
        try:
            if aggressive:
                gc.collect()  # Force Python garbage collection
                logger.debug("Python garbage collected")
            
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
                logger.debug("MPS cache cleared")
                
        except Exception as e:
            logger.warning(f"Memory cleanup warning: {e}")
    
    @staticmethod
    def check_memory_availability(required_gb=3.0):
        """Check if enough memory is available for operation"""
        try:
            if torch.backends.mps.is_available():
                current_memory = torch.mps.current_allocated_memory() / 1024**3
                max_memory = 18.0  # Typical M1/M2 unified memory
                available = max_memory - current_memory
                
                if available < required_gb:
                    logger.warning(f"Low memory: {available:.2f} GB available, {required_gb:.2f} GB required")
                    SmolVLM2MemoryManager.cleanup_memory(aggressive=True)
                    return False
                else:
                    logger.debug(f"Memory OK: {available:.2f} GB available")
                    return True
            return True  # Assume OK if MPS not available
                
        except Exception as e:
            logger.warning(f"Memory check failed: {e}")
            return True  # Assume OK if can't check

class SmolVLM2Server:
    """
    Manages the SmolVLM2 model in-process (no external server needed)
    """
    
    def __init__(self, model_path: str, device: str = "mps"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.processor = None
        self.loaded = False
        self.memory_manager = SmolVLM2MemoryManager()
        
    def start(self) -> bool:
        """Load SmolVLM2 model into memory"""
        if self.loaded:
            logger.info("SmolVLM2 model already loaded")
            return True
            
        logger.info(f"Loading SmolVLM2 model from: {self.model_path}")
        
        try:
            start_time = time.time()
            
            # Check memory before loading
            if not self.memory_manager.check_memory_availability(required_gb=6.0):
                logger.error("Insufficient memory for SmolVLM2 model")
                return False
            
            # Load processor
            processor_start = time.time()
            self.processor = AutoProcessor.from_pretrained(self.model_path)
            processor_time = time.time() - processor_start
            
            # Load model with MPS-optimized settings
            model_start = time.time()
            self.model = AutoModelForImageTextToText.from_pretrained(
                self.model_path,
                torch_dtype=torch.float32,  # MPS-optimized precision
                device_map=None,  # Manual device management for MPS
            )
            self.model = self.model.to(self.device)
            model_time = time.time() - model_start
            
            total_time = time.time() - start_time
            
            logger.info(f"Processor loaded: {processor_time:.2f}s")
            logger.info(f"Model loaded: {model_time:.2f}s")
            logger.info(f"Total loading time: {total_time:.2f}s")
            logger.info(f"Device: {self.device}")
            
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading SmolVLM2 model: {e}")
            self.loaded = False
            return False
    
    def stop(self) -> bool:
        """Unload model from memory"""
        if not self.loaded:
            return True
            
        logger.info("Unloading SmolVLM2 model...")
        try:
            if hasattr(self, 'model') and self.model is not None:
                del self.model
                self.model = None
            if hasattr(self, 'processor') and self.processor is not None:
                del self.processor
                self.processor = None
            
            self.memory_manager.cleanup_memory(aggressive=True)
            self.loaded = False
            logger.info("SmolVLM2 model unloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading SmolVLM2 model: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if model is loaded and ready"""
        return self.loaded and self.model is not None and self.processor is not None
    
    def generate_response(self, messages: List[Dict], max_tokens: int = 150) -> Dict[str, Any]:
        """Generate response from SmolVLM2 model"""
        if not self.is_running():
            return {"error": "Model not loaded"}
        
        try:
            # Pre-check memory availability
            if not self.memory_manager.check_memory_availability(required_gb=3.0):
                return {"error": "Insufficient memory for inference"}
            
            start_time = time.time()
            
            # Apply chat template
            inputs = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            )
            
            # MPS-optimized tensor handling
            inputs = {k: v.to(self.device, dtype=torch.float32 if v.dtype.is_floating_point else v.dtype) 
                     for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
            inference_time = time.time() - start_time
            
            # Enhanced memory cleanup
            del inputs, generated_ids
            self.memory_manager.cleanup_memory(aggressive=True)
            
            # Extract response
            full_response = generated_texts[0]
            if "Assistant:" in full_response:
                response = full_response.split("Assistant:")[-1].strip()
            else:
                response = full_response
            
            return {
                "success": True,
                "response": response,
                "inference_time": inference_time
            }
            
        except Exception as e:
            logger.error(f"Error during SmolVLM2 inference: {e}")
            # Cleanup on error
            self.memory_manager.cleanup_memory(aggressive=True)
            return {"error": f"Inference failed: {str(e)}"}


class SmolVLM2Model(BaseVisionModel):
    """
    Implementation of the SmolVLM2 model with direct transformers integration.
    Maintains API compatibility with SmolVLM while using in-process model loading.
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the SmolVLM2 model.
        
        Args:
            model_name: The name of the model
            config: A dictionary containing model configuration
        """
        super().__init__(model_name, config)
        
        self.model_path = config.get("model_path", "SmolVLM2-500M-Video-Instruct")
        self.device = config.get("device", "mps")
        self.timeout = config.get("timeout", 60)
        self.max_tokens = config.get("max_tokens", 150)
        
        # Create server instance (in-process model management)
        self.server = SmolVLM2Server(self.model_path, self.device)
    
    def load_model(self) -> bool:
        """
        Load the SmolVLM2 model.
        
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            start_time = time.time()
            
            logger.info(f"Loading SmolVLM2 model: {self.model_name}")
            if not self.server.start():
                logger.error("Failed to start SmolVLM2 server")
                return False
                
            self.loaded = True
            self.load_time = time.time() - start_time
            
            logger.info(f"SmolVLM2 model {self.model_name} ready")
            return True
            
        except Exception as e:
            logger.error(f"Error loading SmolVLM2 model: {str(e)}")
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
                model_type="smolvlm2",
                config=self.config,
                return_format="pil"
            )
            
            # Apply SmolVLM2-specific preprocessing
            max_size = self.config.get("image_processing", {}).get("max_size", 512)
            if max(pil_image.size) > max_size:
                scale = max_size / max(pil_image.size)
                new_size = (int(pil_image.size[0] * scale), int(pil_image.size[1] * scale))
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                logger.debug(f"Resized image to {new_size}")
            
            return pil_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image for SmolVLM2: {str(e)}")
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
            
            # Create messages in SmolVLM2 format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": processed_image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Generate response using the server
            result = self.server.generate_response(messages, max_tokens)
            
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