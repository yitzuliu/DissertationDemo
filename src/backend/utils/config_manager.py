"""
Configuration Manager for AI Manual Assistant

This module provides a unified configuration management system with support for:
- Loading and merging configurations from multiple sources
- Hierarchical configuration with inheritance
- Dynamic configuration updates
- Validation of configuration values
"""

import json
import logging
import copy
from pathlib import Path
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Unified configuration manager that handles loading, merging, and accessing 
    configurations throughout the application.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            # Default to src/config directory
            self.base_path = Path(__file__).resolve().parent.parent.parent / "config"
        else:
            self.base_path = Path(base_path)
        
        # Main configuration store
        self._config = {}
        
        # Model-specific configurations
        self._model_configs = {}
        
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
            "model_server": {
                "host": "localhost",
                "port": 8080
            },
            "active_model": "phi3_vision"
        }
        
        # Initialize with default configuration
        self._config = copy.deepcopy(self._defaults)
        
    def load_app_config(self) -> Dict[str, Any]:
        """Load main application configuration"""
        try:
            config_file = self.base_path / "app_config.json"
            logger.info(f"Looking for app config at: {config_file}")
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults, with loaded config taking precedence
                self._config = self._deep_merge(copy.deepcopy(self._defaults), loaded_config)
                logger.info(f"App config loaded successfully from {config_file}")
            else:
                logger.warning(f"App config file not found: {config_file}")
                self._config = copy.deepcopy(self._defaults)
                
            return copy.deepcopy(self._config)
        except Exception as e:
            logger.error(f"Failed to load app config: {e}")
            self._config = copy.deepcopy(self._defaults)
            return copy.deepcopy(self._config)
    
    def load_model_config(self, model_name: str) -> Dict[str, Any]:
        """Load configuration for a specific model"""
        try:
            if model_name in self._model_configs:
                return copy.deepcopy(self._model_configs[model_name])
            
            config_file = self.base_path / "model_configs" / f"{model_name}.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    model_config = json.load(f)
                
                self._model_configs[model_name] = model_config
                logger.info(f"Successfully loaded model config for {model_name}")
                return copy.deepcopy(model_config)
            else:
                logger.warning(f"Model config file not found: {config_file}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load model config for {model_name}: {e}")
            return {}
    
    def get_active_model(self) -> str:
        """Get the currently active model name"""
        return self._config.get("active_model", "phi3_vision")
    
    def get_active_model_config(self) -> Dict[str, Any]:
        """Get configuration for the currently active model"""
        active_model = self.get_active_model()
        return self.load_model_config(active_model)
    
    def get_merged_config(self) -> Dict[str, Any]:
        """Get merged configuration including app and active model config"""
        merged = copy.deepcopy(self._config)
        active_model_config = self.get_active_model_config()
        if active_model_config:
            merged["model_config"] = active_model_config
        return merged
    
    def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """Get configuration value by key path (e.g., 'server.port')"""
        if key is None:
            return copy.deepcopy(self._config)
        
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except (KeyError, TypeError):
            return default
    
    def set_active_model(self, model_name: str, save: bool = True) -> bool:
        """Set the active model"""
        try:
            # Verify model exists first by checking both config file and models_config.json
            model_config_path = self.base_path / "model_configs" / f"{model_name}.json"
            models_config_path = self.base_path / "models_config.json"
            
            # Check individual model config file
            if not model_config_path.exists():
                # Check if model exists in models_config.json
                if models_config_path.exists():
                    with open(models_config_path, 'r', encoding='utf-8') as f:
                        models_config = json.load(f)
                    if model_name not in models_config.get("models", {}):
                        logger.error(f"Cannot set active model: Model '{model_name}' not found in models_config.json")
                        return False
                else:
                    logger.error(f"Cannot set active model: Model configuration for '{model_name}' not found")
                    return False
            
            old_model = self._config.get("active_model", "none")
            self._config["active_model"] = model_name
            
            # Refresh model config cache
            if model_name in self._model_configs:
                del self._model_configs[model_name]
            
            if save:
                success = self._save_app_config()
                if not success:
                    # Rollback on save failure
                    self._config["active_model"] = old_model
                    return False
                
            logger.info(f"Active model changed from '{old_model}' to '{model_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to set active model {model_name}: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any], save: bool = True) -> Dict[str, Any]:
        """Update configuration with new values"""
        try:
            self._config = self._deep_merge(self._config, updates)
            
            if save:
                self._save_app_config()
                
            logger.info(f"Updated config: {updates}")
            return copy.deepcopy(self._config)
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return copy.deepcopy(self._config)

    def get_model_config_value(self, model_name: str, key: str, default: Any = None) -> Any:
        """Get a value from a specific model's configuration"""
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
        """Save the current application configuration to disk"""
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
        """Recursively merge two dictionaries, with values from update taking precedence"""
        result = copy.deepcopy(base)
        
        for key, value in update.items():
            # If both values are dictionaries, merge them
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result

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
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models from models_config.json"""
        try:
            models_config_path = self.base_path / "models_config.json"
            if models_config_path.exists():
                with open(models_config_path, 'r', encoding='utf-8') as f:
                    models_config = json.load(f)
                return models_config.get("models", {})
            else:
                logger.warning("models_config.json not found")
                return {}
        except Exception as e:
            logger.error(f"Failed to load available models: {e}")
            return {}
    
    def validate_model_exists(self, model_name: str) -> bool:
        """Validate that a model exists in the configuration"""
        available_models = self.get_available_models()
        return model_name in available_models
    
    def _save_app_config(self) -> bool:
        """
        Save the current application configuration to disk.
        
        Returns:
            True if successful, False otherwise
        """
        config_path = self.base_path / "app_config.json"
        
        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
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
