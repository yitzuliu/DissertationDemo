#!/usr/bin/env python3
"""
SmolVLM2 Model Testing Script

This script tests the SmolVLM2 model with various tasks:
- Single image description
- Visual question answering
- Multiple image processing
- Video inference capabilities

Usage:
    python test_smolvlm2.py
"""

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
from transformers.image_utils import load_image
import os
import time

class SmolVLM2Tester:
    def __init__(self):
        """Initialize the SmolVLM2 model and processor."""
        print("🚀 Initializing SmolVLM2 Model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Initialize processor and model
        self.processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-Instruct")
        self.model = AutoModelForVision2Seq.from_pretrained(
            "HuggingFaceTB/SmolVLM-Instruct",
            torch_dtype=torch.bfloat16,
            _attn_implementation="flash_attention_2" if self.device == "cuda" else "eager",
        ).to(self.device)
        
        print("✅ Model loaded successfully!")
    
    def generate_response(self, messages, images, max_new_tokens=500):
        """Generate a response from the model."""
        # Prepare inputs
        prompt = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(text=prompt, images=images, return_tensors="pt")
        inputs = inputs.to(self.device)
        
        # Generate outputs
        start_time = time.time()
        generated_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        generation_time = time.time() - start_time
        
        generated_texts = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )
        
        return generated_texts[0], generation_time
    
    def test_single_image_description(self, image_path):
        """Test single image description."""
        print(f"\n📸 Testing Single Image Description with: {image_path}")
        print("-" * 60)
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return
            
        try:
            image = Image.open(image_path)
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": "Describe this image in detail."}
                    ]
                }
            ]
            
            response, gen_time = self.generate_response(messages, [image])
            print(f"Response (generated in {gen_time:.2f}s):")
            print(response)
            
        except Exception as e:
            print(f"❌ Error processing image: {e}")
    
    def test_visual_qa(self, image_path):
        """Test visual question answering."""
        print(f"\n❓ Testing Visual Question Answering with: {image_path}")
        print("-" * 60)
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return
            
        try:
            image = Image.open(image_path)
            
            questions = [
                "What objects can you see in this image?",
                "What colors are prominent in this image?",
                "What might be the setting or location of this image?",
                "Are there any people in this image?",
                "What's the mood or atmosphere of this image?"
            ]
            
            for question in questions:
                print(f"\nQ: {question}")
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image"},
                            {"type": "text", "text": question}
                        ]
                    }
                ]
                
                response, gen_time = self.generate_response(messages, [image], max_new_tokens=200)
                print(f"A: {response} (generated in {gen_time:.2f}s)")
                
        except Exception as e:
            print(f"❌ Error in visual QA: {e}")
    
    def test_multiple_images(self, image_paths):
        """Test multiple image processing."""
        print(f"\n🖼️ Testing Multiple Image Processing")
        print("-" * 60)
        
        valid_images = []
        for path in image_paths:
            if os.path.exists(path):
                valid_images.append(Image.open(path))
                print(f"✅ Loaded: {path}")
            else:
                print(f"❌ Not found: {path}")
        
        if len(valid_images) < 2:
            print("❌ Need at least 2 images for multiple image testing")
            return
        
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "image"},
                        {"type": "text", "text": "Compare these two images. What are the similarities and differences?"}
                    ]
                }
            ]
            
            response, gen_time = self.generate_response(messages, valid_images[:2])
            print(f"\nComparison Response (generated in {gen_time:.2f}s):")
            print(response)
            
        except Exception as e:
            print(f"❌ Error in multiple image processing: {e}")
    
    def test_creative_tasks(self, image_path):
        """Test creative tasks like storytelling."""
        print(f"\n✨ Testing Creative Tasks with: {image_path}")
        print("-" * 60)
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return
            
        try:
            image = Image.open(image_path)
            
            creative_prompts = [
                "Write a short story inspired by this image.",
                "Create a poem based on what you see in this image.",
                "Imagine what happened just before this moment captured in the image."
            ]
            
            for prompt in creative_prompts:
                print(f"\nPrompt: {prompt}")
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image"},
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
                
                response, gen_time = self.generate_response(messages, [image], max_new_tokens=300)
                print(f"Response (generated in {gen_time:.2f}s):")
                print(response)
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ Error in creative tasks: {e}")
    
    def test_with_online_images(self):
        """Test with online images as shown in the documentation."""
        print(f"\n🌐 Testing with Online Images")
        print("-" * 60)
        
        try:
            # Load images from URLs
            image1 = load_image("https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg")
            image2 = load_image("https://huggingface.co/spaces/merve/chameleon-7b/resolve/main/bee.jpg")
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "image"},
                        {"type": "text", "text": "Can you describe these two images and tell me what they represent?"}
                    ]
                },
            ]
            
            response, gen_time = self.generate_response(messages, [image1, image2])
            print(f"Response (generated in {gen_time:.2f}s):")
            print(response)
            
        except Exception as e:
            print(f"❌ Error loading online images: {e}")
            print("This might be due to network connectivity issues.")

def main():
    """Main testing function."""
    print("🤏 SmolVLM2 Model Testing Suite")
    print("=" * 60)
    
    # Initialize tester
    try:
        tester = SmolVLM2Tester()
    except Exception as e:
        print(f"❌ Failed to initialize model: {e}")
        print("Make sure you have transformers, torch, and PIL installed:")
        print("pip install transformers torch pillow")
        return
    
    # Define test image paths
    test_images = [
        "src/models/phi3_vision/debug/images/test_image.png",
        "src/models/phi3_vision/debug/images/sample.jpg",
        "src/models/phi3_vision/debug/images/test.jpg",
        "src/models/phi3_vision/debug/images/IMG_0119.JPG"
    ]
    
    # Test 1: Single image description
    for image_path in test_images:
        if os.path.exists(image_path):
            tester.test_single_image_description(image_path)
            break
    
    # Test 2: Visual Question Answering
    for image_path in test_images:
        if os.path.exists(image_path):
            tester.test_visual_qa(image_path)
            break
    
    # Test 3: Multiple images
    available_images = [path for path in test_images if os.path.exists(path)]
    if len(available_images) >= 2:
        tester.test_multiple_images(available_images[:2])
    
    # Test 4: Creative tasks
    for image_path in test_images:
        if os.path.exists(image_path):
            tester.test_creative_tasks(image_path)
            break
    
    # Test 5: Online images (if network available)
    tester.test_with_online_images()
    
    print("\n🎉 Testing completed!")
    print("\nTo test video inference, check out:")
    print("src/models/smolvlm2/smollm/tools/smolvlm_local_inference/SmolVLM_video_inference.py")

if __name__ == "__main__":
    main() 