#!/usr/bin/env python3
"""
Unified Model Testing Suite - Debug Version

Model-agnostic testing through backend API, simulating real-world usage.
"""

import os
import sys
import time
import json
import base64
import requests
from pathlib import Path
from PIL import Image
import io
from datetime import datetime

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

class DebugModelTestSuite:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.session = requests.Session()
        self.timeout = 120
        
        # Use images from same debug directory
        self.images_dir = current_dir / "images"
        
        # Test state
        self.active_model = None
        self.model_capabilities = {}
        self.test_results = []
        
        # Create results file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_file = current_dir / f"test_results_{timestamp}.json"
        
        print(f"🎯 Debug Test Suite Initialized")
        print(f"📁 Images Directory: {self.images_dir}")
        print(f"🌐 Backend URL: {self.backend_url}")
    
    def log_result(self, test_name, result):
        """Log test result with timestamp"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "active_model": self.active_model,
            "result": result
        }
        self.test_results.append(entry)
        
        # Save results immediately
        with open(self.results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
    
    def detect_system_status(self):
        """Detect active model and system status through backend"""
        print("\n🔍 SYSTEM DETECTION")
        print("=" * 40)
        
        status = {
            "backend_online": False,
            "active_model": None,
            "model_server_online": False,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = self.session.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status["backend_online"] = True
                status["active_model"] = data.get("active_model")
                self.active_model = data.get("active_model")
                
                print(f"✅ Backend: Online")
                print(f"🤖 Active Model: {self.active_model}")
                
                if self.active_model:
                    status["model_server_online"] = True
                    print(f"✅ Model Server: Detected via Backend")
            else:
                print(f"❌ Backend: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Backend: Not reachable - {e}")
        
        self._detect_model_capabilities()
        self.log_result("system_detection", status)
        return status
    
    def _detect_model_capabilities(self):
        """Detect capabilities based on active model name"""
        if not self.active_model:
            return
        
        model_name = self.active_model.lower()
        
        # Model capability database
        capabilities_db = {
            "smolvlm2": {
                "vision": True,
                "text_generation": True,
                "video": True,
                "object_detection": True,
                "scene_analysis": True,
                "text_recognition": True,
                "optimal_image_size": 768,
                "max_tokens": 1024,
                "expected_response_time": 15.0
            },
            "smolvlm": {
                "vision": True,
                "text_generation": True,
                "video": False,
                "object_detection": True,
                "scene_analysis": True,
                "text_recognition": True,
                "optimal_image_size": 512,
                "max_tokens": 512,
                "expected_response_time": 10.0
            }
        }
        
        # Match model name to capabilities
        for key, caps in capabilities_db.items():
            if key in model_name:
                self.model_capabilities = caps
                print(f"📊 Detected Capabilities: {key.title()}")
                print(f"   Vision: {caps['vision']}")
                print(f"   Text Generation: {caps['text_generation']}")
                print(f"   Video: {caps['video']}")
                print(f"   Object Detection: {caps['object_detection']}")
                return
        
        # Default capabilities
        self.model_capabilities = capabilities_db["smolvlm"]
        print(f"⚠️ Unknown model, using default capabilities")
    
    def get_debug_images(self):
        """Get all debug images from the images directory"""
        if not self.images_dir.exists():
            return []
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
        images = []
        
        for file in self.images_dir.iterdir():
            if file.is_file() and file.suffix.lower() in image_extensions:
                images.append(file)
        
        return sorted(images)
    
    def encode_image_to_base64(self, image_path):
        """Convert image to base64 with model-specific optimization"""
        try:
            with Image.open(image_path) as img:
                optimal_size = self.model_capabilities.get("optimal_image_size", 512)
                
                if max(img.size) > optimal_size:
                    scale = optimal_size / max(img.size)
                    new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"🔄 Resized to {new_size}")
                
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=90)
                image_bytes = buffer.getvalue()
                
                return base64.b64encode(image_bytes).decode('utf-8')
                
        except Exception as e:
            print(f"❌ Error encoding {image_path.name}: {e}")
            raise
    
    def send_image_to_backend(self, prompt, image_path):
        """Send image analysis request to backend using OpenAI-compatible API"""
        try:
            image_base64 = self.encode_image_to_base64(image_path)
            
            # OpenAI-compatible payload format
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                "max_tokens": self.model_capabilities.get("max_tokens", 512),
                "temperature": 0.7
            }
            
            print(f"📤 Sending: {image_path.name}")
            print(f"💬 Prompt: {prompt}")
            
            start_time = time.time()
            
            response = self.session.post(
                f"{self.backend_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                # Extract response from OpenAI format
                response_text = ""
                if "choices" in data and len(data["choices"]) > 0:
                    response_text = data["choices"][0].get("message", {}).get("content", "")
                
                # Debug: Check if response is empty
                if not response_text.strip():
                    print(f"⚠️ Empty response detected! Raw API response:")
                    print(f"   {json.dumps(data, indent=2)}")
                
                return {
                    "success": True,
                    "response": response_text,
                    "processing_time": processing_time,
                    "model_used": self.active_model,
                    "image_name": image_path.name,
                    "status_code": response.status_code,
                    "raw_api_response": data  # Add for debugging
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "details": response.text,
                    "processing_time": processing_time,
                    "image_name": image_path.name,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": "Request failed",
                "details": str(e),
                "processing_time": 0,
                "image_name": image_path.name
            }
    
    def test_basic_functionality(self):
        """Test basic backend connectivity"""
        print("\n🔗 BASIC FUNCTIONALITY TEST")
        print("-" * 40)
        
        try:
            response = self.session.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend Health: {data.get('status')}")
                
                self.log_result("basic_functionality", {
                    "success": True,
                    "backend_status": data.get("status"),
                    "active_model": data.get("active_model")
                })
                return True
            else:
                print(f"❌ Backend returned HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend test failed: {e}")
            return False
    
    def test_image_analysis(self):
        """Test image analysis with all debug images"""
        print("\n🖼️ IMAGE ANALYSIS TEST")
        print("-" * 40)
        
        debug_images = self.get_debug_images()
        
        if not debug_images:
            print(f"❌ No debug images found in {self.images_dir}")
            return
        
        print(f"📸 Found {len(debug_images)} debug images:")
        for img in debug_images:
            size = img.stat().st_size / 1024  # KB
            print(f"   • {img.name} ({size:.1f}KB)")
        
        test_prompts = [
            "Describe what you see in this image in detail.",
            "What objects can you identify in this image?",
            "What are the main colors and visual elements?",
            "Describe the scene and any activities you observe."
        ]
        
        for i, image_path in enumerate(debug_images):
            prompt = test_prompts[i % len(test_prompts)]
            
            print(f"\n📸 Testing: {image_path.name}")
            result = self.send_image_to_backend(prompt, image_path)
            
            if result["success"]:
                expected_time = self.model_capabilities.get("expected_response_time", 10.0)
                time_status = "🚀" if result["processing_time"] < expected_time else "🐌"
                
                print(f"✅ Success! {time_status} {result['processing_time']:.2f}s")
                print(f"📝 Full Response:")
                print(f"   {result['response']}")
                print("-" * 60)
                
                self.log_result(f"image_analysis_{image_path.stem}", {
                    "success": True,
                    "image": image_path.name,
                    "prompt": prompt,
                    "response": result["response"],
                    "processing_time": result["processing_time"]
                })
            else:
                print(f"❌ Failed: {result['error']}")
                if "details" in result:
                    print(f"📝 Details: {result['details']}")
                
                self.log_result(f"image_analysis_{image_path.stem}", {
                    "success": False,
                    "image": image_path.name,
                    "error": result["error"]
                })
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 UNIFIED MODEL TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get("result", {}).get("success", False))
        
        print(f"🤖 Active Model: {self.active_model or 'Unknown'}")
        print(f"🧪 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {total_tests - successful_tests}")
        
        if total_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Performance statistics
        processing_times = []
        for result in self.test_results:
            result_data = result.get("result", {})
            if result_data.get("success") and "processing_time" in result_data:
                processing_times.append(result_data["processing_time"])
        
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            expected_time = self.model_capabilities.get("expected_response_time", 10.0)
            
            print(f"⏱️ Average Processing Time: {avg_time:.2f}s")
            print(f"🎯 Expected Time: {expected_time:.2f}s")
            print(f"🚀 Fastest Response: {min(processing_times):.2f}s")
            print(f"🐌 Slowest Response: {max(processing_times):.2f}s")
            
            if avg_time < expected_time:
                print(f"🏆 Performance: Better than expected!")
            elif avg_time < expected_time * 1.2:
                print(f"👍 Performance: Good")
            else:
                print(f"⚠️ Performance: Could be improved")
        
        print(f"\n💾 Results saved to: {self.results_file}")
        print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def run_complete_test_suite(self):
        """Run the complete test suite"""
        print("🧪 UNIFIED MODEL TEST SUITE - DEBUG VERSION")
        print("=" * 60)
        print(f"🎯 Model-agnostic testing through backend API")
        print()
        
        try:
            # Step 1: Detect system status
            system_status = self.detect_system_status()
            
            if not system_status["backend_online"]:
                print("❌ Backend not available. Please start the backend server.")
                return False
            
            # Step 2: Test basic functionality
            if not self.test_basic_functionality():
                print("❌ Basic functionality failed.")
                return False
            
            # Step 3: Test image analysis
            self.test_image_analysis()
            
            # Step 4: Generate report
            self.generate_report()
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Test suite interrupted")
            return False
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            return False


def main():
    """Main execution"""
    print("🚀 DEBUG MODEL TEST SUITE")
    print("=" * 60)
    
    tester = DebugModelTestSuite()
    
    try:
        start_time = time.time()
        success = tester.run_complete_test_suite()
        end_time = time.time()
        
        print(f"\n🕐 Total time: {end_time - start_time:.2f}s")
        
        if success:
            print("🎉 All tests completed!")
            return 0
        else:
            print("⚠️ Some tests failed.")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
        return 1


if __name__ == "__main__":
    exit(main()) 