"""
Configuration Management for VLM Fallback System

Manages all configuration parameters for the fallback system,
including decision thresholds, VLM client settings, and system behavior.
"""

import json
import logging
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class VLMFallbackConfig:
    """
    Configuration for VLM Fallback System.
    
    All configuration parameters with sensible defaults.
    """
    
    # Decision Engine Configuration
    confidence_threshold: float = 0.40
    enable_unknown_query_fallback: bool = True
    enable_no_state_fallback: bool = True
    
    # VLM Client Configuration
    model_server_url: str = "http://localhost:8080"
    vlm_timeout: int = 30
    max_retries: int = 2
    max_tokens: int = 500
    temperature: float = 0.7
    
    # Prompt Configuration
    fallback_prompt_template: str = """You are a helpful AI assistant. Please answer the user's question directly and helpfully.

User Question: {query}

Please provide a clear, accurate, and helpful response. Focus on:
- Being informative and accurate
- Providing practical guidance when appropriate
- Being concise but complete
- Using a friendly and supportive tone

Answer:"""
    
    # Logging Configuration
    enable_decision_logs: bool = True
    enable_vlm_logs: bool = True
    enable_performance_logs: bool = True
    
    # Performance Configuration
    max_concurrent_requests: int = 10
    request_queue_size: int = 100
    
    # Image Fallback Configuration
    enable_image_fallback: bool = True
    image_capture: Dict = None
    image_processing: Dict = None
    fallback_prompts: Dict = None
    
    def __post_init__(self):
        """Initialize default image-related configurations"""
        if self.image_capture is None:
            self.image_capture = {
                "enable_camera_capture": True,
                "enable_state_tracker_capture": True,
                "enable_image_cache": True,
                "cache_duration_seconds": 300,
                "max_image_size_bytes": 1048576
            }
        
        if self.image_processing is None:
            self.image_processing = {
                "default_model": "smolvlm",
                "quality": 85,
                "max_size": 1024,
                "format": "jpeg"
            }
        
        if self.fallback_prompts is None:
            self.fallback_prompts = {
                "image_fallback_template": """You are a helpful AI assistant with visual capabilities. Please analyze the provided image and answer the user's question.

User Question: {query}

Image Format: {image_format}
Image Size: {image_size} bytes

Please provide a clear, accurate, and helpful response based on both the image content and the user's question. Focus on:
- Visual analysis of the image
- Answering the specific question
- Providing practical guidance when appropriate
- Being concise but complete
- Using a friendly and supportive tone

Answer:"""
            }
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'VLMFallbackConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            VLMFallbackConfig: Configuration instance
        """
        config = cls()
        
        # Extract VLM fallback configuration
        fallback_config = config_dict.get('vlm_fallback', {})
        
        # Decision engine configuration
        decision_config = fallback_config.get('decision_engine', {})
        config.confidence_threshold = decision_config.get('confidence_threshold', config.confidence_threshold)
        config.enable_unknown_query_fallback = decision_config.get('enable_unknown_query_fallback', config.enable_unknown_query_fallback)
        config.enable_no_state_fallback = decision_config.get('enable_no_state_fallback', config.enable_no_state_fallback)
        
        # VLM client configuration
        vlm_config = fallback_config.get('vlm_client', {})
        config.model_server_url = vlm_config.get('model_server_url', config.model_server_url)
        config.vlm_timeout = vlm_config.get('timeout', config.vlm_timeout)
        config.max_retries = vlm_config.get('max_retries', config.max_retries)
        config.max_tokens = vlm_config.get('max_tokens', config.max_tokens)
        config.temperature = vlm_config.get('temperature', config.temperature)
        
        # Prompt configuration
        prompts_config = fallback_config.get('prompts', {})
        config.fallback_prompt_template = prompts_config.get('fallback_template', config.fallback_prompt_template)
        
        # Logging configuration
        logging_config = fallback_config.get('logging', {})
        config.enable_decision_logs = logging_config.get('enable_decision_logs', config.enable_decision_logs)
        config.enable_vlm_logs = logging_config.get('enable_vlm_logs', config.enable_vlm_logs)
        config.enable_performance_logs = logging_config.get('enable_performance_logs', config.enable_performance_logs)
        
        # Performance configuration
        performance_config = fallback_config.get('performance', {})
        config.max_concurrent_requests = performance_config.get('max_concurrent_requests', config.max_concurrent_requests)
        config.request_queue_size = performance_config.get('request_queue_size', config.request_queue_size)
        
        # Image fallback configuration
        config.enable_image_fallback = fallback_config.get('enable_image_fallback', config.enable_image_fallback)
        config.image_capture = fallback_config.get('image_capture', config.image_capture)
        config.image_processing = fallback_config.get('image_processing', config.image_processing)
        config.fallback_prompts = fallback_config.get('fallback_prompts', config.fallback_prompts)
        
        return config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'VLMFallbackConfig':
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            VLMFallbackConfig: Configuration instance
        """
        try:
            config_file = Path(config_path)
            
            if not config_file.exists():
                logger.warning(f"Configuration file not found: {config_path}, using defaults")
                return cls()
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            logger.info(f"Configuration loaded from: {config_path}")
            return cls.from_dict(config_dict)
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return cls()
    
    def to_dict(self) -> Dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict: Configuration dictionary
        """
        return {
            "vlm_fallback": {
                "decision_engine": {
                    "confidence_threshold": self.confidence_threshold,
                    "enable_unknown_query_fallback": self.enable_unknown_query_fallback,
                    "enable_no_state_fallback": self.enable_no_state_fallback
                },
                "vlm_client": {
                    "model_server_url": self.model_server_url,
                    "timeout": self.vlm_timeout,
                    "max_retries": self.max_retries,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                },
                "prompts": {
                    "fallback_template": self.fallback_prompt_template
                },
                "logging": {
                    "enable_decision_logs": self.enable_decision_logs,
                    "enable_vlm_logs": self.enable_vlm_logs,
                    "enable_performance_logs": self.enable_performance_logs
                },
                "performance": {
                    "max_concurrent_requests": self.max_concurrent_requests,
                    "request_queue_size": self.request_queue_size
                },
                "image_fallback": {
                    "enable_image_fallback": self.enable_image_fallback,
                    "image_capture": self.image_capture,
                    "image_processing": self.image_processing,
                    "fallback_prompts": self.fallback_prompts
                }
            }
        }
    
    def save_to_file(self, config_path: str):
        """
        Save configuration to JSON file.
        
        Args:
            config_path: Path to save configuration file
        """
        try:
            config_file = Path(config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to: {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
    
    def validate(self) -> bool:
        """
        Validate configuration parameters.
        
        Returns:
            bool: True if configuration is valid
        """
        errors = []
        
        # Validate confidence threshold
        if not 0.0 <= self.confidence_threshold <= 1.0:
            errors.append(f"confidence_threshold must be between 0.0 and 1.0, got {self.confidence_threshold}")
        
        # Validate timeout
        if self.vlm_timeout <= 0:
            errors.append(f"vlm_timeout must be positive, got {self.vlm_timeout}")
        
        # Validate max_retries
        if self.max_retries < 0:
            errors.append(f"max_retries must be non-negative, got {self.max_retries}")
        
        # Validate max_tokens
        if self.max_tokens <= 0:
            errors.append(f"max_tokens must be positive, got {self.max_tokens}")
        
        # Validate temperature
        if not 0.0 <= self.temperature <= 2.0:
            errors.append(f"temperature must be between 0.0 and 2.0, got {self.temperature}")
        
        # Validate model server URL
        if not self.model_server_url.startswith(('http://', 'https://')):
            errors.append(f"model_server_url must be a valid HTTP URL, got {self.model_server_url}")
        
        # Validate prompt template
        if '{query}' not in self.fallback_prompt_template:
            errors.append("fallback_prompt_template must contain '{query}' placeholder")
        
        # Validate performance parameters
        if self.max_concurrent_requests <= 0:
            errors.append(f"max_concurrent_requests must be positive, got {self.max_concurrent_requests}")
        
        if self.request_queue_size <= 0:
            errors.append(f"request_queue_size must be positive, got {self.request_queue_size}")
        
        # Validate image fallback parameters
        if self.image_capture and self.image_capture.get('max_image_size_bytes', 0) <= 0:
            errors.append(f"max_image_size_bytes must be positive, got {self.image_capture.get('max_image_size_bytes')}")
        
        if self.image_processing and self.image_processing.get('max_size', 0) <= 0:
            errors.append(f"image max_size must be positive, got {self.image_processing.get('max_size')}")
        
        if self.fallback_prompts and '{query}' not in self.fallback_prompts.get('image_fallback_template', ''):
            errors.append("image_fallback_template must contain '{query}' placeholder")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration validation error: {error}")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def get_summary(self) -> Dict:
        """
        Get configuration summary for logging/monitoring.
        
        Returns:
            Dict: Configuration summary
        """
        return {
            "confidence_threshold": self.confidence_threshold,
            "model_server_url": self.model_server_url,
            "vlm_timeout": self.vlm_timeout,
            "max_retries": self.max_retries,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "logging_enabled": {
                "decision_logs": self.enable_decision_logs,
                "vlm_logs": self.enable_vlm_logs,
                "performance_logs": self.enable_performance_logs
            },
            "performance_limits": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "request_queue_size": self.request_queue_size
            }
        }
    
    def update_from_dict(self, updates: Dict):
        """
        Update configuration from dictionary (partial updates).
        
        Args:
            updates: Dictionary with configuration updates
        """
        fallback_config = updates.get('vlm_fallback', {})
        
        # Update decision engine settings
        decision_config = fallback_config.get('decision_engine', {})
        if 'confidence_threshold' in decision_config:
            self.confidence_threshold = decision_config['confidence_threshold']
        if 'enable_unknown_query_fallback' in decision_config:
            self.enable_unknown_query_fallback = decision_config['enable_unknown_query_fallback']
        if 'enable_no_state_fallback' in decision_config:
            self.enable_no_state_fallback = decision_config['enable_no_state_fallback']
        
        # Update VLM client settings
        vlm_config = fallback_config.get('vlm_client', {})
        if 'model_server_url' in vlm_config:
            self.model_server_url = vlm_config['model_server_url']
        if 'timeout' in vlm_config:
            self.vlm_timeout = vlm_config['timeout']
        if 'max_retries' in vlm_config:
            self.max_retries = vlm_config['max_retries']
        if 'max_tokens' in vlm_config:
            self.max_tokens = vlm_config['max_tokens']
        if 'temperature' in vlm_config:
            self.temperature = vlm_config['temperature']
        
        # Update prompt settings
        prompts_config = fallback_config.get('prompts', {})
        if 'fallback_template' in prompts_config:
            self.fallback_prompt_template = prompts_config['fallback_template']
        
        # Update logging settings
        logging_config = fallback_config.get('logging', {})
        if 'enable_decision_logs' in logging_config:
            self.enable_decision_logs = logging_config['enable_decision_logs']
        if 'enable_vlm_logs' in logging_config:
            self.enable_vlm_logs = logging_config['enable_vlm_logs']
        if 'enable_performance_logs' in logging_config:
            self.enable_performance_logs = logging_config['enable_performance_logs']
        
        logger.info("Configuration updated from dictionary")


# Default configuration instance
DEFAULT_CONFIG = VLMFallbackConfig()


def load_config(config_path: Optional[str] = None) -> VLMFallbackConfig:
    """
    Load configuration from file or return default.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        VLMFallbackConfig: Configuration instance
    """
    if config_path:
        return VLMFallbackConfig.from_file(config_path)
    
    # Try to load from default locations
    default_paths = [
        "src/config/vlm_fallback_config.json",
        "config/vlm_fallback_config.json",
        "vlm_fallback_config.json"
    ]
    
    for path in default_paths:
        if Path(path).exists():
            return VLMFallbackConfig.from_file(path)
    
    logger.info("No configuration file found, using defaults")
    return DEFAULT_CONFIG