#!/usr/bin/env python3
"""
Unified SmolVLM2-500M Testing Suite - MPS Optimized

Combined testing script with all approaches, optimized for Apple Silicon MPS acceleration.
Combines functionality from test_video_smolvlm2.py, simple_video_test.py, 
quick_test_smolvlm2.py, and direct_video_test.py.
"""

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText
import os
import cv2
import time

# Force MPS usage since we know it's optimal for Apple Silicon
DEVICE = "mps"
MODEL_PATH = "./SmolVLM2-500M-Video-Instruct"
VIDEO_PATH = "../../../src/debug/viedo/Generated File June 24, 2025 - 5_04PM.mp4"
IMAGE_PATHS = [
    "../../../src/debug/images/IMG_0119.JPG",
    "../../../src/debug/images/test_image.png", 
    "../../../src/debug/images/sample.jpg",
    "../../../src/debug/images/test.jpg"
]

def load_model():
    """Load SmolVLM2 model with MPS optimization."""
    print("🍎 SmolVLM2-500M Unified Test Suite - MPS Accelerated")
    print("=" * 60)
    print("🔧 Hardware: Apple Silicon with MPS acceleration")
    print("📊 Model: SmolVLM2-500M-Video-Instruct (500M params)")
    print()
    
    start_time = time.time()
    print("🔄 Loading model...")
    
    try:
        processor = AutoProcessor.from_pretrained(MODEL_PATH)
        model = AutoModelForImageTextToText.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float32,  # MPS-optimized
            device_map=None
        )
        model = model.to(DEVICE)
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f}s on {DEVICE}")
        print()
        
        return processor, model
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None, None

def extract_video_frames(video_path, max_frames=8, target_fps=1):
    """Extract frames from video."""
    print(f"📹 Extracting frames from video...")
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return []
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📊 Video: {total_frames} frames, {fps:.1f}FPS, {duration:.1f}s, {width}x{height}")
    
    frame_interval = max(1, int(fps / target_fps))
    frames = []
    frame_count = 0
    
    while len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            frames.append(pil_image)
        
        frame_count += 1
    
    cap.release()
    print(f"✅ Extracted {len(frames)} frames")
    return frames

def generate_response(processor, model, messages, max_tokens=150):
    """Generate response with MPS optimization."""
    start_time = time.time()
    
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    
    # MPS-optimized tensor handling
    inputs = {k: v.to(DEVICE, dtype=torch.float32 if v.dtype.is_floating_point else v.dtype) 
             for k, v in inputs.items()}
    
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.7,
            pad_token_id=processor.tokenizer.eos_token_id
        )
    
    generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
    inference_time = time.time() - start_time
    
    # Extract clean response
    full_response = generated_texts[0]
    if "Assistant:" in full_response:
        response = full_response.split("Assistant:")[-1].strip()
    else:
        response = full_response
    
    return response, inference_time

def test_image_analysis(processor, model):
    """Test image analysis capabilities."""
    print("🖼️ IMAGE ANALYSIS TEST")
    print("-" * 40)
    
    available_images = [path for path in IMAGE_PATHS if os.path.exists(path)]
    
    if not available_images:
        print("❌ No test images found")
        return
    
    for i, img_path in enumerate(available_images[:2], 1):
        print(f"\n📸 Image {i}: {os.path.basename(img_path)}")
        
        try:
            image = Image.open(img_path)
            file_size = os.path.getsize(img_path) / 1024
            print(f"📊 Size: {image.size}, {file_size:.1f}KB")
            
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": "Describe what you see in this image in detail."}
                ]
            }]
            
            response, inference_time = generate_response(processor, model, messages)
            
            print(f"⚡ Time: {inference_time:.2f}s")
            print(f"🤖 Response: {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_single_frame_video(processor, model):
    """Test single frame from video."""
    print("🎬 SINGLE FRAME VIDEO TEST")
    print("-" * 40)
    
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video not found: {VIDEO_PATH}")
        return
    
    try:
        cap = cv2.VideoCapture(VIDEO_PATH)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("❌ Could not read frame")
            return
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        
        print(f"📸 Frame extracted: {image.size}")
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": "Describe what you see in this frame from the video."}
            ]
        }]
        
        response, inference_time = generate_response(processor, model, messages)
        
        print(f"⚡ Time: {inference_time:.2f}s")
        print(f"🤖 Response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multi_frame_video(processor, model):
    """Test multiple frames as images."""
    print("🎥 MULTI-FRAME VIDEO TEST")
    print("-" * 40)
    
    frames = extract_video_frames(VIDEO_PATH, max_frames=8)
    
    if not frames:
        print("❌ No frames extracted")
        return
    
    try:
        content = [{"type": "text", "text": "Describe what happens across these video frames."}]
        for frame in frames:
            content.append({"type": "image", "image": frame})
        
        messages = [{"role": "user", "content": content}]
        
        response, inference_time = generate_response(processor, model, messages, max_tokens=200)
        
        print(f"⚡ Time: {inference_time:.2f}s")
        print(f"🤖 Response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_direct_video(processor, model):
    """Test direct video path (README format)."""
    print("📹 DIRECT VIDEO TEST (README Format)")
    print("-" * 40)
    
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video not found: {VIDEO_PATH}")
        return
    
    video_abs_path = os.path.abspath(VIDEO_PATH)
    video_size = os.path.getsize(video_abs_path) / 1024 / 1024
    print(f"📹 Video: {video_size:.1f}MB")
    
    try:
        messages = [{
            "role": "user",
            "content": [
                {"type": "video", "path": video_abs_path},
                {"type": "text", "text": "Describe this video in detail"}
            ]
        }]
        
        response, inference_time = generate_response(processor, model, messages, max_tokens=200)
        
        print(f"⚡ Time: {inference_time:.2f}s")
        print(f"🤖 Response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if "pyav" in str(e).lower():
            print("💡 Install PyAV: pip install av")

def show_memory_usage():
    """Show MPS memory usage."""
    try:
        memory_used = torch.mps.current_allocated_memory() / 1024**3
        print(f"📊 MPS Memory: {memory_used:.2f} GB")
    except:
        print("📊 Memory monitoring unavailable")

def run_comprehensive_test():
    """Run all test categories."""
    processor, model = load_model()
    if not processor or not model:
        return
    
    print("🧪 COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    
    # Test 1: Images
    test_image_analysis(processor, model)
    show_memory_usage()
    
    print("\n" + "="*50)
    
    # Test 2: Single frame
    test_single_frame_video(processor, model)
    show_memory_usage()
    
    print("\n" + "="*50)
    
    # Test 3: Multi-frame
    test_multi_frame_video(processor, model)
    show_memory_usage()
    
    print("\n" + "="*50)
    
    # Test 4: Direct video
    test_direct_video(processor, model)
    show_memory_usage()
    
    print("\n" + "="*50)
    print("✅ ALL TESTS COMPLETE")

def run_quick_test():
    """Run quick representative test."""
    processor, model = load_model()
    if not processor or not model:
        return
    
    print("⚡ QUICK TEST")
    print("=" * 30)
    
    # Quick image test
    test_image_analysis(processor, model)
    
    print("\n" + "-"*30)
    
    # Quick video test
    test_direct_video(processor, model)
    
    print("\n" + "="*30)
    print("✅ QUICK TEST COMPLETE")
    show_memory_usage()

def main():
    """Main interface."""
    print("🎬 SmolVLM2-500M Unified Testing Suite")
    print("🍎 Apple Silicon MPS Optimized")
    print("=" * 50)
    print()
    print("Test Options:")
    print("1. Comprehensive Test (all categories)")
    print("2. Quick Test (samples)")
    print("3. Image Analysis Only") 
    print("4. Video Tests Only")
    print("5. Frame Preview Only")
    
    choice = input("\nChoice (1-5): ").strip()
    
    if choice == "1":
        run_comprehensive_test()
    elif choice == "2":
        run_quick_test()
    elif choice == "3":
        processor, model = load_model()
        if processor and model:
            test_image_analysis(processor, model)
            show_memory_usage()
    elif choice == "4":
        processor, model = load_model()
        if processor and model:
            test_single_frame_video(processor, model)
            print("\n" + "-"*40)
            test_multi_frame_video(processor, model)
            print("\n" + "-"*40)
            test_direct_video(processor, model)
            show_memory_usage()
    elif choice == "5":
        frames = extract_video_frames(VIDEO_PATH, max_frames=5)
        if frames:
            print(f"🖼️ Extracted {len(frames)} frames:")
            for i, frame in enumerate(frames, 1):
                print(f"Frame {i}: {frame.size}")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 