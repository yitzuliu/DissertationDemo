#!/usr/bin/env python3
"""
SmolVLM2-500M-Video-Instruct MPS vs CPU Performance Comparison
Simple test to compare Apple Silicon GPU (MPS) vs CPU inference speed
"""

import torch
import time
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image, ImageDraw
import os

def create_test_image():
    """Create a simple test image for consistent comparison"""
    img = Image.new('RGB', (400, 300), color='lightblue')
    draw = ImageDraw.Draw(img)
    draw.ellipse([150, 100, 250, 200], fill='red', outline='darkred', width=3)
    draw.text((160, 220), "Test Circle", fill='black')
    return img

def test_device_performance(device_name):
    """Test performance on specific device"""
    print(f"\n🔄 Testing {device_name.upper()} Performance...")
    
    # Check device availability
    if device_name == 'mps' and not torch.backends.mps.is_available():
        print(f"     ❌ MPS not available")
        return None
    
    try:
        # Load model and processor
        print(f"     Loading SmolVLM2 on {device_name}...")
        model_start = time.time()
        
        processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM2-500M-Video-Instruct")
        model = AutoModelForImageTextToText.from_pretrained(
            "HuggingFaceTB/SmolVLM2-500M-Video-Instruct",
            torch_dtype=torch.bfloat16,
            device_map=device_name
        )
        
        model_load_time = time.time() - model_start
        print(f"     ✅ Model loaded in {model_load_time:.2f}s")
        
        # Create test image
        test_image = create_test_image()
        test_prompt = "What do you see in this image?"
        
        # Run inference test 3 times for average
        inference_times = []
        
        for run in range(3):
            print(f"     Run {run + 1}/3...", end=" ")
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": test_image},
                        {"type": "text", "text": test_prompt}
                    ]
                }
            ]
            
            start_time = time.time()
            inputs = processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(device_name, dtype=torch.bfloat16)
            
            generated_ids = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=50,
                temperature=0.1
            )
            
            response = processor.batch_decode(
                generated_ids,
                skip_special_tokens=True,
            )[0]
            
            inference_time = time.time() - start_time
            inference_times.append(inference_time)
            print(f"{inference_time:.2f}s")
        
        avg_inference = sum(inference_times) / len(inference_times)
        
        # Show sample response from first run
        if len(response) > 0:
            clean_response = response.split("Assistant:")[-1].strip() if "Assistant:" in response else response
            print(f"     Sample response: {clean_response[:80]}...")
        
        # Clean up memory
        del model, processor
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        
        return {
            'device': device_name,
            'model_load_time': model_load_time,
            'avg_inference_time': avg_inference,
            'inference_times': inference_times,
            'success': True
        }
        
    except Exception as e:
        print(f"     ❌ Error: {e}")
        return {'device': device_name, 'success': False, 'error': str(e)}

def main():
    """Main performance comparison function"""
    print("⚡ SmolVLM2-500M MPS vs CPU Performance Comparison")
    print("=" * 55)
    
    # Check system capabilities
    print(f"🖥️  System Information:")
    print(f"   • PyTorch: {torch.__version__}")
    print(f"   • MPS Available: {torch.backends.mps.is_available()}")
    print(f"   • MPS Built: {torch.backends.mps.is_built()}")
    
    results = {}
    
    # Test CPU performance
    results['cpu'] = test_device_performance('cpu')
    
    # Test MPS performance
    results['mps'] = test_device_performance('mps')
    
    # Compare results
    print(f"\n📊 Performance Comparison Results:")
    print(f"=" * 55)
    
    if results['cpu'] and results['mps'] and results['cpu']['success'] and results['mps']['success']:
        cpu_load = results['cpu']['model_load_time']
        cpu_inf = results['cpu']['avg_inference_time']
        mps_load = results['mps']['model_load_time']
        mps_inf = results['mps']['avg_inference_time']
        
        load_speedup = cpu_load / mps_load if mps_load > 0 else 0
        inf_speedup = cpu_inf / mps_inf if mps_inf > 0 else 0
        
        print(f"\n   Device       | Load Time | Avg Inference | Speedup")
        print(f"   -------------|-----------|---------------|--------")
        print(f"   CPU          | {cpu_load:8.2f}s | {cpu_inf:12.2f}s | 1.00x")
        print(f"   MPS (GPU)    | {mps_load:8.2f}s | {mps_inf:12.2f}s | {inf_speedup:.2f}x")
        
        print(f"\n🎯 Performance Summary:")
        print(f"   • Model Loading: MPS is {load_speedup:.1f}x {'faster' if load_speedup > 1 else 'slower'} than CPU")
        print(f"   • Inference Speed: MPS is {inf_speedup:.1f}x {'faster' if inf_speedup > 1 else 'slower'} than CPU")
        
        if inf_speedup >= 3:
            rating = "🌟 EXCELLENT (3x+ speedup)"
        elif inf_speedup >= 2:
            rating = "👍 VERY GOOD (2x+ speedup)"
        elif inf_speedup >= 1.5:
            rating = "✅ GOOD (1.5x+ speedup)"
        elif inf_speedup >= 1.1:
            rating = "⚪ MODERATE (small improvement)"
        else:
            rating = "⚠️ MINIMAL (no significant speedup)"
        
        print(f"   • MPS Performance Rating: {rating}")
        
        # MPS Analysis
        print(f"\n💡 What is MPS?")
        print(f"   • MPS = Metal Performance Shaders")
        print(f"   • Uses your M3 chip's GPU cores instead of CPU cores")
        print(f"   • Should provide faster AI inference on Apple Silicon")
        print(f"   • Your result: {inf_speedup:.1f}x speedup with MPS")
        
    else:
        print("   ❌ Unable to complete full comparison")
        if results['cpu'] and not results['cpu']['success']:
            print(f"   CPU Error: {results['cpu'].get('error', 'Unknown')}")
        if results['mps'] and not results['mps']['success']:
            print(f"   MPS Error: {results['mps'].get('error', 'Unknown')}")
    
    print(f"\n🎉 Performance test complete!")

if __name__ == "__main__":
    main() 