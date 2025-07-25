"""
記憶系統配置管理器

負責加載、驗證和管理記憶系統的配置設置。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MemoryConfigManager:
    """記憶系統配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路徑，如果為None則使用默認路徑
        """
        self.config_path = config_path or self._get_default_config_path()
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """獲取默認配置文件路徑"""
        current_dir = Path(__file__).parent
        return str(current_dir / "memory_config.json")
    
    def _load_config(self) -> None:
        """加載配置文件"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"配置文件不存在: {self.config_path}，使用默認配置")
                self._config = self._get_default_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            
            # 驗證配置
            self._validate_config()
            logger.info(f"成功加載配置文件: {self.config_path}")
            
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式錯誤: {e}")
            self._config = self._get_default_config()
        except Exception as e:
            logger.error(f"加載配置文件失敗: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "storage": {
                "type": "sqlite",
                "database_path": "src/data/memory.db",
                "connection_pool_size": 5,
                "timeout": 30,
                "backup_enabled": True,
                "backup_interval_hours": 24
            },
            "processing": {
                "relevance_threshold": 0.3,
                "max_content_length": 10000,
                "auto_tagging_enabled": True,
                "deduplication_enabled": True,
                "similarity_threshold": 0.85
            },
            "retrieval": {
                "default_limit": 10,
                "max_limit": 100,
                "default_min_relevance": 0.5,
                "search_timeout": 5.0,
                "cache_enabled": True,
                "cache_ttl_seconds": 300
            },
            "cleanup": {
                "enabled": True,
                "max_age_days": 30,
                "max_total_memories": 10000,
                "cleanup_interval_hours": 6,
                "min_relevance_for_retention": 0.2
            },
            "logging": {
                "level": "INFO",
                "log_file": "src/logs/memory_system.log",
                "max_file_size_mb": 10,
                "backup_count": 5
            },
            "performance": {
                "batch_size": 100,
                "index_rebuild_interval_hours": 168,
                "vacuum_interval_hours": 72,
                "memory_usage_limit_mb": 500
            }
        }
    
    def _validate_config(self) -> None:
        """驗證配置的有效性"""
        required_sections = ["storage", "processing", "retrieval", "cleanup", "logging", "performance"]
        
        for section in required_sections:
            if section not in self._config:
                logger.warning(f"配置缺少必需的部分: {section}")
                self._config[section] = self._get_default_config()[section]
        
        # 驗證數值範圍
        self._validate_numeric_ranges()
    
    def _validate_numeric_ranges(self) -> None:
        """驗證數值配置的範圍"""
        validations = [
            ("processing.relevance_threshold", 0.0, 1.0),
            ("processing.similarity_threshold", 0.0, 1.0),
            ("retrieval.default_min_relevance", 0.0, 1.0),
            ("cleanup.min_relevance_for_retention", 0.0, 1.0),
            ("storage.connection_pool_size", 1, 50),
            ("retrieval.default_limit", 1, 1000),
            ("retrieval.max_limit", 1, 1000),
        ]
        
        for path, min_val, max_val in validations:
            value = self.get(path)
            if value is not None and not (min_val <= value <= max_val):
                logger.warning(f"配置值超出範圍 {path}: {value}, 應在 [{min_val}, {max_val}] 範圍內")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        獲取配置值
        
        Args:
            key: 配置鍵，支持點分隔的嵌套鍵（如 'storage.type'）
            default: 默認值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        設置配置值
        
        Args:
            key: 配置鍵，支持點分隔的嵌套鍵
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 導航到最後一級的父級
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 設置值
        config[keys[-1]] = value
        logger.debug(f"配置已更新: {key} = {value}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        獲取配置部分
        
        Args:
            section: 部分名稱
            
        Returns:
            配置部分字典
        """
        return self._config.get(section, {})
    
    def save_config(self, path: Optional[str] = None) -> None:
        """
        保存配置到文件
        
        Args:
            path: 保存路徑，如果為None則使用當前配置文件路徑
        """
        save_path = path or self.config_path
        
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到: {save_path}")
            
        except Exception as e:
            logger.error(f"保存配置文件失敗: {e}")
            raise
    
    def reload_config(self) -> None:
        """重新加載配置文件"""
        logger.info("重新加載配置文件")
        self._load_config()
    
    def get_all_config(self) -> Dict[str, Any]:
        """獲取完整配置"""
        return self._config.copy()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"MemoryConfigManager(config_path='{self.config_path}')"
    
    def __repr__(self) -> str:
        """詳細字符串表示"""
        return f"MemoryConfigManager(config_path='{self.config_path}', sections={list(self._config.keys())})"


# 全局配置管理器實例
memory_config = MemoryConfigManager()