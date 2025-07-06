#!/usr/bin/env python3
"""
Basic Inference Example for SmolVLM2-500M-Video-Instruct
Demonstrates common usage patterns with the custom model wrapper
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from model_wrapper import SmolVLM2Wrapper
from PIL import Image, ImageDraw, ImageFont

def create_sample_images():
    """Create sample images for testing"""
    print("🎨 Creating sample images...")
    
    # Create results directory if it doesn't exist
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Simple object image
    img1 = Image.new('RGB', (400, 300), color='lightblue')
    draw1 = ImageDraw.Draw(img1)
    draw1.ellipse([150, 100, 250, 200], fill='red', outline='darkred', width=3)
    draw1.text((160, 220), "Red Circle", fill='black')
    img1.save(results_dir / "sample_circle.png")
    
    # Text document image
    img2 = Image.new('RGB', (500, 300), color='white')
    draw2 = ImageDraw.Draw(img2)
    draw2.text((50, 50), "COMPANY MEMO", fill='red')
    draw2.text((50, 100), "To: All Staff", fill='black')
    draw2.text((50, 130), "From: Management", fill='black')
    draw2.text((50, 160), "Date: January 27, 2025", fill='blue')
    draw2.text((50, 190), "Subject: Important Update", fill='green')
    draw2.text((50, 220), "Please review the new guidelines.", fill='black')
    img2.save(results_dir / "sample_document.png")
    
    # Complex scene image
    img3 = Image.new('RGB', (400, 300), color='lightgreen')
    draw3 = ImageDraw.Draw(img3)
    # Multiple shapes
    draw3.rectangle([50, 50, 150, 150], fill='blue', outline='navy', width=2)
    draw3.ellipse([200, 80, 300, 180], fill='yellow', outline='orange', width=2)
    draw3.polygon([(320, 200), (370, 150), (370, 250)], fill='purple', outline='indigo')
    draw3.text((50, 250), "Geometric Shapes Scene", fill='black')
    img3.save(results_dir / "sample_complex.png")
    
    print(f"✅ Sample images saved to: {results_dir}")
    return [
        results_dir / "sample_circle.png",
        results_dir / "sample_document.png", 
        results_dir / "sample_complex.png"
    ]

def text_examples(wrapper):
    """Demonstrate text processing capabilities"""
    print("\n" + "="*60)
    print("📝 TEXT PROCESSING EXAMPLES")
    print("="*60)
    
    text_prompts = [
        "What are the three primary colors in art?",
        "Explain the difference between AI and machine learning in simple terms.",
        "Write a short creative story about a robot discovering music.",
        "Solve this math problem: If a pizza has 8 slices and 3 people share it equally, how many slices does each person get?",
        "List 5 benefits of renewable energy sources."
    ]
    
    for i, prompt in enumerate(text_prompts, 1):
        print(f"\n🔤 Example {i}: {prompt}")
        result = wrapper.text_query(prompt, max_tokens=120)
        print(f"💭 Response: {result['response']}")
        print(f"⏱️  Time: {result['inference_time']:.2f}s | Tokens: {result['token_count']}")

def image_examples(wrapper, image_paths):
    """Demonstrate image processing capabilities"""
    print("\n" + "="*60)
    print("🖼️  IMAGE PROCESSING EXAMPLES")
    print("="*60)
    
    image_tasks = [
        {
            "image": image_paths[0],
            "prompts": [
                "What do you see in this image?",
                "What color is the circle?",
                "Describe the background of this image."
            ]
        },
        {
            "image": image_paths[1], 
            "prompts": [
                "What text can you read in this image?",
                "What is the date mentioned in this document?",
                "Who is this memo addressed to?"
            ]
        },
        {
            "image": image_paths[2],
            "prompts": [
                "How many geometric shapes are in this image?",
                "What colors are the shapes?",
                "Describe the layout of objects in this image."
            ]
        }
    ]
    
    for i, task in enumerate(image_tasks, 1):
        print(f"\n🖼️  Image {i}: {task['image'].name}")
        
        for j, prompt in enumerate(task['prompts'], 1):
            print(f"\n  📝 Question {j}: {prompt}")
            result = wrapper.image_query(task['image'], prompt, max_tokens=100)
            print(f"  💭 Response: {result['response']}")
            print(f"  ⏱️  Time: {result['inference_time']:.2f}s | Image: {result['image_size']}")

def batch_processing_example(wrapper, image_paths):
    """Demonstrate batch processing capabilities"""
    print("\n" + "="*60)
    print("🔄 BATCH PROCESSING EXAMPLE")
    print("="*60)
    
    batch_tasks = [
        {"type": "text", "prompt": "What is artificial intelligence?"},
        {"type": "image", "image": image_paths[0], "prompt": "Identify the main object in this image."},
        {"type": "text", "prompt": "Name three benefits of exercise."},
        {"type": "image", "image": image_paths[1], "prompt": "Extract the key information from this document."}
    ]
    
    print(f"Processing {len(batch_tasks)} tasks in batch...")
    results = wrapper.batch_process(batch_tasks)
    
    print(f"\n📊 Batch Results Summary:")
    successful = sum(1 for r in results if r['success'])
    print(f"   ✅ Successful: {successful}/{len(results)}")
    
    total_time = sum(r.get('inference_time', 0) for r in results if r['success'])
    print(f"   ⏱️  Total time: {total_time:.2f}s")
    print(f"   📈 Average time: {total_time/successful:.2f}s per task")

def performance_analysis(wrapper):
    """Analyze model performance"""
    print("\n" + "="*60)
    print("📊 PERFORMANCE ANALYSIS")
    print("="*60)
    
    # Get model information
    info = wrapper.get_model_info()
    print("🔧 Model Configuration:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Quick performance test
    print(f"\n⚡ Quick Performance Test:")
    
    # Text speed test
    start_time = __import__('time').time()
    wrapper.text_query("Test prompt for speed measurement", max_tokens=50)
    text_speed = __import__('time').time() - start_time
    
    # Image speed test  
    test_img = Image.new('RGB', (200, 200), color='blue')
    start_time = __import__('time').time()
    wrapper.image_query(test_img, "Test image query", max_tokens=50)
    image_speed = __import__('time').time() - start_time
    
    print(f"   📝 Text processing speed: {text_speed:.2f}s")
    print(f"   🖼️  Image processing speed: {image_speed:.2f}s")
    print(f"   🎯 Performance rating: {'EXCELLENT' if text_speed < 3 and image_speed < 5 else 'GOOD' if text_speed < 5 and image_speed < 8 else 'ACCEPTABLE'}")

def main():
    """Main demonstration function"""
    print("🎯 SmolVLM2-500M-Video-Instruct Basic Inference Examples")
    print("=" * 60)
    
    # Initialize wrapper
    print("🔧 Initializing model wrapper...")
    wrapper = SmolVLM2Wrapper()
    
    # Load model
    print("📥 Loading model...")
    load_times = wrapper.load_model()
    print(f"✅ Model loaded successfully in {load_times['total_time']:.2f}s")
    
    # Create sample images
    image_paths = create_sample_images()
    
    # Run examples
    try:
        text_examples(wrapper)
        image_examples(wrapper, image_paths)
        batch_processing_example(wrapper, image_paths)
        performance_analysis(wrapper)
        
        print(f"\n🎉 All examples completed successfully!")
        print(f"📁 Check the results/ folder for sample images and outputs.")
        
    except Exception as e:
        print(f"\n❌ Error during examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 