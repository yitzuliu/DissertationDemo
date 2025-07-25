"""
SQLite存儲測試

測試SQLite記憶存儲的各種功能。
"""

import pytest
import pytest_asyncio
import asyncio
import tempfile
import os
from datetime import datetime, timedelta

from src.memory.storage.sqlite_storage import SQLiteMemoryStorage
from src.memory.storage.exceptions import NotFoundError, DatabaseError
from src.memory.models import MemoryRecord, MemoryQuery, MemoryType


class TestSQLiteMemoryStorage:
    """SQLite記憶存儲測試"""
    
    @pytest_asyncio.fixture
    async def storage(self):
        """創建測試存儲實例"""
        # 使用臨時文件作為測試數據庫
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        config = {
            "database_path": temp_db.name,
            "timeout": 30.0
        }
        
        storage = SQLiteMemoryStorage(config)
        await storage.connect()
        
        yield storage
        
        await storage.disconnect()
        # 清理臨時文件
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)
    
    @pytest.fixture
    def sample_memory(self):
        """創建測試記憶記錄"""
        return MemoryRecord(
            content="這是一個測試記憶",
            context_type=MemoryType.SCREEN_OBSERVATION,
            relevance_score=0.8,
            tags=["測試", "記憶"],
            metadata={"source": "test", "version": 1}
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
    async def test_update_memory(self, storage, sample_memory):
        """測試更新記憶"""
        # 先創建記憶
        memory_id = await storage.create_memory(sample_memory)
        
        # 更新記憶
        updates = {
            "content": "更新後的內容",
            "relevance_score": 0.9,
            "tags": ["更新", "測試"],
            "metadata": {"source": "updated", "version": 2}
        }
        
        success = await storage.update_memory(memory_id, updates)
        assert success
        
        # 驗證更新
        updated = await storage.get_memory(memory_id)
        assert updated.content == "更新後的內容"
        assert updated.relevance_score == 0.9
        assert set(updated.tags) == {"更新", "測試"}
        assert updated.metadata["source"] == "updated"
        assert updated.metadata["version"] == 2
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_memory(self, storage):
        """測試更新不存在的記憶"""
        with pytest.raises(NotFoundError):
            await storage.update_memory("nonexistent_id", {"content": "test"})
    
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
    async def test_delete_nonexistent_memory(self, storage):
        """測試刪除不存在的記憶"""
        success = await storage.delete_memory("nonexistent_id")
        assert not success
    
    @pytest.mark.asyncio
    async def test_search_memories(self, storage):
        """測試搜索記憶"""
        # 創建多個測試記憶
        memories = [
            MemoryRecord(
                content="Python編程測試",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.8,
                tags=["python", "編程"]
            ),
            MemoryRecord(
                content="JavaScript開發",
                context_type=MemoryType.USER_INTERACTION,
                relevance_score=0.7,
                tags=["javascript", "開發"]
            ),
            MemoryRecord(
                content="數據庫設計",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.6,
                tags=["數據庫", "設計"]
            )
        ]
        
        for memory in memories:
            await storage.create_memory(memory)
        
        # 測試文本搜索
        query = MemoryQuery(query_text="Python")
        result = await storage.search_memories(query)
        assert len(result.records) == 1
        assert "Python" in result.records[0].content
        
        # 測試類型過濾
        query = MemoryQuery(
            query_text="",
            context_types=[MemoryType.SCREEN_OBSERVATION]
        )
        result = await storage.search_memories(query)
        assert len(result.records) == 2
        
        # 測試相關性過濾
        query = MemoryQuery(
            query_text="",
            min_relevance=0.75
        )
        result = await storage.search_memories(query)
        assert len(result.records) == 1
        assert result.records[0].relevance_score >= 0.75
    
    @pytest.mark.asyncio
    async def test_get_memories_by_type(self, storage):
        """測試根據類型獲取記憶"""
        # 創建不同類型的記憶
        screen_memory = MemoryRecord(
            content="螢幕觀察",
            context_type=MemoryType.SCREEN_OBSERVATION
        )
        user_memory = MemoryRecord(
            content="用戶互動",
            context_type=MemoryType.USER_INTERACTION
        )
        
        await storage.create_memory(screen_memory)
        await storage.create_memory(user_memory)
        
        # 測試獲取特定類型
        screen_memories = await storage.get_memories_by_type(
            MemoryType.SCREEN_OBSERVATION.value
        )
        assert len(screen_memories) == 1
        assert screen_memories[0].context_type == MemoryType.SCREEN_OBSERVATION
    
    @pytest.mark.asyncio
    async def test_get_memories_by_time_range(self, storage):
        """測試根據時間範圍獲取記憶"""
        now = datetime.now()
        past = now - timedelta(hours=1)
        future = now + timedelta(hours=1)
        
        # 創建不同時間的記憶
        old_memory = MemoryRecord(
            content="舊記憶",
            context_type=MemoryType.SCREEN_OBSERVATION,
            timestamp=past
        )
        new_memory = MemoryRecord(
            content="新記憶",
            context_type=MemoryType.SCREEN_OBSERVATION,
            timestamp=now
        )
        
        await storage.create_memory(old_memory)
        await storage.create_memory(new_memory)
        
        # 測試時間範圍查詢
        memories = await storage.get_memories_by_time_range(
            past - timedelta(minutes=30),
            now + timedelta(minutes=30)
        )
        assert len(memories) == 2
    
    @pytest.mark.asyncio
    async def test_get_memories_by_tags(self, storage):
        """測試根據標籤獲取記憶"""
        # 創建帶標籤的記憶
        memory1 = MemoryRecord(
            content="記憶1",
            context_type=MemoryType.SCREEN_OBSERVATION,
            tags=["python", "測試"]
        )
        memory2 = MemoryRecord(
            content="記憶2",
            context_type=MemoryType.SCREEN_OBSERVATION,
            tags=["python", "開發"]
        )
        memory3 = MemoryRecord(
            content="記憶3",
            context_type=MemoryType.SCREEN_OBSERVATION,
            tags=["javascript", "測試"]
        )
        
        await storage.create_memory(memory1)
        await storage.create_memory(memory2)
        await storage.create_memory(memory3)
        
        # 測試匹配任意標籤
        memories = await storage.get_memories_by_tags(["python"], match_all=False)
        assert len(memories) == 2
        
        # 測試匹配所有標籤
        memories = await storage.get_memories_by_tags(["python", "測試"], match_all=True)
        assert len(memories) == 1
        assert memories[0].content == "記憶1"
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, storage):
        """測試獲取統計信息"""
        # 創建一些測試記憶
        memories = [
            MemoryRecord(
                content="記憶1",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=0.8
            ),
            MemoryRecord(
                content="記憶2",
                context_type=MemoryType.USER_INTERACTION,
                relevance_score=0.6
            )
        ]
        
        for memory in memories:
            await storage.create_memory(memory)
        
        stats = await storage.get_statistics()
        assert stats.total_memories == 2
        assert stats.memories_by_type[MemoryType.SCREEN_OBSERVATION.value] == 1
        assert stats.memories_by_type[MemoryType.USER_INTERACTION.value] == 1
        assert stats.average_relevance == 0.7
        assert stats.storage_size_mb > 0
    
    @pytest.mark.asyncio
    async def test_cleanup_old_memories(self, storage):
        """測試清理舊記憶"""
        now = datetime.now()
        old_time = now - timedelta(days=10)
        
        # 創建舊記憶
        old_memory = MemoryRecord(
            content="舊記憶",
            context_type=MemoryType.SCREEN_OBSERVATION,
            timestamp=old_time,
            relevance_score=0.3
        )
        new_memory = MemoryRecord(
            content="新記憶",
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
        
        assert deleted_count == 1
        
        # 驗證只剩下新記憶
        stats = await storage.get_statistics()
        assert stats.total_memories == 1
    
    @pytest.mark.asyncio
    async def test_optimize_storage(self, storage, sample_memory):
        """測試存儲優化"""
        # 創建一些記憶
        await storage.create_memory(sample_memory)
        
        # 執行優化
        success = await storage.optimize_storage()
        assert success