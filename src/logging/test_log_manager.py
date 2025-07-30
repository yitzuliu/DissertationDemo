#!/usr/bin/env python3
"""
LogManager 測試腳本

用於驗證 LogManager 的基本功能
"""

import os
import sys
import time
from datetime import datetime

# 添加當前目錄到路徑
sys.path.append(os.path.dirname(__file__))

from log_manager import LogManager, get_log_manager


def test_log_manager():
    """測試 LogManager 基本功能"""
    print("開始測試 LogManager...")
    
    # 初始化日誌管理器
    log_manager = LogManager("test_logs")
    
    # 測試唯一ID生成
    print("\n1. 測試唯一ID生成:")
    obs_id = log_manager.generate_observation_id()
    query_id = log_manager.generate_query_id()
    req_id = log_manager.generate_request_id()
    state_id = log_manager.generate_state_update_id()
    flow_id = log_manager.generate_flow_id()
    
    print(f"  observation_id: {obs_id}")
    print(f"  query_id: {query_id}")
    print(f"  request_id: {req_id}")
    print(f"  state_update_id: {state_id}")
    print(f"  flow_id: {flow_id}")
    
    # 測試系統日誌
    print("\n2. 測試系統日誌記錄:")
    log_manager.log_system_start("sys_001", "localhost", 8000, "smolvlm")
    log_manager.log_memory_usage("sys_001", "22.1MB")
    log_manager.log_endpoint_call(req_id, "POST", "/v1/chat/completions", 200, 2.31)
    print("  系統日誌記錄完成")
    
    # 測試視覺日誌
    print("\n3. 測試視覺日誌記錄:")
    log_manager.log_eyes_capture(obs_id, req_id, "MacBook FaceTime HD", 
                                "1920x1080", 0.9, "JPEG", "1.2MB")
    log_manager.log_eyes_prompt(obs_id, "描述製作咖啡的步驟...", 48)
    log_manager.log_rag_matching(obs_id, "桌上有咖啡濾紙和滴濾器。", 
                               ["step1", "step2", "step3"], [0.82, 0.65, 0.12])
    log_manager.log_rag_result(obs_id, "step2", "沖洗濾紙", 0.82)
    log_manager.log_state_tracker(obs_id, state_id, 0.82, "UPDATE", 
                                {"task": "brewing_coffee", "step": 2})
    print("  視覺日誌記錄完成")
    
    # 測試使用者查詢日誌
    print("\n4. 測試使用者查詢日誌:")
    log_manager.log_user_query(query_id, req_id, "我需要什麼工具?", "zh", obs_id)
    log_manager.log_query_classify(query_id, "required_tools", 0.95)
    log_manager.log_query_process(query_id, {"task": "brewing_coffee", "step": 2})
    log_manager.log_query_response(query_id, "您需要: 濾紙、滴濾器、熱水、杯子。", 1.2)
    print("  使用者查詢日誌記錄完成")
    
    # 測試流程追蹤日誌
    print("\n5. 測試流程追蹤日誌:")
    log_manager.log_flow_start(flow_id, "EYES_OBSERVATION")
    log_manager.log_flow_step(flow_id, "image_capture", observation_id=obs_id)
    log_manager.log_flow_step(flow_id, "backend_transfer", request_id=req_id)
    log_manager.log_flow_step(flow_id, "user_query", query_id=query_id)
    log_manager.log_flow_end(flow_id, "SUCCESS", 5.0)
    print("  流程追蹤日誌記錄完成")
    
    # 檢查日誌檔案
    print("\n6. 檢查生成的日誌檔案:")
    today = datetime.now().strftime("%Y%m%d")
    log_files = [
        f"test_logs/system_{today}.log",
        f"test_logs/visual_{today}.log", 
        f"test_logs/user_{today}.log",
        f"test_logs/flow_tracking_{today}.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"  {log_file}: {len(lines)} 行")
        else:
            print(f"  {log_file}: 檔案不存在")
    
    # 清理
    log_manager.close_all_loggers()
    print("\n測試完成！")


if __name__ == "__main__":
    test_log_manager()