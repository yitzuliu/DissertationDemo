"""
Test Simplified VLM Fallback

This test validates the simplified VLM Fallback implementation
that directly sends queries to VLM without redundant processing.
"""

import sys
import os
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from state_tracker import StateTracker, ConfidenceLevel, StateRecord, ProcessingMetrics, ActionType
from state_tracker.query_processor import QueryProcessor, QueryType


def test_simplified_vlm_fallback():
    """Test simplified VLM fallback functionality"""
    print("🧪 Testing Simplified VLM Fallback Implementation")
    print("=" * 50)
    
    # Initialize components
    state_tracker = StateTracker()
    query_processor = QueryProcessor()
    
    # Mock VLM fallback systems
    mock_enhanced_fallback = Mock()
    mock_standard_fallback = Mock()
    
    query_processor.enhanced_vlm_fallback = mock_enhanced_fallback
    query_processor.vlm_fallback = mock_standard_fallback
    
    # Test 1: Simplified Enhanced VLM Fallback
    print("🧪 Testing Simplified Enhanced VLM Fallback")
    
    mock_response = {
        "response_text": "I can see coffee beans and a grinder on the counter.",
        "confidence": 0.85
    }
    mock_enhanced_fallback.process_query_with_image_fallback.return_value = mock_response
    
    query = "What do you see?"
    current_image = b"fake_image_data"
    
    result = query_processor.simple_enhanced_vlm_fallback(query, current_image)
    
    # Verify VLM was called correctly
    mock_enhanced_fallback.process_query_with_image_fallback.assert_called_once_with(
        query, {"image": current_image}
    )
    
    assert result == mock_response
    print("   ✅ Simplified Enhanced VLM Fallback working correctly")
    
    # Test 2: Simplified Standard VLM Fallback
    print("🧪 Testing Simplified Standard VLM Fallback")
    
    mock_response2 = {
        "response_text": "Based on the current context, you appear to be in the kitchen.",
        "confidence": 0.75
    }
    mock_standard_fallback.process_query_with_fallback.return_value = mock_response2
    
    query2 = "Where am I?"
    
    result2 = query_processor.simple_vlm_fallback(query2)
    
    # Verify VLM was called correctly
    mock_standard_fallback.process_query_with_fallback.assert_called_once_with(
        query2, {}
    )
    
    assert result2 == mock_response2
    print("   ✅ Simplified Standard VLM Fallback working correctly")
    
    # Test 3: Fallback Decision with Recent Observations
    print("🧪 Testing Fallback Decision with Recent Observations")
    
    # Set up state tracker with recent LOW observations
    state_tracker.current_state = StateRecord(
        timestamp=datetime.now() - timedelta(seconds=20),
        vlm_text="User is grinding coffee beans",
        matched_step={"title": "Grind coffee beans", "description": "Grind the coffee beans"},
        confidence=0.75,
        task_id="coffee_brewing",
        step_index=3
    )
    
    state_tracker.processing_metrics.append(ProcessingMetrics(
        timestamp=datetime.now() - timedelta(seconds=5),
        vlm_input="I see some objects on the counter",
        confidence_score=0.25,
        processing_time_ms=150.0,
        confidence_level=ConfidenceLevel.LOW,
        action_taken=ActionType.OBSERVE,
        matched_task=None,
        matched_step=None,
        consecutive_low_count=2
    ))
    
    # Test fallback decision
    query3 = "Where am I?"
    current_state = state_tracker.get_current_state()
    query_type = query_processor._classify_query(query3)
    confidence = query_processor._calculate_confidence(query_type, current_state, query3)
    
    should_fallback = query_processor._should_use_vlm_fallback(
        query_type, current_state, confidence, state_tracker
    )
    
    assert should_fallback == True, "Should use fallback when recent observations are LOW"
    print("   ✅ Fallback decision working correctly with recent observations")
    
    # Test 4: Query Type and Confidence Usage in Fallback
    print("🧪 Testing Query Type and Confidence Usage in Fallback")
    
    # Mock the simple fallback method to return a response with confidence
    with patch.object(query_processor, 'simple_enhanced_vlm_fallback') as mock_simple:
        mock_simple.return_value = {
            "response_text": "I can see you are in the kitchen with coffee equipment.",
            "confidence": 0.9
        }
        
        # Set up scenario where fallback should be used
        state_tracker.current_state = StateRecord(
            timestamp=datetime.now() - timedelta(seconds=30),  # Old state
            vlm_text="User is grinding coffee beans",
            matched_step={"title": "Grind coffee beans", "description": "Grind the coffee beans"},
            confidence=0.75,
            task_id="coffee_brewing",
            step_index=3
        )
        
        # Add recent LOW observation
        state_tracker.processing_metrics.append(ProcessingMetrics(
            timestamp=datetime.now() - timedelta(seconds=2),
            vlm_input="I see some objects",
            confidence_score=0.25,
            processing_time_ms=150.0,
            confidence_level=ConfidenceLevel.LOW,
            action_taken=ActionType.OBSERVE,
            matched_task=None,
            matched_step=None,
            consecutive_low_count=1
        ))
        
        # Process query
        query4 = "What am I doing?"
        current_state = state_tracker.get_current_state()
        query_type = query_processor._classify_query(query4)
        confidence = query_processor._calculate_confidence(query_type, current_state, query4)
        
        should_fallback = query_processor._should_use_vlm_fallback(
            query_type, current_state, confidence, state_tracker
        )
        
        assert should_fallback == True, "Should use fallback for stale state with LOW observations"
        
        # Test the simplified fallback
        result4 = query_processor.simple_enhanced_vlm_fallback(query4, b"fake_image")
        
        assert result4["confidence"] == 0.9, "Should use VLM's confidence value"
        print("   ✅ Query type and confidence usage working correctly")
    
    # Test 5: Error Handling
    print("🧪 Testing Error Handling")
    
    # Mock VLM to raise exception
    mock_enhanced_fallback.process_query_with_image_fallback.side_effect = Exception("VLM Error")
    
    # Test error handling
    query5 = "What do you see?"
    result5 = query_processor.simple_enhanced_vlm_fallback(query5, b"fake_image")
    
    assert result5 is None, "Should return None on VLM error"
    print("   ✅ Error handling working correctly")
    
    print("\n✅ All simplified VLM fallback tests passed!")
    return True


if __name__ == '__main__':
    success = test_simplified_vlm_fallback()
    sys.exit(0 if success else 1)
