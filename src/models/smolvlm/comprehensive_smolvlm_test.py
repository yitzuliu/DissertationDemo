#!/usr/bin/env python3
"""
Comprehensive SmolVLM Testing Suite

Combined testing script for SmolVLM model with server management and optimization.
Includes image analysis, multi-modal testing capabilities, and server monitoring.

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
    """Comprehensive testing suite for SmolVLM model."""
    
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
            while time.time() - start_time < 60:  # Wait up to 60 seconds
                if self.server_ready or self.is_server_running():
                    print("🎯 Server ready for testing")
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
            print(f"❌ Error starting SmolVLM server: {str(e)}")
            return False
    
    def stop_server(self) -> bool:
        """Stop SmolVLM server."""
        if not self.server_process:
            return True
            
        print("🛑 Stopping SmolVLM server...")
        try:
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
        except Exception as e:
            print(f"❌ Error stopping SmolVLM server: {str(e)}")
            return False
        finally:
            self.server_process = None
            self.server_ready = False
    
    def is_server_running(self) -> bool:
        """Check if server is running."""
        try:
            response = requests.get(self.health_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def image_to_base64(self, image_path: str, max_size: int = 512) -> str:
        """Convert image to base64 string with size optimization."""
        try:
            with Image.open(image_path) as img:
                # Resize if too large
                if max(img.size) > max_size:
                    scale = max_size / max(img.size)
                    new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"🔄 Resized image to {new_size}")
                
                # Convert to JPEG bytes
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=90)
                image_bytes = buffer.getvalue()
                
                # Encode to base64
                return base64.b64encode(image_bytes).decode('utf-8')
                
        except Exception as e:
            print(f"❌ Error processing image {image_path}: {e}")
            raise e
    
    def send_request(self, prompt: str, image_base64: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """Send request to SmolVLM server."""
        payload = {
            "model": "SmolVLM",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.server_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            inference_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API Error {response.status_code}",
                    "details": response.text,
                    "inference_time": inference_time
                }
            
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "response": content,
                "inference_time": inference_time,
                "usage": response_json.get("usage", {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "Request failed",
                "details": str(e),
                "inference_time": time.time() - start_time
            }
    
    def test_server_connectivity(self) -> bool:
        """Test server connectivity and basic functionality."""
        print("🔗 SERVER CONNECTIVITY TESTING")
        print("-" * 40)
        
        # Test health endpoint
        try:
            response = requests.get(self.health_url, timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint accessible")
            else:
                print(f"❌ Health endpoint returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return False
        
        # Test basic API endpoint
        try:
            test_payload = {
                "model": "SmolVLM",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.server_url,
                headers=self.headers,
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ API endpoint accessible")
                return True
            else:
                print(f"❌ API endpoint returned {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API endpoint error: {e}")
            return False
    
    def test_image_analysis(self):
        """Test SmolVLM with image analysis."""
        print("🖼️ IMAGE ANALYSIS TESTING")
        print("-" * 40)
        
        # Find available test images
        available_images = []
        for img_path in self.image_paths:
            if os.path.exists(img_path):
                available_images.append(img_path)
        
        if not available_images:
            print("❌ No test images found")
            return
        
        test_prompts = [
            "Describe what you see in this image in detail.",
            "What objects are visible in this image?",
            "What colors and textures can you identify?",
            "Is there any text visible in this image?",
            "What is the overall scene or setting?"
        ]
        
        for i, img_path in enumerate(available_images[:2], 1):  # Test first 2 images
            print(f"\n📸 Image Test {i}: {os.path.basename(img_path)}")
            
            try:
                # Get image info
                with Image.open(img_path) as img:
                    original_size = img.size
                file_size = os.path.getsize(img_path) / 1024  # KB
                print(f"📊 Original size: {original_size}, {file_size:.1f}KB")
                
                # Convert to base64
                image_base64 = self.image_to_base64(img_path)
                
                # Test with different prompts
                for j, prompt in enumerate(test_prompts[:2], 1):  # Test first 2 prompts
                    print(f"\n🔍 Prompt {j}: {prompt}")
                    
                    result = self.send_request(prompt, image_base64)
                    
                    self.test_count += 1
                    if result["success"]:
                        self.success_count += 1
                        self.total_inference_time += result["inference_time"]
                        
                        print(f"⚡ Inference time: {result['inference_time']:.2f}s")
                        print(f"🤖 Response: {result['response'][:200]}...")
                        
                        if "usage" in result:
                            usage = result["usage"]
                            print(f"📊 Tokens - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                                  f"Completion: {usage.get('completion_tokens', 'N/A')}")
                    else:
                        print(f"❌ Error: {result['error']}")
                        if "details" in result:
                            print(f"📝 Details: {result['details']}")
                
            except Exception as e:
                print(f"❌ Error processing image {i}: {e}")
    
    def test_prompt_variations(self):
        """Test different types of prompts."""
        print("📝 PROMPT VARIATION TESTING")
        print("-" * 40)
        
        # Find first available image
        test_image = None
        for img_path in self.image_paths:
            if os.path.exists(img_path):
                test_image = img_path
                break
        
        if not test_image:
            print("❌ No test image found")
            return
        
        print(f"📸 Using image: {os.path.basename(test_image)}")
        
        # Convert to base64
        image_base64 = self.image_to_base64(test_image)
        
        # Different prompt types
        prompt_tests = [
            {
                "name": "Detailed Description",
                "prompt": "Provide a detailed description of this image, including objects, people, colors, and setting.",
                "max_tokens": 300
            },
            {
                "name": "Object Detection",
                "prompt": "List all the objects you can identify in this image.",
                "max_tokens": 150
            },
            {
                "name": "Scene Analysis",
                "prompt": "What type of scene is this? Indoor or outdoor? What's the mood or atmosphere?",
                "max_tokens": 100
            },
            {
                "name": "Text Recognition",
                "prompt": "Is there any text visible in this image? If so, what does it say?",
                "max_tokens": 100
            },
            {
                "name": "Creative Interpretation",
                "prompt": "Tell me a short story inspired by this image.",
                "max_tokens": 200
            }
        ]
        
        for i, test in enumerate(prompt_tests, 1):
            print(f"\n🔍 Test {i}: {test['name']}")
            print(f"📝 Prompt: {test['prompt']}")
            
            result = self.send_request(
                test['prompt'], 
                image_base64, 
                max_tokens=test['max_tokens']
            )
            
            self.test_count += 1
            if result["success"]:
                self.success_count += 1
                self.total_inference_time += result["inference_time"]
                
                print(f"⚡ Inference time: {result['inference_time']:.2f}s")
                print(f"🤖 Response: {result['response']}")
                
                if "usage" in result:
                    usage = result["usage"]
                    print(f"📊 Tokens - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                          f"Completion: {usage.get('completion_tokens', 'N/A')}")
            else:
                print(f"❌ Error: {result['error']}")
    
    def test_performance_analysis(self):
        """Test performance with different configurations."""
        print("⚡ PERFORMANCE ANALYSIS TESTING")
        print("-" * 40)
        
        # Find first available image
        test_image = None
        for img_path in self.image_paths:
            if os.path.exists(img_path):
                test_image = img_path
                break
        
        if not test_image:
            print("❌ No test image found")
            return
        
        print(f"📸 Using image: {os.path.basename(test_image)}")
        image_base64 = self.image_to_base64(test_image)
        
        # Test different configurations
        configs = [
            {"name": "Conservative", "max_tokens": 50, "temperature": 0.1},
            {"name": "Balanced", "max_tokens": 150, "temperature": 0.7},
            {"name": "Creative", "max_tokens": 300, "temperature": 0.9},
        ]
        
        prompt = "Describe this image in detail."
        
        for config in configs:
            print(f"\n🔧 Testing {config['name']} configuration")
            print(f"📊 Max tokens: {config['max_tokens']}, Temperature: {config['temperature']}")
            
            # Run multiple times for average
            times = []
            for run in range(3):
                result = self.send_request(
                    prompt, 
                    image_base64, 
                    max_tokens=config['max_tokens'],
                    temperature=config['temperature']
                )
                
                if result["success"]:
                    times.append(result["inference_time"])
                    if run == 0:  # Show response for first run
                        print(f"🤖 Response: {result['response'][:100]}...")
                else:
                    print(f"❌ Run {run+1} failed: {result['error']}")
            
            if times:
                avg_time = sum(times) / len(times)
                print(f"⚡ Average inference time: {avg_time:.2f}s (over {len(times)} runs)")
    
    def show_test_summary(self):
        """Display test summary statistics."""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        if self.test_count > 0:
            success_rate = (self.success_count / self.test_count) * 100
            avg_time = self.total_inference_time / self.success_count if self.success_count > 0 else 0
            
            print(f"📈 Total tests: {self.test_count}")
            print(f"✅ Successful: {self.success_count}")
            print(f"❌ Failed: {self.test_count - self.success_count}")
            print(f"📊 Success rate: {success_rate:.1f}%")
            print(f"⚡ Average inference time: {avg_time:.2f}s")
            print(f"🕒 Total inference time: {self.total_inference_time:.2f}s")
        else:
            print("❌ No tests were completed")
    
    def run_comprehensive_test(self):
        """Run all test categories."""
        print("🧪 COMPREHENSIVE SMOLVLM TESTING SUITE")
        print("=" * 60)
        print(f"🤖 Model: {self.model_name}")
        print(f"🌐 Server URL: {self.server_url}")
        print()
        
        # Start server if needed
        if not self.start_server():
            print("❌ Failed to start server, aborting tests")
            return
        
        try:
            # Test 1: Server Connectivity
            if not self.test_server_connectivity():
                print("❌ Server connectivity failed, aborting tests")
                return
            
            print("\n" + "="*60)
            
            # Test 2: Image Analysis
            self.test_image_analysis()
            
            print("\n" + "="*60)
            
            # Test 3: Prompt Variations
            self.test_prompt_variations()
            
            print("\n" + "="*60)
            
            # Test 4: Performance Analysis
            self.test_performance_analysis()
            
            # Show summary
            self.show_test_summary()
            
        finally:
            # Always try to stop server
            self.stop_server()
    
    def run_quick_test(self):
        """Run a quick test with basic functionality."""
        print("⚡ QUICK SMOLVLM TEST")
        print("=" * 40)
        
        # Start server if needed
        if not self.start_server():
            print("❌ Failed to start server")
            return
        
        try:
            # Quick connectivity test
            if not self.test_server_connectivity():
                print("❌ Server connectivity failed")
                return
            
            # Quick image test
            available_images = [path for path in self.image_paths if os.path.exists(path)]
            if available_images:
                print(f"\n📸 Testing with: {os.path.basename(available_images[0])}")
                image_base64 = self.image_to_base64(available_images[0])
                
                result = self.send_request(
                    "Describe this image briefly.", 
                    image_base64, 
                    max_tokens=100
                )
                
                if result["success"]:
                    print(f"⚡ Inference time: {result['inference_time']:.2f}s")
                    print(f"🤖 Response: {result['response']}")
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print("❌ No test images found")
            
        finally:
            self.stop_server()


def main():
    """Main testing interface."""
    test_suite = SmolVLMTestSuite()
    
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\n🛑 Received stop signal...")
        test_suite.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("🎯 SmolVLM Testing Suite")
        print("=" * 50)
        print("🔧 Server-based architecture with llama-server")
        print()
        print("Testing Options:")
        print("1. Comprehensive Test (all categories)")
        print("2. Quick Test (basic functionality)")
        print("3. Image Analysis Only")
        print("4. Prompt Variations Only")
        print("5. Performance Analysis Only")
        print("6. Server Connectivity Test Only")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            test_suite.run_comprehensive_test()
        elif choice == "2":
            test_suite.run_quick_test()
        elif choice == "3":
            if test_suite.start_server():
                test_suite.test_image_analysis()
                test_suite.show_test_summary()
                test_suite.stop_server()
        elif choice == "4":
            if test_suite.start_server():
                test_suite.test_prompt_variations()
                test_suite.show_test_summary()
                test_suite.stop_server()
        elif choice == "5":
            if test_suite.start_server():
                test_suite.test_performance_analysis()
                test_suite.show_test_summary()
                test_suite.stop_server()
        elif choice == "6":
            if test_suite.start_server():
                test_suite.test_server_connectivity()
                test_suite.stop_server()
        else:
            print("❌ Invalid choice. Please run the script again.")
    
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        test_suite.stop_server()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        test_suite.stop_server()
    finally:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main() 