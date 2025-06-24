"""
Configuration Manager for AI Manual Assistant

This module provides a unified configuration management system with support for:
- Loading and merging configurations from multiple sources
- Hierarchical configuration with inheritance
- Dynamic configuration updates
- Validation of configuration values
"""

import json
import os
from pathlib import Path
import logging
from typing import Dict, Any, Optional, Union
import copy

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Unified configuration manager that handles loading, merging, and accessing 
    configurations throughout the application.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            base_path: Base directory path for configuration files. 
                      If None, will use src/config/ relative to this file.
        """
        if base_path is None:
            self.base_path = Path(__file__).parent.parent.parent / "config"
        else:
            self.base_path = base_path
            
        # Main configuration store
        self._config: Dict[str, Any] = {}
        
        # Model-specific configurations
        self._model_configs: Dict[str, Dict[str, Any]] = {}
        
        # Default values for required config entries
        self._defaults = {
            "server": {
                "host": "localhost",
                "port": 8000
            },
            "frontend": {
                "video_width": 640,
                "video_height": 480, 
                "api_base_url": "http://localhost:8000"
            },
            "active_model": "smolvlm"
        }
        
        # Initialize with default configuration
        self._config = copy.deepcopy(self._defaults)
        
    def load_app_config(self) -> Dict[str, Any]:
        """
        Load the main application configuration.
        
        Returns:
            The loaded configuration dictionary
        """
        config_path = self.base_path / "app_config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                
            # Merge with defaults, with loaded config taking precedence
            self._config = self._deep_merge(copy.deepcopy(self._defaults), loaded_config)
            logger.info(f"Application configuration loaded from {config_path}")
            
        except FileNotFoundError:
            logger.warning(f"Configuration file not found at {config_path}. Using defaults.")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file at {config_path}. Using defaults.")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}. Using defaults.")
            
        return self._config
    
    def load_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        Load configuration for a specific model.
        
        Args:
            model_name: Name of the model (should match filename without .json)
            
        Returns:
            Model configuration dictionary
        """
        # Return cached config if already loaded
        if model_name in self._model_configs:
            return self._model_configs[model_name]
        
        model_config_path = self.base_path / "model_configs" / f"{model_name}.json"
        
        try:
            with open(model_config_path, 'r', encoding='utf-8') as f:
                model_config = json.load(f)
                
            # Cache the model configuration
            self._model_configs[model_name] = model_config
            logger.info(f"Model configuration for '{model_name}' loaded from {model_config_path}")
            
            return model_config
            
        except FileNotFoundError:
            logger.warning(f"Model configuration file not found at {model_config_path}")
            self._model_configs[model_name] = {}
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in model configuration file at {model_config_path}")
            self._model_configs[model_name] = {}
            return {}
        except Exception as e:
            logger.error(f"Error loading model configuration: {str(e)}")
            self._model_configs[model_name] = {}
            return {}
    
    def get_active_model(self) -> str:
        """Get the active model name"""
        return self._config.get("active_model", "smolvlm")
    
    def get_active_model_config(self) -> Dict[str, Any]:
        """
        Get the configuration for the currently active model.
        
        Returns:
            The active model's configuration
        """
        active_model = self.get_active_model()
        return self.load_model_config(active_model)
    
    def get_merged_config(self) -> Dict[str, Any]:
        """
        Get a merged configuration containing both app config and active model config.
        
        Returns:
            Merged configuration dictionary
        """
        merged_config = copy.deepcopy(self._config)
        active_model_config = self.get_active_model_config()
        
        # Add model configuration under model_config key
        merged_config["model_config"] = active_model_config
        
        return merged_config
    
    def update_config(self, updates: Dict[str, Any], save: bool = True) -> Dict[str, Any]:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary with new configuration values
            save: Whether to save changes to disk
            
        Returns:
            Updated configuration dictionary
        """
        self._config = self._deep_merge(self._config, updates)
        
        if save:
            self._save_app_config()
            
        return self._config
    
    def set_active_model(self, model_name: str, save: bool = True) -> bool:
        """
        Set the active model and optionally save to disk.
        
        Args:
            model_name: Name of the model to set as active
            save: Whether to save changes to disk
            
        Returns:
            True if successful, False otherwise
        """
        # Verify model exists first
        model_config_path = self.base_path / "model_configs" / f"{model_name}.json"
        if not model_config_path.exists():
            logger.error(f"Cannot set active model: Model configuration for '{model_name}' not found")
            return False
        
        self._config["active_model"] = model_name
        
        # Refresh model config cache
        if model_name in self._model_configs:
            del self._model_configs[model_name]
        
        if save:
            self._save_app_config()
            
        logger.info(f"Active model set to '{model_name}'")
        return True
    
    def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a configuration value by key path.
        
        Args:
            key: Dot-separated key path (e.g., 'server.port')
            default: Default value to return if key not found
            
        Returns:
            Configuration value or default if not found
        """
        if key is None:
            return copy.deepcopy(self._config)
        
        parts = key.split('.')
        value = self._config
        
        try:
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_model_config_value(self, model_name: str, key: str, default: Any = None) -> Any:
        """
        Get a value from a specific model's configuration.
        
        Args:
            model_name: Name of the model
            key: Dot-separated key path (e.g., 'image_processing.size')
            default: Default value to return if key not found
            
        Returns:
            Configuration value or default if not found
        """
        model_config = self.load_model_config(model_name)
        parts = key.split('.')
        value = model_config
        
        try:
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def _save_app_config(self) -> bool:
        """
        Save the current application configuration to disk.
        
        Returns:
            True if successful, False otherwise
        """
        config_path = self.base_path / "app_config.json"
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
            
    @staticmethod
    def _deep_merge(base: Dict, update: Dict) -> Dict:
        """
        Recursively merge two dictionaries, with values from update taking precedence.
        
        Args:
            base: Base dictionary
            update: Dictionary with updates
            
        Returns:
            Merged dictionary
        """
        result = copy.deepcopy(base)
        
        for key, value in update.items():
            # If both values are dictionaries, merge them
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result

# Create a singleton instance for import elsewhere
config_manager = ConfigManager()
