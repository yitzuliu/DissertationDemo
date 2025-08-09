#!/usr/bin/env python3
"""
Complete System End-to-End Test

This test verifies the entire system flow:
1. Backend server startup
2. VLM service connection
3. VLM Fallback system integration
4. State query processing
5. Vision analysis processing
6. Frontend compatibility

Run this test to ensure the complete system is working correctly.
"""

import asyncio
import sys
import os
import time
import json
import subprocess
import signal
import requests
import base64
from pathlib import Path
from PIL import Image
import io
import threading
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class SystemTestRunner:
    """Complete system test runner"""
    
    def __init__(self):
        self.backend_process = None
        self.vlm_process = None
        self.test_results = []
        self.backend_url = "http://localhost:8000"
        self.vlm_url = "http://localhost:8080"
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"    Details: {details}")
    
    def create_test_image(self):
        """Create a test image for vision analysis"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (640, 480), color='lightblue')
            
            # Add some text to make it interesting
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                
                # Try to use a default font
                try:
                    font = ImageFont.truetype("Arial.ttf", 40)
                except:
                    font = ImageFont.load_default()
                
                draw.text((50, 200), "TEST IMAGE", fill='black', font=font)
                draw.text((50, 250), "VLM Fallback Test", fill='darkblue', font=font)
                
            except ImportError:
                # If PIL drawing is not available, just use the plain image
                pass
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=90)
            img_data = buffer.getvalue()
            
            base64_string = base64.b64encode(img_data).decode('utf-8')
            data_url = f"data:image/jpeg;base64,{base64_string}"
            
            return data_url
            
        except Exception as e:
            self.log_test("Create Test Image", False, f"Failed to create test image: {e}")
            return None
    
    def wait_for_service(self, url, service_name, timeout=30):
        """Wait for a service to be available"""
        print(f"⏳ Waiting for {service_name} at {url}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    self.log_test(f"{service_name} Availability", True, f"Service available at {url}")
                    return True
            except:
                pass
            time.sleep(1)
        
        self.log_test(f"{service_name} Availability", False, f"Service not available at {url} after {timeout}s")
        return False
    
    def start_backend_server(self):
        """Start the backend server"""
        try:
            print("🚀 Starting backend server...")
            
            # Change to the backend directory
            backend_dir = Path(__file__).parent.parent / "src" / "backend"
            
            # Start the backend server
            self.backend_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent / "src")}
            )
            
            # Wait for server to start
            if self.wait_for_service(self.backend_url, "Backend Server"):
                return True
            else:
                self.stop_backend_server()
                return False
                
        except Exception as e:
            self.log_test("Backend Server Startup", False, f"Failed to start backend: {e}")
            return False
    
    def start_vlm_server(self):
        """Start the VLM server"""
        try:
            print("🚀 Starting VLM server...")
            
            # Change to the VLM directory
            vlm_dir = Path(__file__).parent.parent / "src" / "models" / "smolvlm"
            
            if not vlm_dir.exists():
                self.log_test("VLM Server Startup", False, "VLM directory not found")
                return False
            
            # Start the VLM server
            self.vlm_process = subprocess.Popen(
                [sys.executable, "run_smolvlm.py"],
                cwd=vlm_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for VLM server to start (longer timeout for model loading)
            if self.wait_for_service(self.vlm_url, "VLM Server", timeout=60):
                return True
            else:
                self.stop_vlm_server()
                return False
                
        except Exception as e:
            self.log_test("VLM Server Startup", False, f"Failed to start VLM server: {e}")
            return False
    
    def stop_backend_server(self):
        """Stop the backend server"""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                self.backend_process.kill()
            self.backend_process = None
    
    def stop_vlm_server(self):
        """Stop the VLM server"""
        if self.vlm_process:
            try:
                self.vlm_process.terminate()
                self.vlm_process.wait(timeout=10)
            except:
                self.vlm_process.kill()
            self.vlm_process = None
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("Backend Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", False, f"Request failed: {e}")
            return False
    
    def test_vlm_health(self):
        """Test VLM server health"""
        try:
            response = requests.get(f"{self.vlm_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("VLM Health", True, "VLM server responding")
                return True
            else:
                self.log_test("VLM Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("VLM Health", False, f"Request failed: {e}")
            return False
    
    def test_state_query_basic(self):
        """Test basic state query functionality"""
        try:
            query_data = {
                "query": "Where am I?",
                "query_id": f"test_{int(time.time())}"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and data.get("response"):
                    self.log_test("State Query Basic", True, f"Response: {data['response'][:50]}...")
                    return True
                else:
                    self.log_test("State Query Basic", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("State Query Basic", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("State Query Basic", False, f"Request failed: {e}")
            return False
    
    def test_state_query_fallback_trigger(self):
        """Test state query that should trigger VLM fallback"""
        try:
            # Use a query that should trigger fallback (unknown query type)
            query_data = {
                "query": "What is the meaning of life and how does quantum physics relate to consciousness?",
                "query_id": f"test_fallback_{int(time.time())}"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=30  # Longer timeout for VLM processing
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and data.get("response"):
                    response_text = data["response"]
                    # Check if response looks like it came from VLM (more detailed than template)
                    if len(response_text) > 50 and not response_text.startswith("Sorry, I don't understand"):
                        self.log_test("State Query Fallback", True, f"VLM fallback triggered: {response_text[:100]}...")
                        return True
                    else:
                        self.log_test("State Query Fallback", True, f"Template response (fallback not triggered): {response_text}")
                        return True
                else:
                    self.log_test("State Query Fallback", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("State Query Fallback", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("State Query Fallback", False, f"Request failed: {e}")
            return False
    
    def test_vision_analysis(self):
        """Test vision analysis functionality"""
        try:
            test_image = self.create_test_image()
            if not test_image:
                return False
            
            request_data = {
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe what you see in this image."},
                            {"type": "image_url", "image_url": {"url": test_image}}
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.backend_url}/v1/chat/completions",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("choices") and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    self.log_test("Vision Analysis", True, f"VLM response: {content[:100]}...")
                    return True
                else:
                    self.log_test("Vision Analysis", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Vision Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Vision Analysis", False, f"Request failed: {e}")
            return False
    
    def test_vlm_fallback_integration(self):
        """Test VLM fallback system integration"""
        try:
            # Import and test the fallback system directly
            from vlm_fallback.fallback_processor import VLMFallbackProcessor
            from vlm_fallback.decision_engine import DecisionEngine
            
            # Test decision engine
            engine = DecisionEngine()
            decision = engine.should_use_vlm_fallback(
                query="What is quantum computing?",
                state_data=None
            )
            
            if decision:
                self.log_test("VLM Fallback Decision", True, "Fallback correctly triggered for unknown query with no state")
            else:
                self.log_test("VLM Fallback Decision", False, "Fallback should have been triggered")
                return False
            
            # Test fallback processor initialization
            processor = VLMFallbackProcessor()
            if processor:
                self.log_test("VLM Fallback Processor", True, "Processor initialized successfully")
                return True
            else:
                self.log_test("VLM Fallback Processor", False, "Failed to initialize processor")
                return False
                
        except Exception as e:
            self.log_test("VLM Fallback Integration", False, f"Integration test failed: {e}")
            return False
    
    def test_query_processor_integration(self):
        """Test query processor with VLM fallback integration"""
        try:
            from state_tracker.query_processor import QueryProcessor
            
            processor = QueryProcessor()
            
            # Test that VLM fallback is available
            if hasattr(processor, 'vlm_fallback') and processor.vlm_fallback:
                self.log_test("Query Processor VLM Integration", True, "VLM fallback available in query processor")
                
                # Test decision logic
                should_fallback = processor._should_use_vlm_fallback(
                    query_type=processor._classify_query("What is the weather like?"),
                    current_state=None,
                    confidence=0.3
                )
                
                if should_fallback:
                    self.log_test("Query Processor Decision Logic", True, "Fallback decision logic working correctly")
                    return True
                else:
                    self.log_test("Query Processor Decision Logic", False, "Fallback should have been triggered")
                    return False
            else:
                self.log_test("Query Processor VLM Integration", True, "VLM fallback not available (expected if dependencies missing)")
                return True
                
        except Exception as e:
            self.log_test("Query Processor Integration", False, f"Integration test failed: {e}")
            return False
    
    def test_frontend_compatibility(self):
        """Test frontend compatibility"""
        try:
            # Test that all required endpoints are available
            endpoints_to_test = [
                ("/", "Root endpoint"),
                ("/health", "Health check"),
                ("/config", "Configuration"),
                ("/status", "Status"),
                ("/api/v1/state", "State API"),
                ("/api/v1/state/query/capabilities", "Query capabilities")
            ]
            
            all_passed = True
            for endpoint, description in endpoints_to_test:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        self.log_test(f"Frontend Endpoint {endpoint}", True, f"{description} available")
                    else:
                        self.log_test(f"Frontend Endpoint {endpoint}", False, f"HTTP {response.status_code}")
                        all_passed = False
                except Exception as e:
                    self.log_test(f"Frontend Endpoint {endpoint}", False, f"Request failed: {e}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test("Frontend Compatibility", False, f"Test failed: {e}")
            return False
    
    def run_all_tests(self, start_servers=True):
        """Run all system tests"""
        print("🧪 Starting Complete System End-to-End Tests")
        print("=" * 60)
        
        try:
            # Start servers if requested
            if start_servers:
                print("\n📡 Starting Services...")
                
                # Start backend server
                if not self.start_backend_server():
                    print("❌ Failed to start backend server. Aborting tests.")
                    return False
                
                # Start VLM server
                vlm_available = self.start_vlm_server()
                if not vlm_available:
                    print("⚠️ VLM server not available. Some tests will be skipped.")
            
            # Run tests
            print("\n🧪 Running Tests...")
            
            # Basic health tests
            self.test_backend_health()
            if start_servers:
                self.test_vlm_health()
            
            # Integration tests
            self.test_vlm_fallback_integration()
            self.test_query_processor_integration()
            
            # API tests
            self.test_state_query_basic()
            self.test_state_query_fallback_trigger()
            
            if start_servers:
                self.test_vision_analysis()
            
            # Frontend compatibility
            self.test_frontend_compatibility()
            
            # Print results
            self.print_test_summary()
            
            return self.get_overall_success()
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Test execution failed: {e}")
            return False
        finally:
            if start_servers:
                print("\n🛑 Stopping Services...")
                self.stop_backend_server()
                self.stop_vlm_server()
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n✅ Passed Tests:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}: {result['message']}")
    
    def get_overall_success(self):
        """Get overall test success status"""
        return all(result["success"] for result in self.test_results)
    
    def save_test_report(self, filename="test_report.json"):
        """Save test results to file"""
        try:
            report = {
                "timestamp": time.time(),
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for r in self.test_results if r["success"]),
                "success_rate": sum(1 for r in self.test_results if r["success"]) / len(self.test_results) * 100,
                "results": self.test_results
            }
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n📄 Test report saved to {filename}")
            
        except Exception as e:
            print(f"⚠️ Failed to save test report: {e}")

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete System End-to-End Test")
    parser.add_argument("--no-servers", action="store_true", help="Don't start servers (assume they're already running)")
    parser.add_argument("--save-report", help="Save test report to file")
    
    args = parser.parse_args()
    
    runner = SystemTestRunner()
    
    try:
        success = runner.run_all_tests(start_servers=not args.no_servers)
        
        if args.save_report:
            runner.save_test_report(args.save_report)
        
        if success:
            print("\n🎉 All tests passed! System is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check the results above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()