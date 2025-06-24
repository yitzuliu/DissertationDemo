#!/usr/bin/env python
"""
Test script to validate the refactored model structure
"""

import os
import sys
from pathlib import Path
import json
import logging

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.base_model import VLMFactory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(model_name):
    """Load configuration for the specified model"""
    config_path = Path(__file__).parent / "src" / "config" / "model_configs"
    
    # Map model names to config files
    config_mapping = {
        "phi3_vision": "phi3_vision.json",
        "smolvlm": "smolvlm.json",
        "yolo8": "yolo8.json",
        "llava": "llava.json"
    }
    
    # Select config file based on model name
    config_file = None
    for name, file in config_mapping.items():
        if name in model_name.lower():
            config_file = file
            break
    
    if not config_file:
        raise ValueError(f"No config found for model {model_name}")
    
    config_file_path = config_path / config_file
    if not config_file_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file_path}")
    
    with open(config_file_path, 'r') as f:
        return json.load(f)

def test_model_imports():
    """Test importing of models after refactoring"""
    
    results = {}
    
    # Check the structure of model files instead of importing them
    model_files = [
        ("Phi3VisionModel", "src/models/phi3_vision/phi3_vision_model.py"),
        ("SmolVLMModel", "src/models/smolvlm/smolvlm_model.py"),
        ("YOLO8Model", "src/models/yolo8/yolo8_model.py"),
        ("LLaVAModel", "src/models/LLava/llava_model.py")
    ]
    
    # Check if files exist
    for model_name, file_path in model_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            logger.info(f"✅ Found {model_name} at {file_path}")
            results[model_name] = "File exists"
        else:
            logger.error(f"❌ Could not find {model_name} at {file_path}")
            results[model_name] = f"Error: File not found"
    
    # Check that the factory imports from new locations
    factory_file = Path(__file__).parent / "src/models/base_model.py"
    if factory_file.exists():
        with open(factory_file, 'r') as f:
            content = f.read()
            
        import_patterns = [
            "from .phi3_vision.phi3_vision_model import Phi3VisionModel",
            "from .smolvlm.smolvlm_model import SmolVLMModel",
            "from .yolo8.yolo8_model import YOLO8Model",
            "from .LLava.llava_model import LLaVAModel"
        ]
        
        factory_status = True
        for pattern in import_patterns:
            if pattern not in content:
                factory_status = False
                logger.error(f"❌ Missing import in factory: {pattern}")
        
        if factory_status:
            logger.info("✅ Factory imports updated correctly")
            results["VLMFactory"] = "Imports updated"
        else:
            results["VLMFactory"] = "Error: Some imports missing"
    else:
        logger.error("❌ Could not find factory file")
        results["VLMFactory"] = "Error: File not found"
    
    return results

if __name__ == "__main__":
    print("Testing refactored model structure...")
    results = test_model_imports()
    
    print("\nResults:")
    for model, result in results.items():
        status = "✅" if "Error" not in result else "❌"
        print(f"{status} {model}: {result}")
