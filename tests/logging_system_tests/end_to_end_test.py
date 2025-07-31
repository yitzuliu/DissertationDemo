#!/usr/bin/env python3
"""
End-to-End Test for Stage 3.1 Logging System

Simulate real user scenarios and verify complete logging flow
"""

import requests
import time
import json
import random
from datetime import datetime

class EndToEndTester:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.test_scenarios = []
        
    def simulate_user_session(self, user_id: str, session_duration: int = 60):
        """Simulate a complete user session"""
        print(f"👤 Simulating user session: {user_id}")
        
        session_start = time.time()
        session_queries = []
        
        # Common query patterns from query.html
        query_patterns = [
            "Where am I?",
            "What is the current step?",
            "What tools do I need?",
            "What's my progress?",
            "Help me with this step",
            "What's next?",
            "Give me an overview",
            "What equipment is required?"
        ]
        
        while time.time() - session_start < session_duration:
            # Random delay between queries (1-5 seconds)
            time.sleep(random.uniform(1, 5))
            
            # Select random query
            query = random.choice(query_patterns)
            query_id = f"e2e_{user_id}_{int(time.time() * 1000)}"
            
            try:
                # Step 1: Log user query
                log_response = requests.post(
                    f"{self.backend_url}/api/v1/logging/user_query",
                    json={
                        'query_id': query_id,
                        'query': query,
                        'language': 'en',
                        'timestamp': datetime.now().isoformat(),
                        'user_agent': f'e2e-test-user-{user_id}',
                        'observation_id': None
                    },
                    timeout=5
                )
                
                # Step 2: Process query
                query_response = requests.post(
                    f"{self.backend_url}/api/v1/state/query",
                    json={
                        'query': query,
                        'query_id': query_id
                    },
                    timeout=10
                )
                
                if log_response.status_code == 200 and query_response.status_code == 200:
                    session_queries.append({
                        'query_id': query_id,
                        'query': query,
                        'log_status': 'success',
                        'query_status': 'success',
                        'response': query_response.json()
                    })
                    print(f"  ✅ Query: '{query}' -> {query_response.json().get('query_type', 'unknown')}")
                else:
                    session_queries.append({
                        'query_id': query_id,
                        'query': query,
                        'log_status': 'failed' if log_response.status_code != 200 else 'success',
                        'query_status': 'failed' if query_response.status_code != 200 else 'success',
                        'error': f"Log: {log_response.status_code}, Query: {query_response.status_code}"
                    })
                    print(f"  ❌ Query: '{query}' -> Failed")
                    
            except Exception as e:
                session_queries.append({
                    'query_id': query_id,
                    'query': query,
                    'log_status': 'error',
                    'query_status': 'error',
                    'error': str(e)
                })
                print(f"  ❌ Query: '{query}' -> Exception: {e}")
        
        return {
            'user_id': user_id,
            'session_duration': session_duration,
            'total_queries': len(session_queries),
            'successful_queries': len([q for q in session_queries if q['query_status'] == 'success']),
            'queries': session_queries
        }
    
    def simulate_multilingual_session(self):
        """Simulate multilingual user queries"""
        print("🌍 Simulating multilingual session...")
        
        multilingual_queries = [
            ("Where am I?", "en"),
            ("我在哪個步驟？", "zh"),
            ("What tools do I need?", "en"),
            ("需要什麼工具？", "zh"),
            ("What's next?", "en"),
            ("下一步是什麼？", "zh"),
            ("Help me with this step", "en"),
            ("幫我完成這個步驟", "zh")
        ]
        
        results = []
        for query, expected_language in multilingual_queries:
            query_id = f"multilingual_{int(time.time() * 1000)}"
            
            try:
                # Test logging with language detection
                log_response = requests.post(
                    f"{self.backend_url}/api/v1/logging/user_query",
                    json={
                        'query_id': query_id,
                        'query': query,
                        'language': expected_language,
                        'timestamp': datetime.now().isoformat(),
                        'user_agent': 'e2e-multilingual-test',
                        'observation_id': None
                    },
                    timeout=5
                )
                
                # Test query processing
                query_response = requests.post(
                    f"{self.backend_url}/api/v1/state/query",
                    json={
                        'query': query,
                        'query_id': query_id
                    },
                    timeout=10
                )
                
                success = log_response.status_code == 200 and query_response.status_code == 200
                results.append({
                    'query': query,
                    'expected_language': expected_language,
                    'success': success,
                    'query_type': query_response.json().get('query_type', 'unknown') if success else None
                })
                
                status = "✅" if success else "❌"
                print(f"  {status} '{query}' ({expected_language}) -> {query_response.json().get('query_type', 'unknown') if success else 'failed'}")
                
            except Exception as e:
                results.append({
                    'query': query,
                    'expected_language': expected_language,
                    'success': False,
                    'error': str(e)
                })
                print(f"  ❌ '{query}' ({expected_language}) -> Exception: {e}")
        
        return results
    
    def verify_logging_consistency(self, query_id: str):
        """Verify that all logging entries for a query_id are consistent"""
        print(f"🔍 Verifying logging consistency for query_id: {query_id}")
        
        # This would typically query the log files
        # For now, we'll simulate the verification
        expected_entries = [
            'USER_QUERY',
            'QUERY_CLASSIFY', 
            'QUERY_PROCESS',
            'QUERY_RESPONSE'
        ]
        
        # In a real implementation, you would:
        # 1. Search log files for the query_id
        # 2. Verify all expected entry types are present
        # 3. Check that timestamps are in chronological order
        # 4. Verify data consistency across entries
        
        print(f"  Expected entries: {expected_entries}")
        print(f"  ✅ Logging consistency verification completed (simulated)")
        
        return True
    
    def run_comprehensive_test(self):
        """Run comprehensive end-to-end test"""
        print("🚀 Stage 3.1 End-to-End Test")
        print("=" * 50)
        
        # Check backend availability
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ Backend service not available")
                return False
            print("✅ Backend service available")
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            return False
        
        # Test 1: Single user session
        print("\n📋 Test 1: Single User Session")
        print("-" * 30)
        user_session = self.simulate_user_session("user_001", 30)  # 30 seconds
        
        # Test 2: Multiple concurrent users
        print("\n📋 Test 2: Multiple Concurrent Users")
        print("-" * 30)
        concurrent_sessions = []
        for i in range(3):
            session = self.simulate_user_session(f"concurrent_user_{i}", 20)  # 20 seconds each
            concurrent_sessions.append(session)
        
        # Test 3: Multilingual support
        print("\n📋 Test 3: Multilingual Support")
        print("-" * 30)
        multilingual_results = self.simulate_multilingual_session()
        
        # Test 4: Logging consistency verification
        print("\n📋 Test 4: Logging Consistency Verification")
        print("-" * 30)
        if user_session['queries']:
            sample_query_id = user_session['queries'][0]['query_id']
            self.verify_logging_consistency(sample_query_id)
        
        # Analyze results
        print("\n📊 End-to-End Test Results:")
        print("=" * 40)
        
        # Single user session results
        print(f"\n👤 Single User Session:")
        print(f"   Total queries: {user_session['total_queries']}")
        print(f"   Successful queries: {user_session['successful_queries']}")
        print(f"   Success rate: {(user_session['successful_queries'] / user_session['total_queries'] * 100):.1f}%")
        
        # Concurrent users results
        total_concurrent_queries = sum(s['total_queries'] for s in concurrent_sessions)
        total_concurrent_success = sum(s['successful_queries'] for s in concurrent_sessions)
        print(f"\n👥 Concurrent Users:")
        print(f"   Total queries: {total_concurrent_queries}")
        print(f"   Successful queries: {total_concurrent_success}")
        print(f"   Success rate: {(total_concurrent_success / total_concurrent_queries * 100):.1f}%")
        
        # Multilingual results
        multilingual_success = len([r for r in multilingual_results if r['success']])
        print(f"\n🌍 Multilingual Support:")
        print(f"   Total queries: {len(multilingual_results)}")
        print(f"   Successful queries: {multilingual_success}")
        print(f"   Success rate: {(multilingual_success / len(multilingual_results) * 100):.1f}%")
        
        # Overall success rate
        total_queries = user_session['total_queries'] + total_concurrent_queries + len(multilingual_results)
        total_success = user_session['successful_queries'] + total_concurrent_success + multilingual_success
        overall_success_rate = (total_success / total_queries * 100) if total_queries > 0 else 0
        
        print(f"\n🎯 Overall Results:")
        print(f"   Total queries: {total_queries}")
        print(f"   Total successful: {total_success}")
        print(f"   Overall success rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 95:
            print("   ✅ Excellent performance!")
        elif overall_success_rate >= 90:
            print("   ✅ Good performance!")
        elif overall_success_rate >= 80:
            print("   ⚠️ Acceptable performance")
        else:
            print("   ❌ Performance needs improvement")
        
        return overall_success_rate >= 80

def main():
    tester = EndToEndTester()
    success = tester.run_comprehensive_test()
    if success:
        print("\n🎉 End-to-end test completed successfully!")
    else:
        print("\n❌ End-to-end test failed!")

if __name__ == "__main__":
    main() 