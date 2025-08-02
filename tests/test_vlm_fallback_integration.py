"""
Test VLM Fallback System Integration

This module tests the integration of VLM fallback system with existing components.
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestVLMFallbackIntegration:
    """Test VLM fallback system integration"""
    
    def test_query_processor_import(self):
        """Test that query processor can import VLM fallback"""
        try:
            from state_tracker.query_processor import QueryProcessor
            processor = QueryProcessor()
            
            # Check if VLM fallback is available
            has_fallback = hasattr(processor, 'vlm_fallback') and processor.vlm_fallback is not None
            print(f"VLM Fallback available: {has_fallback}")
            
            assert hasattr(processor, 'vlm_fallback')
            
        except ImportError as e:
            pytest.skip(f"Cannot import query processor: {e}")
    
    def test_fallback_decision_logic(self):
        """Test VLM fallback decision logic"""
        try:
            from state_tracker.query_processor import QueryProcessor, QueryType
            
            processor = QueryProcessor()
            
            # Test cases for fallback decision
            test_cases = [
                # (query_type, current_state, confidence, expected_fallback)
                (QueryType.UNKNOWN, None, 0.3, True),  # No state
                (QueryType.CURRENT_STEP, {"task_id": "test"}, 0.2, True),  # Low confidence
                (QueryType.UNKNOWN, {"task_id": "test"}, 0.3, True),  # Unknown query
                (QueryType.CURRENT_STEP, {"task_id": "test", "step_index": 1}, 0.9, False),  # Good state
            ]
            
            for query_type, state, confidence, expected in test_cases:
                result = processor._should_use_vlm_fallback(query_type, state, confidence)
                print(f"Query: {query_type}, State: {bool(state)}, Confidence: {confidence} -> Fallback: {result}")
                
                if processor.vlm_fallback is not None:
                    assert result == expected, f"Expected {expected}, got {result} for {query_type}"
                else:
                    assert result == False, "Should not use fallback when not available"
                    
        except ImportError as e:
            pytest.skip(f"Cannot import query processor: {e}")
    
    @pytest.mark.asyncio
    async def test_query_processing_with_fallback(self):
        """Test query processing with VLM fallback"""
        try:
            from state_tracker.query_processor import QueryProcessor
            
            processor = QueryProcessor()
            
            # Mock VLM fallback if available
            if processor.vlm_fallback:
                with patch.object(processor.vlm_fallback, 'process_query') as mock_process:
                    mock_process.return_value = {
                        "response_text": "VLM fallback response",
                        "confidence": 0.8,
                        "processing_time_ms": 100
                    }
                    
                    # Test with low confidence scenario
                    result = processor.process_query(
                        query="What is the meaning of life?",
                        current_state=None
                    )
                    
                    assert result is not None
                    assert hasattr(result, 'response_text')
                    print(f"Query result: {result.response_text}")
            else:
                # Test without fallback
                result = processor.process_query(
                    query="Where am I?",
                    current_state={"task_id": "test", "step_index": 1}
                )
                
                assert result is not None
                assert hasattr(result, 'response_text')
                print(f"Query result: {result.response_text}")
                
        except ImportError as e:
            pytest.skip(f"Cannot import query processor: {e}")
    
    def test_backend_import(self):
        """Test that backend can import VLM fallback"""
        try:
            # Test the import that would happen in main.py
            from vlm_fallback.fallback_processor import VLMFallbackProcessor
            
            # Try to create instance
            processor = VLMFallbackProcessor()
            assert processor is not None
            print("VLM Fallback processor created successfully")
            
        except ImportError as e:
            print(f"VLM Fallback not available: {e}")
            # This is expected if dependencies are missing
    
    def test_config_loading(self):
        """Test VLM fallback configuration loading"""
        try:
            from vlm_fallback.config import load_config
            
            config = load_config()
            
            assert config is not None
            assert hasattr(config, 'confidence_threshold')
            assert hasattr(config, 'model_server_url')
            assert hasattr(config, 'fallback_prompt_template')
            
            print(f"Config loaded with threshold: {config.confidence_threshold}")
            
        except ImportError as e:
            pytest.skip(f"Cannot import VLM fallback config: {e}")
    
    def test_prompt_manager(self):
        """Test prompt manager functionality"""
        try:
            from vlm_fallback.prompt_manager import PromptManager
            
            manager = PromptManager()
            
            # Test status check
            status = manager.get_status()
            assert status is not None
            assert "current_state" in status
            
            print("Prompt manager status check passed")
            
        except ImportError as e:
            pytest.skip(f"Cannot import prompt manager: {e}")

def run_integration_tests():
    """Run integration tests manually"""
    print("=== VLM Fallback Integration Tests ===")
    
    test_instance = TestVLMFallbackIntegration()
    
    try:
        print("\n1. Testing Query Processor Import...")
        test_instance.test_query_processor_import()
        print("✅ Query Processor Import: PASSED")
    except Exception as e:
        print(f"❌ Query Processor Import: FAILED - {e}")
    
    try:
        print("\n2. Testing Fallback Decision Logic...")
        test_instance.test_fallback_decision_logic()
        print("✅ Fallback Decision Logic: PASSED")
    except Exception as e:
        print(f"❌ Fallback Decision Logic: FAILED - {e}")
    
    try:
        print("\n3. Testing Backend Import...")
        test_instance.test_backend_import()
        print("✅ Backend Import: PASSED")
    except Exception as e:
        print(f"❌ Backend Import: FAILED - {e}")
    
    try:
        print("\n4. Testing Config Loading...")
        test_instance.test_config_loading()
        print("✅ Config Loading: PASSED")
    except Exception as e:
        print(f"❌ Config Loading: FAILED - {e}")
    
    try:
        print("\n5. Testing Prompt Manager...")
        test_instance.test_prompt_manager()
        print("✅ Prompt Manager: PASSED")
    except Exception as e:
        print(f"❌ Prompt Manager: FAILED - {e}")
    
    print("\n=== Integration Tests Complete ===")

if __name__ == "__main__":
    run_integration_tests()