"""
AI Manual Assistant System Logger

Provides system-level logging functionality for technical events, resource monitoring, and performance tracking.
"""

import logging
import psutil
import time
from datetime import datetime
from typing import Optional, Dict, Any
try:
    from .log_manager import get_log_manager, LogManager, LogType
except ImportError:
    # Handle standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.app_logging.log_manager import get_log_manager, LogManager, LogType


class SystemLogger:
    """
    System Logger for AI Manual Assistant
    
    Handles system-level logging including startup/shutdown events, resource monitoring,
    endpoint calls, connection status, and error handling.
    """
    
    def __init__(self):
        """Initialize system logger"""
        self.log_manager = get_log_manager()
        self.logger = self.log_manager.get_logger(LogType.SYSTEM)
        self.start_time = time.time()
    
    def log_system_startup(self, host: str, port: int, model: str):
        """
        Log system startup event
        
        Args:
            host: Host address
            port: Port number
            model: Model name
        """
        system_id = f"sys_{int(time.time())}"
        self.log_manager.log_system_start(system_id, host, port, model)
        
        # Log initial memory usage
        memory_info = psutil.virtual_memory()
        memory_usage = f"{memory_info.used / 1024 / 1024:.1f}MB"
        self.log_manager.log_memory_usage(system_id, memory_usage)
        
        # Log CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.log_cpu_usage(f"startup_cpu_usage={cpu_percent}%")
        
        # Log health check
        self.log_health_check("system_startup", "HEALTHY", 0.0)
    
    def log_system_shutdown(self, final_memory: str, uptime: float):
        """
        Log system shutdown event
        
        Args:
            final_memory: Final memory usage
            uptime: System uptime in seconds
        """
        system_id = f"sys_{int(self.start_time)}"
        uptime_str = f"{uptime:.1f}s"
        self.log_manager.log_system_shutdown(system_id, final_memory, uptime_str)
        
        # Log final health check
        self.log_health_check("system_shutdown", "SHUTDOWN", 0.0)
    
    def log_memory_usage(self, context: str):
        """
        Log current memory usage
        
        Args:
            context: Context for memory logging
        """
        memory_info = psutil.virtual_memory()
        memory_usage = f"{memory_info.used / 1024 / 1024:.1f}MB"
        self.logger.info(f"[MEMORY_USAGE] context={context}, memory_usage={memory_usage}, percent={memory_info.percent}%")
    
    def log_cpu_usage(self, context: str):
        """
        Log current CPU usage
        
        Args:
            context: Context for CPU logging
        """
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.logger.info(f"[CPU_USAGE] context={context}, cpu_percent={cpu_percent}%")
    
    def log_endpoint_call(self, method: str, path: str, status: int, duration: float, request_id: str):
        """
        Log endpoint call
        
        Args:
            method: HTTP method
            path: Request path
            status: Response status
            duration: Request duration
            request_id: Request identifier
        """
        self.log_manager.log_endpoint_call(request_id, method, path, status, duration)
        
        # Log performance metric
        self.log_performance_metric("endpoint_response_time", duration, "s", f"{method}_{path}")
    
    def log_connection_status(self, service: str, status: str, details: str):
        """
        Log connection status
        
        Args:
            service: Service name
            status: Connection status
            details: Additional details
        """
        self.logger.info(f"[CONNECTION_STATUS] service={service}, status={status}, details={details}")
        
        # Log health check for connection
        health_status = "HEALTHY" if status == "CONNECTED" else "UNHEALTHY"
        self.log_health_check(f"connection_{service}", health_status, 0.0)
    
    def log_error(self, error_type: str, message: str, context: Dict[str, Any]):
        """
        Log error event
        
        Args:
            error_type: Type of error
            message: Error message
            context: Error context
        """
        self.logger.error(f"[ERROR] error_type={error_type}, message=\"{message}\", context={context}")
        
        # Log performance metric for error
        self.log_performance_metric("error_count", 1, "count", error_type)
    
    def log_performance_metric(self, metric: str, value: float, unit: str, context: str):
        """
        Log performance metric
        
        Args:
            metric: Metric name
            value: Metric value
            unit: Unit of measurement
            context: Context for the metric
        """
        self.logger.info(f"[PERFORMANCE_METRIC] metric={metric}, value={value}, unit={unit}, context={context}")
    
    def log_health_check(self, component: str, status: str, response_time: float):
        """
        Log health check result
        
        Args:
            component: Component name
            status: Health status
            response_time: Response time
        """
        self.logger.info(f"[HEALTH_CHECK] component={component}, status={status}, response_time={response_time}s")


# Global instance
_system_logger = None


def get_system_logger() -> SystemLogger:
    """Get global system logger instance"""
    global _system_logger
    if _system_logger is None:
        _system_logger = SystemLogger()
    return _system_logger


def initialize_system_logger() -> SystemLogger:
    """Initialize global system logger"""
    global _system_logger
    _system_logger = SystemLogger()
    return _system_logger


# Convenience functions
def log_startup(host: str, port: int, model: str):
    """Log system startup"""
    logger = get_system_logger()
    logger.log_system_startup(host, port, model)


def log_shutdown(final_memory: str, uptime: float):
    """Log system shutdown"""
    logger = get_system_logger()
    logger.log_system_shutdown(final_memory, uptime)


def log_request(method: str, path: str, status: int, duration: float, request_id: str):
    """Log API request"""
    logger = get_system_logger()
    logger.log_endpoint_call(method, path, status, duration, request_id)


def log_error(error_type: str, message: str, context: Dict[str, Any]):
    """Log error"""
    logger = get_system_logger()
    logger.log_error(error_type, message, context)


def log_memory(context: str):
    """Log memory usage"""
    logger = get_system_logger()
    logger.log_memory_usage(context)


def log_connection(service: str, status: str, details: str):
    """Log connection status"""
    logger = get_system_logger()
    logger.log_connection_status(service, status, details)