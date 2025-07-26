#!/usr/bin/env python3
"""
Test Different VLM Response Formats

This script tests how the State Tracker handles different VLM response formats
that various models might return.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append('src')

from state_tracker import StateTracker

async def test_vlm_formats():
    """Test State Tracker with different VLM response formats"""
    print("🧪 Testing Different VLM Response Formats...")
    
    # Initialize State Tracker
    tracker = StateTracker()
    print("✅ State Tracker initialized")
    
    # Test different response formats that VLMs might return
    test_cases = [
        {
            "name": "Simple String",
            "content": "I can see a coffee machine with hot water being poured into a cup"
        },
        {
            "name": "List with Text Objects",
            "content": [
                {"type": "text", "text": "I observe coffee beans being ground"},
                {"type": "text", "text": " in an electric grinder"}
            ]
        },
        {
            "name": "List with Mixed Content",
            "content": [
                {"type": "text", "text": "The coffee filter is being prepared"},
                {"type": "image", "url": "..."},
                {"type": "text", "text": " with fresh coffee grounds"}
            ]
        },
        {
            "name": "Dictionary Format",
            "content": {
                "text": "Hot water is being poured over the coffee grounds in a pour-over setup",
                "confidence": 0.95
            }
        },
        {
            "name": "Simple List of Strings",
            "content": ["Coffee", "is", "being", "brewed", "in", "a", "French", "press"]
        },
        {
            "name": "Empty Content",
            "content": ""
        },
        {
            "name": "None Content",
            "content": None
        }
    ]
    
    print("\n📝 Testing VLM Response Format Handling...")
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test {i+1}: {test_case['name']} ---")
        content = test_case['content']
        
        # Simulate the backend processing logic
        vlm_text = None
        
        try:
            if isinstance(content, str):
                vlm_text = content
                print(f"✅ String format: '{vlm_text[:50]}...'")
            
            elif isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif isinstance(item, str):
                        text_parts.append(item)
                vlm_text = ' '.join(text_parts)
                print(f"✅ List format extracted: '{vlm_text[:50]}...'")
            
            elif isinstance(content, dict):
                vlm_text = content.get('text', str(content))
                print(f"✅ Dict format extracted: '{vlm_text[:50]}...'")
            
            elif content is None:
                vlm_text = ""
                print("⚠️  None content, using empty string")
            
            else:
                vlm_text = str(content)
                print(f"⚠️  Unexpected format ({type(content)}), converted to string")
            
            # Test State Tracker processing
            if vlm_text and len(vlm_text.strip()) > 0:
                # Lower threshold for testing
                original_threshold = tracker.confidence_threshold
                tracker.confidence_threshold = 0.3
                
                result = await tracker.process_vlm_response(vlm_text)
                print(f"📊 State Tracker result: updated={result}")
                
                if result:
                    current_state = tracker.get_current_state()
                    if current_state:
                        print(f"   Current state: task={current_state.get('task_id')}, step={current_state.get('step_index')}, confidence={current_state.get('confidence', 0):.2f}")
                
                # Restore threshold
                tracker.confidence_threshold = original_threshold
            else:
                print("❌ No valid text to process")
                
        except Exception as e:
            print(f"❌ Error processing format: {e}")
    
    # Final state summary
    print("\n📊 Final State Summary:")
    summary = tracker.get_state_summary()
    print(f"  Has current state: {summary['has_current_state']}")
    print(f"  History size: {summary['history_size']}")
    
    if summary['current_state']:
        cs = summary['current_state']
        print(f"  Final state: task={cs.get('task_id')}, step={cs.get('step_index')}")
    
    print("\n✅ VLM format testing completed!")

if __name__ == "__main__":
    asyncio.run(test_vlm_formats())