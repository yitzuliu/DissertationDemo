"""
AI Manual Assistant 系統技術日誌記錄器

提供系統級事件的日誌記錄功能，包括系統啟動/關閉、記憶體使用、
端點呼叫和錯誤處理等。
"""

import psutil
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from log_manager import get_log_manager, LogManager, LogType


class SystemLogger:
    """
    系統技術日誌記錄器
    
    負責記錄系統級事件，包括：
    - 系統啟動/關閉事件
    - 記憶體和CPU使用情況
    - 端點呼叫和API請求
    - 連線狀態和錯誤處理
    """
    
    def __init__(self, system_id: Optional[str] = None):
        """
        初始化系統日誌記錄器
        
        Args:
            system_id: 系統唯一識別碼，如果未提供則自動生成
        """
        self.log_manager = get_log_manager()
        self.system_id = system_id or f"sys_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        self.start_time = time.time()
        self.process = psutil.Process()
        
    def log_system_startup(self, host: str = "localhost", port: int = 8000, model: str = "unknown", **kwargs):
        """
        記錄系統啟動事件
        
        Args:
            host: 主機地址
            port: 端口號
            model: 使用的模型名稱
            **kwargs: 其他啟動參數
        """
        self.log_manager.log_system_start(
            system_id=self.system_id,
            host=host,
            port=port,
            model=model
        )
        
        # 記錄啟動時的記憶體使用
        self.log_memory_usage()
        
        # 記錄其他啟動參數
        if kwargs:
            for key, value in kwargs.items():
                self.log_manager.get_logger(LogType.SYSTEM).info(
                    f"[STARTUP_PARAM] system_id={self.system_id} {key}={value}"
                )
    
    def log_system_shutdown(self):
        """記錄系統關閉事件"""
        uptime = time.time() - self.start_time
        uptime_str = f"{uptime:.1f}s"
        
        # 記錄關閉時的記憶體使用
        memory_info = self.process.memory_info()
        final_memory = f"{memory_info.rss / 1024 / 1024:.1f}MB"
        
        self.log_manager.log_system_shutdown(
            system_id=self.system_id,
            final_memory=final_memory,
            uptime=uptime_str
        )
    
    def log_memory_usage(self, context: str = ""):
        """
        記錄記憶體使用情況
        
        Args:
            context: 記錄上下文（如 startup, request_processing 等）
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
        記錄CPU使用情況
        
        Args:
            context: 記錄上下文
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
        記錄端點呼叫
        
        Args:
            method: HTTP方法
            path: 請求路徑
            status_code: 回應狀態碼
            duration: 處理時間（秒）
            request_id: 請求ID
            client_ip: 客戶端IP
            **kwargs: 其他請求參數
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
        
        # 記錄額外的請求資訊
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
        記錄連線狀態
        
        Args:
            service: 服務名稱（如 frontend, model_server, database）
            status: 連線狀態（CONNECTED, DISCONNECTED, ERROR）
            details: 詳細資訊
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
        記錄錯誤事件
        
        Args:
            error_type: 錯誤類型
            error_message: 錯誤訊息
            context: 錯誤上下文
            request_id: 相關的請求ID
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
        記錄性能指標
        
        Args:
            metric_name: 指標名稱
            value: 指標值
            unit: 單位
            context: 上下文
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
        記錄健康檢查結果
        
        Args:
            component: 組件名稱
            status: 健康狀態（HEALTHY, UNHEALTHY, DEGRADED）
            response_time: 響應時間
            details: 詳細資訊
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
        獲取系統資訊
        
        Returns:
            包含系統資訊的字典
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


# 全域系統日誌記錄器實例
_system_logger_instance: Optional[SystemLogger] = None


def get_system_logger() -> SystemLogger:
    """獲取全域系統日誌記錄器實例"""
    global _system_logger_instance
    if _system_logger_instance is None:
        _system_logger_instance = SystemLogger()
    return _system_logger_instance


def initialize_system_logger(system_id: Optional[str] = None) -> SystemLogger:
    """
    初始化全域系統日誌記錄器
    
    Args:
        system_id: 系統唯一識別碼
        
    Returns:
        系統日誌記錄器實例
    """
    global _system_logger_instance
    _system_logger_instance = SystemLogger(system_id)
    return _system_logger_instance


# 便捷函數
def log_startup(host: str = "localhost", port: int = 8000, 
                model: str = "unknown", **kwargs):
    """便捷的系統啟動日誌記錄"""
    get_system_logger().log_system_startup(host, port, model, **kwargs)


def log_shutdown():
    """便捷的系統關閉日誌記錄"""
    get_system_logger().log_system_shutdown()


def log_request(method: str, path: str, status_code: int, duration: float,
                request_id: Optional[str] = None, **kwargs):
    """便捷的請求日誌記錄"""
    get_system_logger().log_endpoint_call(
        method, path, status_code, duration, request_id, **kwargs
    )


def log_error(error_type: str, error_message: str, 
              context: Optional[Dict[str, Any]] = None,
              request_id: Optional[str] = None):
    """便捷的錯誤日誌記錄"""
    get_system_logger().log_error(error_type, error_message, context, request_id)


def log_memory():
    """便捷的記憶體使用日誌記錄"""
    get_system_logger().log_memory_usage()


def log_connection(service: str, status: str, details: Optional[str] = None):
    """便捷的連線狀態日誌記錄"""
    get_system_logger().log_connection_status(service, status, details)