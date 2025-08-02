"""
VLM Client for Fallback System

Handles communication with VLM service for fallback queries.
Works in conjunction with PromptManager to ensure proper prompt management.
"""

import logging
import asyncio
import httpx
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class VLMRequest:
    """VLM request data"""
    query: str
    max_tokens: int
    temperature: float
    timeout: int
    timestamp: datetime

@dataclass
class VLMResponse:
    """VLM response data"""
    content: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class VLMServiceError(Exception):
    """VLM service communication errors"""
    pass

class VLMTimeoutError(VLMServiceError):
    """VLM request timeout errors"""
    pass

class VLMResponseError(VLMServiceError):
    """VLM response format errors"""
    pass

class VLMClient:
    """
    Client for communicating with VLM service.
    
    Handles:
    - Request formatting and sending
    - Response processing and validation
    - Error handling and retries
    - Performance monitoring
    """
    
    def __init__(self, model_server_url: str = "http://localhost:8080", 
                 timeout: int = 30, max_retries: int = 2):
        """
        Initialize VLM client.
        
        Args:
            model_server_url: VLM service URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.model_server_url = model_server_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_processing_time = 0.0
        
        logger.info(f"VLMClient initialized: {model_server_url} (timeout: {timeout}s, retries: {max_retries})")
    
    async def send_query(self, query: str, max_tokens: int = 500, 
                        temperature: float = 0.7) -> str:
        """
        Send query to VLM service with retry logic.
        
        Args:
            query: User query text
            max_tokens: Maximum response tokens
            temperature: Response randomness (0.0-1.0)
            
        Returns:
            str: VLM response text
            
        Raises:
            VLMServiceError: If VLM service is unavailable
            VLMTimeoutError: If request times out
            VLMResponseError: If response format is invalid
        """
        request = VLMRequest(
            query=query,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=self.timeout,
            timestamp=datetime.now()
        )
        
        self.request_count += 1
        
        # Try request with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._execute_request(request, attempt + 1)
                
                if response.success:
                    self.success_count += 1
                    self.total_processing_time += response.processing_time
                    
                    logger.debug(f"VLM query successful (attempt {attempt + 1}): "
                               f"{response.processing_time:.2f}s")
                    return response.content
                else:
                    raise VLMServiceError(response.error_message)
                    
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"VLM request failed (attempt {attempt + 1}), "
                                 f"retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"VLM request failed after {attempt + 1} attempts: {e}")
        
        # All retries failed
        self.error_count += 1
        
        if isinstance(last_error, asyncio.TimeoutError):
            raise VLMTimeoutError(f"VLM request timed out after {self.timeout}s")
        elif isinstance(last_error, httpx.RequestError):
            raise VLMServiceError(f"VLM service unavailable: {last_error}")
        else:
            raise VLMServiceError(f"VLM request failed: {last_error}")
    
    async def _execute_request(self, request: VLMRequest, attempt: int) -> VLMResponse:
        """
        Execute single VLM request.
        
        Args:
            request: VLM request data
            attempt: Current attempt number
            
        Returns:
            VLMResponse: Response data
        """
        start_time = datetime.now()
        
        try:
            # Prepare request payload
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": request.query
                    }
                ],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                # 新增：明確標記為 Fallback 請求
                "metadata": {
                    "source": "fallback_query",
                    "skip_state_tracker": True
                }
            }
            
            # Send request to VLM service
            async with httpx.AsyncClient(timeout=request.timeout) as client:
                response = await client.post(
                    f"{self.model_server_url}/v1/chat/completions",
                    json=payload
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Check response status
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    return VLMResponse(
                        content="",
                        processing_time=processing_time,
                        success=False,
                        error_message=error_msg
                    )
                
                # Parse response
                try:
                    response_data = response.json()
                    content = self._extract_content(response_data)
                    
                    return VLMResponse(
                        content=content,
                        processing_time=processing_time,
                        success=True
                    )
                    
                except Exception as e:
                    return VLMResponse(
                        content="",
                        processing_time=processing_time,
                        success=False,
                        error_message=f"Response parsing error: {e}"
                    )
                    
        except asyncio.TimeoutError:
            processing_time = (datetime.now() - start_time).total_seconds()
            return VLMResponse(
                content="",
                processing_time=processing_time,
                success=False,
                error_message=f"Request timeout after {request.timeout}s"
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return VLMResponse(
                content="",
                processing_time=processing_time,
                success=False,
                error_message=f"Request error: {e}"
            )
    
    def _extract_content(self, response_data: Dict) -> str:
        """
        Extract content from VLM response data.
        
        Args:
            response_data: Raw VLM response JSON
            
        Returns:
            str: Extracted content text
            
        Raises:
            VLMResponseError: If response format is invalid
        """
        try:
            if 'choices' not in response_data or len(response_data['choices']) == 0:
                raise VLMResponseError("No choices in response")
            
            choice = response_data['choices'][0]
            if 'message' not in choice or 'content' not in choice['message']:
                raise VLMResponseError("No message content in response")
            
            content = choice['message']['content']
            
            # Handle different content formats
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
            
            elif isinstance(content, dict):
                # Extract text from dict format
                return content.get('text', str(content)).strip()
            
            else:
                return str(content).strip()
                
        except Exception as e:
            raise VLMResponseError(f"Failed to extract content: {e}")
    
    async def health_check(self) -> Dict:
        """
        Check VLM service health.
        
        Returns:
            Dict: Health status information
        """
        try:
            start_time = datetime.now()
            
            # Send simple health check query
            test_query = "Hello, are you working?"
            
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    f"{self.model_server_url}/v1/chat/completions",
                    json={
                        "messages": [{"role": "user", "content": test_query}],
                        "max_tokens": 10,
                        "temperature": 0.1
                    }
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "healthy": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "service_url": self.model_server_url,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "service_url": self.model_server_url,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_statistics(self) -> Dict:
        """Get client performance statistics"""
        success_rate = (self.success_count / self.request_count * 100) if self.request_count > 0 else 0
        avg_processing_time = (self.total_processing_time / self.success_count) if self.success_count > 0 else 0
        
        return {
            "total_requests": self.request_count,
            "successful_requests": self.success_count,
            "failed_requests": self.error_count,
            "success_rate_percent": round(success_rate, 2),
            "average_processing_time": round(avg_processing_time, 3),
            "total_processing_time": round(self.total_processing_time, 3),
            "service_url": self.model_server_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }
    
    def reset_statistics(self):
        """Reset client statistics"""
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_processing_time = 0.0
        logger.info("VLM client statistics reset")