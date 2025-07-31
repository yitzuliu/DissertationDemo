"""
AI Manual Assistant System Technical Logger

Provides logging functionality for system-level events, including system startup/shutdown, memory usage,
endpoint calls and error handling.
"""

import psutil
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from log_manager import get_log_manager, LogManager, LogType


class SystemLogger:
    """
    System Technical Logger
    
    Responsible for logging system-level events, including:
    - System startup/shutdown events
    - Memory and CPU usage
    - Endpoint calls and API requests
    - Connection status and error handling
    """
    
    def __init__(self, system_id: Optional[str] = None):
        """
        Initialize system logger
        
        Args:
            system_id: System unique identifier, auto-generated if not provided
        """
        self.log_manager = get_log_manager()
        self.system_id = system_id or f"sys_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        self.start_time = time.time()
        self.process = psutil.Process()
        
    def log_system_startup(self, host: str = "localhost", port: int = 8000, model: str = "unknown", **kwargs):
        """
        Log system startup event
        
        Args:
            host: Host address
            port: Port number
            model: Model name being used
            **kwargs: Other startup parameters
        """
        self.log_manager.log_system_start(
            system_id=self.system_id,
            host=host,
            port=port,
            model=model
        )
        
        # Log memory usage at startup
        self.log_memory_usage()
        
        # Log other startup parameters
        if kwargs:
            for key, value in kwargs.items():
                self.log_manager.get_logger(LogType.SYSTEM).info(
                    f"[STARTUP_PARAM] system_id={self.system_id} {key}={value}"
                )
    
    def log_system_shutdown(self):
        """Log system shutdown event"""
        uptime = time.time() - self.start_time
        uptime_str = f"{uptime:.1f}s"
        
        # Log memory usage at shutdown
        memory_info = self.process.memory_info()
        final_memory = f"{memory_info.rss / 1024 / 1024:.1f}MB"
        
        self.log_manager.log_system_shutdown(
            system_id=self.system_id,
            final_memory=final_memory,
            uptime=uptime_str
        )
    
    def log_memory_usage(self, context: str = ""):
        """
        Log memory usage
        
        Args:
            context: Logging context (e.g., startup, request_processing, etc.)
        """
        try:
            memory_info = self.process.memory_info()
            memory_usage = f"{memory_info.rss / 1024 / 1024:.1f}MB"
            
            if context:
                memory_usage = f"{memory_usage} ({context})"
            
            self.log_manager.log_memory_usage(
                system_id=self.system_id,
                memory_usage=memory_usage
            )
        except Exception as e:
            self.log_error("memory_monitoring", str(e))
    
    def log_cpu_usage(self, context: str = ""):
        """
        Log CPU usage
        
        Args:
            context: Logging context
        """
        try:
            cpu_percent = self.process.cpu_percent()
            cpu_usage = f"{cpu_percent:.1f}%"
            
            if context:
                cpu_usage = f"{cpu_usage} ({context})"
            
            self.log_manager.get_logger(LogType.SYSTEM).info(
                f"[CPU_USAGE] system_id={self.system_id} cpu_usage={cpu_usage}"
            )
        except Exception as e:
            self.log_error("cpu_monitoring", str(e))  
  
    def log_endpoint_call(self, method: str, path: str, status_code: int, 
                         duration: float, request_id: Optional[str] = None,
                         client_ip: Optional[str] = None, **kwargs):
        """
        Log endpoint call
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration: Processing time (seconds)
            request_id: Request ID
            client_ip: Client IP
            **kwargs: Other request parameters
        """
        if not request_id:
            request_id = self.log_manager.generate_request_id()
        
        self.log_manager.log_endpoint_call(
            request_id=request_id,
            method=method,
            path=path,
            status=status_code,
            duration=duration
        )
        
        # Log additional request information
        if client_ip or kwargs:
            extra_info = []
            if client_ip:
                extra_info.append(f"client_ip={client_ip}")
            for key, value in kwargs.items():
                extra_info.append(f"{key}={value}")
            
            if extra_info:
                self.log_manager.get_logger(LogType.SYSTEM).info(
                    f"[ENDPOINT_EXTRA] request_id={request_id} {' '.join(extra_info)}"
                )
    
    def log_connection_status(self, service: str, status: str, 
                            details: Optional[str] = None):
        """
        Log connection status
        
        Args:
            service: Service name (e.g., frontend, model_server, database)
            status: Connection status (CONNECTED, DISCONNECTED, ERROR)
            details: Detailed information
        """
        message_parts = [f"[CONNECTION] system_id={self.system_id}",
                        f"service={service}", f"status={status}"]
        
        if details:
            message_parts.append(f"details={details}")
        
        message = " ".join(message_parts)
        self.log_manager.get_logger(LogType.SYSTEM).info(message)
    
    def log_error(self, error_type: str, error_message: str, 
                  context: Optional[Dict[str, Any]] = None,
                  request_id: Optional[str] = None):
        """
        Log error event
        
        Args:
            error_type: Error type
            error_message: Error message
            context: Error context
            request_id: Related request ID
        """
        message_parts = [f"[ERROR] system_id={self.system_id}",
                        f"type={error_type}", f"message={error_message}"]
        
        if request_id:
            message_parts.append(f"request_id={request_id}")
        
        if context:
            for key, value in context.items():
                message_parts.append(f"{key}={value}")
        
        message = " ".join(message_parts)
        self.log_manager.get_logger(LogType.SYSTEM).error(message)
    
    def log_performance_metric(self, metric_name: str, value: float, 
                              unit: str = "", context: Optional[str] = None):
        """
        Log performance metric
        
        Args:
            metric_name: Metric name
            value: Metric value
            unit: Unit
            context: Context
        """
        value_str = f"{value:.3f}{unit}" if unit else f"{value:.3f}"
        
        message_parts = [f"[PERFORMANCE] system_id={self.system_id}",
                        f"metric={metric_name}", f"value={value_str}"]
        
        if context:
            message_parts.append(f"context={context}")
        
        message = " ".join(message_parts)
        self.log_manager.get_logger(LogType.SYSTEM).info(message)
    
    def log_health_check(self, component: str, status: str, 
                        response_time: Optional[float] = None,
                        details: Optional[Dict[str, Any]] = None):
        """
        Log health check result
        
        Args:
            component: Component name
            status: Health status (HEALTHY, UNHEALTHY, DEGRADED)
            response_time: Response time
            details: Detailed information
        """
        message_parts = [f"[HEALTH_CHECK] system_id={self.system_id}",
                        f"component={component}", f"status={status}"]
        
        if response_time is not None:
            message_parts.append(f"response_time={response_time:.3f}ms")
        
        if details:
            for key, value in details.items():
                message_parts.append(f"{key}={value}")
        
        message = " ".join(message_parts)
        self.log_manager.get_logger(LogType.SYSTEM).info(message)   
 
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information
        
        Returns:
            Dictionary containing system information
        """
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
            
            return {
                "system_id": self.system_id,
                "uptime": time.time() - self.start_time,
                "memory_mb": memory_info.rss / 1024 / 1024,
                "cpu_percent": cpu_percent,
                "pid": self.process.pid
            }
        except Exception as e:
            self.log_error("system_info_collection", str(e))
            return {"system_id": self.system_id, "error": str(e)}


# Global system logger instance
_system_logger_instance: Optional[SystemLogger] = None


def get_system_logger() -> SystemLogger:
    """Get global system logger instance"""
    global _system_logger_instance
    if _system_logger_instance is None:
        _system_logger_instance = SystemLogger()
    return _system_logger_instance


def initialize_system_logger(system_id: Optional[str] = None) -> SystemLogger:
    """
    Initialize global system logger
    
    Args:
        system_id: System unique identifier
        
    Returns:
        System logger instance
    """
    global _system_logger_instance
    _system_logger_instance = SystemLogger(system_id)
    return _system_logger_instance


# Convenience functions
def log_startup(host: str = "localhost", port: int = 8000, 
                model: str = "unknown", **kwargs):
    """Convenient system startup logging"""
    get_system_logger().log_system_startup(host, port, model, **kwargs)


def log_shutdown():
    """Convenient system shutdown logging"""
    get_system_logger().log_system_shutdown()


def log_request(method: str, path: str, status_code: int, duration: float,
                request_id: Optional[str] = None, **kwargs):
    """Convenient request logging"""
    get_system_logger().log_endpoint_call(
        method, path, status_code, duration, request_id, **kwargs
    )


def log_error(error_type: str, error_message: str, 
              context: Optional[Dict[str, Any]] = None,
              request_id: Optional[str] = None):
    """Convenient error logging"""
    get_system_logger().log_error(error_type, error_message, context, request_id)


def log_memory():
    """Convenient memory usage logging"""
    get_system_logger().log_memory_usage()


def log_connection(service: str, status: str, details: Optional[str] = None):
    """Convenient connection status logging"""
    get_system_logger().log_connection_status(service, status, details)