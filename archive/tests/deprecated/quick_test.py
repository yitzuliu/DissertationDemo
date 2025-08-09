#!/usr/bin/env python3
"""
Quick System Test

A simple script to quickly verify that your system is working.
Run this after starting both backend and VLM servers.

Usage:
    python quick_test.py
"""

import requests
import json
import base64
import io
from PIL import Image

def create_simple_image():
    """Create a simple test image"""
    img = Image.new('RGB', (200, 200), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_data = buffer.getvalue()
    base64_string = base64.b64encode(img_data).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_string}"

def test_backend():
    """Test backend server"""
    print("🔧 Testing Backend...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_vlm():
    """Test VLM server"""
    print("🤖 Testing VLM...")
    try:
        response = requests.get("http://localhost:8080/health", timeout=10)
        if response.status_code == 200:
            print("✅ VLM is running")
            return True
        else:
            print(f"❌ VLM error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ VLM not accessible: {e}")
        return False

def test_state_query():
    """Test state query"""
    print("🔍 Testing State Query...")
    try:
        data = {"query": "Where am I?", "query_id": "test_123"}
        response = requests.post(
            "http://localhost:8000/api/v1/state/query",
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ State Query works: {result.get('response', '')[:50]}...")
            return True
        else:
            print(f"❌ State Query error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ State Query failed: {e}")
        return False

def test_vision_analysis():
    """Test vision analysis"""
    print("👁️ Testing Vision Analysis...")
    try:
        test_image = create_simple_image()
        data = {
            "max_tokens": 50,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What color is this image?"},
                    {"type": "image_url", "image_url": {"url": test_image}}
                ]
            }]
        }
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"✅ Vision Analysis works: {content[:50]}...")
            return True
        else:
            print(f"❌ Vision Analysis error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Vision Analysis failed: {e}")
        return False

def test_fallback():
    """Test VLM fallback"""
    print("🔄 Testing VLM Fallback...")
    try:
        data = {
            "query": "Explain the concept of artificial intelligence",
            "query_id": "fallback_test"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/state/query",
            json=data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            if len(response_text) > 100:
                print(f"✅ VLM Fallback triggered: {response_text[:50]}...")
            else:
                print(f"✅ Template response: {response_text[:50]}...")
            return True
        else:
            print(f"❌ Fallback test error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False

def main():
    """Run quick tests"""
    print("🚀 Quick System Test")
    print("=" * 40)
    print("Make sure both servers are running:")
    print("1. python src/backend/main.py")
    print("2. python src/models/smolvlm/run_smolvlm.py")
    print("=" * 40)
    
    tests = [
        ("Backend", test_backend),
        ("VLM Server", test_vlm),
        ("State Query", test_state_query),
        ("Vision Analysis", test_vision_analysis),
        ("VLM Fallback", test_fallback)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 40)
    print("📊 RESULTS")
    print("=" * 40)
    
    passed = 0
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
        if success:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed!")
        print("✅ Your system is working correctly!")
        print("🌐 You can now open src/frontend/index.html")
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed")
        print("Please check the error messages above")
    
    return passed == len(results)

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)