"""
Base Vision-Language Model Interface

This module provides the abstract base class that all vision-language models
in the AI Manual Assistant project must implement. It defines a standard interface
for model initialization, prediction, and management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from PIL import Image
import numpy as np
import logging
import time
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseVisionModel(ABC):
    """
    Abstract base class for all vision-language models in the system.
    
    This class defines the standard interface that all model implementations
    must adhere to, ensuring consistent behavior across different model types.
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the model with name and configuration.
        
        Args:
            model_name: The name of the model
            config: A dictionary containing model configuration
        """
        self.model_name = model_name
        self.config = config
        self.model = None
        self.processor = None
        self.loaded = False
        self.load_time = 0
        self.device = 'cpu'  # Default device
        self._stats = {
            'total_requests': 0,
            'total_processing_time': 0,
            'avg_processing_time': 0,
            'last_processing_time': 0
        }
    
    @abstractmethod
    def load_model(self) -> bool:
        """
        Load the model into memory.
        
        Returns:
            True if loading was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> Any:
        """
        Preprocess the input image for the model.
        
        Args:
            image: The input image, either as PIL Image or numpy array
            
        Returns:
            The preprocessed image in the format expected by the model
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def format_response(self, raw_response: Any) -> Dict[str, Any]:
        """
        Format the raw model response into a standardized format.
        
        Args:
            raw_response: The raw output from the model
            
        Returns:
            A standardized response dictionary
        """
        pass
    
    def unload_model(self) -> bool:
        """
        Unload the model from memory to free resources.
        
        Returns:
            True if unloading was successful, False otherwise
        """
        try:
            self.model = None
            self.processor = None
            self.loaded = False
            import gc
            gc.collect()
            logger.info(f"Model {self.model_name} unloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error unloading model {self.model_name}: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            A dictionary containing model information
        """
        return {
            'name': self.model_name,
            'loaded': self.loaded,
            'load_time': self.load_time,
            'device': self.device,
            'stats': self._stats,
            'config': {k: v for k, v in self.config.items() if k != 'server'}
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the model.
        
        Returns:
            A dictionary containing health information
        """
        return {
            'status': 'ok' if self.loaded else 'not_loaded',
            'name': self.model_name,
            'device': self.device,
            'loaded': self.loaded,
            'requests_processed': self._stats['total_requests'],
            'avg_processing_time': self._stats['avg_processing_time']
        }
    
    def _update_stats(self, processing_time: float) -> None:
        """
        Update model processing statistics.
        
        Args:
            processing_time: The time taken for processing the last request
        """
        self._stats['total_requests'] += 1
        self._stats['total_processing_time'] += processing_time
        self._stats['avg_processing_time'] = float(
            self._stats['total_processing_time'] / self._stats['total_requests']
        )
        self._stats['last_processing_time'] = processing_time


class VLMFactory:
    """
    Factory class for creating model instances based on model type.
    """
    
    @staticmethod
    def create_model(model_name: str, config: Dict[str, Any]) -> BaseVisionModel:
        """
        Create and return an instance of the appropriate model class.
        
        Args:
            model_name: The name of the model to create
            config: Model configuration dictionary
            
        Returns:
            An instance of a class that implements BaseVisionModel
            
        Raises:
            ValueError: If the model type is not supported
        """
        # Import implementations here to avoid circular imports
        from .phi3_vision.phi3_vision_model import Phi3VisionModel
        from .smolvlm.smolvlm_model import SmolVLMModel
        from .yolo8.yolo8_model import YOLO8Model
        from .LLava.llava_model import LLaVAModel
        from .moondream2.moondream2_optimized import OptimizedMoondream2Model
        
        model_type = model_name.lower()
        
        if "phi3" in model_type:
            return Phi3VisionModel(model_name, config)
        elif "smolvlm" in model_type:
            return SmolVLMModel(model_name, config)
        elif "yolo" in model_type:
            return YOLO8Model(model_name, config)
        elif "llava" in model_type:
            return LLaVAModel(model_name, config)
        elif "moondream" in model_type:
            return OptimizedMoondream2Model(model_name, config)
        else:
            raise ValueError(f"Unsupported model type: {model_name}")
