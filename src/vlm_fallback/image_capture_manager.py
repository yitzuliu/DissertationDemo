import base64
import logging
from datetime import datetime
from typing import Optional, Dict

# Assume these dependencies exist in the project
# from .camera_manager import CameraManager
# from ..backend.utils.image_processing import preprocess_for_model
# from ..state_tracker.state_tracker import get_state_tracker

logger = logging.getLogger(__name__)

class ImageCaptureManager:
    """
    Unified interface for managing image acquisition and preprocessing.
    Supports:
    1. Real-time camera images
    2. Last processed images from state tracker
    3. Image cache
    """
    def __init__(self, camera_manager=None, image_processor=None):
        self.camera_manager = camera_manager  # Injectable camera manager
        self.image_processor = image_processor  # Injectable custom image processor
        self.last_captured_image = None
        self.image_cache = {}

    async def get_current_image(self, model_type: str = None) -> Optional[Dict]:
        """
        Priority order: camera > state tracker > cache
        Returns dict: {image_data, format, size, processed, timestamp}
        """
        # 1. Camera
        current_image = await self._capture_from_camera()
        if current_image:
            return self._process_for_fallback(current_image, model_type)
        # 2. State tracker
        last_image = await self._get_last_processed_image()
        if last_image:
            return self._process_for_fallback(last_image, model_type)
        # 3. Cache
        cached_image = self._get_cached_image()
        if cached_image:
            return self._process_for_fallback(cached_image, model_type)
        return None

    async def _capture_from_camera(self) -> Optional[bytes]:
        """Capture current image from camera system (if available)"""
        try:
            if self.camera_manager:
                return await self.camera_manager.capture_current_frame()
            return None
        except Exception as e:
            logger.warning(f"Camera capture failed: {e}")
            return None

    async def _get_last_processed_image(self) -> Optional[bytes]:
        """Get last processed image from state tracker (if available)"""
        try:
            # Use relative imports
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
        """Get image from cache (if available)"""
        try:
            if self.last_captured_image:
                return self.last_captured_image
            return None
        except Exception as e:
            logger.warning(f"Cache image retrieval failed: {e}")
            return None

    def _process_for_fallback(self, image_data: bytes, model_type: str = None) -> Optional[Dict]:
        """
        Image preprocessing and base64 encoding, returns dict
        """
        try:
            # Use relative imports
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
            # If image processing fails, return raw base64
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