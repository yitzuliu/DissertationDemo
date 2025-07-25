"""
記憶系統常數定義

定義記憶系統中使用的常數和枚舉值。
"""

from enum import Enum


class MemoryConstants:
    """記憶系統常數"""
    
    # 版本信息
    VERSION = "1.0.0"
    
    # 數據庫相關
    DEFAULT_DB_NAME = "memory.db"
    DEFAULT_DB_PATH = "src/data/memory.db"
    
    # 內容限制
    MAX_CONTENT_LENGTH = 10000
    MAX_TAG_LENGTH = 50
    MAX_TAGS_PER_RECORD = 20
    
    # 相關性分數
    MIN_RELEVANCE_SCORE = 0.0
    MAX_RELEVANCE_SCORE = 1.0
    DEFAULT_RELEVANCE_THRESHOLD = 0.3
    
    # 查詢限制
    DEFAULT_QUERY_LIMIT = 10
    MAX_QUERY_LIMIT = 100
    MIN_QUERY_LIMIT = 1
    
    # 時間相關（秒）
    DEFAULT_CACHE_TTL = 300  # 5分鐘
    DEFAULT_SEARCH_TIMEOUT = 5.0
    DEFAULT_CONNECTION_TIMEOUT = 30.0
    
    # 清理相關
    DEFAULT_MAX_AGE_DAYS = 30
    DEFAULT_MAX_TOTAL_MEMORIES = 10000
    DEFAULT_CLEANUP_INTERVAL_HOURS = 6
    
    # 性能相關
    DEFAULT_BATCH_SIZE = 100
    DEFAULT_CONNECTION_POOL_SIZE = 5
    DEFAULT_MEMORY_LIMIT_MB = 500
    
    # 日誌相關
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_LOG_FILE = "src/logs/memory_system.log"
    DEFAULT_MAX_LOG_SIZE_MB = 10
    DEFAULT_LOG_BACKUP_COUNT = 5


class ErrorCodes:
    """錯誤代碼"""
    
    # 通用錯誤
    UNKNOWN_ERROR = "MEMORY_E001"
    INVALID_INPUT = "MEMORY_E002"
    CONFIGURATION_ERROR = "MEMORY_E003"
    
    # 存儲錯誤
    STORAGE_CONNECTION_ERROR = "MEMORY_E101"
    STORAGE_WRITE_ERROR = "MEMORY_E102"
    STORAGE_READ_ERROR = "MEMORY_E103"
    STORAGE_DELETE_ERROR = "MEMORY_E104"
    DATABASE_CORRUPTION = "MEMORY_E105"
    
    # 處理錯誤
    PROCESSING_ERROR = "MEMORY_E201"
    CONTENT_TOO_LONG = "MEMORY_E202"
    INVALID_MEMORY_TYPE = "MEMORY_E203"
    TAGGING_ERROR = "MEMORY_E204"
    
    # 檢索錯誤
    SEARCH_ERROR = "MEMORY_E301"
    SEARCH_TIMEOUT = "MEMORY_E302"
    INVALID_QUERY = "MEMORY_E303"
    NO_RESULTS_FOUND = "MEMORY_E304"
    
    # 整合錯誤
    VLM_INTEGRATION_ERROR = "MEMORY_E401"
    FRONTEND_INTEGRATION_ERROR = "MEMORY_E402"
    API_ERROR = "MEMORY_E403"
    
    # 系統錯誤
    MEMORY_LIMIT_EXCEEDED = "MEMORY_E501"
    DISK_SPACE_ERROR = "MEMORY_E502"
    PERMISSION_ERROR = "MEMORY_E503"


class LogMessages:
    """日誌消息模板"""
    
    # 系統啟動/關閉
    SYSTEM_STARTING = "記憶系統正在啟動..."
    SYSTEM_STARTED = "記憶系統已成功啟動"
    SYSTEM_STOPPING = "記憶系統正在關閉..."
    SYSTEM_STOPPED = "記憶系統已關閉"
    
    # 存儲操作
    MEMORY_STORED = "記憶已存儲: ID={id}, 類型={type}"
    MEMORY_RETRIEVED = "記憶已檢索: 查詢='{query}', 結果數={count}"
    MEMORY_DELETED = "記憶已刪除: ID={id}"
    MEMORY_UPDATED = "記憶已更新: ID={id}"
    
    # 清理操作
    CLEANUP_STARTED = "記憶清理已開始"
    CLEANUP_COMPLETED = "記憶清理已完成: 刪除了{count}條記憶"
    
    # 錯誤消息
    STORAGE_ERROR = "存儲操作失敗: {error}"
    PROCESSING_ERROR = "處理操作失敗: {error}"
    SEARCH_ERROR = "搜索操作失敗: {error}"
    
    # 性能消息
    PERFORMANCE_WARNING = "性能警告: {metric}={value}, 閾值={threshold}"
    MEMORY_USAGE_HIGH = "記憶體使用率過高: {usage}MB / {limit}MB"


class DatabaseTables:
    """數據庫表名"""
    
    MEMORIES = "memories"
    MEMORY_TAGS = "memory_tags"
    MEMORY_METADATA = "memory_metadata"
    SYSTEM_INFO = "system_info"
    PERFORMANCE_METRICS = "performance_metrics"


class DatabaseColumns:
    """數據庫列名"""
    
    # memories表
    ID = "id"
    CONTENT = "content"
    CONTEXT_TYPE = "context_type"
    TIMESTAMP = "timestamp"
    RELEVANCE_SCORE = "relevance_score"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    
    # memory_tags表
    MEMORY_ID = "memory_id"
    TAG = "tag"
    
    # memory_metadata表
    KEY = "key"
    VALUE = "value"
    
    # system_info表
    VERSION = "version"
    LAST_CLEANUP = "last_cleanup"
    TOTAL_MEMORIES = "total_memories"
    
    # performance_metrics表
    METRIC_NAME = "metric_name"
    METRIC_VALUE = "metric_value"
    RECORDED_AT = "recorded_at"


class CacheKeys:
    """緩存鍵前綴"""
    
    MEMORY_RECORD = "memory:record:"
    SEARCH_RESULT = "memory:search:"
    MEMORY_STATS = "memory:stats"
    SYSTEM_INFO = "memory:system_info"
    USER_CONTEXT = "memory:context:"


class EventTypes:
    """事件類型"""
    
    MEMORY_CREATED = "memory.created"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_DELETED = "memory.deleted"
    MEMORY_SEARCHED = "memory.searched"
    CLEANUP_COMPLETED = "cleanup.completed"
    SYSTEM_ERROR = "system.error"