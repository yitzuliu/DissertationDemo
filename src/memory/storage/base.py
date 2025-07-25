"""
記憶存儲抽象基類

定義記憶存儲的標準接口，所有存儲實現都必須繼承此類。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from ..models import MemoryRecord, MemoryQuery, MemorySearchResult, MemoryStats


class BaseMemoryStorage(ABC):
    """記憶存儲抽象基類"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化存儲
        
        Args:
            config: 存儲配置字典
        """
        self.config = config
        self._is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        連接到存儲後端
        
        Returns:
            bool: 連接是否成功
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        斷開存儲連接
        
        Returns:
            bool: 斷開是否成功
        """
        pass
    
    @abstractmethod
    async def create_memory(self, memory: MemoryRecord) -> str:
        """
        創建新的記憶記錄
        
        Args:
            memory: 記憶記錄對象
            
        Returns:
            str: 創建的記憶ID
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def get_memory(self, memory_id: str) -> Optional[MemoryRecord]:
        """
        根據ID獲取記憶記錄
        
        Args:
            memory_id: 記憶ID
            
        Returns:
            Optional[MemoryRecord]: 記憶記錄，如果不存在則返回None
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新記憶記錄
        
        Args:
            memory_id: 記憶ID
            updates: 要更新的字段字典
            
        Returns:
            bool: 更新是否成功
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """
        刪除記憶記錄
        
        Args:
            memory_id: 記憶ID
            
        Returns:
            bool: 刪除是否成功
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def search_memories(self, query: MemoryQuery) -> MemorySearchResult:
        """
        搜索記憶記錄
        
        Args:
            query: 查詢對象
            
        Returns:
            MemorySearchResult: 搜索結果
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def get_memories_by_type(
        self, 
        context_type: str, 
        limit: int = 10,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """
        根據類型獲取記憶記錄
        
        Args:
            context_type: 上下文類型
            limit: 返回數量限制
            offset: 偏移量
            
        Returns:
            List[MemoryRecord]: 記憶記錄列表
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def get_memories_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: int = 10,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """
        根據時間範圍獲取記憶記錄
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            limit: 返回數量限制
            offset: 偏移量
            
        Returns:
            List[MemoryRecord]: 記憶記錄列表
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def get_memories_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        limit: int = 10,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """
        根據標籤獲取記憶記錄
        
        Args:
            tags: 標籤列表
            match_all: 是否匹配所有標籤（True）或任意標籤（False）
            limit: 返回數量限制
            offset: 偏移量
            
        Returns:
            List[MemoryRecord]: 記憶記錄列表
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def get_statistics(self) -> MemoryStats:
        """
        獲取記憶系統統計信息
        
        Returns:
            MemoryStats: 統計信息
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def cleanup_old_memories(
        self,
        max_age_days: int,
        min_relevance: float = 0.0
    ) -> int:
        """
        清理舊的記憶記錄
        
        Args:
            max_age_days: 最大保留天數
            min_relevance: 最小相關性分數
            
        Returns:
            int: 清理的記憶數量
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @abstractmethod
    async def optimize_storage(self) -> bool:
        """
        優化存儲性能
        
        Returns:
            bool: 優化是否成功
            
        Raises:
            StorageError: 存儲操作失敗
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """檢查是否已連接到存儲"""
        return self._is_connected
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        await self.disconnect()