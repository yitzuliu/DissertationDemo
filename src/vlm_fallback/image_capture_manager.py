import base64
import logging
from datetime import datetime
from typing import Optional, Dict

# 假設這些依賴已存在於專案
# from .camera_manager import CameraManager
# from ..backend.utils.image_processing import preprocess_for_model
# from ..state_tracker.state_tracker import get_state_tracker

logger = logging.getLogger(__name__)

class ImageCaptureManager:
    """
    管理圖片獲取和預處理的統一接口。
    支援：
    1. 相機即時圖片
    2. 狀態追蹤器最後處理圖片
    3. 圖片緩存
    """
    def __init__(self, camera_manager=None, image_processor=None):
        self.camera_manager = camera_manager  # 可注入相機管理器
        self.image_processor = image_processor  # 可注入自訂圖片處理器
        self.last_captured_image = None
        self.image_cache = {}

    async def get_current_image(self, model_type: str = None) -> Optional[Dict]:
        """
        優先順序：相機 > 狀態追蹤器 > 緩存
        回傳 dict: {image_data, format, size, processed, timestamp}
        """
        # 1. 相機
        current_image = await self._capture_from_camera()
        if current_image:
            return self._process_for_fallback(current_image, model_type)
        # 2. 狀態追蹤器
        last_image = await self._get_last_processed_image()
        if last_image:
            return self._process_for_fallback(last_image, model_type)
        # 3. 緩存
        cached_image = self._get_cached_image()
        if cached_image:
            return self._process_for_fallback(cached_image, model_type)
        return None

    async def _capture_from_camera(self) -> Optional[bytes]:
        """從相機系統獲取當前圖片（如有）"""
        try:
            if self.camera_manager:
                return await self.camera_manager.capture_current_frame()
            return None
        except Exception as e:
            logger.warning(f"Camera capture failed: {e}")
            return None

    async def _get_last_processed_image(self) -> Optional[bytes]:
        """從狀態追蹤器獲取最後處理的圖片（如有）"""
        try:
            # 使用相對導入
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from state_tracker.state_tracker import get_state_tracker
            
            state_tracker = get_state_tracker()
            if hasattr(state_tracker, 'get_last_processed_image'):
                return state_tracker.get_last_processed_image()
            return None
        except Exception as e:
            logger.warning(f"Last image retrieval failed: {e}")
            return None

    def _get_cached_image(self) -> Optional[bytes]:
        """從緩存獲取圖片（如有）"""
        try:
            if self.last_captured_image:
                return self.last_captured_image
            return None
        except Exception as e:
            logger.warning(f"Cache image retrieval failed: {e}")
            return None

    def _process_for_fallback(self, image_data: bytes, model_type: str = None) -> Optional[Dict]:
        """
        圖片預處理與 base64 編碼，回傳 dict
        """
        try:
            # 使用相對導入
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from backend.utils.image_processing import preprocess_for_model
            
            processed_image = preprocess_for_model(
                image=image_data,
                model_type=model_type or "smolvlm",
                config={},
                return_format='bytes'
            )
            base64_image = base64.b64encode(processed_image).decode('utf-8')
            return {
                "image_data": base64_image,
                "format": "jpeg",
                "size": len(processed_image),
                "processed": True,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            # 如果圖片處理失敗，返回原始圖片的 base64
            try:
                base64_image = base64.b64encode(image_data).decode('utf-8')
                return {
                    "image_data": base64_image,
                    "format": "jpeg",
                    "size": len(image_data),
                    "processed": False,
                    "timestamp": datetime.now()
                }
            except Exception as fallback_error:
                logger.error(f"Fallback image processing also failed: {fallback_error}")
                return None