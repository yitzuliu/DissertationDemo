import logging
import httpx
import asyncio
from datetime import datetime
from typing import Dict, Optional

from .prompt_manager import PromptManager, PromptState, VLMFallbackError, PromptSwitchError

logger = logging.getLogger(__name__)

class EnhancedPromptManager(PromptManager):
    """
    增強型提示詞管理器，支援圖片傳送。
    擴展自 PromptManager，保持向後兼容性。
    """
    
    def __init__(self, model_server_url: str = "http://localhost:8080", timeout: int = 30, config=None):
        super().__init__(model_server_url, timeout)
        self.config = config
        # 圖片 Fallback 提示詞模板
        self.image_fallback_prompt_template = """You are a helpful AI assistant with visual capabilities. Please analyze the provided image and answer the user's question.

User Question: {query}

Image Format: {image_format}
Image Size: {image_size} bytes

Please provide a clear, accurate, and helpful response based on both the image content and the user's question. Focus on:
- Visual analysis of the image
- Answering the specific question
- Providing practical guidance when appropriate
- Being concise but complete
- Using a friendly and supportive tone

Answer:"""
    
    async def execute_fallback_with_image(self, query: str, image_data: Dict) -> str:
        """
        執行包含圖片的 Fallback 流程。
        完整的提示詞切換流程：保存 → 切換 → VLM查詢 → 恢復。
        """
        operation_start = datetime.now()
        
        try:
            logger.info(f"Starting enhanced fallback execution with image for query: '{query[:50]}...'")
            
            # 步驟 1：保存當前狀態追蹤提示詞
            await self._save_current_prompt()
            
            # 步驟 2：切換到包含圖片的 Fallback 提示詞
            await self._switch_to_image_fallback_prompt(query, image_data)
            
            # 步驟 3：執行包含圖片的 VLM 查詢
            response = await self._execute_vlm_query_with_image(query, image_data)
            
            # 步驟 4：恢復原始提示詞（關鍵！）
            await self._restore_original_prompt()
            
            operation_time = (datetime.now() - operation_start).total_seconds()
            logger.info(f"Enhanced fallback execution completed successfully in {operation_time:.2f}s")
            
            return response
            
        except Exception as e:
            # 確保提示詞恢復
            try:
                await self._restore_original_prompt()
            except Exception as restore_error:
                logger.error(f"Failed to restore prompt after error: {restore_error}")
            
            raise VLMFallbackError(f"Enhanced fallback execution failed: {e}")
    
    async def _switch_to_image_fallback_prompt(self, query: str, image_data: Dict) -> bool:
        """
        切換到包含圖片的 Fallback 提示詞。
        """
        try:
            # 格式化包含圖片的 Fallback 提示詞
            image_fallback_prompt = self.image_fallback_prompt_template.format(
                query=query,
                image_format=image_data.get('format', 'jpeg'),
                image_size=image_data.get('size', 0)
            )
            
            # 切換 VLM 到圖片 Fallback 模式
            success = await self._update_vlm_prompt(image_fallback_prompt)
            
            if success:
                self.current_state = PromptState.FALLBACK  # 使用現有的 FALLBACK 狀態
                self._record_operation("switch_to_image_fallback", True, 
                                     f"Switched to image fallback prompt for query: {query[:30]}...")
                logger.debug("Successfully switched to image fallback prompt")
                return True
            else:
                raise PromptSwitchError("Failed to update VLM prompt for image fallback")
                
        except Exception as e:
            self._record_operation("switch_to_image_fallback", False, str(e))
            logger.error(f"Failed to switch to image fallback prompt: {e}")
            raise PromptSwitchError(f"Failed to switch to image fallback prompt: {e}")
    
    async def _execute_vlm_query_with_image(self, query: str, image_data: Dict) -> str:
        """
        執行包含圖片的 VLM 查詢。
        使用多模態格式：文字 + 圖片。
        """
        try:
            # 創建包含圖片的請求載荷
            # 從配置中獲取參數，如果沒有配置則使用預設值
            max_tokens = self.config.max_tokens if self.config else 500
            temperature = self.config.temperature if self.config else 0.7
            
            request_payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": query
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_data['format']};base64,{image_data['image_data']}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # 發送請求到 VLM 服務
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.model_server_url}/v1/chat/completions",
                    json=request_payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"VLM service error: {response.status_code}")
                
                response_data = response.json()
                
                # 提取回應文字
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    
                    # 處理不同回應格式
                    if isinstance(content, str):
                        return content.strip()
                    elif isinstance(content, list):
                        # 從列表格式提取文字
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
            logger.error(f"VLM query with image execution failed: {e}")
            raise Exception(f"VLM query with image failed: {e}") 