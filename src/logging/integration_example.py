#!/usr/bin/env python3
"""
系統日誌記錄器整合示例

展示如何在實際應用中整合和使用系統日誌記錄器
"""

import os
import sys
import time
import asyncio
from contextlib import asynccontextmanager

# 添加當前目錄到路徑
sys.path.append(os.path.dirname(__file__))

from system_logger import initialize_system_logger, get_system_logger


class MockFastAPIApp:
    """模擬 FastAPI 應用"""
    
    def __init__(self):
        self.system_logger = None
        self.is_running = False
    
    async def startup(self):
        """應用啟動"""
        # 初始化系統日誌記錄器
        self.system_logger = initialize_system_logger("mock_app_001")
        
        # 記錄系統啟動
        self.system_logger.log_system_startup(
            host="0.0.0.0",
            port=8000,
            model="smolvlm",
            framework="FastAPI",
            version="1.0.0"
        )
        
        # 記錄各種服務連線狀態
        self.system_logger.log_connection_status("database", "CONNECTED", "PostgreSQL ready")
        self.system_logger.log_connection_status("redis", "CONNECTED", "Cache server ready")
        self.system_logger.log_connection_status("model_server", "CONNECTED", "VLM model loaded")
        
        self.is_running = True
        print("應用啟動完成")
    
    async def shutdown(self):
        """應用關閉"""
        if self.system_logger:
            # 記錄服務斷線
            self.system_logger.log_connection_status("database", "DISCONNECTED")
            self.system_logger.log_connection_status("redis", "DISCONNECTED")
            self.system_logger.log_connection_status("model_server", "DISCONNECTED")
            
            # 記錄系統關閉
            self.system_logger.log_system_shutdown()
        
        self.is_running = False
        print("應用關閉完成")
    
    async def process_request(self, request_data: dict):
        """處理請求的示例"""
        start_time = time.time()
        request_id = f"req_{int(time.time() * 1000)}"
        
        try:
            # 記錄請求開始時的記憶體使用
            self.system_logger.log_memory_usage(f"request_start_{request_id}")
            
            # 模擬圖像處理
            if request_data.get("type") == "image":
                await self._process_image(request_data, request_id)
            
            # 模擬文字查詢處理
            elif request_data.get("type") == "query":
                await self._process_query(request_data, request_id)
            
            # 記錄成功的請求
            duration = time.time() - start_time
            self.system_logger.log_endpoint_call(
                method="POST",
                path="/api/process",
                status_code=200,
                duration=duration,
                request_id=request_id,
                client_ip="127.0.0.1"
            )
            
            # 記錄性能指標
            self.system_logger.log_performance_metric(
                "request_processing_time",
                duration,
                "s",
                "successful_request"
            )
            
            return {"status": "success", "request_id": request_id}
            
        except Exception as e:
            # 記錄錯誤
            duration = time.time() - start_time
            self.system_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={"request_type": request_data.get("type", "unknown")},
                request_id=request_id
            )
            
            # 記錄失敗的請求
            self.system_logger.log_endpoint_call(
                method="POST",
                path="/api/process",
                status_code=500,
                duration=duration,
                request_id=request_id
            )
            
            raise
    
    async def _process_image(self, request_data: dict, request_id: str):
        """處理圖像請求"""
        # 模擬圖像處理時間
        processing_start = time.time()
        
        # 記錄圖像處理開始
        self.system_logger.log_performance_metric(
            "image_size",
            request_data.get("size", 0),
            "bytes",
            f"image_processing_{request_id}"
        )
        
        # 模擬處理時間
        await asyncio.sleep(0.2)
        
        # 記錄處理完成
        processing_time = time.time() - processing_start
        self.system_logger.log_performance_metric(
            "image_processing_time",
            processing_time,
            "s",
            f"vlm_inference_{request_id}"
        )
        
        # 記錄記憶體使用
        self.system_logger.log_memory_usage(f"after_image_processing_{request_id}")
    
    async def _process_query(self, request_data: dict, request_id: str):
        """處理查詢請求"""
        query_text = request_data.get("query", "")
        
        # 記錄查詢長度
        self.system_logger.log_performance_metric(
            "query_length",
            len(query_text),
            "chars",
            f"query_processing_{request_id}"
        )
        
        # 模擬查詢處理
        await asyncio.sleep(0.1)
        
        # 記錄處理完成
        self.system_logger.log_performance_metric(
            "query_processing_time",
            0.1,
            "s",
            f"query_response_{request_id}"
        )
    
    async def health_check(self):
        """健康檢查"""
        components = [
            ("database", "HEALTHY", 5.2),
            ("redis", "HEALTHY", 1.8),
            ("model_server", "HEALTHY", 25.6),
            ("disk_space", "HEALTHY", 0.5)
        ]
        
        for component, status, response_time in components:
            self.system_logger.log_health_check(
                component=component,
                status=status,
                response_time=response_time,
                details={"last_check": time.time()}
            )
    
    async def monitor_resources(self):
        """資源監控"""
        while self.is_running:
            # 記錄記憶體和CPU使用
            self.system_logger.log_memory_usage("periodic_monitoring")
            self.system_logger.log_cpu_usage("periodic_monitoring")
            
            # 等待下次監控
            await asyncio.sleep(5)


async def simulate_application_lifecycle():
    """模擬應用生命週期"""
    app = MockFastAPIApp()
    
    try:
        # 啟動應用
        await app.startup()
        
        # 啟動資源監控（背景任務）
        monitor_task = asyncio.create_task(app.monitor_resources())
        
        # 模擬一些請求
        requests = [
            {"type": "image", "size": 1024000},
            {"type": "query", "query": "What is in this image?"},
            {"type": "image", "size": 2048000},
            {"type": "query", "query": "Describe the scene"},
        ]
        
        print("開始處理請求...")
        for i, request_data in enumerate(requests):
            try:
                result = await app.process_request(request_data)
                print(f"請求 {i+1} 處理成功: {result['request_id']}")
                
                # 間隔一段時間
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"請求 {i+1} 處理失敗: {e}")
        
        # 執行健康檢查
        print("執行健康檢查...")
        await app.health_check()
        
        # 運行一段時間讓監控收集數據
        print("運行監控 10 秒...")
        await asyncio.sleep(10)
        
        # 停止監控
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
    finally:
        # 關閉應用
        await app.shutdown()


async def demonstrate_error_scenarios():
    """演示錯誤場景的日誌記錄"""
    print("\n=== 演示錯誤場景 ===")
    
    system_logger = get_system_logger()
    
    # 模擬各種錯誤情況
    error_scenarios = [
        {
            "error_type": "ConnectionError",
            "message": "Failed to connect to model server",
            "context": {"host": "model-server", "port": 8080, "timeout": 30}
        },
        {
            "error_type": "ValidationError", 
            "message": "Invalid image format",
            "context": {"format": "txt", "expected": ["jpg", "png", "gif"]}
        },
        {
            "error_type": "TimeoutError",
            "message": "Request timeout",
            "context": {"timeout": 30, "actual_time": 35.2}
        }
    ]
    
    for scenario in error_scenarios:
        system_logger.log_error(
            error_type=scenario["error_type"],
            error_message=scenario["message"],
            context=scenario["context"],
            request_id=f"error_demo_{int(time.time())}"
        )
        
        # 記錄相關的健康檢查失敗
        if "Connection" in scenario["error_type"]:
            system_logger.log_health_check(
                component="model_server",
                status="UNHEALTHY",
                response_time=30000.0,
                details={"error": scenario["message"]}
            )


async def main():
    """主函數"""
    print("開始系統日誌記錄器整合示例")
    print("=" * 50)
    
    try:
        # 模擬應用生命週期
        await simulate_application_lifecycle()
        
        # 演示錯誤場景
        await demonstrate_error_scenarios()
        
        print("\n" + "=" * 50)
        print("整合示例完成！")
        
        # 顯示最終系統資訊
        system_logger = get_system_logger()
        if system_logger:
            final_info = system_logger.get_system_info()
            print(f"最終系統資訊: {final_info}")
        
    except Exception as e:
        print(f"示例運行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())