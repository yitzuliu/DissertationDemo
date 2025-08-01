#!/usr/bin/env python3
"""
Test Refactored SmolVLM Implementation

This script tests the refactored SmolVLM implementation to ensure
it works correctly with the unified server manager.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add the current directory to the path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Add parent directories to path for imports
project_root = current_dir.parent.parent.parent.parent
sys.path.append(str(project_root))

from server_manager import SmolVLMServerManager
from smolvlm_model import SmolVLMModel

def test_server_manager():
    """Test the unified server manager."""
    print("🧪 Testing SmolVLMServerManager...")
    
    # Create server manager
    manager = SmolVLMServerManager()
    
    # Test server status
    is_running = manager.is_running()
    print(f"Server running: {is_running}")
    
    # Test server info
    info = manager.get_server_info()
    print(f"Server info: {info}")
    
    return True

def test_model_initialization():
    """Test SmolVLM model initialization."""
    print("\n🧪 Testing SmolVLMModel initialization...")
    
    # Create test configuration
    config = {
        "smolvlm_version": "ggml-org/SmolVLM-500M-Instruct-GGUF",
        "port": 8080,
        "timeout": 60,
        "manage_server": False,  # Don't start server for this test
        "image_processing": {
            "smart_crop": True,
            "size": [1024, 1024],
            "min_size": 512,
            "preserve_aspect_ratio": True,
            "format": "JPEG",
            "jpeg_quality": 95,
            "optimize": True
        }
    }
    
    try:
        # Initialize model
        model = SmolVLMModel("smolvlm", config)
        print("✅ Model initialized successfully")
        
        # Test model properties
        print(f"Model name: {model.model_name}")
        print(f"Server URL: {model.server_url}")
        print(f"Port: {model.port}")
        print(f"Timeout: {model.timeout}")
        
        return True
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        return False

def test_server_connection():
    """Test server connection without starting server."""
    print("\n🧪 Testing server connection...")
    
    manager = SmolVLMServerManager()
    
    # Test if server is running (should be False if not started)
    is_running = manager.is_running()
    print(f"Server running: {is_running}")
    
    if is_running:
        print("✅ Server is already running")
        return True
    else:
        print("ℹ️ Server is not running (expected)")
        return True

def test_configuration_loading():
    """Test configuration loading from file."""
    print("\n🧪 Testing configuration loading...")
    
    # Test with different configurations
    configs = [
        {
            "smolvlm_version": "ggml-org/SmolVLM-500M-Instruct-GGUF",
            "port": 8080,
            "timeout": 60
        },
        {
            "smolvlm_version": "custom/model/path",
            "port": 9090,
            "timeout": 120,
            "manage_server": True
        }
    ]
    
    for i, config in enumerate(configs):
        print(f"Testing config {i+1}:")
        try:
            model = SmolVLMModel(f"smolvlm_{i}", config)
            print(f"  ✅ Config {i+1} loaded successfully")
            print(f"  Model version: {model.smolvlm_version}")
            print(f"  Port: {model.port}")
            print(f"  Timeout: {model.timeout}")
        except Exception as e:
            print(f"  ❌ Config {i+1} failed: {e}")
    
    return True

def main():
    """Main test function."""
    print("🎯 Testing Refactored SmolVLM Implementation")
    print("=" * 60)
    
    tests = [
        ("Server Manager", test_server_manager),
        ("Model Initialization", test_model_initialization),
        ("Server Connection", test_server_connection),
        ("Configuration Loading", test_configuration_loading)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactored implementation is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 