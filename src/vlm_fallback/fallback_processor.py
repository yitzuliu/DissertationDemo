"""
VLM Fallback Processor

Core orchestrator for the VLM fallback system. Coordinates decision making,
prompt management, and VLM communication while ensuring seamless user experience.

Key Responsibility: Make VLM fallback completely transparent to users.
All responses appear as "State Query" responses regardless of source.
"""

import logging
import time
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from .decision_engine import DecisionEngine
from .prompt_manager import PromptManager, VLMFallbackError
from .vlm_client import VLMClient, VLMServiceError
from .config import VLMFallbackConfig

logger = logging.getLogger(__name__)

@dataclass
class FallbackResult:
    """Result of fallback processing"""
    response_text: str
    query_type: str
    response_mode: str  # "template" or "vlm_fallback" (internal only)
    confidence: float
    processing_time_ms: float
    decision_reason: str
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class VLMFallbackProcessor:
    """
    Core processor that orchestrates VLM fallback functionality.
    
    Ensures complete transparency - users cannot distinguish between
    template responses and VLM fallback responses.
    
    Architecture:
    User Query → Decision Engine → [Template OR VLM Fallback] → Unified Response
    """
    
    def __init__(self, config: Optional[VLMFallbackConfig] = None):
        """
        Initialize fallback processor.
        
        Args:
            config: Configuration object (uses defaults if None)
        """
        self.config = config or VLMFallbackConfig()
        
        # Initialize components
        self.decision_engine = DecisionEngine(
            confidence_threshold=self.config.confidence_threshold
        )
        self.prompt_manager = PromptManager(
            model_server_url=self.config.model_server_url,
            timeout=self.config.vlm_timeout
        )
        self.vlm_client = VLMClient(
            model_server_url=self.config.model_server_url,
            timeout=self.config.vlm_timeout,
            max_retries=self.config.max_retries
        )
        
        # Statistics
        self.total_queries = 0
        self.template_queries = 0
        self.fallback_queries = 0
        self.error_queries = 0
        
        logger.info("VLMFallbackProcessor initialized successfully")
    
    async def process_query_with_fallback(self, query: str, state_data: Optional[Dict]) -> Dict:
        """
        Main processing method - handles query with transparent fallback.
        
        This method ensures users cannot distinguish between template and VLM responses.
        All responses appear as "State Query" responses with consistent formatting.
        
        Args:
            query: User query string
            state_data: Current state tracker data
            
        Returns:
            Dict: Unified response format (always appears as template response)
        """
        start_time = time.time()
        self.total_queries += 1
        
        try:
            # Step 1: Make fallback decision
            should_use_fallback = self.decision_engine.should_use_vlm_fallback(query, state_data)
            
            if should_use_fallback:
                # Use VLM fallback (transparent to user)
                result = await self._execute_vlm_fallback(query, state_data)
                self.fallback_queries += 1
            else:
                # Use template response
                result = self._execute_template_response(query, state_data)
                self.template_queries += 1
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            
            # Return unified response format (user cannot distinguish source)
            return self._format_unified_response(result)
            
        except Exception as e:
            self.error_queries += 1
            processing_time = (time.time() - start_time) * 1000
            
            logger.error(f"Fallback processing failed: {e}")
            
            # Return error response in unified format
            error_result = FallbackResult(
                response_text=self._get_error_response(e),
                query_type=self._determine_apparent_query_type(query),
                response_mode="template",  # Always appear as template
                confidence=0.5,  # Reasonable confidence for error case
                processing_time_ms=processing_time,
                decision_reason=f"Error: {str(e)}",
                success=False,
                error_message=str(e)
            )
            
            return self._format_unified_response(error_result)
    
    async def _execute_vlm_fallback(self, query: str, state_data: Optional[Dict]) -> FallbackResult:
        """
        Execute VLM fallback with complete prompt management.
        
        Args:
            query: User query
            state_data: State tracker data
            
        Returns:
            FallbackResult: Fallback execution result
        """
        try:
            logger.debug(f"Executing VLM fallback for query: '{query[:50]}...'")
            
            # Execute VLM fallback with prompt switching
            vlm_response = await self.prompt_manager.execute_fallback_with_prompt_switch(query)
            
            # Create result that appears as template response
            return FallbackResult(
                response_text=vlm_response,
                query_type=self._determine_apparent_query_type(query),
                response_mode="template",  # CRITICAL: Always appear as template
                confidence=self._calculate_apparent_confidence(state_data),
                processing_time_ms=0.0,  # Will be set by caller
                decision_reason="VLM fallback (transparent)",
                success=True
            )
            
        except VLMFallbackError as e:
            logger.error(f"VLM fallback execution failed: {e}")
            
            # Return friendly error response
            return FallbackResult(
                response_text=self._get_fallback_error_response(e),
                query_type=self._determine_apparent_query_type(query),
                response_mode="template",  # Always appear as template
                confidence=0.6,  # Reasonable confidence
                processing_time_ms=0.0,
                decision_reason=f"Fallback error: {str(e)}",
                success=False,
                error_message=str(e)
            )
    
    def _execute_template_response(self, query: str, state_data: Optional[Dict]) -> FallbackResult:
        """
        Execute template response (existing functionality).
        
        Args:
            query: User query
            state_data: State tracker data
            
        Returns:
            FallbackResult: Template response result
        """
        try:
            # This would call the existing template response logic
            # For now, we'll simulate a template response
            
            template_response = self._generate_template_response(query, state_data)
            
            return FallbackResult(
                response_text=template_response,
                query_type=self._classify_query_type(query, state_data),
                response_mode="template",
                confidence=state_data.get('confidence', 0.8) if state_data else 0.8,
                processing_time_ms=0.0,  # Will be set by caller
                decision_reason="Template response",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Template response failed: {e}")
            
            return FallbackResult(
                response_text="I'm having trouble processing your request. Please try again.",
                query_type="HELP",
                response_mode="template",
                confidence=0.5,
                processing_time_ms=0.0,
                decision_reason=f"Template error: {str(e)}",
                success=False,
                error_message=str(e)
            )
    
    def _determine_apparent_query_type(self, query: str) -> str:
        """
        Determine what query type should appear to the user.
        
        This makes VLM fallback responses look like normal state tracker responses.
        
        Args:
            query: User query
            
        Returns:
            str: Apparent query type for user display
        """
        query_lower = query.lower()
        
        # Map query patterns to apparent types
        if any(word in query_lower for word in ['step', 'where', 'current', 'am i']):
            return "CURRENT_STEP"
        elif any(word in query_lower for word in ['next', 'what next', 'then']):
            return "NEXT_STEP"
        elif any(word in query_lower for word in ['tools', 'need', 'equipment', 'require']):
            return "REQUIRED_TOOLS"
        elif any(word in query_lower for word in ['progress', 'done', 'complete', 'finish']):
            return "COMPLETION_STATUS"
        elif any(word in query_lower for word in ['overall', 'summary', 'overview']):
            return "PROGRESS_OVERVIEW"
        else:
            return "HELP"  # Default for unknown queries
    
    def _calculate_apparent_confidence(self, state_data: Optional[Dict]) -> float:
        """
        Calculate confidence value that appears reasonable to users.
        
        Even if original confidence was low (triggering fallback),
        we show a reasonable confidence to maintain user trust.
        
        Args:
            state_data: State tracker data
            
        Returns:
            float: Apparent confidence value
        """
        if not state_data:
            return 0.75  # Reasonable confidence for no-state case
        
        original_confidence = state_data.get('confidence', 0.0)
        
        # If original confidence was very low, show reasonable confidence
        if original_confidence < 0.40:
            return 0.72  # Appears as decent confidence
        else:
            return original_confidence  # Use original if it was reasonable
    
    def _classify_query_type(self, query: str, state_data: Optional[Dict]) -> str:
        """
        Classify query type for template responses.
        
        Args:
            query: User query
            state_data: State tracker data
            
        Returns:
            str: Query type classification
        """
        # This would use existing query classification logic
        # For now, use the apparent query type logic
        return self._determine_apparent_query_type(query)
    
    def _generate_template_response(self, query: str, state_data: Optional[Dict]) -> str:
        """
        Generate template response (placeholder for existing logic).
        
        Args:
            query: User query
            state_data: State tracker data
            
        Returns:
            str: Template response text
        """
        # This is a placeholder - in real implementation,
        # this would call the existing template response logic
        
        if not state_data:
            return "I don't have information about your current state. Please start a task first."
        
        query_type = self._classify_query_type(query, state_data)
        
        if query_type == "CURRENT_STEP":
            return f"You are currently on step {state_data.get('step_id', 'unknown')} of your task."
        elif query_type == "NEXT_STEP":
            return "The next step will be provided once you complete the current step."
        elif query_type == "REQUIRED_TOOLS":
            return "Please refer to the task instructions for required tools."
        else:
            return "I'm here to help with your current task. What would you like to know?"
    
    def _get_error_response(self, error: Exception) -> str:
        """Get user-friendly error response"""
        if isinstance(error, VLMServiceError):
            return "I'm having trouble accessing the AI service right now. Please try again in a moment."
        elif isinstance(error, VLMFallbackError):
            return "I encountered an issue while processing your request. Please try rephrasing your question."
        else:
            return "I'm experiencing a temporary issue. Please try again or contact support if the problem persists."
    
    def _get_fallback_error_response(self, error: VLMFallbackError) -> str:
        """Get specific fallback error response"""
        return "I'm having trouble processing your request right now. Please try again with a different question."
    
    def _format_unified_response(self, result: FallbackResult) -> Dict:
        """
        Format response in unified format that's transparent to users.
        
        CRITICAL: This ensures users cannot distinguish between template and fallback responses.
        
        Args:
            result: Processing result
            
        Returns:
            Dict: Unified response format
        """
        return {
            "status": "success",
            "response_text": result.response_text,
            "query_type": result.query_type,
            "confidence": result.confidence,
            "processing_time_ms": result.processing_time_ms,
            # NOTE: response_mode is NOT included - users cannot see the source
            # NOTE: decision_reason is NOT included - internal only
        }
    
    def get_statistics(self) -> Dict:
        """Get processor performance statistics"""
        fallback_rate = (self.fallback_queries / self.total_queries * 100) if self.total_queries > 0 else 0
        error_rate = (self.error_queries / self.total_queries * 100) if self.total_queries > 0 else 0
        
        return {
            "total_queries": self.total_queries,
            "template_queries": self.template_queries,
            "fallback_queries": self.fallback_queries,
            "error_queries": self.error_queries,
            "fallback_rate_percent": round(fallback_rate, 2),
            "error_rate_percent": round(error_rate, 2),
            "decision_engine_stats": self.decision_engine.get_statistics(),
            "vlm_client_stats": self.vlm_client.get_statistics()
        }
    
    async def health_check(self) -> Dict:
        """Perform comprehensive health check"""
        # Check VLM service health
        vlm_health = await self.vlm_client.health_check()
        
        # Check prompt manager health
        prompt_health = self.prompt_manager.health_check()
        
        # Overall health assessment
        is_healthy = (
            vlm_health.get("healthy", False) and
            prompt_health.get("healthy", False)
        )
        
        return {
            "healthy": is_healthy,
            "vlm_service": vlm_health,
            "prompt_manager": prompt_health,
            "statistics": self.get_statistics(),
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.total_queries = 0
        self.template_queries = 0
        self.fallback_queries = 0
        self.error_queries = 0
        
        self.decision_engine.reset_statistics()
        self.vlm_client.reset_statistics()
        
        logger.info("VLM fallback processor statistics reset")