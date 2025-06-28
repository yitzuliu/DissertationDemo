#!/usr/bin/env python3
"""
Comprehensive SmolVLM2-500M-Video-Instruct Testing Suite

Combined testing script for SmolVLM2-500M-Video-Instruct model with optimized MPS acceleration.
Includes image, video, and multi-modal testing capabilities.

Environment: Apple Silicon with MPS acceleration
Model: SmolVLM2-500M-Video-Instruct (1.9GB, 500M parameters)
"""

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText
import os
import cv2
import numpy as np
from pathlib import Path
import time
from typing import Optional, List

class SmolVLM2TestSuite:
    """Comprehensive testing suite for SmolVLM2-500M-Video-Instruct."""
    
    def __init__(self):
        """Initialize the test suite with MPS optimization."""
        self.device = "mps"  # Force MPS for optimal Apple Silicon performance
        self.model: Optional[AutoModelForImageTextToText] = None
        self.processor: Optional[AutoProcessor] = None
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(script_dir, "SmolVLM2-500M-Video-Instruct")
        self.video_path = os.path.join(script_dir, "../../../src/debug/viedo/Generated File June 24, 2025 - 5_04PM.mp4")
        self.image_paths = [
            os.path.join(script_dir, "../../../src/debug/images/IMG_0119.JPG"),
            os.path.join(script_dir, "../../../src/debug/images/test_image.png"),
            os.path.join(script_dir, "../../../src/debug/images/sample.jpg"),
            os.path.join(script_dir, "../../../src/debug/images/test.jpg")
        ]
        
    def load_model(self):
        """Load SmolVLM2 model with MPS optimization."""
        print("🍎 SmolVLM2-500M Test Suite - MPS Accelerated")
        print("=" * 60)
        print("🔧 Hardware: Apple Silicon with MPS acceleration")
        print("📊 Model: SmolVLM2-500M-Video-Instruct (500M params, 1.9GB)")
        print()
        
        start_time = time.time()
        print("🔄 Loading SmolVLM2-500M-Video-Instruct model...")
        
        try:
            # Load processor
            processor_start = time.time()
            self.processor = AutoProcessor.from_pretrained(self.model_path)
            processor_time = time.time() - processor_start
            
            # Load model with MPS-optimized settings
            model_start = time.time()
            self.model = AutoModelForImageTextToText.from_pretrained(
                self.model_path,
                torch_dtype=torch.float32,  # MPS-optimized precision
                device_map=None,  # Manual device management for MPS
            )
            self.model = self.model.to(self.device)
            model_time = time.time() - model_start
            
            total_time = time.time() - start_time
            
            print(f"✅ Processor loaded: {processor_time:.2f}s")
            print(f"✅ Model loaded: {model_time:.2f}s")
            print(f"✅ Total loading time: {total_time:.2f}s")
            print(f"🚀 Device: {self.device} (MPS acceleration active)")
            print()
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
        
        return True
    
    def extract_video_frames(self, video_path, max_frames=64, target_fps=1):
        """Extract frames from video for SmolVLM2 processing."""
        print(f"📹 Extracting frames from video...")
        
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Could not open video file: {video_path}")
            return []
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📊 Video: {total_frames} frames, {fps:.1f} FPS, {duration:.1f}s, {width}x{height}")
        
        # Calculate frame sampling interval
        frame_interval = max(1, int(fps / target_fps))
        
        frames = []
        frame_count = 0
        
        while len(frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)
            
            frame_count += 1
        
        cap.release()
        print(f"✅ Extracted {len(frames)} frames for processing")
        return frames
    
    def test_image_analysis(self):
        """Test SmolVLM2 with image analysis."""
        print("🖼️ IMAGE ANALYSIS TESTING")
        print("-" * 40)
        
        # Find available test images
        available_images = []
        for img_path in self.image_paths:
            if os.path.exists(img_path):
                available_images.append(img_path)
        
        if not available_images:
            print("❌ No test images found")
            return
        
        test_prompts = [
            "Describe what you see in this image in detail.",
            "What objects are visible in this image?",
            "What colors and textures can you identify?",
            "Is there any text visible in this image?",
            "What is the overall scene or setting?"
        ]
        
        for i, img_path in enumerate(available_images[:2], 1):  # Test first 2 images
            print(f"\n📸 Image Test {i}: {os.path.basename(img_path)}")
            
            try:
                # Load image
                image = Image.open(img_path)
                file_size = os.path.getsize(img_path) / 1024  # KB
                print(f"📊 Size: {image.size}, {file_size:.1f}KB")
                
                # Test with a representative prompt
                prompt = test_prompts[0]  # Use first prompt for images
                
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": image},
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
                
                # Process and generate
                start_time = time.time()
                inputs = self.processor.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    tokenize=True,
                    return_dict=True,
                    return_tensors="pt",
                )
                inputs = {k: v.to(self.device, dtype=torch.float32 if v.dtype.is_floating_point else v.dtype) 
                         for k, v in inputs.items()}
                
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        **inputs,
                        max_new_tokens=150,
                        do_sample=True,
                        temperature=0.7,
                        pad_token_id=self.processor.tokenizer.eos_token_id
                    )
                
                generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
                inference_time = time.time() - start_time
                
                # Extract response
                full_response = generated_texts[0]
                if "Assistant:" in full_response:
                    response = full_response.split("Assistant:")[-1].strip()
                else:
                    response = full_response
                
                print(f"⚡ Inference time: {inference_time:.2f}s")
                print(f"🤖 Response: {response}")
                
            except Exception as e:
                print(f"❌ Error processing image {i}: {e}")
    
    def test_single_frame_video(self):
        """Test SmolVLM2 with single frame from video."""
        print("🎬 SINGLE FRAME VIDEO TESTING")
        print("-" * 40)
        
        if not os.path.exists(self.video_path):
            print(f"❌ Video file not found: {self.video_path}")
            return
        
        try:
            # Extract first frame
            cap = cv2.VideoCapture(self.video_path)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                print("❌ Could not read frame from video")
                return
            
            # Convert to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            
            print(f"📸 Extracted single frame: {image.size}")
            
            prompt = "Describe what you see in this frame from the video."
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Process and generate
            start_time = time.time()
            inputs = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            )
            inputs = {k: v.to(self.device, dtype=torch.float32 if v.dtype.is_floating_point else v.dtype) 
                     for k, v in inputs.items()}
            
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
            inference_time = time.time() - start_time
            
            # Extract response
            full_response = generated_texts[0]
            if "Assistant:" in full_response:
                response = full_response.split("Assistant:")[-1].strip()
            else:
                response = full_response
            
            print(f"⚡ Inference time: {inference_time:.2f}s")
            print(f"🤖 Response: {response}")
            
        except Exception as e:
            print(f"❌ Error in single frame test: {e}")
    
    def test_multi_frame_video(self):
        """Test SmolVLM2 with multiple frames as images."""
        print("🎥 MULTI-FRAME VIDEO TESTING (Frame Extraction)")
        print("-" * 40)
        
        frames = self.extract_video_frames(self.video_path, max_frames=8, target_fps=1)
        
        if not frames:
            print("❌ No frames extracted from video")
            return
        
        test_prompts = [
            "Describe what happens across these video frames.",
            "What objects do you see in these frames?",
            "What is the main activity taking place?",
            "Describe any changes or movements you notice."
        ]
        
        for i, prompt in enumerate(test_prompts[:2], 1):  # Test first 2 prompts
            print(f"\n🔍 Multi-frame Test {i}: {prompt}")
            
            try:
                # Create message with multiple image tokens
                content = [{"type": "text", "text": prompt}]
                for frame in frames:
                    content.append({"type": "image", "image": frame})
                
                messages = [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
                
                # Process and generate
                start_time = time.time()
                inputs = self.processor.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    tokenize=True,
                    return_dict=True,
                    return_tensors="pt",
                )
                inputs = {k: v.to(self.device, dtype=torch.float32 if v.dtype.is_floating_point else v.dtype) 
                         for k, v in inputs.items()}
                
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        **inputs,
                        max_new_tokens=200,
                        do_sample=True,
                        temperature=0.7,
                        pad_token_id=self.processor.tokenizer.eos_token_id
                    )
                
                generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
                inference_time = time.time() - start_time
                
                # Extract response
                full_response = generated_texts[0]
                if "Assistant:" in full_response:
                    response = full_response.split("Assistant:")[-1].strip()
                else:
                    response = full_response
                
                print(f"⚡ Inference time: {inference_time:.2f}s")
                print(f"🤖 Response: {response}")
                
            except Exception as e:
                print(f"❌ Error in multi-frame test {i}: {e}")
    
    def test_direct_video(self):
        """Test SmolVLM2 with direct video path (README format)."""
        print("📹 DIRECT VIDEO TESTING (README Format)")
        print("-" * 40)
        
        if not os.path.exists(self.video_path):
            print(f"❌ Video file not found: {self.video_path}")
            return
        
        video_abs_path = os.path.abspath(self.video_path)
        video_size = os.path.getsize(video_abs_path) / 1024 / 1024  # MB
        print(f"📹 Video: {video_size:.1f}MB - {os.path.basename(video_abs_path)}")
        
        test_prompts = [
            "Describe this video in detail",
            "What is happening in this video?",
            "What objects do you see in this video?"
        ]
        
        for i, prompt in enumerate(test_prompts[:2], 1):  # Test first 2 prompts
            print(f"\n🔍 Direct Video Test {i}: {prompt}")
            
            try:
                # Using exact README format
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "video", "path": video_abs_path},
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
                
                # Process and generate
                start_time = time.time()
                inputs = self.processor.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    tokenize=True,
                    return_dict=True,
                    return_tensors="pt",
                )
                
                # MPS-optimized input handling
                inputs = {k: v.to(self.device, dtype=torch.float32 if v.dtype.is_floating_point else v.dtype) 
                         for k, v in inputs.items()}
                
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        **inputs,
                        do_sample=True,
                        temperature=0.7,
                        max_new_tokens=200,
                        pad_token_id=self.processor.tokenizer.eos_token_id
                    )
                
                generated_texts = self.processor.batch_decode(
                    generated_ids,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True
                )
                inference_time = time.time() - start_time
                
                # Extract response
                full_response = generated_texts[0]
                if "Assistant:" in full_response:
                    response = full_response.split("Assistant:")[-1].strip()
                else:
                    response = full_response
                
                print(f"⚡ Inference time: {inference_time:.2f}s")
                print(f"🤖 Response: {response}")
                
            except Exception as e:
                print(f"❌ Error in direct video test {i}: {e}")
                if "pyav" in str(e).lower() or "av" in str(e).lower():
                    print("💡 Hint: Make sure PyAV is installed: pip install av")
    
    def show_memory_usage(self):
        """Display current MPS memory usage."""
        try:
            memory_used = torch.mps.current_allocated_memory() / 1024**3
            print(f"\n📊 MPS Memory Usage: {memory_used:.2f} GB")
        except:
            print("\n📊 Memory monitoring not available")
    
    def run_comprehensive_test(self):
        """Run all test categories."""
        if not self.load_model():
            return
        
        print("🧪 COMPREHENSIVE SMOLVLM2 TESTING SUITE")
        print("=" * 60)
        
        # Test 1: Image Analysis
        try:
            self.test_image_analysis()
            self.show_memory_usage()
        except Exception as e:
            print(f"❌ Image testing failed: {e}")
        
        print("\n" + "="*60)
        
        # Test 2: Single Frame Video
        try:
            self.test_single_frame_video()
            self.show_memory_usage()
        except Exception as e:
            print(f"❌ Single frame testing failed: {e}")
        
        print("\n" + "="*60)
        
        # Test 3: Multi-Frame Video
        try:
            self.test_multi_frame_video()
            self.show_memory_usage()
        except Exception as e:
            print(f"❌ Multi-frame testing failed: {e}")
        
        print("\n" + "="*60)
        
        # Test 4: Direct Video (README format)
        try:
            self.test_direct_video()
            self.show_memory_usage()
        except Exception as e:
            print(f"❌ Direct video testing failed: {e}")
        
        print("\n" + "="*60)
        print("✅ COMPREHENSIVE TESTING COMPLETE")
        self.show_memory_usage()
    
    def run_quick_test(self):
        """Run a quick test with one example from each category."""
        if not self.load_model():
            return
        
        print("⚡ QUICK SMOLVLM2 TEST")
        print("=" * 40)
        
        # Quick image test
        try:
            print("📸 Quick Image Test...")
            self.test_image_analysis()
        except Exception as e:
            print(f"❌ Quick image test failed: {e}")
        
        print("\n" + "-"*40)
        
        # Quick video test (direct method)
        try:
            print("🎬 Quick Video Test...")
            self.test_direct_video()
        except Exception as e:
            print(f"❌ Quick video test failed: {e}")
        
        print("\n" + "="*40)
        print("✅ QUICK TEST COMPLETE")
        self.show_memory_usage()


def main():
    """Main testing interface."""
    test_suite = SmolVLM2TestSuite()
    
    print("🎬 SmolVLM2-500M-Video-Instruct Testing Suite")
    print("=" * 50)
    print("🍎 Optimized for Apple Silicon with MPS acceleration")
    print()
    print("Testing Options:")
    print("1. Comprehensive Test (all categories)")
    print("2. Quick Test (representative samples)")
    print("3. Image Analysis Only")
    print("4. Video Testing Only (all methods)")
    print("5. Direct Video Test (README format)")
    print("6. Frame Extraction Preview")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        test_suite.run_comprehensive_test()
    elif choice == "2":
        test_suite.run_quick_test()
    elif choice == "3":
        if test_suite.load_model():
            test_suite.test_image_analysis()
            test_suite.show_memory_usage()
    elif choice == "4":
        if test_suite.load_model():
            test_suite.test_single_frame_video()
            print("\n" + "-"*40)
            test_suite.test_multi_frame_video()
            print("\n" + "-"*40)
            test_suite.test_direct_video()
            test_suite.show_memory_usage()
    elif choice == "5":
        if test_suite.load_model():
            test_suite.test_direct_video()
            test_suite.show_memory_usage()
    elif choice == "6":
        frames = test_suite.extract_video_frames(test_suite.video_path, max_frames=5)
        if frames:
            print(f"\n🖼️ Frame Preview: {len(frames)} frames extracted")
            for i, frame in enumerate(frames):
                print(f"Frame {i+1}: {frame.size} pixels")
    else:
        print("❌ Invalid choice. Please run the script again.")


if __name__ == "__main__":
    main() 