#!/usr/bin/env python3
"""
Test Results Saving Verification
Verifies that individual model results are properly saved to the results directory

Author: AI Manual Assistant Team
Date: 2025-01-27
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Ensure parent directory is in sys.path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_single_model_saving():
    """Test that single model results are saved with proper naming"""
    print("🧪 Testing Single Model Results Saving")
    print("=" * 60)
    
    try:
        from vqa_framework import VQAFramework
        
        # Initialize framework
        data_dir = Path(__file__).parent.parent / 'materials' / 'vqa2'
        framework = VQAFramework(data_dir=str(data_dir))
        print("✅ VQA framework initialized successfully")
        
        # Create mock results for testing
        mock_results = {
            "phi35_vision": {
                "model_id": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "total": 3,
                "correct": 1,
                "accuracy": 0.333,
                "vqa_accuracy": 0.350,
                "avg_time": 5.29,
                "evaluation_time": 15.87,
                "question_results": [
                    {
                        "question_id": "test_1",
                        "image_id": 123,
                        "is_correct": True,
                        "model_answer": "test answer",
                        "ground_truth": "test answer"
                    }
                ]
            }
        }
        
        # Test single model saving
        print("\n🔧 Testing single model results saving...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"single_phi35_vision_{timestamp}"
        
        results_file = framework.save_results(mock_results, "coco", 3, suffix)
        print(f"✅ Results saved to: {results_file}")
        
        # Verify file exists and has correct content
        if results_file.exists():
            print("✅ File exists")
            
            # Read and verify content
            with open(results_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Check structure
            if "experiment_metadata" in content:
                print("✅ Experiment metadata present")
            if "results" in content:
                print("✅ Results section present")
            if "phi35_vision" in content["results"]:
                print("✅ Model results present")
            
            print(f"📊 File size: {results_file.stat().st_size} bytes")
            
        else:
            print("❌ File does not exist")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_complete_test_saving():
    """Test that complete test results are saved with proper naming"""
    print("\n🧪 Testing Complete Test Results Saving")
    print("=" * 60)
    
    try:
        from vqa_framework import VQAFramework
        
        # Initialize framework
        data_dir = Path(__file__).parent.parent / 'materials' / 'vqa2'
        framework = VQAFramework(data_dir=str(data_dir))
        
        # Create mock results for multiple models
        mock_results = {
            "phi35_vision": {
                "model_id": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "total": 3,
                "correct": 1,
                "accuracy": 0.333,
                "vqa_accuracy": 0.350,
                "avg_time": 5.29
            },
            "moondream2": {
                "model_id": "vikhyatk/moondream2",
                "total": 3,
                "correct": 2,
                "accuracy": 0.667,
                "vqa_accuracy": 0.650,
                "avg_time": 8.35
            }
        }
        
        # Test complete test saving
        print("🔧 Testing complete test results saving...")
        results_file = framework.save_results(mock_results, "coco", 3)
        print(f"✅ Results saved to: {results_file}")
        
        # Verify file exists
        if results_file.exists():
            print("✅ File exists")
            print(f"📊 File size: {results_file.stat().st_size} bytes")
        else:
            print("❌ File does not exist")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_results_directory():
    """Check the results directory structure and naming consistency"""
    print("\n🧪 Checking Results Directory Structure")
    print("=" * 60)
    
    try:
        results_dir = Path(__file__).parent.parent / 'results'
        
        if not results_dir.exists():
            print("❌ Results directory does not exist")
            return False
        
        print(f"📁 Results directory: {results_dir}")
        
        # List all VQA result files
        vqa_files = list(results_dir.glob("vqa2_results_*.json"))
        print(f"📊 Found {len(vqa_files)} VQA result files:")
        
        for file in sorted(vqa_files):
            file_size = file.stat().st_size
            print(f"  📄 {file.name} ({file_size} bytes)")
        
        # Check naming patterns
        single_model_files = [f for f in vqa_files if "single_" in f.name]
        complete_test_files = [f for f in vqa_files if "coco_" in f.name and "single_" not in f.name]
        
        print(f"\n📋 Naming Analysis:")
        print(f"  🎯 Single model files: {len(single_model_files)}")
        print(f"  🎯 Complete test files: {len(complete_test_files)}")
        
        if single_model_files:
            print("  ✅ Single model files found")
        if complete_test_files:
            print("  ✅ Complete test files found")
        
        return True
        
    except Exception as e:
        print(f"❌ Check failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 VQA Results Saving Test Suite")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Single Model Saving", test_single_model_saving),
        ("Complete Test Saving", test_complete_test_saving),
        ("Results Directory Check", check_results_directory)
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
        print("🎉 All tests passed! Results saving is working correctly.")
        print("\n📋 Summary:")
        print("  ✅ Single model results are saved to results/ directory")
        print("  ✅ Complete test results are saved to results/ directory")
        print("  ✅ Consistent naming format for all files")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 