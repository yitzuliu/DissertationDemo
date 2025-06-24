"""
LLaVA Model Implementation

This module implements the BaseVisionModel interface for the LLaVA model
using Ollama as the backend service. It handles model loading, image preprocessing,
and prediction.
"""

import time
import json
import numpy as np
from typing import Dict, Any, Optional, Union
from PIL import Image
import logging

from .base_model import BaseVisionModel
from src.backend.utils.image_processing import preprocess_for_model

logger = logging.getLogger(__name__)

class LLaVAModel(BaseVisionModel):
    """
    Implementation of the LLaVA model using Ollama as the backend.
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the LLaVA model.
        
        Args:
            model_name: The name of the model
            config: A dictionary containing model configuration
        """
        super().__init__(model_name, config)
        
        # Get Ollama model name from config or use default
        self.ollama_model = config.get("ollama_model", "llava:7b")
        self.ollama_url = config.get("ollama_url", "http://localhost:11434")
        self.timeout = config.get("timeout", 60)  # Default timeout in seconds
    
    def load_model(self) -> bool:
        """
        Check if Ollama service is available with the LLaVA model.
        
        Since Ollama manages the model, we just verify the service is running
        and the model is available.
        
        Returns:
            True if the service is available and model is ready, False otherwise
        """
        try:
            # Import here to avoid requiring the package for the entire project
            import ollama
            
            start_time = time.time()
            logger.info(f"Checking Ollama service and LLaVA model {self.ollama_model} availability...")
            
            # Configure Ollama client
            if self.ollama_url:
                ollama.set_host(self.ollama_url)
            
            # Check if model exists by listing models and looking for our model
            models = ollama.list()
            model_exists = any(model["name"] == self.ollama_model for model in models.get("models", []))
            
            if not model_exists:
                logger.warning(f"Model {self.ollama_model} not found in Ollama. Attempting to pull...")
                ollama.pull(self.ollama_model)
            
            self.loaded = True
            self.load_time = time.time() - start_time
            
            # We'll use the ollama module directly, no need to store a model instance
            logger.info(f"LLaVA model {self.ollama_model} is available via Ollama service.")
            return True
            
        except Exception as e:
            logger.error(f"Error checking Ollama service/LLaVA model: {str(e)}")
            self.loaded = False
            return False
    
    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> bytes:
        """
        Preprocess the input image for the model.
        
        Args:
            image: The input image, either as PIL Image or numpy array
            
        Returns:
            The preprocessed image as bytes, ready for the Ollama API
        """
        try:
            # Use centralized image preprocessing utility with bytes output for Ollama
            return preprocess_for_model(
                image=image,
                model_type="llava",
                config=self.config,
                return_format="bytes"
            )
        except Exception as e:
            logger.error(f"Error preprocessing image for LLaVA: {str(e)}")
            # If all fails, try to encode the original image
            if isinstance(image, Image.Image):
                import io
                buffer = io.BytesIO()
                image.save(buffer, format="JPEG")
                return buffer.getvalue()
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
                return {"error": "Model service is not available"}
        
        try:
            # Import here to avoid requiring the package for the entire project
            import ollama
            
            start_time = time.time()
            
            # Apply default options if not provided
            if options is None:
                options = {}
                
            # Get generation parameters from options
            temperature = options.get("temperature", 0.0)
            num_predict = options.get("max_tokens", 512)
            
            # Configure Ollama client if URL is set
            if self.ollama_url:
                ollama.set_host(self.ollama_url)
            
            # Preprocess the image
            image_bytes = self.preprocess_image(image)
            
            # Call the Ollama chat API
            response = ollama.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [image_bytes]
                    }
                ],
                options={
                    'temperature': temperature,
                    'num_predict': num_predict
                }
            )
            
            # Extract the text content from the response
            raw_response = response['message']['content']
            
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            # Format the response
            response_dict = self.format_response(raw_response)
            response_dict["processing_time"] = processing_time
            
            return response_dict
            
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
