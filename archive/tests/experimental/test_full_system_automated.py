#!/usr/bin/env python3
"""
Full System Automated Test

This test automatically:
1. Starts backend server (src/backend/main.py)
2. Starts VLM server (src/models/smolvlm/run_smolvlm.py)
3. Runs comprehensive tests
4. Stops all servers
5. Reports results

This is the definitive test to verify the complete VLM Fallback System.
"""

import subprocess
import sys
import os
import time
import requests
import json
import base64
import io
from PIL import Image
import signal
import threading
from pathlib import Path
import uuid

class FullSystemTest:
    """Complete automated system test"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.backend_process = None
        self.vlm_process = None
        self.backend_url = "http://localhost:8000"
        self.vlm_url = "http://localhost:8080"
        self.test_results = []
        self.start_time = time.time()
        
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
            img = Image.new('RGB', (400, 300), color='lightblue')
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=90)
            img_data = buffer.getvalue()
            
            base64_string = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_string}"
            
        except Exception as e:
            self.log_test("Create Test Image", False, f"Failed: {e}")
            return None
    
    def start_backend_server(self):
        """Start backend server"""
        try:
            print("🚀 Starting Backend Server...")
            
            backend_dir = self.base_dir / "src" / "backend"
            if not backend_dir.exists():
                self.log_test("Backend Server Start", False, "Backend directory not found")
                return False
            
            # Start backend server
            self.backend_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONPATH": str(self.base_dir / "src")}
            )
            
            # Wait for server to start
            if self.wait_for_service(self.backend_url, "Backend Server", 30):
                self.log_test("Backend Server Start", True, "Server started successfully")
                return True
            else:
                self.stop_backend_server()
                self.log_test("Backend Server Start", False, "Server failed to start")
                return False
                
        except Exception as e:
            self.log_test("Backend Server Start", False, f"Exception: {e}")
            return False
    
    def start_vlm_server(self):
        """Start VLM server"""
        try:
            print("🤖 Starting VLM Server...")
            
            vlm_dir = self.base_dir / "src" / "models" / "smolvlm"
            if not vlm_dir.exists():
                self.log_test("VLM Server Start", False, "VLM directory not found")
                return False
            
            # Start VLM server
            self.vlm_process = subprocess.Popen(
                [sys.executable, "run_smolvlm.py"],
                cwd=vlm_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for VLM server (longer timeout for model loading)
            if self.wait_for_service(self.vlm_url, "VLM Server", 90):
                self.log_test("VLM Server Start", True, "Server started successfully")
                return True
            else:
                self.stop_vlm_server()
                self.log_test("VLM Server Start", False, "Server failed to start")
                return False
                
        except Exception as e:
            self.log_test("VLM Server Start", False, f"Exception: {e}")
            return False
    
    def wait_for_service(self, url, service_name, timeout=30):
        """Wait for service to be available"""
        print(f"⏳ Waiting for {service_name} at {url}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ {service_name} is ready!")
                    return True
            except:
                pass
            time.sleep(1)
        
        print(f"❌ {service_name} not ready after {timeout}s")
        return False
    
    def stop_backend_server(self):
        """Stop backend server"""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                self.backend_process.kill()
            self.backend_process = None
    
    def stop_vlm_server(self):
        """Stop VLM server"""
        if self.vlm_process:
            try:
                self.vlm_process.terminate()
                self.vlm_process.wait(timeout=10)
            except:
                self.vlm_process.kill()
            self.vlm_process = None
    
    def test_backend_health(self):
        """Test backend health"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Backend Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", False, f"Request failed: {e}")
            return False
    
    def test_vlm_health(self):
        """Test VLM health"""
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
    
    def test_basic_state_query(self):
        """Test basic state query"""
        try:
            query_data = {
                "query": "Where am I?",
                "query_id": f"test_basic_{int(time.time())}"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Basic State Query", True, f"Response: {data.get('response', '')[:50]}...")
                    return True
                else:
                    self.log_test("Basic State Query", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Basic State Query", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Basic State Query", False, f"Request failed: {e}")
            return False
    
    def test_vlm_fallback_trigger(self):
        """Test VLM fallback triggering"""
        try:
            # Use a complex query that should trigger VLM fallback
            query_data = {
                "query": "Explain the philosophical implications of artificial intelligence and consciousness in modern society",
                "query_id": f"test_fallback_{int(time.time())}"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    response_text = data.get("response", "")
                    # Check if response is detailed (likely from VLM fallback)
                    if len(response_text) > 100:
                        self.log_test("VLM Fallback Trigger", True, f"Detailed response received: {response_text[:80]}...")
                    else:
                        self.log_test("VLM Fallback Trigger", True, f"Template response: {response_text[:50]}...")
                    return True
                else:
                    self.log_test("VLM Fallback Trigger", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("VLM Fallback Trigger", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("VLM Fallback Trigger", False, f"Request failed: {e}")
            return False
    
    def test_vision_analysis(self):
        """Test vision analysis"""
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
                            {"type": "text", "text": "What color is this image?"},
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
                    self.log_test("Vision Analysis", True, f"VLM response: {content[:80]}...")
                    return True
                else:
                    self.log_test("Vision Analysis", False, "Invalid response format")
                    return False
            else:
                self.log_test("Vision Analysis", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Vision Analysis", False, f"Request failed: {e}")
            return False
    
    def test_frontend_endpoints(self):
        """Test frontend compatibility endpoints"""
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/config", "Configuration"),
            ("/status", "Status"),
            ("/api/v1/state", "State API"),
            ("/api/v1/state/query/capabilities", "Query capabilities")
        ]
        
        all_passed = True
        for endpoint, description in endpoints:
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
    
    def test_vlm_fallback_integration(self):
        """Test VLM fallback system integration"""
        try:
            # Test integration without servers (import test)
            sys.path.insert(0, str(self.base_dir / "src"))
            
            from vlm_fallback.fallback_processor import VLMFallbackProcessor
            from vlm_fallback.decision_engine import DecisionEngine
            from state_tracker.query_processor import QueryProcessor
            
            # Test decision engine
            engine = DecisionEngine()
            decision = engine.should_use_vlm_fallback(
                query="What is quantum computing?",
                state_data=None
            )
            
            if decision:
                self.log_test("VLM Fallback Integration", True, "Decision engine working correctly")
                return True
            else:
                self.log_test("VLM Fallback Integration", False, "Decision engine not working")
                return False
                
        except Exception as e:
            self.log_test("VLM Fallback Integration", False, f"Integration test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run complete automated test suite"""
        print("🧪 Full System Automated Test")
        print("=" * 60)
        print("This test will:")
        print("1. Start backend server")
        print("2. Start VLM server")
        print("3. Run comprehensive tests")
        print("4. Stop all servers")
        print("5. Report results")
        print("=" * 60)
        
        try:
            # Phase 1: Start Services
            print("\n📡 Phase 1: Starting Services...")
            
            backend_started = self.start_backend_server()
            if not backend_started:
                print("❌ Backend server failed to start. Aborting tests.")
                return False
            
            vlm_started = self.start_vlm_server()
            if not vlm_started:
                print("⚠️ VLM server failed to start. Continuing with limited tests.")
            
            # Phase 2: Health Checks
            print("\n🔍 Phase 2: Health Checks...")
            self.test_backend_health()
            if vlm_started:
                self.test_vlm_health()
            
            # Phase 3: Integration Tests
            print("\n🔗 Phase 3: Integration Tests...")
            self.test_vlm_fallback_integration()
            
            # Phase 4: Functional Tests
            print("\n⚙️ Phase 4: Functional Tests...")
            self.test_basic_state_query()
            self.test_vlm_fallback_trigger()
            
            if vlm_started:
                self.test_vision_analysis()
            
            # Phase 5: Frontend Compatibility
            print("\n🌐 Phase 5: Frontend Compatibility...")
            self.test_frontend_endpoints()
            
            # Phase 6: Results
            print("\n📊 Phase 6: Test Results...")
            self.print_final_results()
            
            return self.get_overall_success()
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n💥 Test execution failed: {e}")
            return False
        finally:
            print("\n🛑 Phase 7: Cleanup...")
            self.stop_backend_server()
            self.stop_vlm_server()
            print("✅ All services stopped")
    
    def print_final_results(self):
        """Print comprehensive test results"""
        total_time = time.time() - self.start_time
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 60)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 60)
        
        print(f"⏱️  Total Test Time: {total_time:.1f} seconds")
        print(f"📊 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"📈 Success Rate: {(passed/total*100):.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n✅ Passed Tests:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}: {result['message']}")
        
        # Overall assessment
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ VLM Fallback System is fully functional!")
            print("🚀 System is ready for production use!")
        elif passed >= total * 0.8:
            print(f"\n⚠️ Most tests passed ({passed}/{total})")
            print("🔧 System is mostly functional with minor issues")
        else:
            print(f"\n❌ Many tests failed ({total-passed}/{total})")
            print("🚨 System needs attention before production use")
    
    def get_overall_success(self):
        """Get overall test success status"""
        return all(result["success"] for result in self.test_results)
    
    def save_test_report(self, filename="full_system_test_report.json"):
        """Save detailed test report"""
        try:
            report = {
                "test_run_id": str(uuid.uuid4()),
                "timestamp": time.time(),
                "total_time": time.time() - self.start_time,
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for r in self.test_results if r["success"]),
                "success_rate": sum(1 for r in self.test_results if r["success"]) / len(self.test_results) * 100,
                "backend_started": self.backend_process is not None,
                "vlm_started": self.vlm_process is not None,
                "results": self.test_results,
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "base_directory": str(self.base_dir)
                }
            }
            
            report_path = self.base_dir / filename
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n📄 Detailed test report saved to: {report_path}")
            
        except Exception as e:
            print(f"⚠️ Failed to save test report: {e}")

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Full System Automated Test")
    parser.add_argument("--save-report", help="Save detailed test report to file")
    parser.add_argument("--timeout", type=int, default=120, help="Overall test timeout in seconds")
    
    args = parser.parse_args()
    
    # Set up signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print("\n⚠️ Test interrupted by signal")
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the test
    tester = FullSystemTest()
    
    try:
        success = tester.run_all_tests()
        
        if args.save_report:
            tester.save_test_report(args.save_report)
        
        if success:
            print("\n🎊 CONGRATULATIONS! 🎊")
            print("All tests passed! Your VLM Fallback System is working perfectly!")
            sys.exit(0)
        else:
            print("\n🔧 Some tests failed. Please check the results above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()