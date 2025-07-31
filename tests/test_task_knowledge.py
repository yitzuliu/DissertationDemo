#!/usr/bin/env python3
"""
Test script for Task Knowledge System

This script tests the task knowledge data format, validation, and loading functionality.
It verifies that our coffee brewing task data is properly structured and can be loaded correctly.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory.rag.validation import validate_task_file, TaskKnowledgeValidator
from memory.rag.task_loader import TaskKnowledgeLoader, load_coffee_brewing_task


def test_coffee_brewing_validation():
    """Test validation of the coffee brewing task file"""
    print("🧪 Testing Coffee Brewing Task Validation...")
    
    coffee_file = Path("data/tasks/coffee_brewing.yaml")
    
    if not coffee_file.exists():
        print(f"❌ Task file not found: {coffee_file}")
        return False
    
    is_valid, errors = validate_task_file(coffee_file)
    
    if is_valid:
        print("✅ Coffee brewing task validation passed!")
        return True
    else:
        print("❌ Coffee brewing task validation failed:")
        for error in errors:
            print(f"   - {error}")
        return False


def test_task_loading():
    """Test loading of the coffee brewing task"""
    print("\n🧪 Testing Task Loading...")
    
    try:
        # Test specific task loading
        task = load_coffee_brewing_task()
        
        print(f"✅ Successfully loaded task: {task.display_name}")
        print(f"   - Task name: {task.task_name}")
        print(f"   - Total steps: {task.get_total_steps()}")
        print(f"   - Estimated duration: {task.estimated_total_duration}")
        print(f"   - Difficulty: {task.difficulty_level}")
        
        # Test step access
        first_step = task.get_step(1)
        if first_step:
            print(f"   - First step: {first_step.title}")
            print(f"   - Tools needed: {len(first_step.tools_needed)}")
            print(f"   - Visual cues: {len(first_step.visual_cues)}")
        
        # Test aggregated data
        all_tools = task.get_all_tools()
        all_cues = task.get_all_visual_cues()
        print(f"   - Total unique tools: {len(all_tools)}")
        print(f"   - Total unique visual cues: {len(all_cues)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Task loading failed: {str(e)}")
        return False


def test_task_loader_functionality():
    """Test the TaskKnowledgeLoader class functionality"""
    print("\n🧪 Testing TaskKnowledgeLoader Functionality...")
    
    try:
        loader = TaskKnowledgeLoader()
        
        # Test loading
        task = loader.load_task("coffee_brewing")
        print("✅ TaskKnowledgeLoader.load_task() works")
        
        # Test caching
        task2 = loader.load_task("coffee_brewing")  # Should use cache
        assert task is task2, "Caching not working properly"
        print("✅ Task caching works correctly")
        
        # Test task summary
        summary = loader.get_task_summary("coffee_brewing")
        print("✅ Task summary generation works")
        print(f"   - Summary keys: {list(summary.keys())}")
        
        # Test utility methods
        assert loader.is_task_loaded("coffee_brewing"), "is_task_loaded() not working"
        loaded_tasks = loader.get_loaded_tasks()
        assert "coffee_brewing" in loaded_tasks, "get_loaded_tasks() not working"
        print("✅ Utility methods work correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ TaskKnowledgeLoader functionality test failed: {str(e)}")
        return False


def test_step_details():
    """Test detailed step information"""
    print("\n🧪 Testing Step Details...")
    
    try:
        task = load_coffee_brewing_task()
        
        print(f"📋 Coffee Brewing Task - {task.get_total_steps()} Steps:")
        
        for step in task.steps:
            print(f"\n   Step {step.step_id}: {step.title}")
            print(f"   - Description: {step.task_description[:60]}...")
            print(f"   - Tools: {', '.join(step.tools_needed[:3])}{'...' if len(step.tools_needed) > 3 else ''}")
            print(f"   - Visual cues: {', '.join(step.visual_cues[:3])}{'...' if len(step.visual_cues) > 3 else ''}")
            print(f"   - Duration: {step.estimated_duration}")
            
            if step.safety_notes:
                print(f"   - Safety notes: {len(step.safety_notes)} items")
        
        print(f"\n📊 Task Statistics:")
        print(f"   - Total tools needed: {len(task.get_all_tools())}")
        print(f"   - Total visual cues: {len(task.get_all_visual_cues())}")
        print(f"   - Global safety notes: {len(task.global_safety_notes)}")
        print(f"   - Task completion indicators: {len(task.task_completion_indicators)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Step details test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Task Knowledge System Tests\n")
    
    tests = [
        ("Validation", test_coffee_brewing_validation),
        ("Task Loading", test_task_loading),
        ("Loader Functionality", test_task_loader_functionality),
        ("Step Details", test_step_details)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Task knowledge system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)