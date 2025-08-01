#!/usr/bin/env python3
"""
Unified SmolVLM Testing Suite

Comprehensive testing script for SmolVLM model with server management and optimization.
Combines features from both comprehensive and unified test suites.

Environment: llama-server with OpenAI API compatibility
Model: SmolVLM-500M-Instruct-GGUF
"""

import time
import requests
import base64
import json
import os
import subprocess
import threading
import signal
import sys
from PIL import Image
from pathlib import Path
from typing import Optional, List, Dict, Any
import io

class SmolVLMTestSuite:
    """Unified testing suite for SmolVLM model."""
    
    def __init__(self):
        """Initialize the test suite with server management."""
        self.model_name = "ggml-org/SmolVLM-500M-Instruct-GGUF"
        self.port = 8080
        self.server_url = f"http://localhost:{self.port}/v1/chat/completions"
        self.health_url = f"http://localhost:{self.port}/health"
        self.headers = {"Content-Type": "application/json"}
        self.timeout = 60
        
        # Server process management
        self.server_process = None
        self.server_ready = False
        self.output_thread = None
        
        # Get paths relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_paths = [
            os.path.join(script_dir, "../../debug/images/IMG_0119.JPG"),
            os.path.join(script_dir, "../../debug/images/test_image.png"),
            os.path.join(script_dir, "../../debug/images/sample.jpg"),
            os.path.join(script_dir, "../../debug/images/test.jpg")
        ]
        
        # Test statistics
        self.test_count = 0
        self.success_count = 0
        self.total_inference_time = 0.0
    
    def start_server(self) -> bool:
        """Start SmolVLM server if not already running."""
        if self.is_server_running():
            print("✅ SmolVLM server already running")
            return True
        
        cmd = [
            "llama-server",
            "-hf", self.model_name,
            "-ngl", "99",
            "--port", str(self.port)
        ]
        
        print("🚀 Starting SmolVLM server...")
        print(f"📦 Model: {self.model_name}")
        print(f"🌐 Port: {self.port}")
        print(f"💻 Command: {' '.join(cmd)}")
        print("-" * 50)
        
        try:
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Start a thread to monitor server output
            def monitor_output():
                if self.server_process and self.server_process.stdout:
                    for line in iter(self.server_process.stdout.readline, ''):
                        if "HTTP server listening" in line or "Server listening" in line:
                            print(f"✅ SmolVLM server running at http://localhost:{self.port}")
                            self.server_ready = True
                        elif "error" in line.lower():
                            print(f"❌ Server error: {line.rstrip()}")
            
            self.output_thread = threading.Thread(target=monitor_output)
            self.output_thread.daemon = True
            self.output_thread.start()
            
            # Wait for server to become ready
            start_time = time.time()
            while time.time() - start_time < 60:
                if self.server_ready or self.is_server_running():
                    return True
                if self.server_process.poll() is not None:
                    print("❌ SmolVLM server failed to start")
                    return False
                time.sleep(1)
                
            print("⏰ Timed out waiting for SmolVLM server to start")
            return False
            
        except FileNotFoundError:
            print("❌ Error: 'llama-server' command not found")
            print("Please ensure llama.cpp is properly installed and added to PATH")
            return False
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """Stop SmolVLM server."""
        if self.server_process:
            print("🔄 Stopping SmolVLM server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ SmolVLM server stopped")
                return True
            except subprocess.TimeoutExpired:
                print("⚠️ Force stopping server...")
                self.server_process.kill()
                self.server_process.wait()
                print("✅ SmolVLM server force stopped")
                return True
        return False
    
    def is_server_running(self) -> bool:
        """Check if server is running."""
        try:
            response = requests.get(self.health_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def image_to_base64(self, image_path: str, max_size: int = 512) -> str:
        """Convert image to base64 with optimization."""
        try:
            if not os.path.exists(image_path):
                print(f"⚠️ Image not found: {image_path}")
                return ""
            
            # Load and optimize image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"🔧 Resized image: {new_size}")
            
            # Convert to JPEG with optimization
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=90, optimize=True)
            image_data = buffer.getvalue()
            
            # Convert to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_data}"
            
        except Exception as e:
            print(f"❌ Error processing image {image_path}: {e}")
            return ""
    
    def send_request(self, prompt: str, image_base64: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """Send request to SmolVLM server."""
        if not image_base64:
            return {"error": "No image data provided", "success": False}
        
        request_data = {
            "model": "SmolVLM",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_base64}}
                    ]
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.server_url,
                headers=self.headers,
                json=request_data,
                timeout=self.timeout
            )
            inference_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return {
                        "success": True,
                        "response": content,
                        "inference_time": inference_time,
                        "tokens_used": result.get('usage', {}).get('total_tokens', 0)
                    }
                else:
                    return {"error": "Invalid response format", "success": False}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}", "success": False}
                
        except requests.exceptions.Timeout:
            return {"error": "Request timeout", "success": False}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}", "success": False}
    
    def test_server_connectivity(self) -> bool:
        """Test server connectivity and health."""
        print("\n🔍 Testing Server Connectivity")
        print("-" * 30)
        
        try:
            # Test health endpoint
            response = requests.get(self.health_url, timeout=10)
            if response.status_code == 200:
                print("✅ Health check passed")
                health_data = response.json()
                print(f"📊 Server status: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connectivity test failed: {e}")
            return False
    
    def test_image_analysis(self):
        """Test image analysis with various prompts."""
        print("\n🖼️ Testing Image Analysis")
        print("-" * 30)
        
        test_prompts = [
            "Describe what you see in this image",
            "What objects are visible in this image?",
            "What colors are prominent in this image?",
            "Is this image taken indoors or outdoors?"
        ]
        
        available_images = [path for path in self.image_paths if os.path.exists(path)]
        
        if not available_images:
            print("⚠️ No test images found")
            return
        
        for i, image_path in enumerate(available_images[:2]):  # Test first 2 images
            print(f"\n📸 Testing image {i+1}: {os.path.basename(image_path)}")
            
            image_base64 = self.image_to_base64(image_path)
            if not image_base64:
                continue
            
            for j, prompt in enumerate(test_prompts[:2]):  # Test first 2 prompts
                print(f"  🔍 Prompt {j+1}: {prompt}")
                
                result = self.send_request(prompt, image_base64)
                self.test_count += 1
                
                if result.get("success"):
                    self.success_count += 1
                    self.total_inference_time += result.get("inference_time", 0)
                    print(f"    ✅ Success ({result.get('inference_time', 0):.2f}s)")
                    print(f"    📝 Response: {result.get('response', '')[:100]}...")
                else:
                    print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
    
    def test_prompt_variations(self):
        """Test different prompt types and formats."""
        print("\n💬 Testing Prompt Variations")
        print("-" * 30)
        
        # Find first available image
        test_image = None
        for path in self.image_paths:
            if os.path.exists(path):
                test_image = self.image_to_base64(path)
                break
        
        if not test_image:
            print("⚠️ No test images available")
            return
        
        prompt_variations = [
            "What do you see?",
            "Describe the scene",
            "List the main objects",
            "What is happening in this image?",
            "Analyze the composition of this image"
        ]
        
        for i, prompt in enumerate(prompt_variations):
            print(f"🔍 Testing prompt {i+1}: {prompt}")
            
            result = self.send_request(prompt, test_image)
            self.test_count += 1
            
            if result.get("success"):
                self.success_count += 1
                self.total_inference_time += result.get("inference_time", 0)
                print(f"  ✅ Success ({result.get('inference_time', 0):.2f}s)")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
    
    def test_performance_analysis(self):
        """Test performance with different configurations."""
        print("\n⚡ Testing Performance Analysis")
        print("-" * 30)
        
        # Find first available image
        test_image = None
        for path in self.image_paths:
            if os.path.exists(path):
                test_image = self.image_to_base64(path)
                break
        
        if not test_image:
            print("⚠️ No test images available")
            return
        
        test_configs = [
            {"max_tokens": 100, "temperature": 0.7, "name": "Standard"},
            {"max_tokens": 200, "temperature": 0.7, "name": "Longer response"},
            {"max_tokens": 50, "temperature": 0.3, "name": "Short, focused"},
            {"max_tokens": 150, "temperature": 1.0, "name": "Creative"}
        ]
        
        prompt = "Describe what you see in this image"
        
        for config in test_configs:
            print(f"🔧 Testing {config['name']} configuration")
            
            result = self.send_request(
                prompt, 
                test_image, 
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            self.test_count += 1
            
            if result.get("success"):
                self.success_count += 1
                self.total_inference_time += result.get("inference_time", 0)
                print(f"  ✅ Success ({result.get('inference_time', 0):.2f}s)")
                print(f"  📊 Tokens used: {result.get('tokens_used', 0)}")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
    
    def show_test_summary(self):
        """Display test results summary."""
        print("\n📊 Test Results Summary")
        print("=" * 30)
        print(f"Total tests: {self.test_count}")
        print(f"Successful: {self.success_count}")
        print(f"Success rate: {(self.success_count/self.test_count*100):.1f}%" if self.test_count > 0 else "N/A")
        print(f"Average inference time: {(self.total_inference_time/self.success_count):.2f}s" if self.success_count > 0 else "N/A")
        print(f"Total inference time: {self.total_inference_time:.2f}s")
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite."""
        print("🎯 Running Comprehensive SmolVLM Test Suite")
        print("=" * 50)
        
        # Start server
        if not self.start_server():
            print("❌ Failed to start server")
            return
        
        try:
            # Run all tests
            self.test_server_connectivity()
            self.test_image_analysis()
            self.test_prompt_variations()
            self.test_performance_analysis()
            
            # Show summary
            self.show_test_summary()
            
        finally:
            # Stop server
            self.stop_server()
    
    def run_quick_test(self):
        """Run quick functionality test."""
        print("⚡ Running Quick SmolVLM Test")
        print("=" * 30)
        
        # Start server
        if not self.start_server():
            print("❌ Failed to start server")
            return
        
        try:
            # Basic connectivity test
            if not self.test_server_connectivity():
                print("❌ Server connectivity failed")
                return
            
            # Simple image test
            available_images = [path for path in self.image_paths if os.path.exists(path)]
            if available_images:
                print(f"\n📸 Testing with image: {os.path.basename(available_images[0])}")
                image_base64 = self.image_to_base64(available_images[0])
                if image_base64:
                    result = self.send_request("Describe this image", image_base64)
                    if result.get("success"):
                        print("✅ Quick test passed")
                        print(f"📝 Response: {result.get('response', '')[:100]}...")
                    else:
                        print(f"❌ Quick test failed: {result.get('error', 'Unknown error')}")
                else:
                    print("❌ Failed to process test image")
            else:
                print("⚠️ No test images available")
            
        finally:
            # Stop server
            self.stop_server()
    
    def debug_server(self):
        """Debug server status and configuration."""
        print("🔧 SmolVLM Server Debug Information")
        print("=" * 40)
        
        print(f"Model: {self.model_name}")
        print(f"Port: {self.port}")
        print(f"Server URL: {self.server_url}")
        print(f"Health URL: {self.health_url}")
        
        # Check if server is running
        if self.is_server_running():
            print("✅ Server is running")
            try:
                response = requests.get(self.health_url, timeout=5)
                print(f"Health check: HTTP {response.status_code}")
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"Server info: {json.dumps(health_data, indent=2)}")
            except Exception as e:
                print(f"Health check failed: {e}")
        else:
            print("❌ Server is not running")
        
        # Check test images
        print(f"\n📁 Test images:")
        for path in self.image_paths:
            if os.path.exists(path):
                print(f"  ✅ {os.path.basename(path)}")
            else:
                print(f"  ❌ {os.path.basename(path)} (not found)")

def main():
    """Main function with menu interface."""
    def signal_handler(signum, frame):
        print("\n🛑 Received stop signal, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    test_suite = SmolVLMTestSuite()
    
    print("🎯 SmolVLM Unified Test Suite")
    print("=" * 40)
    print("1. Comprehensive Test (All features)")
    print("2. Quick Test (Basic functionality)")
    print("3. Server Connectivity Test Only")
    print("4. Image Analysis Test Only")
    print("5. Prompt Variations Test Only")
    print("6. Performance Analysis Test Only")
    print("7. Debug Server Status")
    print("0. Exit")
    print("-" * 40)
    
    try:
        choice = input("Select test option (0-7): ").strip()
        
        if choice == "1":
            test_suite.run_comprehensive_test()
        elif choice == "2":
            test_suite.run_quick_test()
        elif choice == "3":
            if test_suite.start_server():
                test_suite.test_server_connectivity()
                test_suite.stop_server()
        elif choice == "4":
            if test_suite.start_server():
                test_suite.test_image_analysis()
                test_suite.stop_server()
        elif choice == "5":
            if test_suite.start_server():
                test_suite.test_prompt_variations()
                test_suite.stop_server()
        elif choice == "6":
            if test_suite.start_server():
                test_suite.test_performance_analysis()
                test_suite.stop_server()
        elif choice == "7":
            test_suite.debug_server()
        elif choice == "0":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main() 