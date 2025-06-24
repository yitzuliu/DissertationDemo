"""
YOLO8 Model Implementation

This module implements the BaseVisionModel interface for the YOLO8 object detection model.
It handles model loading, image preprocessing, and object detection.
"""

import time
import json
import numpy as np
import os
from typing import Dict, Any, Optional, Union, List
from PIL import Image
import logging
from pathlib import Path

from .base_model import BaseVisionModel
from src.backend.utils.image_processing import preprocess_for_model

logger = logging.getLogger(__name__)

class YOLO8Model(BaseVisionModel):
    """
    Implementation of the YOLO8 object detection model.
    """
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the YOLO8 model.
        
        Args:
            model_name: The name of the model
            config: A dictionary containing model configuration
        """
        super().__init__(model_name, config)
        
        # Default to yolov8s.pt if not specified
        self.model_variant = config.get("model_variant", "yolov8s.pt")
        self.confidence_threshold = config.get("confidence_threshold", 0.25)
        self.model_path = config.get("model_path", "")
        
        # Ensure the model file exists, or use the one in the yolo8 folder
        if not self.model_path or not os.path.exists(self.model_path):
            base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            yolo_dir = base_dir / "yolo8"
            self.model_path = str(yolo_dir / self.model_variant)
            
            # If still not found, we'll let the YOLO library download it
            if not os.path.exists(self.model_path):
                self.model_path = self.model_variant
                logger.info(f"Model file {self.model_variant} not found locally, will be downloaded.")
    
    def load_model(self) -> bool:
        """
        Load the YOLO8 model into memory.
        
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            # Import here to avoid requiring the package for the entire project
            from ultralytics import YOLO
            
            start_time = time.time()
            logger.info(f"Loading YOLO8 model {self.model_path}...")
            
            self.model = YOLO(self.model_path)
            self.loaded = True
            self.load_time = time.time() - start_time
            
            logger.info(f"Model {self.model_name} loaded successfully in {self.load_time:.2f} seconds.")
            return True
        except Exception as e:
            logger.error(f"Error loading YOLO8 model: {str(e)}")
            self.loaded = False
            return False
    
    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> np.ndarray:
        """
        Preprocess the input image for the model.
        
        Args:
            image: The input image, either as PIL Image or numpy array
            
        Returns:
            The preprocessed image in the format expected by the model (numpy array)
        """
        # YOLO expects a numpy array in BGR format
        return preprocess_for_model(
            image=image,
            model_type="yolo",
            config=self.config,
            return_format="cv2"
        )
    
    def predict(self, 
                image: Union[Image.Image, np.ndarray], 
                prompt: str, 
                options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform object detection on the image.
        
        Args:
            image: The input image
            prompt: The text prompt (ignored for YOLO, but included for interface compatibility)
            options: Additional model-specific options
            
        Returns:
            A dictionary containing the detection results
        """
        if not self.loaded:
            if not self.load_model():
                return {"error": "Model failed to load"}
        
        try:
            start_time = time.time()
            
            # Apply default options if not provided
            if options is None:
                options = {}
            
            # Get confidence threshold from options or use default
            conf = options.get("confidence_threshold", self.confidence_threshold)
            
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Run detection
            results = self.model(processed_image, conf=conf)
            
            # Extract and format results
            raw_response = self._extract_detections(results)
            
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            # Format response
            response = self.format_response(raw_response)
            response["processing_time"] = processing_time
            
            return response
            
        except Exception as e:
            logger.error(f"Error during prediction with {self.model_name}: {str(e)}")
            return {
                "error": f"Failed to analyze image with {self.model_name}",
                "details": str(e)
            }
    
    def _extract_detections(self, results):
        """
        Extract detection information from YOLO results.
        
        Args:
            results: The results from the YOLO model
            
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        # Process first image results (assume single image)
        for box in results[0].boxes:
            # Get the coordinates of the bounding box (x1, y1, x2, y2)
            coords = box.xyxy[0].tolist()
            
            # Get the class ID and the class name
            class_id = int(box.cls[0])
            class_name = results[0].names[class_id]
            
            # Get the confidence score
            confidence = float(box.conf[0])
            
            detection = {
                "class": class_name,
                "confidence": round(confidence, 3),
                "bbox": {
                    "x1": round(coords[0], 2),
                    "y1": round(coords[1], 2),
                    "x2": round(coords[2], 2),
                    "y2": round(coords[3], 2),
                }
            }
            detections.append(detection)
        
        return detections
    
    def format_response(self, raw_response: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format the raw model response into a standardized format.
        
        Args:
            raw_response: The raw detections from the model
            
        Returns:
            A standardized response dictionary
        """
        # Group detections by class
        objects_by_class = {}
        for det in raw_response:
            class_name = det["class"]
            if class_name not in objects_by_class:
                objects_by_class[class_name] = []
            objects_by_class[class_name].append(det)
        
        # Construct standardized response
        response = {
            "success": True,
            "response": {
                "objects_detected": len(raw_response),
                "unique_classes": len(objects_by_class),
                "class_counts": {cls: len(objs) for cls, objs in objects_by_class.items()},
                "detections": raw_response
            },
            "raw_detections": raw_response
        }
        
        return response
