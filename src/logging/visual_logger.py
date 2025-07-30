#!/usr/bin/env python3
"""
AI Manual Assistant 視覺日誌記錄器

提供VLM視覺處理相關的日誌記錄功能，包括：
- 後端接收日誌
- 圖像處理過程和結果
- RAG系統資料傳遞
- 狀態追蹤器整合
"""

import time
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from log_manager import get_log_manager, LogManager, LogType


class VisualLogger:
    """
    視覺日誌記錄器
    
    負責記錄VLM視覺處理相關的事件，包括：
    - 後端接收處理
    - 圖像處理過程
    - RAG匹配過程
    - 狀態更新過程
    """
    
    def __init__(self):
        """初始化視覺日誌記錄器"""
        self.log_manager = get_log_manager()
        
    def log_backend_receive(self, observation_id: str, request_id: str, 
                           request_data: Dict[str, Any]):
        """
        記錄後端接收VLM請求
        
        Args:
            observation_id: 觀察ID
            request_id: 請求ID
            request_data: 請求數據
        """
        # 安全地處理圖像數據，避免記錄完整的base64
        safe_request_data = self._sanitize_request_data(request_data)
        
        message = (f"[BACKEND_RECEIVE] observation_id={observation_id} "
                  f"request_id={request_id} "
                  f"data={json.dumps(safe_request_data, ensure_ascii=False)}")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_image_processing_start(self, observation_id: str, request_id: str,
                                  image_count: int, model: str):
        """
        記錄圖像處理開始
        
        Args:
            observation_id: 觀察ID
            request_id: 請求ID
            image_count: 圖像數量
            model: 使用的模型
        """
        message = (f"[IMAGE_PROCESSING_START] observation_id={observation_id} "
                  f"request_id={request_id} image_count={image_count} "
                  f"model={model}")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_image_processing_result(self, observation_id: str, request_id: str,
                                   processing_time: float, success: bool,
                                   details: Optional[Dict[str, Any]] = None):
        """
        記錄圖像處理結果
        
        Args:
            observation_id: 觀察ID
            request_id: 請求ID
            processing_time: 處理時間（秒）
            success: 是否成功
            details: 處理詳情
        """
        status = "SUCCESS" if success else "FAILED"
        message_parts = [
            f"[IMAGE_PROCESSING_RESULT] observation_id={observation_id}",
            f"request_id={request_id}",
            f"status={status}",
            f"processing_time={processing_time:.3f}s"
        ]
        
        if details:
            for key, value in details.items():
                message_parts.append(f"{key}={value}")
        
        message = " ".join(message_parts)
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_vlm_request(self, observation_id: str, request_id: str,
                       model: str, prompt_length: int, image_count: int):
        """
        記錄VLM模型請求
        
        Args:
            observation_id: 觀察ID
            request_id: 請求ID
            model: 模型名稱
            prompt_length: 提示詞長度
            image_count: 圖像數量
        """
        message = (f"[VLM_REQUEST] observation_id={observation_id} "
                  f"request_id={request_id} model={model} "
                  f"prompt_length={prompt_length} image_count={image_count}")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_vlm_response(self, observation_id: str, request_id: str,
                        response_length: int, processing_time: float,
                        success: bool, model: str):
        """
        記錄VLM模型回應
        
        Args:
            observation_id: 觀察ID
            request_id: 請求ID
            response_length: 回應長度
            processing_time: 處理時間
            success: 是否成功
            model: 模型名稱
        """
        status = "SUCCESS" if success else "FAILED"
        message = (f"[VLM_RESPONSE] observation_id={observation_id} "
                  f"request_id={request_id} model={model} status={status} "
                  f"response_length={response_length} "
                  f"processing_time={processing_time:.3f}s")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_rag_data_transfer(self, observation_id: str, vlm_text: str,
                             transfer_success: bool):
        """
        記錄RAG系統資料傳遞
        
        Args:
            observation_id: 觀察ID
            vlm_text: VLM輸出文本
            transfer_success: 傳遞是否成功
        """
        status = "SUCCESS" if transfer_success else "FAILED"
        text_preview = vlm_text[:100] + "..." if len(vlm_text) > 100 else vlm_text
        
        message = (f"[RAG_DATA_TRANSFER] observation_id={observation_id} "
                  f"status={status} text_length={len(vlm_text)} "
                  f"text_preview={json.dumps(text_preview, ensure_ascii=False)}")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_state_tracker_integration(self, observation_id: str, 
                                     state_updated: bool, 
                                     processing_time: Optional[float] = None):
        """
        記錄狀態追蹤器整合
        
        Args:
            observation_id: 觀察ID
            state_updated: 狀態是否更新
            processing_time: 處理時間
        """
        message_parts = [
            f"[STATE_TRACKER_INTEGRATION] observation_id={observation_id}",
            f"state_updated={state_updated}"
        ]
        
        if processing_time is not None:
            message_parts.append(f"processing_time={processing_time:.3f}s")
        
        message = " ".join(message_parts)
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def log_error(self, observation_id: str, request_id: str, 
                  error_type: str, error_message: str, 
                  context: Optional[str] = None):
        """
        記錄視覺處理錯誤
        
        Args:
            observation_id: 觀察ID
            request_id: 請求ID
            error_type: 錯誤類型
            error_message: 錯誤訊息
            context: 錯誤上下文
        """
        message_parts = [
            f"[VISUAL_ERROR] observation_id={observation_id}",
            f"request_id={request_id}",
            f"error_type={error_type}",
            f"error_message={json.dumps(error_message, ensure_ascii=False)}"
        ]
        
        if context:
            message_parts.append(f"context={context}")
        
        message = " ".join(message_parts)
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.error(message)
    
    def log_performance_metric(self, observation_id: str, metric_name: str,
                              value: float, unit: str = ""):
        """
        記錄性能指標
        
        Args:
            observation_id: 觀察ID
            metric_name: 指標名稱
            value: 指標值
            unit: 單位
        """
        value_str = f"{value:.3f}{unit}" if unit else f"{value:.3f}"
        message = (f"[VISUAL_PERFORMANCE] observation_id={observation_id} "
                  f"metric={metric_name} value={value_str}")
        
        logger = self.log_manager.get_logger(LogType.VISUAL)
        logger.info(message)
    
    def _sanitize_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理請求數據，移除敏感或過大的內容
        
        Args:
            request_data: 原始請求數據
            
        Returns:
            清理後的請求數據
        """
        safe_data = {}
        
        for key, value in request_data.items():
            if key == "messages" and isinstance(value, list):
                # 處理消息列表，移除圖像數據
                safe_messages = []
                for message in value:
                    safe_message = {"role": message.get("role", "unknown")}
                    
                    content = message.get("content")
                    if isinstance(content, str):
                        # 文本內容，截斷過長的內容
                        safe_message["content"] = content[:200] + "..." if len(content) > 200 else content
                    elif isinstance(content, list):
                        # 多模態內容
                        safe_content = []
                        for item in content:
                            if isinstance(item, dict):
                                if item.get("type") == "text":
                                    text = item.get("text", "")
                                    safe_content.append({
                                        "type": "text",
                                        "text": text[:200] + "..." if len(text) > 200 else text
                                    })
                                elif item.get("type") == "image_url":
                                    safe_content.append({
                                        "type": "image_url",
                                        "image_url": {"url": "[IMAGE_DATA_REMOVED]"}
                                    })
                        safe_message["content"] = safe_content
                    
                    safe_messages.append(safe_message)
                safe_data[key] = safe_messages
            elif key in ["max_tokens", "temperature", "top_p", "model"]:
                # 保留這些參數
                safe_data[key] = value
            else:
                # 其他參數轉為字符串並截斷
                str_value = str(value)
                safe_data[key] = str_value[:100] + "..." if len(str_value) > 100 else str_value
        
        return safe_data


# 全域視覺日誌記錄器實例
_visual_logger_instance: Optional[VisualLogger] = None


def get_visual_logger() -> VisualLogger:
    """
    獲取全域視覺日誌記錄器實例
    
    Returns:
        VisualLogger 實例
    """
    global _visual_logger_instance
    if _visual_logger_instance is None:
        _visual_logger_instance = VisualLogger()
    return _visual_logger_instance


# 便捷函數
def log_backend_receive(observation_id: str, request_id: str, request_data: Dict[str, Any]):
    """便捷的後端接收日誌記錄"""
    get_visual_logger().log_backend_receive(observation_id, request_id, request_data)


def log_image_processing(observation_id: str, request_id: str, 
                        processing_time: float, success: bool, **kwargs):
    """便捷的圖像處理日誌記錄"""
    get_visual_logger().log_image_processing_result(
        observation_id, request_id, processing_time, success, kwargs
    )


def log_vlm_interaction(observation_id: str, request_id: str, model: str,
                       request_time: float, response_time: float, success: bool):
    """便捷的VLM交互日誌記錄"""
    visual_logger = get_visual_logger()
    visual_logger.log_vlm_request(observation_id, request_id, model, 0, 0)
    visual_logger.log_vlm_response(observation_id, request_id, 0, response_time, success, model)


def log_visual_error(observation_id: str, request_id: str, error: Exception, context: str = ""):
    """便捷的視覺錯誤日誌記錄"""
    get_visual_logger().log_error(
        observation_id, request_id, type(error).__name__, str(error), context
    )