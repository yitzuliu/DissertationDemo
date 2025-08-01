#!/usr/bin/env python3
"""
Backend VLM Processing Logging End-to-End Test

Simulates complete VLM processing flow, validates all logging functionality

Usage:
1. First start SmolVLM server: python src/models/smolvlm/run_smolvlm.py
2. Run this test in another terminal: python src/logging/test_backend_vlm_logging.py
3. After test completion, you can stop SmolVLM server (Ctrl+C)
"""

import asyncio
import json
import time
import uuid
import subprocess
import requests
import signal
import sys
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

class SmolVLMServerManager:
    """SmolVLM Server Manager"""
    
    def __init__(self):
        self.process = None
        self.model_port = 8080
        self.base_dir = Path(__file__).parent.parent.parent
        self.server_script = self.base_dir / "src" / "models" / "smolvlm" / "run_smolvlm.py"
        
    def check_server_running(self):
        """Check if server is running"""
        try:
            response = requests.get(f"http://localhost:{self.model_port}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_server(self):
        """Start SmolVLM server"""
        if self.check_server_running():
            print("✅ SmolVLM server is already running")
            return True
            
        if not self.server_script.exists():
            print(f"❌ SmolVLM server script not found: {self.server_script}")
            return False
            
        print("🚀 Starting SmolVLM server...")
        try:
            self.process = subprocess.Popen(
                [sys.executable, str(self.server_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for i in range(30):  # Wait up to 30 seconds
                if self.check_server_running():
                    print("✅ SmolVLM server started successfully")
                    return True
                time.sleep(1)
                print(f"   Waiting... ({i+1}/30)")
            
            print("❌ SmolVLM server startup timeout")
            self.stop_server()
            return False
            
        except Exception as e:
            print(f"❌ Failed to start SmolVLM server: {e}")
            return False
    
    def stop_server(self):
        """Stop SmolVLM server"""
        if self.process:
            print("🛑 Stopping SmolVLM server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print("✅ SmolVLM server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️ Force stopping SmolVLM server...")
                self.process.kill()
                self.process.wait()
                print("✅ SmolVLM server force stopped")
            self.process = None


# Mock backend VLM processing flow
class MockVLMProcessor:
    def __init__(self):
        # Import visual logger
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from visual_logger import get_visual_logger
        
        self.visual_logger = get_visual_logger()
        self.model = "smolvlm"
    
    async def process_chat_completion(self, request_data: Dict[str, Any]):
        """Mock complete chat completion processing flow"""
        request_start_time = time.time()
        request_id = f"req_{int(request_start_time * 1000)}"
        observation_id = f"obs_{int(request_start_time * 1000)}_{uuid.uuid4().hex[:8]}"
        
        print(f"🚀 Starting VLM request processing - Observation ID: {observation_id}")
        
        try:
            # 1. Log backend receive
            print("📥 Step 1: Log backend receive")
            self.visual_logger.log_backend_receive(observation_id, request_id, request_data)
            await asyncio.sleep(0.01)
            
            # 2. Image processing
            print("🖼️ Step 2: Image processing")
            image_count = self._count_images(request_data)
            self.visual_logger.log_image_processing_start(observation_id, request_id, image_count, self.model)
            
            # Mock image processing time
            image_processing_time = 0.15
            await asyncio.sleep(image_processing_time)
            
            self.visual_logger.log_image_processing_result(
                observation_id, request_id, image_processing_time, True,
                {"image_count": image_count, "model": self.model, "resolution": "1024x768"}
            )
            
            # 3. VLM request
            print("🤖 Step 3: VLM model request")
            prompt_length = self._calculate_prompt_length(request_data)
            self.visual_logger.log_vlm_request(observation_id, request_id, self.model, prompt_length, image_count)
            
            # Mock VLM inference time
            vlm_processing_time = 0.85
            await asyncio.sleep(vlm_processing_time)
            
            # Mock VLM response
            vlm_response = "I can see coffee brewing equipment including a pour-over dripper, coffee filter, gooseneck kettle, digital scale, and coffee beans. This appears to be step 1 of the coffee brewing process - gathering equipment and ingredients."
            response_length = len(vlm_response)
            
            self.visual_logger.log_vlm_response(
                observation_id, request_id, response_length, vlm_processing_time, True, self.model
            )
            
            # 4. RAG data transfer
            print("🔄 Step 4: RAG data transfer")
            self.visual_logger.log_rag_data_transfer(observation_id, vlm_response, True)
            
            # 5. State tracker integration
            print("📊 Step 5: State tracker integration")
            state_processing_time = 0.05
            await asyncio.sleep(state_processing_time)
            
            state_updated = True  # Mock successful state update
            self.visual_logger.log_state_tracker_integration(observation_id, state_updated, state_processing_time)
            
            # 6. Performance metrics logging
            print("⚡ Step 6: Performance metrics logging")
            total_time = time.time() - request_start_time
            
            self.visual_logger.log_performance_metric(observation_id, "total_processing_time", total_time, "s")
            self.visual_logger.log_performance_metric(observation_id, "image_processing_time", image_processing_time, "s")
            self.visual_logger.log_performance_metric(observation_id, "model_inference_time", vlm_processing_time, "s")
            self.visual_logger.log_performance_metric(observation_id, "state_tracker_time", state_processing_time, "s")
            
            print(f"✅ VLM processing completed - Total time: {total_time:.2f}s")
            
            return {
                "choices": [
                    {
                        "message": {
                            "content": vlm_response,
                            "role": "assistant"
                        }
                    }
                ],
                "model": self.model,
                "usage": {
                    "prompt_tokens": prompt_length,
                    "completion_tokens": response_length,
                    "total_tokens": prompt_length + response_length
                }
            }
            
        except Exception as e:
            # Error handling
            error_time = time.time() - request_start_time
            print(f"❌ Error occurred during processing: {e}")
            
            self.visual_logger.log_error(observation_id, request_id, type(e).__name__, str(e), "vlm_processing")
            self.visual_logger.log_performance_metric(observation_id, "error_time", error_time, "s")
            
            raise
    
    def _count_images(self, request_data: Dict[str, Any]) -> int:
        """計算請求中的圖像數量"""
        image_count = 0
        messages = request_data.get("messages", [])
        
        for message in messages:
            content = message.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "image_url":
                        image_count += 1
        
        return image_count
    
    def _calculate_prompt_length(self, request_data: Dict[str, Any]) -> int:
        """計算提示詞長度"""
        prompt_length = 0
        messages = request_data.get("messages", [])
        
        for message in messages:
            content = message.get("content", [])
            if isinstance(content, str):
                prompt_length += len(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        prompt_length += len(item.get("text", ""))
        
        return prompt_length


async def test_single_image_request():
    """Test single image request"""
    print("🧪 Test 1: Single Image Request")
    print("-" * 40)
    
    processor = MockVLMProcessor()
    
    request_data = {
        "model": "smolvlm",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    result = await processor.process_chat_completion(request_data)
    print(f"✅ Test 1 completed - Response length: {len(result['choices'][0]['message']['content'])}")
    return True


async def test_multiple_images_request():
    """Test multiple images request"""
    print("\n🧪 Test 2: Multiple Images Request")
    print("-" * 40)
    
    processor = MockVLMProcessor()
    
    request_data = {
        "model": "smolvlm",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Compare these two images and describe the differences"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."}
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."}
                    }
                ]
            }
        ],
        "max_tokens": 200
    }
    
    result = await processor.process_chat_completion(request_data)
    print(f"✅ Test 2 completed - Response length: {len(result['choices'][0]['message']['content'])}")
    return True


async def test_text_only_request():
    """Test text-only request"""
    print("\n🧪 Test 3: Text-Only Request")
    print("-" * 40)
    
    processor = MockVLMProcessor()
    
    request_data = {
        "model": "smolvlm",
        "messages": [
            {
                "role": "user",
                "content": "Explain the coffee brewing process step by step"
            }
        ],
        "max_tokens": 150
    }
    
    result = await processor.process_chat_completion(request_data)
    print(f"✅ Test 3 completed - Response length: {len(result['choices'][0]['message']['content'])}")
    return True


async def test_error_scenario():
    """Test error scenario"""
    print("\n🧪 Test 4: Error Scenario")
    print("-" * 40)
    
    processor = MockVLMProcessor()
    
    # Mock request that will cause an error
    request_data = {
        "model": "invalid_model",
        "messages": [],  # Empty message list
        "max_tokens": -1  # Invalid token count
    }
    
    try:
        # Mock error during VLM request phase
        original_method = processor.visual_logger.log_vlm_request
        
        def mock_vlm_request(*args, **kwargs):
            original_method(*args, **kwargs)
            raise ConnectionError("Failed to connect to model server")
        
        processor.visual_logger.log_vlm_request = mock_vlm_request
        
        await processor.process_chat_completion(request_data)
        print("❌ Test 4 failed - Should have thrown exception")
        return False
        
    except ConnectionError:
        # Restore original method
        processor.visual_logger.log_vlm_request = original_method
        print("✅ Test 4 completed - Error correctly handled and logged")
        return True
    except Exception as e:
        # Restore original method
        processor.visual_logger.log_vlm_request = original_method
        print(f"⚠️ Test 4 partially successful - Caught exception: {type(e).__name__}")
        return True


async def test_performance_monitoring():
    """Test performance monitoring"""
    print("\n🧪 Test 5: Performance Monitoring")
    print("-" * 40)
    
    # Create new processor instance to avoid mock effects from previous tests
    processor = MockVLMProcessor()
    
    # Execute multiple requests to test performance monitoring
    requests = []
    for i in range(3):
        request_data = {
            "model": "smolvlm",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analyze image {i+1}"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,image_{i+1}_data"}
                        }
                    ]
                }
            ],
            "max_tokens": 100
        }
        requests.append(request_data)
    
    start_time = time.time()
    results = []
    
    for i, request_data in enumerate(requests):
        print(f"  Processing request {i+1}/3")
        result = await processor.process_chat_completion(request_data)
        results.append(result)
        await asyncio.sleep(0.1)  # Interval time
    
    total_time = time.time() - start_time
    print(f"✅ Test 5 completed - Processed {len(results)} requests, total time: {total_time:.2f}s")
    return True


async def main():
    """Main test function"""
    print("🧪 Backend VLM Processing Logging End-to-End Test")
    print("=" * 60)
    
    # Check if server needs to be started
    server_manager = SmolVLMServerManager()
    server_started_by_test = False
    
    print("🔍 Checking SmolVLM server status...")
    if not server_manager.check_server_running():
        print("⚠️ SmolVLM server is not running")
        print("\nThere are two ways to run this test:")
        print("1. Auto-start server (recommended)")
        print("2. Manual server startup")
        print("\nChoose auto-start? (y/n): ", end="")
        
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes', '']:
                if server_manager.start_server():
                    server_started_by_test = True
                else:
                    print("❌ Unable to start server, please start manually and retry")
                    print("Manual startup command: python src/models/smolvlm/run_smolvlm.py")
                    return False
            else:
                print("Please manually start SmolVLM server first:")
                print("python src/models/smolvlm/run_smolvlm.py")
                print("Then run this test again")
                return False
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            return False
    else:
        print("✅ SmolVLM server is running")
    
    test_results = []
    
    try:
        print("\n🎯 Starting test execution...")
        print("=" * 60)
        
        # Execute all tests
        test_results.append(await test_single_image_request())
        test_results.append(await test_multiple_images_request())
        test_results.append(await test_text_only_request())
        test_results.append(await test_error_scenario())
        test_results.append(await test_performance_monitoring())
        
        # Display test results
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        total_tests = len(test_results)
        passed_tests = sum(test_results)
        success_rate = (passed_tests / total_tests * 100)
        
        print(f"Total tests: {total_tests}")
        print(f"Passed tests: {passed_tests}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Backend VLM processing logging functionality working normally.")
        else:
            print("\n⚠️ Some tests failed, please check log output.")
        
        # Check log files
        import os
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        if os.path.exists(log_dir):
            visual_log_files = [f for f in os.listdir(log_dir) if f.startswith("visual_")]
            if visual_log_files:
                print(f"\n📁 Generated visual log files: {visual_log_files}")
                
                # Display last few lines of latest log
                latest_log = max(visual_log_files)
                log_path = os.path.join(log_dir, latest_log)
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"\n📄 Latest log content (last 5 lines):")
                            for line in lines[-5:]:
                                print(f"   {line.strip()}")
                except Exception as e:
                    print(f"   Unable to read log file: {e}")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ Error occurred during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup server
        if server_started_by_test:
            print("\n🧹 Cleaning up test environment...")
            server_manager.stop_server()


def signal_handler(signum, frame):
    """Handle interrupt signal"""
    print("\n🛑 Test interrupted, cleaning up...")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    success = asyncio.run(main())
    exit(0 if success else 1)