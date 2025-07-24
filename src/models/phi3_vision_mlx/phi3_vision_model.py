"""
Phi-3.5-Vision Standard Model Implementation

Standard version of Phi-3.5-Vision model using:
- MLX-VLM for Apple Silicon optimization (primary)
- Transformers as fallback
- OpenAI-compatible API
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

logger = logging.getLogger(__name__)

# Add parent directories to path for imports
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
sys.path.append(project_root)

# Import with fallback strategy
try:
    from src.models.base_model import BaseVisionModel
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

class StandardPhi3VisionServer:
    """
    Standard Phi-3.5-Vision server with MLX and transformers fallback
    """
    
    def __init__(self, model_path: str, device: str = "auto"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.processor = None
        self.loaded = False
        self.use_mlx = False
        
    def start(self) -> bool:
        """Load Phi-3.5-Vision model with MLX and transformers fallback"""
        if self.loaded:
            logger.info("Phi-3.5-Vision model already loaded")
            return True
            
        logger.info(f"Loading Phi-3.5-Vision model from: {self.model_path}")
        
        try:
            start_time = time.time()
            
            # Strategy 1: Try MLX-VLM first
            try:
                logger.info("Loading MLX-VLM optimized Phi-3.5-Vision-Instruct model...")
                from mlx_vlm import load, generate
                
                self.model, self.processor = load(self.model_path, trust_remote_code=True)
                self.use_mlx = True
                
                total_time = time.time() - start_time
                logger.info(f"✅ MLX Phi-3.5-Vision loaded in {total_time:.2f}s")
                self.loaded = True
                return True
                
            except ImportError as e:
                logger.warning(f"MLX-VLM not available: {e}, using transformers fallback...")
                self.use_mlx = False
                
            except Exception as e:
                logger.warning(f"MLX-VLM loading failed: {e}, using transformers fallback...")
                self.use_mlx = False
            
            # Strategy 2: Fallback to transformers
            if not self.use_mlx:
                from transformers import AutoProcessor, AutoModelForVision2Seq
                
                logger.info("Loading transformers Phi-3.5-Vision (fallback)...")
                
                # 使用正確的 Microsoft 模型路徑作為 fallback
                fallback_model_path = "microsoft/Phi-3.5-vision-instruct"
                
                self.processor = AutoProcessor.from_pretrained(
                    fallback_model_path, 
                    trust_remote_code=True
                )
                
                self.model = AutoModelForVision2Seq.from_pretrained(
                    fallback_model_path,
                    torch_dtype=torch.float16,
                    device_map="cpu",  # Force CPU for stability
                    trust_remote_code=True,
                    _attn_implementation="eager"
                )
                
                total_time = time.time() - start_time
                logger.info(f"✅ Transformers fallback loaded in {total_time:.2f}s")
            
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading Phi-3.5-Vision model: {e}")
            return False
    
    def generate_response(self, image: Image.Image, prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate response from Phi-3.5-Vision model"""
        if not self.loaded:
            return {"error": "Model not loaded"}
        
        # 確保沒有硬編碼的回應
        logger.info(f"🔍 Processing prompt: '{prompt[:50]}...'")
        logger.info(f"🔍 Image size: {image.size}")
        
        try:
            start_time = time.time()
            
            if self.use_mlx:
                # MLX inference
                from mlx_vlm import generate
                
                # Save image to temp file for MLX
                temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                temp_path = temp_file.name
                temp_file.close()
                
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(temp_path, 'JPEG', quality=95)
                
                try:
                    # MLX prompt format - 確保使用正確的提示
                    mlx_prompt = f"<|image_1|>\nUser: {prompt}\nAssistant:"
                    logger.info(f"🔍 MLX prompt: '{mlx_prompt[:100]}...'")
                    
                    response = generate(
                        model=self.model,
                        processor=self.processor,
                        image=temp_path,
                        prompt=mlx_prompt,
                        max_tokens=max_tokens,
                        temp=0.7,
                        verbose=True  # 啟用詳細模式來調試
                    )
                    
                    logger.info(f"🔍 Raw MLX response: {response}")
                    
                    # Process response
                    if isinstance(response, tuple):
                        text_response = response[0]
                    else:
                        text_response = str(response)
                    
                    # Clean response - 確保不會意外過濾掉有效回應
                    text_response = text_response.replace("<|end|>", "").replace("<|endoftext|>", "").strip()
                    
                    # 檢查是否為空回應
                    if not text_response:
                        logger.warning("⚠️ Empty response from MLX model")
                        text_response = f"MLX model processed your request about the image but returned an empty response."
                    
                    logger.info(f"🔍 Processed response: '{text_response[:100]}...'")
                    
                finally:
                    # Cleanup temp file
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                
            else:
                # Transformers inference - 確保使用正確的提示格式
                messages = [{"role": "user", "content": f"<|image_1|>\n{prompt}"}]
                logger.info(f"🔍 Transformers messages: {messages}")
                
                prompt_text = self.processor.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                
                logger.info(f"🔍 Formatted prompt: '{prompt_text[:100]}...'")
                
                inputs = self.processor(prompt_text, [image], return_tensors="pt")
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        do_sample=False,
                        temperature=0.7,
                        pad_token_id=self.processor.tokenizer.eos_token_id
                    )
                
                text_response = self.processor.decode(outputs[0], skip_special_tokens=True)
                logger.info(f"🔍 Raw transformers response: '{text_response[:100]}...'")
                
                # Clean transformers response
                if "Assistant:" in text_response:
                    text_response = text_response.split("Assistant:")[-1].strip()
                
                # 檢查是否為空回應
                if not text_response:
                    logger.warning("⚠️ Empty response from transformers model")
                    text_response = f"Transformers model processed your request about the image but returned an empty response."
            
            processing_time = time.time() - start_time
            
            return {
                "response": text_response,
                "processing_time": processing_time,
                "success": True,
                "method": "MLX" if self.use_mlx else "Transformers"
            }
            
        except Exception as e:
            logger.error(f"Error during Phi-3.5-Vision inference: {e}")
            return {
                "error": f"Inference failed: {str(e)}",
                "success": False
            }

class Phi3VisionModel(BaseVisionModel):
    """
    Standard Phi-3.5-Vision Model Implementation
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name=model_name, config=config)
        
        # 使用正確的配置鍵名，優先使用 model_path
        self.model_path = self.config.get("model_path", "mlx-community/Phi-3.5-vision-instruct-4bit")
        self.device = self.config.get("device", "auto")
        self.timeout = self.config.get("timeout", 180)
        self.max_tokens = self.config.get("max_tokens", 100)
        
        logger.info(f"🔧 Phi3VisionModel initialized with model_path: {self.model_path}")
        
        self.server = None
        self.loaded = False
        self.load_time = 0
        self.stats = {"requests": 0, "total_time": 0.0}
    
    def load_model(self) -> bool:
        """Load Phi-3.5-Vision model"""
        if self.loaded:
            return True
            
        try:
            start_time = time.time()
            
            # Initialize server with correct model path
            self.server = StandardPhi3VisionServer(self.model_path, self.device)
            
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
            
            # Get target size from config
            image_config = self.config.get("image_processing", {})
            target_size = image_config.get("size", [512, 512])
            max_size = image_config.get("max_size", 1024)
            
            # Resize if needed
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
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
            
            if result.get("success", False):
                return {
                    "response": {"text": result["response"]},
                    "processing_time": result["processing_time"],
                    "model": self.model_name,
                    "method": result.get("method", "Unknown"),
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
            "text": raw_response,
            "model": self.model_name,
            "framework": "MLX-VLM + Transformers",
            "device": self.device
        }

    def unload_model(self) -> bool:
        """Unload model and clean up memory"""
        try:
            if self.server is not None:
                self.server.stop()
                self.server = None
                self.loaded = False
                return True
            return True
        except Exception as e:
            logger.error(f"Error unloading Phi-3.5-Vision model: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        avg_time = self.stats["total_time"] / max(self.stats["requests"], 1)
        
        return {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "loaded": self.loaded,
            "framework": "MLX-VLM + Transformers Fallback",
            "device": self.device,
            "load_time": self.load_time,
            "stats": self.stats,
            "avg_inference_time": f"{avg_time:.2f}s",
            "use_mlx": getattr(self.server, 'use_mlx', False) if self.server else False
        }

if __name__ == '__main__':
    print("This script is not meant to be run directly. Use a runner script.")