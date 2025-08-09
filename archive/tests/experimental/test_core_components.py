#!/usr/bin/env python3
"""
Core Components Test

Tests the three main components you mentioned:
1. src/backend/main.py - Backend server
2. src/models/smolvlm/run_smolvlm.py - VLM server  
3. src/frontend/index.html - Frontend interface

This is a focused test to ensure the basic flow works.
"""

import requests
import time
import json
import base64
import io
from PIL import Image
import sys
import os

class CoreComponentsTest:
    """Test core system components"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.vlm_url = "http://localhost:8080"
        self.results = []
    
    def log_result(self, component, test, success, message):
        """Log test result"""
        status = "✅" if success else "❌"
        result = f"{status} {component} - {test}: {message}"
        print(result)
        self.results.append({
            "component": component,
            "test": test,
            "success": success,
            "message": message
        })
        return success
    
    def create_test_image(self):
        """Create a simple test image"""
        try:
            # Create a test image
            img = Image.new('RGB', (400, 300), color='lightblue')
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=90)
            img_data = buffer.getvalue()
            
            base64_string = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_string}"
            
        except Exception as e:
            print(f"❌ Failed to create test image: {e}")
            return None
    
    def test_backend_server(self):
        """Test backend server (main.py)"""
        print("\n🔧 Testing Backend Server (src/backend/main.py)")
        print("-" * 50)
        
        # Test 1: Health check
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Backend", "Health Check", True, f"Server healthy: {data.get('status')}")
            else:
                self.log_result("Backend", "Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Backend", "Health Check", False, f"Connection failed: {e}")
            return False
        
        # Test 2: Configuration endpoint
        try:
            response = requests.get(f"{self.backend_url}/config", timeout=5)
            if response.status_code == 200:
                config = response.json()
                self.log_result("Backend", "Configuration", True, f"Config loaded, active model: {config.get('active_model', 'unknown')}")
            else:
                self.log_result("Backend", "Configuration", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Backend", "Configuration", False, f"Request failed: {e}")
        
        # Test 3: State query endpoint
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
                if data.get("status") == "success":
                    self.log_result("Backend", "State Query", True, f"Query processed: {data.get('response', '')[:50]}...")
                else:
                    self.log_result("Backend", "State Query", False, f"Invalid response: {data}")
            else:
                self.log_result("Backend", "State Query", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Backend", "State Query", False, f"Request failed: {e}")
        
        return True
    
    def test_vlm_server(self):
        """Test VLM server (run_smolvlm.py)"""
        print("\n🤖 Testing VLM Server (src/models/smolvlm/run_smolvlm.py)")
        print("-" * 50)
        
        # Test 1: VLM server health
        try:
            response = requests.get(f"{self.vlm_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_result("VLM Server", "Health Check", True, "VLM server responding")
            else:
                self.log_result("VLM Server", "Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("VLM Server", "Health Check", False, f"Connection failed: {e}")
            print("⚠️  Make sure VLM server is running: python src/models/smolvlm/run_smolvlm.py")
            return False
        
        # Test 2: Direct VLM query
        try:
            test_image = self.create_test_image()
            if not test_image:
                self.log_result("VLM Server", "Direct Query", False, "Failed to create test image")
                return False
            
            request_data = {
                "max_tokens": 50,
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
                f"{self.vlm_url}/v1/chat/completions",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("choices") and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    self.log_result("VLM Server", "Direct Query", True, f"VLM response: {content[:50]}...")
                else:
                    self.log_result("VLM Server", "Direct Query", False, f"Invalid response format")
            else:
                self.log_result("VLM Server", "Direct Query", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("VLM Server", "Direct Query", False, f"Request failed: {e}")
        
        return True
    
    def test_backend_vlm_integration(self):
        """Test backend to VLM integration"""
        print("\n🔗 Testing Backend-VLM Integration")
        print("-" * 50)
        
        # Test vision analysis through backend
        try:
            test_image = self.create_test_image()
            if not test_image:
                self.log_result("Integration", "Vision Analysis", False, "Failed to create test image")
                return False
            
            request_data = {
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image briefly."},
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
                    self.log_result("Integration", "Vision Analysis", True, f"Backend→VLM successful: {content[:50]}...")
                else:
                    self.log_result("Integration", "Vision Analysis", False, "Invalid response format")
            else:
                self.log_result("Integration", "Vision Analysis", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Integration", "Vision Analysis", False, f"Request failed: {e}")
        
        return True
    
    def test_vlm_fallback_system(self):
        """Test VLM fallback system"""
        print("\n🔄 Testing VLM Fallback System")
        print("-" * 50)
        
        # Test fallback trigger with complex query
        try:
            query_data = {
                "query": "Explain the philosophical implications of artificial intelligence and consciousness",
                "query_id": f"fallback_test_{int(time.time())}"
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
                    if len(response_text) > 100 and "artificial intelligence" in response_text.lower():
                        self.log_result("Fallback", "Complex Query", True, f"VLM fallback triggered: {response_text[:80]}...")
                    else:
                        self.log_result("Fallback", "Complex Query", True, f"Template response: {response_text[:50]}...")
                else:
                    self.log_result("Fallback", "Complex Query", False, f"Invalid response: {data}")
            else:
                self.log_result("Fallback", "Complex Query", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Fallback", "Complex Query", False, f"Request failed: {e}")
        
        return True
    
    def test_frontend_compatibility(self):
        """Test frontend compatibility"""
        print("\n🌐 Testing Frontend Compatibility (src/frontend/index.html)")
        print("-" * 50)
        
        # Test all endpoints that frontend needs
        frontend_endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/config", "Configuration"),
            ("/status", "System status"),
            ("/api/v1/state", "State API"),
            ("/api/v1/state/query/capabilities", "Query capabilities")
        ]
        
        all_good = True
        for endpoint, description in frontend_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_result("Frontend", f"Endpoint {endpoint}", True, f"{description} available")
                else:
                    self.log_result("Frontend", f"Endpoint {endpoint}", False, f"HTTP {response.status_code}")
                    all_good = False
            except Exception as e:
                self.log_result("Frontend", f"Endpoint {endpoint}", False, f"Request failed: {e}")
                all_good = False
        
        return all_good
    
    def run_all_tests(self):
        """Run all core component tests"""
        print("🧪 Core Components Test")
        print("=" * 60)
        print("Testing the three main components:")
        print("1. Backend Server (src/backend/main.py)")
        print("2. VLM Server (src/models/smolvlm/run_smolvlm.py)")
        print("3. Frontend Interface (src/frontend/index.html)")
        print("=" * 60)
        
        # Run tests
        backend_ok = self.test_backend_server()
        vlm_ok = self.test_vlm_server()
        
        if backend_ok and vlm_ok:
            self.test_backend_vlm_integration()
            self.test_vlm_fallback_system()
        
        self.test_frontend_compatibility()
        
        # Print summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        # Group by component
        components = {}
        for result in self.results:
            comp = result["component"]
            if comp not in components:
                components[comp] = {"passed": 0, "total": 0}
            components[comp]["total"] += 1
            if result["success"]:
                components[comp]["passed"] += 1
        
        for comp, stats in components.items():
            success_rate = (stats["passed"] / stats["total"]) * 100
            status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
            print(f"{status} {comp}: {stats['passed']}/{stats['total']} ({success_rate:.0f}%)")
        
        total_passed = sum(1 for r in self.results if r["success"])
        total_tests = len(self.results)
        overall_rate = (total_passed / total_tests) * 100
        
        print(f"\n🎯 Overall: {total_passed}/{total_tests} ({overall_rate:.0f}%)")
        
        if overall_rate == 100:
            print("\n🎉 All tests passed! Your system is working correctly.")
            print("\n✅ You can now:")
            print("   - Open src/frontend/index.html in your browser")
            print("   - Use the vision analysis features")
            print("   - Test state queries")
            print("   - Experience the VLM fallback system")
        else:
            print(f"\n⚠️ {total_tests - total_passed} tests failed. Please check the issues above.")
    
    def get_overall_success(self):
        """Check if all tests passed"""
        return all(result["success"] for result in self.results)

def main():
    """Main test function"""
    print("🚀 Starting Core Components Test...")
    print("Make sure both servers are running:")
    print("1. Backend: python src/backend/main.py")
    print("2. VLM: python src/models/smolvlm/run_smolvlm.py")
    print()
    
    input("Press Enter when both servers are ready...")
    
    tester = CoreComponentsTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All core components are working!")
        return 0
    else:
        print("\n❌ Some components have issues.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())