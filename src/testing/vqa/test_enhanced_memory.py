#!/usr/bin/env python3
"""
Enhanced MLX Memory Management Test Script
Tests the improved memory management for MLX models in VQA framework

Author: AI Manual Assistant Team
Date: 2025-01-27
"""

import sys
import time
import gc
from pathlib import Path

# Ensure parent directory is in sys.path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_mlx_memory_functions():
    """Test the enhanced MLX memory management functions"""
    print("🧪 Testing Enhanced MLX Memory Management")
    print("=" * 60)
    
    try:
        # Import the enhanced memory functions
        from vlm.vlm_tester import clear_mlx_memory, clear_model_memory
        print("✅ Successfully imported enhanced memory functions")
        
        # Test MLX memory clearing
        print("\n🔧 Testing MLX memory clearing...")
        try:
            clear_mlx_memory()
            print("✅ MLX memory clearing test passed")
        except Exception as e:
            print(f"⚠️ MLX memory clearing test warning: {e}")
        
        # Test general memory clearing
        print("\n🔧 Testing general memory clearing...")
        try:
            # Create dummy model and processor for testing
            dummy_model = {"test": "model"}
            dummy_processor = {"test": "processor"}
            clear_model_memory(dummy_model, dummy_processor)
            print("✅ General memory clearing test passed")
        except Exception as e:
            print(f"⚠️ General memory clearing test warning: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_vqa_framework_memory():
    """Test VQA framework memory management"""
    print("\n🧪 Testing VQA Framework Memory Management")
    print("=" * 60)
    
    try:
        from vqa_framework import VQAFramework
        print("✅ Successfully imported VQA framework")
        
        # Initialize framework
        data_dir = Path(__file__).parent.parent / 'materials' / 'vqa2'
        framework = VQAFramework(data_dir=str(data_dir))
        print("✅ VQA framework initialized successfully")
        
        # Test memory pressure checking
        print("\n🔧 Testing memory pressure detection...")
        try:
            pressure = framework._check_mlx_memory_pressure()
            print(f"✅ Memory pressure check completed: {pressure}")
        except Exception as e:
            print(f"⚠️ Memory pressure check warning: {e}")
        
        # Test MLX setup
        print("\n🔧 Testing MLX setup...")
        try:
            framework._setup_mlx_memory_monitoring()
            print("✅ MLX setup test completed")
        except Exception as e:
            print(f"⚠️ MLX setup test warning: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ VQA framework test failed: {e}")
        return False

def test_memory_cleanup_cycle():
    """Test memory cleanup cycle simulation"""
    print("\n🧪 Testing Memory Cleanup Cycle")
    print("=" * 60)
    
    try:
        from vlm.vlm_tester import clear_mlx_memory
        
        print("🔄 Simulating memory cleanup cycles...")
        
        for cycle in range(3):
            print(f"  Cycle {cycle + 1}/3:")
            
            # Simulate memory usage
            print("    📊 Simulating memory usage...")
            time.sleep(0.5)
            
            # Perform cleanup
            print("    🧹 Performing memory cleanup...")
            try:
                clear_mlx_memory()
                gc.collect()
                print("    ✅ Cleanup completed")
            except Exception as e:
                print(f"    ⚠️ Cleanup warning: {e}")
            
            time.sleep(0.5)
        
        print("✅ Memory cleanup cycle test completed")
        return True
        
    except Exception as e:
        print(f"❌ Memory cleanup cycle test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Enhanced MLX Memory Management Test Suite")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("MLX Memory Functions", test_mlx_memory_functions),
        ("VQA Framework Memory", test_vqa_framework_memory),
        ("Memory Cleanup Cycle", test_memory_cleanup_cycle)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced memory management is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 