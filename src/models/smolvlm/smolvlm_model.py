"""
SmolVLM Model Implementation (Refactored)

This module implements the BaseVisionModel interface for the SmolVLM model.
It uses the unified server manager for better consistency and maintainability.
"""

import time
import json
import requests
import base64
import numpy as np
from typing import Dict, Any, Optional, Union
from PIL import Image, ImageEnhance, ImageFilter, ImageChops, ImageOps
import logging
import io
import sys
import os
from pathlib import Path

# Add the current directory to the path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from server_manager import SmolVLMServerManager

# Add parent directories to path for imports
project_root = current_dir.parent.parent.parent.parent
sys.path.append(str(project_root))

try:
    from src.models.base_model import BaseVisionModel
    from src.backend.utils.image_processing import (
        preprocess_for_model,
        smart_crop_and_resize,
        reduce_noise,
        enhance_color_balance
    )
except ImportError:
    # Fallback for direct execution
    sys.path.append(str(current_dir.parent.parent))
    from models.base_model import BaseVisionModel
    from backend.utils.image_processing import (
        preprocess_for_model,
        smart_crop_and_resize,
        reduce_noise,
        enhance_color_balance
    )

logger = logging.getLogger(__name__)

class SmolVLMModel(BaseVisionModel):
    """
    Implementation of the SmolVLM model using the unified server manager.
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the SmolVLM model.
        
        Args:
            model_name: The name of the model
            config: A dictionary containing model configuration
        """
        super().__init__(model_name, config)
        
        # Get configuration with defaults
        self.smolvlm_version = config.get("smolvlm_version", "ggml-org/SmolVLM-500M-Instruct-GGUF")
        self.port = config.get("port", 8080)
        self.timeout = config.get("timeout", 60)
        self.server_url = f"http://localhost:{self.port}/v1/chat/completions"
        self.headers = {"Content-Type": "application/json"}
        
        # Server management
        self.manage_server = config.get("manage_server", True)
        if self.manage_server:
            self.server_manager = SmolVLMServerManager(
                model_name=self.smolvlm_version,
                port=self.port,
                timeout=self.timeout
            )
        else:
            self.server_manager = None
    
    def load_model(self) -> bool:
        """
        Load the SmolVLM model by starting or connecting to the server.
        
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            start_time = time.time()
            
            # If we're managing the server, start it if it's not running
            if self.manage_server:
                if self.server_manager is None:
                    logger.error("Server manager not initialized")
                    return False
                    
                if not self.server_manager.is_running():
                    logger.info(f"Starting SmolVLM server for model {self.model_name}...")
                    if not self.server_manager.start(verbose=False):
                        logger.error("Failed to start SmolVLM server")
                        return False
            
            # Check if the server is accessible
            try:
                response = requests.get(f"http://localhost:{self.port}/health", timeout=5)
                if response.status_code != 200:
                    logger.error(f"SmolVLM server health check failed: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to connect to SmolVLM server: {str(e)}")
                return False
                
            self.loaded = True
            self.load_time = time.time() - start_time
            
            logger.info(f"SmolVLM model {self.model_name} ready")
            return True
            
        except Exception as e:
            logger.error(f"Error loading SmolVLM model: {str(e)}")
            self.loaded = False
            return False
    
    def enhance_color_lab(self, image: Image.Image, config: Dict) -> Image.Image:
        """
        Enhance image colors in LAB color space.
        LAB color space is closer to human visual perception.
        """
        try:
            from skimage import color
            import numpy as np
            
            # Convert to LAB color space
            img_array = np.array(image)
            lab_image = color.rgb2lab(img_array)
            
            # Enhance L channel (lightness)
            l_boost = float(config.get("l_channel_boost", 1.2))
            l_channel = lab_image[:,:,0]
            l_channel = np.clip(l_channel * l_boost, 0, 100)
            lab_image[:,:,0] = l_channel
            
            # Enhance a,b channels (color)
            ab_boost = float(config.get("ab_channel_boost", 1.2))
            lab_image[:,:,1:] *= ab_boost
            
            # Convert back to RGB
            enhanced_array = color.lab2rgb(lab_image)
            return Image.fromarray((enhanced_array * 255).astype(np.uint8))
        except Exception as e:
            logger.error(f"LAB color enhancement failed: {e}")
            return image
    
    def enhance_details_multi_scale(self, image: Image.Image, config: Dict) -> Image.Image:
        """Multi-scale detail enhancement"""
        try:
            scales = config.get("scales", [0.5, 1.0, 2.0])
            detail_boost = float(config.get("detail_boost", 1.5))
            enhanced = image.copy()
            
            for scale in scales:
                # Create Gaussian blur version
                radius = 2 * scale
                blurred = image.filter(ImageFilter.GaussianBlur(radius=radius))
                
                # Calculate detail layer
                detail = ImageChops.difference(image, blurred)
                
                # Enhance details
                detail = ImageEnhance.Contrast(detail).enhance(detail_boost)
                
                # Merge back to original
                enhanced = ImageChops.add(enhanced, detail, scale=1.0, offset=0)
            
            return enhanced
        except Exception as e:
            logger.error(f"Multi-scale detail enhancement failed: {e}")
            return image
    
    def adaptive_contrast_enhance(self, image: Image.Image, config: Dict) -> Image.Image:
        """
        Adaptive contrast enhancement based on image characteristics.
        Automatically adjusts contrast based on image brightness.
        """
        try:
            from PIL import ImageStat
            
            # Calculate image statistics
            stat = ImageStat.Stat(image)
            mean = sum(stat.mean) / len(stat.mean)  # Average of all channels
            
            # Adjust contrast based on image characteristics
            dark_boost = float(config.get("dark_boost", 1.4))
            light_boost = float(config.get("light_boost", 1.2))
            
            if mean < 128:  # Dark image
                factor = dark_boost
            else:  # Light image
                factor = light_boost
            
            return ImageEnhance.Contrast(image).enhance(factor)
        except Exception as e:
            logger.error(f"Adaptive contrast enhancement failed: {e}")
            return image
    
    def edge_preserving_smooth(self, image: Image.Image, config: Dict) -> Image.Image:
        """Edge-preserving smoothing"""
        try:
            import cv2
            import numpy as np
            
            # Get parameters
            bilateral = config.get("bilateral_filter", {})
            d = bilateral.get("diameter", 9)
            sigma_color = bilateral.get("sigma_color", 75)
            sigma_space = bilateral.get("sigma_space", 75)
            
            # Convert to OpenCV format
            img_array = np.array(image)
            
            # Apply bilateral filter
            smoothed = cv2.bilateralFilter(
                img_array, 
                d=d,
                sigmaColor=sigma_color,
                sigmaSpace=sigma_space
            )
            
            return Image.fromarray(smoothed)
        except Exception as e:
            logger.error(f"Edge-preserving smoothing failed: {e}")
            return image
    
    def hdr_simulation(self, image: Image.Image, config: Dict) -> Image.Image:
        """
        HDR effect simulation.
        Creates a high dynamic range effect by blending multiple exposures.
        """
        try:
            strength = float(config.get("strength", 0.5))
            under_exp = float(config.get("under_exposure", 0.7))
            over_exp = float(config.get("over_exposure", 1.3))
            
            # Create multiple exposure effects
            under_exposed = ImageEnhance.Brightness(image).enhance(under_exp)
            over_exposed = ImageEnhance.Brightness(image).enhance(over_exp)
            
            # Blend different exposures
            result = Image.blend(under_exposed, image, strength)
            result = Image.blend(result, over_exposed, strength * 0.6)
            
            return result
        except Exception as e:
            logger.error(f"HDR simulation failed: {e}")
            return image
    
    def enhance_image_quality(self, image: Image.Image, config: Dict) -> Image.Image:
        """
        Apply advanced image enhancement techniques.
        Uses the centralized image processing utilities.
        """
        try:
            # Output current configuration
            logger.info("Current image processing configuration:")
            logger.info(f"Color balance config: {config.get('color_balance', {})}")
            logger.info(f"Noise reduction config: {config.get('noise_reduction', {})}")
            
            # Apply color balance enhancement
            if config.get("color_balance", {}).get("enabled", True):
                method = config["color_balance"].get("method", "lab")
                logger.info(f"Applying color balance enhancement: {method}")
                image = enhance_color_balance(
                    image,
                    method=method,
                    config=config["color_balance"]
                )
            
            # Apply noise reduction
            if config.get("noise_reduction", {}).get("enabled", True):
                method = config["noise_reduction"].get("method", "bilateral")
                logger.info(f"Applying noise reduction: {method}")
                image = reduce_noise(
                    image,
                    method=method,
                    config=config["noise_reduction"]
                )
            
            return image
            
        except Exception as e:
            logger.error(f"Error in advanced image enhancement: {e}")
            return image

    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> str:
        """
        Preprocess the input image for the model with enhanced quality.
        """
        try:
            # Convert numpy array to PIL Image if needed
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            elif not isinstance(image, Image.Image):
                raise ValueError("Input must be PIL Image or numpy array")
            
            # Get image processing configuration
            image_config = self.config.get("image_processing", {})
            
            # Apply smart cropping and resizing
            if image_config.get("smart_crop", True):
                target_size = image_config.get("size", [1024, 1024])
                min_size = image_config.get("min_size", 512)
                preserve_aspect_ratio = image_config.get("preserve_aspect_ratio", True)
                
                image = smart_crop_and_resize(
                    image,
                    target_size=target_size,
                    min_size=min_size,
                    preserve_aspect_ratio=preserve_aspect_ratio
                )
            
            # Apply image quality enhancements
            image = self.enhance_image_quality(image, image_config)
            
            # Save image
            buffer = io.BytesIO()
            save_format = image_config.get("format", "JPEG").upper()
            
            # Prepare save parameters
            save_params = {
                "format": save_format,
                "quality": int(image_config.get("jpeg_quality", 95)),
                "optimize": image_config.get("optimize", True)
            }
            
            # Additional JPEG parameters
            if save_format == "JPEG":
                if image_config.get("progressive"):
                    save_params["progressive"] = True
                if image_config.get("subsampling"):
                    save_params["subsampling"] = image_config["subsampling"]
            
            # Save image
            image.save(buffer, **save_params)
            image_bytes = buffer.getvalue()
            
            # Encode to base64
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            logger.debug(f"Image processed successfully: format={save_format}, size={len(image_bytes)/1024:.1f}KB")
            
            return encoded_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image for SmolVLM: {str(e)}")
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
                return {"error": "Model server is not available"}
        
        try:
            start_time = time.time()
            
            # Apply default options if not provided
            if options is None:
                options = {}
                
            # Get generation parameters
            temperature = options.get("temperature", 0.0)
            max_tokens = options.get("max_tokens", 512)
            
            # Preprocess the image to base64
            image_base64 = self.preprocess_image(image)
            
            # Create the API request payload
            payload = {
                "model": "SmolVLM",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # Make the API call
            response = requests.post(
                self.server_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"SmolVLM API error: {response.status_code} - {response.text}")
                return {
                    "error": f"API Error {response.status_code}",
                    "details": response.text
                }
            
            # Extract the response content
            response_json = response.json()
            raw_response = response_json["choices"][0]["message"]["content"]
            
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            # Format the response
            result = self.format_response(raw_response)
            result["processing_time"] = processing_time
            
            return result
            
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
            # Clean up response to extract any JSON
            clean_text = raw_response.strip()
            
            # Remove markdown code block formatting if present
            if "```json" in clean_text:
                clean_text = clean_text.replace("```json", "").replace("```", "").strip()
            elif "```" in clean_text:
                # Extract content between first and last ```
                start = clean_text.find("```") + 3
                end = clean_text.rfind("```")
                if start < end:
                    clean_text = clean_text[start:end].strip()
            
            # Try to parse as JSON
            try:
                parsed_json = json.loads(clean_text)
                return {
                    "success": True,
                    "response": parsed_json,
                    "raw_response": raw_response
                }
            except json.JSONDecodeError:
                # If not valid JSON, return as text
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
        
        If we're managing the server, this will stop it.
        
        Returns:
            True if unloading was successful, False otherwise
        """
        try:
            if self.manage_server and self.server_manager:
                self.server_manager.stop()
                
            self.loaded = False
            import gc
            gc.collect()
            logger.info(f"Model {self.model_name} unloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error unloading model {self.model_name}: {str(e)}")
            return False 