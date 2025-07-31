"""
AI Manual Assistant 日誌系統核心管理器

提供統一的日誌管理功能，支援多種日誌類型和唯一ID追蹤機制。
"""

import logging
import uuid
import time
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum
import os


class LogType(Enum):
    """日誌類型枚舉"""
    SYSTEM = "system"
    VISUAL = "visual" 
    USER = "user"
    FLOW_TRACKING = "flow_tracking"


class LogManager:
    """
    統一日誌管理器
    
    負責管理所有類型的日誌記錄，提供唯一ID生成和統一格式化功能。
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        初始化日誌管理器
        
        Args:
            log_dir: 日誌目錄路徑
        """
        self.log_dir = log_dir
        self.loggers: Dict[LogType, logging.Logger] = {}
        self._ensure_log_directory()
        self._setup_loggers()
    
    def _ensure_log_directory(self):
        """確保日誌目錄存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _setup_loggers(self):
        """設置各類型日誌記錄器"""
        for log_type in LogType:
            logger = logging.getLogger(f"ai_assistant_{log_type.value}")
            logger.setLevel(logging.INFO)
            
            # 創建檔案處理器
            today = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(self.log_dir, f"{log_type.value}_{today}.log")
            
            handler = logging.FileHandler(log_file, encoding='utf-8')
            handler.setLevel(logging.INFO)
            
            # 設定統一格式
            formatter = logging.Formatter(
                '%(asctime)s,%(msecs)03d [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            logger.addHandler(handler)
            self.loggers[log_type] = logger    

    # 唯一ID生成方法
    def generate_observation_id(self) -> str:
        """生成觀察事件唯一ID"""
        timestamp = int(time.time() * 1000)
        return f"obs_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_query_id(self) -> str:
        """生成查詢事件唯一ID"""
        timestamp = int(time.time() * 1000)
        return f"query_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_request_id(self) -> str:
        """生成請求唯一ID"""
        timestamp = int(time.time() * 1000)
        return f"req_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_state_update_id(self) -> str:
        """生成狀態更新唯一ID"""
        timestamp = int(time.time() * 1000)
        return f"state_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_flow_id(self) -> str:
        """生成流程唯一ID"""
        timestamp = int(time.time() * 1000)
        return f"flow_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def _format_log_message(self, event_type: str, **kwargs) -> str:
        """
        格式化日誌訊息
        
        Args:
            event_type: 事件類型
            **kwargs: 日誌參數
            
        Returns:
            格式化的日誌訊息
        """
        parts = [f"[{event_type}]"]
        
        for key, value in kwargs.items():
            if value is not None:
                parts.append(f"{key}={value}")
        
        return " ".join(parts)
    
    # 系統日誌記錄方法
    def log_system_start(self, system_id: str, host: str, port: int, model: str):
        """記錄系統啟動"""
        message = self._format_log_message(
            "SYSTEM_START",
            system_id=system_id,
            host=host,
            port=port,
            model=model
        )
        self.loggers[LogType.SYSTEM].info(message) 
   
    def log_system_shutdown(self, system_id: str, final_memory: str, uptime: str):
        """記錄系統關閉"""
        message = self._format_log_message(
            "SYSTEM_SHUTDOWN",
            system_id=system_id,
            final_memory=final_memory,
            uptime=uptime
        )
        self.loggers[LogType.SYSTEM].info(message)
    
    def log_memory_usage(self, system_id: str, memory_usage: str):
        """記錄記憶體使用"""
        message = self._format_log_message(
            "MEMORY",
            system_id=system_id,
            memory_usage=memory_usage
        )
        self.loggers[LogType.SYSTEM].info(message)
    
    def log_endpoint_call(self, request_id: str, method: str, path: str, 
                         status: int, duration: float):
        """記錄端點呼叫"""
        message = self._format_log_message(
            "ENDPOINT",
            request_id=request_id,
            method=method,
            path=path,
            status=status,
            duration=f"{duration:.2f}s"
        )
        self.loggers[LogType.SYSTEM].info(message)
    
    # 視覺日誌記錄方法
    def log_eyes_capture(self, observation_id: str, request_id: str, 
                        device: str, resolution: str, quality: float, 
                        format: str, size: str):
        """記錄圖像捕獲"""
        message = self._format_log_message(
            "EYES_CAPTURE",
            observation_id=observation_id,
            request_id=request_id,
            device=device,
            resolution=resolution,
            quality=quality,
            format=format,
            size=size
        )
        self.loggers[LogType.VISUAL].info(message)  
  
    def log_eyes_prompt(self, observation_id: str, prompt: str, length: int):
        """記錄視覺提示詞"""
        message = self._format_log_message(
            "EYES_PROMPT",
            observation_id=observation_id,
            prompt=f'"{prompt}"',
            length=f"{length} chars"
        )
        self.loggers[LogType.VISUAL].info(message)
    
    def log_eyes_transfer(self, observation_id: str, sent_data: Dict[str, Any]):
        """記錄後端傳輸"""
        message = self._format_log_message(
            "EYES_TRANSFER",
            observation_id=observation_id,
            sent_to_backend=str(sent_data)
        )
        self.loggers[LogType.VISUAL].info(message)
    
    def log_rag_matching(self, observation_id: str, vlm_observation: str, 
                        candidate_steps: list, similarities: list):
        """記錄RAG匹配過程"""
        message = self._format_log_message(
            "RAG_MATCHING",
            observation_id=observation_id,
            vlm_observation=f'"{vlm_observation}"',
            candidate_steps=str(candidate_steps),
            similarities=str(similarities)
        )
        self.loggers[LogType.VISUAL].info(message)
    
    def log_rag_result(self, observation_id: str, selected: str, 
                      title: str, similarity: float):
        """記錄RAG匹配結果"""
        message = self._format_log_message(
            "RAG_RESULT",
            observation_id=observation_id,
            selected=selected,
            title=f'"{title}"',
            similarity=similarity
        )
        self.loggers[LogType.VISUAL].info(message)
    
    def log_state_tracker(self, observation_id: str, state_update_id: str,
                         confidence: float, action: str, state: Dict[str, Any]):
        """記錄狀態追蹤器決策"""
        message = self._format_log_message(
            "STATE_TRACKER",
            observation_id=observation_id,
            state_update_id=state_update_id,
            confidence=confidence,
            action=action,
            state=str(state)
        )
        self.loggers[LogType.VISUAL].info(message)    
 
   # 使用者查詢日誌記錄方法
    def log_user_query(self, query_id: str, request_id: str, question: str, 
                      language: str, used_observation_id: Optional[str] = None):
        """記錄使用者查詢"""
        message = self._format_log_message(
            "USER_QUERY",
            query_id=query_id,
            request_id=request_id,
            question=f'"{question}"',
            language=language,
            used_observation_id=used_observation_id
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_classify(self, query_id: str, query_type: str, confidence: float):
        """記錄查詢分類"""
        message = self._format_log_message(
            "QUERY_CLASSIFY",
            query_id=query_id,
            type=query_type,
            confidence=confidence
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_process(self, query_id: str, state: Dict[str, Any]):
        """記錄查詢處理"""
        message = self._format_log_message(
            "QUERY_PROCESS",
            query_id=query_id,
            state=str(state)
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_response(self, query_id: str, response: str, duration: float):
        """記錄查詢回應"""
        # Clean response text for logging (remove newlines and limit length)
        clean_response = response.replace('\n', ' ').replace('\r', ' ').strip()
        if len(clean_response) > 200:
            clean_response = clean_response[:200] + "..."
        
        message = self._format_log_message(
            "QUERY_RESPONSE",
            query_id=query_id,
            response=f'"{clean_response}"',
            duration=f"{duration:.1f}ms"
        )
        self.loggers[LogType.USER].info(message)
    
    # 流程追蹤日誌記錄方法
    def log_flow_start(self, flow_id: str, flow_type: str):
        """記錄流程開始"""
        message = self._format_log_message(
            "FLOW_START",
            flow_id=flow_id,
            type=flow_type,
            status="started"
        )
        self.loggers[LogType.FLOW_TRACKING].info(message)    

    def log_flow_step(self, flow_id: str, step: str, **related_ids):
        """記錄流程步驟"""
        message_parts = [f"[FLOW_STEP] flow_id={flow_id}", f"step={step}"]
        
        for key, value in related_ids.items():
            if value:
                message_parts.append(f"{key}={value}")
        
        message = " ".join(message_parts)
        self.loggers[LogType.FLOW_TRACKING].info(message)
    
    def log_flow_end(self, flow_id: str, status: str, total_duration: float):
        """記錄流程結束"""
        message = self._format_log_message(
            "FLOW_END",
            flow_id=flow_id,
            status=status,
            total_duration=f"{total_duration:.1f}s"
        )
        self.loggers[LogType.FLOW_TRACKING].info(message)
    
    def get_logger(self, log_type: LogType) -> logging.Logger:
        """獲取指定類型的日誌記錄器"""
        return self.loggers.get(log_type)
    
    def close_all_loggers(self):
        """關閉所有日誌記錄器"""
        for logger in self.loggers.values():
            for handler in logger.handlers:
                handler.close()
                logger.removeHandler(handler)


# 全域日誌管理器實例
_log_manager_instance: Optional[LogManager] = None


def get_log_manager() -> LogManager:
    """獲取全域日誌管理器實例"""
    global _log_manager_instance
    if _log_manager_instance is None:
        _log_manager_instance = LogManager()
    return _log_manager_instance


def initialize_log_manager(log_dir: str = "logs") -> LogManager:
    """初始化全域日誌管理器"""
    global _log_manager_instance
    _log_manager_instance = LogManager(log_dir)
    return _log_manager_instance