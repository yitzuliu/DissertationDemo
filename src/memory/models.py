"""
記憶系統數據模型

定義記憶系統中使用的核心數據結構和類型。
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
import uuid


class MemoryType(str, Enum):
    """記憶類型枚舉"""
    SCREEN_OBSERVATION = "screen_observation"
    USER_INTERACTION = "user_interaction"
    SYSTEM_EVENT = "system_event"
    CHAT_CONTEXT = "chat_context"


class MemoryRecord(BaseModel):
    """記憶記錄數據模型"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="記憶唯一標識符")
    content: str = Field(..., description="記憶內容")
    context_type: MemoryType = Field(..., description="上下文類型")
    timestamp: datetime = Field(default_factory=datetime.now, description="創建時間戳")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元數據")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="相關性分數")
    tags: List[str] = Field(default_factory=list, description="標籤列表")
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v):
        """驗證內容不為空"""
        if not v or not v.strip():
            raise ValueError('記憶內容不能為空')
        return v.strip()
    
    @field_validator('tags')
    @classmethod
    def tags_lowercase(cls, v):
        """將標籤轉換為小寫"""
        return [tag.lower().strip() for tag in v if tag.strip()]
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class MemoryQuery(BaseModel):
    """記憶查詢數據模型"""
    
    query_text: str = Field(..., description="查詢文本")
    time_range: Optional[Tuple[datetime, datetime]] = Field(None, description="時間範圍")
    context_types: List[MemoryType] = Field(default_factory=list, description="上下文類型過濾")
    limit: int = Field(default=10, ge=1, le=100, description="結果數量限制")
    min_relevance: float = Field(default=0.5, ge=0.0, le=1.0, description="最小相關性閾值")
    tags: List[str] = Field(default_factory=list, description="標籤過濾")
    
    @field_validator('query_text')
    @classmethod
    def query_not_empty(cls, v):
        """驗證查詢文本不為空"""
        if not v or not v.strip():
            raise ValueError('查詢文本不能為空')
        return v.strip()
    
    @field_validator('time_range')
    @classmethod
    def validate_time_range(cls, v):
        """驗證時間範圍"""
        if v is not None:
            start_time, end_time = v
            if start_time >= end_time:
                raise ValueError('開始時間必須早於結束時間')
        return v
    
    @field_validator('tags')
    @classmethod
    def tags_lowercase(cls, v):
        """將標籤轉換為小寫"""
        return [tag.lower().strip() for tag in v if tag.strip()]
    
    model_config = ConfigDict(use_enum_values=True)


class MemoryContext(BaseModel):
    """記憶上下文數據模型"""
    
    current_activity: str = Field(default="", description="當前活動")
    recent_interactions: List[str] = Field(default_factory=list, description="最近互動")
    active_applications: List[str] = Field(default_factory=list, description="活動應用程序")
    user_focus_area: str = Field(default="", description="用戶關注區域")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="會話ID")
    last_updated: datetime = Field(default_factory=datetime.now, description="最後更新時間")
    
    @field_validator('recent_interactions')
    @classmethod
    def limit_recent_interactions(cls, v):
        """限制最近互動的數量"""
        return v[-10:] if len(v) > 10 else v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class MemorySearchResult(BaseModel):
    """記憶搜索結果數據模型"""
    
    records: List[MemoryRecord] = Field(..., description="匹配的記憶記錄")
    total_count: int = Field(..., description="總匹配數量")
    query_time: float = Field(..., description="查詢耗時（秒）")
    relevance_scores: List[float] = Field(default_factory=list, description="相關性分數列表")
    
    @field_validator('relevance_scores')
    @classmethod
    def scores_match_records(cls, v, info):
        """驗證相關性分數與記錄數量匹配"""
        if info.data and 'records' in info.data and len(v) != len(info.data['records']):
            raise ValueError('相關性分數數量必須與記錄數量匹配')
        return v


class MemoryStats(BaseModel):
    """記憶系統統計數據模型"""
    
    total_memories: int = Field(default=0, description="總記憶數量")
    memories_by_type: Dict[str, int] = Field(default_factory=dict, description="按類型分組的記憶數量")
    average_relevance: float = Field(default=0.0, description="平均相關性分數")
    oldest_memory: Optional[datetime] = Field(None, description="最舊記憶時間")
    newest_memory: Optional[datetime] = Field(None, description="最新記憶時間")
    storage_size_mb: float = Field(default=0.0, description="存儲大小（MB）")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )