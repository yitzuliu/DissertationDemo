#!/usr/bin/env python3
"""
Test script to verify detailed response implementation
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from state_tracker.query_processor import QueryProcessor, QueryType

def test_detailed_responses():
    """Test the detailed response functionality"""
    
    # Create query processor
    processor = QueryProcessor()
    
    # Mock state data with detailed step information
    mock_state_data = {
        'task_id': 'brewing_coffee',
        'step_index': 1,
        'confidence': 0.85,
        'matched_step': {
            'step_title': 'Gather Equipment and Ingredients',
            'step_description': 'Collect all necessary equipment and fresh coffee beans for brewing',
            'tools_needed': ['coffee_beans', 'coffee_grinder', 'pour_over_dripper', 'coffee_filter', 'gooseneck_kettle', 'digital_scale', 'timer', 'coffee_mug'],
            'completion_indicators': ['all_equipment_visible_on_counter', 'coffee_beans_ready_for_grinding', 'filter_placed_in_dripper'],
            'visual_cues': ['coffee_beans', 'grinder', 'pour_over_setup', 'scale', 'kettle', 'filter_paper'],
            'estimated_duration': '1-2 minutes',
            'safety_notes': ['ensure_clean_equipment', 'check_grinder_functionality']
        }
    }
    
    print("🧪 Testing Detailed Response Implementation")
    print("=" * 50)
    
    # Test different query types
    test_queries = [
        ("What is the current step?", QueryType.CURRENT_STEP),
        ("What tools do I need?", QueryType.REQUIRED_TOOLS),
        ("How do I do this step?", QueryType.HELP),
        ("What's my progress?", QueryType.COMPLETION_STATUS),
        ("Give me an overview", QueryType.PROGRESS_OVERVIEW)
    ]
    
    for query, expected_type in test_queries:
        print(f"\n📝 Query: '{query}'")
        print(f"🔍 Expected Type: {expected_type.value}")
        
        # Process query
        result = processor.process_query(query, mock_state_data)
        
        print(f"✅ Actual Type: {result.query_type.value}")
        print(f"📋 Response:\n{result.response_text}")
        print("-" * 40)
    
    # Test with no state data
    print(f"\n📝 Query: 'Where am I?' (No state)")
    result = processor.process_query("Where am I?", None)
    print(f"📋 Response: {result.response_text}")

if __name__ == "__main__":
    test_detailed_responses() 