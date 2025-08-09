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
        Initialize the log manager
        
        Args:
            log_dir: Log directory path
        """
        # Use absolute path for log directory
        if not os.path.isabs(log_dir):
            log_dir = os.path.join(os.path.dirname(__file__), log_dir)
        
        self.log_dir = log_dir
        self.loggers: Dict[LogType, logging.Logger] = {}
        self._ensure_log_directory()
        self._setup_loggers()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _setup_loggers(self):
        """Setup loggers for each type"""
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
        """Generate unique ID for request"""
        timestamp = int(time.time() * 1000)
        return f"req_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_state_update_id(self) -> str:
        """Generate unique ID for state update"""
        timestamp = int(time.time() * 1000)
        return f"state_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def generate_flow_id(self) -> str:
        """Generate unique ID for flow"""
        timestamp = int(time.time() * 1000)
        return f"flow_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    # System logging methods
    def log_system_start(self, system_id: str, host: str, port: int, model: str):
        """
        Log system startup event
        
        Args:
            system_id: System identifier
            host: Host address
            port: Port number
            model: Model name
        """
        logger = self.get_logger(LogType.SYSTEM)
        logger.info(f"[SYSTEM_START] system_id={system_id}, host={host}, port={port}, model={model}")
    
    def log_system_shutdown(self, system_id: str, final_memory: str, uptime: str):
        """
        Log system shutdown event
        
        Args:
            system_id: System identifier
            final_memory: Final memory usage
            uptime: System uptime
        """
        logger = self.get_logger(LogType.SYSTEM)
        logger.info(f"[SYSTEM_SHUTDOWN] system_id={system_id}, final_memory={final_memory}, uptime={uptime}")
    
    def log_memory_usage(self, system_id: str, memory_usage: str):
        """
        Log memory usage
        
        Args:
            system_id: System identifier
            memory_usage: Memory usage information
        """
        logger = self.get_logger(LogType.SYSTEM)
        logger.info(f"[MEMORY] system_id={system_id}, memory_usage={memory_usage}")
    
    def log_endpoint_call(self, request_id: str, method: str, path: str, 
                         status: int, duration: float):
        """
        Log endpoint call
        
        Args:
            request_id: Request identifier
            method: HTTP method
            path: Request path
            status: Response status
            duration: Request duration
        """
        logger = self.get_logger(LogType.SYSTEM)
        logger.info(f"[ENDPOINT] request_id={request_id}, method={method}, path={path}, status={status}, duration={duration}s")
    
    # Visual logging methods
    def log_eyes_capture(self, observation_id: str, request_id: str, 
                        device: str, resolution: str, quality: float, 
                        format: str, size: str):
        """
        Log image capture event
        
        Args:
            observation_id: Observation identifier
            request_id: Request identifier
            device: Camera device name
            resolution: Image resolution
            quality: Image quality
            format: Image format
            size: Image size
        """
        logger = self.get_logger(LogType.VISUAL)
        logger.info(f"[EYES_CAPTURE] observation_id={observation_id}, request_id={request_id}, device={device}, resolution={resolution}, quality={quality}, format={format}, size={size}")
    
    def log_eyes_prompt(self, observation_id: str, prompt: str, length: int):
        """
        Log visual prompt usage
        
        Args:
            observation_id: Observation identifier
            prompt: Prompt content
            length: Prompt length
        """
        logger = self.get_logger(LogType.VISUAL)
        logger.info(f"[EYES_PROMPT] observation_id={observation_id}, prompt=\"{prompt}\", length={length} chars")
    
    def log_eyes_transfer(self, observation_id: str, sent_data: Dict[str, Any]):
        """
        Log data transfer to backend
        
        Args:
            observation_id: Observation identifier
            sent_data: Data sent to backend
        """
        logger = self.get_logger(LogType.VISUAL)
        logger.info(f"[EYES_TRANSFER] observation_id={observation_id}, sent_to_backend={sent_data}")
    
    def log_rag_matching(self, observation_id: str, vlm_observation: str, 
                        candidate_steps: list, similarities: list):
        """
        Log RAG matching process
        
        Args:
            observation_id: Observation identifier
            vlm_observation: VLM observation text
            candidate_steps: Candidate steps
            similarities: Similarity scores
        """
        logger = self.get_logger(LogType.VISUAL)
        logger.info(f"[RAG_MATCHING] observation_id={observation_id}, vlm_observation=\"{vlm_observation}\", candidate_steps={candidate_steps}, similarities={similarities}")
    
    def log_rag_result(self, observation_id: str, selected: str, 
                      title: str, similarity: float):
        """
        Log RAG matching result
        
        Args:
            observation_id: Observation identifier
            selected: Selected step
            title: Step title
            similarity: Best similarity score
        """
        logger = self.get_logger(LogType.VISUAL)
        logger.info(f"[RAG_RESULT] observation_id={observation_id}, selected={selected}, title=\"{title}\", similarity={similarity}")
    
    def log_state_tracker(self, observation_id: str, state_update_id: str,
                         confidence: float, action: str, state: Dict[str, Any]):
        """
        Log state tracker decision
        
        Args:
            observation_id: Observation identifier
            state_update_id: State update identifier
            confidence: Confidence score
            action: Action taken
            state: Updated state
        """
        logger = self.get_logger(LogType.VISUAL)
        logger.info(f"[STATE_TRACKER] observation_id={observation_id}, state_update_id={state_update_id}, confidence={confidence}, action={action}, state={state}")
    
    # User query logging methods
    def log_user_query(self, query_id: str, request_id: str, question: str, 
                      language: str, used_observation_id: Optional[str] = None):
        """
        Log user query
        
        Args:
            query_id: Query identifier
            request_id: Request identifier
            question: User question
            language: Query language
            used_observation_id: Related observation ID
        """
        logger = self.get_logger(LogType.USER)
        obs_ref = f", used_observation_id={used_observation_id}" if used_observation_id else ""
        logger.info(f"[USER_QUERY] query_id={query_id}, request_id={request_id}, question=\"{question}\", language={language}{obs_ref}")
    
    def log_query_classify(self, query_id: str, query_type: str, confidence: float):
        """
        Log query classification
        
        Args:
            query_id: Query identifier
            query_type: Classified query type
            confidence: Classification confidence
        """
        logger = self.get_logger(LogType.USER)
        logger.info(f"[QUERY_CLASSIFY] query_id={query_id}, type={query_type}, confidence={confidence}")
    
    def log_query_process(self, query_id: str, state: Dict[str, Any]):
        """
        Log query processing
        
        Args:
            query_id: Query identifier
            state: Current state information
        """
        logger = self.get_logger(LogType.USER)
        logger.info(f"[QUERY_PROCESS] query_id={query_id}, state={state}")
    
    def log_query_response(self, query_id: str, response: str, duration: float):
        """
        Log query response
        
        Args:
            query_id: Query identifier
            response: Response content
            duration: Processing duration
        """
        logger = self.get_logger(LogType.USER)
        logger.info(f"[QUERY_RESPONSE] query_id={query_id}, response=\"{response}\", duration={duration}ms")
    
    # Flow tracking logging methods
    def log_flow_start(self, flow_id: str, flow_type: str):
        """
        Log flow start
        
        Args:
            flow_id: Flow identifier
            flow_type: Flow type
        """
        logger = self.get_logger(LogType.FLOW_TRACKING)
        logger.info(f"[FLOW_START] flow_id={flow_id}, type={flow_type}, started")
    
    def log_flow_step(self, flow_id: str, step: str, **related_ids):
        """
        Log flow step
        
        Args:
            flow_id: Flow identifier
            step: Step name
            **related_ids: Related identifiers
        """
        logger = self.get_logger(LogType.FLOW_TRACKING)
        related_info = ", ".join([f"{k}={v}" for k, v in related_ids.items()])
        logger.info(f"[FLOW_STEP] flow_id={flow_id}, step={step}, {related_info}")
    
    def log_flow_end(self, flow_id: str, status: str, total_duration: float):
        """
        Log flow end
        
        Args:
            flow_id: Flow identifier
            status: Flow status
            total_duration: Total flow duration
        """
        logger = self.get_logger(LogType.FLOW_TRACKING)
        logger.info(f"[FLOW_END] flow_id={flow_id}, status={status}, total_duration={total_duration}s")
    
    def get_logger(self, log_type: LogType) -> logging.Logger:
        """Get logger for specific type"""
        return self.loggers[log_type]
    
    def close_all_loggers(self):
        """Close all loggers and handlers"""
        for logger in self.loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)


# Global instance
_log_manager = None


def get_log_manager() -> LogManager:
    """Get global log manager instance"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


def initialize_log_manager(log_dir: str = "logs") -> LogManager:
    """Initialize global log manager with custom directory"""
    global _log_manager
    _log_manager = LogManager(log_dir)
    return _log_manager