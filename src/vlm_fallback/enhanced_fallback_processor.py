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
    Enhanced VLM Fallback Processor with image support.
    Extends VLMFallbackProcessor to provide image-aware fallback capabilities.
    """
    
    def __init__(self, config: Optional[VLMFallbackConfig] = None):
        super().__init__(config)
        self.image_capture_manager = ImageCaptureManager()
        self.enable_image_fallback = config.enable_image_fallback if config else True
        
        # Re-initialize prompt_manager as EnhancedPromptManager
        from .enhanced_prompt_manager import EnhancedPromptManager
        self.prompt_manager = EnhancedPromptManager(
            model_server_url=self.config.model_server_url,
            timeout=self.config.vlm_timeout,
            config=self.config
        )
    
    async def process_query_with_image_fallback(self, query: str, state_data: Optional[Dict]) -> Dict:
        """
        Process query with image-aware VLM Fallback support.
        Maintains the same interface as process_query_with_fallback.
        """
        start_time = time.time()
        self.total_queries += 1
        
        try:
            # Decision: whether to use VLM Fallback
            should_use_fallback = self.decision_engine.should_use_vlm_fallback(query, state_data)
            
            if should_use_fallback and self.enable_image_fallback:
                # Use Enhanced VLM Fallback (with image support)
                result = await self._execute_enhanced_vlm_fallback(query, state_data)
                self.fallback_queries += 1
            elif should_use_fallback:
                # Use traditional VLM Fallback (text-only)
                result = await self._execute_vlm_fallback(query, state_data)
                self.fallback_queries += 1
            else:
                # Use template response
                result = self._execute_template_response(query, state_data)
                self.template_queries += 1
            
            # Calculate processing time
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
        Execute VLM Fallback with image support.
        Automatically captures current image and sends it to VLM.
        """
        try:
            logger.debug(f"Executing enhanced VLM fallback for query: '{query[:50]}...'")
            
            # Get current image
            image_data = await self.image_capture_manager.get_current_image()
            
            if image_data:
                # Execute VLM Fallback with image
                vlm_response = await self.prompt_manager.execute_fallback_with_image(
                    query, image_data
                )
                logger.info("Enhanced VLM fallback executed with image")
            else:
                # Fallback to text-only Fallback
                vlm_response = await self.prompt_manager.execute_fallback_with_prompt_switch(query)
                logger.info("Enhanced VLM fallback executed without image (fallback to text-only)")
            
            return FallbackResult(
                response_text=vlm_response,
                query_type=self._determine_apparent_query_type(query),
                response_mode="template",  # Maintain transparency
                confidence=self._calculate_apparent_confidence(state_data),
                processing_time_ms=0.0,
                decision_reason="Enhanced VLM fallback (with image)",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Enhanced VLM fallback execution failed: {e}")
            return self._create_fallback_error_result(e, query)
    
    def _create_error_result(self, error: Exception, processing_time: float) -> FallbackResult:
        """Create error result"""
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
        """Create Fallback error result"""
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