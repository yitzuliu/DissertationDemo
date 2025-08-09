#!/usr/bin/env python3
"""
Test specific confidence scenarios
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from state_tracker.query_processor import QueryProcessor, QueryType

def test_low_confidence_scenarios():
    """Test the specific scenarios from the failing test"""
    print("🧪 Testing Low Confidence Scenarios")
    print("=" * 50)
    
    processor = QueryProcessor()
    
    test_cases = [
        ("What am I doing?", None, "Should be low confidence (no state)"),
        ("Where am I in the process?", None, "Should be low confidence (no state)"),
        ("What's my current status?", None, "Should be low confidence (no state)"),
        ("Am I making progress?", None, "Should be low confidence (no state)"),
    ]
    
    low_confidence_count = 0
    
    for query, state, description in test_cases:
        query_type = processor._classify_query(query)
        confidence = processor._calculate_confidence(query_type, state, query)
        
        is_low = confidence < 0.4
        should_trigger_fallback = processor._should_use_vlm_fallback(query_type, state, confidence, None)
        
        if is_low:
            low_confidence_count += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} '{query}'")
        print(f"    Type: {query_type.value}, Confidence: {confidence:.2f}")
        print(f"    Should trigger fallback: {should_trigger_fallback}")
        print(f"    {description}")
        print()
    
    accuracy = (low_confidence_count / len(test_cases)) * 100
    print(f"📊 Low Confidence Accuracy: {accuracy:.1f}% ({low_confidence_count}/{len(test_cases)})")
    
    return accuracy >= 75

if __name__ == "__main__":
    success = test_low_confidence_scenarios()
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}")
    sys.exit(0 if success else 1)