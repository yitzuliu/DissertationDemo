#!/usr/bin/env python3
"""
RAG日誌記錄演示

展示RAG匹配過程的完整日誌記錄功能。
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from log_manager import get_log_manager
from memory.rag.knowledge_base import RAGKnowledgeBase
from state_tracker.state_tracker import get_state_tracker


async def demonstrate_rag_logging():
    """演示RAG日誌記錄功能"""
    print("=== RAG日誌記錄演示 ===\n")
    
    # Get log manager
    log_manager = get_log_manager()
    
    # Generate observation ID
    observation_id = log_manager.generate_observation_id()
    print(f"生成觀察ID: {observation_id}")
    
    # Initialize RAG knowledge base
    print("\n1. 初始化RAG知識庫...")
    rag_kb = RAGKnowledgeBase()
    try:
        rag_kb.initialize(precompute_embeddings=False)
        print("✓ RAG知識庫初始化成功")
    except Exception as e:
        print(f"⚠ RAG知識庫初始化失敗: {e}")
        return
    
    # Test different VLM observations
    test_observations = [
        "我看到咖啡機上有一個紅色的電源按鈕",
        "用戶正在將咖啡豆倒入研磨機",
        "水壺裡的水正在加熱，溫度計顯示85度",
        "咖啡正在滴濾到杯子裡，顏色很深",
        "用戶正在清潔咖啡機的濾網"
    ]
    
    print(f"\n2. 測試 {len(test_observations)} 個VLM觀察...")
    
    for i, observation in enumerate(test_observations, 1):
        print(f"\n--- 測試 {i}: {observation} ---")
        
        # Generate new observation ID for each test
        obs_id = log_manager.generate_observation_id()
        
        # Test RAG knowledge base directly
        print("直接測試RAG知識庫匹配...")
        match_result = rag_kb.find_matching_step(
            observation=observation,
            observation_id=obs_id
        )
        
        if match_result and match_result.similarity > 0:
            print(f"✓ 匹配結果: {match_result.task_name}:step_{match_result.step_id}")
            print(f"  相似度: {match_result.similarity:.3f}")
            print(f"  信心度: {match_result.confidence_level}")
            print(f"  步驟描述: {match_result.task_description[:100]}...")
        else:
            print("⚠ 未找到匹配結果")
        
        # Test through state tracker
        print("通過狀態追蹤器測試...")
        state_tracker = get_state_tracker()
        
        try:
            state_updated = await state_tracker.process_vlm_response(
                vlm_text=observation,
                observation_id=obs_id
            )
            print(f"✓ 狀態追蹤器處理完成，狀態更新: {state_updated}")
        except Exception as e:
            print(f"⚠ 狀態追蹤器處理失敗: {e}")
    
    print(f"\n3. 檢查日誌文件...")
    
    # Check log files
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"找到 {len(log_files)} 個日誌文件:")
        
        for log_file in log_files:
            print(f"  - {log_file.name}")
            
            # Check for RAG-related entries
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                rag_matching_count = content.count("RAG_MATCHING")
                rag_result_count = content.count("RAG_RESULT")
                
                if rag_matching_count > 0 or rag_result_count > 0:
                    print(f"    RAG_MATCHING: {rag_matching_count} 條記錄")
                    print(f"    RAG_RESULT: {rag_result_count} 條記錄")
                    
                    # Show recent RAG entries
                    lines = content.split('\n')
                    rag_lines = [line for line in lines if 'RAG_' in line]
                    
                    if rag_lines:
                        print("    最近的RAG日誌條目:")
                        for line in rag_lines[-3:]:  # Show last 3 entries
                            print(f"      {line}")
                            
            except Exception as e:
                print(f"    讀取日誌文件失敗: {e}")
    else:
        print("未找到日誌目錄")
    
    print(f"\n=== RAG日誌記錄演示完成 ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_rag_logging())