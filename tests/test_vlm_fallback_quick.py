#!/usr/bin/env python3
"""
Quick VLM Fallback Test - Test the fixes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from state_tracker.query_processor import QueryProcessor, QueryType

def test_query_classification():
    """Test query classification improvements"""
    print("🧪 Testing Query Classification Improvements")
    print("=" * 50)
    
    processor = QueryProcessor()
    
    test_queries = [
        ("What is the meaning of life?", QueryType.UNKNOWN),
        ("Tell me a joke about programming", QueryType.UNKNOWN),
        ("How do I make the perfect cup of coffee?", QueryType.UNKNOWN),
        ("What's the weather like in Tokyo?", QueryType.UNKNOWN),
        ("Explain quantum physics in simple terms", QueryType.UNKNOWN),
        ("What step am I on?", QueryType.CURRENT_STEP),
        ("What tools do I need?", QueryType.REQUIRED_TOOLS),
        ("Help me with this step", QueryType.HELP),
    ]
    
    correct_classifications = 0
    
    for query, expected_type in test_queries:
        classified_type = processor._classify_query(query)
        is_correct = classified_type == expected_type
        
        if is_correct:
            correct_classifications += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} '{query}' -> {classified_type.value} (expected: {expected_type.value})")
    
    accuracy = (correct_classifications / len(test_queries)) * 100
    print(f"\n📊 Classification Accuracy: {accuracy:.1f}% ({correct_classifications}/{len(test_queries)})")
    
    return accuracy >= 80

def test_confidence_calculation():
    """Test confidence calculation improvements"""
    print("\n🧪 Testing Confidence Calculation Improvements")
    print("=" * 50)
    
    processor = QueryProcessor()
    
    test_cases = [
        ("What is the meaning of life?", None, "Should be low confidence"),
        ("Tell me a joke", None, "Should be low confidence"),
        ("What step am I on?", {"task_id": "test", "step_index": 1}, "Should be high confidence"),
        ("What am I doing?", None, "Should be low confidence (no state)"),
    ]
    
    low_confidence_count = 0
    
    for query, state, description in test_cases:
        query_type = processor._classify_query(query)
        confidence = processor._calculate_confidence(query_type, state, query)
        
        should_be_low = "low confidence" in description
        is_low = confidence < 0.4
        
        if should_be_low == is_low:
            low_confidence_count += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} '{query}' -> {confidence:.2f} ({description})")
    
    accuracy = (low_confidence_count / len(test_cases)) * 100
    print(f"\n📊 Confidence Accuracy: {accuracy:.1f}% ({low_confidence_count}/{len(test_cases)})")
    
    return accuracy >= 75

def main():
    """Run quick tests"""
    print("🎯 Quick VLM Fallback Fix Test")
    print("=" * 60)
    
    classification_ok = test_query_classification()
    confidence_ok = test_confidence_calculation()
    
    print(f"\n📊 Overall Results:")
    print(f"   Classification: {'✅ PASS' if classification_ok else '❌ FAIL'}")
    print(f"   Confidence: {'✅ PASS' if confidence_ok else '❌ FAIL'}")
    
    if classification_ok and confidence_ok:
        print("\n✅ Quick Fix Test: PASS")
        return True
    else:
        print("\n❌ Quick Fix Test: FAIL")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)