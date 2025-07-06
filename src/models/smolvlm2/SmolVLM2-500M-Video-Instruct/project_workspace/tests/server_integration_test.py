#!/usr/bin/env python3
"""
SmolVLM2 Server Integration Test

Tests the running SmolVLM2 server via HTTP API calls using real debug images.
This test validates the complete server pipeline including image processing,
model inference, and response formatting.

Author: AI Assistant
Created: June 28, 2025
"""

import os
import sys
import time
import base64
import json
import requests
from pathlib import Path
from PIL import Image
import io

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.append(str(project_root))

class SmolVLM2ServerIntegrationTest:
    """
    Comprehensive integration test for SmolVLM2 server using HTTP API calls
    """
    
    def __init__(self, server_url="http://localhost:8080", images_dir=None):
        self.server_url = server_url
        self.images_dir = images_dir or str(project_root / "src" / "debug" / "images")
        self.test_results = []
        self.session = requests.Session()
        
    def encode_image_to_base64(self, image_path):
        """Convert image file to base64 data URL"""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                
            # Get image format
            img = Image.open(image_path)
            format_map = {'JPEG': 'jpeg', 'PNG': 'png', 'JPG': 'jpeg'}
            img_format = format_map.get(img.format, 'jpeg')
            
            # Encode to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/{img_format};base64,{base64_data}"
            
        except Exception as e:
            print(f"❌ Error encoding image {image_path}: {e}")
            return None
    
    def check_server_health(self):
        """Check if server is running and healthy"""
        print("🔍 Checking server health...")
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server healthy: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server not reachable: {e}")
            return False
    
    def get_server_info(self):
        """Get server information"""
        try:
            response = self.session.get(f"{self.server_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Server Info:")
                print(f"   Message: {data.get('message', 'N/A')}")
                print(f"   Version: {data.get('version', 'N/A')}")
                print(f"   Status: {data.get('status', 'N/A')}")
                return data
        except Exception as e:
            print(f"❌ Failed to get server info: {e}")
        return None
    
    def test_image_analysis(self, image_path, prompt="Describe what you see in this image in detail.", max_tokens=150):
        """Test image analysis via server API"""
        print(f"\n🖼️ Testing image: {os.path.basename(image_path)}")
        
        # Encode image
        image_data_url = self.encode_image_to_base64(image_path)
        if not image_data_url:
            return None
            
        # Prepare request
        payload = {
            "model": "SmolVLM2",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.server_url}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('choices', [{}])[0].get('message', {}).get('content', 'No response')
                processing_time = data.get('processing_time', end_time - start_time)
                inference_time = data.get('inference_time', 0)
                
                result = {
                    'image': os.path.basename(image_path),
                    'prompt': prompt,
                    'response': response_text,
                    'processing_time': processing_time,
                    'inference_time': inference_time,
                    'success': True
                }
                
                print(f"✅ Success! Processing time: {processing_time:.2f}s")
                print(f"📝 Response: {response_text[:100]}...")
                
                return result
                
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Failed: {error_msg}")
                return {
                    'image': os.path.basename(image_path),
                    'prompt': prompt,
                    'error': error_msg,
                    'success': False
                }
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Request failed: {error_msg}")
            return {
                'image': os.path.basename(image_path),
                'prompt': prompt,
                'error': error_msg,
                'success': False
            }
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🧪 SmolVLM2 Server Integration Test Suite")
        print("=" * 60)
        
        # 1. Check server health
        if not self.check_server_health():
            print("❌ Server not available. Please ensure SmolVLM2 server is running on port 8080.")
            return False
        
        # 2. Get server info
        self.get_server_info()
        
        # 3. Find test images
        print(f"\n📂 Looking for test images in: {self.images_dir}")
        image_files = []
        
        if os.path.exists(self.images_dir):
            for file in os.listdir(self.images_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_files.append(os.path.join(self.images_dir, file))
            
            print(f"📸 Found {len(image_files)} test images:")
            for img in image_files:
                size = os.path.getsize(img) / 1024  # KB
                print(f"   • {os.path.basename(img)} ({size:.1f}KB)")
        else:
            print(f"❌ Images directory not found: {self.images_dir}")
            return False
        
        if not image_files:
            print("❌ No test images found")
            return False
        
        # 4. Test different prompts
        test_prompts = [
            "Describe what you see in this image in detail.",
            "What objects can you identify in this image?",
            "What colors are prominent in this image?",
            "Describe the scene and any activities you observe.",
            "What is the main subject of this image?"
        ]
        
        print(f"\n🎯 Running tests with {len(test_prompts)} different prompts...")
        
        # 5. Run tests
        total_tests = 0
        successful_tests = 0
        total_processing_time = 0
        
        for i, image_path in enumerate(image_files):
            # Use different prompts for variety
            prompt = test_prompts[i % len(test_prompts)]
            
            result = self.test_image_analysis(image_path, prompt)
            if result:
                self.test_results.append(result)
                total_tests += 1
                
                if result.get('success', False):
                    successful_tests += 1
                    total_processing_time += result.get('processing_time', 0)
        
        # 6. Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"🧪 Total tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {total_tests - successful_tests}")
        
        if successful_tests > 0:
            avg_time = total_processing_time / successful_tests
            print(f"⏱️ Average processing time: {avg_time:.2f}s")
            print(f"🎯 Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # 7. Show detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result.get('success') else "❌"
            image_name = result['image']
            
            if result.get('success'):
                time_taken = result.get('processing_time', 0)
                response_preview = result.get('response', '')[:80] + "..."
                print(f"{status} {image_name}: {time_taken:.2f}s - {response_preview}")
            else:
                error = result.get('error', 'Unknown error')
                print(f"{status} {image_name}: {error}")
        
        return successful_tests == total_tests
    
    def test_specific_capabilities(self):
        """Test specific model capabilities"""
        print("\n🎯 Testing Specific Capabilities")
        print("-" * 40)
        
        # Find a suitable test image
        test_image = None
        for file in os.listdir(self.images_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                test_image = os.path.join(self.images_dir, file)
                break
        
        if not test_image:
            print("❌ No test image available")
            return
        
        # Test different types of analysis
        capability_tests = [
            {
                "name": "Object Detection",
                "prompt": "List all objects you can see in this image."
            },
            {
                "name": "Color Analysis", 
                "prompt": "What are the main colors in this image?"
            },
            {
                "name": "Scene Description",
                "prompt": "Describe the overall scene and setting."
            },
            {
                "name": "Detail Analysis",
                "prompt": "Provide a detailed analysis of the most important elements."
            }
        ]
        
        print(f"🖼️ Using test image: {os.path.basename(test_image)}")
        
        for test in capability_tests:
            print(f"\n🔍 {test['name']}:")
            result = self.test_image_analysis(test_image, test['prompt'], max_tokens=100)
            
            if result and result.get('success'):
                response = result.get('response', '')
                print(f"   📝 {response[:150]}...")
            else:
                print(f"   ❌ Test failed")

def main():
    """Main test execution"""
    print("🚀 Starting SmolVLM2 Server Integration Tests")
    print(f"🕐 Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Initialize test suite
    tester = SmolVLM2ServerIntegrationTest()
    
    try:
        # Run comprehensive tests
        success = tester.run_comprehensive_test()
        
        # Run capability tests
        tester.test_specific_capabilities()
        
        print(f"\n🏁 Testing completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success:
            print("🎉 ALL TESTS PASSED! SmolVLM2 server is working correctly.")
            return 0
        else:
            print("⚠️ Some tests failed. Check the results above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 