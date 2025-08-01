"""
AI Manual Assistant Logging System Core Manager

Provides unified logging management functionality, supporting multiple log types and unique ID tracking mechanisms.
"""

import logging
import uuid
import time
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum
import os
from pathlib import Path


class LogType(Enum):
    """Log type enumeration"""
    SYSTEM = "system"
    VISUAL = "visual" 
    USER = "user"
    FLOW_TRACKING = "flow_tracking"


class LogManager:
    """
    Unified Log Manager
    
    Responsible for managing all types of log records, providing unique ID generation and unified formatting functionality.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize log manager
        
        Args:
            log_dir: Log directory path
        """
        # Dynamically resolve log path
        self.log_dir = self._resolve_log_path(log_dir)
        self.loggers: Dict[LogType, logging.Logger] = {}
        self._ensure_log_directory()
        self._setup_loggers()
    
    def _resolve_log_path(self, log_dir: str) -> Path:
        """Dynamically resolve log path"""
        # If already absolute path, use directly
        if os.path.isabs(log_dir):
            return Path(log_dir)
        
        # Start from current file location and search upward for project root
        current = Path(__file__).resolve().parent
        
        # Search upward up to 5 levels to avoid infinite loop
        for _ in range(5):
            # Check if it's project root
            if self._is_project_root(current):
                return current / log_dir
            current = current.parent
        
        # If not found, use current directory
        return Path.cwd() / log_dir
    
    def _is_project_root(self, path: Path) -> bool:
        """Check if it's project root directory"""
        return (
            (path / "requirements.txt").exists() and
            (path / "src" / "backend" / "main.py").exists()
        )
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _setup_loggers(self):
        """Setup various type loggers"""
        for log_type in LogType:
            logger = logging.getLogger(f"ai_assistant_{log_type.value}")
            logger.setLevel(logging.INFO)
            
            # Create file handler
            today = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(self.log_dir, f"{log_type.value}_{today}.log")
            
            handler = logging.FileHandler(log_file, encoding='utf-8')
            handler.setLevel(logging.INFO)
            
            # Set unified format
            formatter = logging.Formatter(
                '%(asctime)s,%(msecs)03d [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            logger.addHandler(handler)
            self.loggers[log_type] = logger    

    # Unique ID generation methods
    def generate_observation_id(self) -> str:
        """Generate unique ID for observation event"""
        timestamp = int(time.time() * 1000)
        return f"obs_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_query_id(self) -> str:
        """Generate unique ID for query event"""
        timestamp = int(time.time() * 1000)
        return f"query_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_request_id(self) -> str:
        """Generate unique ID for request event"""
        timestamp = int(time.time() * 1000)
        return f"req_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_state_update_id(self) -> str:
        """Generate unique ID for state update event"""
        timestamp = int(time.time() * 1000)
        return f"state_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_flow_id(self) -> str:
        """Generate unique ID for flow tracking event"""
        timestamp = int(time.time() * 1000)
        return f"flow_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def _format_log_message(self, event_type: str, **kwargs) -> str:
        """
        Format log message
        
        Args:
            event_type: Event type
            **kwargs: Log parameters
            
        Returns:
            Formatted log message
        """
        parts = [f"[{event_type}]"]
        
        for key, value in kwargs.items():
            if value is not None:
                parts.append(f"{key}={value}")
        
        return " ".join(parts)
    
    # System logging methods
    def log_system_start(self, system_id: str, host: str, port: int, model: str):
        """Log system startup"""
        message = self._format_log_message(
            "SYSTEM_START",
            system_id=system_id,
            host=host,
            port=port,
            model=model
        )
        self.loggers[LogType.SYSTEM].info(message) 
   
    def log_system_shutdown(self, system_id: str, final_memory: str, uptime: str):
        """Log system shutdown"""
        message = self._format_log_message(
            "SYSTEM_SHUTDOWN",
            system_id=system_id,
            final_memory=final_memory,
            uptime=uptime
        )
        self.loggers[LogType.SYSTEM].info(message)
    
    def log_memory_usage(self, system_id: str, memory_usage: str):
        """Log memory usage"""
        message = self._format_log_message(
            "MEMORY",
            system_id=system_id,
            memory_usage=memory_usage
        )
        self.loggers[LogType.SYSTEM].info(message)
    
    def log_endpoint_call(self, request_id: str, method: str, path: str, 
                         status: int, duration: float):
        """Log endpoint call"""
        message = self._format_log_message(
            "ENDPOINT",
            request_id=request_id,
            method=method,
            path=path,
            status=status,
            duration=f"{duration:.2f}s"
        )
        self.loggers[LogType.SYSTEM].info(message)
    
    # Visual logging methods
    def log_eyes_capture(self, observation_id: str, request_id: str, 
                        device: str, resolution: str, quality: float, 
                        format: str, size: str):
        """Log image capture"""
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
        """Log visual prompt"""
        message = self._format_log_message(
            "EYES_PROMPT",
            observation_id=observation_id,
            prompt=f'"{prompt}"',
            length=f"{length} chars"
        )
        self.loggers[LogType.VISUAL].info(message)
    
    def log_eyes_transfer(self, observation_id: str, sent_data: Dict[str, Any]):
        """Log backend transfer"""
        message = self._format_log_message(
            "EYES_TRANSFER",
            observation_id=observation_id,
            sent_to_backend=str(sent_data)
        )
        self.loggers[LogType.VISUAL].info(message)
    
    def log_rag_matching(self, observation_id: str, vlm_observation: str, 
                        candidate_steps: list, similarities: list):
        """Log RAG matching process"""
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
        """Log RAG matching result"""
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
        """Log state tracker decision"""
        message = self._format_log_message(
            "STATE_TRACKER",
            observation_id=observation_id,
            state_update_id=state_update_id,
            confidence=confidence,
            action=action,
            state=str(state)
        )
        self.loggers[LogType.VISUAL].info(message)    
 
       # User query logging methods
    def log_user_query(self, query_id: str, request_id: str, question: str, 
                      language: str, used_observation_id: Optional[str] = None):
        """Log user query"""
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
        """Log query classification"""
        message = self._format_log_message(
            "QUERY_CLASSIFY",
            query_id=query_id,
            query_type=query_type,
            confidence=f"{confidence:.3f}"
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_process(self, query_id: str, state: Dict[str, Any]):
        """Log query processing"""
        message = self._format_log_message(
            "QUERY_PROCESS",
            query_id=query_id,
            state=str(state)
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_response(self, query_id: str, response: str, duration: float):
        """Log query response"""
        message = self._format_log_message(
            "QUERY_RESPONSE",
            query_id=query_id,
            response=f'"{response}"',
            duration=f"{duration:.2f}s"
        )
        self.loggers[LogType.USER].info(message)
    
    # Detailed query processing methods
    def log_query_classify_start(self, query_id: str, query: str):
        """Log query classification start"""
        message = self._format_log_message(
            "QUERY_CLASSIFY_START",
            query_id=query_id,
            query=f'"{query}"'
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_pattern_check(self, query_id: str, pattern: str, query_type: str):
        """Log pattern check process"""
        message = self._format_log_message(
            "QUERY_PATTERN_CHECK",
            query_id=query_id,
            pattern=f'"{pattern}"',
            query_type=query_type
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_pattern_match(self, query_id: str, query_type: str, pattern: str):
        """Log pattern match success"""
        message = self._format_log_message(
            "QUERY_PATTERN_MATCH",
            query_id=query_id,
            query_type=query_type,
            pattern=f'"{pattern}"'
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_classify_result(self, query_id: str, query_type: str, confidence: float):
        """Log classification final result"""
        message = self._format_log_message(
            "QUERY_CLASSIFY_RESULT",
            query_id=query_id,
            query_type=query_type,
            confidence=f"{confidence:.3f}"
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_process_start(self, query_id: str, query: str, state_keys: list):
        """Log query processing start"""
        message = self._format_log_message(
            "QUERY_PROCESS_START",
            query_id=query_id,
            query=f'"{query}"',
            state_keys=str(state_keys)
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_state_lookup(self, query_id: str, state_found: bool, state_info: dict):
        """Log state lookup process"""
        message = self._format_log_message(
            "QUERY_STATE_LOOKUP",
            query_id=query_id,
            state_found=state_found,
            state_info=str(state_info)
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_response_generate(self, query_id: str, response_type: str, response_length: int):
        """Log response generation process"""
        message = self._format_log_message(
            "QUERY_RESPONSE_GENERATE",
            query_id=query_id,
            response_type=response_type,
            response_length=response_length
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_process_complete(self, query_id: str, processing_time: float):
        """Log query processing complete"""
        message = self._format_log_message(
            "QUERY_PROCESS_COMPLETE",
            query_id=query_id,
            processing_time=f"{processing_time:.3f}s"
        )
        self.loggers[LogType.USER].info(message)
    
    def log_query_received(self, query_id: str, query: str):
        """Log query received"""
        message = self._format_log_message(
            "QUERY_RECEIVED",
            query_id=query_id,
            query=f'"{query}"'
        )
        self.loggers[LogType.USER].info(message)
    
    # Flow tracking logging methods
    def log_flow_start(self, flow_id: str, flow_type: str):
        """Log flow start"""
        message = self._format_log_message(
            "FLOW_START",
            flow_id=flow_id,
            flow_type=flow_type
        )
        self.loggers[LogType.FLOW_TRACKING].info(message)    

    def log_flow_step(self, flow_id: str, step: str, **related_ids):
        """Log flow step"""
        message = self._format_log_message(
            "FLOW_STEP",
            flow_id=flow_id,
            step=step,
            **related_ids
        )
        self.loggers[LogType.FLOW_TRACKING].info(message)
    
    def log_flow_end(self, flow_id: str, status: str, total_duration: float):
        """Log flow end"""
        message = self._format_log_message(
            "FLOW_END",
            flow_id=flow_id,
            status=status,
            total_duration=f"{total_duration:.2f}s"
        )
        self.loggers[LogType.FLOW_TRACKING].info(message)
    
    # Utility methods
    def get_logger(self, log_type: LogType) -> logging.Logger:
        """Get logger for specified type"""
        return self.loggers[log_type]
    
    def close_all_loggers(self):
        """Close all loggers and handlers"""
        for logger in self.loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)


# Global instance management
def get_log_manager() -> LogManager:
    """Get global log manager instance"""
    if not hasattr(get_log_manager, '_instance'):
        get_log_manager._instance = LogManager()
    return get_log_manager._instance


def initialize_log_manager(log_dir: str = "logs") -> LogManager:
    """Initialize log manager with custom directory"""
    return LogManager(log_dir)