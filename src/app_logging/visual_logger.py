#!/usr/bin/env python3
"""
AI Manual Assistant Visual Logger

Provides visual processing logging functionality for VLM operations, image processing, and RAG integration.
"""

import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
try:
    from .log_manager import get_log_manager, LogManager, LogType
except ImportError:
    # Handle standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.app_logging.log_manager import get_log_manager, LogManager, LogType


class VisualLogger:
    """
    Visual Logger for AI Manual Assistant
    
    Handles visual processing logging including image capture, VLM processing,
    RAG matching, and state tracker integration.
    """
    
    def __init__(self):
        """Initialize visual logger"""
        self.log_manager = get_log_manager()
        self.logger = self.log_manager.get_logger(LogType.VISUAL)
    
    def log_backend_receive(self, observation_id: str, request_id: str, request_data: Dict[str, Any]):
        """
        Log backend reception of visual data
        
        Args:
            observation_id: Observation identifier
            request_id: Request identifier
            request_data: Request data received by backend
        """
        self.logger.info(f"[BACKEND_RECEIVE] observation_id={observation_id}, request_id={request_id}, request_data={request_data}")
    
    def log_image_processing_start(self, observation_id: str, request_id: str, image_count: int, model: str):
        """
        Log start of image processing
        
        Args:
            observation_id: Observation identifier
            request_id: Request identifier
            image_count: Number of images to process
            model: Model name for processing
        """
        self.logger.info(f"[IMAGE_PROCESSING_START] observation_id={observation_id}, request_id={request_id}, image_count={image_count}, model={model}")
    
    def log_image_processing_result(self, observation_id: str, request_id: str, processing_time: float, 
                                  success: bool, metadata: Dict[str, Any]):
        """
        Log image processing result
        
        Args:
            observation_id: Observation identifier
            request_id: Request identifier
            processing_time: Processing time in seconds
            success: Whether processing was successful
            metadata: Processing metadata
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"[IMAGE_PROCESSING_RESULT] observation_id={observation_id}, request_id={request_id}, processing_time={processing_time}s, status={status}, metadata={metadata}")
        
        # Log performance metric
        self.log_performance_metric(observation_id, "image_processing_time", processing_time, "s")
    
    def log_vlm_request(self, observation_id: str, request_id: str, model: str, token_count: int, image_count: int):
        """
        Log VLM request
        
        Args:
            observation_id: Observation identifier
            request_id: Request identifier
            model: VLM model name
            token_count: Number of tokens in request
            image_count: Number of images in request
        """
        self.logger.info(f"[VLM_REQUEST] observation_id={observation_id}, request_id={request_id}, model={model}, token_count={token_count}, image_count={image_count}")
    
    def log_vlm_response(self, observation_id: str, request_id: str, response_length: int, 
                        processing_time: float, success: bool, model: str):
        """
        Log VLM response
        
        Args:
            observation_id: Observation identifier
            request_id: Request identifier
            response_length: Length of response
            processing_time: Processing time in seconds
            success: Whether processing was successful
            model: VLM model name
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"[VLM_RESPONSE] observation_id={observation_id}, request_id={request_id}, response_length={response_length}, processing_time={processing_time}s, status={status}, model={model}")
        
        # Log performance metric
        self.log_performance_metric(observation_id, "vlm_processing_time", processing_time, "s")
    
    def log_rag_data_transfer(self, observation_id: str, vlm_response: str, success: bool):
        """
        Log RAG data transfer
        
        Args:
            observation_id: Observation identifier
            vlm_response: VLM response text
            success: Whether transfer was successful
        """
        status = "SUCCESS" if success else "FAILED"
        # Truncate response for logging if too long
        response_preview = vlm_response[:100] + "..." if len(vlm_response) > 100 else vlm_response
        self.logger.info(f"[RAG_DATA_TRANSFER] observation_id={observation_id}, vlm_response=\"{response_preview}\", status={status}")
    
    def log_state_tracker_integration(self, observation_id: str, success: bool, processing_time: float):
        """
        Log state tracker integration
        
        Args:
            observation_id: Observation identifier
            success: Whether integration was successful
            processing_time: Processing time in seconds
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"[STATE_TRACKER_INTEGRATION] observation_id={observation_id}, status={status}, processing_time={processing_time}s")
        
        # Log performance metric
        self.log_performance_metric(observation_id, "state_tracker_time", processing_time, "s")
    
    def log_error(self, observation_id: str, request_id: str, error_type: str, message: str, context: str):
        """
        Log visual processing error
        
        Args:
            observation_id: Observation identifier
            request_id: Request identifier
            error_type: Type of error
            message: Error message
            context: Error context
        """
        self.logger.error(f"[VISUAL_ERROR] observation_id={observation_id}, request_id={request_id}, error_type={error_type}, message=\"{message}\", context={context}")
    
    def log_performance_metric(self, observation_id: str, metric: str, value: float, unit: str):
        """
        Log performance metric for visual processing
        
        Args:
            observation_id: Observation identifier
            metric: Metric name
            value: Metric value
            unit: Unit of measurement
        """
        self.logger.info(f"[VISUAL_PERFORMANCE] observation_id={observation_id}, metric={metric}, value={value}, unit={unit}")


# Global instance
_visual_logger = None


def get_visual_logger() -> VisualLogger:
    """Get global visual logger instance"""
    global _visual_logger
    if _visual_logger is None:
        _visual_logger = VisualLogger()
    return _visual_logger


def initialize_visual_logger() -> VisualLogger:
    """Initialize global visual logger"""
    global _visual_logger
    _visual_logger = VisualLogger()
    return _visual_logger


# Convenience functions
def log_backend_receive(observation_id: str, request_id: str, request_data: Dict[str, Any]):
    """Log backend reception"""
    logger = get_visual_logger()
    logger.log_backend_receive(observation_id, request_id, request_data)


def log_image_processing_start(observation_id: str, request_id: str, image_count: int, model: str):
    """Log image processing start"""
    logger = get_visual_logger()
    logger.log_image_processing_start(observation_id, request_id, image_count, model)


def log_image_processing_result(observation_id: str, request_id: str, processing_time: float, 
                              success: bool, metadata: Dict[str, Any]):
    """Log image processing result"""
    logger = get_visual_logger()
    logger.log_image_processing_result(observation_id, request_id, processing_time, success, metadata)


def log_vlm_request(observation_id: str, request_id: str, model: str, token_count: int, image_count: int):
    """Log VLM request"""
    logger = get_visual_logger()
    logger.log_vlm_request(observation_id, request_id, model, token_count, image_count)


def log_vlm_response(observation_id: str, request_id: str, response_length: int, 
                    processing_time: float, success: bool, model: str):
    """Log VLM response"""
    logger = get_visual_logger()
    logger.log_vlm_response(observation_id, request_id, response_length, processing_time, success, model)


def log_rag_data_transfer(observation_id: str, vlm_response: str, success: bool):
    """Log RAG data transfer"""
    logger = get_visual_logger()
    logger.log_rag_data_transfer(observation_id, vlm_response, success)


def log_state_tracker_integration(observation_id: str, success: bool, processing_time: float):
    """Log state tracker integration"""
    logger = get_visual_logger()
    logger.log_state_tracker_integration(observation_id, success, processing_time)


def log_visual_error(observation_id: str, request_id: str, error_type: str, message: str, context: str):
    """Log visual processing error"""
    logger = get_visual_logger()
    logger.log_error(observation_id, request_id, error_type, message, context)


def log_visual_performance(observation_id: str, metric: str, value: float, unit: str):
    """Log visual performance metric"""
    logger = get_visual_logger()
    logger.log_performance_metric(observation_id, metric, value, unit)