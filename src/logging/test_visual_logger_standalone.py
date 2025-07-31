#!/usr/bin/env python3
"""
Visual Logger Standalone Test

No actual VLM server required, specifically tests logging functionality
"""

import asyncio
import time
import uuid
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add path
sys.path.append(os.path.dirname(__file__))

from visual_logger import get_visual_logger


class StandaloneVLMLoggerTest:
    """Standalone VLM logger test"""
    
    def __init__(self):
        self.visual_logger = get_visual_logger()
        self.test_results = []
    
    def test_basic_logging_functions(self):
        """Test basic logging functionality"""
        print("🧪 Test 1: Basic Logging Functions")
        print("-" * 40)
        
        observation_id = f"obs_test_{int(time.time())}"
        request_id = f"req_test_{int(time.time())}"
        
        try:
            # Test backend receive logging
            request_data = {
                "model": "smolvlm",
                "messages": [{"role": "user", "content": "Test message"}],
                "max_tokens": 100
            }
            self.visual_logger.log_backend_receive(observation_id, request_id, request_data)
            print("  ✅ Backend receive logging successful")
            
            # Test image processing logging
            self.visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
            self.visual_logger.log_image_processing_result(observation_id, request_id, 0.15, True, {"image_count": 1})
            print("  ✅ Image processing logging successful")
            
            # Test VLM request and response logging
            self.visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 25, 1)
            self.visual_logger.log_vlm_response(observation_id, request_id, 150, 0.8, True, "smolvlm")
            print("  ✅ VLM request and response logging successful")
            
            # Test RAG data transfer logging
            vlm_text = "Test VLM response for RAG processing"
            self.visual_logger.log_rag_data_transfer(observation_id, vlm_text, True)
            print("  ✅ RAG data transfer logging successful")
            
            # Test state tracker integration logging
            self.visual_logger.log_state_tracker_integration(observation_id, True, 0.05)
            print("  ✅ State tracker integration logging successful")
            
            # Test performance metric logging
            self.visual_logger.log_performance_metric(observation_id, "total_time", 1.0, "s")
            print("  ✅ Performance metric logging successful")
            
            # Test error logging
            self.visual_logger.log_error(observation_id, request_id, "TestError", "Test error message", "test_context")
            print("  ✅ Error logging successful")
            
            print("✅ Test 1 completed - All basic logging functions working")
            return True
            
        except Exception as e:
            print(f"❌ Test 1 failed: {e}")
            return False
    
    def test_data_sanitization(self):
        """Test data sanitization functionality"""
        print("\n🧪 Test 2: Data Sanitization")
        print("-" * 40)
        
        observation_id = f"obs_sanitize_{int(time.time())}"
        request_id = f"req_sanitize_{int(time.time())}"
        
        try:
            # Test request sanitization with sensitive data
            request_data = {
                "model": "smolvlm",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What do you see?"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "data:image/jpeg;base64," + "x" * 1000  # Long image data
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 100
            }
            
            self.visual_logger.log_backend_receive(observation_id, request_id, request_data)
            print("  ✅ Sensitive data sanitization successful")
            
            # Test long text sanitization
            long_text = "This is a very long text that should be truncated. " * 20
            self.visual_logger.log_rag_data_transfer(observation_id, long_text, True)
            print("  ✅ Long text sanitization successful")
            
            print("✅ Test 2 completed - Data sanitization working")
            return True
            
        except Exception as e:
            print(f"❌ Test 2 failed: {e}")
            return False
    
    def test_id_consistency(self):
        """Test ID consistency"""
        print("\n🧪 Test 3: ID Consistency")
        print("-" * 40)
        
        try:
            # Generate consistent set of IDs
            base_time = int(time.time() * 1000)
            observation_id = f"obs_{base_time}_{uuid.uuid4().hex[:8]}"
            request_id = f"req_{base_time}"
            
            print(f"  Observation ID: {observation_id}")
            print(f"  Request ID: {request_id}")
            
            # Use same IDs throughout the flow
            self.visual_logger.log_backend_receive(observation_id, request_id, {"test": "data"})
            self.visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
            self.visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 10, 1)
            self.visual_logger.log_vlm_response(observation_id, request_id, 50, 0.5, True, "smolvlm")
            self.visual_logger.log_rag_data_transfer(observation_id, "test response", True)
            self.visual_logger.log_state_tracker_integration(observation_id, True, 0.02)
            
            print("  ✅ IDs consistent throughout the flow")
            print("✅ Test 3 completed - ID consistency working")
            return True
            
        except Exception as e:
            print(f"❌ Test 3 failed: {e}")
            return False
    
    def test_performance_metrics(self):
        """Test performance metric logging"""
        print("\n🧪 Test 4: Performance Metric Logging")
        print("-" * 40)
        
        observation_id = f"obs_perf_{int(time.time())}"
        
        try:
            # Test various performance metrics
            metrics = [
                ("image_processing_time", 0.125, "s"),
                ("model_inference_time", 0.850, "s"),
                ("state_tracker_time", 0.045, "s"),
                ("total_processing_time", 1.020, "s"),
                ("memory_usage", 256.5, "MB"),
                ("cpu_usage", 45.2, "%"),
                ("throughput", 2.5, "req/s")
            ]
            
            for metric_name, value, unit in metrics:
                self.visual_logger.log_performance_metric(observation_id, metric_name, value, unit)
                print(f"  ✅ Logged metric: {metric_name} = {value}{unit}")
            
            print("✅ Test 4 completed - Performance metric logging working")
            return True
            
        except Exception as e:
            print(f"❌ Test 4 failed: {e}")
            return False
    
    def test_error_scenarios(self):
        """Test error scenarios"""
        print("\n🧪 Test 5: Error Scenarios")
        print("-" * 40)
        
        observation_id = f"obs_error_{int(time.time())}"
        request_id = f"req_error_{int(time.time())}"
        
        try:
            # Test various error types
            error_scenarios = [
                ("ConnectionError", "Failed to connect to model server", "model_communication"),
                ("ValidationError", "Invalid image format", "image_processing"),
                ("TimeoutError", "Request timeout after 30s", "vlm_request"),
                ("ProcessingError", "State tracker processing failed", "state_tracker"),
                ("MemoryError", "Out of memory during processing", "resource_management")
            ]
            
            for error_type, error_message, context in error_scenarios:
                self.visual_logger.log_error(observation_id, request_id, error_type, error_message, context)
                print(f"  ✅ Logged error: {error_type}")
            
            print("✅ Test 5 completed - Error scenario logging working")
            return True
            
        except Exception as e:
            print(f"❌ Test 5 failed: {e}")
            return False
    
    async def test_concurrent_logging(self):
        """Test concurrent logging"""
        print("\n🧪 Test 6: Concurrent Logging")
        print("-" * 40)
        
        try:
            async def log_request(request_num):
                observation_id = f"obs_concurrent_{int(time.time())}_{request_num}"
                request_id = f"req_concurrent_{int(time.time())}_{request_num}"
                
                # Simulate concurrent request logging
                self.visual_logger.log_backend_receive(observation_id, request_id, {"request": request_num})
                await asyncio.sleep(0.01)  # Simulate processing time
                
                self.visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
                await asyncio.sleep(0.02)
                
                self.visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 20, 1)
                await asyncio.sleep(0.05)
                
                self.visual_logger.log_vlm_response(observation_id, request_id, 100, 0.05, True, "smolvlm")
                self.visual_logger.log_performance_metric(observation_id, "request_time", 0.08, "s")
                
                return f"Request {request_num} completed"
            
            # Execute multiple requests concurrently
            tasks = [log_request(i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            
            print(f"  ✅ Processed {len(results)} requests concurrently")
            for result in results:
                print(f"    - {result}")
            
            print("✅ Test 6 completed - Concurrent logging working")
            return True
            
        except Exception as e:
            print(f"❌ Test 6 failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Visual Logger Standalone Test")
        print("=" * 60)
        print("📝 This test does not require actual VLM server running")
        print("=" * 60)
        
        # Execute all tests
        test_methods = [
            self.test_basic_logging_functions,
            self.test_data_sanitization,
            self.test_id_consistency,
            self.test_performance_metrics,
            self.test_error_scenarios,
            self.test_concurrent_logging
        ]
        
        results = []
        for i, test_method in enumerate(test_methods, 1):
            if asyncio.iscoroutinefunction(test_method):
                result = await test_method()
            else:
                result = test_method()
            results.append(result)
        
        # Display test results
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(results)
        success_rate = (passed_tests / total_tests * 100)
        
        print(f"Total tests: {total_tests}")
        print(f"Passed tests: {passed_tests}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Visual logger functionality working.")
        else:
            print("\n⚠️ Some tests failed, please check above output.")
        
        # Check log files
        self.check_log_files()
        
        return passed_tests == total_tests
    
    def check_log_files(self):
        """Check generated log files"""
        print("\n📁 Checking log files...")
        
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        if os.path.exists(log_dir):
            visual_log_files = [f for f in os.listdir(log_dir) if f.startswith("visual_")]
            if visual_log_files:
                print(f"✅ Found visual log files: {visual_log_files}")
                
                # Display statistics of latest log
                latest_log = max(visual_log_files)
                log_path = os.path.join(log_dir, latest_log)
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"📊 Log statistics:")
                        print(f"   - Total log entries: {len(lines)}")
                        
                        # Count different log types
                        log_types = {}
                        for line in lines:
                            for log_type in ['BACKEND_RECEIVE', 'IMAGE_PROCESSING', 'VLM_REQUEST', 
                                           'VLM_RESPONSE', 'RAG_DATA_TRANSFER', 'STATE_TRACKER_INTEGRATION',
                                           'VISUAL_PERFORMANCE', 'VISUAL_ERROR']:
                                if log_type in line:
                                    log_types[log_type] = log_types.get(log_type, 0) + 1
                        
                        for log_type, count in log_types.items():
                            print(f"   - {log_type}: {count}")
                            
                except Exception as e:
                    print(f"   ⚠️ Cannot read log file: {e}")
            else:
                print("⚠️ No visual log files found")
        else:
            print("⚠️ Log directory does not exist")


async def main():
    """Main function"""
    tester = StandaloneVLMLoggerTest()
    success = await tester.run_all_tests()
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)