#!/usr/bin/env python3
"""
AI Manual Assistant Visual Logger

Provides VLM visual processing related logging functionality, including:
- Backend receive logging
- Image processing procedures and results
- RAG system data transfer
- State tracker integration
"""

import time
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
try:
    from .log_manager import get_log_manager, LogManager, LogType
except ImportError:
    from log_manager import get_log_manager, LogManager, LogType


class VisualLogger:
    """
    Visual Logger
    
    Responsible for recording VLM visual processing related events, including:
    - Backend receive processing
    - Image processing procedures
    - RAG matching process
    - State update process
    """
    
    def __init__(self):
        """Initialize visual logger"""
        self.log_manager = get_log_manager()
        
    def log_backend_receive(self, observation_id: str, request_id: str, 
                           request_data: Dict[str, Any]):
        """
        Log backend receive VLM request
        
        Args:
            observation_id: Observation ID
            request_id: Request ID
            request_data: Request data
        """
        # Safely process image data, avoid logging complete base64
        safe_request_data = self._sanitize_request_data(request_data)
        
        message = (f"[BACKEND_RECEIVE] observation_id={observation_id} "
                  f"request_id={request_id} "
                  f"data={json.dumps(safe_request_data, ensure_ascii=False)}")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_image_processing_start(self, observation_id: str, request_id: str,
                                  image_count: int, model: str):
        """
        Log image processing start
        
        Args:
            observation_id: Observation ID
            request_id: Request ID
            image_count: Image count
            model: Model used
        """
        message = (f"[IMAGE_PROCESSING_START] observation_id={observation_id} "
                  f"request_id={request_id} image_count={image_count} "
                  f"model={model}")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_image_processing_result(self, observation_id: str, request_id: str,
                                   processing_time: float, success: bool,
                                   details: Optional[Dict[str, Any]] = None):
        """
        Log image processing result
        
        Args:
            observation_id: Observation ID
            request_id: Request ID
            processing_time: Processing time (seconds)
            success: Whether successful
            details: Processing details
        """
        status = "SUCCESS" if success else "FAILED"
        message_parts = [
            f"[IMAGE_PROCESSING_RESULT] observation_id={observation_id}",
            f"request_id={request_id}",
            f"status={status}",
            f"processing_time={processing_time:.3f}s"
        ]
        
        if details:
            for key, value in details.items():
                message_parts.append(f"{key}={value}")
        
        message = " ".join(message_parts)
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_vlm_request(self, observation_id: str, request_id: str,
                       model: str, prompt_length: int, image_count: int):
        """
        Log VLM request
        
        Args:
            observation_id: Observation ID
            request_id: Request ID
            model: Model name
            prompt_length: Prompt length
            image_count: Image count
        """
        message = (f"[VLM_REQUEST] observation_id={observation_id} "
                  f"request_id={request_id} model={model} "
                  f"prompt_length={prompt_length} image_count={image_count}")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_vlm_response(self, observation_id: str, request_id: str,
                        response_length: int, processing_time: float,
                        success: bool, model: str):
        """
        Log VLM response
        
        Args:
            observation_id: Observation ID
            request_id: Request ID
            response_length: Response length
            processing_time: Processing time (seconds)
            success: Whether successful
            model: Model name
        """
        status = "SUCCESS" if success else "FAILED"
        message = (f"[VLM_RESPONSE] observation_id={observation_id} "
                  f"request_id={request_id} model={model} status={status} "
                  f"response_length={response_length} "
                  f"processing_time={processing_time:.3f}s")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_rag_data_transfer(self, observation_id: str, vlm_text: str,
                             transfer_success: bool):
        """
        Log RAG data transfer
        
        Args:
            observation_id: Observation ID
            vlm_text: VLM response text
            transfer_success: Whether transfer successful
        """
        status = "SUCCESS" if transfer_success else "FAILED"
        # Truncate VLM text for logging
        truncated_text = vlm_text[:100] + "..." if len(vlm_text) > 100 else vlm_text
        
        message = (f"[RAG_DATA_TRANSFER] observation_id={observation_id} "
                  f"status={status} vlm_text=\"{truncated_text}\"")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_state_tracker_integration(self, observation_id: str, 
                                     state_updated: bool, 
                                     processing_time: Optional[float] = None):
        """
        Log state tracker integration
        
        Args:
            observation_id: Observation ID
            state_updated: Whether state updated
            processing_time: Processing time (seconds)
        """
        status = "UPDATED" if state_updated else "NO_CHANGE"
        message_parts = [
            f"[STATE_TRACKER_INTEGRATION] observation_id={observation_id}",
            f"state_updated={state_updated}"
        ]
        
        if processing_time is not None:
            message_parts.append(f"processing_time={processing_time:.3f}s")
        
        message = " ".join(message_parts)
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_error(self, observation_id: str, request_id: str, 
                  error_type: str, error_message: str, 
                  context: Optional[str] = None):
        """
        Log error
        
        Args:
            observation_id: Observation ID
            request_id: Request ID
            error_type: Error type
            error_message: Error message
            context: Error context
        """
        message_parts = [
            f"[VISUAL_ERROR] observation_id={observation_id}",
            f"request_id={request_id}",
            f"error_type={error_type}",
            f"error_message=\"{error_message}\""
        ]
        
        if context:
            message_parts.append(f"context={context}")
        
        message = " ".join(message_parts)
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.error(message)
    
    def log_performance_metric(self, observation_id: str, metric_name: str,
                              value: float, unit: str = ""):
        """
        Log performance metric
        
        Args:
            observation_id: Observation ID
            metric_name: Metric name
            value: Metric value
            unit: Metric unit
        """
        unit_str = f" {unit}" if unit else ""
        message = (f"[VISUAL_PERFORMANCE] observation_id={observation_id} "
                  f"metric={metric_name} value={value}{unit_str}")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def _sanitize_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize request data for logging
        
        Args:
            request_data: Original request data
            
        Returns:
            Sanitized request data
        """
        sanitized = request_data.copy()
        
        # Remove or truncate sensitive data
        if 'messages' in sanitized:
            sanitized_messages = []
            for message in sanitized['messages']:
                if isinstance(message, dict) and 'content' in message:
                    content = message['content']
                    if isinstance(content, list):
                        # Handle multimodal content
                        sanitized_content = []
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'image_url':
                                # Truncate image URL
                                image_url = item.get('image_url', {})
                                if isinstance(image_url, dict) and 'url' in image_url:
                                    url = image_url['url']
                                    if url.startswith('data:image'):
                                        # Truncate base64 data
                                        truncated_url = url[:50] + "...[TRUNCATED]"
                                        sanitized_content.append({
                                            'type': 'image_url',
                                            'image_url': {'url': truncated_url}
                                        })
                                    else:
                                        sanitized_content.append(item)
                                else:
                                    sanitized_content.append(item)
                            else:
                                sanitized_content.append(item)
                        sanitized_messages.append({
                            'role': message.get('role', 'unknown'),
                            'content': sanitized_content
                        })
                    else:
                        # Handle text content
                        sanitized_messages.append(message)
                else:
                    sanitized_messages.append(message)
            sanitized['messages'] = sanitized_messages
        
        return sanitized


# Global instance
_visual_logger_instance: Optional[VisualLogger] = None


def get_visual_logger() -> VisualLogger:
    """Get global visual logger instance"""
    global _visual_logger_instance
    if _visual_logger_instance is None:
        _visual_logger_instance = VisualLogger()
    return _visual_logger_instance


# Convenience functions
def log_backend_receive(observation_id: str, request_id: str, request_data: Dict[str, Any]):
    """Convenient backend receive logging"""
    logger = get_visual_logger()
    logger.log_backend_receive(observation_id, request_id, request_data)


def log_image_processing(observation_id: str, request_id: str, 
                        processing_time: float, success: bool, **kwargs):
    """Convenient image processing logging"""
    logger = get_visual_logger()
    logger.log_image_processing_result(observation_id, request_id, processing_time, success, kwargs)


def log_vlm_interaction(observation_id: str, request_id: str, model: str,
                       request_time: float, response_time: float, success: bool):
    """Convenient VLM interaction logging"""
    logger = get_visual_logger()
    logger.log_vlm_response(observation_id, request_id, 0, response_time, success, model)


def log_visual_error(observation_id: str, request_id: str, error: Exception, context: str = ""):
    """Convenient visual error logging"""
    logger = get_visual_logger()
    logger.log_error(observation_id, request_id, type(error).__name__, str(error), context)