#!/usr/bin/env python3
"""
系統日誌記錄器測試腳本

測試 SystemLogger 的各項功能
"""

import os
import sys
import time
import asyncio
from datetime import datetime

# 添加當前目錄到路徑
sys.path.append(os.path.dirname(__file__))

from system_logger import (
    SystemLogger, get_system_logger, initialize_system_logger,
    log_startup, log_shutdown, log_request, log_error, log_memory, log_connection
)


def test_basic_functionality():
    """測試基本功能"""
    print("=== 測試基本功能 ===")
    
    # 初始化系統日誌記錄器
    system_logger = initialize_system_logger("test_system_001")
    print(f"系統ID: {system_logger.system_id}")
    
    # 測試系統啟動日誌
    system_logger.log_system_startup(
        host="localhost",
        port=8000,
        model="smolvlm",
        framework="FastAPI",
        debug_mode=True
    )
    
    # 測試記憶體和CPU使用記錄
    system_logger.log_memory_usage("startup")
    system_logger.log_cpu_usage("startup")
    
    # 測試連線狀態記錄
    system_logger.log_connection_status("frontend", "CONNECTED", "WebSocket established")
    system_logger.log_connection_status("model_server", "CONNECTED", "HTTP connection ready")
    
    # 測試端點呼叫記錄
    system_logger.log_endpoint_call(
        method="POST",
        path="/api/process_image",
        status_code=200,
        duration=0.125,
        client_ip="127.0.0.1",
        content_length=1024
    )
    
    # 測試錯誤記錄
    system_logger.log_error(
        error_type="ValidationError",
        error_message="Invalid image format",
        context={"file_type": "txt", "expected": "jpg,png"},
        request_id="req_123456"
    )
    
    # 測試性能指標記錄
    system_logger.log_performance_metric("image_processing_time", 0.234, "s", "vlm_inference")
    system_logger.log_performance_metric("memory_peak", 512.5, "MB", "image_processing")
    
    # 測試健康檢查記錄
    system_logger.log_health_check(
        component="vlm_model",
        status="HEALTHY",
        response_time=45.2,
        details={"model_loaded": True, "gpu_available": True}
    )
    
    # 獲取系統資訊
    system_info = system_logger.get_system_info()
    print(f"系統資訊: {system_info}")
    
    # 測試系統關閉日誌
    time.sleep(1)  # 模擬運行時間
    system_logger.log_system_shutdown()
    
    print("基本功能測試完成")


def test_convenience_functions():
    """測試便捷函數"""
    print("\n=== 測試便捷函數 ===")
    
    # 使用便捷函數
    log_startup(host="0.0.0.0", port=8080, model="test_model", version="1.0")
    log_memory()
    log_connection("database", "CONNECTED", "PostgreSQL ready")
    log_request("GET", "/api/health", 200, 0.005, client_ip="192.168.1.100")
    log_error("TimeoutError", "Request timeout after 30s", {"timeout": 30})
    log_shutdown()
    
    print("便捷函數測試完成")


def test_concurrent_logging():
    """測試並發日誌記錄"""
    print("\n=== 測試並發日誌記錄 ===")
    
    async def simulate_request(request_id: int):
        """模擬請求處理"""
        system_logger = get_system_logger()
        
        # 模擬請求開始
        start_time = time.time()
        
        # 記錄請求開始
        system_logger.log_connection_status(f"client_{request_id}", "CONNECTED")
        
        # 模擬處理時間
        await asyncio.sleep(0.1)
        
        # 記錄記憶體使用
        system_logger.log_memory_usage(f"request_{request_id}")
        
        # 模擬更多處理時間
        await asyncio.sleep(0.05)
        
        # 記錄請求完成
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
        """運行並發測試"""
        # 創建多個並發請求
        tasks = [simulate_request(i) for i in range(5)]
        await asyncio.gather(*tasks)
    
    # 運行並發測試
    asyncio.run(run_concurrent_test())
    
    print("並發日誌記錄測試完成")


def test_error_handling():
    """測試錯誤處理"""
    print("\n=== 測試錯誤處理 ===")
    
    system_logger = get_system_logger()
    
    # 測試各種錯誤情況
    try:
        # 模擬網路錯誤
        raise ConnectionError("Failed to connect to model server")
    except Exception as e:
        system_logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={"component": "model_client", "retry_count": 3}
        )
    
    try:
        # 模擬處理錯誤
        raise ValueError("Invalid input format")
    except Exception as e:
        system_logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={"input_type": "image", "expected_format": "base64"},
            request_id="req_error_test"
        )
    
    # 測試健康檢查失敗
    system_logger.log_health_check(
        component="external_api",
        status="UNHEALTHY",
        response_time=5000.0,
        details={"error": "timeout", "last_success": "2024-01-01T10:00:00Z"}
    )
    
    print("錯誤處理測試完成")


def test_performance_monitoring():
    """測試性能監控"""
    print("\n=== 測試性能監控 ===")
    
    system_logger = get_system_logger()
    
    # 模擬不同的性能指標
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
        time.sleep(0.01)  # 小延遲模擬真實情況
    
    # 記錄系統資源使用
    for i in range(3):
        system_logger.log_memory_usage(f"monitoring_cycle_{i}")
        system_logger.log_cpu_usage(f"monitoring_cycle_{i}")
        time.sleep(0.1)
    
    print("性能監控測試完成")


def main():
    """主測試函數"""
    print("開始系統日誌記錄器測試")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_convenience_functions()
        test_concurrent_logging()
        test_error_handling()
        test_performance_monitoring()
        
        print("\n" + "=" * 50)
        print("所有測試完成！")
        
        # 顯示最終系統資訊
        system_logger = get_system_logger()
        final_info = system_logger.get_system_info()
        print(f"最終系統資訊: {final_info}")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()