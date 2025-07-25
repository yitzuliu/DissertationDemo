"""
記憶存儲異常類

定義記憶存儲操作中可能出現的各種異常。
"""

from typing import Optional, Any


class MemoryStorageError(Exception):
    """記憶存儲基礎異常類"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    ):
        """
        初始化存儲異常
        
        Args:
            message: 錯誤消息
            error_code: 錯誤代碼
            details: 錯誤詳情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details
    
    def __str__(self) -> str:
        """字符串表示"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConnectionError(MemoryStorageError):
    """存儲連接錯誤"""
    pass


class DatabaseError(MemoryStorageError):
    """數據庫操作錯誤"""
    pass


class ValidationError(MemoryStorageError):
    """數據驗證錯誤"""
    pass


class NotFoundError(MemoryStorageError):
    """記錄未找到錯誤"""
    pass


class DuplicateError(MemoryStorageError):
    """重複記錄錯誤"""
    pass


class PermissionError(MemoryStorageError):
    """權限錯誤"""
    pass


class StorageFullError(MemoryStorageError):
    """存儲空間不足錯誤"""
    pass


class CorruptionError(MemoryStorageError):
    """數據損壞錯誤"""
    pass


class TimeoutError(MemoryStorageError):
    """操作超時錯誤"""
    pass


class ConfigurationError(MemoryStorageError):
    """配置錯誤"""
    pass