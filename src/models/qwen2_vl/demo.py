#!/usr/bin/env python3
"""
Qwen2-VL-2B Model Usage Example
This script demonstrates how to use the Qwen2-VL-2B model to process images and generate responses
"""

import os
import sys
import argparse
import torch
from PIL import Image
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Qwen2-VL-2B Demo")

def setup_args():
    parser = argparse.ArgumentParser(description="Use Qwen2-VL-2B model to process images")
    parser.add_argument("--model_dir", type=str, default="./model",
                      help="Model directory (default: ./model)")
    parser.add_argument("--image", type=str, required=True,
                      help="Path to the image for analysis")
    parser.add_argument("--prompt", type=str, default="Describe the content in this image",
                      help="Prompt text")
    parser.add_argument("--max_tokens", type=int, default=100,
                      help="Maximum number of tokens to generate")
    return parser.parse_args()

def check_dependencies():
    """Check necessary dependencies"""
    try:
        import torch
        import transformers
        from PIL import Image
        logger.info("All basic dependencies installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.info("Please run: pip install torch transformers pillow")
        return False

def load_model(model_dir):
    """Load Qwen2-VL-2B model"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
        
        logger.info(f"Loading model from {model_dir}...")
        
        # Load tokenizer
        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        
        # Load model
        logger.info("Loading model...")
        model = AutoModelForCausalLM.from_pretrained(model_dir, device_map="auto", trust_remote_code=True)
        
        # Load processor
        logger.info("Loading processor...")
        processor = AutoProcessor.from_pretrained(model_dir, trust_remote_code=True)
        
        logger.info("Model loading complete!")
        return model, tokenizer, processor
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None, None, None

def process_image(image_path, prompt, model, tokenizer, processor, max_tokens=100):
    """Process image and generate response"""
    try:
        # Load image
        logger.info(f"Loading image: {image_path}")
        image = Image.open(image_path).convert('RGB')
        
        # Prepare input
        logger.info(f"Processing input, prompt: '{prompt}'")
        inputs = processor(prompt, image, return_tensors="pt").to(model.device)
        
        # Generate response
        logger.info("Generating response...")
        with torch.no_grad():
            response = model.generate(**inputs, max_new_tokens=max_tokens)
        
        # Decode response
        answer = tokenizer.decode(response[0], skip_special_tokens=True)
        
        return answer
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return None

def main():
    args = setup_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create full paths
    model_dir = os.path.abspath(args.model_dir)
    image_path = os.path.abspath(args.image)
    
    # Check file existence
    if not os.path.exists(model_dir):
        logger.error(f"Model directory does not exist: {model_dir}")
        sys.exit(1)
        
    if not os.path.exists(image_path):
        logger.error(f"Image does not exist: {image_path}")
        sys.exit(1)
    
    # Load model
    model, tokenizer, processor = load_model(model_dir)
    if model is None or tokenizer is None or processor is None:
        logger.error("Failed to load model!")
        sys.exit(1)
    
    # Process image
    answer = process_image(image_path, args.prompt, model, tokenizer, processor, args.max_tokens)
    
    if answer:
        logger.info("\n===== Model Response =====")
        print(f"\n{answer}\n")
    else:
        logger.error("Image processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
