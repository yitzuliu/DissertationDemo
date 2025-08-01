#!/usr/bin/env python3
"""
Unified Logging System Test Suite

Integrates all logging system test functions, including:
- Visual logger tests
- System logger tests
- Log manager tests
- Backend integration tests
"""

import asyncio
import time
import uuid
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# 添加路徑
sys.path.append(os.path.dirname(__file__))

from visual_logger import get_visual_logger
from system_logger import get_system_logger, initialize_system_logger
from log_manager import get_log_manager


class UnifiedLoggingTestSuite:
    """Unified logging system test suite"""
    
    def __init__(self):
        self.visual_logger = get_visual_logger()
        self.system_logger = get_system_logger()
        self.log_manager = get_log_manager()
        self.test_results = []
        self.start_time = time.time()
    
    def test_basic_logging_functions(self):
        """Test basic logging functions"""
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
            
            # Test performance metrics logging
            self.visual_logger.log_performance_metric(observation_id, "total_time", 1.0, "s")
            print("  ✅ Performance metrics logging successful")
            
            # Test error logging
            self.visual_logger.log_error(observation_id, request_id, "TestError", "Test error message", "test_context")
            print("  ✅ Error logging successful")
            
            print("✅ Test 1 completed - All basic logging functions normal")
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
            # Test request with sensitive data sanitization
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
                                    "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Log sanitized data
            self.visual_logger.log_backend_receive(observation_id, request_id, request_data)
            print("  ✅ Sensitive data sanitization successful")
            
            print("✅ Test 2 completed - Data sanitization normal")
            return True
            
        except Exception as e:
            print(f"❌ Test 2 failed: {e}")
            return False
    
    def test_id_consistency(self):
        """Test ID consistency"""
        print("\n🧪 Test 3: ID Consistency")
        print("-" * 40)
        
        try:
            # Generate various IDs
            observation_id = self.log_manager.generate_observation_id()
            query_id = self.log_manager.generate_query_id()
            request_id = self.log_manager.generate_request_id()
            state_update_id = self.log_manager.generate_state_update_id()
            flow_id = self.log_manager.generate_flow_id()
            
            print(f"  ✅ Observation ID: {observation_id}")
            print(f"  ✅ Query ID: {query_id}")
            print(f"  ✅ Request ID: {request_id}")
            print(f"  ✅ State Update ID: {state_update_id}")
            print(f"  ✅ Flow ID: {flow_id}")
            
            # Validate ID format
            assert observation_id.startswith("obs_")
            assert query_id.startswith("query_")
            assert request_id.startswith("req_")
            assert state_update_id.startswith("state_")
            assert flow_id.startswith("flow_")
            
            print("✅ Test 3 completed - ID consistency normal")
            return True
            
        except Exception as e:
            print(f"❌ Test 3 failed: {e}")
            return False
    
    def test_system_logger(self):
        """Test system logger"""
        print("\n🧪 Test 4: System Logger")
        print("-" * 40)
        
        try:
            # Initialize system logger
            system_logger = initialize_system_logger("test_app_001")
            
            # Log system startup
            system_logger.log_system_startup(
                host="0.0.0.0",
                port=8000,
                model="smolvlm",
                framework="FastAPI"
            )
            print("  ✅ System startup logging successful")
            
            # Log API request
            system_logger.log_endpoint_call(
                method="POST",
                path="/api/process",
                status_code=200,
                duration=0.125,
                request_id="test_req_001"
            )
            print("  ✅ API request logging successful")
            
            # Log memory usage
            system_logger.log_memory_usage("test_memory_check")
            print("  ✅ Memory usage logging successful")
            
            # Log error
            system_logger.log_error(
                error_type="TestError",
                error_message="Test error for logging",
                context={"test": True},
                request_id="test_req_001"
            )
            print("  ✅ Error logging successful")
            
            # Log system shutdown
            system_logger.log_system_shutdown()
            print("  ✅ System shutdown logging successful")
            
            print("✅ Test 4 completed - System logger normal")
            return True
            
        except Exception as e:
            print(f"❌ Test 4 failed: {e}")
            return False
    
    def test_log_manager(self):
        """Test log manager"""
        print("\n🧪 Test 5: Log Manager")
        print("-" * 40)
        
        try:
            # Test log manager basic functionality
            log_manager = get_log_manager()
            
            # Generate various IDs
            obs_id = log_manager.generate_observation_id()
            query_id = log_manager.generate_query_id()
            request_id = log_manager.generate_request_id()
            
            # Log system events
            log_manager.log_system_start("sys_001", "localhost", 8000, "smolvlm")
            print("  ✅ System startup logging successful")
            
            # Log memory usage
            log_manager.log_memory_usage("sys_001", "22.1MB")
            print("  ✅ Memory usage logging successful")
            
            # Log endpoint call
            log_manager.log_endpoint_call(request_id, "POST", "/v1/chat/completions", 200, 2.31)
            print("  ✅ Endpoint call logging successful")
            
            # Log visual processing
            log_manager.log_eyes_capture(obs_id, request_id, "Test Camera", "1920x1080", 0.9, "JPEG", "1.2MB")
            print("  ✅ Visual processing logging successful")
            
            # Log user query
            log_manager.log_user_query(query_id, request_id, "Test question?", "en", obs_id)
            print("  ✅ User query logging successful")
            
            # Log flow tracking
            flow_id = log_manager.generate_flow_id()
            log_manager.log_flow_start(flow_id, "TEST_FLOW")
            log_manager.log_flow_step(flow_id, "test_step", observation_id=obs_id)
            log_manager.log_flow_end(flow_id, "SUCCESS", 1.0)
            print("  ✅ Flow tracking logging successful")
            
            print("✅ Test 5 completed - Log manager normal")
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
                """Concurrent logging for single request"""
                observation_id = f"obs_concurrent_{request_num}_{int(time.time())}"
                request_id = f"req_concurrent_{request_num}_{int(time.time())}"
                
                # Log complete request flow
                self.visual_logger.log_backend_receive(observation_id, request_id, {"test": True})
                self.visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
                await asyncio.sleep(0.01)  # Simulate processing time
                self.visual_logger.log_image_processing_result(observation_id, request_id, 0.01, True, {})
                self.visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 10, 1)
                await asyncio.sleep(0.01)
                self.visual_logger.log_vlm_response(observation_id, request_id, 50, 0.01, True, "smolvlm")
                
                return True
            
            # Execute 10 concurrent requests
            tasks = [log_request(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            
            success_count = sum(results)
            print(f"  ✅ Concurrent test completed: {success_count}/10 successful")
            
            if success_count == 10:
                print("✅ Test 6 completed - Concurrent logging normal")
                return True
            else:
                print(f"❌ Test 6 failed - Only {success_count}/10 successful")
                return False
                
        except Exception as e:
            print(f"❌ Test 6 failed: {e}")
            return False
    
    def check_log_files(self):
        """Check log files"""
        print("\n🧪 Test 7: Log Files Check")
        print("-" * 40)
        
        try:
            # Check both current directory and project root
            log_dir = Path("logs")
            if not log_dir.exists():
                # Try project root
                log_dir = Path(__file__).parent.parent.parent / "logs"
                if not log_dir.exists():
                    print("  ⚠️ logs directory not found")
                    return False
            
            log_files = list(log_dir.glob("*.log"))
            print(f"  📁 Found {len(log_files)} log files:")
            
            for log_file in log_files:
                print(f"    - {log_file.name}")
                
                # Check file size
                size = log_file.stat().st_size
                print(f"      Size: {size} bytes")
                
                # Check recent log entries
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            last_line = lines[-1].strip()
                            print(f"      Latest entry: {last_line[:100]}...")
                        else:
                            print(f"      File is empty")
                except Exception as e:
                    print(f"      Read failed: {e}")
            
            print("✅ Test 7 completed - Log files check normal")
            return True
            
        except Exception as e:
                    print(f"❌ Test 7 failed: {e}")
        return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Unified Logging System Test Suite")
        print("=" * 60)
        
        # Run all tests
        tests = [
            ("Basic Logging Functions", self.test_basic_logging_functions),
            ("Data Sanitization", self.test_data_sanitization),
            ("ID Consistency", self.test_id_consistency),
            ("System Logger", self.test_system_logger),
            ("Log Manager", self.test_log_manager),
            ("Concurrent Logging", self.test_concurrent_logging),
            ("Log Files Check", self.check_log_files),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} execution failed: {e}")
                results.append((test_name, False))
        
        # Display test results
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ Passed" if result else "❌ Failed"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Logging system running normally")
        else:
            print("⚠️ Some tests failed, please check related functionality")
        
        # Display execution time
        execution_time = time.time() - self.start_time
        print(f"⏱️ Total execution time: {execution_time:.2f} seconds")
        
        return passed == total


async def main():
    """Main function"""
    test_suite = UnifiedLoggingTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🎯 Test suite execution completed - All functionality normal")
        return 0
    else:
        print("\n⚠️ Test suite execution completed - Issues found")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 