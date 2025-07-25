"""
記憶系統數據模型測試

測試記憶系統中的數據模型和驗證邏輯。
"""

import pytest
from datetime import datetime, timedelta
from src.memory.models import (
    MemoryRecord, MemoryQuery, MemoryContext, MemoryType,
    MemorySearchResult, MemoryStats
)


class TestMemoryRecord:
    """MemoryRecord模型測試"""
    
    def test_create_valid_memory_record(self):
        """測試創建有效的記憶記錄"""
        record = MemoryRecord(
            content="測試記憶內容",
            context_type=MemoryType.SCREEN_OBSERVATION,
            relevance_score=0.8,
            tags=["測試", "記憶"]
        )
        
        assert record.content == "測試記憶內容"
        assert record.context_type == MemoryType.SCREEN_OBSERVATION
        assert record.relevance_score == 0.8
        assert record.tags == ["測試", "記憶"]
        assert record.id is not None
        assert isinstance(record.timestamp, datetime)
    
    def test_empty_content_validation(self):
        """測試空內容驗證"""
        with pytest.raises(ValueError, match="記憶內容不能為空"):
            MemoryRecord(
                content="",
                context_type=MemoryType.SCREEN_OBSERVATION
            )
    
    def test_whitespace_content_validation(self):
        """測試空白內容驗證"""
        with pytest.raises(ValueError, match="記憶內容不能為空"):
            MemoryRecord(
                content="   ",
                context_type=MemoryType.SCREEN_OBSERVATION
            )
    
    def test_relevance_score_range(self):
        """測試相關性分數範圍"""
        # 有效範圍
        record = MemoryRecord(
            content="測試",
            context_type=MemoryType.SCREEN_OBSERVATION,
            relevance_score=0.5
        )
        assert record.relevance_score == 0.5
        
        # 無效範圍
        with pytest.raises(ValueError):
            MemoryRecord(
                content="測試",
                context_type=MemoryType.SCREEN_OBSERVATION,
                relevance_score=1.5
            )
    
    def test_tags_lowercase_conversion(self):
        """測試標籤小寫轉換"""
        record = MemoryRecord(
            content="測試",
            context_type=MemoryType.SCREEN_OBSERVATION,
            tags=["TEST", "Memory", "  TAG  "]
        )
        
        assert record.tags == ["test", "memory", "tag"]


class TestMemoryQuery:
    """MemoryQuery模型測試"""
    
    def test_create_valid_query(self):
        """測試創建有效查詢"""
        query = MemoryQuery(
            query_text="搜索測試",
            limit=5,
            min_relevance=0.6
        )
        
        assert query.query_text == "搜索測試"
        assert query.limit == 5
        assert query.min_relevance == 0.6
    
    def test_empty_query_validation(self):
        """測試空查詢驗證"""
        with pytest.raises(ValueError, match="查詢文本不能為空"):
            MemoryQuery(query_text="")
    
    def test_time_range_validation(self):
        """測試時間範圍驗證"""
        now = datetime.now()
        past = now - timedelta(hours=1)
        
        # 有效時間範圍
        query = MemoryQuery(
            query_text="測試",
            time_range=(past, now)
        )
        assert query.time_range == (past, now)
        
        # 無效時間範圍
        with pytest.raises(ValueError, match="開始時間必須早於結束時間"):
            MemoryQuery(
                query_text="測試",
                time_range=(now, past)
            )
    
    def test_limit_range(self):
        """測試限制範圍"""
        # 有效範圍
        query = MemoryQuery(query_text="測試", limit=50)
        assert query.limit == 50
        
        # 無效範圍
        with pytest.raises(ValueError):
            MemoryQuery(query_text="測試", limit=0)
        
        with pytest.raises(ValueError):
            MemoryQuery(query_text="測試", limit=101)


class TestMemoryContext:
    """MemoryContext模型測試"""
    
    def test_create_context(self):
        """測試創建上下文"""
        context = MemoryContext(
            current_activity="編程",
            recent_interactions=["查詢1", "查詢2"],
            active_applications=["VSCode", "Chrome"],
            user_focus_area="開發"
        )
        
        assert context.current_activity == "編程"
        assert context.recent_interactions == ["查詢1", "查詢2"]
        assert context.active_applications == ["VSCode", "Chrome"]
        assert context.user_focus_area == "開發"
        assert context.session_id is not None
    
    def test_recent_interactions_limit(self):
        """測試最近互動數量限制"""
        interactions = [f"互動{i}" for i in range(15)]
        context = MemoryContext(recent_interactions=interactions)
        
        # 應該只保留最後10個
        assert len(context.recent_interactions) == 10
        assert context.recent_interactions == [f"互動{i}" for i in range(5, 15)]


class TestMemorySearchResult:
    """MemorySearchResult模型測試"""
    
    def test_create_search_result(self):
        """測試創建搜索結果"""
        records = [
            MemoryRecord(content="記錄1", context_type=MemoryType.SCREEN_OBSERVATION),
            MemoryRecord(content="記錄2", context_type=MemoryType.USER_INTERACTION)
        ]
        
        result = MemorySearchResult(
            records=records,
            total_count=2,
            query_time=0.5,
            relevance_scores=[0.8, 0.6]
        )
        
        assert len(result.records) == 2
        assert result.total_count == 2
        assert result.query_time == 0.5
        assert result.relevance_scores == [0.8, 0.6]
    
    def test_scores_records_mismatch(self):
        """測試分數與記錄數量不匹配"""
        records = [
            MemoryRecord(content="記錄1", context_type=MemoryType.SCREEN_OBSERVATION)
        ]
        
        with pytest.raises(ValueError, match="相關性分數數量必須與記錄數量匹配"):
            MemorySearchResult(
                records=records,
                total_count=1,
                query_time=0.5,
                relevance_scores=[0.8, 0.6]  # 2個分數但只有1個記錄
            )


class TestMemoryStats:
    """MemoryStats模型測試"""
    
    def test_create_stats(self):
        """測試創建統計信息"""
        now = datetime.now()
        past = now - timedelta(days=1)
        
        stats = MemoryStats(
            total_memories=100,
            memories_by_type={"screen_observation": 60, "user_interaction": 40},
            average_relevance=0.7,
            oldest_memory=past,
            newest_memory=now,
            storage_size_mb=5.2
        )
        
        assert stats.total_memories == 100
        assert stats.memories_by_type["screen_observation"] == 60
        assert stats.average_relevance == 0.7
        assert stats.oldest_memory == past
        assert stats.newest_memory == now
        assert stats.storage_size_mb == 5.2