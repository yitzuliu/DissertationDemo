"""
AI Manual Assistant 統一流程追蹤器

提供端到端流程追蹤功能，通過唯一的 flow_id 連結所有相關事件。
實現完整的時間線記錄和相關ID關聯。
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from dataclasses import dataclass

from .log_manager import get_log_manager, LogType

logger = logging.getLogger(__name__)

class FlowType(Enum):
    """流程類型枚舉"""
    EYES_OBSERVATION = "EYES_OBSERVATION"
    USER_QUERY = "USER_QUERY"
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    ERROR_RECOVERY = "ERROR_RECOVERY"

class FlowStatus(Enum):
    """流程狀態枚舉"""
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class FlowStep(Enum):
    """流程步驟枚舉"""
    # 視覺觀察流程步驟
    IMAGE_CAPTURE = "image_capture"
    BACKEND_TRANSFER = "backend_transfer"
    VLM_PROCESSING = "vlm_processing"
    RAG_MATCHING = "rag_matching"
    STATE_UPDATE = "state_update"
    
    # 使用者查詢流程步驟
    QUERY_RECEIVED = "query_received"
    QUERY_CLASSIFICATION = "query_classification"
    STATE_LOOKUP = "state_lookup"
    RESPONSE_GENERATION = "response_generation"
    RESPONSE_SENT = "response_sent"
    
    # 系統流程步驟
    SYSTEM_INIT = "system_init"
    MODEL_LOADING = "model_loading"
    SERVICE_START = "service_start"
    HEALTH_CHECK = "health_check"

@dataclass
class FlowStepRecord:
    """流程步驟記錄"""
    step: str
    timestamp: datetime
    duration_ms: float
    related_ids: Dict[str, str]
    metadata: Dict[str, Any]

class FlowTracker:
    """
    統一流程追蹤器
    
    負責管理所有流程的端到端追蹤，提供完整的時間線記錄。
    """
    
    def __init__(self):
        """初始化流程追蹤器"""
        self.log_manager = get_log_manager()
        self.active_flows: Dict[str, Dict[str, Any]] = {}
        self.flow_history: List[Dict[str, Any]] = []
    
    def start_flow(self, flow_type: FlowType, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        開始新的流程
        
        Args:
            flow_type: 流程類型
            metadata: 額外的元數據
            
        Returns:
            flow_id: 流程唯一ID
        """
        flow_id = self.log_manager.generate_flow_id()
        start_time = datetime.now()
        
        # 記錄流程開始
        self.log_manager.log_flow_start(flow_id, flow_type.value)
        
        # 儲存流程資訊
        flow_info = {
            'flow_id': flow_id,
            'flow_type': flow_type.value,
            'status': FlowStatus.STARTED.value,
            'start_time': start_time,
            'steps': [],
            'metadata': metadata or {},
            'related_ids': {}
        }
        
        self.active_flows[flow_id] = flow_info
        
        logger.info(f"Flow started: {flow_id} ({flow_type.value})")
        return flow_id
    
    def add_flow_step(self, flow_id: str, step: FlowStep, 
                     related_ids: Optional[Dict[str, str]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加流程步驟
        
        Args:
            flow_id: 流程ID
            step: 步驟類型
            related_ids: 相關的唯一ID
            metadata: 步驟元數據
            
        Returns:
            bool: 是否成功添加
        """
        if flow_id not in self.active_flows:
            logger.warning(f"Flow {flow_id} not found for step {step.value}")
            return False
        
        step_start_time = datetime.now()
        related_ids = related_ids or {}
        metadata = metadata or {}
        
        # 記錄流程步驟
        self.log_manager.log_flow_step(flow_id, step.value, **related_ids)
        
        # 更新流程資訊
        flow_info = self.active_flows[flow_id]
        flow_info['steps'].append({
            'step': step.value,
            'timestamp': step_start_time,
            'related_ids': related_ids,
            'metadata': metadata
        })
        
        # 更新相關ID
        flow_info['related_ids'].update(related_ids)
        
        logger.debug(f"Flow step added: {flow_id} -> {step.value}")
        return True
    
    def end_flow(self, flow_id: str, status: FlowStatus = FlowStatus.SUCCESS,
                final_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        結束流程
        
        Args:
            flow_id: 流程ID
            status: 結束狀態
            final_metadata: 最終元數據
            
        Returns:
            bool: 是否成功結束
        """
        if flow_id not in self.active_flows:
            logger.warning(f"Flow {flow_id} not found for ending")
            return False
        
        flow_info = self.active_flows[flow_id]
        end_time = datetime.now()
        start_time = flow_info['start_time']
        total_duration = (end_time - start_time).total_seconds() * 1000
        
        # 更新最終元數據
        if final_metadata:
            flow_info['metadata'].update(final_metadata)
        
        # 記錄流程結束
        self.log_manager.log_flow_end(flow_id, status.value, total_duration)
        
        # 更新流程狀態
        flow_info['status'] = status.value
        flow_info['end_time'] = end_time
        flow_info['total_duration_ms'] = total_duration
        
        # 移動到歷史記錄
        self.flow_history.append(flow_info)
        del self.active_flows[flow_id]
        
        logger.info(f"Flow ended: {flow_id} ({status.value}) in {total_duration:.1f}ms")
        return True
    
    def get_flow_info(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取流程資訊
        
        Args:
            flow_id: 流程ID
            
        Returns:
            Dict: 流程資訊或None
        """
        # 先檢查活躍流程
        if flow_id in self.active_flows:
            return self.active_flows[flow_id]
        
        # 再檢查歷史記錄
        for flow in self.flow_history:
            if flow['flow_id'] == flow_id:
                return flow
        
        return None
    
    def get_active_flows(self) -> List[Dict[str, Any]]:
        """
        獲取所有活躍流程
        
        Returns:
            List: 活躍流程列表
        """
        return list(self.active_flows.values())
    
    def get_flow_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        獲取流程歷史記錄
        
        Args:
            limit: 返回記錄數量限制
            
        Returns:
            List: 流程歷史記錄
        """
        return self.flow_history[-limit:] if self.flow_history else []
    
    def get_flows_by_type(self, flow_type: FlowType) -> List[Dict[str, Any]]:
        """
        根據類型獲取流程
        
        Args:
            flow_type: 流程類型
            
        Returns:
            List: 匹配的流程列表
        """
        matching_flows = []
        
        # 檢查活躍流程
        for flow in self.active_flows.values():
            if flow['flow_type'] == flow_type.value:
                matching_flows.append(flow)
        
        # 檢查歷史記錄
        for flow in self.flow_history:
            if flow['flow_type'] == flow_type.value:
                matching_flows.append(flow)
        
        return matching_flows
    
    def cleanup_old_flows(self, max_age_hours: int = 24) -> int:
        """
        清理舊的流程記錄
        
        Args:
            max_age_hours: 最大保留時間（小時）
            
        Returns:
            int: 清理的記錄數量
        """
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        original_count = len(self.flow_history)
        
        # 過濾掉舊記錄
        self.flow_history = [
            flow for flow in self.flow_history
            if flow.get('end_time', flow.get('start_time')).timestamp() > cutoff_time
        ]
        
        cleaned_count = original_count - len(self.flow_history)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old flow records")
        
        return cleaned_count
    
    def get_flow_statistics(self) -> Dict[str, Any]:
        """
        獲取流程統計資訊
        
        Returns:
            Dict: 統計資訊
        """
        total_flows = len(self.active_flows) + len(self.flow_history)
        
        # 按類型統計
        type_counts = {}
        for flow in list(self.active_flows.values()) + self.flow_history:
            flow_type = flow['flow_type']
            type_counts[flow_type] = type_counts.get(flow_type, 0) + 1
        
        # 按狀態統計
        status_counts = {}
        for flow in list(self.active_flows.values()) + self.flow_history:
            status = flow.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 平均持續時間
        completed_flows = [f for f in self.flow_history if 'total_duration_ms' in f]
        avg_duration = sum(f['total_duration_ms'] for f in completed_flows) / len(completed_flows) if completed_flows else 0
        
        return {
            'total_flows': total_flows,
            'active_flows': len(self.active_flows),
            'completed_flows': len(self.flow_history),
            'type_distribution': type_counts,
            'status_distribution': status_counts,
            'average_duration_ms': avg_duration
        }

# 全局流程追蹤器實例
_flow_tracker_instance: Optional[FlowTracker] = None

def get_flow_tracker() -> FlowTracker:
    """獲取全局流程追蹤器實例"""
    global _flow_tracker_instance
    if _flow_tracker_instance is None:
        _flow_tracker_instance = FlowTracker()
    return _flow_tracker_instance

def start_flow(flow_type: FlowType, metadata: Optional[Dict[str, Any]] = None) -> str:
    """便捷函數：開始流程"""
    return get_flow_tracker().start_flow(flow_type, metadata)

def add_flow_step(flow_id: str, step: FlowStep, 
                 related_ids: Optional[Dict[str, str]] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
    """便捷函數：添加流程步驟"""
    return get_flow_tracker().add_flow_step(flow_id, step, related_ids, metadata)

def end_flow(flow_id: str, status: FlowStatus = FlowStatus.SUCCESS,
            final_metadata: Optional[Dict[str, Any]] = None) -> bool:
    """便捷函數：結束流程"""
    return get_flow_tracker().end_flow(flow_id, status, final_metadata) 