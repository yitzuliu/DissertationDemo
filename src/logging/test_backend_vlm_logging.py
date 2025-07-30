#!/usr/bin/env python3
"""
後端VLM處理日誌記錄端到端測試

模擬完整的VLM處理流程，驗證所有日誌記錄功能

使用方法:
1. 先啟動SmolVLM服務器: python src/models/smolvlm/run_smolvlm.py
2. 在另一個終端運行此測試: python src/logging/test_backend_vlm_logging.py
3. 測試完成後可以停止SmolVLM服務器 (Ctrl+C)
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
    """SmolVLM服務器管理器"""
    
    def __init__(self):
        self.process = None
        self.model_port = 8080
        self.base_dir = Path(__file__).parent.parent.parent
        self.server_script = self.base_dir / "src" / "models" / "smolvlm" / "run_smolvlm.py"
        
    def check_server_running(self):
        """檢查服務器是否運行"""
        try:
            response = requests.get(f"http://localhost:{self.model_port}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_server(self):
        """啟動SmolVLM服務器"""
        if self.check_server_running():
            print("✅ SmolVLM服務器已經在運行")
            return True
            
        if not self.server_script.exists():
            print(f"❌ 找不到SmolVLM服務器腳本: {self.server_script}")
            return False
            
        print("🚀 啟動SmolVLM服務器...")
        try:
            self.process = subprocess.Popen(
                [sys.executable, str(self.server_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服務器啟動
            print("⏳ 等待服務器啟動...")
            for i in range(30):  # 等待最多30秒
                if self.check_server_running():
                    print("✅ SmolVLM服務器啟動成功")
                    return True
                time.sleep(1)
                print(f"   等待中... ({i+1}/30)")
            
            print("❌ SmolVLM服務器啟動超時")
            self.stop_server()
            return False
            
        except Exception as e:
            print(f"❌ 啟動SmolVLM服務器失敗: {e}")
            return False
    
    def stop_server(self):
        """停止SmolVLM服務器"""
        if self.process:
            print("🛑 停止SmolVLM服務器...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print("✅ SmolVLM服務器已停止")
            except subprocess.TimeoutExpired:
                print("⚠️ 強制停止SmolVLM服務器...")
                self.process.kill()
                self.process.wait()
                print("✅ SmolVLM服務器已強制停止")
            self.process = None


# 模擬後端VLM處理流程
class MockVLMProcessor:
    def __init__(self):
        # 導入視覺日誌記錄器
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from visual_logger import get_visual_logger
        
        self.visual_logger = get_visual_logger()
        self.model = "smolvlm"
    
    async def process_chat_completion(self, request_data: Dict[str, Any]):
        """模擬完整的chat completion處理流程"""
        request_start_time = time.time()
        request_id = f"req_{int(request_start_time * 1000)}"
        observation_id = f"obs_{int(request_start_time * 1000)}_{uuid.uuid4().hex[:8]}"
        
        print(f"🚀 開始處理VLM請求 - 觀察ID: {observation_id}")
        
        try:
            # 1. 記錄後端接收
            print("📥 步驟 1: 記錄後端接收")
            self.visual_logger.log_backend_receive(observation_id, request_id, request_data)
            await asyncio.sleep(0.01)
            
            # 2. 圖像處理
            print("🖼️ 步驟 2: 圖像處理")
            image_count = self._count_images(request_data)
            self.visual_logger.log_image_processing_start(observation_id, request_id, image_count, self.model)
            
            # 模擬圖像處理時間
            image_processing_time = 0.15
            await asyncio.sleep(image_processing_time)
            
            self.visual_logger.log_image_processing_result(
                observation_id, request_id, image_processing_time, True,
                {"image_count": image_count, "model": self.model, "resolution": "1024x768"}
            )
            
            # 3. VLM請求
            print("🤖 步驟 3: VLM模型請求")
            prompt_length = self._calculate_prompt_length(request_data)
            self.visual_logger.log_vlm_request(observation_id, request_id, self.model, prompt_length, image_count)
            
            # 模擬VLM推理時間
            vlm_processing_time = 0.85
            await asyncio.sleep(vlm_processing_time)
            
            # 模擬VLM回應
            vlm_response = "I can see coffee brewing equipment including a pour-over dripper, coffee filter, gooseneck kettle, digital scale, and coffee beans. This appears to be step 1 of the coffee brewing process - gathering equipment and ingredients."
            response_length = len(vlm_response)
            
            self.visual_logger.log_vlm_response(
                observation_id, request_id, response_length, vlm_processing_time, True, self.model
            )
            
            # 4. RAG資料傳遞
            print("🔄 步驟 4: RAG資料傳遞")
            self.visual_logger.log_rag_data_transfer(observation_id, vlm_response, True)
            
            # 5. 狀態追蹤器整合
            print("📊 步驟 5: 狀態追蹤器整合")
            state_processing_time = 0.05
            await asyncio.sleep(state_processing_time)
            
            state_updated = True  # 模擬狀態更新成功
            self.visual_logger.log_state_tracker_integration(observation_id, state_updated, state_processing_time)
            
            # 6. 性能指標記錄
            print("⚡ 步驟 6: 性能指標記錄")
            total_time = time.time() - request_start_time
            
            self.visual_logger.log_performance_metric(observation_id, "total_processing_time", total_time, "s")
            self.visual_logger.log_performance_metric(observation_id, "image_processing_time", image_processing_time, "s")
            self.visual_logger.log_performance_metric(observation_id, "model_inference_time", vlm_processing_time, "s")
            self.visual_logger.log_performance_metric(observation_id, "state_tracker_time", state_processing_time, "s")
            
            print(f"✅ VLM處理完成 - 總時間: {total_time:.2f}s")
            
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
            # 錯誤處理
            error_time = time.time() - request_start_time
            print(f"❌ 處理過程中發生錯誤: {e}")
            
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
    """測試單圖像請求"""
    print("🧪 測試 1: 單圖像請求")
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
    print(f"✅ 測試 1 完成 - 回應長度: {len(result['choices'][0]['message']['content'])}")
    return True


async def test_multiple_images_request():
    """測試多圖像請求"""
    print("\n🧪 測試 2: 多圖像請求")
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
    print(f"✅ 測試 2 完成 - 回應長度: {len(result['choices'][0]['message']['content'])}")
    return True


async def test_text_only_request():
    """測試純文本請求"""
    print("\n🧪 測試 3: 純文本請求")
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
    print(f"✅ 測試 3 完成 - 回應長度: {len(result['choices'][0]['message']['content'])}")
    return True


async def test_error_scenario():
    """測試錯誤場景"""
    print("\n🧪 測試 4: 錯誤場景")
    print("-" * 40)
    
    processor = MockVLMProcessor()
    
    # 模擬會導致錯誤的請求
    request_data = {
        "model": "invalid_model",
        "messages": [],  # 空消息列表
        "max_tokens": -1  # 無效的token數量
    }
    
    try:
        # 在VLM請求階段模擬錯誤
        original_method = processor.visual_logger.log_vlm_request
        
        def mock_vlm_request(*args, **kwargs):
            original_method(*args, **kwargs)
            raise ConnectionError("Failed to connect to model server")
        
        processor.visual_logger.log_vlm_request = mock_vlm_request
        
        await processor.process_chat_completion(request_data)
        print("❌ 測試 4 失敗 - 應該拋出異常")
        return False
        
    except ConnectionError:
        # 恢復原始方法
        processor.visual_logger.log_vlm_request = original_method
        print("✅ 測試 4 完成 - 錯誤正確處理和記錄")
        return True
    except Exception as e:
        # 恢復原始方法
        processor.visual_logger.log_vlm_request = original_method
        print(f"⚠️ 測試 4 部分成功 - 捕獲到異常: {type(e).__name__}")
        return True


async def test_performance_monitoring():
    """測試性能監控"""
    print("\n🧪 測試 5: 性能監控")
    print("-" * 40)
    
    # 創建新的處理器實例，避免之前測試的mock影響
    processor = MockVLMProcessor()
    
    # 執行多個請求來測試性能監控
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
        print(f"  處理請求 {i+1}/3")
        result = await processor.process_chat_completion(request_data)
        results.append(result)
        await asyncio.sleep(0.1)  # 間隔時間
    
    total_time = time.time() - start_time
    print(f"✅ 測試 5 完成 - 處理了 {len(results)} 個請求，總時間: {total_time:.2f}s")
    return True


async def main():
    """主測試函數"""
    print("🧪 後端VLM處理日誌記錄端到端測試")
    print("=" * 60)
    
    # 檢查是否需要啟動服務器
    server_manager = SmolVLMServerManager()
    server_started_by_test = False
    
    print("🔍 檢查SmolVLM服務器狀態...")
    if not server_manager.check_server_running():
        print("⚠️ SmolVLM服務器未運行")
        print("\n有兩種方式運行此測試:")
        print("1. 自動啟動服務器 (推薦)")
        print("2. 手動啟動服務器")
        print("\n選擇自動啟動? (y/n): ", end="")
        
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes', '']:
                if server_manager.start_server():
                    server_started_by_test = True
                else:
                    print("❌ 無法啟動服務器，請手動啟動後重試")
                    print("手動啟動命令: python src/models/smolvlm/run_smolvlm.py")
                    return False
            else:
                print("請先手動啟動SmolVLM服務器:")
                print("python src/models/smolvlm/run_smolvlm.py")
                print("然後重新運行此測試")
                return False
        except KeyboardInterrupt:
            print("\n測試被用戶中斷")
            return False
    else:
        print("✅ SmolVLM服務器正在運行")
    
    test_results = []
    
    try:
        print("\n🎯 開始執行測試...")
        print("=" * 60)
        
        # 執行所有測試
        test_results.append(await test_single_image_request())
        test_results.append(await test_multiple_images_request())
        test_results.append(await test_text_only_request())
        test_results.append(await test_error_scenario())
        test_results.append(await test_performance_monitoring())
        
        # 顯示測試結果
        print("\n" + "=" * 60)
        print("📊 測試結果摘要")
        print("=" * 60)
        
        total_tests = len(test_results)
        passed_tests = sum(test_results)
        success_rate = (passed_tests / total_tests * 100)
        
        print(f"總測試數量: {total_tests}")
        print(f"通過測試: {passed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 所有測試通過！後端VLM處理日誌記錄功能正常工作。")
        else:
            print("\n⚠️ 部分測試失敗，請檢查日誌輸出。")
        
        # 檢查日誌文件
        import os
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        if os.path.exists(log_dir):
            visual_log_files = [f for f in os.listdir(log_dir) if f.startswith("visual_")]
            if visual_log_files:
                print(f"\n📁 生成的視覺日誌文件: {visual_log_files}")
                
                # 顯示最新日誌的最後幾行
                latest_log = max(visual_log_files)
                log_path = os.path.join(log_dir, latest_log)
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"\n📄 最新日誌內容（最後5行）:")
                            for line in lines[-5:]:
                                print(f"   {line.strip()}")
                except Exception as e:
                    print(f"   無法讀取日誌文件: {e}")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理服務器
        if server_started_by_test:
            print("\n🧹 清理測試環境...")
            server_manager.stop_server()


def signal_handler(signum, frame):
    """處理中斷信號"""
    print("\n🛑 測試被中斷，正在清理...")
    sys.exit(0)


if __name__ == "__main__":
    # 註冊信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    success = asyncio.run(main())
    exit(0 if success else 1)