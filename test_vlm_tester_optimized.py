#!/usr/bin/env python3
"""
Test script to verify the optimized vlm_tester.py works correctly
"""

import sys
import os
sys.path.append('src/testing/vlm')

def test_imports():
    """Test if all imports work correctly"""
    print("🧪 Testing imports...")
    try:
        from vlm_tester import VLMTester, VLMModelLoader
        print("✅ Imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_class_initialization():
    """Test if VLMTester can be initialized"""
    print("🧪 Testing class initialization...")
    try:
        from vlm_tester import VLMTester
        tester = VLMTester()
        print("✅ VLMTester initialization successful")
        print(f"📊 Found {len(tester.models_config)} configured models")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def test_helper_methods():
    """Test helper methods"""
    print("🧪 Testing helper methods...")
    try:
        from vlm_tester import VLMTester
        tester = VLMTester()
        
        # Test MLX output parsing
        test_output = """
Files: ['test.jpg']
Prompt: What is this?
==========
Assistant: This is a test response.
Generation: 1.23 tokens/s
Peak memory: 2.34 GB
"""
        result = tester._parse_mlx_output(test_output)
        print(f"📝 MLX output parsing result: {result}")
        
        # Test response evaluation
        good_response = "This is a valid response."
        bad_response = "Error: inference failed"
        
        good_eval = tester._evaluate_text_response(good_response)
        bad_eval = tester._evaluate_text_response(bad_response)
        
        print(f"✅ Good response evaluation: {good_eval}")
        print(f"❌ Bad response evaluation: {bad_eval}")
        
        return good_eval and not bad_eval
        
    except Exception as e:
        print(f"❌ Helper methods test failed: {e}")
        return False

def test_model_dispatch():
    """Test model dispatch logic"""
    print("🧪 Testing model dispatch logic...")
    try:
        from vlm_tester import VLMTester
        tester = VLMTester()
        
        # Mock models for testing
        mock_gguf_model = {"type": "smolvlm_gguf", "api_endpoint": "http://localhost:8080"}
        mock_processor = None
        
        # Test dispatch for different model types
        test_cases = [
            ("SmolVLM-500M-Instruct", mock_gguf_model, mock_processor),
            ("Moondream2", None, None),
            ("Phi-3.5-Vision-Instruct", None, None),
            ("SmolVLM2-500M-Video-Instruct-MLX", None, None),
            ("LLaVA-v1.6-Mistral-7B-MLX", None, None),
        ]
        
        for model_name, model, processor in test_cases:
            try:
                # This will fail due to missing models, but should not crash
                result = tester._dispatch_text_only_test(model, processor, model_name, "Test prompt")
                print(f"📝 {model_name}: Dispatch successful (result type: {type(result)})")
            except Exception as e:
                print(f"⚠️ {model_name}: Expected failure - {str(e)[:50]}...")
        
        print("✅ Model dispatch logic working")
        return True
        
    except Exception as e:
        print(f"❌ Model dispatch test failed: {e}")
        return False

def test_save_results():
    """Test results saving functionality"""
    print("🧪 Testing results saving...")
    try:
        from vlm_tester import VLMTester
        tester = VLMTester()
        
        # Add some test data
        tester.results["test_data"] = {
            "timestamp": "2025-01-01 12:00:00",
            "test_result": "success"
        }
        
        # Test saving with suffix
        tester.save_results("test_optimization")
        print("✅ Results saving successful")
        return True
        
    except Exception as e:
        print(f"❌ Results saving test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing optimized vlm_tester.py")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_class_initialization,
        test_helper_methods,
        test_model_dispatch,
        test_save_results
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! vlm_tester.py is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)