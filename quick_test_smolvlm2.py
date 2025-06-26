#!/usr/bin/env python3
"""
Quick SmolVLM2 Test Script

A lightweight script to quickly test SmolVLM2 with a single image.
"""

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
import os

def quick_test():
    """Quick test of SmolVLM2 with a single image."""
    print("🚀 Quick SmolVLM2 Test")
    print("-" * 40)
    
    # Check device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Find an available test image
    test_images = [
        "src/models/phi3_vision/debug/images/IMG_0119.jpg"
    ]
        #     "src/models/phi3_vision/debug/images/sample.jpg",
        # "src/models/phi3_vision/debug/images/test.jpg"
    
    image_path = None
    for path in test_images:
        if os.path.exists(path):
            image_path = path
            break
    
    if not image_path:
        print("❌ No test images found. Please check the image paths.")
        return
    
    print(f"📸 Using image: {image_path}")
    
    try:
        # Load model
        print("Loading model...")
        processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-Instruct")
        model = AutoModelForVision2Seq.from_pretrained(
            "HuggingFaceTB/SmolVLM-Instruct",
            torch_dtype=torch.bfloat16,
            _attn_implementation="flash_attention_2" if device == "cuda" else "eager",
        ).to(device)
        
        # Load image
        image = Image.open(image_path)
        
        # Create message
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": "What do you see in this image?"}
                ]
            }
        ]
        
        # Process and generate
        print("Processing image...")
        prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(text=prompt, images=[image], return_tensors="pt")
        inputs = inputs.to(device)
        
        print("Generating response...")
        generated_ids = model.generate(**inputs, max_new_tokens=200)
        generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
        
        print("\n✅ Response:")
        print(generated_texts[0])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have the required packages: pip install -r smolvlm2_requirements.txt")
        print("2. Check your internet connection (model needs to be downloaded)")
        print("3. Ensure you have enough disk space and memory")

if __name__ == "__main__":
    quick_test() 