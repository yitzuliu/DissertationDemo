#!/usr/bin/env python3
"""
Qwen2-VL-2B Model Download Script
This script downloads the Qwen2-VL-2B model from Hugging Face and saves it locally
"""

import os
import sys
from pathlib import Path
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Qwen2-VL-2B Downloader")

def setup_args():
    parser = argparse.ArgumentParser(description="Download and set up Qwen VL models")
    parser.add_argument("--output_dir", type=str, default="./model",
                      help="Model save directory (default: ./model)")
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2-VL-2B",
                      help="Model name to download, options: Qwen/Qwen2-VL-2B, Qwen/Qwen2.5-VL-3B, Qwen/Qwen2.5-VL-7B")
    parser.add_argument("--use_safetensors", action="store_true",
                      help="Use safetensors format to download model")
    parser.add_argument("--convert_to_gguf", action="store_true",
                      help="Convert to GGUF format after download (requires llama-cpp-python)")
    parser.add_argument("--quantize", type=str, choices=["int8", "int4", "none"], default="none",
                      help="Quantization level (requires --convert_to_gguf)")
    return parser.parse_args()

def check_dependencies():
    """Check necessary dependencies"""
    try:
        import torch
        import transformers
        from huggingface_hub import snapshot_download
        logger.info("All basic dependencies installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.info("Please run: pip install torch transformers huggingface_hub")
        return False

def download_model(output_dir, model_id="Qwen/Qwen2-VL-2B", use_safetensors=False):
    """Download Qwen VL model"""
    try:
        from huggingface_hub import snapshot_download
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Starting download from Hugging Face: {model_id}")
        logger.info(f"Model will be saved to {output_dir}")
        
        # Get model parameter size
        if "2B" in model_id:
            model_size = "2B"
            estimated_disk = "~5GB"
        elif "3B" in model_id:
            model_size = "3B"
            estimated_disk = "~7GB" 
        elif "7B" in model_id:
            model_size = "7B" 
            estimated_disk = "~14GB"
        else:
            model_size = "unknown"
            estimated_disk = "unknown"
            
        logger.info(f"Model size: {model_size} parameters")
        logger.info(f"Estimated disk space requirement: {estimated_disk}")
        
        # Download model
        allow_patterns = ["*.safetensors"] if use_safetensors else ["*.bin", "*.json", "*.model", "*.py", "tokenizer.*"]
        
        # Download model files
        snapshot_download(
            repo_id=model_id,
            local_dir=output_dir,
            allow_patterns=allow_patterns + ["*.json", "*.txt", "*.py", "*.md", "tokenizer.*"],
            ignore_patterns=[".*", "*.msgpack", "*.h5"],
        )
        
        logger.info(f"Model download complete!")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        return False

def convert_to_gguf(model_dir, quantize="none"):
    """Convert model to GGUF format"""
    try:
        import subprocess
        
        logger.info("Attempting to convert model to GGUF format...")
        output_path = os.path.join(os.path.dirname(model_dir), "qwen2vl-2b")
        
        if quantize == "int8":
            output_path += "-q8_0.gguf"
            quant_arg = "--quantize q8_0"
        elif quantize == "int4":
            output_path += "-q4_k_m.gguf"  # k_m typically offers good quality for 4-bit
            quant_arg = "--quantize q4_k_m"
        else:
            output_path += ".gguf"
            quant_arg = ""
        
        cmd = f"python -m llama_cpp.model_converter --model {model_dir} --outfile {output_path} {quant_arg}"
        
        logger.info(f"Executing conversion command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        
        logger.info(f"Model has been converted to GGUF format: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error converting model: {e}")
        logger.error("Please make sure llama-cpp-python is installed: pip install llama-cpp-python")
        return False

def main():
    args = setup_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create full output path
    output_dir = os.path.abspath(args.output_dir)
    
    # Download model
    if download_model(output_dir, args.model_name, args.use_safetensors):
        logger.info("Model download successful!")
        
        # If conversion to GGUF is needed
        if args.convert_to_gguf:
            try:
                import llama_cpp
                if convert_to_gguf(output_dir, args.quantize):
                    logger.info("Model conversion successful!")
            except ImportError:
                logger.error("llama-cpp-python module not found, cannot convert to GGUF format")
                logger.info("Please run: pip install llama-cpp-python")
    else:
        logger.error("Model download failed!")
        sys.exit(1)
    
    # Extract short version of model name for display
    model_short_name = args.model_name.split("/")[-1]
    
    # Suggest next steps
    logger.info("\n===== Next Steps =====")
    logger.info("1. Before loading the model, ensure all necessary dependencies are installed:")
    logger.info("   pip install torch transformers pillow")
    logger.info(f"2. Use the following code to load the {model_short_name} model:")
    logger.info("""
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
    from PIL import Image
    
    # Load model and processor
    model_path = "%s"
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True)
    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
    
    # Prepare image and prompt
    image = Image.open("your_image.jpg")
    prompt = "Describe the content in this image"
    
    # Process input
    inputs = processor(prompt, image, return_tensors="pt").to(model.device)
    
    # Generate response
    with torch.no_grad():
        response = model.generate(**inputs, max_new_tokens=100)
    
    # Decode response
    answer = tokenizer.decode(response[0], skip_special_tokens=True)
    print(answer)
    """ % output_dir)
    
    # For GGUF models, show different usage method
    if args.convert_to_gguf:
        logger.info("\n3. For the converted GGUF format, you can use llama-cpp-python:")
        logger.info("""
    from llama_cpp import Llama
    from PIL import Image
    import base64
    from io import BytesIO
    
    # Encode image to base64
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    # Load model
    model = Llama(
        model_path="%s.gguf",  # Path to the converted model
        n_ctx=4096,            # Context window size
        n_threads=4            # Number of threads
    )
    
    # Encode image
    image_base64 = encode_image("your_image.jpg")
    
    # Build multimodal prompt
    prompt = f\"\"\"
    <img>{image_base64}</img>
    Human: Describe the content in this image
    Assistant: 
    \"\"\"
    
    # Generate response
    result = model.create_completion(
        prompt,
        max_tokens=100,
        stop=["Human:", "Human："],
        temperature=0.1
    )
    
    print(result["choices"][0]["text"])
        """ % (output_dir.replace(".gguf", "") if output_dir.endswith(".gguf") else output_dir))
