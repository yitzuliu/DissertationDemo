"""
SQLite記憶存儲實現

基於SQLite數據庫的記憶存儲實現，提供高性能的本地存儲。
"""

import sqlite3
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import time

from .base import BaseMemoryStorage
from .exceptions import (
    ConnectionError, DatabaseError, NotFoundError, 
    ValidationError, CorruptionError
)
from ..models import MemoryRecord, MemoryQuery, MemorySearchResult, MemoryStats, MemoryType
from ..constants import DatabaseTables, DatabaseColumns

logger = logging.getLogger(__name__)


class SQLiteMemoryStorage(BaseMemoryStorage):
    """SQLite記憶存儲實現"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化SQLite存儲
        
        Args:
            config: 存儲配置
        """
        super().__init__(config)
        self.db_path = config.get("database_path", "src/data/memory.db")
        self.timeout = config.get("timeout", 30.0)
        self.connection: Optional[sqlite3.Connection] = None
        
        # 確保數據目錄存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    async def connect(self) -> bool:
        """連接到SQLite數據庫"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                timeout=self.timeout,
                check_same_thread=False
            )
            
            # 設置SQLite優化選項
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("PRAGMA synchronous=NORMAL")
            self.connection.execute("PRAGMA cache_size=10000")
            self.connection.execute("PRAGMA temp_store=MEMORY")
            
            # 創建表結構
            await self._create_tables()
            
            self._is_connected = True
            logger.info(f"成功連接到SQLite數據庫: {self.db_path}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"連接SQLite數據庫失敗: {e}")
            raise ConnectionError(f"無法連接到數據庫: {e}", "STORAGE_CONNECTION_ERROR")
    
    async def disconnect(self) -> bool:
        """斷開數據庫連接"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            
            self._is_connected = False
            logger.info("已斷開SQLite數據庫連接")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"斷開數據庫連接失敗: {e}")
            return False
    
    async def _create_tables(self) -> None:
        """創建數據庫表結構"""
        try:
            cursor = self.connection.cursor()
            
            # 創建主記憶表
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DatabaseTables.MEMORIES} (
                    {DatabaseColumns.ID} TEXT PRIMARY KEY,
                    {DatabaseColumns.CONTENT} TEXT NOT NULL,
                    {DatabaseColumns.CONTEXT_TYPE} TEXT NOT NULL,
                    {DatabaseColumns.TIMESTAMP} TEXT NOT NULL,
                    {DatabaseColumns.RELEVANCE_SCORE} REAL DEFAULT 0.0,
                    {DatabaseColumns.CREATED_AT} TEXT NOT NULL,
                    {DatabaseColumns.UPDATED_AT} TEXT NOT NULL
                )
            """)
            
            # 創建標籤表
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DatabaseTables.MEMORY_TAGS} (
                    {DatabaseColumns.MEMORY_ID} TEXT NOT NULL,
                    {DatabaseColumns.TAG} TEXT NOT NULL,
                    PRIMARY KEY ({DatabaseColumns.MEMORY_ID}, {DatabaseColumns.TAG}),
                    FOREIGN KEY ({DatabaseColumns.MEMORY_ID}) 
                        REFERENCES {DatabaseTables.MEMORIES}({DatabaseColumns.ID}) 
                        ON DELETE CASCADE
                )
            """)
            
            # 創建元數據表
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DatabaseTables.MEMORY_METADATA} (
                    {DatabaseColumns.MEMORY_ID} TEXT NOT NULL,
                    {DatabaseColumns.KEY} TEXT NOT NULL,
                    {DatabaseColumns.VALUE} TEXT,
                    PRIMARY KEY ({DatabaseColumns.MEMORY_ID}, {DatabaseColumns.KEY}),
                    FOREIGN KEY ({DatabaseColumns.MEMORY_ID}) 
                        REFERENCES {DatabaseTables.MEMORIES}({DatabaseColumns.ID}) 
                        ON DELETE CASCADE
                )
            """)
            
            # 創建系統信息表
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DatabaseTables.SYSTEM_INFO} (
                    {DatabaseColumns.KEY} TEXT PRIMARY KEY,
                    {DatabaseColumns.VALUE} TEXT,
                    {DatabaseColumns.UPDATED_AT} TEXT NOT NULL
                )
            """)
            
            # 創建索引以提高查詢性能
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_memories_timestamp 
                ON {DatabaseTables.MEMORIES}({DatabaseColumns.TIMESTAMP})
            """)
            
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_memories_context_type 
                ON {DatabaseTables.MEMORIES}({DatabaseColumns.CONTEXT_TYPE})
            """)
            
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_memories_relevance 
                ON {DatabaseTables.MEMORIES}({DatabaseColumns.RELEVANCE_SCORE})
            """)
            
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_tags_tag 
                ON {DatabaseTables.MEMORY_TAGS}({DatabaseColumns.TAG})
            """)
            
            # 創建全文搜索索引
            cursor.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts 
                USING fts5({DatabaseColumns.CONTENT}, content={DatabaseTables.MEMORIES})
            """)
            
            self.connection.commit()
            logger.info("數據庫表結構創建完成")
            
        except sqlite3.Error as e:
            logger.error(f"創建數據庫表失敗: {e}")
            raise DatabaseError(f"無法創建數據庫表: {e}", "DATABASE_CREATION_ERROR")
    
    async def create_memory(self, memory: MemoryRecord) -> str:
        """創建新的記憶記錄"""
        try:
            cursor = self.connection.cursor()
            now = datetime.now().isoformat()
            
            # 插入主記錄
            cursor.execute(f"""
                INSERT INTO {DatabaseTables.MEMORIES} (
                    {DatabaseColumns.ID}, {DatabaseColumns.CONTENT}, 
                    {DatabaseColumns.CONTEXT_TYPE}, {DatabaseColumns.TIMESTAMP},
                    {DatabaseColumns.RELEVANCE_SCORE}, {DatabaseColumns.CREATED_AT},
                    {DatabaseColumns.UPDATED_AT}
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id, memory.content, memory.context_type,
                memory.timestamp.isoformat(), memory.relevance_score, now, now
            ))
            
            # 插入標籤
            for tag in memory.tags:
                cursor.execute(f"""
                    INSERT OR IGNORE INTO {DatabaseTables.MEMORY_TAGS} 
                    ({DatabaseColumns.MEMORY_ID}, {DatabaseColumns.TAG}) 
                    VALUES (?, ?)
                """, (memory.id, tag))
            
            # 插入元數據
            for key, value in memory.metadata.items():
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {DatabaseTables.MEMORY_METADATA} 
                    ({DatabaseColumns.MEMORY_ID}, {DatabaseColumns.KEY}, {DatabaseColumns.VALUE}) 
                    VALUES (?, ?, ?)
                """, (memory.id, key, json.dumps(value)))
            
            # 更新全文搜索索引
            cursor.execute(f"""
                INSERT INTO memories_fts(rowid, {DatabaseColumns.CONTENT}) 
                VALUES ((SELECT rowid FROM {DatabaseTables.MEMORIES} WHERE {DatabaseColumns.ID} = ?), ?)
            """, (memory.id, memory.content))
            
            self.connection.commit()
            logger.debug(f"成功創建記憶記錄: {memory.id}")
            return memory.id
            
        except sqlite3.Error as e:
            logger.error(f"創建記憶記錄失敗: {e}")
            raise DatabaseError(f"無法創建記憶記錄: {e}", "MEMORY_CREATE_ERROR")
    
    async def get_memory(self, memory_id: str) -> Optional[MemoryRecord]:
        """根據ID獲取記憶記錄"""
        try:
            cursor = self.connection.cursor()
            
            # 獲取主記錄
            cursor.execute(f"""
                SELECT {DatabaseColumns.ID}, {DatabaseColumns.CONTENT}, 
                       {DatabaseColumns.CONTEXT_TYPE}, {DatabaseColumns.TIMESTAMP},
                       {DatabaseColumns.RELEVANCE_SCORE}
                FROM {DatabaseTables.MEMORIES} 
                WHERE {DatabaseColumns.ID} = ?
            """, (memory_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # 獲取標籤
            cursor.execute(f"""
                SELECT {DatabaseColumns.TAG} 
                FROM {DatabaseTables.MEMORY_TAGS} 
                WHERE {DatabaseColumns.MEMORY_ID} = ?
            """, (memory_id,))
            tags = [row[0] for row in cursor.fetchall()]
            
            # 獲取元數據
            cursor.execute(f"""
                SELECT {DatabaseColumns.KEY}, {DatabaseColumns.VALUE} 
                FROM {DatabaseTables.MEMORY_METADATA} 
                WHERE {DatabaseColumns.MEMORY_ID} = ?
            """, (memory_id,))
            metadata = {}
            for key, value in cursor.fetchall():
                try:
                    metadata[key] = json.loads(value) if value else None
                except json.JSONDecodeError:
                    metadata[key] = value
            
            # 構建記憶記錄對象
            memory = MemoryRecord(
                id=row[0],
                content=row[1],
                context_type=MemoryType(row[2]),
                timestamp=datetime.fromisoformat(row[3]),
                relevance_score=row[4],
                tags=tags,
                metadata=metadata
            )
            
            return memory
            
        except sqlite3.Error as e:
            logger.error(f"獲取記憶記錄失敗: {e}")
            raise DatabaseError(f"無法獲取記憶記錄: {e}", "MEMORY_GET_ERROR")
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """更新記憶記錄"""
        try:
            cursor = self.connection.cursor()
            
            # 檢查記錄是否存在
            cursor.execute(f"""
                SELECT 1 FROM {DatabaseTables.MEMORIES} WHERE {DatabaseColumns.ID} = ?
            """, (memory_id,))
            
            if not cursor.fetchone():
                raise NotFoundError(f"記憶記錄不存在: {memory_id}", "MEMORY_NOT_FOUND")
            
            # 構建更新語句
            update_fields = []
            update_values = []
            
            for field, value in updates.items():
                if field in ['content', 'context_type', 'relevance_score']:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if update_fields:
                update_fields.append(f"{DatabaseColumns.UPDATED_AT} = ?")
                update_values.append(datetime.now().isoformat())
                update_values.append(memory_id)
                
                cursor.execute(f"""
                    UPDATE {DatabaseTables.MEMORIES} 
                    SET {', '.join(update_fields)} 
                    WHERE {DatabaseColumns.ID} = ?
                """, update_values)
            
            # 更新標籤
            if 'tags' in updates:
                cursor.execute(f"""
                    DELETE FROM {DatabaseTables.MEMORY_TAGS} 
                    WHERE {DatabaseColumns.MEMORY_ID} = ?
                """, (memory_id,))
                
                for tag in updates['tags']:
                    cursor.execute(f"""
                        INSERT INTO {DatabaseTables.MEMORY_TAGS} 
                        ({DatabaseColumns.MEMORY_ID}, {DatabaseColumns.TAG}) 
                        VALUES (?, ?)
                    """, (memory_id, tag))
            
            # 更新元數據
            if 'metadata' in updates:
                cursor.execute(f"""
                    DELETE FROM {DatabaseTables.MEMORY_METADATA} 
                    WHERE {DatabaseColumns.MEMORY_ID} = ?
                """, (memory_id,))
                
                for key, value in updates['metadata'].items():
                    cursor.execute(f"""
                        INSERT INTO {DatabaseTables.MEMORY_METADATA} 
                        ({DatabaseColumns.MEMORY_ID}, {DatabaseColumns.KEY}, {DatabaseColumns.VALUE}) 
                        VALUES (?, ?, ?)
                    """, (memory_id, key, json.dumps(value)))
            
            self.connection.commit()
            logger.debug(f"成功更新記憶記錄: {memory_id}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"更新記憶記錄失敗: {e}")
            raise DatabaseError(f"無法更新記憶記錄: {e}", "MEMORY_UPDATE_ERROR")
    
    async def delete_memory(self, memory_id: str) -> bool:
        """刪除記憶記錄"""
        try:
            cursor = self.connection.cursor()
            
            # 刪除主記錄（外鍵約束會自動刪除相關記錄）
            cursor.execute(f"""
                DELETE FROM {DatabaseTables.MEMORIES} 
                WHERE {DatabaseColumns.ID} = ?
            """, (memory_id,))
            
            deleted_count = cursor.rowcount
            
            # 從全文搜索索引中刪除
            cursor.execute(f"""
                DELETE FROM memories_fts 
                WHERE rowid IN (
                    SELECT rowid FROM {DatabaseTables.MEMORIES} 
                    WHERE {DatabaseColumns.ID} = ?
                )
            """, (memory_id,))
            
            self.connection.commit()
            
            if deleted_count > 0:
                logger.debug(f"成功刪除記憶記錄: {memory_id}")
                return True
            else:
                logger.warning(f"記憶記錄不存在: {memory_id}")
                return False
                
        except sqlite3.Error as e:
            logger.error(f"刪除記憶記錄失敗: {e}")
            raise DatabaseError(f"無法刪除記憶記錄: {e}", "MEMORY_DELETE_ERROR")
    
    async def search_memories(self, query: MemoryQuery) -> MemorySearchResult:
        """搜索記憶記錄"""
        start_time = time.time()
        
        try:
            cursor = self.connection.cursor()
            
            # 構建基礎查詢
            base_query = f"""
                SELECT DISTINCT m.{DatabaseColumns.ID}, m.{DatabaseColumns.CONTENT}, 
                       m.{DatabaseColumns.CONTEXT_TYPE}, m.{DatabaseColumns.TIMESTAMP},
                       m.{DatabaseColumns.RELEVANCE_SCORE}
                FROM {DatabaseTables.MEMORIES} m
            """
            
            conditions = []
            params = []
            
            # 全文搜索條件
            if query.query_text.strip():
                base_query += f" JOIN memories_fts fts ON m.rowid = fts.rowid"
                conditions.append("fts.content MATCH ?")
                params.append(query.query_text)
            
            # 時間範圍條件
            if query.time_range:
                conditions.append(f"m.{DatabaseColumns.TIMESTAMP} BETWEEN ? AND ?")
                params.extend([
                    query.time_range[0].isoformat(),
                    query.time_range[1].isoformat()
                ])
            
            # 上下文類型條件
            if query.context_types:
                type_placeholders = ','.join(['?' for _ in query.context_types])
                conditions.append(f"m.{DatabaseColumns.CONTEXT_TYPE} IN ({type_placeholders})")
                params.extend([str(ct) for ct in query.context_types])
            
            # 相關性分數條件
            conditions.append(f"m.{DatabaseColumns.RELEVANCE_SCORE} >= ?")
            params.append(query.min_relevance)
            
            # 標籤條件
            if query.tags:
                base_query += f" JOIN {DatabaseTables.MEMORY_TAGS} t ON m.{DatabaseColumns.ID} = t.{DatabaseColumns.MEMORY_ID}"
                tag_placeholders = ','.join(['?' for _ in query.tags])
                conditions.append(f"t.{DatabaseColumns.TAG} IN ({tag_placeholders})")
                params.extend(query.tags)
            
            # 組合查詢條件
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            # 排序和限制
            base_query += f" ORDER BY m.{DatabaseColumns.RELEVANCE_SCORE} DESC, m.{DatabaseColumns.TIMESTAMP} DESC"
            base_query += " LIMIT ?"
            params.append(query.limit)
            
            # 執行查詢
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            # 構建結果
            memories = []
            for row in rows:
                # 獲取標籤和元數據
                memory = await self.get_memory(row[0])
                if memory:
                    memories.append(memory)
            
            # 獲取總數（不含限制）
            count_query = base_query.replace(
                f"SELECT DISTINCT m.{DatabaseColumns.ID}, m.{DatabaseColumns.CONTENT}, "
                f"m.{DatabaseColumns.CONTEXT_TYPE}, m.{DatabaseColumns.TIMESTAMP}, "
                f"m.{DatabaseColumns.RELEVANCE_SCORE}",
                "SELECT COUNT(DISTINCT m.id)"
            ).split(" ORDER BY")[0]  # 移除排序和限制
            
            cursor.execute(count_query, params[:-1])  # 移除limit參數
            total_count = cursor.fetchone()[0]
            
            query_time = time.time() - start_time
            
            return MemorySearchResult(
                records=memories,
                total_count=total_count,
                query_time=query_time,
                relevance_scores=[m.relevance_score for m in memories]
            )
            
        except sqlite3.Error as e:
            logger.error(f"搜索記憶記錄失敗: {e}")
            raise DatabaseError(f"無法搜索記憶記錄: {e}", "MEMORY_SEARCH_ERROR")
    
    async def get_memories_by_type(
        self, 
        context_type: str, 
        limit: int = 10,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """根據類型獲取記憶記錄"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute(f"""
                SELECT {DatabaseColumns.ID}
                FROM {DatabaseTables.MEMORIES} 
                WHERE {DatabaseColumns.CONTEXT_TYPE} = ?
                ORDER BY {DatabaseColumns.TIMESTAMP} DESC
                LIMIT ? OFFSET ?
            """, (context_type, limit, offset))
            
            memory_ids = [row[0] for row in cursor.fetchall()]
            memories = []
            
            for memory_id in memory_ids:
                memory = await self.get_memory(memory_id)
                if memory:
                    memories.append(memory)
            
            return memories
            
        except sqlite3.Error as e:
            logger.error(f"根據類型獲取記憶失敗: {e}")
            raise DatabaseError(f"無法根據類型獲取記憶: {e}", "MEMORY_GET_BY_TYPE_ERROR")
    
    async def get_memories_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: int = 10,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """根據時間範圍獲取記憶記錄"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute(f"""
                SELECT {DatabaseColumns.ID}
                FROM {DatabaseTables.MEMORIES} 
                WHERE {DatabaseColumns.TIMESTAMP} BETWEEN ? AND ?
                ORDER BY {DatabaseColumns.TIMESTAMP} DESC
                LIMIT ? OFFSET ?
            """, (start_time.isoformat(), end_time.isoformat(), limit, offset))
            
            memory_ids = [row[0] for row in cursor.fetchall()]
            memories = []
            
            for memory_id in memory_ids:
                memory = await self.get_memory(memory_id)
                if memory:
                    memories.append(memory)
            
            return memories
            
        except sqlite3.Error as e:
            logger.error(f"根據時間範圍獲取記憶失敗: {e}")
            raise DatabaseError(f"無法根據時間範圍獲取記憶: {e}", "MEMORY_GET_BY_TIME_ERROR")
    
    async def get_memories_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        limit: int = 10,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """根據標籤獲取記憶記錄"""
        try:
            cursor = self.connection.cursor()
            
            if match_all:
                # 匹配所有標籤
                placeholders = ','.join(['?' for _ in tags])
                cursor.execute(f"""
                    SELECT m.{DatabaseColumns.ID}
                    FROM {DatabaseTables.MEMORIES} m
                    JOIN {DatabaseTables.MEMORY_TAGS} t ON m.{DatabaseColumns.ID} = t.{DatabaseColumns.MEMORY_ID}
                    WHERE t.{DatabaseColumns.TAG} IN ({placeholders})
                    GROUP BY m.{DatabaseColumns.ID}
                    HAVING COUNT(DISTINCT t.{DatabaseColumns.TAG}) = ?
                    ORDER BY m.{DatabaseColumns.TIMESTAMP} DESC
                    LIMIT ? OFFSET ?
                """, tags + [len(tags), limit, offset])
            else:
                # 匹配任意標籤
                placeholders = ','.join(['?' for _ in tags])
                cursor.execute(f"""
                    SELECT DISTINCT m.{DatabaseColumns.ID}
                    FROM {DatabaseTables.MEMORIES} m
                    JOIN {DatabaseTables.MEMORY_TAGS} t ON m.{DatabaseColumns.ID} = t.{DatabaseColumns.MEMORY_ID}
                    WHERE t.{DatabaseColumns.TAG} IN ({placeholders})
                    ORDER BY m.{DatabaseColumns.TIMESTAMP} DESC
                    LIMIT ? OFFSET ?
                """, tags + [limit, offset])
            
            memory_ids = [row[0] for row in cursor.fetchall()]
            memories = []
            
            for memory_id in memory_ids:
                memory = await self.get_memory(memory_id)
                if memory:
                    memories.append(memory)
            
            return memories
            
        except sqlite3.Error as e:
            logger.error(f"根據標籤獲取記憶失敗: {e}")
            raise DatabaseError(f"無法根據標籤獲取記憶: {e}", "MEMORY_GET_BY_TAGS_ERROR")
    
    async def get_statistics(self) -> MemoryStats:
        """獲取記憶系統統計信息"""
        try:
            cursor = self.connection.cursor()
            
            # 總記憶數量
            cursor.execute(f"SELECT COUNT(*) FROM {DatabaseTables.MEMORIES}")
            total_memories = cursor.fetchone()[0]
            
            # 按類型分組的記憶數量
            cursor.execute(f"""
                SELECT {DatabaseColumns.CONTEXT_TYPE}, COUNT(*) 
                FROM {DatabaseTables.MEMORIES} 
                GROUP BY {DatabaseColumns.CONTEXT_TYPE}
            """)
            memories_by_type = dict(cursor.fetchall())
            
            # 平均相關性分數
            cursor.execute(f"""
                SELECT AVG({DatabaseColumns.RELEVANCE_SCORE}) 
                FROM {DatabaseTables.MEMORIES}
            """)
            avg_relevance = cursor.fetchone()[0] or 0.0
            
            # 最舊和最新記憶時間
            cursor.execute(f"""
                SELECT MIN({DatabaseColumns.TIMESTAMP}), MAX({DatabaseColumns.TIMESTAMP}) 
                FROM {DatabaseTables.MEMORIES}
            """)
            oldest_str, newest_str = cursor.fetchone()
            
            oldest_memory = datetime.fromisoformat(oldest_str) if oldest_str else None
            newest_memory = datetime.fromisoformat(newest_str) if newest_str else None
            
            # 存儲大小（近似值）
            db_size = os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0.0
            
            return MemoryStats(
                total_memories=total_memories,
                memories_by_type=memories_by_type,
                average_relevance=avg_relevance,
                oldest_memory=oldest_memory,
                newest_memory=newest_memory,
                storage_size_mb=db_size
            )
            
        except sqlite3.Error as e:
            logger.error(f"獲取統計信息失敗: {e}")
            raise DatabaseError(f"無法獲取統計信息: {e}", "STATS_GET_ERROR")
    
    async def cleanup_old_memories(
        self,
        max_age_days: int,
        min_relevance: float = 0.0
    ) -> int:
        """清理舊的記憶記錄"""
        try:
            cursor = self.connection.cursor()
            cutoff_date = (datetime.now() - timedelta(days=max_age_days)).isoformat()
            
            cursor.execute(f"""
                DELETE FROM {DatabaseTables.MEMORIES} 
                WHERE {DatabaseColumns.TIMESTAMP} < ? 
                AND {DatabaseColumns.RELEVANCE_SCORE} < ?
            """, (cutoff_date, min_relevance))
            
            deleted_count = cursor.rowcount
            self.connection.commit()
            
            logger.info(f"清理了 {deleted_count} 條舊記憶記錄")
            return deleted_count
            
        except sqlite3.Error as e:
            logger.error(f"清理舊記憶失敗: {e}")
            raise DatabaseError(f"無法清理舊記憶: {e}", "CLEANUP_ERROR")
    
    async def optimize_storage(self) -> bool:
        """優化存儲性能"""
        try:
            cursor = self.connection.cursor()
            
            # 重建索引
            cursor.execute("REINDEX")
            
            # 清理數據庫
            cursor.execute("VACUUM")
            
            # 分析查詢計劃
            cursor.execute("ANALYZE")
            
            self.connection.commit()
            logger.info("存儲優化完成")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"存儲優化失敗: {e}")
            raise DatabaseError(f"無法優化存儲: {e}", "OPTIMIZE_ERROR")