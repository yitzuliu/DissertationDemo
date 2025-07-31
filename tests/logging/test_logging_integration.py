#!/usr/bin/env python3
"""
AI Manual Assistant 日誌系統整合測試

測試日誌系統的完整功能，包括前端、後端和工具整合。
"""

import os
import sys
import json
import time
import unittest
from datetime import datetime, timedelta
from typing import Dict, Any

# 添加專案根目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.app_logging.log_manager import get_log_manager, initialize_log_manager, LogType
from src.app_logging.flow_tracker import get_flow_tracker, FlowType, FlowStatus, FlowStep
from tools.log_analyzer import LogAnalyzer
from tools.log_diagnostics import LogDiagnostics

class TestLoggingIntegration(unittest.TestCase):
    """日誌系統整合測試類別"""
    
    def setUp(self):
        """測試前設置"""
        # 設置測試日誌目錄
        self.test_log_dir = "test_logs"
        if not os.path.exists(self.test_log_dir):
            os.makedirs(self.test_log_dir)
        
        # 初始化日誌管理器
        self.log_manager = initialize_log_manager(self.test_log_dir)
        self.flow_tracker = get_flow_tracker()
        
        # 初始化分析工具
        self.log_analyzer = LogAnalyzer(self.test_log_dir)
        self.log_diagnostics = LogDiagnostics(self.test_log_dir)
    
    def tearDown(self):
        """測試後清理"""
        # 清理測試日誌檔案
        import shutil
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
    
    def test_log_manager_functionality(self):
        """測試日誌管理器基本功能"""
        # 測試唯一ID生成
        observation_id = self.log_manager.generate_observation_id()
        query_id = self.log_manager.generate_query_id()
        request_id = self.log_manager.generate_request_id()
        state_update_id = self.log_manager.generate_state_update_id()
        flow_id = self.log_manager.generate_flow_id()
        
        # 驗證ID格式
        self.assertTrue(observation_id.startswith('obs_'))
        self.assertTrue(query_id.startswith('query_'))
        self.assertTrue(request_id.startswith('req_'))
        self.assertTrue(state_update_id.startswith('state_'))
        self.assertTrue(flow_id.startswith('flow_'))
        
        # 測試日誌記錄
        self.log_manager.log_user_query(
            query_id=query_id,
            request_id=request_id,
            question="測試查詢",
            language="zh"
        )
        
        self.log_manager.log_query_classify(
            query_id=query_id,
            query_type="current_step",
            confidence=0.95
        )
        
        self.log_manager.log_query_response(
            query_id=query_id,
            response="您目前在步驟2",
            duration=1.5
        )
        
        # 驗證日誌檔案存在
        today = datetime.now().strftime("%Y%m%d")
        user_log_file = os.path.join(self.test_log_dir, f"user_{today}.log")
        self.assertTrue(os.path.exists(user_log_file))
    
    def test_flow_tracker_functionality(self):
        """測試流程追蹤器功能"""
        # 開始流程
        flow_id = self.flow_tracker.start_flow(
            FlowType.USER_QUERY,
            metadata={"test": True}
        )
        
        # 添加流程步驟
        self.flow_tracker.add_flow_step(
            flow_id=flow_id,
            step=FlowStep.QUERY_RECEIVED,
            related_ids={"query_id": "test_query_123"}
        )
        
        self.flow_tracker.add_flow_step(
            flow_id=flow_id,
            step=FlowStep.QUERY_CLASSIFICATION,
            related_ids={"query_id": "test_query_123"},
            metadata={"confidence": 0.95}
        )
        
        # 結束流程
        self.flow_tracker.end_flow(
            flow_id=flow_id,
            status=FlowStatus.SUCCESS,
            final_metadata={"result": "success"}
        )
        
        # 驗證流程資訊
        flow_info = self.flow_tracker.get_flow_info(flow_id)
        self.assertIsNotNone(flow_info)
        self.assertEqual(flow_info['status'], FlowStatus.SUCCESS.value)
        self.assertEqual(len(flow_info['steps']), 2)
    
    def test_log_analyzer_functionality(self):
        """測試日誌分析器功能"""
        # 生成測試日誌
        query_id = self.log_manager.generate_query_id()
        request_id = self.log_manager.generate_request_id()
        
        self.log_manager.log_user_query(
            query_id=query_id,
            request_id=request_id,
            question="測試分析查詢",
            language="zh"
        )
        
        self.log_manager.log_query_classify(
            query_id=query_id,
            query_type="current_step",
            confidence=0.9
        )
        
        self.log_manager.log_query_response(
            query_id=query_id,
            response="測試回應",
            duration=2.0
        )
        
        # 等待日誌寫入
        time.sleep(0.1)
        
        # 測試事件流程分析
        flow_analysis = self.log_analyzer.analyze_event_flow(query_id=query_id)
        self.assertIsNotNone(flow_analysis)
        self.assertEqual(flow_analysis['total_events'], 3)
        
        # 測試完整性檢查
        integrity_report = self.log_analyzer.check_data_integrity()
        self.assertIsNotNone(integrity_report)
        self.assertIn('total_queries', integrity_report)
    
    def test_log_diagnostics_functionality(self):
        """測試日誌診斷器功能"""
        # 生成測試日誌
        for i in range(5):
            query_id = self.log_manager.generate_query_id()
            request_id = self.log_manager.generate_request_id()
            
            self.log_manager.log_user_query(
                query_id=query_id,
                request_id=request_id,
                question=f"測試診斷查詢 {i}",
                language="zh"
            )
            
            self.log_manager.log_query_classify(
                query_id=query_id,
                query_type="current_step",
                confidence=0.8 + (i * 0.02)
            )
            
            self.log_manager.log_query_response(
                query_id=query_id,
                response=f"測試回應 {i}",
                duration=1.0 + (i * 0.1)
            )
        
        # 等待日誌寫入
        time.sleep(0.1)
        
        # 測試查詢分類準確度分析
        classification_analysis = self.log_diagnostics.analyze_query_classification_accuracy()
        self.assertIsNotNone(classification_analysis)
        self.assertEqual(classification_analysis['total_queries'], 5)
        self.assertGreater(classification_analysis['average_confidence'], 0.8)
        
        # 測試性能監控
        performance_monitor = self.log_diagnostics.monitor_system_performance()
        self.assertIsNotNone(performance_monitor)
        self.assertIn('query_response_times', performance_monitor)
    
    def test_comprehensive_diagnostics(self):
        """測試綜合診斷功能"""
        # 生成混合測試日誌
        for i in range(3):
            # 正常查詢
            query_id = self.log_manager.generate_query_id()
            request_id = self.log_manager.generate_request_id()
            
            self.log_manager.log_user_query(
                query_id=query_id,
                request_id=request_id,
                question=f"正常查詢 {i}",
                language="zh"
            )
            
            self.log_manager.log_query_classify(
                query_id=query_id,
                query_type="current_step",
                confidence=0.9
            )
            
            self.log_manager.log_query_response(
                query_id=query_id,
                response=f"正常回應 {i}",
                duration=1.0
            )
            
            # 觀察流程
            observation_id = self.log_manager.generate_observation_id()
            self.log_manager.log_eyes_capture(
                observation_id=observation_id,
                request_id=request_id,
                device="test_device",
                resolution="1920x1080",
                quality=0.9,
                format="JPEG",
                size="1.2MB"
            )
            
            self.log_manager.log_rag_matching(
                observation_id=observation_id,
                vlm_observation="測試觀察",
                candidate_steps=["步驟1", "步驟2"],
                similarities=[0.8, 0.6]
            )
        
        # 等待日誌寫入
        time.sleep(0.1)
        
        # 執行綜合診斷
        diagnostics_report = self.log_diagnostics.run_comprehensive_diagnostics()
        self.assertIsNotNone(diagnostics_report)
        self.assertIn('overall_status', diagnostics_report)
        self.assertIn('recommendations', diagnostics_report)
        
        # 驗證診斷結果
        self.assertIn('vlm_failure_analysis', diagnostics_report)
        self.assertIn('query_classification_analysis', diagnostics_report)
        self.assertIn('performance_monitoring', diagnostics_report)
        self.assertIn('anomaly_detection', diagnostics_report)
    
    def test_log_file_rotation(self):
        """測試日誌檔案輪轉"""
        # 生成今天的日誌
        query_id = self.log_manager.generate_query_id()
        request_id = self.log_manager.generate_request_id()
        
        self.log_manager.log_user_query(
            query_id=query_id,
            request_id=request_id,
            question="測試輪轉",
            language="zh"
        )
        
        # 驗證今天的日誌檔案存在
        today = datetime.now().strftime("%Y%m%d")
        user_log_file = os.path.join(self.test_log_dir, f"user_{today}.log")
        self.assertTrue(os.path.exists(user_log_file))
        
        # 驗證日誌內容
        with open(user_log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            self.assertIn("USER_QUERY", log_content)
            self.assertIn(query_id, log_content)
    
    def test_error_handling(self):
        """測試錯誤處理"""
        # 測試無效的日誌記錄
        try:
            self.log_manager.log_user_query(
                query_id="",
                request_id="",
                question="",
                language=""
            )
        except Exception as e:
            self.fail(f"日誌記錄應該處理空值，但拋出了異常: {e}")
        
        # 測試流程追蹤器錯誤處理
        try:
            self.flow_tracker.add_flow_step(
                flow_id="invalid_flow_id",
                step=FlowStep.QUERY_RECEIVED
            )
        except Exception as e:
            self.fail(f"流程追蹤器應該優雅處理無效流程ID，但拋出了異常: {e}")
    
    def test_performance_impact(self):
        """測試性能影響"""
        start_time = time.time()
        
        # 執行大量日誌記錄
        for i in range(100):
            query_id = self.log_manager.generate_query_id()
            request_id = self.log_manager.generate_request_id()
            
            self.log_manager.log_user_query(
                query_id=query_id,
                request_id=request_id,
                question=f"性能測試查詢 {i}",
                language="zh"
            )
            
            self.log_manager.log_query_classify(
                query_id=query_id,
                query_type="current_step",
                confidence=0.9
            )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 驗證性能（100次記錄應該在1秒內完成）
        self.assertLess(total_time, 1.0, f"日誌記錄性能不符合要求: {total_time:.3f}秒")

def run_integration_tests():
    """執行整合測試"""
    print("🧪 開始執行日誌系統整合測試...")
    
    # 創建測試套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestLoggingIntegration)
    
    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 輸出測試結果
    print(f"\n📊 測試結果摘要:")
    print(f"  執行測試: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失敗: {len(result.failures)}")
    print(f"  錯誤: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ 失敗的測試:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\n⚠️ 錯誤的測試:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n✅ 所有測試通過！日誌系統整合成功。")
        return True
    else:
        print(f"\n❌ 部分測試失敗，請檢查日誌系統實現。")
        return False

if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1) 