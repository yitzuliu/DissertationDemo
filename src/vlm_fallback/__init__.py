"""
VLM Fallback System

A transparent fallback system that automatically switches to VLM direct queries
when state tracker confidence is low, while maintaining seamless user experience.

Core Components:
- DecisionEngine: Determines when to use VLM fallback
- PromptManager: Manages VLM prompt switching and restoration
- VLMClient: Handles communication with VLM service
- VLMFallbackProcessor: Orchestrates the entire fallback process
- VLMFallbackConfig: Configuration management

Key Features:
- Transparent to users (always appears as "State Query")
- Automatic prompt switching and restoration
- Error recovery and fault tolerance
- Seamless integration with existing state tracker
"""

from .decision_engine import DecisionEngine
from .prompt_manager import PromptManager
from .vlm_client import VLMClient
from .fallback_processor import VLMFallbackProcessor
from .config import VLMFallbackConfig

__version__ = "1.0.0"
__author__ = "AI Manual Assistant Team"

__all__ = [
    "DecisionEngine",
    "PromptManager", 
    "VLMClient",
    "VLMFallbackProcessor",
    "VLMFallbackConfig"
]