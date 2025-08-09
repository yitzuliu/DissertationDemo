"""
Integration tests for VLM Fallback Image Enhancement functionality.

Tests the complete image fallback flow from query to response.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Import the modules to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.state_tracker.query_processor import QueryProcessor
from src.vlm_fallback.enhanced_fallback_processor import EnhancedVLMFallbackProcessor
from src.vlm_fallback.config import VLMFallbackConfig

class TestImageFallbackIntegration:
    """Integration tests for image fallback functionality"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return VLMFallbackConfig(
            enable_image_fallback=True,
            confidence_threshold=0.40
        )
    
    @pytest.fixture
    def query_processor(self):
        """Create a test instance of QueryProcessor"""
        return QueryProcessor()
    
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
    async def test_complete_image_fallback_flow(self, query_processor, mock_image_data):
        """Test complete image fallback flow from query to response"""
        query = "What objects do you see in this image?"
        current_state = None  # No state to trigger fallback
        
        # Mock the enhanced VLM fallback processor
        if hasattr(query_processor, 'enhanced_vlm_fallback') and query_processor.enhanced_vlm_fallback:
            with patch.object(query_processor.enhanced_vlm_fallback, 'process_query_with_image_fallback') as mock_process:
                # Mock successful image fallback response
                mock_process.return_value = {
                    "response_text": "I can see a coffee cup, a laptop, and some books on a wooden desk.",
                    "confidence": 0.85,
                    "processing_time_ms": 2500,
                    "success": True,
                    "decision_reason": "Enhanced VLM fallback with image"
                }
                
                # Process the query
                result = query_processor.process_query(query, current_state)
                
                # Verify the result
                assert result is not None
                assert "coffee cup" in result.response_text
                assert result.confidence > 0.8
                
                # Verify enhanced fallback was called
                mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_image_fallback_with_no_image_available(self, query_processor):
        """Test image fallback when no image is available (should fall back to text-only)"""
        query = "What do you see in the current image?"
        current_state = None
        
        if hasattr(query_processor, 'enhanced_vlm_fallback') and query_processor.enhanced_vlm_fallback:
            with patch.object(query_processor.enhanced_vlm_fallback, 'process_query_with_image_fallback') as mock_process:
                # Mock response when no image is available
                mock_process.return_value = {
                    "response_text": "I don't have access to any image at the moment. Could you please share an image for me to analyze?",
                    "confidence": 0.70,
                    "processing_time_ms": 1200,
                    "success": True,
                    "decision_reason": "Enhanced VLM fallback without image (text-only)"
                }
                
                result = query_processor.process_query(query, current_state)
                
                assert result is not None
                assert "don't have access" in result.response_text or "no image" in result.response_text.lower()
                mock_process.assert_called_once()
    
    def test_query_classification_for_image_queries(self, query_processor):
        """Test that image-related queries are properly classified"""
        image_queries = [
            "What do you see in this image?",
            "Describe the objects in the picture",
            "What colors are visible in the photo?",
            "Can you identify the items in this image?"
        ]
        
        for query in image_queries:
            # Mock the classification process
            query_type = query_processor._classify_query(query)
            
            # Image-related queries should often be classified as UNKNOWN or HELP
            # which would trigger fallback
            assert query_type in ['unknown', 'help', 'current_step']
    
    def test_confidence_calculation_for_image_queries(self, query_processor):
        """Test confidence calculation for image-related queries"""
        image_query = "What objects are visible in this image?"
        current_state = None  # No state should lower confidence
        
        # Mock the confidence calculation
        if hasattr(query_processor, '_calculate_confidence'):
            confidence = query_processor._calculate_confidence('unknown', current_state, image_query)
            
            # Should have low confidence due to no state and complex query
            assert confidence < 0.40  # Should trigger fallback
    
    @pytest.mark.asyncio
    async def test_image_fallback_error_handling(self, query_processor):
        """Test error handling in image fallback processing"""
        query = "What's in this image?"
        current_state = None
        
        if hasattr(query_processor, 'enhanced_vlm_fallback') and query_processor.enhanced_vlm_fallback:
            with patch.object(query_processor.enhanced_vlm_fallback, 'process_query_with_image_fallback') as mock_process:
                # Mock an error in image processing
                mock_process.side_effect = Exception("Image processing failed")
                
                # Should fall back to standard VLM fallback
                with patch.object(query_processor, 'vlm_fallback') as mock_standard_fallback:
                    if mock_standard_fallback:
                        # Mock standard fallback response
                        mock_fallback_result = Mock()
                        mock_fallback_result.response_text = "I'm having trouble processing images right now, but I can help with text-based questions."
                        mock_fallback_result.confidence = 0.60
                        mock_fallback_result.processing_time_ms = 800
                        
                        # Mock the thread execution for standard fallback
                        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
                            mock_future = Mock()
                            mock_future.result.return_value = {
                                "response_text": "I'm having trouble processing images right now.",
                                "confidence": 0.60
                            }
                            mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future
                            
                            result = query_processor.process_query(query, current_state)
                            
                            # Should get a fallback response
                            assert result is not None
                            # Either enhanced fallback error handling or standard fallback should work
                            assert len(result.response_text) > 0
    
    @pytest.mark.asyncio
    async def test_image_fallback_performance(self, query_processor, mock_image_data):
        """Test performance characteristics of image fallback"""
        query = "Analyze this image for me"
        current_state = None
        
        if hasattr(query_processor, 'enhanced_vlm_fallback') and query_processor.enhanced_vlm_fallback:
            with patch.object(query_processor.enhanced_vlm_fallback, 'process_query_with_image_fallback') as mock_process:
                # Mock a realistic response time for image processing
                mock_process.return_value = {
                    "response_text": "This image shows a detailed scene with multiple elements.",
                    "confidence": 0.80,
                    "processing_time_ms": 3500,  # Realistic image processing time
                    "success": True
                }
                
                import time
                start_time = time.time()
                result = query_processor.process_query(query, current_state)
                end_time = time.time()
                
                # Verify response
                assert result is not None
                
                # Processing should complete within reasonable time (allowing for mocking overhead)
                processing_time = (end_time - start_time) * 1000
                assert processing_time < 5000  # Should complete within 5 seconds
    
    async def test_image_fallback_disabled_falls_back_to_text(self, query_processor):
        """Test that when image fallback is disabled, it falls back to text-only"""
        query = "What do you see in this image?"
        current_state = {"confidence": 0.3}
        
        # Mock the enhanced VLM fallback processor with image fallback disabled
        if hasattr(query_processor, 'enhanced_vlm_fallback') and query_processor.enhanced_vlm_fallback:
            with patch.object(query_processor.enhanced_vlm_fallback, 'enable_image_fallback', False):
                with patch.object(query_processor.enhanced_vlm_fallback, 'process_query_with_image_fallback') as mock_process:
                    # Mock text-only fallback response
                    mock_process.return_value = {
                        "response_text": "I cannot see any image to analyze. Image processing is currently disabled.",
                        "confidence": 0.6,
                        "success": True,
                        "decision_reason": "Image fallback disabled, using text-only"
                    }
                    
                    # Process the query
                    result = query_processor.process_query(query, current_state)
                    
                    # Verify the result
                    assert result is not None
                    assert "cannot see" in result.response_text.lower() or "disabled" in result.response_text.lower()
                    mock_process.assert_called_once()
        """Test complete image fallback flow from query to response"""
        query = "What do you see in this image?"
        current_state = {"confidence": 0.3}  # Low confidence triggers fallback
        
        # Mock the enhanced VLM fallback processor
        with patch.object(query_processor, 'enhanced_vlm_fallback') as mock_enhanced:
            if mock_enhanced:
                # Mock the decision engine
                mock_enhanced.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
                
                # Mock image capture
                mock_enhanced.image_capture_manager.get_current_image = AsyncMock(return_value=mock_image_data)
                
                # Mock prompt manager
                mock_enhanced.prompt_manager.execute_fallback_with_image = AsyncMock(return_value="I can see a coffee cup in the image.")
                
                # Mock the process_query_with_image_fallback method
                mock_enhanced.process_query_with_image_fallback = AsyncMock(return_value={
                    "response_text": "I can see a coffee cup in the image.",
                    "confidence": 0.8,
                    "success": True
                })
                
                # Process the query
                result = query_processor.process_query(query, current_state)
                
                # Verify the result
                assert result is not None
                assert result.response_text == "I can see a coffee cup in the image."
                assert result.confidence == 0.8
                assert result.query_type.value == "help"  # Should be classified as help query
    
    @pytest.mark.asyncio
    async def test_image_fallback_with_no_image_available(self, query_processor):
        """Test image fallback when no image is available"""
        query = "What do you see in this image?"
        current_state = {"confidence": 0.3}
        
        # Mock the enhanced VLM fallback processor
        with patch.object(query_processor, 'enhanced_vlm_fallback') as mock_enhanced:
            if mock_enhanced:
                # Mock the decision engine
                mock_enhanced.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
                
                # Mock no image available
                mock_enhanced.image_capture_manager.get_current_image = AsyncMock(return_value=None)
                
                # Mock fallback to text-only
                mock_enhanced.prompt_manager.execute_fallback_with_prompt_switch = AsyncMock(return_value="I cannot see any image to analyze.")
                
                # Mock the process_query_with_image_fallback method
                mock_enhanced.process_query_with_image_fallback = AsyncMock(return_value={
                    "response_text": "I cannot see any image to analyze.",
                    "confidence": 0.6,
                    "success": True
                })
                
                # Process the query
                result = query_processor.process_query(query, current_state)
                
                # Verify the result
                assert result is not None
                assert result.response_text == "I cannot see any image to analyze."
                assert result.confidence == 0.6
    
    @pytest.mark.asyncio
    async def test_image_fallback_disabled_falls_back_to_text(self, query_processor):
        """Test that when image fallback is disabled, it falls back to text-only"""
        query = "What do you see in this image?"
        current_state = {"confidence": 0.3}
        
        # Mock the enhanced VLM fallback processor with image fallback disabled
        with patch.object(query_processor, 'enhanced_vlm_fallback') as mock_enhanced:
            if mock_enhanced:
                mock_enhanced.enable_image_fallback = False
                
                # Mock the decision engine
                mock_enhanced.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
                
                # Mock text-only fallback
                mock_enhanced.prompt_manager.execute_fallback_with_prompt_switch = AsyncMock(return_value="I cannot see any image to analyze.")
                
                # Mock the process_query_with_image_fallback method
                mock_enhanced.process_query_with_image_fallback = AsyncMock(return_value={
                    "response_text": "I cannot see any image to analyze.",
                    "confidence": 0.6,
                    "success": True
                })
                
                # Process the query
                result = query_processor.process_query(query, current_state)
                
                # Verify the result
                assert result is not None
                assert result.response_text == "I cannot see any image to analyze."
    
    @pytest.mark.asyncio
    async def test_image_fallback_error_handling(self, query_processor):
        """Test error handling in image fallback flow"""
        query = "What do you see in this image?"
        current_state = {"confidence": 0.3}
        
        # Mock the enhanced VLM fallback processor
        with patch.object(query_processor, 'enhanced_vlm_fallback') as mock_enhanced:
            if mock_enhanced:
                # Mock the decision engine
                mock_enhanced.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
                
                # Mock image capture failure
                mock_enhanced.image_capture_manager.get_current_image = AsyncMock(side_effect=Exception("Image capture failed"))
                
                # Mock the process_query_with_image_fallback method with error
                mock_enhanced.process_query_with_image_fallback = AsyncMock(return_value={
                    "response_text": "Sorry, I encountered an error processing your query: Image capture failed",
                    "confidence": 0.5,
                    "success": False
                })
                
                # Process the query
                result = query_processor.process_query(query, current_state)
                
                # Verify the result
                assert result is not None
                assert "error" in result.response_text.lower()
                assert result.success is False
    
    def test_query_classification_for_image_queries(self, query_processor):
        """Test that image-related queries are properly classified"""
        # Test various image-related queries
        image_queries = [
            "What do you see in this image?",
            "Can you describe what's in the picture?",
            "What objects are visible in the image?",
            "Tell me about this photo",
            "What's happening in this picture?"
        ]
        
        for query in image_queries:
            query_type = query_processor._classify_query(query)
            # These should be classified as HELP queries since they're not standard state queries
            assert query_type.value in ["help", "unknown"]
    
    def test_confidence_calculation_for_image_queries(self, query_processor):
        """Test confidence calculation for image-related queries"""
        query = "What do you see in this image?"
        current_state = {"confidence": 0.3}
        
        confidence = query_processor._calculate_confidence(
            query_processor._classify_query(query), 
            current_state, 
            query
        )
        
        # Confidence should be low for complex image queries
        assert confidence < 0.5
    
    @pytest.mark.asyncio
    async def test_image_fallback_performance(self, query_processor, mock_image_data):
        """Test performance of image fallback flow"""
        query = "What do you see in this image?"
        current_state = {"confidence": 0.3}
        
        # Mock the enhanced VLM fallback processor
        with patch.object(query_processor, 'enhanced_vlm_fallback') as mock_enhanced:
            if mock_enhanced:
                # Mock all components for performance testing
                mock_enhanced.decision_engine.should_use_vlm_fallback = Mock(return_value=True)
                mock_enhanced.image_capture_manager.get_current_image = AsyncMock(return_value=mock_image_data)
                mock_enhanced.prompt_manager.execute_fallback_with_image = AsyncMock(return_value="Test response")
                mock_enhanced.process_query_with_image_fallback = AsyncMock(return_value={
                    "response_text": "Test response",
                    "confidence": 0.8,
                    "success": True
                })
                
                # Measure processing time
                start_time = datetime.now()
                result = query_processor.process_query(query, current_state)
                end_time = datetime.now()
                
                processing_time = (end_time - start_time).total_seconds()
                
                # Verify performance (should be fast since everything is mocked)
                assert processing_time < 1.0  # Should complete within 1 second
                assert result is not None
                assert result.response_text == "Test response"

if __name__ == "__main__":
    pytest.main([__file__]) 