"""
Model Interface Integration Test

This script tests the BaseVisionModel interface implementations for various models
to ensure they follow the standardized interface and can be loaded through the factory.

Usage: python test_model_interface.py [model_name]
If no model_name is provided, all models will be tested.
"""

import os
import sys
import json
import logging
import time
import argparse
from PIL import Image
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("model-interface-test")

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the model factory and base class
from models.base_model import VLMFactory, BaseVisionModel

def load_model_config(model_name):
    """
    Load model configuration from config files
    """
    config_dir = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "config" / "model_configs"
    
    # Map model name patterns to config files
    model_configs = {
        "phi3": "phi3_vision.json",
        "yolo": "yolo8.json", 
        "llava": "llava.json",
        "smolvlm": "smolvlm.json"
    }
    
    # Find matching config file
    config_file = None
    for pattern, filename in model_configs.items():
        if pattern in model_name.lower():
            config_file = config_dir / filename
            break
    
    if not config_file or not config_file.exists():
        logger.error(f"No configuration file found for model {model_name}")
        return None
    
    with open(config_file, 'r') as f:
        return json.load(f)

def load_test_image():
    """
    Load a test image - first try to find one in the project, otherwise use a simple generated image
    """
    # Try to find an image in the project
    image_paths = [
        Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "assets" / "test_image.jpg",
        Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "frontend" / "assets" / "test_image.jpg"
    ]
    
    for path in image_paths:
        if path.exists():
            logger.info(f"Using test image from {path}")
            return Image.open(path)
    
    # Create a simple test image if no image found
    logger.info("Creating a simple test image")
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (640, 480), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.rectangle([200, 100, 400, 300], fill=(128, 0, 0))
    d.ellipse([250, 150, 350, 250], fill=(255, 255, 0))
    return img

def test_model(model_name):
    """
    Test a specific model's integration with the BaseVisionModel interface
    """
    logger.info(f"Testing model: {model_name}")
    
    try:
        # 1. Load configuration
        config = load_model_config(model_name)
        if not config:
            logger.error(f"Failed to load configuration for {model_name}")
            return False
        
        # 2. Create model instance using factory
        model = VLMFactory.create_model(model_name, config)
        logger.info(f"Created model instance: {type(model).__name__}")
        
        # 3. Check that it implements BaseVisionModel
        if not isinstance(model, BaseVisionModel):
            logger.error(f"Model {model_name} is not an instance of BaseVisionModel")
            return False
        
        # 4. Test model.get_model_info() method
        model_info = model.get_model_info()
        logger.info(f"Model info: {model_info['name']}, Loaded: {model_info['loaded']}")
        
        # 5. Test model loading
        logger.info("Loading model...")
        load_start = time.time()
        load_success = model.load_model()
        load_time = time.time() - load_start
        
        if not load_success:
            logger.error(f"Failed to load model {model_name}")
            return False
        
        logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
        
        # 6. Load test image
        test_image = load_test_image()
        
        # 7. Test image preprocessing
        logger.info("Testing image preprocessing...")
        preprocessed = model.preprocess_image(test_image)
        logger.info(f"Image preprocessed, type: {type(preprocessed)}")
        
        # 8. Test prediction
        logger.info("Testing prediction...")
        predict_start = time.time()
        test_prompt = "Describe what you see in this image in detail."
        prediction = model.predict(test_image, test_prompt)
        predict_time = time.time() - predict_start
        
        logger.info(f"Prediction completed in {predict_time:.2f} seconds")
        logger.info(f"Prediction result (success): {prediction.get('success', False)}")
        
        # 9. Test model unloading
        logger.info("Unloading model...")
        unload_success = model.unload_model()
        logger.info(f"Model unloaded: {unload_success}")
        
        logger.info(f"All tests passed for model {model_name}")
        return True
    
    except Exception as e:
        logger.error(f"Error testing model {model_name}: {str(e)}", exc_info=True)
        return False

def main():
    """
    Main test execution function
    """
    parser = argparse.ArgumentParser(description='Test model interfaces')
    parser.add_argument('model', nargs='?', help='Model name to test (omit to test all)')
    args = parser.parse_args()
    
    if args.model:
        # Test specific model
        test_model(args.model)
    else:
        # Test all models
        models_to_test = ["phi3_vision", "yolo8", "llava", "smolvlm"]
        results = {}
        
        for model in models_to_test:
            logger.info(f"\n{'=' * 40}\nTesting {model}\n{'=' * 40}")
            results[model] = test_model(model)
            
        # Print summary
        logger.info("\n\n" + "=" * 50)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 50)
        
        all_passed = True
        for model, result in results.items():
            status = "PASSED" if result else "FAILED"
            logger.info(f"{model}: {status}")
            all_passed = all_passed and result
        
        logger.info("=" * 50)
        logger.info(f"OVERALL: {'PASSED' if all_passed else 'FAILED'}")
        logger.info("=" * 50)

if __name__ == "__main__":
    main()
