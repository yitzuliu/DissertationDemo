#!/usr/bin/env python3
"""
SmolVLM2 Model Loading (Legacy - Deprecated)
This file has been reorganized. Use the new MLX-optimized structure:
- start_server.py for server operations
- inference/ directory for processing scripts
"""

# DEPRECATED: This approach uses CUDA/transformers
# NEW: Use MLX-optimized approach for Apple Silicon

# Legacy CUDA approach (for reference only)
# !pip install git+https://github.com/huggingface/transformers@v4.49.0-SmolVLM-2
# from transformers import AutoProcessor, AutoModelForImageTextToText
# import torch
# 
# processor = AutoProcessor.from_pretrained(model_path)
# model = AutoModelForImageTextToText.from_pretrained(
#     model_path,
#     torch_dtype=torch.bfloat16,
#     _attn_implementation="flash_attention_2"
# ).to("cuda")

# NEW MLX-optimized approach for Apple Silicon
import sys
from pathlib import Path

print("⚠️  DEPRECATED: This file has been reorganized for Apple Silicon optimization")
print("🔄 Please use the new MLX-optimized structure:")
print("   • Server: python start_server.py")
print("   • Image: python inference/single_image.py")
print("   • Video: python inference/video_processing.py")
print("   • Multi-image: python inference/multi_image.py")
print("\n📚 See README.md for complete usage instructions")

# Redirect to new structure
if __name__ == "__main__":
    print("\n🚀 Starting new MLX-optimized server...")
    import subprocess
    subprocess.run([sys.executable, "start_server.py"] + sys.argv[1:])

