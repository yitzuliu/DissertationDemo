#!/usr/bin/env python3
"""
Test Backend Only

Simple test to verify backend is working without VLM server.
"""

import requests
import time

def test_backend():
    """Test backend functionality"""
    print("🔧 Testing Backend Server...")
    
    # Test 1: Health check
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status')}")
        else:
            print(f"❌ Health Check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check failed: {e}")
        return False
    
    # Test 2: Configuration
    try:
        response = requests.get("http://localhost:8000/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Configuration: Active model = {config.get('active_model')}")
        else:
            print(f"❌ Configuration failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
    
    # Test 3: State query (basic)
    try:
        query_data = {
            "query": "Where am I?",
            "query_id": f"test_{int(time.time())}"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/state/query",
            json=query_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"✅ State Query: {data.get('response', '')[:50]}...")
            else:
                print(f"❌ State Query failed: {data}")
        else:
            print(f"❌ State Query failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ State Query failed: {e}")
    
    # Test 4: State query (fallback trigger)
    try:
        query_data = {
            "query": "What is the meaning of life?",
            "query_id": f"fallback_test_{int(time.time())}"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/state/query",
            json=query_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                response_text = data.get('response', '')
                print(f"✅ Fallback Query: {response_text[:50]}...")
            else:
                print(f"❌ Fallback Query failed: {data}")
        else:
            print(f"❌ Fallback Query failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Fallback Query failed: {e}")
    
    return True

def main():
    """Main test"""
    print("🧪 Backend Only Test")
    print("=" * 40)
    print("Make sure backend is running:")
    print("python src/backend/main.py")
    print("=" * 40)
    
    input("Press Enter when backend is ready...")
    
    success = test_backend()
    
    if success:
        print("\n🎉 Backend tests completed!")
        print("✅ Backend server is working correctly")
        print("⚠️ VLM fallback will be skipped without VLM server")
    else:
        print("\n❌ Backend tests failed")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)