#!/usr/bin/env python3
"""
驗證已完成任務的實現狀況

檢查 .kiro/specs/logging-system/tasks.md 中標記為完成的項目
是否真的實現了所需的功能。
"""

import os
import sys
import re
from pathlib import Path

def check_file_exists(file_path):
    """檢查文件是否存在"""
    return Path(file_path).exists()

def check_content_in_file(file_path, patterns):
    """檢查文件中是否包含指定的模式"""
    if not check_file_exists(file_path):
        return False, f"文件不存在: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern in patterns:
            if not re.search(pattern, content, re.IGNORECASE):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            return False, f"缺少模式: {missing_patterns}"
        
        return True, "所有模式都找到了"
    
    except Exception as e:
        return False, f"讀取文件時出錯: {e}"

def verify_completed_tasks():
    """驗證已完成的任務"""
    print("🔍 驗證已完成任務的實現狀況")
    print("=" * 50)
    
    # 檢查項目列表
    checks = [
        {
            "task": "1.1 核心 LogManager 類別",
            "file": "src/logging/log_manager.py",
            "patterns": [
                r"class LogManager",
                r"def generate_observation_id",
                r"def generate_query_id", 
                r"def generate_request_id",
                r"def generate_state_update_id",
                r"def generate_flow_id",
                r"def log_eyes_capture",
                r"def log_rag_matching",
                r"def log_rag_result"
            ]
        },
        {
            "task": "1.3 系統技術日誌記錄器",
            "file": "src/logging/system_logger.py",
            "patterns": [
                r"class SystemLogger",
                r"def log_system_startup",
                r"def log_system_shutdown",
                r"def log_memory_usage",
                r"def log_endpoint_call",
                r"def log_connection_status",
                r"def log_error"
            ]
        },
        {
            "task": "2.1 前端圖像捕獲日誌整合",
            "file": "src/frontend/index.html",
            "patterns": [
                r"class FrontendVisualLogger",
                r"logEyesCapture",
                r"logEyesPrompt",
                r"logEyesTransfer",
                r"EYES_CAPTURE",
                r"EYES_PROMPT",
                r"EYES_TRANSFER"
            ]
        },
        {
            "task": "2.2 後端VLM處理日誌整合",
            "file": "src/backend/main.py",
            "patterns": [
                r"visual_logger",
                r"observation_id",
                r"log_backend_receive",
                r"log_vlm_request",
                r"log_vlm_response",
                r"log_image_processing"
            ]
        },
        {
            "task": "2.3 RAG匹配過程日誌整合",
            "file": "src/memory/rag/knowledge_base.py",
            "patterns": [
                r"log_rag_matching",
                r"log_rag_result",
                r"RAG_MATCHING",
                r"RAG_RESULT"
            ]
        },
        {
            "task": "2.4 狀態追蹤器日誌整合",
            "file": "src/state_tracker/state_tracker.py",
            "patterns": [
                r"log_manager",
                r"state_update_id",
                r"log_state_tracker",
                r"STATE_TRACKER",
                r"generate_state_update_id"
            ]
        }
    ]
    
    all_passed = True
    
    for check in checks:
        print(f"\n📋 檢查: {check['task']}")
        print(f"📁 文件: {check['file']}")
        
        # 檢查文件是否存在
        if not check_file_exists(check['file']):
            print(f"❌ 文件不存在: {check['file']}")
            all_passed = False
            continue
        
        # 檢查內容
        success, message = check_content_in_file(check['file'], check['patterns'])
        
        if success:
            print(f"✅ 實現完整: {message}")
        else:
            print(f"❌ 實現不完整: {message}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 所有已標記完成的任務都已正確實現！")
        return True
    else:
        print("⚠️  部分任務的實現不完整，請檢查上述問題。")
        return False

def check_log_files_structure():
    """檢查日誌文件結構"""
    print("\n🗂️  檢查日誌文件結構")
    print("-" * 30)
    
    expected_structure = [
        "src/logging/",
        "src/logging/log_manager.py",
        "src/logging/system_logger.py",
        "logs/"
    ]
    
    for path in expected_structure:
        if Path(path).exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path} (缺少)")

def main():
    """主函數"""
    print("🚀 日誌系統實現驗證工具")
    print("檢查已完成任務的實際實現狀況\n")
    
    # 切換到項目根目錄
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # 驗證已完成任務
    tasks_verified = verify_completed_tasks()
    
    # 檢查文件結構
    check_log_files_structure()
    
    # 總結
    print(f"\n📊 驗證結果: {'通過' if tasks_verified else '失敗'}")
    
    return 0 if tasks_verified else 1

if __name__ == "__main__":
    sys.exit(main())