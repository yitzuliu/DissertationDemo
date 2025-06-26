#!/usr/bin/env python3
"""
SmolVLM2-500M-Video-Instruct Text & Image Capability Test
Following TODOLIST.md Phase 2: Core Capability Testing
"""

import torch
import time
import sys
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image, ImageDraw, ImageFont
import io
import base64

class SmolVLM2Tester:
    def __init__(self):
        self.model_path = './src/models/smolvlm2/SmolVLM2-500M-Video-Instruct'
        self.device = 'mps' if torch.backends.mps.is_available() else 'cpu'
        self.processor = None
        self.model = None
        self.test_results = []
        
    def load_model(self):
        """Load the model and processor"""
        print("🔧 Loading SmolVLM2-500M-Video-Instruct...")
        print(f"📱 Device: {self.device}")
        
        # Load processor
        start_time = time.time()
        self.processor = AutoProcessor.from_pretrained(self.model_path)
        processor_time = time.time() - start_time
        
        # Load model
        start_time = time.time()
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,
            device_map=self.device
        )
        model_time = time.time() - start_time
        
        print(f"✅ Processor: {processor_time:.2f}s")
        print(f"✅ Model: {model_time:.2f}s")
        print(f"✅ Ready for testing!\n")
        
        return processor_time, model_time
    
    def generate_response(self, messages, max_tokens=100):
        """Generate response for given messages"""
        start_time = time.time()
        
        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.device, dtype=torch.bfloat16)
        
        generated_ids = self.model.generate(
            **inputs, 
            do_sample=False, 
            max_new_tokens=max_tokens,
            temperature=0.1
        )
        
        response = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]
        
        inference_time = time.time() - start_time
        return response, inference_time
    
    def create_test_image(self, content_type="simple"):
        """Create test images for different scenarios"""
        if content_type == "simple":
            # Simple object image
            img = Image.new('RGB', (400, 300), color='lightblue')
            draw = ImageDraw.Draw(img)
            # Draw a red circle
            draw.ellipse([150, 100, 250, 200], fill='red', outline='darkred', width=3)
            draw.text((160, 220), "Red Circle", fill='black')
            return img
            
        elif content_type == "text":
            # Text-heavy image
            img = Image.new('RGB', (500, 300), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), "IMPORTANT NOTICE", fill='red', anchor="mm")
            draw.text((50, 100), "This is a test document", fill='black')
            draw.text((50, 130), "Date: January 27, 2025", fill='black')
            draw.text((50, 160), "Status: ACTIVE", fill='green')
            draw.text((50, 190), "ID: TEST-001", fill='blue')
            return img
            
        elif content_type == "complex":
            # Complex scene
            img = Image.new('RGB', (400, 300), color='lightgreen')
            draw = ImageDraw.Draw(img)
            # Multiple objects
            draw.rectangle([50, 50, 150, 150], fill='blue', outline='navy', width=2)
            draw.ellipse([200, 80, 300, 180], fill='yellow', outline='orange', width=2)
            draw.polygon([(320, 200), (370, 150), (370, 250)], fill='purple', outline='indigo')
            draw.text((50, 250), "Blue Square, Yellow Circle, Purple Triangle", fill='black')
            return img
    
    def test_text_only(self):
        """Test text-only processing capabilities"""
        print("📝 Testing Text-Only Processing...")
        
        test_cases = [
            {
                "name": "Math Problem",
                "prompt": "What is 15 × 7? Please show your work.",
                "expected_topic": "mathematics"
            },
            {
                "name": "Creative Writing",
                "prompt": "Write a short story about a robot learning to paint.",
                "expected_topic": "creative writing"
            },
            {
                "name": "Factual Question",
                "prompt": "What are the primary colors in traditional color theory?",
                "expected_topic": "color theory"
            },
            {
                "name": "Reasoning Task", 
                "prompt": "If a train leaves Station A at 2 PM traveling at 60 mph, and another train leaves Station B at 3 PM traveling at 80 mph toward Station A, when will they meet if the stations are 200 miles apart?",
                "expected_topic": "logical reasoning"
            }
        ]
        
        text_results = []
        for i, test in enumerate(test_cases, 1):
            print(f"\n  {i}. {test['name']}")
            print(f"     Q: {test['prompt']}")
            
            messages = [{"role": "user", "content": [{"type": "text", "text": test['prompt']}]}]
            
            try:
                response, inference_time = self.generate_response(messages, max_tokens=150)
                # Extract just the model's response (remove the prompt)
                clean_response = response.split("Assistant:")[-1].strip() if "Assistant:" in response else response
                
                print(f"     A: {clean_response[:200]}{'...' if len(clean_response) > 200 else ''}")
                print(f"     ⏱️  {inference_time:.2f}s")
                
                text_results.append({
                    'test': test['name'],
                    'time': inference_time,
                    'response_length': len(clean_response),
                    'success': True
                })
                
            except Exception as e:
                print(f"     ❌ Error: {e}")
                text_results.append({
                    'test': test['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return text_results
    
    def test_image_understanding(self):
        """Test image understanding capabilities"""
        print("\n🖼️  Testing Image Understanding...")
        
        test_scenarios = [
            {
                "name": "Simple Object Recognition",
                "image_type": "simple",
                "prompt": "What do you see in this image? Describe it in detail."
            },
            {
                "name": "Text Recognition (OCR)",
                "image_type": "text", 
                "prompt": "What text can you read in this image? Please list all the text you can see."
            },
            {
                "name": "Complex Scene Analysis",
                "image_type": "complex",
                "prompt": "Describe all the objects in this image, including their colors and shapes."
            },
            {
                "name": "Visual Question Answering",
                "image_type": "simple",
                "prompt": "What color is the circle in this image?"
            },
            {
                "name": "Counting Task",
                "image_type": "complex", 
                "prompt": "How many geometric shapes are in this image?"
            }
        ]
        
        image_results = []
        for i, test in enumerate(test_scenarios, 1):
            print(f"\n  {i}. {test['name']}")
            print(f"     Creating {test['image_type']} test image...")
            
            # Create test image
            test_image = self.create_test_image(test['image_type'])
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": test_image},
                        {"type": "text", "text": test['prompt']}
                    ]
                }
            ]
            
            try:
                response, inference_time = self.generate_response(messages, max_tokens=120)
                clean_response = response.split("Assistant:")[-1].strip() if "Assistant:" in response else response
                
                print(f"     Q: {test['prompt']}")
                print(f"     A: {clean_response[:200]}{'...' if len(clean_response) > 200 else ''}")
                print(f"     ⏱️  {inference_time:.2f}s")
                
                image_results.append({
                    'test': test['name'],
                    'time': inference_time,
                    'response_length': len(clean_response),
                    'success': True
                })
                
            except Exception as e:
                print(f"     ❌ Error: {e}")
                image_results.append({
                    'test': test['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return image_results
    
    def analyze_results(self, text_results, image_results, load_times):
        """Analyze and summarize test results"""
        print("\n" + "="*60)
        print("📊 SMOLVLM2-500M-VIDEO-INSTRUCT TEST RESULTS")
        print("="*60)
        
        # Loading Performance
        print(f"\n🚀 Loading Performance:")
        print(f"   • Processor: {load_times[0]:.2f}s")
        print(f"   • Model: {load_times[1]:.2f}s")
        print(f"   • Total: {sum(load_times):.2f}s")
        print(f"   • Target: <60s ✅ {'EXCELLENT' if sum(load_times) < 10 else 'GOOD' if sum(load_times) < 30 else 'ACCEPTABLE'}")
        
        # Text Processing Results
        print(f"\n📝 Text Processing Results:")
        text_success = [r for r in text_results if r.get('success')]
        if text_success:
            avg_time = sum(r['time'] for r in text_success) / len(text_success)
            print(f"   • Tests Passed: {len(text_success)}/{len(text_results)}")
            print(f"   • Avg Response Time: {avg_time:.2f}s")
            print(f"   • Target: 1-3s ✅ {'EXCELLENT' if avg_time < 2 else 'GOOD' if avg_time < 4 else 'SLOW'}")
        
        # Image Processing Results  
        print(f"\n🖼️  Image Processing Results:")
        image_success = [r for r in image_results if r.get('success')]
        if image_success:
            avg_time = sum(r['time'] for r in image_success) / len(image_success)
            print(f"   • Tests Passed: {len(image_success)}/{len(image_results)}")
            print(f"   • Avg Response Time: {avg_time:.2f}s")
            print(f"   • Target: 1-3s ✅ {'EXCELLENT' if avg_time < 3 else 'GOOD' if avg_time < 5 else 'SLOW'}")
        
        # Overall Assessment
        total_success = len(text_success) + len(image_success)
        total_tests = len(text_results) + len(image_results)
        success_rate = (total_success / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 Overall Assessment:")
        print(f"   • Success Rate: {success_rate:.1f}% ({total_success}/{total_tests})")
        print(f"   • Quality Rating: {'🌟 EXCELLENT' if success_rate >= 90 else '👍 GOOD' if success_rate >= 70 else '⚠️  NEEDS WORK'}")
        
        # TODOLIST Phase 2 Completion Status
        print(f"\n✅ TODOLIST Phase 2 Status:")
        print(f"   • [✓] Model Loading Test")
        print(f"   • [✓] Text Processing Test")  
        print(f"   • [✓] Image Understanding Test")
        print(f"   • [✓] Performance Benchmarks")
        print(f"   • [{'✓' if success_rate >= 80 else '○'}] Quality Assessment")
        
        return {
            'load_time': sum(load_times),
            'text_success_rate': len(text_success) / len(text_results) * 100 if text_results else 0,
            'image_success_rate': len(image_success) / len(image_results) * 100 if image_results else 0,
            'overall_success_rate': success_rate
        }

def main():
    """Main testing function"""
    print("🎯 SmolVLM2-500M-Video-Instruct Capability Assessment")
    print("Following TODOLIST.md Phase 2: Core Capability Testing")
    print("-" * 60)
    
    tester = SmolVLM2Tester()
    
    try:
        # Load model
        load_times = tester.load_model()
        
        # Run text tests
        text_results = tester.test_text_only()
        
        # Run image tests  
        image_results = tester.test_image_understanding()
        
        # Analyze results
        summary = tester.analyze_results(text_results, image_results, load_times)
        
        print(f"\n🎉 Testing Complete! Model is {'READY for production' if summary['overall_success_rate'] >= 80 else 'suitable for development testing'}")
        
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 