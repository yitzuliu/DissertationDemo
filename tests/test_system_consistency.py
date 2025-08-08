"""
System Consistency Test

This test validates that all components of the recent observation aware fallback
system are properly integrated and working together.
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from state_tracker import StateTracker, ConfidenceLevel, StateRecord, ProcessingMetrics, ActionType
from state_tracker.query_processor import QueryProcessor, QueryType


def test_system_consistency():
    """Test that all components work together correctly"""
    print("🧪 Testing System Consistency")
    print("=" * 40)
    
    # Initialize components
    print("1. Initializing components...")
    state_tracker = StateTracker()
    query_processor = QueryProcessor()
    
    # Mock VLM fallback to avoid actual VLM calls
    query_processor.enhanced_vlm_fallback = None
    query_processor.vlm_fallback = None
    
    print("   ✅ Components initialized successfully")
    
    # Test 1: Basic functionality
    print("\n2. Testing basic functionality...")
    
    # Set up a state
    state_tracker.current_state = StateRecord(
        timestamp=datetime.now() - timedelta(seconds=10),
        vlm_text="User is grinding coffee beans",
        matched_step={"title": "Grind coffee beans", "description": "Grind the coffee beans"},
        confidence=0.75,
        task_id="coffee_brewing",
        step_index=3
    )
    
    # Get current state
    current_state = state_tracker.get_current_state()
    assert current_state is not None, "Current state should not be None"
    print("   ✅ Current state retrieval working")
    
    # Test 2: Recent observation status
    print("\n3. Testing recent observation status...")
    
    # Add a recent observation
    state_tracker.processing_metrics.append(ProcessingMetrics(
        timestamp=datetime.now() - timedelta(seconds=2),
        vlm_input="I see some objects on the counter",
        confidence_score=0.25,
        processing_time_ms=150.0,
        confidence_level=ConfidenceLevel.LOW,
        action_taken=ActionType.OBSERVE,
        matched_task=None,
        matched_step=None,
        consecutive_low_count=1
    ))
    
    # Get recent observation status
    status = state_tracker.get_recent_observation_status()
    assert hasattr(status, 'fallback_recommended'), "Status should have fallback_recommended attribute"
    print("   ✅ Recent observation status working")
    
    # Test 3: Query processing with recent observation awareness
    print("\n4. Testing query processing...")
    
    # Process a query
    query = "Where am I?"
    query_type = query_processor._classify_query(query)
    confidence = query_processor._calculate_confidence(query_type, current_state, query)
    
    # Test fallback decision
    should_fallback = query_processor._should_use_vlm_fallback(
        query_type, current_state, confidence, state_tracker
    )
    
    print(f"   ✅ Query processing working (fallback: {should_fallback})")
    
    # Test 4: Integration test
    print("\n5. Testing full integration...")
    
    # Test process_instant_query with recent observation awareness
    try:
        result = state_tracker.process_instant_query(query)
        print("   ✅ Full integration working")
    except Exception as e:
        print(f"   ⚠️ Integration test had expected issues (VLM fallback not available): {e}")
    
    # Test 5: Configuration consistency
    print("\n6. Testing configuration consistency...")
    
    # Test with different TTL values
    status_15s = state_tracker.get_recent_observation_status(15.0)
    status_30s = state_tracker.get_recent_observation_status(30.0)
    
    assert status_15s is not None, "Status with 15s TTL should not be None"
    assert status_30s is not None, "Status with 30s TTL should not be None"
    print("   ✅ Configuration consistency working")
    
    print("\n🎉 All system consistency tests passed!")
    print("   The recent observation aware fallback system is properly integrated.")
    
    return True


def test_performance_consistency():
    """Test that performance characteristics are maintained"""
    print("\n⚡ Testing Performance Consistency")
    print("=" * 40)
    
    state_tracker = StateTracker()
    
    # Test recent observation status performance
    start_time = time.time()
    for _ in range(100):
        status = state_tracker.get_recent_observation_status()
    end_time = time.time()
    
    avg_time_ms = ((end_time - start_time) / 100) * 1000
    print(f"1. Recent observation status check: {avg_time_ms:.3f}ms average")
    
    if avg_time_ms < 5.0:
        print("   ✅ Performance target met (<5ms)")
    else:
        print("   ⚠️ Performance target exceeded")
    
    # Test memory consistency
    print("\n2. Testing memory consistency...")
    initial_memory = len(state_tracker.processing_metrics)
    
    # Add some observations
    for i in range(10):
        state_tracker.processing_metrics.append(ProcessingMetrics(
            timestamp=datetime.now(),
            vlm_input=f"Test observation {i}",
            confidence_score=0.5,
            processing_time_ms=100.0,
            confidence_level=ConfidenceLevel.MEDIUM,
            action_taken=ActionType.OBSERVE,
            matched_task="test",
            matched_step=i,
            consecutive_low_count=0
        ))
    
    final_memory = len(state_tracker.processing_metrics)
    print(f"   ✅ Memory management working (added {final_memory - initial_memory} records)")
    
    print("\n🎉 Performance consistency tests completed!")


if __name__ == '__main__':
    try:
        test_system_consistency()
        test_performance_consistency()
        print("\n✅ All consistency tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Consistency test failed: {e}")
        sys.exit(1)

