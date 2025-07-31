"""
AI Manual Assistant Flow Tracker

Provides unified flow tracking functionality for end-to-end process monitoring and correlation.
"""

import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
try:
    from .log_manager import get_log_manager, LogManager, LogType
except ImportError:
    # Handle standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.app_logging.log_manager import get_log_manager, LogManager, LogType


class FlowType(Enum):
    """Flow type enumeration"""
    EYES_OBSERVATION = "EYES_OBSERVATION"
    USER_QUERY = "USER_QUERY"
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"


class FlowStatus(Enum):
    """Flow status enumeration"""
    ACTIVE = "ACTIVE"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class FlowStep(Enum):
    """Flow step enumeration"""
    # Eyes observation flow steps
    IMAGE_CAPTURE = "image_capture"
    BACKEND_TRANSFER = "backend_transfer"
    VLM_PROCESSING = "vlm_processing"
    RAG_MATCHING = "rag_matching"
    STATE_UPDATE = "state_update"
    
    # User query flow steps
    QUERY_RECEIVED = "query_received"
    QUERY_CLASSIFICATION = "query_classification"
    STATE_LOOKUP = "state_lookup"
    RESPONSE_GENERATION = "response_generation"
    RESPONSE_SENT = "response_sent"
    
    # System flow steps
    SYSTEM_INIT = "system_init"
    MODEL_LOADING = "model_loading"
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"


class FlowTracker:
    """
    Flow Tracker for AI Manual Assistant
    
    Manages end-to-end flow tracking, correlating all related events through unique flow IDs.
    """
    
    def __init__(self):
        """Initialize flow tracker"""
        self.log_manager = get_log_manager()
        self.logger = self.log_manager.get_logger(LogType.FLOW_TRACKING)
        self.active_flows: Dict[str, Dict[str, Any]] = {}
        self.completed_flows: Dict[str, Dict[str, Any]] = {}
    
    def start_flow(self, flow_type: FlowType, metadata: Dict[str, Any]) -> str:
        """
        Start a new flow
        
        Args:
            flow_type: Type of flow
            metadata: Flow metadata
            
        Returns:
            Flow ID
        """
        flow_id = self.log_manager.generate_flow_id()
        start_time = time.time()
        
        flow_info = {
            "flow_id": flow_id,
            "type": flow_type.value,
            "status": FlowStatus.ACTIVE.value,
            "start_time": start_time,
            "metadata": metadata,
            "steps": [],
            "end_time": None,
            "total_duration": None,
            "result": None
        }
        
        self.active_flows[flow_id] = flow_info
        
        # Log flow start
        self.logger.info(f"[FLOW_START] flow_id={flow_id}, type={flow_type.value}, metadata={metadata}")
        
        return flow_id
    
    def add_flow_step(self, flow_id: str, step: FlowStep, metadata: Dict[str, Any]):
        """
        Add a step to the flow
        
        Args:
            flow_id: Flow identifier
            step: Flow step
            metadata: Step metadata
        """
        if flow_id not in self.active_flows:
            raise ValueError(f"Flow {flow_id} not found or already completed")
        
        step_info = {
            "step": step.value,
            "timestamp": time.time(),
            "metadata": metadata
        }
        
        self.active_flows[flow_id]["steps"].append(step_info)
        
        # Log flow step
        step_metadata_str = ", ".join([f"{k}={v}" for k, v in metadata.items()])
        self.logger.info(f"[FLOW_STEP] flow_id={flow_id}, step={step.value}, {step_metadata_str}")
    
    def end_flow(self, flow_id: str, status: FlowStatus, result: Dict[str, Any]):
        """
        End a flow
        
        Args:
            flow_id: Flow identifier
            status: Flow status
            result: Flow result
        """
        if flow_id not in self.active_flows:
            raise ValueError(f"Flow {flow_id} not found or already completed")
        
        flow_info = self.active_flows[flow_id]
        end_time = time.time()
        total_duration = end_time - flow_info["start_time"]
        
        # Update flow info
        flow_info["status"] = status.value
        flow_info["end_time"] = end_time
        flow_info["total_duration"] = total_duration
        flow_info["result"] = result
        
        # Move to completed flows
        self.completed_flows[flow_id] = flow_info
        del self.active_flows[flow_id]
        
        # Log flow end
        self.logger.info(f"[FLOW_END] flow_id={flow_id}, status={status.value}, total_duration={total_duration:.3f}s, result={result}")
    
    def get_flow_info(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get flow information
        
        Args:
            flow_id: Flow identifier
            
        Returns:
            Flow information or None if not found
        """
        if flow_id in self.active_flows:
            return self.active_flows[flow_id]
        elif flow_id in self.completed_flows:
            return self.completed_flows[flow_id]
        else:
            return None
    
    def get_flow_statistics(self) -> Dict[str, Any]:
        """
        Get flow statistics
        
        Returns:
            Flow statistics
        """
        total_flows = len(self.active_flows) + len(self.completed_flows)
        active_flows = len(self.active_flows)
        completed_flows = len(self.completed_flows)
        
        # Count by status
        status_counts = {}
        for flow_info in self.completed_flows.values():
            status = flow_info["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by type
        type_counts = {}
        for flow_info in list(self.active_flows.values()) + list(self.completed_flows.values()):
            flow_type = flow_info["type"]
            type_counts[flow_type] = type_counts.get(flow_type, 0) + 1
        
        return {
            "total_flows": total_flows,
            "active_flows": active_flows,
            "completed_flows": completed_flows,
            "status_counts": status_counts,
            "type_counts": type_counts
        }
    
    def get_flows_by_type(self, flow_type: FlowType) -> List[Dict[str, Any]]:
        """
        Get flows by type
        
        Args:
            flow_type: Flow type
            
        Returns:
            List of flows of the specified type
        """
        flows = []
        
        for flow_info in list(self.active_flows.values()) + list(self.completed_flows.values()):
            if flow_info["type"] == flow_type.value:
                flows.append(flow_info)
        
        return flows
    
    def get_flows_by_status(self, status: FlowStatus) -> List[Dict[str, Any]]:
        """
        Get flows by status
        
        Args:
            status: Flow status
            
        Returns:
            List of flows with the specified status
        """
        flows = []
        
        if status == FlowStatus.ACTIVE:
            flows.extend(self.active_flows.values())
        else:
            for flow_info in self.completed_flows.values():
                if flow_info["status"] == status.value:
                    flows.append(flow_info)
        
        return flows
    
    def cleanup_old_flows(self, max_age_hours: int = 24):
        """
        Clean up old completed flows
        
        Args:
            max_age_hours: Maximum age in hours
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        flows_to_remove = []
        for flow_id, flow_info in self.completed_flows.items():
            if flow_info["end_time"] and (current_time - flow_info["end_time"]) > max_age_seconds:
                flows_to_remove.append(flow_id)
        
        for flow_id in flows_to_remove:
            del self.completed_flows[flow_id]
        
        if flows_to_remove:
            self.logger.info(f"[FLOW_CLEANUP] removed {len(flows_to_remove)} old flows")


# Global instance
_flow_tracker = None


def get_flow_tracker() -> FlowTracker:
    """Get global flow tracker instance"""
    global _flow_tracker
    if _flow_tracker is None:
        _flow_tracker = FlowTracker()
    return _flow_tracker


def initialize_flow_tracker() -> FlowTracker:
    """Initialize global flow tracker"""
    global _flow_tracker
    _flow_tracker = FlowTracker()
    return _flow_tracker


# Convenience functions
def start_flow(flow_type: FlowType, metadata: Dict[str, Any]) -> str:
    """Start a new flow"""
    tracker = get_flow_tracker()
    return tracker.start_flow(flow_type, metadata)


def add_flow_step(flow_id: str, step: FlowStep, metadata: Dict[str, Any]):
    """Add a step to the flow"""
    tracker = get_flow_tracker()
    tracker.add_flow_step(flow_id, step, metadata)


def end_flow(flow_id: str, status: FlowStatus, result: Dict[str, Any]):
    """End a flow"""
    tracker = get_flow_tracker()
    tracker.end_flow(flow_id, status, result)


def get_flow_info(flow_id: str) -> Optional[Dict[str, Any]]:
    """Get flow information"""
    tracker = get_flow_tracker()
    return tracker.get_flow_info(flow_id)


def get_flow_statistics() -> Dict[str, Any]:
    """Get flow statistics"""
    tracker = get_flow_tracker()
    return tracker.get_flow_statistics() 