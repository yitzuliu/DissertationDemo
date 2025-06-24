"""
Phi-3 Vision Model Implementation

This module implements the BaseVisionModel interface for the Phi-3 Vision model
from Microsoft. It handles model loading, image preprocessing, and prediction.
"""

import time
import json
import torch
import numpy as np
from typing import Dict, Any, Optional, Union
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
import logging

from ..base_model import BaseVisionModel
from src.backend.utils.image_processing import preprocess_for_model, enhance_image_clahe

logger = logging.getLogger(__name__)

class Phi3VisionModel(BaseVisionModel):
    """
    Implementation of the Phi-3 Vision model from Microsoft.
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the Phi-3 Vision model.
        
        Args:
            model_name: The name of the model
            config: A dictionary containing model configuration
        """
        super().__init__(model_name, config)
        self.model_id = config.get("model_id", "microsoft/Phi-3-vision-128k-instruct")
        
        # Configure device
        if torch.backends.mps.is_available() and config.get("use_mps", True):
            self.device = "mps"
            self.torch_dtype = torch.bfloat16
            logger.info(f"{model_name} configured to use Apple Metal (MPS) GPU.")
        elif torch.cuda.is_available() and config.get("use_cuda", True):
            self.device = "cuda"
            self.torch_dtype = torch.bfloat16
            logger.info(f"{model_name} configured to use CUDA GPU.")
        else:
            self.device = "cpu"
            self.torch_dtype = torch.float32
            logger.info(f"{model_name} configured to use CPU.")
    
    def load_model(self) -> bool:
        """
        Load the Phi-3 Vision model into memory.
        
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            start_time = time.time()
            logger.info(f"Loading model '{self.model_id}' into memory...")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map=self.device,
                trust_remote_code=True,
                torch_dtype=self.torch_dtype
            )
            
            self.processor = AutoProcessor.from_pretrained(
                self.model_id,
                trust_remote_code=True
            )
            
            self.loaded = True
            self.load_time = time.time() - start_time
            
            logger.info(f"Model {self.model_name} loaded successfully in {self.load_time:.2f} seconds.")
            return True
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            self.loaded = False
            return False
    
    def enhance_image(self, image: Image.Image) -> Image.Image:
        """
        Applies CLAHE enhancement to an image.
        
        Args:
            image: PIL Image to enhance
            
        Returns:
            Enhanced PIL Image
        """
        try:
            return enhance_image_clahe(image)
        except Exception as e:
            logger.error(f"Error during image enhancement: {str(e)}")
            return image
    
    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """
        Preprocess the input image for the model.
        
        Args:
            image: The input image, either as PIL Image or numpy array
            
        Returns:
            The preprocessed image in the format expected by the model
        """
        # Use centralized image preprocessing utility
        return preprocess_for_model(
            image=image,
            model_type="phi3",
            config=self.config,
            return_format="pil"
        )
    
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
                return {"error": "Model failed to load"}
        
        try:
            start_time = time.time()
            
            # Apply default options if not provided
            if options is None:
                options = {}
                
            # Get generation parameters
            max_new_tokens = options.get("max_new_tokens", 500)
            temperature = options.get("temperature", 0.0)
            do_sample = options.get("do_sample", False)
            
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Format the messages for the model
            messages = [
                {"role": "user", "content": f"<|image_1|>\n{prompt}"},
            ]
            prompt_for_model = self.processor.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            # Prepare inputs
            inputs = self.processor(
                prompt_for_model, [processed_image], return_tensors="pt"
            ).to(self.device)
            
            # Generate response
            generation_args = {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "do_sample": do_sample,
            }
            
            generate_ids = self.model.generate(
                **inputs, 
                eos_token_id=self.processor.tokenizer.eos_token_id, 
                **generation_args
            )
            
            # Extract generated text
            generate_ids = generate_ids[:, inputs['input_ids'].shape[1]:]
            raw_response = self.processor.batch_decode(
                generate_ids, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            # Format the response
            response = self.format_response(raw_response)
            response["processing_time"] = processing_time
            
            return response
            
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
            raw_response: The raw output from the model
            
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
