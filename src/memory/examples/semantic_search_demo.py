"""
語義搜索演示

展示語義向量搜索如何理解語義相關性，而不僅僅是關鍵字匹配。
"""

import asyncio
import tempfile
import shutil
import sys
import os

# 添加項目根目錄到Python路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.memory.storage.chroma_storage import ChromaMemoryStorage
from src.memory.models import MemoryRecord, MemoryQuery, MemoryType


async def semantic_search_demo():
    """演示語義搜索的威力"""
    
    # 創建臨時存儲
    temp_dir = tempfile.mkdtemp()
    config = {
        "persist_directory": temp_dir,
        "collection_name": "demo_collection",
        "embedding_model": "all-MiniLM-L6-v2",
        "max_memories": 100
    }
    
    storage = ChromaMemoryStorage(config)
    await storage.connect()
    
    try:
        # 創建一些VLM觀察記憶
        vlm_memories = [
            MemoryRecord(
                content="我看到桌面上放著一把螺絲刀和一個扳手",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.9,
                tags=["桌面", "工具"]
            ),
            MemoryRecord(
                content="用戶正在使用Python編寫代碼，螢幕上顯示VSCode編輯器",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.8,
                tags=["編程", "python", "vscode"]
            ),
            MemoryRecord(
                content="桌上有一杯咖啡和一些文件",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.7,
                tags=["桌面", "飲料", "文件"]
            ),
            MemoryRecord(
                content="用戶打開了瀏覽器，正在查看技術文檔",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.8,
                tags=["瀏覽器", "文檔", "學習"]
            ),
            MemoryRecord(
                content="螢幕上顯示一個機器學習模型的訓練過程",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.9,
                tags=["機器學習", "AI", "訓練"]
            )
        ]
        
        # 存儲記憶
        for memory in vlm_memories:
            await storage.create_memory(memory)
        
        print("🧠 VLM記憶已存儲，現在測試語義搜索...")
        print("=" * 60)
        
        # 測試各種語義查詢
        test_queries = [
            "桌上有什麼工具？",           # 應該找到螺絲刀和扳手
            "用戶在做什麼編程工作？",      # 應該找到Python編程
            "有什麼可以喝的嗎？",         # 應該找到咖啡
            "用戶在學習什麼？",           # 應該找到技術文檔和機器學習
            "AI相關的活動",              # 應該找到機器學習訓練
        ]
        
        for query_text in test_queries:
            print(f"\n🔍 查詢: '{query_text}'")
            
            query = MemoryQuery(
                query_text=query_text,
                min_relevance=0.3,  # 較低的閾值以展示更多結果
                limit=3
            )
            
            result = await storage.search_memories(query)
            
            if result.records:
                print(f"✅ 找到 {len(result.records)} 個相關記憶:")
                for i, memory in enumerate(result.records):
                    relevance = result.relevance_scores[i]
                    print(f"   {i+1}. [{relevance:.3f}] {memory.content}")
            else:
                print("❌ 沒有找到相關記憶")
            
            print(f"   查詢時間: {result.query_time:.3f}秒")
        
        print("\n" + "=" * 60)
        print("🎯 語義搜索的優勢:")
        print("1. 理解語義關係：'工具' ↔ '螺絲刀、扳手'")
        print("2. 模糊匹配：不需要精確的關鍵字")
        print("3. 上下文理解：理解用戶意圖")
        print("4. 多語言支持：中文語義理解")
        
    finally:
        await storage.disconnect()
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    asyncio.run(semantic_search_demo())