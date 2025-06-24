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
from PIL import Image
import logging
import io
import subprocess
import sys
import os
import signal
import threading
from pathlib import Path

from .base_model import BaseVisionModel
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
    
    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> str:
        """
        Preprocess the input image for the model.
        
        Convert the image to a base64 encoded string for the API.
        
        Args:
            image: The input image, either as PIL Image or numpy array
            
        Returns:
            Base64 encoded image string
        """
        try:
            # Process the image to get a PIL image first
            pil_image = preprocess_for_model(
                image=image,
                model_type="smolvlm",
                config=self.config,
                return_format="pil"
            )
            
            # Convert to JPEG bytes
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()
            
            # Encode to base64
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
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
