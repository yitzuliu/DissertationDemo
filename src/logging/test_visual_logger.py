#!/usr/bin/env python3
"""
視覺日誌記錄器測試腳本

測試 VisualLogger 的各項功能
"""

import os
import sys
import time
import asyncio
from datetime import datetime

# 添加當前目錄到路徑
sys.path.append(os.path.dirname(__file__))

from visual_logger import VisualLogger, get_visual_logger


def test_basic_functionality():
    """測試基本功能"""
    print("=== 測試基本功能 ===")
    
    # 初始化視覺日誌記錄器
    visual_logger = get_visual_logger()
    
    # 生成測試ID
    observation_id = f"obs_test_{int(time.time())}"
    request_id = f"req_test_{int(time.time())}"
    
    print(f"觀察ID: {observation_id}")
    print(f"請求ID: {request_id}")
    
    # 測試後端接收日誌
    print("\n1. 測試後端接收日誌")
    request_data = {
        "model": "smolvlm",
        "messages": [
            {"role": "user", "content": "What do you see in this image?"}
        ],
        "max_tokens": 100
    }
    visual_logger.log_backend_receive(observation_id, request_id, request_data)
    
    # 測試圖像處理日誌
    print("\n2. 測試圖像處理日誌")
    visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
    time.sleep(0.1)  # 模擬處理時間
    visual_logger.log_image_processing_result(
        observation_id, request_id, 0.1, True,
        {"image_count": 1, "resolution": "1024x768"}
    )
    
    # 測試VLM請求和回應日誌
    print("\n3. 測試VLM請求和回應日誌")
    visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 25, 1)
    time.sleep(0.2)  # 模擬VLM處理時間
    visual_logger.log_vlm_response(observation_id, request_id, 150, 0.2, True, "smolvlm")
    
    # 測試RAG資料傳遞日誌
    print("\n4. 測試RAG資料傳遞日誌")
    vlm_text = "I can see coffee beans, a grinder, and brewing equipment on the counter."
    visual_logger.log_rag_data_transfer(observation_id, vlm_text, True)
    
    # 測試狀態追蹤器整合日誌
    print("\n5. 測試狀態追蹤器整合日誌")
    visual_logger.log_state_tracker_integration(observation_id, True, 0.05)
    
    # 測試性能指標日誌
    print("\n6. 測試性能指標日誌")
    visual_logger.log_performance_metric(observation_id, "total_processing_time", 0.35, "s")
    visual_logger.log_performance_metric(observation_id, "image_processing_time", 0.1, "s")
    visual_logger.log_performance_metric(observation_id, "model_inference_time", 0.2, "s")
    
    print("\n基本功能測試完成")


def test_error_handling():
    """測試錯誤處理"""
    print("\n=== 測試錯誤處理 ===")
    
    visual_logger = get_visual_logger()
    observation_id = f"obs_error_{int(time.time())}"
    request_id = f"req_error_{int(time.time())}"
    
    # 測試各種錯誤情況
    error_scenarios = [
        ("ConnectionError", "Failed to connect to model server", "model_communication"),
        ("ValidationError", "Invalid image format", "image_processing"),
        ("TimeoutError", "Request timeout after 30s", "vlm_request"),
        ("ProcessingError", "State tracker processing failed", "state_tracker")
    ]
    
    for error_type, error_message, context in error_scenarios:
        print(f"記錄錯誤: {error_type}")
        visual_logger.log_error(observation_id, request_id, error_type, error_message, context)
    
    print("錯誤處理測試完成")


def test_data_sanitization():
    """測試數據清理功能"""
    print("\n=== 測試數據清理功能 ===")
    
    visual_logger = get_visual_logger()
    observation_id = f"obs_sanitize_{int(time.time())}"
    request_id = f"req_sanitize_{int(time.time())}"
    
    # 測試包含敏感數據的請求
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
                            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    print("記錄包含圖像數據的請求（應該被清理）")
    visual_logger.log_backend_receive(observation_id, request_id, request_data)
    
    # 測試長文本清理
    long_text = "This is a very long text that should be truncated in the logs. " * 10
    print(f"\n記錄長文本（原長度: {len(long_text)}）")
    visual_logger.log_rag_data_transfer(observation_id, long_text, True)
    
    print("數據清理功能測試完成")


def test_performance_monitoring():
    """測試性能監控"""
    print("\n=== 測試性能監控 ===")
    
    visual_logger = get_visual_logger()
    observation_id = f"obs_perf_{int(time.time())}"
    
    # 模擬不同的性能指標
    metrics = [
        ("image_processing_time", 0.125, "s"),
        ("model_inference_time", 0.850, "s"),
        ("state_tracker_time", 0.045, "s"),
        ("total_processing_time", 1.020, "s"),
        ("memory_usage", 256.5, "MB"),
        ("throughput", 2.5, "req/s")
    ]
    
    for metric_name, value, unit in metrics:
        print(f"記錄性能指標: {metric_name} = {value}{unit}")
        visual_logger.log_performance_metric(observation_id, metric_name, value, unit)
        time.sleep(0.01)  # 小延遲模擬真實情況
    
    print("性能監控測試完成")


async def test_complete_vlm_flow():
    """測試完整的VLM處理流程"""
    print("\n=== 測試完整VLM處理流程 ===")
    
    visual_logger = get_visual_logger()
    observation_id = f"obs_flow_{int(time.time())}"
    request_id = f"req_flow_{int(time.time())}"
    
    print(f"開始完整流程測試 - 觀察ID: {observation_id}")
    
    # 1. 後端接收
    print("步驟 1: 後端接收VLM請求")
    request_data = {
        "model": "smolvlm",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe the coffee brewing process step by step"},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,[IMAGE_DATA]"}}
                ]
            }
        ],
        "max_tokens": 150
    }
    visual_logger.log_backend_receive(observation_id, request_id, request_data)
    await asyncio.sleep(0.1)
    
    # 2. 圖像處理
    print("步驟 2: 圖像處理")
    visual_logger.log_image_processing_start(observation_id, request_id, 1, "smolvlm")
    await asyncio.sleep(0.2)  # 模擬圖像處理時間
    visual_logger.log_image_processing_result(
        observation_id, request_id, 0.2, True,
        {"image_count": 1, "model": "smolvlm", "resolution": "1024x768"}
    )
    
    # 3. VLM請求
    print("步驟 3: VLM模型請求")
    visual_logger.log_vlm_request(observation_id, request_id, "smolvlm", 45, 1)
    await asyncio.sleep(0.8)  # 模擬VLM推理時間
    visual_logger.log_vlm_response(observation_id, request_id, 180, 0.8, True, "smolvlm")
    
    # 4. RAG資料傳遞
    print("步驟 4: RAG資料傳遞")
    vlm_response = "I can see coffee brewing equipment including a pour-over dripper, coffee filter, gooseneck kettle, digital scale, and coffee beans. This appears to be step 1 of the coffee brewing process - gathering equipment and ingredients."
    visual_logger.log_rag_data_transfer(observation_id, vlm_response, True)
    
    # 5. 狀態追蹤器整合
    print("步驟 5: 狀態追蹤器整合")
    await asyncio.sleep(0.05)  # 模擬狀態處理時間
    visual_logger.log_state_tracker_integration(observation_id, True, 0.05)
    
    # 6. 性能指標記錄
    print("步驟 6: 性能指標記錄")
    total_time = 0.2 + 0.8 + 0.05  # 圖像處理 + VLM推理 + 狀態處理
    visual_logger.log_performance_metric(observation_id, "total_processing_time", total_time, "s")
    visual_logger.log_performance_metric(observation_id, "image_processing_time", 0.2, "s")
    visual_logger.log_performance_metric(observation_id, "model_inference_time", 0.8, "s")
    visual_logger.log_performance_metric(observation_id, "state_tracker_time", 0.05, "s")
    
    print(f"完整流程測試完成 - 總處理時間: {total_time:.2f}s")


def main():
    """主測試函數"""
    print("開始視覺日誌記錄器測試")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_error_handling()
        test_data_sanitization()
        test_performance_monitoring()
        
        # 運行異步測試
        asyncio.run(test_complete_vlm_flow())
        
        print("\n" + "=" * 50)
        print("所有測試完成！")
        
        # 檢查日誌文件
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        if os.path.exists(log_dir):
            visual_log_files = [f for f in os.listdir(log_dir) if f.startswith("visual_")]
            if visual_log_files:
                print(f"視覺日誌文件已生成: {visual_log_files}")
            else:
                print("注意: 未找到視覺日誌文件，請檢查日誌配置")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()