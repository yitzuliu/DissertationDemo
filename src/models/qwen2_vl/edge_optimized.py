#!/usr/bin/env python3
"""
Qwen2-VL-2B Edge Device Optimized Version
This script optimizes the Qwen2-VL-2B model for efficient operation on edge devices (laptops, iPhones, etc.)
"""

import os
import sys
import argparse
import logging
import time
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Qwen2-VL-2B Edge")

def setup_args():
    parser = argparse.ArgumentParser(description="Optimized Qwen2-VL edge device version")
    parser.add_argument("--model_path", type=str, default="./model/qwen2vl-2b-q4_k_m.gguf",
                      help="Path to model in GGUF format")
    parser.add_argument("--image", type=str, required=True,
                      help="Path to the image for analysis")
    parser.add_argument("--prompt", type=str, default="Describe the content in this image",
                      help="Prompt text")
    parser.add_argument("--max_tokens", type=int, default=100,
                      help="Maximum number of tokens to generate")
    parser.add_argument("--cpu_threads", type=int, default=4,
                      help="Number of CPU threads to use")
    parser.add_argument("--optimization_level", type=str, choices=["low", "medium", "high"], default="medium",
                      help="Optimization level: low=quality priority, medium=balanced, high=speed priority")
    parser.add_argument("--model_type", type=str, choices=["qwen2-vl-2b", "qwen25-vl-3b", "qwen25-vl-7b"], 
                      default="qwen2-vl-2b",
                      help="Model type: qwen2-vl-2b(edge friendly), qwen25-vl-3b(balanced), qwen25-vl-7b(high performance)")
    return parser.parse_args()

def check_dependencies():
    """Check necessary dependencies"""
    try:
        from llama_cpp import Llama
        from PIL import Image
        logger.info("All basic dependencies installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.info("Please run: pip install llama-cpp-python pillow numpy")
        return False

def get_model_info(model_type):
    """Return information based on model type"""
    model_info = {
        "qwen2-vl-2b": {
            "name": "Qwen2-VL-2B",
            "params": "2B",
            "ram": "~4-5GB",
            "suitable_for": "Edge devices, laptops, some high-end mobile devices",
            "context_length": 2048,
            "recommended_threads": 4
        },
        "qwen25-vl-3b": {
            "name": "Qwen2.5-VL-3B",
            "params": "3B",
            "ram": "~6-7GB",
            "suitable_for": "Mid to high-end laptops, desktops, high-end mobile devices",
            "context_length": 4096,
            "recommended_threads": 6
        },
        "qwen25-vl-7b": {
            "name": "Qwen2.5-VL-7B",
            "params": "7B",
            "ram": "~12-14GB",
            "suitable_for": "High-end laptops, desktops, not suitable for most mobile devices",
            "context_length": 8192,
            "recommended_threads": 8
        }
    }
    return model_info.get(model_type)

def load_optimized_model(model_path, cpu_threads=4, model_type="qwen2-vl-2b"):
    """Load optimized Qwen VL model"""
    try:
        from llama_cpp import Llama
        
        # Get model information
        model_info = get_model_info(model_type)
        if not model_info:
            model_info = get_model_info("qwen2-vl-2b")  # Default fallback to 2B model
        
        # Adjust threads, but don't exceed recommended value
        actual_threads = min(cpu_threads, model_info["recommended_threads"])
        
        logger.info(f"Loading {model_info['name']} ({model_info['params']} parameters) from {model_path}...")
        logger.info(f"Estimated memory requirement: {model_info['ram']}")
        logger.info(f"Suitable for: {model_info['suitable_for']}")
        
        # Load model
        model = Llama(
            model_path=model_path,
            n_ctx=model_info["context_length"],  # Adjust context window size based on model
            n_batch=512,  # Batch size
            n_threads=actual_threads,  # CPU threads
            n_gpu_layers=-1,  # Try to move all layers to GPU (-1)
            verbose=False
        )
        
        logger.info("Optimized model loading complete!")
        return model
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

def preprocess_image(image_path, opt_level="medium"):
    """Optimized image processing"""
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        import numpy as np
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Adjust resolution based on optimization level
        if opt_level == "high":  # Speed priority
            new_size = (336, 336)
        elif opt_level == "medium":  # Balanced
            new_size = (448, 448)
        else:  # Quality priority
            new_size = (560, 560)
            
        # Resize
        image = image.resize(new_size, Image.LANCZOS)
        
        if opt_level != "high":  # For non-speed-priority modes, apply image enhancement
            # Apply slight enhancements
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Additional processing for "low" optimization level
            if opt_level == "low":
                # Apply bilateral filter rather than Gaussian blur (preserves edges)
                # Use numpy to simulate simple bilateral filtering
                img_array = np.array(image)
                filtered = np.copy(img_array)
                
                # Simplified bilateral filter simulation
                for _ in range(1):  # Light filtering
                    filtered = np.array(Image.fromarray(filtered).filter(
                        ImageFilter.SMOOTH_MORE))
                
                # Preserve edges
                edges = np.array(Image.fromarray(img_array).filter(
                    ImageFilter.FIND_EDGES))
                
                # Merge results
                result = filtered.astype(np.float32) + edges.astype(np.float32) * 0.2
                result = np.clip(result, 0, 255).astype(np.uint8)
                
                image = Image.fromarray(result)
        
        logger.info(f"Image preprocessing complete, optimization level: {opt_level}")
        return image
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return None

def encode_image(image):
    """Encode PIL image to base64 string"""
    import base64
    from io import BytesIO
    
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def process_with_edge_model(model, image, prompt, max_tokens=100):
    """Process image with optimized edge model"""
    try:
        # Encode image
        image_base64 = encode_image(image)
        
        # Build multimodal prompt
        multimodal_prompt = f"""
        <img>{image_base64}</img>
        Human: {prompt}
        Assistant: 
        """
        
        # Start timing
        start_time = time.time()
        
        # Generate response
        logger.info("Generating response...")
        result = model.create_completion(
            multimodal_prompt,
            max_tokens=max_tokens,
            stop=["Human:", "Human："],
            temperature=0.1,  # Low temperature for consistency
            repeat_penalty=1.1  # Reduce repetition
        )
        
        # End timing
        elapsed_time = time.time() - start_time
        
        # Extract answer
        answer = result["choices"][0]["text"].strip()
        
        logger.info(f"Generation complete, time taken: {elapsed_time:.2f} seconds")
        return answer, elapsed_time
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return None, None

def memory_usage_info():
    """Get memory usage information"""
    import psutil
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # MB

def main():
    args = setup_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create full paths
    model_path = os.path.abspath(args.model_path)
    image_path = os.path.abspath(args.image)
    
    # Check file existence
    if not os.path.exists(model_path):
        logger.error(f"Model file does not exist: {model_path}")
        sys.exit(1)
        
    if not os.path.exists(image_path):
        logger.error(f"Image does not exist: {image_path}")
        sys.exit(1)
    
    # Display model type and expected performance
    model_info = get_model_info(args.model_type)
    logger.info(f"Selected model: {model_info['name']} ({model_info['params']} parameters)")
    logger.info(f"Estimated memory requirement: {model_info['ram']}")
    logger.info(f"Suitable device types: {model_info['suitable_for']}")
    
    # Record initial memory
    initial_memory = memory_usage_info()
    logger.info(f"Initial memory usage: {initial_memory:.2f} MB")
    
    # Load optimized model
    model = load_optimized_model(model_path, args.cpu_threads, args.model_type)
    if model is None:
        logger.error("Model loading failed!")
        sys.exit(1)
    
    # Memory after loading model
    after_load_memory = memory_usage_info()
    logger.info(f"Memory usage after model load: {after_load_memory:.2f} MB (increase: {after_load_memory - initial_memory:.2f} MB)")
    
    # Preprocess image
    processed_image = preprocess_image(image_path, args.optimization_level)
    if processed_image is None:
        logger.error("Image preprocessing failed!")
        sys.exit(1)
    
    # Process image
    answer, process_time = process_with_edge_model(model, processed_image, args.prompt, args.max_tokens)
    
    # Memory after processing
    final_memory = memory_usage_info()
    
    if answer:
        logger.info("\n===== Model Response =====")
        print(f"\n{answer}\n")
        
        logger.info("\n===== Performance Data =====")
        logger.info(f"Model used: {model_info['name']} ({model_info['params']} parameters)")
        logger.info(f"Processing time: {process_time:.2f} seconds")
        logger.info(f"Final memory usage: {final_memory:.2f} MB")
        logger.info(f"Optimization level: {args.optimization_level}")
        logger.info(f"Image size: {processed_image.size}")
    else:
        logger.error("Image processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
