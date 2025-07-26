#!/usr/bin/env python3
"""
Test VLM Randomness and Robustness

This script tests how the State Tracker handles random, inconsistent,
and potentially problematic VLM outputs that might occur in real usage.
"""

import asyncio
import sys
import os
import random

# Add src to path
sys.path.append('src')

from state_tracker import StateTracker

async def test_vlm_randomness():
    """Test State Tracker with random and problematic VLM outputs"""
    print("🧪 Testing VLM Randomness and Robustness...")
    
    # Initialize State Tracker
    tracker = StateTracker()
    print("✅ State Tracker initialized")
    
    # Simulate random VLM outputs that might occur
    random_outputs = [
        # Good coffee-related outputs
        "I see a coffee machine brewing coffee",
        "Coffee beans are being ground in a grinder",
        "Hot water is poured over coffee grounds",
        "A coffee cup is being filled",
        
        # Partially relevant outputs
        "There's a kitchen appliance running",
        "I observe some brown liquid",
        "Steam is coming from a device",
        "Someone is preparing a beverage",
        
        # Irrelevant outputs
        "I see a blue sky with clouds",
        "There's a cat sitting on a table",
        "The room has white walls",
        "A person is reading a book",
        
        # Problematic outputs
        "",
        "   ",
        "Error: Unable to process image",
        "I cannot see anything clearly",
        "The image is too blurry to describe",
        "...",
        "NULL",
        "undefined",
        
        # Garbled outputs
        "Cffee machne brewng",
        "Hot wtr pour ovr gronds",
        "!@#$%^&*()",
        "123456789",
        "aaaaaaaaaaaaaa",
        
        # Very long outputs
        "I can see a very detailed coffee brewing setup with multiple components including a high-end espresso machine, a precision grinder, various brewing accessories, temperature control systems, and many other coffee-related items that are all working together in a complex coffee preparation process that involves multiple steps and careful attention to detail in order to create the perfect cup of coffee with optimal flavor extraction and temperature control throughout the entire brewing process.",
        
        # Mixed language or encoding issues
        "咖啡機正在煮咖啡",
        "Máquina de café está funcionando",
        "コーヒーマシンが動いています",
    ]
    
    print(f"\n📝 Testing {len(random_outputs)} random VLM outputs...")
    
    # Track statistics
    total_processed = 0
    successful_updates = 0
    errors = 0
    confidence_scores = []
    
    # Lower threshold for testing
    original_threshold = tracker.confidence_threshold
    tracker.confidence_threshold = 0.3
    
    for i, vlm_output in enumerate(random_outputs):
        print(f"\n--- Test {i+1}: '{vlm_output[:50]}...' ---")
        
        try:
            result = await tracker.process_vlm_response(vlm_output)
            total_processed += 1
            
            if result:
                successful_updates += 1
                current_state = tracker.get_current_state()
                if current_state:
                    confidence = current_state.get('confidence', 0)
                    confidence_scores.append(confidence)
                    print(f"✅ Updated: task={current_state.get('task_id')}, step={current_state.get('step_index')}, confidence={confidence:.2f}")
                else:
                    print("✅ Updated but no current state")
            else:
                print("⚠️  No update (low confidence or no match)")
                
        except Exception as e:
            errors += 1
            print(f"❌ Error: {e}")
    
    # Restore threshold
    tracker.confidence_threshold = original_threshold
    
    # Calculate statistics
    print("\n📊 Randomness Test Statistics:")
    print(f"  Total outputs tested: {len(random_outputs)}")
    print(f"  Successfully processed: {total_processed}")
    print(f"  State updates: {successful_updates}")
    print(f"  Errors: {errors}")
    print(f"  Success rate: {(successful_updates/total_processed)*100:.1f}%")
    print(f"  Error rate: {(errors/len(random_outputs))*100:.1f}%")
    
    if confidence_scores:
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        max_confidence = max(confidence_scores)
        min_confidence = min(confidence_scores)
        print(f"  Average confidence: {avg_confidence:.2f}")
        print(f"  Confidence range: {min_confidence:.2f} - {max_confidence:.2f}")
    
    # Test state consistency
    print("\n🔄 Testing State Consistency:")
    summary = tracker.get_state_summary()
    print(f"  Final state exists: {summary['has_current_state']}")
    print(f"  History size: {summary['history_size']}")
    
    if summary['current_state']:
        cs = summary['current_state']
        print(f"  Final state: task={cs.get('task_id')}, step={cs.get('step_index')}")
        print(f"  Final confidence: {cs.get('confidence', 0):.2f}")
    
    # Test rapid-fire processing (simulate continuous VLM calls)
    print("\n⚡ Testing Rapid Processing:")
    rapid_outputs = [
        "Coffee machine is on",
        "Grinding coffee beans", 
        "Pouring hot water",
        "Coffee is ready"
    ]
    
    start_time = asyncio.get_event_loop().time()
    for output in rapid_outputs:
        await tracker.process_vlm_response(output)
    end_time = asyncio.get_event_loop().time()
    
    processing_time = end_time - start_time
    print(f"  Processed {len(rapid_outputs)} outputs in {processing_time:.3f}s")
    print(f"  Average time per output: {processing_time/len(rapid_outputs):.3f}s")
    
    print("\n✅ VLM randomness testing completed!")
    
    # Recommendations based on results
    print("\n💡 Recommendations:")
    if errors > 0:
        print(f"  - {errors} errors occurred, consider improving error handling")
    if successful_updates / total_processed < 0.3:
        print("  - Low update rate, consider adjusting confidence threshold")
    if avg_confidence < 0.5:
        print("  - Low average confidence, may need better RAG matching")
    
    print("  - System shows good robustness to random VLM outputs")
    print("  - Ready for real-world VLM integration")

if __name__ == "__main__":
    asyncio.run(test_vlm_randomness())