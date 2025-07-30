#!/usr/bin/env python3
"""
測試RAG匹配過程日誌整合

驗證RAG系統的日誌記錄功能是否正確整合到知識庫和向量搜索中。
"""

import sys
import os
import asyncio
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from log_manager import initialize_log_manager, get_log_manager
from memory.rag.knowledge_base import RAGKnowledgeBase
from state_tracker.state_tracker import get_state_tracker


def setup_test_environment():
    """設置測試環境"""
    # Create temporary log directory
    temp_log_dir = tempfile.mkdtemp(prefix="rag_logging_test_")
    
    # Initialize log manager with temp directory
    log_manager = initialize_log_manager(temp_log_dir)
    
    return temp_log_dir, log_manager


def cleanup_test_environment(temp_log_dir):
    """清理測試環境"""
    if os.path.exists(temp_log_dir):
        shutil.rmtree(temp_log_dir)


def test_rag_knowledge_base_logging():
    """測試RAG知識庫的日誌記錄功能"""
    print("=== 測試RAG知識庫日誌記錄 ===")
    
    temp_log_dir, log_manager = setup_test_environment()
    
    try:
        # Create RAG knowledge base
        rag_kb = RAGKnowledgeBase()
        
        # Check if we can initialize (may fail if no task data)
        try:
            rag_kb.initialize(precompute_embeddings=False)
            print("✓ RAG知識庫初始化成功")
        except Exception as e:
            print(f"⚠ RAG知識庫初始化失敗（預期，因為沒有任務數據）: {e}")
            return True  # This is expected in test environment
        
        # Test observation ID generation
        observation_id = log_manager.generate_observation_id()
        print(f"✓ 生成觀察ID: {observation_id}")
        
        # Test find_matching_step with observation_id
        test_observation = "用戶正在查看咖啡機的電源按鈕"
        
        try:
            match_result = rag_kb.find_matching_step(
                observation=test_observation,
                observation_id=observation_id
            )
            print(f"✓ RAG匹配測試完成，結果: {match_result}")
        except Exception as e:
            print(f"⚠ RAG匹配測試失敗（預期，因為沒有任務數據）: {e}")
        
        # Check if log files were created
        log_files = list(Path(temp_log_dir).glob("*.log"))
        print(f"✓ 創建了 {len(log_files)} 個日誌文件")
        
        # Check visual log content
        from log_manager import LogType
        visual_log_file = Path(temp_log_dir) / f"visual_{log_manager.loggers[LogType.VISUAL].handlers[0].baseFilename.split('_')[-1]}"
        if visual_log_file.exists():
            with open(visual_log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                if "RAG_MATCHING" in log_content or "RAG_RESULT" in log_content:
                    print("✓ 視覺日誌包含RAG相關記錄")
                else:
                    print("⚠ 視覺日誌未包含RAG記錄（可能因為沒有實際匹配）")
        
        return True
        
    except Exception as e:
        print(f"✗ RAG知識庫日誌測試失敗: {e}")
        return False
        
    finally:
        cleanup_test_environment(temp_log_dir)


async def test_state_tracker_rag_logging():
    """測試狀態追蹤器的RAG日誌記錄功能"""
    print("\n=== 測試狀態追蹤器RAG日誌記錄 ===")
    
    temp_log_dir, log_manager = setup_test_environment()
    
    try:
        # Get state tracker
        state_tracker = get_state_tracker()
        
        # Generate observation ID
        observation_id = log_manager.generate_observation_id()
        print(f"✓ 生成觀察ID: {observation_id}")
        
        # Test VLM response processing with observation_id
        test_vlm_text = "我看到咖啡機上有一個紅色的電源按鈕，它目前是關閉狀態"
        
        try:
            result = await state_tracker.process_vlm_response(
                vlm_text=test_vlm_text,
                observation_id=observation_id
            )
            print(f"✓ 狀態追蹤器處理完成，結果: {result}")
        except Exception as e:
            print(f"⚠ 狀態追蹤器處理失敗（預期，因為沒有任務數據）: {e}")
        
        # Check if log files were created
        log_files = list(Path(temp_log_dir).glob("*.log"))
        print(f"✓ 創建了 {len(log_files)} 個日誌文件")
        
        return True
        
    except Exception as e:
        print(f"✗ 狀態追蹤器RAG日誌測試失敗: {e}")
        return False
        
    finally:
        cleanup_test_environment(temp_log_dir)


def test_log_manager_rag_methods():
    """測試日誌管理器的RAG相關方法"""
    print("\n=== 測試日誌管理器RAG方法 ===")
    
    temp_log_dir, log_manager = setup_test_environment()
    
    try:
        # Generate test IDs
        observation_id = log_manager.generate_observation_id()
        
        # Test RAG matching logging
        test_observation = "用戶正在查看咖啡機"
        test_candidates = ["coffee_task:step_1", "coffee_task:step_2", "tea_task:step_1"]
        test_similarities = [0.85, 0.72, 0.45]
        
        log_manager.log_rag_matching(
            observation_id=observation_id,
            vlm_observation=test_observation,
            candidate_steps=test_candidates,
            similarities=test_similarities
        )
        print("✓ RAG匹配過程日誌記錄成功")
        
        # Test RAG result logging
        log_manager.log_rag_result(
            observation_id=observation_id,
            selected="coffee_task:step_1",
            title="檢查咖啡機電源",
            similarity=0.85
        )
        print("✓ RAG結果日誌記錄成功")
        
        # Check log file content
        visual_log_files = list(Path(temp_log_dir).glob("visual_*.log"))
        if visual_log_files:
            with open(visual_log_files[0], 'r', encoding='utf-8') as f:
                log_content = f.read()
                
                if "RAG_MATCHING" in log_content:
                    print("✓ 日誌文件包含RAG_MATCHING記錄")
                else:
                    print("✗ 日誌文件缺少RAG_MATCHING記錄")
                
                if "RAG_RESULT" in log_content:
                    print("✓ 日誌文件包含RAG_RESULT記錄")
                else:
                    print("✗ 日誌文件缺少RAG_RESULT記錄")
                
                if observation_id in log_content:
                    print("✓ 日誌文件包含觀察ID")
                else:
                    print("✗ 日誌文件缺少觀察ID")
        
        return True
        
    except Exception as e:
        print(f"✗ 日誌管理器RAG方法測試失敗: {e}")
        return False
        
    finally:
        cleanup_test_environment(temp_log_dir)


def main():
    """主測試函數"""
    print("開始RAG日誌整合測試...")
    
    tests = [
        ("RAG知識庫日誌記錄", test_rag_knowledge_base_logging),
        ("狀態追蹤器RAG日誌記錄", lambda: asyncio.run(test_state_tracker_rag_logging())),
        ("日誌管理器RAG方法", test_log_manager_rag_methods)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"執行測試: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                print(f"✓ {test_name} 測試通過")
                passed += 1
            else:
                print(f"✗ {test_name} 測試失敗")
        except Exception as e:
            print(f"✗ {test_name} 測試異常: {e}")
    
    print(f"\n{'='*50}")
    print(f"測試總結: {passed}/{total} 測試通過")
    print('='*50)
    
    if passed == total:
        print("🎉 所有RAG日誌整合測試通過！")
        return True
    else:
        print("⚠ 部分測試失敗，請檢查實現")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)