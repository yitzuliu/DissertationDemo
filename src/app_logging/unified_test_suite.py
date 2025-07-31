#!/usr/bin/env python3
"""
AI Manual Assistant 日誌系統統一測試套件

整合所有測試功能：
1. 核心功能測試
2. 系統整合測試
3. 最終驗證
4. 單元測試
"""

import os
import sys
import time
import asyncio
import json
import requests
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.app_logging import (
    get_log_manager, LogManager, LogType,
    get_system_logger, initialize_system_logger,
    get_visual_logger, VisualLogger,
    get_flow_tracker, FlowType, FlowStatus, FlowStep
)


class UnifiedTestSuite:
    """統一的測試套件"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
        # 初始化所有日誌組件
        self.log_manager = get_log_manager()
        self.system_logger = get_system_logger()
        self.visual_logger = get_visual_logger()
        self.flow_tracker = get_flow_tracker()
        
        print("🧪 AI Manual Assistant 日誌系統統一測試套件")
        print("=" * 60)
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """記錄測試結果"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
    
    def run_test(self, test_name: str, test_func):
        """運行單個測試"""
        try:
            result = test_func()
            self.log_test_result(test_name, True, result)
            return True
        except Exception as e:
            self.log_test_result(test_name, False, f"Error: {str(e)}")
            return False
    
    async def run_async_test(self, test_name: str, test_func):
        """運行異步測試"""
        try:
            result = await test_func()
            self.log_test_result(test_name, True, result)
            return True
        except Exception as e:
            self.log_test_result(test_name, False, f"Error: {str(e)}")
            return False
    
    # ==================== 單元測試 ====================
    
    def test_log_manager_core_functionality(self):
        """測試 LogManager 核心功能"""
        # 測試唯一ID生成
        obs_id = self.log_manager.generate_observation_id()
        query_id = self.log_manager.generate_query_id()
        request_id = self.log_manager.generate_request_id()
        state_id = self.log_manager.generate_state_update_id()
        flow_id = self.log_manager.generate_flow_id()
        
        # 驗證ID格式
        assert obs_id.startswith("obs_"), "Observation ID format error"
        assert query_id.startswith("query_"), "Query ID format error"
        assert request_id.startswith("req_"), "Request ID format error"
        assert state_id.startswith("state_"), "State ID format error"
        assert flow_id.startswith("flow_"), "Flow ID format error"
        
        # 測試日誌記錄
        self.log_manager.log_system_start("test_sys", "localhost", 8000, "test_model")
        self.log_manager.log_memory_usage("test_sys", "25.5MB")
        self.log_manager.log_endpoint_call(request_id, "POST", "/api/test", 200, 0.5)
        
        return f"Generated IDs: {obs_id[:20]}..., {query_id[:20]}..., {request_id[:20]}..."
    
    def test_system_logger_functionality(self):
        """測試系統日誌記錄器功能"""
        # 測試系統啟動日誌
        self.system_logger.log_system_startup("localhost", 8000, "test_model")
        
        # 測試記憶體和CPU使用記錄
        self.system_logger.log_memory_usage("test_context")
        self.system_logger.log_cpu_usage("test_context")
        
        # 測試端點調用記錄
        self.system_logger.log_endpoint_call("GET", "/health", 200, 0.1, "req_test")
        
        # 測試連接狀態記錄
        self.system_logger.log_connection_status("database", "CONNECTED", "Ready")
        
        # 測試錯誤記錄
        self.system_logger.log_error("TestError", "Test error message", {"context": "test"})
        
        # 測試性能指標記錄
        self.system_logger.log_performance_metric("test_metric", 1.5, "s", "test_context")
        
        # 測試健康檢查記錄
        self.system_logger.log_health_check("test_component", "HEALTHY", 0.05)
        
        return "All system logger functions tested successfully"
    
    def test_visual_logger_functionality(self):
        """測試視覺日誌記錄器功能"""
        obs_id = self.log_manager.generate_observation_id()
        request_id = self.log_manager.generate_request_id()
        
        # 測試後端接收日誌
        request_data = {"model": "test_model", "messages": [{"role": "user", "content": "test"}]}
        self.visual_logger.log_backend_receive(obs_id, request_id, request_data)
        
        # 測試圖像處理日誌
        self.visual_logger.log_image_processing_start(obs_id, request_id, 1, "test_model")
        self.visual_logger.log_image_processing_result(obs_id, request_id, 0.2, True, {"resolution": "1024x768"})
        
        # 測試VLM請求/回應日誌
        self.visual_logger.log_vlm_request(obs_id, request_id, "test_model", 50, 1)
        self.visual_logger.log_vlm_response(obs_id, request_id, 100, 0.5, True, "test_model")
        
        # 測試RAG資料傳遞日誌
        self.visual_logger.log_rag_data_transfer(obs_id, "Test VLM response", True)
        
        # 測試狀態追蹤器整合日誌
        self.visual_logger.log_state_tracker_integration(obs_id, True, 0.05)
        
        # 測試錯誤記錄
        self.visual_logger.log_error(obs_id, request_id, "TestError", "Test error", "test_context")
        
        # 測試性能指標記錄
        self.visual_logger.log_performance_metric(obs_id, "processing_time", 1.0, "s")
        
        return "All visual logger functions tested successfully"
    
    def test_flow_tracker_functionality(self):
        """測試流程追蹤器功能"""
        # 測試流程開始
        flow_id = self.flow_tracker.start_flow(FlowType.EYES_OBSERVATION, {"test": "data"})
        
        # 測試流程步驟
        self.flow_tracker.add_flow_step(flow_id, FlowStep.IMAGE_CAPTURE, {"observation_id": "obs_test"})
        self.flow_tracker.add_flow_step(flow_id, FlowStep.BACKEND_TRANSFER, {"request_id": "req_test"})
        self.flow_tracker.add_flow_step(flow_id, FlowStep.VLM_PROCESSING, {"model": "test_model"})
        self.flow_tracker.add_flow_step(flow_id, FlowStep.RAG_MATCHING, {"task": "test_task"})
        self.flow_tracker.add_flow_step(flow_id, FlowStep.STATE_UPDATE, {"state_id": "state_test"})
        
        # 測試流程結束
        self.flow_tracker.end_flow(flow_id, FlowStatus.SUCCESS, {"result": "completed"})
        
        # 測試流程信息檢索
        flow_info = self.flow_tracker.get_flow_info(flow_id)
        assert flow_info is not None, "Flow info should be retrievable"
        assert flow_info['status'] == FlowStatus.SUCCESS.value, "Flow status should be SUCCESS"
        
        # 測試統計信息
        stats = self.flow_tracker.get_flow_statistics()
        assert stats['total_flows'] > 0, "Should have flow statistics"
        
        return f"Flow tracking tested successfully. Flow ID: {flow_id}"
    
    # ==================== 整合測試 ====================
    
    async def test_vlm_processing_flow(self):
        """測試完整的VLM處理流程"""
        obs_id = self.log_manager.generate_observation_id()
        request_id = self.log_manager.generate_request_id()
        flow_id = self.flow_tracker.start_flow(FlowType.EYES_OBSERVATION, {"test": "vlm_flow"})
        
        try:
            # 1. 圖像捕獲階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.IMAGE_CAPTURE, {"observation_id": obs_id})
            self.visual_logger.log_backend_receive(obs_id, request_id, {
                "model": "smolvlm",
                "messages": [{"role": "user", "content": "What do you see?"}]
            })
            
            # 2. 圖像處理階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.BACKEND_TRANSFER, {"request_id": request_id})
            self.visual_logger.log_image_processing_start(obs_id, request_id, 1, "smolvlm")
            await asyncio.sleep(0.1)  # 模擬處理時間
            self.visual_logger.log_image_processing_result(obs_id, request_id, 0.1, True, {
                "resolution": "1024x768",
                "format": "JPEG"
            })
            
            # 3. VLM處理階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.VLM_PROCESSING, {"model": "smolvlm"})
            self.visual_logger.log_vlm_request(obs_id, request_id, "smolvlm", 25, 1)
            await asyncio.sleep(0.2)  # 模擬VLM推理時間
            self.visual_logger.log_vlm_response(obs_id, request_id, 150, 0.2, True, "smolvlm")
            
            # 4. RAG匹配階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.RAG_MATCHING, {"task": "coffee_brewing"})
            self.visual_logger.log_rag_data_transfer(obs_id, "I can see coffee brewing equipment...", True)
            
            # 5. 狀態更新階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.STATE_UPDATE, {"state_id": "state_001"})
            self.visual_logger.log_state_tracker_integration(obs_id, True, 0.05)
            
            # 6. 記錄性能指標
            self.visual_logger.log_performance_metric(obs_id, "total_processing_time", 0.35, "s")
            
            # 7. 結束流程
            self.flow_tracker.end_flow(flow_id, FlowStatus.SUCCESS, {"final_result": "vlm_processing_completed"})
            
            return f"VLM processing flow completed successfully. Flow ID: {flow_id}"
            
        except Exception as e:
            self.flow_tracker.end_flow(flow_id, FlowStatus.FAILED, {"error": str(e)})
            raise
    
    async def test_user_query_processing_flow(self):
        """測試完整的使用者查詢處理流程"""
        query_id = self.log_manager.generate_query_id()
        request_id = self.log_manager.generate_request_id()
        flow_id = self.flow_tracker.start_flow(FlowType.USER_QUERY, {"user_id": "user_001"})
        
        try:
            # 1. 查詢接收階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.QUERY_RECEIVED, {"query_id": query_id})
            self.log_manager.log_user_query(query_id, request_id, "What tools do I need?", "en", "obs_001")
            
            # 2. 查詢分類階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.QUERY_CLASSIFICATION, {"type": "tool_request"})
            self.log_manager.log_query_classify(query_id, "required_tools", 0.95)
            
            # 3. 狀態查找階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.STATE_LOOKUP, {"current_step": 2})
            self.log_manager.log_query_process(query_id, {"task": "coffee_brewing", "step": 2})
            
            # 4. 回應生成階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.RESPONSE_GENERATION, {"response_length": 120})
            await asyncio.sleep(0.1)  # 模擬回應生成時間
            
            # 5. 回應發送階段
            self.flow_tracker.add_flow_step(flow_id, FlowStep.RESPONSE_SENT, {"client_ip": "127.0.0.1"})
            self.log_manager.log_query_response(query_id, "You need: filter paper, drip coffee maker, hot water, cup.", 0.1)
            
            # 6. 記錄性能指標
            self.system_logger.log_performance_metric("query_processing_time", 0.1, "s", "user_query")
            
            # 7. 結束流程
            self.flow_tracker.end_flow(flow_id, FlowStatus.SUCCESS, {"final_result": "query_processing_completed"})
            
            return f"User query processing flow completed successfully. Flow ID: {flow_id}"
            
        except Exception as e:
            self.flow_tracker.end_flow(flow_id, FlowStatus.FAILED, {"error": str(e)})
            raise
    
    async def test_rag_system_integration(self):
        """測試RAG系統整合"""
        obs_id = self.log_manager.generate_observation_id()
        
        # 模擬RAG匹配過程
        vlm_observation = "I can see coffee filters and a drip coffee maker on the table."
        candidate_steps = ["step1", "step2", "step3", "step4"]
        similarities = [0.85, 0.92, 0.45, 0.23]
        
        # 記錄RAG匹配日誌
        self.log_manager.log_rag_matching(obs_id, vlm_observation, candidate_steps, similarities)
        
        # 記錄RAG結果
        selected_step = "step2"
        step_title = "Rinse the filter paper"
        best_similarity = 0.92
        
        self.log_manager.log_rag_result(obs_id, selected_step, step_title, best_similarity)
        
        # 記錄狀態追蹤器
        state_id = self.log_manager.generate_state_update_id()
        self.log_manager.log_state_tracker(
            obs_id, state_id, best_similarity, "UPDATE", 
            {"task": "coffee_brewing", "step": 2}
        )
        
        return f"RAG system integration completed. Selected step: {selected_step}"
    
    # ==================== 端到端測試 ====================
    
    async def test_complete_end_to_end_flow(self):
        """測試完整的端到端流程"""
        # 模擬完整的用戶場景：系統啟動 -> 視覺觀察 -> 用戶查詢 -> 回應生成
        
        # 1. 系統啟動流程
        startup_flow_id = self.flow_tracker.start_flow(FlowType.SYSTEM_STARTUP, {"version": "1.0.0"})
        self.system_logger.log_system_startup("0.0.0.0", 8000, "smolvlm")
        self.flow_tracker.add_flow_step(startup_flow_id, FlowStep.SYSTEM_INIT, {"host": "0.0.0.0"})
        self.flow_tracker.add_flow_step(startup_flow_id, FlowStep.MODEL_LOADING, {"model": "smolvlm"})
        self.flow_tracker.add_flow_step(startup_flow_id, FlowStep.SERVICE_START, {"port": 8000})
        self.flow_tracker.end_flow(startup_flow_id, FlowStatus.SUCCESS)
        
        # 2. 視覺觀察流程
        obs_id = self.log_manager.generate_observation_id()
        request_id = self.log_manager.generate_request_id()
        eyes_flow_id = self.flow_tracker.start_flow(FlowType.EYES_OBSERVATION, {"observation_id": obs_id})
        
        # 圖像捕獲
        self.flow_tracker.add_flow_step(eyes_flow_id, FlowStep.IMAGE_CAPTURE, {"observation_id": obs_id})
        self.visual_logger.log_backend_receive(obs_id, request_id, {"model": "smolvlm", "messages": []})
        self.visual_logger.log_image_processing_start(obs_id, request_id, 1, "smolvlm")
        await asyncio.sleep(0.1)
        self.visual_logger.log_image_processing_result(obs_id, request_id, 0.1, True, {"resolution": "1024x768"})
        
        # VLM處理
        self.flow_tracker.add_flow_step(eyes_flow_id, FlowStep.VLM_PROCESSING, {"model": "smolvlm"})
        self.visual_logger.log_vlm_request(obs_id, request_id, "smolvlm", 30, 1)
        await asyncio.sleep(0.2)
        self.visual_logger.log_vlm_response(obs_id, request_id, 200, 0.2, True, "smolvlm")
        
        # RAG匹配
        self.flow_tracker.add_flow_step(eyes_flow_id, FlowStep.RAG_MATCHING, {"task": "coffee_brewing"})
        self.visual_logger.log_rag_data_transfer(obs_id, "I can see coffee brewing equipment...", True)
        
        # 狀態更新
        self.flow_tracker.add_flow_step(eyes_flow_id, FlowStep.STATE_UPDATE, {"state_id": "state_001"})
        self.visual_logger.log_state_tracker_integration(obs_id, True, 0.05)
        self.flow_tracker.end_flow(eyes_flow_id, FlowStatus.SUCCESS)
        
        # 3. 用戶查詢流程
        query_id = self.log_manager.generate_query_id()
        query_flow_id = self.flow_tracker.start_flow(FlowType.USER_QUERY, {"user_id": "user_001"})
        
        # 查詢處理
        self.flow_tracker.add_flow_step(query_flow_id, FlowStep.QUERY_RECEIVED, {"query_id": query_id})
        self.log_manager.log_user_query(query_id, request_id, "What's the next step?", "en", obs_id)
        
        self.flow_tracker.add_flow_step(query_flow_id, FlowStep.QUERY_CLASSIFICATION, {"type": "next_step"})
        self.log_manager.log_query_classify(query_id, "next_step", 0.9)
        
        self.flow_tracker.add_flow_step(query_flow_id, FlowStep.STATE_LOOKUP, {"current_step": 2})
        self.log_manager.log_query_process(query_id, {"task": "coffee_brewing", "step": 2})
        
        # 回應生成
        self.flow_tracker.add_flow_step(query_flow_id, FlowStep.RESPONSE_GENERATION, {"response_length": 150})
        await asyncio.sleep(0.1)
        
        self.flow_tracker.add_flow_step(query_flow_id, FlowStep.RESPONSE_SENT, {"client_ip": "127.0.0.1"})
        self.log_manager.log_query_response(query_id, "The next step is to rinse the filter paper...", 0.1)
        self.flow_tracker.end_flow(query_flow_id, FlowStatus.SUCCESS)
        
        # 4. 記錄整體性能指標
        total_time = time.time() - self.start_time
        self.system_logger.log_performance_metric("end_to_end_processing_time", total_time, "s", "complete_flow")
        
        return f"End-to-end flow completed successfully. Total time: {total_time:.2f}s"
    
    # ==================== 測試執行器 ====================
    
    async def run_all_tests(self):
        """運行所有測試"""
        print("\n🔧 階段1：單元測試")
        print("-" * 40)
        
        # 單元測試
        self.run_test("LogManager 核心功能", self.test_log_manager_core_functionality)
        self.run_test("System Logger 功能", self.test_system_logger_functionality)
        self.run_test("Visual Logger 功能", self.test_visual_logger_functionality)
        self.run_test("Flow Tracker 功能", self.test_flow_tracker_functionality)
        
        print("\n🔍 階段2：整合測試")
        print("-" * 40)
        
        # 整合測試
        await self.run_async_test("VLM 處理流程", self.test_vlm_processing_flow)
        await self.run_async_test("使用者查詢處理流程", self.test_user_query_processing_flow)
        await self.run_async_test("RAG系統整合", self.test_rag_system_integration)
        
        print("\n🚀 階段3：端到端測試")
        print("-" * 40)
        
        # 端到端測試
        await self.run_async_test("完整端到端流程", self.test_complete_end_to_end_flow)
        
        # 生成測試報告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成測試報告"""
        print("\n" + "=" * 60)
        print("📊 統一測試報告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"總測試數量: {total_tests}")
        print(f"通過測試: {passed_tests}")
        print(f"失敗測試: {failed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失敗的測試:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        # 檢查日誌文件
        print("\n📁 日誌文件檢查:")
        log_files = [
            "logs/system_20250731.log",
            "logs/visual_20250731.log", 
            "logs/user_20250731.log",
            "logs/flow_tracking_20250731.log"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"  ✅ {log_file}: {len(lines)} 行")
            else:
                print(f"  ❌ {log_file}: 文件不存在")
        
        # 保存測試結果
        report_file = f"unified_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_results": self.test_results,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate
                },
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 測試報告已保存到: {report_file}")
        
        if success_rate == 100:
            print("\n🎉 所有測試通過！日誌系統功能完整。")
        else:
            print(f"\n⚠️ 有 {failed_tests} 個測試失敗，請檢查相關功能。")


async def main():
    """主函數"""
    test_suite = UnifiedTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 