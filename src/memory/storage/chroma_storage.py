"""
ChromaDB記憶存儲實現

基於ChromaDB向量數據庫的記憶存儲實現，提供語義搜索和RAG功能。
適合本地設備的記憶體限制環境。
"""

import chromadb
from chromadb.config import Settings
import logging
import os
import time
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from sentence_transformers import SentenceTransformer

from .base import BaseMemoryStorage
from .exceptions import (
    ConnectionError, DatabaseError, NotFoundError, 
    ValidationError, CorruptionError
)
from ..models import MemoryRecord, MemoryQuery, MemorySearchResult, MemoryStats, MemoryType
from ..constants import MemoryConstants

logger = logging.getLogger(__name__)


class ChromaMemoryStorage(BaseMemoryStorage):
    """ChromaDB記憶存儲實現"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化ChromaDB存儲
        
        Args:
            config: 存儲配置
        """
        super().__init__(config)
        
        # 配置參數
        self.persist_directory = config.get("persist_directory", "src/data/chroma_db")
        self.collection_name = config.get("collection_name", "memory_collection")
        self.embedding_model_name = config.get("embedding_model", "all-MiniLM-L6-v2")
        self.max_memories = config.get("max_memories", 10000)  # 記憶體限制
        
        # ChromaDB客戶端和集合
        self.client: Optional[chromadb.Client] = None
        self.collection: Optional[chromadb.Collection] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        
        # 確保持久化目錄存在
        os.makedirs(self.persist_directory, exist_ok=True)
    
    async def connect(self) -> bool:
        """連接到ChromaDB"""
        try:
            # 初始化ChromaDB客戶端（本地持久化）
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,  # 禁用遙測
                    allow_reset=True
                )
            )
            
            # 初始化嵌入模型（輕量級模型適合本地設備）
            logger.info(f"正在加載嵌入模型: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # 獲取或創建集合
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"已連接到現有集合: {self.collection_name}")
            except Exception:
                # 集合不存在，創建新集合
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "AI Manual Assistant 記憶存儲"}
                )
                logger.info(f"已創建新集合: {self.collection_name}")
            
            self._is_connected = True
            logger.info(f"成功連接到ChromaDB: {self.persist_directory}")
            return True
            
        except Exception as e:
            logger.error(f"連接ChromaDB失敗: {e}")
            raise ConnectionError(f"無法連接到ChromaDB: {e}", "CHROMA_CONNECTION_ERROR")
    
    async def disconnect(self) -> bool:
        """斷開ChromaDB連接"""
        try:
            # ChromaDB會自動持久化，無需特殊斷開操作
            self.client = None
            self.collection = None
            self.embedding_model = None
            
            self._is_connected = False
            logger.info("已斷開ChromaDB連接")
            return True
            
        except Exception as e:
            logger.error(f"斷開ChromaDB連接失敗: {e}")
            return False
    
    def _generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        try:
            if not self.embedding_model:
                raise ValueError("嵌入模型未初始化")
            
            # 生成嵌入向量
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"生成嵌入向量失敗: {e}")
            raise DatabaseError(f"無法生成嵌入向量: {e}", "EMBEDDING_ERROR")
    
    def _memory_to_document(self, memory: MemoryRecord) -> Dict[str, Any]:
        """將記憶記錄轉換為ChromaDB文檔格式"""
        return {
            "id": memory.id,
            "document": memory.content,
            "embedding": self._generate_embedding(memory.content),
            "metadata": {
                "context_type": memory.context_type,
                "timestamp": memory.timestamp.isoformat(),
                "relevance_score": memory.relevance_score,
                "tags": ",".join(memory.tags),  # 將標籤列表轉為字符串
                "metadata_json": json.dumps(memory.metadata) if memory.metadata else "{}"
            }
        }
    
    def _document_to_memory(self, doc_id: str, document: str, metadata: Dict[str, Any]) -> MemoryRecord:
        """將ChromaDB文檔轉換為記憶記錄"""
        try:
            # 解析標籤
            tags = metadata.get("tags", "").split(",") if metadata.get("tags") else []
            tags = [tag.strip() for tag in tags if tag.strip()]
            
            # 解析元數據
            metadata_json = metadata.get("metadata_json", "{}")
            try:
                parsed_metadata = json.loads(metadata_json) if metadata_json and metadata_json != "{}" else {}
            except (json.JSONDecodeError, TypeError):
                parsed_metadata = {}
            
            return MemoryRecord(
                id=doc_id,
                content=document,
                context_type=MemoryType(metadata.get("context_type", "screen_observation")),
                timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat())),
                relevance_score=float(metadata.get("relevance_score", 0.0)),
                tags=tags,
                metadata=parsed_metadata
            )
            
        except Exception as e:
            logger.error(f"轉換文檔為記憶記錄失敗: {e}")
            raise DatabaseError(f"無法轉換文檔: {e}", "DOCUMENT_CONVERSION_ERROR")
    
    async def create_memory(self, memory: MemoryRecord) -> str:
        """創建新的記憶記錄"""
        try:
            # 檢查記憶體數量限制
            current_count = self.collection.count()
            if current_count >= self.max_memories:
                # 自動清理最舊的記憶
                await self._cleanup_oldest_memories(int(self.max_memories * 0.1))  # 清理10%
            
            # 轉換為ChromaDB格式
            doc = self._memory_to_document(memory)
            
            # 添加到集合
            self.collection.add(
                ids=[doc["id"]],
                documents=[doc["document"]],
                embeddings=[doc["embedding"]],
                metadatas=[doc["metadata"]]
            )
            
            logger.debug(f"成功創建記憶記錄: {memory.id}")
            return memory.id
            
        except Exception as e:
            logger.error(f"創建記憶記錄失敗: {e}")
            raise DatabaseError(f"無法創建記憶記錄: {e}", "MEMORY_CREATE_ERROR")
    
    async def get_memory(self, memory_id: str) -> Optional[MemoryRecord]:
        """根據ID獲取記憶記錄"""
        try:
            # 從集合中獲取
            result = self.collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"]
            )
            
            if not result["ids"] or len(result["ids"]) == 0:
                return None
            
            # 轉換為記憶記錄
            doc_id = result["ids"][0]
            document = result["documents"][0]
            metadata = result["metadatas"][0]
            
            return self._document_to_memory(doc_id, document, metadata)
            
        except Exception as e:
            logger.error(f"獲取記憶記錄失敗: {e}")
            raise DatabaseError(f"無法獲取記憶記錄: {e}", "MEMORY_GET_ERROR")
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """更新記憶記錄"""
        try:
            # 先獲取現有記憶
            existing_memory = await self.get_memory(memory_id)
            if not existing_memory:
                raise NotFoundError(f"記憶記錄不存在: {memory_id}", "MEMORY_NOT_FOUND")
            
            # 應用更新
            for field, value in updates.items():
                if hasattr(existing_memory, field):
                    setattr(existing_memory, field, value)
            
            # 刪除舊記錄
            self.collection.delete(ids=[memory_id])
            
            # 創建更新後的記錄
            await self.create_memory(existing_memory)
            
            logger.debug(f"成功更新記憶記錄: {memory_id}")
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新記憶記錄失敗: {e}")
            raise DatabaseError(f"無法更新記憶記錄: {e}", "MEMORY_UPDATE_ERROR")
    
    async def delete_memory(self, memory_id: str) -> bool:
        """刪除記憶記錄"""
        try:
            # 檢查記錄是否存在
            existing = await self.get_memory(memory_id)
            if not existing:
                logger.warning(f"記憶記錄不存在: {memory_id}")
                return False
            
            # 從集合中刪除
            self.collection.delete(ids=[memory_id])
            
            logger.debug(f"成功刪除記憶記錄: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"刪除記憶記錄失敗: {e}")
            raise DatabaseError(f"無法刪除記憶記錄: {e}", "MEMORY_DELETE_ERROR")
    
    async def search_memories(self, query: MemoryQuery) -> MemorySearchResult:
        """搜索記憶記錄（語義搜索）"""
        start_time = time.time()
        
        try:
            # 生成查詢嵌入
            query_embedding = self._generate_embedding(query.query_text)
            
            # 構建過濾條件
            where_conditions = {}
            
            # 時間範圍過濾
            if query.time_range:
                # ChromaDB的時間過濾需要特殊處理
                # 這裡我們先獲取所有結果，然後在Python中過濾
                pass
            
            # 上下文類型過濾
            if query.context_types:
                where_conditions["context_type"] = {"$in": [str(ct) for ct in query.context_types]}
            
            # 執行向量搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(query.limit, 100),  # 限制結果數量
                where=where_conditions if where_conditions else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # 轉換結果
            memories = []
            relevance_scores = []
            
            if results["ids"] and len(results["ids"]) > 0:
                for i, doc_id in enumerate(results["ids"][0]):
                    document = results["documents"][0][i]
                    metadata = results["metadatas"][0][i]
                    distance = results["distances"][0][i]
                    
                    # 將距離轉換為相關性分數（距離越小，相關性越高）
                    # ChromaDB使用餘弦距離，我們使用更保守的計算
                    # 確保只有真正相關的內容才會被返回
                    relevance = max(0.0, 1.0 - distance)
                    
                    # 應用相關性過濾
                    if relevance >= query.min_relevance:
                        memory = self._document_to_memory(doc_id, document, metadata)
                        
                        # 時間範圍過濾（在Python中進行）
                        if query.time_range:
                            if not (query.time_range[0] <= memory.timestamp <= query.time_range[1]):
                                continue
                        
                        # 標籤過濾
                        if query.tags:
                            if not any(tag in memory.tags for tag in query.tags):
                                continue
                        
                        memories.append(memory)
                        relevance_scores.append(relevance)
            
            # 按相關性排序
            if memories:
                sorted_pairs = sorted(zip(memories, relevance_scores), key=lambda x: x[1], reverse=True)
                memories, relevance_scores = zip(*sorted_pairs)
                memories = list(memories)
                relevance_scores = list(relevance_scores)
            
            query_time = time.time() - start_time
            
            return MemorySearchResult(
                records=memories[:query.limit],
                total_count=len(memories),
                query_time=query_time,
                relevance_scores=relevance_scores[:query.limit]
            )
            
        except Exception as e:
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
            # ChromaDB不直接支持offset，我們獲取更多結果然後切片
            results = self.collection.get(
                where={"context_type": context_type},
                limit=limit + offset,
                include=["documents", "metadatas"]
            )
            
            memories = []
            if results["ids"]:
                for i, doc_id in enumerate(results["ids"]):
                    if i < offset:
                        continue
                    if len(memories) >= limit:
                        break
                    
                    document = results["documents"][i]
                    metadata = results["metadatas"][i]
                    memory = self._document_to_memory(doc_id, document, metadata)
                    memories.append(memory)
            
            # 按時間排序
            memories.sort(key=lambda x: x.timestamp, reverse=True)
            return memories
            
        except Exception as e:
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
            # 獲取所有記憶，然後在Python中過濾時間範圍
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
            
            memories = []
            if results["ids"]:
                for i, doc_id in enumerate(results["ids"]):
                    document = results["documents"][i]
                    metadata = results["metadatas"][i]
                    memory = self._document_to_memory(doc_id, document, metadata)
                    
                    # 時間範圍過濾
                    if start_time <= memory.timestamp <= end_time:
                        memories.append(memory)
            
            # 按時間排序
            memories.sort(key=lambda x: x.timestamp, reverse=True)
            
            # 應用offset和limit
            return memories[offset:offset + limit]
            
        except Exception as e:
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
            # 獲取所有記憶，然後在Python中過濾標籤
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
            
            memories = []
            if results["ids"]:
                for i, doc_id in enumerate(results["ids"]):
                    document = results["documents"][i]
                    metadata = results["metadatas"][i]
                    memory = self._document_to_memory(doc_id, document, metadata)
                    
                    # 標籤過濾
                    if match_all:
                        # 匹配所有標籤
                        if all(tag in memory.tags for tag in tags):
                            memories.append(memory)
                    else:
                        # 匹配任意標籤
                        if any(tag in memory.tags for tag in tags):
                            memories.append(memory)
            
            # 按時間排序
            memories.sort(key=lambda x: x.timestamp, reverse=True)
            
            # 應用offset和limit
            return memories[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"根據標籤獲取記憶失敗: {e}")
            raise DatabaseError(f"無法根據標籤獲取記憶: {e}", "MEMORY_GET_BY_TAGS_ERROR")
    
    async def get_statistics(self) -> MemoryStats:
        """獲取記憶系統統計信息"""
        try:
            # 獲取所有記憶的元數據
            results = self.collection.get(
                include=["metadatas"]
            )
            
            total_memories = len(results["ids"]) if results["ids"] else 0
            
            # 統計各類型記憶數量
            memories_by_type = {}
            relevance_scores = []
            timestamps = []
            
            if results["metadatas"]:
                for metadata in results["metadatas"]:
                    context_type = metadata.get("context_type", "unknown")
                    memories_by_type[context_type] = memories_by_type.get(context_type, 0) + 1
                    
                    relevance_score = float(metadata.get("relevance_score", 0.0))
                    relevance_scores.append(relevance_score)
                    
                    timestamp_str = metadata.get("timestamp")
                    if timestamp_str:
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str)
                            timestamps.append(timestamp)
                        except ValueError:
                            pass
            
            # 計算統計值
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
            oldest_memory = min(timestamps) if timestamps else None
            newest_memory = max(timestamps) if timestamps else None
            
            # 估算存儲大小（ChromaDB目錄大小）
            storage_size_mb = 0.0
            try:
                for root, dirs, files in os.walk(self.persist_directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        storage_size_mb += os.path.getsize(file_path)
                storage_size_mb = storage_size_mb / (1024 * 1024)  # 轉換為MB
            except Exception:
                pass
            
            return MemoryStats(
                total_memories=total_memories,
                memories_by_type=memories_by_type,
                average_relevance=avg_relevance,
                oldest_memory=oldest_memory,
                newest_memory=newest_memory,
                storage_size_mb=storage_size_mb
            )
            
        except Exception as e:
            logger.error(f"獲取統計信息失敗: {e}")
            raise DatabaseError(f"無法獲取統計信息: {e}", "STATS_GET_ERROR")
    
    async def cleanup_old_memories(
        self,
        max_age_days: int,
        min_relevance: float = 0.0
    ) -> int:
        """清理舊的記憶記錄"""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # 獲取所有記憶
            results = self.collection.get(
                include=["metadatas"]
            )
            
            ids_to_delete = []
            
            if results["ids"] and results["metadatas"]:
                for i, doc_id in enumerate(results["ids"]):
                    metadata = results["metadatas"][i]
                    
                    # 檢查時間和相關性
                    timestamp_str = metadata.get("timestamp")
                    relevance_score = float(metadata.get("relevance_score", 0.0))
                    
                    if timestamp_str:
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str)
                            if timestamp < cutoff_date and relevance_score < min_relevance:
                                ids_to_delete.append(doc_id)
                        except ValueError:
                            pass
            
            # 批量刪除
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
            
            deleted_count = len(ids_to_delete)
            logger.info(f"清理了 {deleted_count} 條舊記憶記錄")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理舊記憶失敗: {e}")
            raise DatabaseError(f"無法清理舊記憶: {e}", "CLEANUP_ERROR")
    
    async def _cleanup_oldest_memories(self, count: int) -> int:
        """清理最舊的記憶記錄（內部方法）"""
        try:
            # 獲取所有記憶
            results = self.collection.get(
                include=["metadatas"]
            )
            
            if not results["ids"]:
                return 0
            
            # 按時間排序，找出最舊的記憶
            memory_times = []
            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i]
                timestamp_str = metadata.get("timestamp")
                
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        memory_times.append((doc_id, timestamp))
                    except ValueError:
                        pass
            
            # 按時間排序
            memory_times.sort(key=lambda x: x[1])
            
            # 選擇要刪除的記憶
            ids_to_delete = [item[0] for item in memory_times[:count]]
            
            # 批量刪除
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
            
            deleted_count = len(ids_to_delete)
            logger.info(f"清理了 {deleted_count} 條最舊的記憶記錄")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理最舊記憶失敗: {e}")
            return 0
    
    async def optimize_storage(self) -> bool:
        """優化存儲性能"""
        try:
            # ChromaDB會自動優化，這裡我們可以執行一些維護操作
            
            # 獲取當前統計信息
            stats = await self.get_statistics()
            logger.info(f"存儲優化前統計: 總記憶數={stats.total_memories}, 存儲大小={stats.storage_size_mb:.2f}MB")
            
            # 如果記憶數量超過限制，清理一些舊記憶
            if stats.total_memories > self.max_memories:
                cleanup_count = stats.total_memories - self.max_memories
                await self._cleanup_oldest_memories(cleanup_count)
            
            logger.info("存儲優化完成")
            return True
            
        except Exception as e:
            logger.error(f"存儲優化失敗: {e}")
            raise DatabaseError(f"無法優化存儲: {e}", "OPTIMIZE_ERROR")