import logging
import time
from datetime import datetime
from typing import Optional, Dict

from .fallback_processor import VLMFallbackProcessor, FallbackResult
from .config import VLMFallbackConfig
from .image_capture_manager import ImageCaptureManager

logger = logging.getLogger(__name__)

class EnhancedVLMFallbackProcessor(VLMFallbackProcessor):
    """
    增強型 VLM Fallback 處理器，支援圖片傳送。
    擴展自 VLMFallbackProcessor，保持向後兼容性。
    """
    
    def __init__(self, config: Optional[VLMFallbackConfig] = None):
        super().__init__(config)
        self.image_capture_manager = ImageCaptureManager()
        self.enable_image_fallback = config.enable_image_fallback if config else True
        
        # 重新初始化 prompt_manager 為 EnhancedPromptManager
        from .enhanced_prompt_manager import EnhancedPromptManager
        self.prompt_manager = EnhancedPromptManager(
            model_server_url=self.config.model_server_url,
            timeout=self.config.vlm_timeout,
            config=self.config
        )
    
    async def process_query_with_image_fallback(self, query: str, state_data: Optional[Dict]) -> Dict:
        """
        處理查詢，支援圖片傳送的 VLM Fallback。
        保持與原 process_query_with_fallback 相同的介面。
        """
        start_time = time.time()
        self.total_queries += 1
        
        try:
            # 決策：是否使用 VLM Fallback
            should_use_fallback = self.decision_engine.should_use_vlm_fallback(query, state_data)
            
            if should_use_fallback and self.enable_image_fallback:
                # 使用增強型 VLM Fallback（包含圖片）
                result = await self._execute_enhanced_vlm_fallback(query, state_data)
                self.fallback_queries += 1
            elif should_use_fallback:
                # 使用傳統 VLM Fallback（僅文字）
                result = await self._execute_vlm_fallback(query, state_data)
                self.fallback_queries += 1
            else:
                # 使用模板回應
                result = self._execute_template_response(query, state_data)
                self.template_queries += 1
            
            # 計算處理時間
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            
            return self._format_unified_response(result)
            
        except Exception as e:
            self.error_queries += 1
            processing_time = (time.time() - start_time) * 1000
            
            logger.error(f"Enhanced fallback processing failed: {e}")
            
            return self._format_unified_response(self._create_error_result(e, processing_time))
    
    async def _execute_enhanced_vlm_fallback(self, query: str, state_data: Optional[Dict]) -> FallbackResult:
        """
        執行包含圖片的 VLM Fallback。
        自動獲取當前圖片並傳送給 VLM。
        """
        try:
            logger.debug(f"Executing enhanced VLM fallback for query: '{query[:50]}...'")
            
            # 獲取當前圖片
            image_data = await self.image_capture_manager.get_current_image()
            
            if image_data:
                # 執行包含圖片的 VLM Fallback
                vlm_response = await self.prompt_manager.execute_fallback_with_image(
                    query, image_data
                )
                logger.info("Enhanced VLM fallback executed with image")
            else:
                # 回退到純文字 Fallback
                vlm_response = await self.prompt_manager.execute_fallback_with_prompt_switch(query)
                logger.info("Enhanced VLM fallback executed without image (fallback to text-only)")
            
            return FallbackResult(
                response_text=vlm_response,
                query_type=self._determine_apparent_query_type(query),
                response_mode="template",  # 保持透明性
                confidence=self._calculate_apparent_confidence(state_data),
                processing_time_ms=0.0,
                decision_reason="Enhanced VLM fallback (with image)",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Enhanced VLM fallback execution failed: {e}")
            return self._create_fallback_error_result(e, query)
    
    def _create_error_result(self, error: Exception, processing_time: float) -> FallbackResult:
        """創建錯誤結果"""
        return FallbackResult(
            response_text=f"Sorry, I encountered an error processing your query: {str(error)}",
            query_type="UNKNOWN",
            response_mode="template",
            confidence=0.5,
            processing_time_ms=processing_time,
            decision_reason=f"Error: {str(error)}",
            success=False,
            error_message=str(error)
        )
    
    def _create_fallback_error_result(self, error: Exception, query: str) -> FallbackResult:
        """創建 Fallback 錯誤結果"""
        return FallbackResult(
            response_text=f"I'm having trouble processing your request right now. Please try again.",
            query_type=self._determine_apparent_query_type(query),
            response_mode="template",
            confidence=0.6,
            processing_time_ms=0.0,
            decision_reason=f"Fallback error: {str(error)}",
            success=False,
            error_message=str(error)
        ) 