"""
AI Manual Assistant 記憶系統

這個模組提供持續觀察和上下文記憶功能，實現雙軌架構：
1. 持續觀察軌道：VLM基於螢幕觀察和處理
2. 記憶存儲軌道：上下文信息存儲和檢索
"""

from .models import MemoryRecord, MemoryQuery, MemoryContext, MemoryType
from .storage import MemoryStorage, ChromaMemoryStorage

__version__ = "1.0.0"
__author__ = "AI Manual Assistant Team"

__all__ = [
    "MemoryRecord",
    "MemoryQuery", 
    "MemoryContext",
    "MemoryType",
    "MemoryStorage",
    "ChromaMemoryStorage"
]