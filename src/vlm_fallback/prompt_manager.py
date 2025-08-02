"""
Prompt Manager for VLM Fallback System

Manages VLM prompt switching and restoration to ensure the VLM can continue
its state tracking function after providing fallback responses.

Critical Flow:
1. Save current state tracking prompt
2. Switch to fallback prompt  
3. Execute VLM query
4. Restore original state tracking prompt (CRITICAL!)
"""

import logging
import asyncio
import httpx
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class PromptState(Enum):
    """VLM prompt states"""
    TRACKING = "tracking"      # Normal state tracking mode
    FALLBACK = "fallback"      # Temporary fallback mode
    ERROR = "error"           # Error state
    UNKNOWN = "unknown"       # Unknown state

@dataclass
class PromptOperation:
    """Record of prompt operation"""
    operation_type: str
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    prompt_preview: Optional[str] = None

class VLMFallbackError(Exception):
    """VLM Fallback system errors"""
    pass

class PromptSwitchError(VLMFallbackError):
    """Prompt switching errors"""
    pass

class PromptRestoreError(VLMFallbackError):
    """Prompt restoration errors"""
    pass

class PromptManager:
    """
    Manages VLM prompt switching for fallback functionality.
    
    CRITICAL: This class ensures VLM can continue state tracking after fallback.
    The restore_original_prompt() method is essential for system integrity.
    """
    
    def __init__(self, model_server_url: str = "http://localhost:8080", timeout: int = 30):
        """
        Initialize prompt manager.
        
        Args:
            model_server_url: VLM service URL
            timeout: Request timeout in seconds
        """
        self.model_server_url = model_server_url
        self.timeout = timeout
        self.current_state = PromptState.UNKNOWN
        self.original_prompt = None
        self.operation_history = []
        
        # Fallback prompt template
        self.fallback_prompt_template = """You are a helpful AI assistant. Please answer the user's question directly and helpfully.

User Question: {query}

Please provide a clear, accurate, and helpful response. Focus on:
- Being informative and accurate
- Providing practical guidance when appropriate  
- Being concise but complete
- Using a friendly and supportive tone

Answer:"""
        
        logger.info(f"PromptManager initialized for VLM service: {model_server_url}")
    
    async def execute_fallback_with_prompt_switch(self, query: str) -> str:
        """
        Execute complete fallback flow with prompt switching.
        
        This is the main method that orchestrates the entire process:
        1. Save current prompt
        2. Switch to fallback prompt
        3. Execute VLM query
        4. Restore original prompt (CRITICAL!)
        
        Args:
            query: User query to process
            
        Returns:
            str: VLM response
            
        Raises:
            PromptSwitchError: If prompt switching fails
            PromptRestoreError: If prompt restoration fails
        """
        operation_start = datetime.now()
        
        try:
            logger.info(f"Starting fallback execution for query: '{query[:50]}...'")
            
            # Step 1: Save current state tracking prompt
            await self._save_current_prompt()
            
            # Step 2: Switch to fallback prompt
            await self._switch_to_fallback_prompt(query)
            
            # Step 3: Execute VLM query
            response = await self._execute_vlm_query(query)
            
            # Step 4: Restore original prompt (CRITICAL!)
            await self._restore_original_prompt()
            
            operation_time = (datetime.now() - operation_start).total_seconds()
            logger.info(f"Fallback execution completed successfully in {operation_time:.2f}s")
            
            return response
            
        except Exception as e:
            # CRITICAL: Always try to restore prompt even if error occurs
            try:
                await self._restore_original_prompt()
                logger.warning("Original prompt restored after error")
            except Exception as restore_error:
                logger.error(f"CRITICAL: Failed to restore prompt after error: {restore_error}")
                # This is a critical system error
                raise PromptRestoreError(f"Failed to restore prompt: {restore_error}") from e
            
            # Re-raise original error
            raise PromptSwitchError(f"Fallback execution failed: {e}") from e
    
    async def _save_current_prompt(self) -> bool:
        """
        Save the current VLM state tracking prompt.
        
        Returns:
            bool: Success status
        """
        try:
            # Get current prompt from VLM service
            # Note: This is a simplified implementation
            # In practice, you might need to call a specific endpoint to get current prompt
            
            # For now, we'll simulate saving the state tracking prompt
            # In real implementation, this would call the VLM service to get current prompt
            self.original_prompt = "STATE_TRACKING_PROMPT_PLACEHOLDER"
            self.current_state = PromptState.TRACKING
            
            self._record_operation("save_prompt", True, "State tracking prompt saved")
            logger.debug("Current state tracking prompt saved successfully")
            return True
            
        except Exception as e:
            self._record_operation("save_prompt", False, str(e))
            logger.error(f"Failed to save current prompt: {e}")
            raise PromptSwitchError(f"Failed to save current prompt: {e}")
    
    async def _switch_to_fallback_prompt(self, query: str) -> bool:
        """
        Switch VLM to fallback prompt mode.
        
        Args:
            query: User query to include in prompt
            
        Returns:
            bool: Success status
        """
        try:
            # Format fallback prompt with user query
            fallback_prompt = self.fallback_prompt_template.format(query=query)
            
            # Switch VLM to fallback mode
            # Note: This is a simplified implementation
            # In practice, you would call VLM service to update the system prompt
            
            success = await self._update_vlm_prompt(fallback_prompt)
            
            if success:
                self.current_state = PromptState.FALLBACK
                self._record_operation("switch_to_fallback", True, 
                                     f"Switched to fallback prompt for query: {query[:30]}...")
                logger.debug("Successfully switched to fallback prompt")
                return True
            else:
                raise PromptSwitchError("Failed to update VLM prompt")
                
        except Exception as e:
            self._record_operation("switch_to_fallback", False, str(e))
            logger.error(f"Failed to switch to fallback prompt: {e}")
            raise PromptSwitchError(f"Failed to switch to fallback prompt: {e}")
    
    async def _restore_original_prompt(self) -> bool:
        """
        Restore the original state tracking prompt.
        
        This is CRITICAL for system integrity - VLM must return to state tracking mode.
        
        Returns:
            bool: Success status
        """
        try:
            if not self.original_prompt:
                logger.warning("No original prompt to restore")
                return False
            
            # Restore original state tracking prompt
            success = await self._update_vlm_prompt(self.original_prompt)
            
            if success:
                self.current_state = PromptState.TRACKING
                self.original_prompt = None  # Clear saved prompt
                self._record_operation("restore_prompt", True, "Original state tracking prompt restored")
                logger.debug("Successfully restored original state tracking prompt")
                return True
            else:
                raise PromptRestoreError("Failed to restore VLM prompt")
                
        except Exception as e:
            self.current_state = PromptState.ERROR
            self._record_operation("restore_prompt", False, str(e))
            logger.error(f"CRITICAL: Failed to restore original prompt: {e}")
            raise PromptRestoreError(f"Failed to restore original prompt: {e}")
    
    async def _execute_vlm_query(self, query: str) -> str:
        """
        Execute query against VLM service.
        
        Args:
            query: User query
            
        Returns:
            str: VLM response
        """
        try:
            # Create request payload
            request_payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            # Send request to VLM service
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.model_server_url}/v1/chat/completions",
                    json=request_payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"VLM service error: {response.status_code}")
                
                response_data = response.json()
                
                # Extract response text
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    
                    # Handle different response formats
                    if isinstance(content, str):
                        return content.strip()
                    elif isinstance(content, list):
                        # Extract text from list format
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text_parts.append(item.get('text', ''))
                            elif isinstance(item, str):
                                text_parts.append(item)
                        return ' '.join(text_parts).strip()
                    else:
                        return str(content).strip()
                else:
                    raise Exception("Invalid VLM response format")
                    
        except Exception as e:
            logger.error(f"VLM query execution failed: {e}")
            raise Exception(f"VLM query failed: {e}")
    
    async def _update_vlm_prompt(self, prompt: str) -> bool:
        """
        Update VLM system prompt.
        
        Note: This is a simplified implementation.
        In practice, you would need to call the specific VLM service endpoint
        that updates the system prompt.
        
        Args:
            prompt: New system prompt
            
        Returns:
            bool: Success status
        """
        try:
            # This is a placeholder implementation
            # In real implementation, you would call VLM service to update system prompt
            
            # Simulate prompt update
            await asyncio.sleep(0.1)  # Simulate network delay
            
            logger.debug(f"VLM prompt updated: {prompt[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update VLM prompt: {e}")
            return False
    
    def _record_operation(self, operation_type: str, success: bool, 
                         message: str, prompt_preview: Optional[str] = None):
        """Record prompt operation for monitoring"""
        operation = PromptOperation(
            operation_type=operation_type,
            timestamp=datetime.now(),
            success=success,
            error_message=None if success else message,
            prompt_preview=prompt_preview
        )
        
        self.operation_history.append(operation)
        
        # Keep only last 50 operations
        if len(self.operation_history) > 50:
            self.operation_history = self.operation_history[-50:]
    
    def get_status(self) -> Dict:
        """Get current prompt manager status"""
        recent_operations = self.operation_history[-10:] if self.operation_history else []
        
        return {
            "current_state": self.current_state.value,
            "has_saved_prompt": bool(self.original_prompt),
            "total_operations": len(self.operation_history),
            "recent_operations": [
                {
                    "type": op.operation_type,
                    "timestamp": op.timestamp.isoformat(),
                    "success": op.success,
                    "error": op.error_message
                }
                for op in recent_operations
            ]
        }
    
    def health_check(self) -> Dict:
        """Perform health check"""
        recent_failures = [
            op for op in self.operation_history[-20:] 
            if not op.success
        ]
        
        is_healthy = (
            self.current_state != PromptState.ERROR and
            len(recent_failures) < 5  # Less than 5 failures in last 20 operations
        )
        
        return {
            "healthy": is_healthy,
            "current_state": self.current_state.value,
            "recent_failure_count": len(recent_failures),
            "last_operation": self.operation_history[-1].timestamp.isoformat() if self.operation_history else None
        }