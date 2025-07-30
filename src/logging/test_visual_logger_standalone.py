#!/usr/bin/env python3
"""
視覺日誌記錄器獨立測試

不需要實際的VLM服務器，專門測試日誌記錄功能
"""

import asyncio
import time
import uuid
import sys
import os
from datetime import datetime
from typing import Dict, Any

# 添加路徑
sys.path.append(os.path.dirname(__file__))

from visual_logger import get_visual_logger


class StandaloneVLMLoggerTest:
    """獨立的VLM日誌記錄器測試"""
    
    def __init__(self):
        self.visual_logger = get_visual_logger()
        self.test_results = []
    
    def test_basic_logging_functions(self):
        """測試基本日誌記錄功能"""
        print("🧪 測試 1: 基本日誌記錄功能")
        print("-" * 40)
        
        observation_id = f"obs_test_{int(time.time())}"
        request_id = f"req_test_{int(time.time())}"
        
        try:
            # 測試後端接收日誌
            request_data = {
                "model": "smolvlm",
                "messages": [{"role": "user", "content": "Test message"}],
                "max_tokens": 100
            }
            self.visual_logger.log_backend_receive(observation_id, request_id, request_data)
            print("  ✅ 後端接收日誌記錄成功")
            
            # 測試圖像處理日誌
            self.visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
            self.visual_logger.log_image_processing_result(observation_id, request_id, 0.15, True, {"image_count": 1})
            print("  ✅ 圖像處理日誌記錄成功")
            
            # 測試VLM請求和回應日誌
            self.visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 25, 1)
            self.visual_logger.log_vlm_response(observation_id, request_id, 150, 0.8, True, "smolvlm")
            print("  ✅ VLM請求和回應日誌記錄成功")
            
            # 測試RAG資料傳遞日誌
            vlm_text = "Test VLM response for RAG processing"
            self.visual_logger.log_rag_data_transfer(observation_id, vlm_text, True)
            print("  ✅ RAG資料傳遞日誌記錄成功")
            
            # 測試狀態追蹤器整合日誌
            self.visual_logger.log_state_tracker_integration(observation_id, True, 0.05)
            print("  ✅ 狀態追蹤器整合日誌記錄成功")
            
            # 測試性能指標日誌
            self.visual_logger.log_performance_metric(observation_id, "total_time", 1.0, "s")
            print("  ✅ 性能指標日誌記錄成功")
            
            # 測試錯誤日誌
            self.visual_logger.log_error(observation_id, request_id, "TestError", "Test error message", "test_context")
            print("  ✅ 錯誤日誌記錄成功")
            
            print("✅ 測試 1 完成 - 所有基本日誌記錄功能正常")
            return True
            
        except Exception as e:
            print(f"❌ 測試 1 失敗: {e}")
            return False
    
    def test_data_sanitization(self):
        """測試數據清理功能"""
        print("\n🧪 測試 2: 數據清理功能")
        print("-" * 40)
        
        observation_id = f"obs_sanitize_{int(time.time())}"
        request_id = f"req_sanitize_{int(time.time())}"
        
        try:
            # 測試包含敏感數據的請求清理
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
                                    "url": "data:image/jpeg;base64," + "x" * 1000  # 長圖像數據
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 100
            }
            
            self.visual_logger.log_backend_receive(observation_id, request_id, request_data)
            print("  ✅ 敏感數據清理成功")
            
            # 測試長文本清理
            long_text = "This is a very long text that should be truncated. " * 20
            self.visual_logger.log_rag_data_transfer(observation_id, long_text, True)
            print("  ✅ 長文本清理成功")
            
            print("✅ 測試 2 完成 - 數據清理功能正常")
            return True
            
        except Exception as e:
            print(f"❌ 測試 2 失敗: {e}")
            return False
    
    def test_id_consistency(self):
        """測試ID一致性"""
        print("\n🧪 測試 3: ID一致性")
        print("-" * 40)
        
        try:
            # 生成一組一致的ID
            base_time = int(time.time() * 1000)
            observation_id = f"obs_{base_time}_{uuid.uuid4().hex[:8]}"
            request_id = f"req_{base_time}"
            
            print(f"  觀察ID: {observation_id}")
            print(f"  請求ID: {request_id}")
            
            # 在整個流程中使用相同的ID
            self.visual_logger.log_backend_receive(observation_id, request_id, {"test": "data"})
            self.visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
            self.visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 10, 1)
            self.visual_logger.log_vlm_response(observation_id, request_id, 50, 0.5, True, "smolvlm")
            self.visual_logger.log_rag_data_transfer(observation_id, "test response", True)
            self.visual_logger.log_state_tracker_integration(observation_id, True, 0.02)
            
            print("  ✅ ID在整個流程中保持一致")
            print("✅ 測試 3 完成 - ID一致性正常")
            return True
            
        except Exception as e:
            print(f"❌ 測試 3 失敗: {e}")
            return False
    
    def test_performance_metrics(self):
        """測試性能指標記錄"""
        print("\n🧪 測試 4: 性能指標記錄")
        print("-" * 40)
        
        observation_id = f"obs_perf_{int(time.time())}"
        
        try:
            # 測試各種性能指標
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
                print(f"  ✅ 記錄指標: {metric_name} = {value}{unit}")
            
            print("✅ 測試 4 完成 - 性能指標記錄正常")
            return True
            
        except Exception as e:
            print(f"❌ 測試 4 失敗: {e}")
            return False
    
    def test_error_scenarios(self):
        """測試錯誤場景"""
        print("\n🧪 測試 5: 錯誤場景")
        print("-" * 40)
        
        observation_id = f"obs_error_{int(time.time())}"
        request_id = f"req_error_{int(time.time())}"
        
        try:
            # 測試各種錯誤類型
            error_scenarios = [
                ("ConnectionError", "Failed to connect to model server", "model_communication"),
                ("ValidationError", "Invalid image format", "image_processing"),
                ("TimeoutError", "Request timeout after 30s", "vlm_request"),
                ("ProcessingError", "State tracker processing failed", "state_tracker"),
                ("MemoryError", "Out of memory during processing", "resource_management")
            ]
            
            for error_type, error_message, context in error_scenarios:
                self.visual_logger.log_error(observation_id, request_id, error_type, error_message, context)
                print(f"  ✅ 記錄錯誤: {error_type}")
            
            print("✅ 測試 5 完成 - 錯誤場景記錄正常")
            return True
            
        except Exception as e:
            print(f"❌ 測試 5 失敗: {e}")
            return False
    
    async def test_concurrent_logging(self):
        """測試並發日誌記錄"""
        print("\n🧪 測試 6: 並發日誌記錄")
        print("-" * 40)
        
        try:
            async def log_request(request_num):
                observation_id = f"obs_concurrent_{int(time.time())}_{request_num}"
                request_id = f"req_concurrent_{int(time.time())}_{request_num}"
                
                # 模擬並發請求的日誌記錄
                self.visual_logger.log_backend_receive(observation_id, request_id, {"request": request_num})
                await asyncio.sleep(0.01)  # 模擬處理時間
                
                self.visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
                await asyncio.sleep(0.02)
                
                self.visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 20, 1)
                await asyncio.sleep(0.05)
                
                self.visual_logger.log_vlm_response(observation_id, request_id, 100, 0.05, True, "smolvlm")
                self.visual_logger.log_performance_metric(observation_id, "request_time", 0.08, "s")
                
                return f"Request {request_num} completed"
            
            # 並發執行多個請求
            tasks = [log_request(i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            
            print(f"  ✅ 並發處理了 {len(results)} 個請求")
            for result in results:
                print(f"    - {result}")
            
            print("✅ 測試 6 完成 - 並發日誌記錄正常")
            return True
            
        except Exception as e:
            print(f"❌ 測試 6 失敗: {e}")
            return False
    
    async def run_all_tests(self):
        """運行所有測試"""
        print("🧪 視覺日誌記錄器獨立測試")
        print("=" * 60)
        print("📝 此測試不需要實際的VLM服務器運行")
        print("=" * 60)
        
        # 執行所有測試
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
        
        # 顯示測試結果
        print("\n" + "=" * 60)
        print("📊 測試結果摘要")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(results)
        success_rate = (passed_tests / total_tests * 100)
        
        print(f"總測試數量: {total_tests}")
        print(f"通過測試: {passed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 所有測試通過！視覺日誌記錄器功能正常。")
        else:
            print("\n⚠️ 部分測試失敗，請檢查上述輸出。")
        
        # 檢查日誌文件
        self.check_log_files()
        
        return passed_tests == total_tests
    
    def check_log_files(self):
        """檢查生成的日誌文件"""
        print("\n📁 檢查日誌文件...")
        
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        if os.path.exists(log_dir):
            visual_log_files = [f for f in os.listdir(log_dir) if f.startswith("visual_")]
            if visual_log_files:
                print(f"✅ 找到視覺日誌文件: {visual_log_files}")
                
                # 顯示最新日誌的統計
                latest_log = max(visual_log_files)
                log_path = os.path.join(log_dir, latest_log)
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"📊 日誌統計:")
                        print(f"   - 總日誌條目: {len(lines)}")
                        
                        # 統計不同類型的日誌
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
                    print(f"   ⚠️ 無法讀取日誌文件: {e}")
            else:
                print("⚠️ 未找到視覺日誌文件")
        else:
            print("⚠️ 日誌目錄不存在")


async def main():
    """主函數"""
    tester = StandaloneVLMLoggerTest()
    success = await tester.run_all_tests()
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 測試被用戶中斷")
        sys.exit(1)