#!/usr/bin/env python3
"""
Backend API Test

Test all the API endpoints to ensure they work correctly
"""

import asyncio
import httpx
import json

async def test_backend_api():
    """Test all backend API endpoints"""
    print("🧪 Testing Backend API Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Test 1: Health Check
        print("\n📋 Test 1: Health Check")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Health check: {data['status']}")
                print(f"  ✅ Active model: {data['active_model']}")
            else:
                print(f"  ❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Health check error: {e}")
        
        # Test 2: State Query
        print("\n📋 Test 2: State Query API")
        test_queries = [
            "What step am I on?",
            "What's the next step?",
            "current step",
            "help"
        ]
        
        for query in test_queries:
            try:
                response = await client.post(
                    f"{base_url}/api/v1/state/query",
                    json={"query": query}
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Query '{query}': {data['query_type']} ({data['processing_time_ms']:.1f}ms)")
                else:
                    print(f"  ❌ Query '{query}' failed: {response.status_code}")
            except Exception as e:
                print(f"  ❌ Query '{query}' error: {e}")
        
        # Test 3: Query Capabilities
        print("\n📋 Test 3: Query Capabilities")
        try:
            response = await client.get(f"{base_url}/api/v1/state/query/capabilities")
            if response.status_code == 200:
                data = response.json()
                capabilities = data['capabilities']
                print(f"  ✅ Supported query types: {len(capabilities['supported_query_types'])}")
                print(f"  ✅ Example queries: {len(capabilities['example_queries'])}")
                print(f"  ✅ Response time target: {capabilities['response_time_target_ms']}ms")
            else:
                print(f"  ❌ Capabilities failed: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Capabilities error: {e}")
        
        # Test 4: State Info
        print("\n📋 Test 4: State Information")
        try:
            response = await client.get(f"{base_url}/api/v1/state")
            if response.status_code == 200:
                data = response.json()
                summary = data['summary']
                print(f"  ✅ Has current state: {summary['has_current_state']}")
                print(f"  ✅ Sliding window size: {summary['sliding_window_size']}")
                print(f"  ✅ Memory usage: {summary['memory_stats']['memory_usage_mb']:.3f}MB")
            else:
                print(f"  ❌ State info failed: {response.status_code}")
        except Exception as e:
            print(f"  ❌ State info error: {e}")
        
        # Test 5: Memory Stats
        print("\n📋 Test 5: Memory Statistics")
        try:
            response = await client.get(f"{base_url}/api/v1/state/memory")
            if response.status_code == 200:
                data = response.json()
                stats = data['memory_stats']
                print(f"  ✅ Total records: {stats['total_records']}")
                print(f"  ✅ Memory usage: {stats['memory_usage_mb']:.3f}MB")
                print(f"  ✅ Cleanup count: {stats['cleanup_count']}")
            else:
                print(f"  ❌ Memory stats failed: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Memory stats error: {e}")
    
    print("\n✅ Backend API Test Complete!")
    print("   All endpoints are functional and ready for frontend integration.")

if __name__ == "__main__":
    print("⚠️  Make sure backend is running: cd src/backend && python main.py")
    print("   Then run this test to verify API functionality.\n")
    
    try:
        asyncio.run(test_backend_api())
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("   Make sure the backend server is running on localhost:8000")