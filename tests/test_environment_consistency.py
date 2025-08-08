#!/usr/bin/env python3
"""
Environment Consistency Test

This test verifies that the VLM Fallback system works consistently
between test environment and production environment.
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

class EnvironmentConsistencyTester:
    """Test environment consistency for VLM Fallback system"""
    
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
        """Start services in production mode"""
        print("🚀 Starting services in production mode...")
        
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
            time.sleep(20)
        
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
                "--host", "127.0.0.1", "--port", str(self.backend_port)],
                cwd=str(backend_script.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            time.sleep(10)
        
        return self.check_services()
    
    def check_services(self):
        """Check if services are running"""
        try:
            model_response = requests.get(f"http://localhost:{self.model_port}/v1/models", timeout=5)
            model_ok = model_response.status_code == 200
            
            backend_response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            backend_ok = backend_response.status_code == 200
            
            print(f"📊 Service Status: Model={'✅' if model_ok else '❌'}, Backend={'✅' if backend_ok else '❌'}")
            return model_ok and backend_ok
        except:
            return False
    
    def test_api_endpoints_consistency(self):
        """Test that API endpoints work consistently"""
        print("\n🔍 Testing API Endpoints Consistency")
        print("=" * 50)
        
        tests = []
        
        # Test 1: Health check endpoint
        try:
            response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            tests.append({
                'name': 'Health Check',
                'success': response.status_code == 200,
                'details': f"Status: {response.status_code}"
            })
        except Exception as e:
            tests.append({
                'name': 'Health Check',
                'success': False,
                'details': f"Error: {e}"
            })
        
        # Test 2: State query endpoint
        try:
            response = requests.post(
                f"http://localhost:{self.backend_port}/api/v1/state/query",
                json={"query": "What step am I on?"},
                timeout=10
            )
            tests.append({
                'name': 'State Query',
                'success': response.status_code == 200,
                'details': f"Status: {response.status_code}"
            })
        except Exception as e:
            tests.append({
                'name': 'State Query',
                'success': False,
                'details': f"Error: {e}"
            })
        
        # Test 3: VLM chat completions endpoint
        try:
            response = requests.post(
                f"http://localhost:{self.backend_port}/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": "Hello, how are you?"}],
                    "max_tokens": 50
                },
                timeout=15
            )
            tests.append({
                'name': 'VLM Chat Completions',
                'success': response.status_code == 200,
                'details': f"Status: {response.status_code}"
            })
        except Exception as e:
            tests.append({
                'name': 'VLM Chat Completions',
                'success': False,
                'details': f"Error: {e}"
            })
        
        # Print results
        for test in tests:
            status = "✅" if test['success'] else "❌"
            print(f"{status} {test['name']}: {test['details']}")
        
        success_count = sum(1 for t in tests if t['success'])
        return success_count == len(tests)
    
    def test_vlm_fallback_integration(self):
        """Test VLM Fallback integration consistency"""
        print("\n🔍 Testing VLM Fallback Integration")
        print("=" * 50)
        
        # Test queries that should trigger VLM Fallback
        fallback_queries = [
            "What is the meaning of life?",
            "Tell me a joke",
            "What am I doing?",
            "What do you see in this image?"
        ]
        
        fallback_triggered = 0
        
        for query in fallback_queries:
            try:
                response = requests.post(
                    f"http://localhost:{self.backend_port}/api/v1/state/query",
                    json={"query": query},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    query_type = data.get('query_type', 'unknown')
                    confidence = data.get('confidence', 0.0)
                    response_text = data.get('response', '')
                    
                    # Check if VLM Fallback was likely triggered
                    likely_fallback = (
                        query_type == 'unknown' or 
                        confidence < 0.4 or 
                        len(response_text) > 50
                    )
                    
                    if likely_fallback:
                        fallback_triggered += 1
                    
                    status = "✅" if likely_fallback else "⚠️"
                    print(f"{status} '{query}' -> Type: {query_type}, Confidence: {confidence:.2f}")
                else:
                    print(f"❌ '{query}' -> HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ '{query}' -> Error: {e}")
        
        success_rate = fallback_triggered / len(fallback_queries)
        print(f"\n📊 VLM Fallback Trigger Rate: {success_rate*100:.1f}% ({fallback_triggered}/{len(fallback_queries)})")
        
        return success_rate >= 0.75  # 75% or more should trigger fallback
    
    def test_image_processing_consistency(self):
        """Test image processing consistency"""
        print("\n🔍 Testing Image Processing Consistency")
        print("=" * 50)
        
        # Create a simple test image
        test_image_b64 = self.create_simple_test_image()
        
        if not test_image_b64:
            print("❌ Failed to create test image")
            return False
        
        try:
            # Send image to VLM system
            response = requests.post(
                f"http://localhost:{self.backend_port}/v1/chat/completions",
                json={
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Describe this image."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{test_image_b64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 100
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    print(f"✅ Image processed successfully")
                    print(f"📄 Response: {content[:100]}...")
                    
                    # Wait and test VLM Fallback with image
                    time.sleep(2)
                    
                    fallback_response = requests.post(
                        f"http://localhost:{self.backend_port}/api/v1/state/query",
                        json={"query": "What do you see in this image?"},
                        timeout=15
                    )
                    
                    if fallback_response.status_code == 200:
                        fallback_data = fallback_response.json()
                        fallback_text = fallback_data.get('response', '')
                        print(f"✅ VLM Fallback with image works")
                        print(f"📄 Fallback Response: {fallback_text[:100]}...")
                        return True
                    else:
                        print(f"❌ VLM Fallback failed: HTTP {fallback_response.status_code}")
                        return False
                else:
                    print("❌ Invalid VLM response format")
                    return False
            else:
                print(f"❌ Image processing failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Image processing error: {e}")
            return False
    
    def create_simple_test_image(self):
        """Create a simple test image as base64"""
        try:
            # Create a simple 100x100 red square PNG
            from PIL import Image
            import io
            
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            import base64
            return base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        except ImportError:
            print("⚠️ PIL not available, skipping image test")
            return None
        except Exception as e:
            print(f"⚠️ Failed to create test image: {e}")
            return None
    
    def test_configuration_consistency(self):
        """Test configuration consistency"""
        print("\n🔍 Testing Configuration Consistency")
        print("=" * 50)
        
        config_checks = []
        
        # Check VLM Fallback config file
        config_file = self.base_dir / "src/config/vlm_fallback_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Check key configuration values
                vlm_config = config.get('vlm_fallback', {})
                confidence_threshold = vlm_config.get('decision_engine', {}).get('confidence_threshold', 0.0)
                model_url = vlm_config.get('vlm_client', {}).get('model_server_url', '')
                image_fallback = vlm_config.get('enable_image_fallback', False)
                
                config_checks.append({
                    'name': 'VLM Fallback Config File',
                    'success': True,
                    'details': f"Threshold: {confidence_threshold}, URL: {model_url}, Image: {image_fallback}"
                })
            except Exception as e:
                config_checks.append({
                    'name': 'VLM Fallback Config File',
                    'success': False,
                    'details': f"Error: {e}"
                })
        else:
            config_checks.append({
                'name': 'VLM Fallback Config File',
                'success': False,
                'details': "File not found"
            })
        
        # Print results
        for check in config_checks:
            status = "✅" if check['success'] else "❌"
            print(f"{status} {check['name']}: {check['details']}")
        
        return all(check['success'] for check in config_checks)
    
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
    
    def run_consistency_test(self):
        """Run complete consistency test"""
        print("🎯 Environment Consistency Test")
        print("=" * 60)
        print("Verifying VLM Fallback system consistency between test and production environments")
        print()
        
        try:
            # Start services
            if not self.start_services():
                print("❌ Failed to start services")
                return False
            
            # Run consistency tests
            tests = [
                ("API Endpoints", self.test_api_endpoints_consistency),
                ("VLM Fallback Integration", self.test_vlm_fallback_integration),
                ("Image Processing", self.test_image_processing_consistency),
                ("Configuration", self.test_configuration_consistency)
            ]
            
            passed_tests = 0
            for test_name, test_method in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                try:
                    if test_method():
                        passed_tests += 1
                        print(f"🏆 {test_name}: ✅ PASS")
                    else:
                        print(f"🏆 {test_name}: ❌ FAIL")
                except Exception as e:
                    print(f"🏆 {test_name}: ❌ Exception - {e}")
                
                time.sleep(1)
            
            # Final assessment
            success_rate = (passed_tests / len(tests)) * 100
            
            print(f"\n📊 Environment Consistency Test Results")
            print("=" * 60)
            print(f"   Tests Passed: {passed_tests}/{len(tests)}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 75:
                print("\n✅ Environment Consistency Test: PASS")
                print("🎯 VLM Fallback system is consistent between test and production environments")
                return True
            else:
                print("\n❌ Environment Consistency Test: FAIL")
                print("🔧 Some inconsistencies detected, review needed")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
            return False
        finally:
            self.cleanup()

def main():
    """Main function"""
    tester = EnvironmentConsistencyTester()
    success = tester.run_consistency_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()