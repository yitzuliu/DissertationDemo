#!/usr/bin/env python3
"""
VLM Fallback Test with Real Images

This test specifically focuses on testing VLM Fallback with real images
from src/testing/materials/images/
"""

import sys
import os
import time
import json
import requests
import base64
from pathlib import Path
import subprocess

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class VLMFallbackRealImageTester:
    """Test VLM Fallback with real images"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.model_port = 8080
        self.backend_port = 8000
        self.model_process = None
        self.backend_process = None
        
        # Virtual environment setup
        self.venv_path = self.base_dir / "ai_vision_env"
        self.python_executable = self.venv_path / "bin" / "python"
        
        if not self.python_executable.exists():
            self.python_executable = sys.executable
            print(f"⚠️ Using system Python: {self.python_executable}")
        else:
            print(f"✅ Using virtual environment: {self.python_executable}")
    
    def start_services(self):
        """Start model and backend services"""
        print("🚀 Starting services for real image testing...")
        
        # Start model service
        model_script = self.base_dir / "src/models/smolvlm/run_smolvlm.py"
        if model_script.exists():
            print("📋 Starting model service...")
            env = os.environ.copy()
            if self.venv_path.exists():
                env["VIRTUAL_ENV"] = str(self.venv_path)
                env["PATH"] = f"{self.venv_path / 'bin'}:{env.get('PATH', '')}"
            
            self.model_process = subprocess.Popen(
                [str(self.python_executable), str(model_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=str(model_script.parent)
            )
            time.sleep(20)  # Wait for model to start
        
        # Start backend service
        backend_script = self.base_dir / "src/backend/main.py"
        if backend_script.exists():
            print("📋 Starting backend service...")
            env = os.environ.copy()
            if self.venv_path.exists():
                env["VIRTUAL_ENV"] = str(self.venv_path)
                env["PATH"] = f"{self.venv_path / 'bin'}:{env.get('PATH', '')}"
                env["PYTHONPATH"] = str(self.base_dir / "src")
            
            self.backend_process = subprocess.Popen(
                [str(self.python_executable), "-m", "uvicorn", "main:app", 
                "--host", "127.0.0.1", "--port", str(self.backend_port), "--reload"],
                cwd=str(backend_script.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            time.sleep(10)  # Wait for backend to start
        
        # Verify services
        return self.check_services()
    
    def check_services(self):
        """Check if services are running"""
        try:
            # Check model service
            model_response = requests.get(f"http://localhost:{self.model_port}/v1/models", timeout=5)
            model_ok = model_response.status_code == 200
            
            # Check backend service
            backend_response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            backend_ok = backend_response.status_code == 200
            
            print(f"📊 Service Status: Model={'✅' if model_ok else '❌'}, Backend={'✅' if backend_ok else '❌'}")
            return model_ok and backend_ok
        except:
            return False
    
    def load_real_images(self):
        """Load real images from testing materials"""
        images_dir = self.base_dir / "src/testing/materials/images"
        real_images = []
        
        if not images_dir.exists():
            print(f"❌ Images directory not found: {images_dir}")
            return real_images
        
        image_files = [
            "IMG_0119.JPG",
            "IMG_2053.JPG", 
            "test_image.jpg"
        ]
        
        for image_file in image_files:
            image_path = images_dir / image_file
            if image_path.exists():
                try:
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                    
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    real_images.append({
                        'name': image_file,
                        'path': str(image_path),
                        'data': image_data,
                        'base64': base64_image,
                        'size': len(image_data)
                    })
                    print(f"✅ Loaded {image_file}: {len(image_data)} bytes")
                except Exception as e:
                    print(f"❌ Failed to load {image_file}: {e}")
            else:
                print(f"⚠️ Image not found: {image_path}")
        
        return real_images
    
    def send_image_to_vlm(self, image_info, description_query="Describe this image in detail."):
        """Send image to VLM system and get response"""
        try:
            image_url = f"data:image/jpeg;base64,{image_info['base64']}"
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": description_query
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"http://localhost:{self.backend_port}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    return {
                        'success': True,
                        'response': content,
                        'image_name': image_info['name']
                    }
            
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}",
                'image_name': image_info['name']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'image_name': image_info['name']
            }
    
    def test_vlm_fallback_with_images(self, real_images):
        """Test VLM Fallback with real images"""
        print("\n🖼️ Testing VLM Fallback with Real Images")
        print("=" * 60)
        
        fallback_queries = [
            "What do you see in this image?",
            "Describe the objects in this photo",
            "What colors are prominent in this image?",
            "Is this an indoor or outdoor scene?",
            "What activities might be happening here?",
            "What is the main subject of this photograph?"
        ]
        
        results = []
        
        for image_info in real_images:
            print(f"\n📸 Testing with image: {image_info['name']}")
            print(f"   Size: {image_info['size']} bytes")
            
            # First, send image to VLM system to populate last_processed_image
            print("   📤 Sending image to VLM system...")
            vlm_result = self.send_image_to_vlm(image_info, "Analyze this image briefly.")
            
            if vlm_result['success']:
                print(f"   ✅ Image processed by VLM")
                print(f"   📄 VLM Response: {vlm_result['response'][:100]}...")
                
                # Wait a moment for state tracker to process
                time.sleep(2)
                
                # Now test VLM Fallback queries
                for i, query in enumerate(fallback_queries):
                    print(f"\n   🔍 Query {i+1}: '{query}'")
                    
                    try:
                        response = requests.post(
                            f"http://localhost:{self.backend_port}/api/v1/state/query",
                            json={"query": query},
                            timeout=20
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            response_text = data.get('response', '')
                            confidence = data.get('confidence', 0.0)
                            query_type = data.get('query_type', 'unknown')
                            
                            # Check if this looks like VLM Fallback was triggered
                            is_meaningful = len(response_text) > 30
                            has_image_content = any(word in response_text.lower() for word in 
                                                  ['image', 'photo', 'picture', 'see', 'visible', 'color', 'object'])
                            
                            result = {
                                'image_name': image_info['name'],
                                'query': query,
                                'response': response_text,
                                'confidence': confidence,
                                'query_type': query_type,
                                'is_meaningful': is_meaningful,
                                'has_image_content': has_image_content,
                                'likely_fallback': is_meaningful and (confidence < 0.5 or query_type == 'unknown' or has_image_content)
                            }
                            
                            results.append(result)
                            
                            status = "✅" if result['likely_fallback'] else "⚠️"
                            print(f"      {status} Type: {query_type}, Confidence: {confidence:.2f}")
                            print(f"      📄 Response: {response_text[:80]}...")
                            
                        else:
                            print(f"      ❌ HTTP {response.status_code}")
                            
                    except Exception as e:
                        print(f"      ❌ Exception: {e}")
                    
                    time.sleep(1)
                
            else:
                print(f"   ❌ Failed to send image: {vlm_result['error']}")
        
        return results
    
    def analyze_results(self, results):
        """Analyze test results"""
        print("\n📊 Test Results Analysis")
        print("=" * 60)
        
        if not results:
            print("❌ No results to analyze")
            return False
        
        total_queries = len(results)
        meaningful_responses = sum(1 for r in results if r['is_meaningful'])
        image_content_responses = sum(1 for r in results if r['has_image_content'])
        likely_fallback_responses = sum(1 for r in results if r['likely_fallback'])
        
        print(f"📋 Total queries tested: {total_queries}")
        print(f"📋 Meaningful responses: {meaningful_responses} ({meaningful_responses/total_queries*100:.1f}%)")
        print(f"📋 Responses with image content: {image_content_responses} ({image_content_responses/total_queries*100:.1f}%)")
        print(f"📋 Likely VLM Fallback responses: {likely_fallback_responses} ({likely_fallback_responses/total_queries*100:.1f}%)")
        
        # Group by image
        images_tested = set(r['image_name'] for r in results)
        print(f"\n🖼️ Images tested: {len(images_tested)}")
        
        for image_name in images_tested:
            image_results = [r for r in results if r['image_name'] == image_name]
            image_fallback_count = sum(1 for r in image_results if r['likely_fallback'])
            print(f"   📸 {image_name}: {image_fallback_count}/{len(image_results)} likely fallback responses")
        
        # Success criteria
        success_rate = likely_fallback_responses / total_queries
        image_content_rate = image_content_responses / total_queries
        
        success = success_rate >= 0.6 and image_content_rate >= 0.4
        
        print(f"\n🎯 Overall Assessment:")
        print(f"   VLM Fallback Success Rate: {success_rate*100:.1f}% (target: ≥60%)")
        print(f"   Image Content Rate: {image_content_rate*100:.1f}% (target: ≥40%)")
        print(f"   Test Result: {'✅ PASS' if success else '❌ FAIL'}")
        
        return success
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Cleaning up...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                print("   ✅ Backend service stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("   ⚠️ Backend service force stopped")
        
        if self.model_process:
            self.model_process.terminate()
            try:
                self.model_process.wait(timeout=5)
                print("   ✅ Model service stopped")
            except subprocess.TimeoutExpired:
                self.model_process.kill()
                print("   ⚠️ Model service force stopped")
    
    def run_test(self):
        """Run the complete test"""
        print("🎯 VLM Fallback Real Image Test")
        print("=" * 60)
        print("Testing VLM Fallback functionality with real images from src/testing/materials/images/")
        print()
        
        try:
            # Start services
            if not self.start_services():
                print("❌ Failed to start services")
                return False
            
            # Load real images
            real_images = self.load_real_images()
            if not real_images:
                print("❌ No real images loaded")
                return False
            
            print(f"✅ Loaded {len(real_images)} real images")
            
            # Test VLM Fallback with images
            results = self.test_vlm_fallback_with_images(real_images)
            
            # Analyze results
            success = self.analyze_results(results)
            
            return success
            
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
            return False
        finally:
            self.cleanup()

def main():
    """Main function"""
    tester = VLMFallbackRealImageTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()