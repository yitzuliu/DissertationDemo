"""
Unit tests for VLM Fallback Image Enhancement functionality.

Tests the image capture, processing, and fallback mechanisms.
"""

import pytest
import asyncio
import base64
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Import the modules to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.vlm_fallback.image_capture_manager import ImageCaptureManager
from src.vlm_fallback.enhanced_fallback_processor import EnhancedVLMFallbackProcessor
from src.vlm_fallback.enhanced_prompt_manager import EnhancedPromptManager
from src.vlm_fallback.config import VLMFallbackConfig

class TestImageCaptureManager:
    """Test ImageCaptureManager functionality"""
    
    @pytest.fixture
    def image_capture_manager(self):
        """Create a test instance of ImageCaptureManager"""
        return ImageCaptureManager()
    
    @pytest.fixture
    def mock_image_data(self):
        """Create mock image data for testing"""
        # Create a simple test image (1x1 pixel JPEG)
        test_image_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        return test_image_bytes
    
    @pytest.fixture
    def real_test_images(self):
        """Load real test images from the materials directory"""
        images_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'testing', 'materials', 'images')
        test_images = {}
        
        # Load test images
        image_files = ['test_image.jpg', 'IMG_0119.JPG']
        
        for image_file in image_files:
            image_path = os.path.join(images_dir, image_file)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    test_images[image_file] = f.read()
        
        return test_images
    
    @pytest.fixture
    def real_image_data(self, real_test_images):
        """Get the first available real image data"""
        if real_test_images:
            # Use test_image.jpg as the primary test image
            image_name = 'test_image.jpg'
            if image_name in real_test_images:
                return real_test_images[image_name]
            # Fallback to any available image
            return list(real_test_images.values())[0]
        return None

    @pytest.mark.asyncio
    async def test_get_current_image_no_sources(self, image_capture_manager):
        """Test get_current_image when no image sources are available"""
        result = await image_capture_manager.get_current_image()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_current_image_with_camera(self, image_capture_manager, mock_image_data):
        """Test get_current_image with camera source"""
        # Mock camera manager
        mock_camera = Mock()
        mock_camera.capture_current_frame = AsyncMock(return_value=mock_image_data)
        image_capture_manager.camera_manager = mock_camera
        
        # Mock image processing to avoid import issues
        with patch.object(image_capture_manager, '_process_for_fallback') as mock_process:
            expected_result = {
                "image_data": base64.b64encode(mock_image_data).decode('utf-8'),
                "format": "jpeg",
                "size": len(mock_image_data),
                "processed": True,
                "timestamp": datetime.now()
            }
            mock_process.return_value = expected_result
            
            result = await image_capture_manager.get_current_image()
            
            # Verify camera was called
            mock_camera.capture_current_frame.assert_called_once()
            mock_process.assert_called_once_with(mock_image_data, None)
            assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_get_current_image_with_real_camera(self, image_capture_manager, real_image_data):
        """Test get_current_image with real image from camera"""
        if not real_image_data:
            pytest.skip("No real test images available")
            
        # Mock camera manager with real image
        mock_camera = Mock()
        mock_camera.capture_current_frame = AsyncMock(return_value=real_image_data)
        image_capture_manager.camera_manager = mock_camera
        
        # Mock image processing to avoid import issues
        with patch.object(image_capture_manager, '_process_for_fallback') as mock_process:
            expected_result = {
                "image_data": base64.b64encode(real_image_data).decode('utf-8'),
                "format": "jpeg",
                "size": len(real_image_data),
                "processed": True,
                "timestamp": datetime.now()
            }
            mock_process.return_value = expected_result
            
            result = await image_capture_manager.get_current_image()
            
            # Verify camera was called
            mock_camera.capture_current_frame.assert_called_once()
            mock_process.assert_called_once_with(real_image_data, None)
            assert result == expected_result
            assert result["size"] > 0
            assert len(result["image_data"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_current_image_with_state_tracker(self, image_capture_manager, mock_image_data):
        """Test get_current_image with state tracker source"""
        # Mock state tracker
        with patch.object(image_capture_manager, '_get_last_processed_image') as mock_get_last:
            mock_get_last.return_value = mock_image_data
            
            with patch.object(image_capture_manager, '_process_for_fallback') as mock_process:
                expected_result = {
                    "image_data": base64.b64encode(mock_image_data).decode('utf-8'),
                    "format": "jpeg",
                    "size": len(mock_image_data),
                    "processed": True,
                    "timestamp": datetime.now()
                }
                mock_process.return_value = expected_result
                
                result = await image_capture_manager.get_current_image()
                
                # Verify state tracker was called
                mock_get_last.assert_called_once()
                mock_process.assert_called_once_with(mock_image_data, None)
                assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_get_current_image_with_real_state_tracker(self, image_capture_manager, real_image_data):
        """Test get_current_image with real image from state tracker"""
        if not real_image_data:
            pytest.skip("No real test images available")
            
        # Mock state tracker with real image
        with patch.object(image_capture_manager, '_get_last_processed_image') as mock_get_last:
            mock_get_last.return_value = real_image_data
            
            with patch.object(image_capture_manager, '_process_for_fallback') as mock_process:
                expected_result = {
                    "image_data": base64.b64encode(real_image_data).decode('utf-8'),
                    "format": "jpeg",
                    "size": len(real_image_data),
                    "processed": True,
                    "timestamp": datetime.now()
                }
                mock_process.return_value = expected_result
                
                result = await image_capture_manager.get_current_image()
                
                # Verify state tracker was called
                mock_get_last.assert_called_once()
                mock_process.assert_called_once_with(real_image_data, None)
                assert result == expected_result
                assert result["size"] > 0
                assert len(result["image_data"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_current_image_with_cache(self, image_capture_manager, mock_image_data):
        """Test get_current_image with cached image"""
        # Set cached image
        image_capture_manager.last_captured_image = mock_image_data
        
        with patch.object(image_capture_manager, '_process_for_fallback') as mock_process:
            expected_result = {
                "image_data": base64.b64encode(mock_image_data).decode('utf-8'),
                "format": "jpeg",
                "size": len(mock_image_data),
                "processed": True,
                "timestamp": datetime.now()
            }
            mock_process.return_value = expected_result
            
            result = await image_capture_manager.get_current_image()
            
            # Verify cache was used
            mock_process.assert_called_once_with(mock_image_data, None)
            assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_get_current_image_with_real_cache(self, image_capture_manager, real_image_data):
        """Test get_current_image with real cached image"""
        if not real_image_data:
            pytest.skip("No real test images available")
            
        # Set real cached image
        image_capture_manager.last_captured_image = real_image_data
        
        with patch.object(image_capture_manager, '_process_for_fallback') as mock_process:
            expected_result = {
                "image_data": base64.b64encode(real_image_data).decode('utf-8'),
                "format": "jpeg",
                "size": len(real_image_data),
                "processed": True,
                "timestamp": datetime.now()
            }
            mock_process.return_value = expected_result
            
            result = await image_capture_manager.get_current_image()
            
            # Verify cache was used
            mock_process.assert_called_once_with(real_image_data, None)
            assert result == expected_result
            assert result["size"] > 0
            assert len(result["image_data"]) > 0
    
    def test_process_for_fallback_success(self, image_capture_manager, mock_image_data):
        """Test successful image processing for fallback"""
        # Mock the image processing function to avoid import issues
        with patch('base64.b64encode') as mock_b64encode:
            mock_b64encode.return_value.decode.return_value = "test_base64_data"
            
            # Mock the preprocess_for_model function
            with patch('src.vlm_fallback.image_capture_manager.preprocess_for_model', create=True) as mock_preprocess:
                mock_preprocess.return_value = mock_image_data
                
                result = image_capture_manager._process_for_fallback(mock_image_data, "smolvlm")
                
                assert result is not None
                assert result["image_data"] == "test_base64_data"
    
    def test_process_for_fallback_with_real_image(self, image_capture_manager, real_image_data):
        """Test image processing with real image data"""
        if not real_image_data:
            pytest.skip("No real test images available")
            
        # Mock the image processing function to avoid import issues
        with patch('base64.b64encode') as mock_b64encode:
            mock_b64encode.return_value.decode.return_value = "real_image_base64_data"
            
            # Mock the preprocess_for_model function
            with patch('src.vlm_fallback.image_capture_manager.preprocess_for_model', create=True) as mock_preprocess:
                mock_preprocess.return_value = real_image_data
                
                result = image_capture_manager._process_for_fallback(real_image_data, "smolvlm")
                
                assert result is not None
                assert result["image_data"] == "real_image_base64_data"
                assert result["size"] == len(real_image_data)
                assert result["format"] == "jpeg"
                assert result["processed"] == True
    
    def test_process_for_fallback_failure(self, image_capture_manager):
        """Test image processing failure handling"""
        test_data = b"test_image_data"
        
        # Mock the image processing function to raise an exception
        with patch('src.vlm_fallback.image_capture_manager.preprocess_for_model', create=True) as mock_preprocess:
            mock_preprocess.side_effect = Exception("Processing failed")
            
            # Mock base64 encoding for fallback
            with patch('base64.b64encode') as mock_b64encode:
                mock_b64encode.return_value.decode.return_value = "fallback_base64_data"
                
                result = image_capture_manager._process_for_fallback(test_data, "smolvlm")
                
                assert result is not None
                assert result["image_data"] == "fallback_base64_data"
                assert result["processed"] == False


class TestEnhancedVLMFallbackProcessor:
    """Test EnhancedVLMFallbackProcessor functionality"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        config = VLMFallbackConfig()
        config.enable_image_fallback = True
        return config
    
    @pytest.fixture
    def enhanced_processor(self, config):
        """Create test instance of EnhancedVLMFallbackProcessor"""
        with patch('src.vlm_fallback.enhanced_fallback_processor.ImageCaptureManager'):
            return EnhancedVLMFallbackProcessor(config)
    
    @pytest.fixture
    def real_image_data(self, real_test_images):
        """Get the first available real image data"""
        if real_test_images:
            # Use test_image.jpg as the primary test image
            image_name = 'test_image.jpg'
            if image_name in real_test_images:
                return real_test_images[image_name]
            # Fallback to any available image
            return list(real_test_images.values())[0]
        return None
    
    @pytest.mark.asyncio
    async def test_process_query_with_image_fallback_success(self, enhanced_processor):
        """Test successful image fallback processing"""
        query = "What do you see in this image?"
        state_data = {"confidence": 0.3}
        
        # Mock dependencies
        enhanced_processor.decision_engine = Mock()
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
        
        # Mock image capture manager
        mock_image_data = {
            "image_data": "test_base64_image",
            "format": "jpeg",
            "size": 1024,
            "processed": True,
            "timestamp": datetime.now()
        }
        enhanced_processor.image_capture_manager.get_current_image = AsyncMock(return_value=mock_image_data)
        
        # Mock prompt manager
        enhanced_processor.prompt_manager = Mock()
        enhanced_processor.prompt_manager.execute_fallback_with_image = AsyncMock(return_value="I can see a test image with various objects.")
        
        # Mock helper methods
        enhanced_processor._determine_apparent_query_type = Mock(return_value="UNKNOWN")
        enhanced_processor._calculate_apparent_confidence = Mock(return_value=0.75)
        enhanced_processor._format_unified_response = Mock(return_value={"response": "formatted_response"})
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        # Verify the process
        enhanced_processor.decision_engine.should_use_vlm_fallback.assert_called_once_with(query, state_data)
        enhanced_processor.image_capture_manager.get_current_image.assert_called_once()
        enhanced_processor.prompt_manager.execute_fallback_with_image.assert_called_once_with(query, mock_image_data)
        
        assert result == {"response": "formatted_response"}
    
    @pytest.mark.asyncio
    async def test_process_query_with_real_image_fallback_success(self, enhanced_processor, real_image_data):
        """Test successful image fallback processing with real image"""
        if not real_image_data:
            pytest.skip("No real test images available")
            
        query = "What do you see in this image?"
        state_data = {"confidence": 0.3}
        
        # Mock dependencies
        enhanced_processor.decision_engine = Mock()
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
        
        # Mock image capture manager with real image data
        mock_image_data = {
            "image_data": base64.b64encode(real_image_data).decode('utf-8'),
            "format": "jpeg",
            "size": len(real_image_data),
            "processed": True,
            "timestamp": datetime.now()
        }
        enhanced_processor.image_capture_manager.get_current_image = AsyncMock(return_value=mock_image_data)
        
        # Mock prompt manager
        enhanced_processor.prompt_manager = Mock()
        enhanced_processor.prompt_manager.execute_fallback_with_image = AsyncMock(return_value="I can see a real test image with various objects.")
        
        # Mock helper methods
        enhanced_processor._determine_apparent_query_type = Mock(return_value="UNKNOWN")
        enhanced_processor._calculate_apparent_confidence = Mock(return_value=0.75)
        enhanced_processor._format_unified_response = Mock(return_value={"response": "real_image_response"})
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        # Verify the process
        enhanced_processor.decision_engine.should_use_vlm_fallback.assert_called_once_with(query, state_data)
        enhanced_processor.image_capture_manager.get_current_image.assert_called_once()
        enhanced_processor.prompt_manager.execute_fallback_with_image.assert_called_once_with(query, mock_image_data)
        
        assert result == {"response": "real_image_response"}
        assert mock_image_data["size"] > 0
        assert len(mock_image_data["image_data"]) > 0
    
    @pytest.mark.asyncio
    async def test_process_query_with_image_fallback_no_image(self, enhanced_processor):
        """Test image fallback when no image is available"""
        query = "What do you see?"
        state_data = {"confidence": 0.3}
        
        # Mock dependencies
        enhanced_processor.decision_engine = Mock()
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
        
        # Mock no image available
        enhanced_processor.image_capture_manager.get_current_image = AsyncMock(return_value=None)
        
        # Mock prompt manager for text-only fallback
        enhanced_processor.prompt_manager = Mock()
        enhanced_processor.prompt_manager.execute_fallback_with_prompt_switch = AsyncMock(return_value="I cannot see any image to analyze.")
        
        # Mock helper methods
        enhanced_processor._determine_apparent_query_type = Mock(return_value="UNKNOWN")
        enhanced_processor._calculate_apparent_confidence = Mock(return_value=0.75)
        enhanced_processor._format_unified_response = Mock(return_value={"response": "text_only_response"})
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        # Verify fallback to text-only
        enhanced_processor.image_capture_manager.get_current_image.assert_called_once()
        enhanced_processor.prompt_manager.execute_fallback_with_prompt_switch.assert_called_once_with(query)
        
        assert result == {"response": "text_only_response"}
    
    @pytest.mark.asyncio
    async def test_process_query_with_image_fallback_disabled(self, enhanced_processor):
        """Test when image fallback is disabled"""
        enhanced_processor.enable_image_fallback = False
        query = "What do you see?"
        state_data = {"confidence": 0.3}
        
        # Mock dependencies
        enhanced_processor.decision_engine = Mock()
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
        
        # Mock _execute_vlm_fallback method
        enhanced_processor._execute_vlm_fallback = AsyncMock(return_value=Mock(processing_time_ms=0))
        enhanced_processor._format_unified_response = Mock(return_value={"response": "text_fallback"})
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        # Verify text-only fallback was used
        enhanced_processor._execute_vlm_fallback.assert_called_once_with(query, state_data)
        assert result == {"response": "text_fallback"}
    
    @pytest.mark.asyncio
    async def test_process_query_with_image_fallback_error(self, enhanced_processor):
        """Test error handling in image fallback processing"""
        query = "What do you see?"
        state_data = {"confidence": 0.3}
        
        # Mock dependencies to raise an error
        enhanced_processor.decision_engine = Mock()
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(side_effect=Exception("Test error"))
        
        # Mock error handling
        enhanced_processor._create_error_result = Mock(return_value=Mock(processing_time_ms=0))
        enhanced_processor._format_unified_response = Mock(return_value={"error": "error_response"})
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        # Verify error handling
        enhanced_processor._create_error_result.assert_called_once()
        assert result == {"error": "error_response"}


class TestEnhancedPromptManager:
    """Test EnhancedPromptManager functionality"""
    
    @pytest.fixture
    def enhanced_prompt_manager(self):
        """Create test instance of EnhancedPromptManager"""
        return EnhancedPromptManager()
    
    def test_image_fallback_prompt_template(self, enhanced_prompt_manager):
        """Test that image fallback prompt template is properly set"""
        assert hasattr(enhanced_prompt_manager, 'image_fallback_prompt_template')
        assert '{query}' in enhanced_prompt_manager.image_fallback_prompt_template
        assert '{image_format}' in enhanced_prompt_manager.image_fallback_prompt_template
        assert '{image_size}' in enhanced_prompt_manager.image_fallback_prompt_template
    
    @pytest.mark.asyncio
    async def test_execute_fallback_with_image_success(self, enhanced_prompt_manager, mock_image_data):
        """Test successful execution of fallback with image"""
        query = "What do you see in this image?"
        image_data = {
            "image_data": base64.b64encode(mock_image_data).decode('utf-8'),
            "format": "jpeg",
            "size": len(mock_image_data)
        }
        
        # Mock all the internal methods
        enhanced_prompt_manager._save_current_prompt = AsyncMock()
        enhanced_prompt_manager._switch_to_image_fallback_prompt = AsyncMock()
        enhanced_prompt_manager._execute_vlm_query_with_image = AsyncMock(return_value="I can see various objects in the image.")
        enhanced_prompt_manager._restore_original_prompt = AsyncMock()
        
        result = await enhanced_prompt_manager.execute_fallback_with_image(query, image_data)
        
        # Verify the complete workflow
        enhanced_prompt_manager._save_current_prompt.assert_called_once()
        enhanced_prompt_manager._switch_to_image_fallback_prompt.assert_called_once_with(query, image_data)
        enhanced_prompt_manager._execute_vlm_query_with_image.assert_called_once_with(query, image_data)
        enhanced_prompt_manager._restore_original_prompt.assert_called_once()
        
        assert result == "I can see various objects in the image."
    
    @pytest.mark.asyncio
    async def test_execute_fallback_with_image_vlm_error(self, enhanced_prompt_manager, mock_image_data):
        """Test error handling when VLM query fails"""
        query = "What do you see?"
        image_data = {
            "image_data": base64.b64encode(mock_image_data).decode('utf-8'),
            "format": "jpeg",
            "size": len(mock_image_data)
        }
        
        # Mock methods with VLM error
        enhanced_prompt_manager._save_current_prompt = AsyncMock()
        enhanced_prompt_manager._switch_to_image_fallback_prompt = AsyncMock()
        enhanced_prompt_manager._execute_vlm_query_with_image = AsyncMock(side_effect=Exception("VLM service error"))
        enhanced_prompt_manager._restore_original_prompt = AsyncMock()
        
        # Should raise VLMFallbackError
        with pytest.raises(Exception) as exc_info:
            await enhanced_prompt_manager.execute_fallback_with_image(query, image_data)
        
        # Verify cleanup was attempted
        enhanced_prompt_manager._restore_original_prompt.assert_called_once()
        assert "Enhanced fallback execution failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execute_fallback_with_image_prompt_switch_failure(self, enhanced_prompt_manager, mock_image_data):
        """Test error handling when prompt switching fails"""
        query = "What do you see?"
        image_data = {
            "image_data": base64.b64encode(mock_image_data).decode('utf-8'),
            "format": "jpeg",
            "size": len(mock_image_data)
        }
        
        # Mock methods with prompt switch error
        enhanced_prompt_manager._save_current_prompt = AsyncMock()
        enhanced_prompt_manager._switch_to_image_fallback_prompt = AsyncMock(side_effect=Exception("Prompt switch failed"))
        enhanced_prompt_manager._restore_original_prompt = AsyncMock()
        
        # Should raise VLMFallbackError
        with pytest.raises(Exception) as exc_info:
            await enhanced_prompt_manager.execute_fallback_with_image(query, image_data)
        
        # Verify cleanup was attempted
        enhanced_prompt_manager._restore_original_prompt.assert_called_once()
        assert "Enhanced fallback execution failed" in str(exc_info.value)
        
        result = await image_capture_manager.get_current_image()
        
        assert result is not None
        assert result['format'] == 'jpeg'
        assert result['processed'] is True
        assert 'image_data' in result
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_get_current_image_with_state_tracker(self, image_capture_manager, mock_image_data):
        """Test get_current_image with state tracker source"""
        # Mock state tracker
        with patch('src.vlm_fallback.image_capture_manager.get_state_tracker') as mock_get_tracker:
            mock_tracker = Mock()
            mock_tracker.get_last_processed_image.return_value = mock_image_data
            mock_get_tracker.return_value = mock_tracker
            
            result = await image_capture_manager.get_current_image()
            
            assert result is not None
            assert result['format'] == 'jpeg'
            assert result['processed'] is True
    
    @pytest.mark.asyncio
    async def test_get_current_image_with_cache(self, image_capture_manager, mock_image_data):
        """Test get_current_image with cache source"""
        # Set cached image
        image_capture_manager.last_captured_image = mock_image_data
        
        result = await image_capture_manager.get_current_image()
        
        assert result is not None
        assert result['format'] == 'jpeg'
        assert result['processed'] is True
    
    def test_process_for_fallback_success(self, image_capture_manager, mock_image_data):
        """Test _process_for_fallback with valid image data"""
        with patch('src.vlm_fallback.image_capture_manager.preprocess_for_model') as mock_preprocess:
            mock_preprocess.return_value = mock_image_data
            
            result = image_capture_manager._process_for_fallback(mock_image_data, "smolvlm")
            
            assert result is not None
            assert result['format'] == 'jpeg'
            assert result['size'] == len(mock_image_data)
            assert result['processed'] is True
            assert 'image_data' in result
            assert 'timestamp' in result
    
    def test_process_for_fallback_failure(self, image_capture_manager):
        """Test _process_for_fallback with invalid image data"""
        with patch('src.vlm_fallback.image_capture_manager.preprocess_for_model') as mock_preprocess:
            mock_preprocess.side_effect = Exception("Processing failed")
            
            result = image_capture_manager._process_for_fallback(b'invalid_data', "smolvlm")
            
            assert result is None

class TestEnhancedVLMFallbackProcessor:
    """Test EnhancedVLMFallbackProcessor functionality"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return VLMFallbackConfig(
            enable_image_fallback=True,
            confidence_threshold=0.40
        )
    
    @pytest.fixture
    def enhanced_processor(self, config):
        """Create a test instance of EnhancedVLMFallbackProcessor"""
        return EnhancedVLMFallbackProcessor(config)
    
    @pytest.mark.asyncio
    async def test_process_query_with_image_fallback_success(self, enhanced_processor):
        """Test successful image fallback processing"""
        query = "What do you see in this image?"
        state_data = {"confidence": 0.3}  # Low confidence triggers fallback
        
        # Mock the decision engine
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
        
        # Mock image capture
        mock_image_data = {
            "image_data": "base64_encoded_image",
            "format": "jpeg",
            "size": 1024,
            "processed": True,
            "timestamp": datetime.now()
        }
        enhanced_processor.image_capture_manager.get_current_image = AsyncMock(return_value=mock_image_data)
        
        # Mock prompt manager
        enhanced_processor.prompt_manager.execute_fallback_with_image = AsyncMock(return_value="I can see a coffee cup in the image.")
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        assert result is not None
        assert "response_text" in result
        assert result["response_text"] == "I can see a coffee cup in the image."
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_process_query_with_image_fallback_no_image(self, enhanced_processor):
        """Test fallback to text-only when no image is available"""
        query = "What do you see in this image?"
        state_data = {"confidence": 0.3}
        
        # Mock the decision engine
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
        
        # Mock no image available
        enhanced_processor.image_capture_manager.get_current_image = AsyncMock(return_value=None)
        
        # Mock prompt manager for text-only fallback
        enhanced_processor.prompt_manager.execute_fallback_with_prompt_switch = AsyncMock(return_value="I cannot see any image to analyze.")
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        assert result is not None
        assert "response_text" in result
        assert result["response_text"] == "I cannot see any image to analyze."
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_process_query_with_image_fallback_disabled(self, enhanced_processor):
        """Test fallback to text-only when image fallback is disabled"""
        enhanced_processor.enable_image_fallback = False
        query = "What do you see in this image?"
        state_data = {"confidence": 0.3}
        
        # Mock the decision engine
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
        
        # Mock prompt manager for text-only fallback
        enhanced_processor.prompt_manager.execute_fallback_with_prompt_switch = AsyncMock(return_value="I cannot see any image to analyze.")
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        assert result is not None
        assert "response_text" in result
        assert result["response_text"] == "I cannot see any image to analyze."
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_process_query_with_image_fallback_error(self, enhanced_processor):
        """Test error handling in image fallback processing"""
        query = "What do you see in this image?"
        state_data = {"confidence": 0.3}
        
        # Mock the decision engine
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
        
        # Mock image capture failure
        enhanced_processor.image_capture_manager.get_current_image = AsyncMock(side_effect=Exception("Image capture failed"))
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        assert result is not None
        assert "response_text" in result
        assert "error" in result["response_text"].lower()
        assert result["success"] is False

class TestEnhancedPromptManager:
    """Test EnhancedPromptManager functionality"""
    
    @pytest.fixture
    def enhanced_prompt_manager(self):
        """Create a test instance of EnhancedPromptManager"""
        return EnhancedPromptManager("http://localhost:8080", 30)
    
    @pytest.fixture
    def mock_image_data(self):
        """Create mock image data for testing"""
        return {
            "image_data": "base64_encoded_image_data",
            "format": "jpeg",
            "size": 1024,
            "processed": True,
            "timestamp": datetime.now()
        }
    
    @pytest.mark.asyncio
    async def test_execute_fallback_with_image_success(self, enhanced_prompt_manager, mock_image_data):
        """Test successful image fallback execution"""
        query = "What do you see in this image?"
        
        # Mock the parent class methods
        enhanced_prompt_manager._save_current_prompt = AsyncMock(return_value=True)
        enhanced_prompt_manager._update_vlm_prompt = AsyncMock(return_value=True)
        enhanced_prompt_manager._restore_original_prompt = AsyncMock(return_value=True)
        
        # Mock VLM response
        mock_response = {"choices": [{"message": {"content": "I can see a coffee cup in the image."}}]}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value.status_code = 200
            mock_client.return_value.__aenter__.return_value.post.return_value.json.return_value = mock_response
            
            result = await enhanced_prompt_manager.execute_fallback_with_image(query, mock_image_data)
            
            assert result == "I can see a coffee cup in the image."
    
    @pytest.mark.asyncio
    async def test_execute_fallback_with_image_prompt_switch_failure(self, enhanced_prompt_manager, mock_image_data):
        """Test prompt switch failure handling"""
        query = "What do you see in this image?"
        
        # Mock the parent class methods
        enhanced_prompt_manager._save_current_prompt = AsyncMock(return_value=True)
        enhanced_prompt_manager._update_vlm_prompt = AsyncMock(return_value=False)  # Prompt switch fails
        enhanced_prompt_manager._restore_original_prompt = AsyncMock(return_value=True)
        
        with pytest.raises(Exception):
            await enhanced_prompt_manager.execute_fallback_with_image(query, mock_image_data)
    
    @pytest.mark.asyncio
    async def test_execute_fallback_with_image_vlm_error(self, enhanced_prompt_manager, mock_image_data):
        """Test VLM service error handling"""
        query = "What do you see in this image?"
        
        # Mock the parent class methods
        enhanced_prompt_manager._save_current_prompt = AsyncMock(return_value=True)
        enhanced_prompt_manager._update_vlm_prompt = AsyncMock(return_value=True)
        enhanced_prompt_manager._restore_original_prompt = AsyncMock(return_value=True)
        
        # Mock VLM service error
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value.status_code = 500
            
            with pytest.raises(Exception):
                await enhanced_prompt_manager.execute_fallback_with_image(query, mock_image_data)
    
    def test_image_fallback_prompt_template(self, enhanced_prompt_manager):
        """Test image fallback prompt template formatting"""
        query = "What do you see?"
        image_data = {"format": "jpeg", "size": 1024}
        
        formatted_prompt = enhanced_prompt_manager.image_fallback_prompt_template.format(
            query=query,
            image_format=image_data["format"],
            image_size=image_data["size"]
        )
        
        assert query in formatted_prompt
        assert "jpeg" in formatted_prompt
        assert "1024" in formatted_prompt
        assert "Visual analysis" in formatted_prompt

if __name__ == "__main__":
    pytest.main([__file__]) 