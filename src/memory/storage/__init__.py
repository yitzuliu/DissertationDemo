"""
記憶存儲模組

提供記憶系統的存儲接口和實現，支持多種存儲後端。
"""

from .base import BaseMemoryStorage
from .chroma_storage import ChromaMemoryStorage
from .sqlite_storage import SQLiteMemoryStorage
from .exceptions import (
    MemoryStorageError, ConnectionError, DatabaseError,
    ValidationError, NotFoundError, DuplicateError,
    PermissionError, StorageFullError, CorruptionError,
    TimeoutError, ConfigurationError
)

# 默認使用ChromaDB存儲（適合本地設備）
MemoryStorage = ChromaMemoryStorage

__all__ = [
    "BaseMemoryStorage",
    "ChromaMemoryStorage",
    "SQLiteMemoryStorage", 
    "MemoryStorage",  # 默認存儲
    "MemoryStorageError",
    "ConnectionError", 
    "DatabaseError",
    "ValidationError",
    "NotFoundError",
    "DuplicateError",
    "PermissionError",
    "StorageFullError",
    "CorruptionError",
    "TimeoutError",
    "ConfigurationError"
]