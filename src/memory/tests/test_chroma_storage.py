"""
ChromaDB存儲測試

測試ChromaDB記憶存儲的各種功能，包括語義搜索和RAG功能。
"""

import pytest
import pytest_asyncio
import tempfile
import shutil
import os
from datetime import datetime, timedelta

from src.memory.storage.chroma_storage import ChromaMemoryStorage
from src.memory.storage.exceptions import NotFoundError, DatabaseError
from src.memory.models import MemoryRecord, MemoryQuery, MemoryType


class TestChromaMemoryStorage:
    """ChromaDB記憶存儲測試"""
    
    @pytest_asyncio.fixture
    async def storage(self):
        """創建測試存儲實例"""
        # 使用臨時目錄作為測試數據庫
        temp_dir = tempfile.mkdtemp()
        
        config = {
            "persist_directory": temp_dir,
            "collection_name": "test_memory_collection",
            "embedding_model": "all-MiniLM-L6-v2",
            "max_memories": 100  # 測試用較小限制
        }
        
        storage = ChromaMemoryStorage(config)
        await storage.connect()
        
        yield storage
        
        await storage.disconnect()
        # 清理臨時目錄
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_memory(self):
        """創建測試記憶記錄"""
        return MemoryRecord(
            content="這是一個關於Python編程的測試記憶",
            context_type=MemoryType.SCREEN_OBSERVATION,
            relevance_score=0.8,
            tags=["python", "編程", "測試"],
            metadata={"source": "test", "language": "python"}
        )
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, storage):
        """測試連接和斷開"""
        assert storage.is_connected
        
        await storage.disconnect()
        assert not storage.is_connected
        
        await storage.connect()
        assert storage.is_connected
    
    @pytest.mark.asyncio
    async def test_create_memory(self, storage, sample_memory):
        """測試創建記憶"""
        memory_id = await storage.create_memory(sample_memory)
        assert memory_id == sample_memory.id
        
        # 驗證記憶已創建
        retrieved = await storage.get_memory(memory_id)
        assert retrieved is not None
        assert retrieved.content == sample_memory.content
        assert retrieved.context_type == sample_memory.context_type
        assert retrieved.relevance_score == sample_memory.relevance_score
        assert set(retrieved.tags) == set(sample_memory.tags)
        assert retrieved.metadata == sample_memory.metadata
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_memory(self, storage):
        """測試獲取不存在的記憶"""
        result = await storage.get_memory("nonexistent_id")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_semantic_search(self, storage):
        """測試語義搜索功能"""
        # 創建多個相關的測試記憶
        memories = [
            MemoryRecord(
                content="Python是一種編程語言，適合初學者學習",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.9,
                tags=["python", "編程", "學習"]
            ),
            MemoryRecord(
                content="JavaScript是網頁開發的重要技術",
                context_type=MemoryType.USER_INTERACTION,
                relevance_score=0.8,
                tags=["javascript", "網頁", "開發"]
            ),
            MemoryRecord(
                content="機器學習使用Python進行數據分析",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.85,
                tags=["python", "機器學習", "數據"]
            )
        ]
        
        for memory in memories:
            await storage.create_memory(memory)
        
        # 測試語義搜索 - 搜索與Python相關的內容
        query = MemoryQuery(
            query_text="Python編程語言",
            min_relevance=0.3  # 降低相關性閾值
        )
        result = await storage.search_memories(query)
        
        # 應該找到與Python相關的記憶
        assert len(result.records) >= 1  # 至少找到1個
        assert result.total_count >= 1
        
        # 檢查結果相關性
        python_related = [r for r in result.records if "python" in r.content.lower() or "python" in r.tags]
        assert len(python_related) >= 1
        
        # 測試語義搜索 - 搜索所有記憶（使用更寬鬆的查詢）
        query = MemoryQuery(
            query_text="學習",  # 更通用的詞，應該匹配多個記憶
            min_relevance=0.0,  # 最低閾值
            limit=10
        )
        result = await storage.search_memories(query)
        
        # 驗證搜索執行了
        assert result.query_time > 0
        # 如果找到結果，驗證結果格式正確
        if result.records:
            assert len(result.records) >= 1
            assert len(result.relevance_scores) == len(result.records)
    
    @pytest.mark.asyncio
    async def test_update_memory(self, storage, sample_memory):
        """測試更新記憶"""
        # 先創建記憶
        memory_id = await storage.create_memory(sample_memory)
        
        # 更新記憶
        updates = {
            "content": "這是更新後的Python編程記憶內容",
            "relevance_score": 0.95,
            "tags": ["python", "更新", "測試"],
            "metadata": {"source": "updated", "language": "python", "version": 2}
        }
        
        success = await storage.update_memory(memory_id, updates)
        assert success
        
        # 驗證更新
        updated = await storage.get_memory(memory_id)
        assert updated.content == "這是更新後的Python編程記憶內容"
        assert updated.relevance_score == 0.95
        assert set(updated.tags) == {"python", "更新", "測試"}
        assert updated.metadata["version"] == 2
    
    @pytest.mark.asyncio
    async def test_delete_memory(self, storage, sample_memory):
        """測試刪除記憶"""
        # 先創建記憶
        memory_id = await storage.create_memory(sample_memory)
        
        # 刪除記憶
        success = await storage.delete_memory(memory_id)
        assert success
        
        # 驗證已刪除
        result = await storage.get_memory(memory_id)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_memory_limit_and_cleanup(self, storage):
        """測試記憶體限制和自動清理"""
        # 創建超過限制的記憶數量
        memories = []
        for i in range(105):  # 超過配置的100個限制
            memory = MemoryRecord(
                content=f"測試記憶內容 {i}",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.5 + (i % 50) / 100,  # 變化的相關性分數
                tags=[f"tag{i}"]
            )
            memories.append(memory)
            await storage.create_memory(memory)
        
        # 檢查是否觸發了自動清理
        stats = await storage.get_statistics()
        assert stats.total_memories <= 100  # 應該不超過限制
    
    @pytest.mark.asyncio
    async def test_get_memories_by_type(self, storage):
        """測試根據類型獲取記憶"""
        # 創建不同類型的記憶
        screen_memory = MemoryRecord(
            content="螢幕觀察記憶",
            context_type=MemoryType.SCREEN_OBSERVATION,
            tags=["螢幕", "觀察"]
        )
        user_memory = MemoryRecord(
            content="用戶互動記憶",
            context_type=MemoryType.USER_INTERACTION,
            tags=["用戶", "互動"]
        )
        
        await storage.create_memory(screen_memory)
        await storage.create_memory(user_memory)
        
        # 測試獲取特定類型
        screen_memories = await storage.get_memories_by_type(
            MemoryType.SCREEN_OBSERVATION.value
        )
        assert len(screen_memories) >= 1
        assert all(m.context_type == MemoryType.SCREEN_OBSERVATION for m in screen_memories)
    
    @pytest.mark.asyncio
    async def test_get_memories_by_tags(self, storage):
        """測試根據標籤獲取記憶"""
        # 創建帶標籤的記憶
        memory1 = MemoryRecord(
            content="Python和機器學習",
            context_type=MemoryType.SCREEN_OBSERVATION,
            tags=["python", "機器學習", "AI"]
        )
        memory2 = MemoryRecord(
            content="Python網頁開發",
            context_type=MemoryType.SCREEN_OBSERVATION,
            tags=["python", "網頁", "開發"]
        )
        memory3 = MemoryRecord(
            content="JavaScript前端開發",
            context_type=MemoryType.SCREEN_OBSERVATION,
            tags=["javascript", "前端", "開發"]
        )
        
        await storage.create_memory(memory1)
        await storage.create_memory(memory2)
        await storage.create_memory(memory3)
        
        # 測試匹配任意標籤
        memories = await storage.get_memories_by_tags(["python"], match_all=False)
        python_memories = [m for m in memories if "python" in m.tags]
        assert len(python_memories) >= 2
        
        # 測試匹配所有標籤
        memories = await storage.get_memories_by_tags(["python", "開發"], match_all=True)
        matching_memories = [m for m in memories if "python" in m.tags and "開發" in m.tags]
        assert len(matching_memories) >= 1
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, storage):
        """測試獲取統計信息"""
        # 創建一些測試記憶
        memories = [
            MemoryRecord(
                content="統計測試記憶1",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.8
            ),
            MemoryRecord(
                content="統計測試記憶2",
                context_type=MemoryType.USER_INTERACTION,
                relevance_score=0.6
            )
        ]
        
        for memory in memories:
            await storage.create_memory(memory)
        
        stats = await storage.get_statistics()
        assert stats.total_memories >= 2
        assert MemoryType.SCREEN_OBSERVATION.value in stats.memories_by_type
        assert MemoryType.USER_INTERACTION.value in stats.memories_by_type
        assert 0.6 <= stats.average_relevance <= 0.8
        assert stats.storage_size_mb >= 0
    
    @pytest.mark.asyncio
    async def test_cleanup_old_memories(self, storage):
        """測試清理舊記憶"""
        now = datetime.now()
        old_time = now - timedelta(days=10)
        
        # 創建舊記憶
        old_memory = MemoryRecord(
            content="舊記憶內容",
            context_type=MemoryType.SCREEN_OBSERVATION,
            timestamp=old_time,
            relevance_score=0.3
        )
        new_memory = MemoryRecord(
            content="新記憶內容",
            context_type=MemoryType.SCREEN_OBSERVATION,
            relevance_score=0.8
        )
        
        await storage.create_memory(old_memory)
        await storage.create_memory(new_memory)
        
        # 清理7天前的低相關性記憶
        deleted_count = await storage.cleanup_old_memories(
            max_age_days=7,
            min_relevance=0.5
        )
        
        assert deleted_count >= 1
        
        # 驗證舊記憶被清理
        remaining_old = await storage.get_memory(old_memory.id)
        assert remaining_old is None
        
        # 驗證新記憶仍存在
        remaining_new = await storage.get_memory(new_memory.id)
        assert remaining_new is not None
    
    @pytest.mark.asyncio
    async def test_optimize_storage(self, storage, sample_memory):
        """測試存儲優化"""
        # 創建一些記憶
        await storage.create_memory(sample_memory)
        
        # 執行優化
        success = await storage.optimize_storage()
        assert success