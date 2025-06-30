"""
SmolVLM Model Implementation

This module implements the BaseVisionModel interface for the SmolVLM model.
It uses a running SmolVLM server via llama-server and communicates with it
using the OpenAI API compatibility interface.
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
import subprocess
import sys
import os
import signal
import threading
from pathlib import Path

from ..base_model import BaseVisionModel
from src.backend.utils.image_processing import preprocess_for_model

logger = logging.getLogger(__name__)

class SmolVLMServer:
    """
    Manages the SmolVLM server process using llama-server
    """
    
    def __init__(self, model_name="ggml-org/SmolVLM-500M-Instruct-GGUF", port=8080):
        self.process = None
        self.model_name = model_name
        self.port = port
        self.server_url = f"http://localhost:{port}/v1/chat/completions"
        self.server_ready = False
        self.output_thread = None
        
    def start(self) -> bool:
        """Start SmolVLM server"""
        if self.is_running():
            logger.info("SmolVLM server already running")
            return True
            
        cmd = [
            "llama-server",
            "-hf", self.model_name,
            "-ngl", "99",
            "--port", str(self.port)
        ]
        
        logger.info(f"Starting SmolVLM server with model: {self.model_name} on port: {self.port}")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Start a thread to monitor server output
            def monitor_output():
                if self.process and self.process.stdout:
                    for line in iter(self.process.stdout.readline, ''):
                        logger.debug(f"SmolVLM server: {line.rstrip()}")
                        if "HTTP server listening" in line or "Server listening" in line:
                            logger.info(f"SmolVLM server running at http://localhost:{self.port}")
                            self.server_ready = True
            
            self.output_thread = threading.Thread(target=monitor_output)
            self.output_thread.daemon = True
            self.output_thread.start()
            
            # Wait for server to become ready
            start_time = time.time()
            while time.time() - start_time < 30:  # Wait up to 30 seconds
                if self.server_ready:
                    return True
                if self.process.poll() is not None:
                    logger.error("SmolVLM server failed to start")
                    return False
                time.sleep(0.5)
                
            logger.warning("Timed out waiting for SmolVLM server to start")
            return self.is_running()
            
        except FileNotFoundError:
            logger.error("Error: 'llama-server' command not found")
            return False
        except Exception as e:
            logger.error(f"Error starting SmolVLM server: {str(e)}")
            return False
            
    def stop(self) -> bool:
        """Stop server"""
        if not self.process:
            return True
            
        logger.info("Stopping SmolVLM server...")
        try:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                logger.info("SmolVLM server stopped")
                return True
            except subprocess.TimeoutExpired:
                logger.warning("Force stopping server...")
                self.process.kill()
                self.process.wait()
                logger.info("SmolVLM server force stopped")
                return True
        except Exception as e:
            logger.error(f"Error stopping SmolVLM server: {str(e)}")
            return False
        finally:
            self.process = None
            self.server_ready = False
    
    def is_running(self) -> bool:
        """Check if server is running by testing the endpoint"""
        try:
            response = requests.get(f"http://localhost:{self.port}/health")
            return response.status_code == 200
        except:
            return False


class SmolVLMModel(BaseVisionModel):
    """
    Implementation of the SmolVLM model using llama-server with OpenAI API compatibility.
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the SmolVLM model.
        
        Args:
            model_name: The name of the model
            config: A dictionary containing model configuration
        """
        super().__init__(model_name, config)
        
        self.smolvlm_version = config.get("smolvlm_version", "ggml-org/SmolVLM-500M-Instruct-GGUF")
        self.port = config.get("port", 8080)
        self.server_url = f"http://localhost:{self.port}/v1/chat/completions"
        self.timeout = config.get("timeout", 60)
        self.headers = {"Content-Type": "application/json"}
        
        # If manage_server is True, we'll start a server instance
        self.manage_server = config.get("manage_server", True)
        if self.manage_server:
            self.server = SmolVLMServer(self.smolvlm_version, self.port)
        else:
            self.server = None
    
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
                if self.server is None:
                    logger.error("Server instance not initialized")
                    return False
                    
                if not self.server.is_running():
                    logger.info(f"Starting SmolVLM server for model {self.model_name}...")
                    if not self.server.start():
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
        """多尺度細節增強"""
        try:
            scales = config.get("scales", [0.5, 1.0, 2.0])
            detail_boost = float(config.get("detail_boost", 1.5))
            enhanced = image.copy()
            
            for scale in scales:
                # 創建高斯模糊版本
                radius = 2 * scale
                blurred = image.filter(ImageFilter.GaussianBlur(radius=radius))
                
                # 計算細節層
                detail = ImageChops.difference(image, blurred)
                
                # 增強細節
                detail = ImageEnhance.Contrast(detail).enhance(detail_boost)
                
                # 合併回原圖
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
        """邊緣保持平滑"""
        try:
            import cv2
            import numpy as np
            
            # 獲取參數
            bilateral = config.get("bilateral_filter", {})
            d = bilateral.get("diameter", 9)
            sigma_color = bilateral.get("sigma_color", 75)
            sigma_space = bilateral.get("sigma_space", 75)
            
            # 轉換為 OpenCV 格式
            img_array = np.array(image)
            
            # 應用雙邊濾波
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
        Includes LAB color enhancement, adaptive contrast, and HDR simulation.
        """
        try:
            # Output current configuration
            logger.info("Current image processing configuration:")
            logger.info(f"Advanced color config: {config.get('advanced_color', {})}")
            logger.info(f"Adaptive enhancement config: {config.get('adaptive_enhancement', {})}")
            logger.info(f"HDR simulation config: {config.get('hdr_simulation', {})}")
            
            # Advanced color processing in LAB space
            if config.get("advanced_color", {}).get("enabled", True):
                logger.info("Applying LAB color enhancement")
                image = self.enhance_color_lab(image, config["advanced_color"])
            
            # Adaptive enhancement
            if config.get("adaptive_enhancement", {}).get("enabled", True):
                if config["adaptive_enhancement"].get("auto_contrast"):
                    logger.info("Applying adaptive contrast enhancement")
                    image = self.adaptive_contrast_enhance(image, config["adaptive_enhancement"])
            
            # HDR simulation
            if config.get("hdr_simulation", {}).get("enabled", True):
                logger.info("Applying HDR simulation")
                image = self.hdr_simulation(image, config["hdr_simulation"])
            
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
            
            # Process the image to get a PIL image first
            pil_image = preprocess_for_model(
                image=image,
                model_type="smolvlm",
                config=self.config,
                return_format="pil"
            )
            
            if not isinstance(pil_image, Image.Image):
                raise ValueError("Preprocessed image must be PIL Image")
            
            # 確保圖像是 RGB 模式
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 獲取圖像處理配置
            image_config = self.config.get("image_processing", {})
            
            # 保持長寬比的大小調整
            if image_config.get("preserve_aspect_ratio", True):
                target_size = image_config.get("size", [1024, 1024])
                min_size = image_config.get("min_size", 512)
                
                # 計算目標大小
                width, height = pil_image.size
                scale = min(target_size[0]/width, target_size[1]/height)
                
                # 確保不小於最小尺寸
                new_width = max(int(width * scale), min_size)
                new_height = max(int(height * scale), min_size)
                
                # 使用指定的調整方法
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.debug(f"Resized to {new_width}x{new_height}")
            
            # 應用基本圖像增強
            if image_config.get("contrast_factor"):
                pil_image = ImageEnhance.Contrast(pil_image).enhance(
                    float(image_config["contrast_factor"]))
            
            if image_config.get("brightness_factor"):
                pil_image = ImageEnhance.Brightness(pil_image).enhance(
                    float(image_config["brightness_factor"]))
            
            if image_config.get("sharpness_factor"):
                pil_image = ImageEnhance.Sharpness(pil_image).enhance(
                    float(image_config["sharpness_factor"]))
            
            # 應用高級圖像增強
            pil_image = self.enhance_image_quality(pil_image, image_config)
            
            # 保存圖像
            buffer = io.BytesIO()
            save_format = image_config.get("format", "JPEG").upper()
            
            # 準備保存參數
            save_params = {
                "format": save_format,
                "quality": int(image_config.get("jpeg_quality", 95)),
                "optimize": image_config.get("optimize", True)
            }
            
            # 對於 JPEG 格式的額外參數
            if save_format == "JPEG":
                if image_config.get("progressive"):
                    save_params["progressive"] = True
                if image_config.get("subsampling"):
                    save_params["subsampling"] = image_config["subsampling"]
            
            # 保存圖像
            pil_image.save(buffer, **save_params)
            image_bytes = buffer.getvalue()
            
            # 編碼為 base64
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
            if self.manage_server and self.server:
                self.server.stop()
                
            self.loaded = False
            import gc
            gc.collect()
            logger.info(f"Model {self.model_name} unloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error unloading model {self.model_name}: {str(e)}")
            return False
