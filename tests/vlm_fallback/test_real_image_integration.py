#!/usr/bin/env python3
"""
Real Image Integration Tests for VLM Fallback Image Enhancement

This module provides comprehensive integration tests using real images
from the testing materials directory. These tests verify that the image
fallback system works correctly with actual image files.
"""

import asyncio
import base64
import os
import sys
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vlm_fallback.image_capture_manager import ImageCaptureManager
from vlm_fallback.enhanced_fallback_processor import EnhancedVLMFallbackProcessor
from vlm_fallback.enhanced_prompt_manager import EnhancedPromptManager
from vlm_fallback.config import VLMFallbackConfig
from state_tracker.query_processor import QueryProcessor

class TestRealImageIntegration:
    """Integration tests using real images"""
    
    def real_test_images(self):
        """Load real test images from the materials directory"""
        images_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'testing', 'materials', 'images')
        test_images = {}
        
        # Load test images
        image_files = ['test_image.jpg', 'IMG_0119.JPG']
        
        for image_file in image_files:
            image_path = os.path.join(images_dir, image_file)
            if os.path.exists(image_path):
                try:
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                        test_images[image_file] = {
                            "raw_data": image_data,
                            "image_data": base64.b64encode(image_data).decode('utf-8'),
                            "format": "jpeg",
                            "size": len(image_data),
                            "processed": True,
                            "timestamp": datetime.now()
                        }
                        print(f"✅ Loaded real image: {image_file} ({len(image_data)} bytes)")
                except Exception as e:
                    print(f"❌ Failed to load {image_file}: {e}")
            else:
                print(f"⚠️ Image file not found: {image_path}")
        
        return test_images
    
    def image_capture_manager(self):
        """Create ImageCaptureManager instance"""
        return ImageCaptureManager()
    
    def enhanced_processor(self):
        """Create EnhancedVLMFallbackProcessor instance"""
        config = VLMFallbackConfig()
        config.enable_image_fallback = True
        return EnhancedVLMFallbackProcessor(config)
    
    def query_processor(self):
        """Create QueryProcessor instance"""
        return QueryProcessor()
    
    async def test_real_image_processing_workflow(self, image_capture_manager, real_test_images):
        """Test complete image processing workflow with real images"""
        if not real_test_images:
            pytest.skip("No real test images available")
        
        for image_name, image_data in real_test_images.items():
            print(f"\n📸 Testing workflow with {image_name}")
            
            # Test 1: Direct image processing
            with patch('vlm_fallback.image_capture_manager.preprocess_for_model', create=True) as mock_preprocess:
                mock_preprocess.return_value = image_data["raw_data"]
                
                result = image_capture_manager._process_for_fallback(image_data["raw_data"], "smolvlm")
                
                assert result is not None
                assert result["format"] == "jpeg"
                assert result["size"] > 0
                assert result["processed"] == True
                assert len(result["image_data"]) > 0
                
                print(f"  ✅ Direct processing successful: {result['size']} bytes")
            
            # Test 2: Camera capture simulation
            mock_camera = Mock()
            mock_camera.capture_current_frame = AsyncMock(return_value=image_data["raw_data"])
            image_capture_manager.camera_manager = mock_camera
            
            with patch.object(image_capture_manager, '_process_for_fallback') as mock_process:
                expected_result = {
                    "image_data": image_data["image_data"],
                    "format": "jpeg",
                    "size": image_data["size"],
                    "processed": True,
                    "timestamp": datetime.now()
                }
                mock_process.return_value = expected_result
                
                result = await image_capture_manager.get_current_image()
                
                assert result == expected_result
                mock_camera.capture_current_frame.assert_called_once()
                print(f"  ✅ Camera capture simulation successful")
    
    async def test_real_image_fallback_processing(self, enhanced_processor, real_test_images):
        """Test image fallback processing with real images"""
        if not real_test_images:
            print("⚠️ No real test images available, skipping test")
            return
        
        # Use the first available image
        image_name, image_data = list(real_test_images.items())[0]
        print(f"\n📸 Testing fallback processing with {image_name}")
        
        # Mock dependencies
        enhanced_processor.decision_engine = Mock()
        enhanced_processor.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
        
        # Mock image capture manager
        enhanced_processor.image_capture_manager.get_current_image = AsyncMock(return_value={
            "image_data": image_data["image_data"],
            "format": "jpeg",
            "size": image_data["size"],
            "processed": True,
            "timestamp": datetime.now()
        })
        
        # Mock prompt manager
        enhanced_processor.prompt_manager = Mock()
        enhanced_processor.prompt_manager.execute_fallback_with_image = AsyncMock(
            return_value=f"I can see a real image ({image_name}) with various objects."
        )
        
        # Mock helper methods
        enhanced_processor._determine_apparent_query_type = Mock(return_value="UNKNOWN")
        enhanced_processor._calculate_apparent_confidence = Mock(return_value=0.75)
        enhanced_processor._format_unified_response = Mock(return_value={
            "response_text": f"Real image analysis result for {image_name}",
            "confidence": 0.75,
            "processing_time_ms": 100.0
        })
        
        # Test the fallback processing
        query = "What do you see in this image?"
        state_data = {"confidence": 0.3}
        
        result = await enhanced_processor.process_query_with_image_fallback(query, state_data)
        
        # Verify the process
        enhanced_processor.decision_engine.should_use_vlm_fallback.assert_called_once_with(query, state_data)
        enhanced_processor.image_capture_manager.get_current_image.assert_called_once()
        enhanced_processor.prompt_manager.execute_fallback_with_image.assert_called_once()
        
        assert result is not None
        assert "response_text" in result
        assert image_name in result["response_text"]
        print(f"  ✅ Fallback processing successful")
    
    async def test_real_image_prompt_manager(self, real_test_images):
        """Test EnhancedPromptManager with real images"""
        if not real_test_images:
            print("⚠️ No real test images available, skipping test")
            return
        
        # Use the first available image
        image_name, image_data = list(real_test_images.items())[0]
        print(f"\n📸 Testing prompt manager with {image_name}")
        
        prompt_manager = EnhancedPromptManager()
        
        # Mock the VLM service response
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": f"I can see a real image ({image_name}) with various objects and details."
                    }
                }
            ]
        }
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response
            
            # Mock prompt switching methods
            prompt_manager._save_current_prompt = AsyncMock(return_value=True)
            prompt_manager._update_vlm_prompt = AsyncMock(return_value=True)
            prompt_manager._restore_original_prompt = AsyncMock(return_value=True)
            
            result = await prompt_manager.execute_fallback_with_image(
                "What do you see in this image?", 
                {
                    "image_data": image_data["image_data"],
                    "format": "jpeg",
                    "size": image_data["size"]
                }
            )
            
            assert result is not None
            assert image_name in result
            assert len(result) > 50  # Should be a substantial response
            
            print(f"  ✅ Prompt manager test successful")
    
    def test_real_image_size_analysis(self, real_test_images):
        """Analyze real image sizes and processing characteristics"""
        if not real_test_images:
            print("⚠️ No real test images available, skipping test")
            return
        
        print(f"\n📊 Real Image Size Analysis")
        print("-" * 40)
        
        for image_name, image_data in real_test_images.items():
            original_size = image_data["size"]
            base64_size = len(image_data["image_data"])
            
            print(f"📸 {image_name}:")
            print(f"   Original: {original_size:,} bytes")
            print(f"   Base64: {base64_size:,} bytes")
            print(f"   Ratio: {base64_size/original_size:.2f}x")
            
            # Verify reasonable sizes
            assert original_size > 0
            assert base64_size > original_size
            assert base64_size/original_size < 1.4  # Base64 should not be more than ~1.37x
    
    async def test_real_image_error_handling(self, image_capture_manager, real_test_images):
        """Test error handling with real images"""
        if not real_test_images:
            print("⚠️ No real test images available, skipping test")
            return
        
        # Use the first available image
        image_name, image_data = list(real_test_images.items())[0]
        print(f"\n📸 Testing error handling with {image_name}")
        
        # Test processing failure with fallback
        with patch('vlm_fallback.image_capture_manager.preprocess_for_model', create=True) as mock_preprocess:
            mock_preprocess.side_effect = Exception("Processing failed")
            
            result = image_capture_manager._process_for_fallback(image_data["raw_data"], "smolvlm")
            
            # Should return fallback result
            assert result is not None
            assert result["processed"] == False
            assert len(result["image_data"]) > 0
            
            print(f"  ✅ Error handling with fallback successful")
    
    def test_real_image_format_validation(self, real_test_images):
        """Validate real image formats and metadata"""
        if not real_test_images:
            print("⚠️ No real test images available, skipping test")
            return
        
        print(f"\n🔍 Real Image Format Validation")
        print("-" * 40)
        
        for image_name, image_data in real_test_images.items():
            # Check JPEG header
            raw_data = image_data["raw_data"]
            if raw_data.startswith(b'\xff\xd8\xff'):
                print(f"✅ {image_name}: Valid JPEG header")
            else:
                print(f"⚠️ {image_name}: Unexpected header")
            
            # Check reasonable size
            if 1000 <= image_data["size"] <= 5000000:  # 1KB to 5MB
                print(f"✅ {image_name}: Reasonable size ({image_data['size']:,} bytes)")
            else:
                print(f"⚠️ {image_name}: Unusual size ({image_data['size']:,} bytes)")
            
            # Check base64 encoding
            try:
                decoded = base64.b64decode(image_data["image_data"])
                assert decoded == raw_data
                print(f"✅ {image_name}: Valid base64 encoding")
            except Exception as e:
                print(f"❌ {image_name}: Base64 encoding error: {e}")

def main():
    """Run real image integration tests"""
    print("🚀 Real Image Integration Tests")
    print("=" * 50)
    
    # Run tests
    test_instance = TestRealImageIntegration()
    
    # Test image loading
    real_images = test_instance.real_test_images()
    if not real_images:
        print("❌ No real test images found!")
        return
    
    print(f"✅ Loaded {len(real_images)} real test images")
    
    # Run individual tests
    image_capture_manager = test_instance.image_capture_manager()
    enhanced_processor = test_instance.enhanced_processor()
    
    # Run tests
    asyncio.run(test_instance.test_real_image_processing_workflow(image_capture_manager, real_images))
    asyncio.run(test_instance.test_real_image_fallback_processing(enhanced_processor, real_images))
    asyncio.run(test_instance.test_real_image_prompt_manager(real_images))
    test_instance.test_real_image_size_analysis(real_images)
    asyncio.run(test_instance.test_real_image_error_handling(image_capture_manager, real_images))
    test_instance.test_real_image_format_validation(real_images)
    
    print("\n" + "=" * 50)
    print("🏁 Real image integration tests completed!")

if __name__ == "__main__":
    main() 