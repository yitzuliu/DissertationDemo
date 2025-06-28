#!/usr/bin/env python3
"""
Unified SmolVLM Testing Suite - Server-based Architecture

Simplified testing script for SmolVLM model using llama-server.
Focuses on core functionality testing with clean server management.

Environment: llama-server with OpenAI API compatibility
Model: SmolVLM-500M-Instruct-GGUF
"""

import time
import requests
import base64
import os
import subprocess
import threading
import signal
import sys
from PIL import Image
from typing import Dict, Any
import io

# Configuration
MODEL_NAME = "ggml-org/SmolVLM-500M-Instruct-GGUF"
PORT = 8080
SERVER_URL = f"http://localhost:{PORT}/v1/chat/completions"
HEALTH_URL = f"http://localhost:{PORT}/health"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 60

# Get test image paths
script_dir = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATHS = [
    os.path.join(script_dir, "../../debug/images/IMG_0119.JPG"),
    os.path.join(script_dir, "../../debug/images/test_image.png"),
    os.path.join(script_dir, "../../debug/images/sample.jpg"),
    os.path.join(script_dir, "../../debug/images/test.jpg")
]

# Global server process
server_process = None
server_ready = False

def start_server() -> bool:
    """Start SmolVLM server if not already running."""
    global server_process, server_ready
    
    if is_server_running():
        print("✅ SmolVLM server already running")
        return True
    
    cmd = [
        "llama-server",
        "-hf", MODEL_NAME,
        "-ngl", "99",
        "--port", str(PORT)
    ]
    
    print("🚀 Starting SmolVLM server...")
    print(f"📦 Model: {MODEL_NAME}")
    print(f"🌐 Port: {PORT}")
    print("-" * 50)
    
    try:
        server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor server output
        def monitor_output():
            global server_ready
            if server_process and server_process.stdout:
                for line in iter(server_process.stdout.readline, ''):
                    if "HTTP server listening" in line or "Server listening" in line:
                        print(f"✅ SmolVLM server running at http://localhost:{PORT}")
                        server_ready = True
                    elif "error" in line.lower():
                        print(f"❌ Server error: {line.rstrip()}")
        
        output_thread = threading.Thread(target=monitor_output)
        output_thread.daemon = True
        output_thread.start()
        
        # Wait for server to become ready
        start_time = time.time()
        while time.time() - start_time < 60:
            if server_ready or is_server_running():
                return True
            if server_process.poll() is not None:
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

def stop_server() -> bool:
    """Stop SmolVLM server."""
    global server_process, server_ready
    
    if not server_process:
        return True
        
    print("🛑 Stopping SmolVLM server...")
    try:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
            print("✅ SmolVLM server stopped")
        except subprocess.TimeoutExpired:
            print("⚠️ Force stopping server...")
            server_process.kill()
            server_process.wait()
            print("✅ SmolVLM server force stopped")
        return True
    except Exception as e:
        print(f"❌ Error stopping SmolVLM server: {str(e)}")
        return False
    finally:
        server_process = None
        server_ready = False

def is_server_running() -> bool:
    """Check if server is running."""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def image_to_base64(image_path: str, max_size: int = 512) -> str:
    """Convert image to base64 string with size optimization."""
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

def send_request(prompt: str, image_base64: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
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
            SERVER_URL,
            headers=HEADERS,
            json=payload,
            timeout=TIMEOUT
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

def test_image_analysis():
    """Test image analysis capabilities."""
    print("🖼️ IMAGE ANALYSIS TEST")
    print("-" * 40)
    
    available_images = [path for path in IMAGE_PATHS if os.path.exists(path)]
    
    if not available_images:
        print("❌ No test images found")
        return
    
    for i, img_path in enumerate(available_images[:2], 1):
        print(f"\n📸 Image {i}: {os.path.basename(img_path)}")
        
        try:
            # Get image info
            with Image.open(img_path) as img:
                original_size = img.size
            file_size = os.path.getsize(img_path) / 1024
            print(f"📊 Size: {original_size}, {file_size:.1f}KB")
            
            # Convert to base64
            image_base64 = image_to_base64(img_path)
            
            # Test with prompt
            result = send_request(
                "Describe what you see in this image in detail.",
                image_base64
            )
            
            if result["success"]:
                print(f"⚡ Time: {result['inference_time']:.2f}s")
                print(f"🤖 Response: {result['response']}")
                
                if "usage" in result:
                    usage = result["usage"]
                    print(f"📊 Tokens - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                          f"Completion: {usage.get('completion_tokens', 'N/A')}")
            else:
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_prompt_variations():
    """Test different prompt types."""
    print("📝 PROMPT VARIATION TEST")
    print("-" * 40)
    
    # Find first available image
    test_image = None
    for img_path in IMAGE_PATHS:
        if os.path.exists(img_path):
            test_image = img_path
            break
    
    if not test_image:
        print("❌ No test image found")
        return
    
    print(f"📸 Using: {os.path.basename(test_image)}")
    image_base64 = image_to_base64(test_image)
    
    prompts = [
        "What objects can you see in this image?",
        "Describe the colors and mood of this image.",
        "Is there any text visible in this image?"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n🔍 Test {i}: {prompt}")
        
        result = send_request(prompt, image_base64, max_tokens=150)
        
        if result["success"]:
            print(f"⚡ Time: {result['inference_time']:.2f}s")
            print(f"🤖 Response: {result['response']}")
        else:
            print(f"❌ Error: {result['error']}")

def show_memory_usage():
    """Show server status."""
    if is_server_running():
        print("📊 Server Status: Running")
    else:
        print("📊 Server Status: Stopped")

def run_comprehensive_test():
    """Run all test categories."""
    if not start_server():
        print("❌ Failed to start server")
        return
    
    try:
        print("🧪 COMPREHENSIVE TEST SUITE")
        print("=" * 50)
        
        # Test 1: Images
        test_image_analysis()
        show_memory_usage()
        
        print("\n" + "="*50)
        
        # Test 2: Prompt variations
        test_prompt_variations()
        show_memory_usage()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS COMPLETE")
        
    finally:
        stop_server()

def run_quick_test():
    """Run quick representative test."""
    if not start_server():
        print("❌ Failed to start server")
        return
    
    try:
        print("⚡ QUICK TEST")
        print("=" * 30)
        
        # Quick image test
        available_images = [path for path in IMAGE_PATHS if os.path.exists(path)]
        if available_images:
            print(f"📸 Testing with: {os.path.basename(available_images[0])}")
            image_base64 = image_to_base64(available_images[0])
            
            result = send_request(
                "Describe this image briefly.",
                image_base64,
                max_tokens=100
            )
            
            if result["success"]:
                print(f"⚡ Time: {result['inference_time']:.2f}s")
                print(f"🤖 Response: {result['response']}")
            else:
                print(f"❌ Error: {result['error']}")
        else:
            print("❌ No test images found")
        
        print("\n" + "="*30)
        print("✅ QUICK TEST COMPLETE")
        show_memory_usage()
        
    finally:
        stop_server()

def debug_server():
    """Debug server connectivity."""
    print("🔍 SERVER DEBUG")
    print("=" * 30)
    
    print(f"Model: {MODEL_NAME}")
    print(f"Port: {PORT}")
    print(f"Health URL: {HEALTH_URL}")
    print(f"API URL: {SERVER_URL}")
    
    if is_server_running():
        print("✅ Server is running")
    else:
        print("❌ Server is not running")
        print("Try starting with option 1 or 2")

def main():
    """Main interface."""
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\n🛑 Received stop signal...")
        stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("🎯 SmolVLM Unified Testing Suite")
        print("🔧 Server-based Architecture")
        print("=" * 50)
        print()
        print("Test Options:")
        print("1. Comprehensive Test (all categories)")
        print("2. Quick Test (basic functionality)")
        print("3. Image Analysis Only")
        print("4. Prompt Variations Only")
        print("5. Debug Server Status")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "1":
            run_comprehensive_test()
        elif choice == "2":
            run_quick_test()
        elif choice == "3":
            if start_server():
                test_image_analysis()
                show_memory_usage()
                stop_server()
        elif choice == "4":
            if start_server():
                test_prompt_variations()
                show_memory_usage()
                stop_server()
        elif choice == "5":
            debug_server()
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        stop_server()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        stop_server()
    finally:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 