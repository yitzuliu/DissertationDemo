#!/usr/bin/env python3
"""
Stage 3.1: Correct Service Startup and Communication Test Flow

Following the correct sequence:
1. Start model service (SmolVLM on port 8080)
2. Start backend service (Backend on port 8000) 
3. Test service communication functionality
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path

class Stage31ProperTester:
    def __init__(self):
        self.model_port = 8080
        self.backend_port = 8000
        self.model_process = None
        self.backend_process = None
        self.max_retries = 3
        
        # Virtual environment setup
        self.base_dir = Path(__file__).parent.parent.parent
        self.venv_path = self.base_dir / "ai_vision_env"
        self.python_executable = self.venv_path / "bin" / "python"
        
        if not self.python_executable.exists():
            print(f"⚠️ Virtual environment Python path doesn't exist: {self.python_executable}")
            print(f"Will use system Python: {sys.executable}")
            self.python_executable = sys.executable
        
    def kill_port(self, port):
        """Force close processes occupying port"""
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], 
                capture_output=True, text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(["kill", "-9", pid])
                print(f"✅ Forcibly closed processes on port {port}")
                time.sleep(2)
        except Exception as e:
            print(f"⚠️ Error cleaning up port {port}: {e}")
    
    def start_model_service(self):
        """Step 1: Start model service (run_smolvlm.py)"""
        print("🚀 Step 1: Starting model service (SmolVLM)")
        print("=" * 50)
        
        # Use absolute path to ensure correct script location
        model_script = self.base_dir / "src/models/smolvlm/run_smolvlm.py"
        if not model_script.exists():
            print(f"❌ Model startup script doesn't exist: {model_script}")
            return False
        
        print(f"🐍 Using Python: {self.python_executable}")
        print(f"📄 Model script: {model_script}")
        
        for attempt in range(self.max_retries):
            print(f"📋 Attempt {attempt + 1}/{self.max_retries} to start model service...")
            
            # Clean up port
            self.kill_port(self.model_port)
            
            try:
                # Set environment variables, activate virtual environment
                env = os.environ.copy()
                if self.venv_path.exists():
                    env["VIRTUAL_ENV"] = str(self.venv_path)
                    env["PATH"] = f"{self.venv_path / 'bin'}:{env.get('PATH', '')}"
                
                # Start model service
                self.model_process = subprocess.Popen(
                    [str(self.python_executable), str(model_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    cwd=str(model_script.parent)
                )
                
                # Wait for startup
                print("⏳ Waiting for model service to start...")
                time.sleep(20)  # SmolVLM needs more time to start
                
                # Check service status
                if self.check_model_service():
                    print("✅ Model service started successfully")
                    return True
                else:
                    print(f"❌ Attempt {attempt + 1} failed")
                    if self.model_process:
                        self.model_process.terminate()
                        
            except Exception as e:
                print(f"❌ Error starting model service: {e}")
        
        print("❌ Model service startup failed, reached maximum retry attempts")
        return False
    
    def check_model_service(self):
        """Check if model service is running normally"""
        try:
            # Check process status
            if self.model_process and self.model_process.poll() is not None:
                print("❌ Model process has terminated")
                return False
            
            # Check port response - llama-server usually listens on root path
            try:
                response = requests.get(f"http://localhost:{self.model_port}/v1/models", timeout=10)
                if response.status_code == 200:
                    print("✅ Model service /v1/models endpoint responding normally")
                    return True
            except Exception as e:
                print(f"⚠️ /v1/models check failed: {e}")
            
            # Backup check: try root path
            try:
                response = requests.get(f"http://localhost:{self.model_port}/", timeout=5)
                if response.status_code in [200, 404]:  # 404 also indicates service is running
                    print("✅ Model service root path responding normally")
                    return True
            except Exception as e:
                print(f"⚠️ Root path check failed: {e}")
            
            return False
        except Exception as e:
            print(f"❌ Error checking model service: {e}")
            return False
    
    def start_backend_service(self):
        """Step 2: Start backend service (main.py)"""
        print("\n🚀 Step 2: Starting backend service")
        print("=" * 50)
        
        # Use absolute path to ensure correct script location
        backend_script = self.base_dir / "src/backend/main.py"
        if not backend_script.exists():
            print(f"❌ Backend startup script doesn't exist: {backend_script}")
            return False
        
        print(f"🐍 Using Python: {self.python_executable}")
        print(f"📄 Backend script: {backend_script}")
        
        for attempt in range(self.max_retries):
            print(f"📋 Attempt {attempt + 1}/{self.max_retries} to start backend service...")
            
            # Clean up port
            self.kill_port(self.backend_port)
            
            try:
                # Set environment variables, activate virtual environment
                env = os.environ.copy()
                if self.venv_path.exists():
                    env["VIRTUAL_ENV"] = str(self.venv_path)
                    env["PATH"] = f"{self.venv_path / 'bin'}:{env.get('PATH', '')}"
                    env["PYTHONPATH"] = str(self.base_dir / "src")
                
                # Start backend service - use uvicorn command
                self.backend_process = subprocess.Popen(
                    [str(self.python_executable), "-m", "uvicorn", "main:app", 
                     "--host", "127.0.0.1", "--port", str(self.backend_port), "--reload"],
                    cwd=str(backend_script.parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env
                )
                
                # Wait for startup
                print("⏳ Waiting for backend service to start...")
                time.sleep(10)  # Give more time for backend to start
                
                # Check service status
                if self.check_backend_service():
                    print("✅ Backend service started successfully")
                    return True
                else:
                    print(f"❌ Attempt {attempt + 1} failed")
                    if self.backend_process:
                        self.backend_process.terminate()
                        time.sleep(2)
                        
            except Exception as e:
                print(f"❌ Error starting backend service: {e}")
        
        print("❌ Backend service startup failed, reached maximum retry attempts")
        return False
    
    def check_backend_service(self):
        """Check if backend service is running normally"""
        try:
            # Check process status
            if self.backend_process and self.backend_process.poll() is not None:
                print("❌ Backend process has terminated")
                if self.backend_process.stderr:
                    stderr_output = self.backend_process.stderr.read()
                    if stderr_output:
                        print(f"❌ Backend error message: {stderr_output[:200]}...")
                return False
            
            # Check port response
            response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend health check endpoint responding normally")
                return True
            else:
                print(f"❌ Backend health check returned: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error checking backend service: {e}")
            return False
    
    def test_service_communication(self):
        """Step 3: Test service communication functionality"""
        print("\n🚀 Step 3: Testing service communication functionality")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Backend health check
        total_tests += 1
        print("📋 Test 1: Backend health check...")
        try:
            response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend health check passed")
                tests_passed += 1
            else:
                print(f"❌ Backend health check failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Backend health check connection failed: {e}")
        
        # Test 2: Backend status endpoint
        total_tests += 1
        print("📋 Test 2: Backend status endpoint...")
        try:
            response = requests.get(f"http://localhost:{self.backend_port}/status", timeout=5)
            if response.status_code == 200:
                print("✅ Backend status endpoint normal")
                tests_passed += 1
            else:
                print(f"❌ Backend status endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Backend status endpoint connection failed: {e}")
        
        # Test 3: Model service communication (via backend)
        total_tests += 1
        print("📋 Test 3: Model service communication...")
        try:
            test_data = {
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Hello, can you see this message?"}
                        ]
                    }
                ]
            }
            response = requests.post(
                f"http://localhost:{self.backend_port}/v1/chat/completions",
                json=test_data,
                timeout=30
            )
            if response.status_code == 200:
                print("✅ Model service communication normal")
                tests_passed += 1
            else:
                print(f"❌ Model service communication failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Model service communication connection failed: {e}")
        
        # Test 4: State Tracker endpoint
        total_tests += 1
        print("📋 Test 4: State Tracker endpoint...")
        try:
            response = requests.get(f"http://localhost:{self.backend_port}/api/v1/state", timeout=5)
            if response.status_code == 200:
                print("✅ State Tracker endpoint normal")
                tests_passed += 1
            else:
                print(f"❌ State Tracker endpoint failed: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Response content: {response.text[:200]}")
        except Exception as e:
            print(f"❌ State Tracker endpoint connection failed: {e}")
        
        # Test 5: State Tracker VLM processing endpoint
        total_tests += 1
        print("📋 Test 5: State Tracker VLM processing...")
        try:
            test_vlm_data = {
                "text": "User is preparing coffee beans and grinding equipment"
            }
            response = requests.post(
                f"http://localhost:{self.backend_port}/api/v1/state/process",
                json=test_vlm_data,
                timeout=10
            )
            if response.status_code == 200:
                print("✅ State Tracker VLM processing normal")
                tests_passed += 1
            else:
                print(f"❌ State Tracker VLM processing failed: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Response content: {response.text[:200]}")
        except Exception as e:
            print(f"❌ State Tracker VLM processing connection failed: {e}")
        
        # Test 6: State Tracker instant query
        total_tests += 1
        print("📋 Test 6: State Tracker instant query...")
        try:
            test_query_data = {
                "query": "What step am I on now?"
            }
            response = requests.post(
                f"http://localhost:{self.backend_port}/api/v1/state/query",
                json=test_query_data,
                timeout=5
            )
            if response.status_code == 200:
                print("✅ State Tracker instant query normal")
                tests_passed += 1
            else:
                print(f"❌ State Tracker instant query failed: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Response content: {response.text[:200]}")
        except Exception as e:
            print(f"❌ State Tracker instant query connection failed: {e}")
        
        # Display test results
        print(f"\n📊 Test Results Summary:")
        print(f"   Passed tests: {tests_passed}/{total_tests}")
        print(f"   Success rate: {(tests_passed/total_tests*100):.1f}%")
        
        return tests_passed == total_tests
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Cleaning up processes...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.model_process:
            self.model_process.terminate()
            try:
                self.model_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.model_process.kill()
        
        print("✅ Cleanup completed")
    
    def run_full_test(self):
        """Execute complete Stage 3.1 test"""
        print("🎯 Stage 3.1: Correct Service Startup and Communication Test")
        print("=" * 60)
        
        try:
            # Step 1: Start model service
            if not self.start_model_service():
                print("❌ Stage 3.1 test failed: Model service startup failed")
                return False
            
            # Step 2: Start backend service
            if not self.start_backend_service():
                print("❌ Stage 3.1 test failed: Backend service startup failed")
                return False
            
            # Step 3: Test service communication
            if self.test_service_communication():
                print("\n✅ Stage 3.1 test completed successfully!")
                print("🎯 All services running normally, communication functionality normal")
                return True
            else:
                print("\n⚠️ Stage 3.1 partial test failure")
                print("🔧 Service startup successful, but communication functionality has issues")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
            return False
        finally:
            self.cleanup()

def main():
    tester = Stage31ProperTester()
    success = tester.run_full_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()