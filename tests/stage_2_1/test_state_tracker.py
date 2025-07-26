#!/usr/bin/env python3
"""
Test script for State Tracker functionality

This script tests the basic functionality of the State Tracker system
including VLM text processing and RAG matching.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append('src')

from state_tracker import StateTracker, VLMTextProcessor

async def test_state_tracker():
    """Test State Tracker basic functionality"""
    print("🧪 Testing State Tracker...")
    
    # Initialize State Tracker
    tracker = StateTracker()
    print("✅ State Tracker initialized")
    
    # Test text processor
    processor = VLMTextProcessor()
    
    # Test cases
    test_cases = [
        "I see a coffee machine with water being poured",
        "The coffee beans are being ground in the grinder",
        "Hot water is being poured over the coffee grounds",
        "",  # Empty text
        "abc",  # Too short
        "!@#$%^&*()",  # Invalid characters
    ]
    
    print("\n📝 Testing VLM text processing...")
    for i, test_text in enumerate(test_cases):
        print(f"\nTest {i+1}: '{test_text}'")
        
        # Test validation
        is_valid = processor.is_valid_text(test_text)
        print(f"  Valid: {is_valid}")
        
        if is_valid:
            # Test cleaning
            cleaned = processor.clean_text(test_text)
            print(f"  Cleaned: '{cleaned}'")
            
            # Test key phrase extraction
            key_phrases = processor.extract_key_phrases(cleaned)
            print(f"  Key phrases: {key_phrases}")
            
            # Test anomaly detection
            anomalies = processor.detect_anomalies(test_text)
            if anomalies:
                print(f"  Anomalies: {anomalies}")
            
            # Test state tracker processing
            try:
                # Temporarily lower threshold for testing
                original_threshold = tracker.confidence_threshold
                tracker.confidence_threshold = 0.3
                
                result = await tracker.process_vlm_response(test_text)
                print(f"  State updated: {result}")
                
                # Get current state
                current_state = tracker.get_current_state()
                if current_state:
                    print(f"  Current state: task={current_state.get('task_id')}, step={current_state.get('step_index')}, confidence={current_state.get('confidence'):.2f}")
                else:
                    # Check if we got a match but confidence was too low
                    match_result = tracker.rag_kb.find_matching_step(cleaned)
                    if match_result:
                        print(f"  Match found but confidence too low: similarity={match_result.similarity:.2f}, threshold={original_threshold}")
                
                # Restore threshold
                tracker.confidence_threshold = original_threshold
                
            except Exception as e:
                print(f"  Error: {e}")
    
    # Test state summary
    print("\n📊 State Tracker Summary:")
    summary = tracker.get_state_summary()
    print(f"  Has current state: {summary['has_current_state']}")
    print(f"  History size: {summary['history_size']}")
    print(f"  Confidence threshold: {summary['confidence_threshold']}")
    
    print("\n✅ State Tracker test completed!")

if __name__ == "__main__":
    asyncio.run(test_state_tracker())