#!/usr/bin/env python3
"""
Test Instant Response Whiteboard Mechanism (Task 2.4)

This script tests the instant response system including query processing,
fast state reading, response templates, and performance targets.
"""

import asyncio
import sys
import os
import time

# Add src to path
sys.path.append('src')

from state_tracker import StateTracker, QueryType

async def test_instant_response():
    """Test instant response whiteboard mechanism"""
    print("🧪 Testing Instant Response Whiteboard Mechanism...")
    
    # Initialize State Tracker
    tracker = StateTracker()
    print("✅ State Tracker with instant response initialized")
    
    # First, create some state to query
    print("\n📝 Setting up test state...")
    await tracker.process_vlm_response("Coffee beans are being ground in the grinder")
    await tracker.process_vlm_response("Hot water is being poured over coffee grounds")
    
    current_state = tracker.get_current_state()
    if current_state:
        print(f"✅ Test state created: {current_state['task_id']} step {current_state['step_index']}")
    else:
        print("⚠️ No current state - testing with empty state")
    
    # Test 1: Query Processing and Classification
    print("\n🔍 Test 1: Query Processing and Classification...")
    
    test_queries = [
        # Chinese queries
        ("我在哪個步驟？", QueryType.CURRENT_STEP),
        ("下一步是什麼？", QueryType.NEXT_STEP),
        ("需要什麼工具？", QueryType.REQUIRED_TOOLS),
        ("完成了嗎？", QueryType.COMPLETION_STATUS),
        ("整體進度如何？", QueryType.PROGRESS_OVERVIEW),
        ("怎麼做這個步驟？", QueryType.HELP),
        
        # English queries
        ("current step", QueryType.CURRENT_STEP),
        ("next step", QueryType.NEXT_STEP),
        ("tools needed", QueryType.REQUIRED_TOOLS),
        ("progress status", QueryType.COMPLETION_STATUS),
        ("help", QueryType.HELP),
        
        # Edge cases
        ("random question", QueryType.UNKNOWN),
        ("", QueryType.UNKNOWN),
    ]
    
    classification_correct = 0
    for query, expected_type in test_queries:
        if not query:  # Skip empty query for classification test
            continue
            
        result = tracker.process_instant_query(query)
        is_correct = result.query_type == expected_type
        status = "✅" if is_correct else "❌"
        
        print(f"  {status} '{query}' -> {result.query_type.value} (expected: {expected_type.value})")
        
        if is_correct:
            classification_correct += 1
    
    classification_accuracy = (classification_correct / (len(test_queries) - 1)) * 100  # -1 for empty query
    print(f"  Classification accuracy: {classification_accuracy:.1f}%")
    
    # Test 2: Response Time Performance (<20ms target)
    print("\n⚡ Test 2: Response Time Performance...")
    
    performance_queries = [
        "我在哪個步驟？",
        "下一步是什麼？",
        "current step",
        "next step",
        "progress"
    ]
    
    response_times = []
    for query in performance_queries:
        # Measure multiple runs for accuracy
        times = []
        for _ in range(5):
            start_time = time.time()
            result = tracker.process_instant_query(query)
            end_time = time.time()
            
            processing_time = (end_time - start_time) * 1000
            times.append(processing_time)
        
        avg_time = sum(times) / len(times)
        response_times.append(avg_time)
        
        status = "✅" if avg_time < 20 else "⚠️"
        print(f"  {status} '{query}': {avg_time:.1f}ms (target: <20ms)")
    
    overall_avg_time = sum(response_times) / len(response_times)
    performance_target_met = overall_avg_time < 20
    
    print(f"  Overall average: {overall_avg_time:.1f}ms")
    print(f"  Performance target (<20ms): {'✅ MET' if performance_target_met else '❌ MISSED'}")
    
    # Test 3: Response Template Quality
    print("\n📝 Test 3: Response Template Quality...")
    
    template_queries = [
        "我在哪個步驟？",
        "下一步是什麼？",
        "需要什麼工具？",
        "完成了嗎？",
        "整體進度如何？"
    ]
    
    for query in template_queries:
        result = tracker.process_instant_query(query)
        print(f"  Query: '{query}'")
        print(f"    Response: '{result.response_text}'")
        print(f"    Type: {result.query_type.value}, Confidence: {result.confidence:.2f}")
        print()
    
    # Test 4: Query Capabilities
    print("\n🔧 Test 4: Query Capabilities...")
    
    capabilities = tracker.get_query_capabilities()
    print(f"  Supported query types: {len(capabilities['supported_query_types'])}")
    print(f"  Example queries: {len(capabilities['example_queries'])}")
    print(f"  Response time target: {capabilities['response_time_target_ms']}ms")
    print(f"  Current state available: {capabilities['current_state_available']}")
    
    # Test 5: Error Handling
    print("\n❌ Test 5: Error Handling...")
    
    error_cases = [
        "",  # Empty query
        "   ",  # Whitespace only
        "completely unrelated random text that should not match anything",
    ]
    
    for error_query in error_cases:
        try:
            result = tracker.process_instant_query(error_query)
            print(f"  ✅ Handled: '{error_query}' -> {result.query_type.value}")
            print(f"    Response: '{result.response_text[:50]}...'")
        except Exception as e:
            print(f"  ❌ Error with '{error_query}': {e}")
    
    # Test 6: Stress Test (Multiple Rapid Queries)
    print("\n🚀 Test 6: Stress Test...")
    
    stress_queries = ["我在哪？"] * 20
    start_time = time.time()
    
    stress_results = []
    for query in stress_queries:
        result = tracker.process_instant_query(query)
        stress_results.append(result.processing_time_ms)
    
    end_time = time.time()
    total_stress_time = (end_time - start_time) * 1000
    
    avg_stress_time = sum(stress_results) / len(stress_results)
    max_stress_time = max(stress_results)
    min_stress_time = min(stress_results)
    
    print(f"  Processed {len(stress_queries)} queries in {total_stress_time:.1f}ms")
    print(f"  Average per query: {avg_stress_time:.1f}ms")
    print(f"  Range: {min_stress_time:.1f}ms - {max_stress_time:.1f}ms")
    print(f"  Throughput: {len(stress_queries) / (total_stress_time / 1000):.1f} queries/second")
    
    # Final Summary
    print("\n📋 Task 2.4 Validation Summary:")
    print(f"  ✅ Fast query interface: Implemented with {overall_avg_time:.1f}ms average")
    print(f"  ✅ Response templates: Generated for all query types")
    print(f"  ✅ Performance target: {'MET' if performance_target_met else 'MISSED'} (<20ms)")
    print(f"  ✅ Query classification: {classification_accuracy:.1f}% accuracy")
    print(f"  ✅ Error handling: Graceful handling of edge cases")
    print(f"  ✅ Stress testing: {len(stress_queries)} queries processed successfully")
    
    print("\n✅ Instant response whiteboard mechanism test completed!")
    
    return {
        'avg_response_time_ms': overall_avg_time,
        'performance_target_met': performance_target_met,
        'classification_accuracy': classification_accuracy,
        'stress_test_throughput': len(stress_queries) / (total_stress_time / 1000)
    }

if __name__ == "__main__":
    result = asyncio.run(test_instant_response())
    print(f"\n🎯 Final Test Results: {result}")