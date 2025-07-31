#!/usr/bin/env python3
"""
System Logger Test Script

Test various functionalities of SystemLogger
"""

import os
import sys
import time
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from system_logger import (
    SystemLogger, get_system_logger, initialize_system_logger,
    log_startup, log_shutdown, log_request, log_error, log_memory, log_connection
)


def test_basic_functionality():
    """Test basic functionality"""
    print("=== Testing Basic Functionality ===")
    
    # Initialize system logger
    system_logger = initialize_system_logger("test_system_001")
    print(f"System ID: {system_logger.system_id}")
    
    # Test system startup logging
    system_logger.log_system_startup(
        host="localhost",
        port=8000,
        model="smolvlm",
        framework="FastAPI",
        debug_mode=True
    )
    
    # Test memory and CPU usage logging
    system_logger.log_memory_usage("startup")
    system_logger.log_cpu_usage("startup")
    
    # Test connection status logging
    system_logger.log_connection_status("frontend", "CONNECTED", "WebSocket established")
    system_logger.log_connection_status("model_server", "CONNECTED", "HTTP connection ready")
    
    # Test endpoint call logging
    system_logger.log_endpoint_call(
        method="POST",
        path="/api/process_image",
        status_code=200,
        duration=0.125,
        client_ip="127.0.0.1",
        content_length=1024
    )
    
    # Test error logging
    system_logger.log_error(
        error_type="ValidationError",
        error_message="Invalid image format",
        context={"file_type": "txt", "expected": "jpg,png"},
        request_id="req_123456"
    )
    
    # Test performance metric logging
    system_logger.log_performance_metric("image_processing_time", 0.234, "s", "vlm_inference")
    system_logger.log_performance_metric("memory_peak", 512.5, "MB", "image_processing")
    
    # Test health check logging
    system_logger.log_health_check(
        component="vlm_model",
        status="HEALTHY",
        response_time=45.2,
        details={"model_loaded": True, "gpu_available": True}
    )
    
    # Get system information
    system_info = system_logger.get_system_info()
    print(f"System Information: {system_info}")
    
    # Test system shutdown logging
    time.sleep(1)  # Simulate running time
    system_logger.log_system_shutdown()
    
    print("Basic functionality test completed")


def test_convenience_functions():
    """Test convenience functions"""
    print("\n=== Testing Convenience Functions ===")
    
    # Use convenience functions
    log_startup(host="0.0.0.0", port=8080, model="test_model", version="1.0")
    log_memory()
    log_connection("database", "CONNECTED", "PostgreSQL ready")
    log_request("GET", "/api/health", 200, 0.005, client_ip="192.168.1.100")
    log_error("TimeoutError", "Request timeout after 30s", {"timeout": 30})
    log_shutdown()
    
    print("Convenience functions test completed")


def test_concurrent_logging():
    """Test concurrent logging"""
    print("\n=== Testing Concurrent Logging ===")
    
    async def simulate_request(request_id: int):
        """Simulate request processing"""
        system_logger = get_system_logger()
        
        # Simulate request start
        start_time = time.time()
        
        # Log request start
        system_logger.log_connection_status(f"client_{request_id}", "CONNECTED")
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Log memory usage
        system_logger.log_memory_usage(f"request_{request_id}")
        
        # Simulate more processing time
        await asyncio.sleep(0.05)
        
        # Log request completion
        duration = time.time() - start_time
        system_logger.log_endpoint_call(
            method="POST",
            path=f"/api/request_{request_id}",
            status_code=200,
            duration=duration,
            request_id=f"req_{request_id}"
        )
        
        system_logger.log_connection_status(f"client_{request_id}", "DISCONNECTED")
    
    async def run_concurrent_test():
        """Run concurrent test"""
        # Create multiple concurrent requests
        tasks = [simulate_request(i) for i in range(5)]
        await asyncio.gather(*tasks)
    
    # Run concurrent test
    asyncio.run(run_concurrent_test())
    
    print("Concurrent logging test completed")


def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===")
    
    system_logger = get_system_logger()
    
    # Test various error scenarios
    try:
        # Simulate network error
        raise ConnectionError("Failed to connect to model server")
    except Exception as e:
        system_logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={"component": "model_client", "retry_count": 3}
        )
    
    try:
        # Simulate processing error
        raise ValueError("Invalid input format")
    except Exception as e:
        system_logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={"input_type": "image", "expected_format": "base64"},
            request_id="req_error_test"
        )
    
    # Test health check failure
    system_logger.log_health_check(
        component="external_api",
        status="UNHEALTHY",
        response_time=5000.0,
        details={"error": "timeout", "last_success": "2024-01-01T10:00:00Z"}
    )
    
    print("Error handling test completed")


def test_performance_monitoring():
    """Test performance monitoring"""
    print("\n=== Testing Performance Monitoring ===")
    
    system_logger = get_system_logger()
    
    # Simulate different performance metrics
    metrics = [
        ("request_latency", 0.125, "s"),
        ("throughput", 150.5, "req/s"),
        ("memory_usage", 768.2, "MB"),
        ("cpu_utilization", 45.8, "%"),
        ("disk_io", 1024.0, "KB/s"),
        ("network_bandwidth", 2.5, "MB/s")
    ]
    
    for metric_name, value, unit in metrics:
        system_logger.log_performance_metric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            context="performance_test"
        )
        time.sleep(0.01)  # Small delay to simulate real situation
    
    # Log system resource usage
    for i in range(3):
        system_logger.log_memory_usage(f"monitoring_cycle_{i}")
        system_logger.log_cpu_usage(f"monitoring_cycle_{i}")
        time.sleep(0.1)
    
    print("Performance monitoring test completed")


def main():
    """Main test function"""
    print("Starting System Logger Test")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_convenience_functions()
        test_concurrent_logging()
        test_error_handling()
        test_performance_monitoring()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
        # Display final system information
        system_logger = get_system_logger()
        final_info = system_logger.get_system_info()
        print(f"Final System Information: {final_info}")
        
    except Exception as e:
        print(f"Error occurred during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()