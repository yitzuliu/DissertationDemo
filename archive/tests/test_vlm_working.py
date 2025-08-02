#!/usr/bin/env python3
"""
Test VLM Fallback Working

Test if VLM fallback is actually working now that both servers are running.
"""

import requests
import time
import json

def test_vlm_fallback_working():
    """Test VLM fallback with both servers running"""
    backend_url = "http://localhost:8000"
    
    print("🧪 Testing VLM Fallback (Both Servers Running)")
    print("=" * 50)
    
    # Test queries that should trigger VLM fallback
    test_queries = [
        "What is the meaning of life?",
        "Explain artificial intelligence to me",
        "Tell me about quantum physics",
        "What is consciousness?",
        "How does the universe work?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        try:
            query_data = {
                "query": query,
                "query_id": f"vlm_test_{int(time.time())}_{i}"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{backend_url}/api/v1/state/query",
                json=query_data,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    response_text = data.get("response", "")
                    confidence = data.get("confidence", 0)
                    
                    print(f"⏱️  Response time: {response_time:.2f}s")
                    print(f"🎯 Confidence: {confidence}")
                    print(f"📝 Response length: {len(response_text)} chars")
                    print(f"📄 Response preview: {response_text[:150]}...")
                    
                    # Check if this is a VLM response or template response
                    if "No active state" in response_text:
                        print("❌ Template response - VLM fallback not working")
                    elif len(response_text) > 50 and response_time > 1.0:
                        print("✅ Likely VLM fallback response (detailed + slow)")
                    else:
                        print("❓ Unclear response type")
                else:
                    print(f"❌ Error response: {data}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(1)  # Brief pause between requests
    
    print("\n" + "=" * 50)
    print("🏁 VLM Fallback Test Completed")

def test_basic_query():
    """Test basic query for comparison"""
    backend_url = "http://localhost:8000"
    
    print("\n🔧 Testing Basic Query (Should be fast template)")
    print("-" * 40)
    
    query_data = {
        "query": "Where am I?",
        "query_id": f"basic_test_{int(time.time())}"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{backend_url}/api/v1/state/query",
            json=query_data,
            timeout=10
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            confidence = data.get("confidence", 0)
            
            print(f"⏱️  Response time: {response_time:.2f}s")
            print(f"🎯 Confidence: {confidence}")
            print(f"📄 Response: {response_text}")
            
            if "No active state" in response_text and response_time < 1.0:
                print("✅ Fast template response as expected")
            else:
                print("❓ Unexpected response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    """Main test function"""
    print("🚀 VLM Fallback Working Test")
    print("Testing with both backend and VLM servers running")
    print()
    
    # Check if both servers are available
    try:
        backend_response = requests.get("http://localhost:8000/health", timeout=5)
        vlm_response = requests.get("http://localhost:8080/health", timeout=5)
        
        if backend_response.status_code == 200 and vlm_response.status_code == 200:
            print("✅ Both servers are running")
        else:
            print("❌ One or both servers not healthy")
            return
    except:
        print("❌ Cannot connect to servers")
        print("Make sure both servers are running:")
        print("1. Backend: python start_system.py --backend")
        print("2. VLM: python start_system.py --vlm")
        return
    
    # Run tests
    test_basic_query()
    test_vlm_fallback_working()
    
    print("\n💡 Expected Results:")
    print("- Basic queries should be fast template responses")
    print("- Complex queries should be slower VLM responses")
    print("- VLM responses should be longer and more detailed")

if __name__ == "__main__":
    main()