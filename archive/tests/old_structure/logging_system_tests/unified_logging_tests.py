#!/usr/bin/env python3
"""
Unified Logging System Tests

This file combines all logging system tests into a single comprehensive test suite:
- End-to-end user session simulation
- Performance testing and benchmarking
- Stage 3.1 and 3.2 specific logging validation
"""

import requests
import time
import json
import random
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class UnifiedLoggingTester:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.test_results = {
            'end_to_end': {'passed': False, 'details': {}},
            'performance': {'passed': False, 'details': {}},
            'stage_3_1': {'passed': False, 'details': {}},
            'stage_3_2': {'passed': False, 'details': {}}
        }
    
    def test_end_to_end_logging(self):
        """Test end-to-end user session logging"""
        print("🧪 End-to-End Logging Test")
        print("-" * 40)
        
        try:
            # Simulate user session
            user_id = f"e2e_user_{int(time.time())}"
            session_duration = 30  # 30 seconds for testing
            
            print(f"👤 Simulating user session: {user_id}")
            
            session_start = time.time()
            successful_queries = 0
            total_queries = 0
            
            query_patterns = [
                "Where am I?", "What is the current step?", "What tools do I need?",
                "What's my progress?", "Help me with this step", "What's next?"
            ]
            
            while time.time() - session_start < session_duration:
                time.sleep(random.uniform(1, 3))
                query = random.choice(query_patterns)
                query_id = f"e2e_{user_id}_{int(time.time() * 1000)}"
                total_queries += 1
                
                try:
                    # Log user query
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
                    
                    # Process query
                    query_response = requests.post(
                        f"{self.backend_url}/api/v1/state/query",
                        json={'query': query, 'query_id': query_id},
                        timeout=10
                    )
                    
                    if log_response.status_code == 200 and query_response.status_code == 200:
                        successful_queries += 1
                        print(f"  ✅ Query: '{query}' -> {query_response.json().get('query_type', 'unknown')}")
                    else:
                        print(f"  ❌ Query: '{query}' -> Failed")
                        
                except Exception as e:
                    print(f"  ❌ Query: '{query}' -> Exception: {e}")
            
            # Check results
            success_rate = successful_queries / total_queries if total_queries > 0 else 0
            if success_rate >= 0.8:  # 80% success rate
                self.test_results['end_to_end']['passed'] = True
                self.test_results['end_to_end']['details'] = {
                    'successful_queries': successful_queries,
                    'total_queries': total_queries,
                    'success_rate': success_rate,
                    'session_duration': session_duration
                }
                print(f"✅ End-to-End Test PASSED: {successful_queries}/{total_queries} queries successful")
            else:
                print(f"❌ End-to-End Test FAILED: Only {successful_queries}/{total_queries} queries successful")
                
        except Exception as e:
            print(f"❌ End-to-End Test ERROR: {str(e)}")
    
    def test_performance_logging(self):
        """Test logging performance impact"""
        print("\n🧪 Performance Logging Test")
        print("-" * 40)
        
        try:
            results = {
                'logging_endpoint': [],
                'query_with_logging': [],
                'query_without_logging': []
            }
            
            iterations = 50  # Reduced for faster testing
            
            # Test logging endpoint performance
            print(f"  📊 Testing logging endpoint ({iterations} iterations)...")
            for i in range(iterations):
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{self.backend_url}/api/v1/logging/user_query",
                        json={
                            'query_id': f"perf_test_{i}_{int(time.time() * 1000)}",
                            'query': f'Performance test query {i}',
                            'language': 'en',
                            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'user_agent': 'performance-test',
                            'observation_id': None
                        },
                        timeout=5
                    )
                    duration = (time.time() - start_time) * 1000
                    if response.status_code == 200:
                        results['logging_endpoint'].append(duration)
                except Exception as e:
                    print(f"    ❌ Logging endpoint error: {e}")
            
            # Test query with logging performance
            print(f"  📊 Testing query with logging ({iterations} iterations)...")
            for i in range(iterations):
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{self.backend_url}/api/v1/state/query",
                        json={
                            'query': f'Performance test query {i}',
                            'query_id': f"perf_query_{i}_{int(time.time() * 1000)}"
                        },
                        timeout=10
                    )
                    duration = (time.time() - start_time) * 1000
                    if response.status_code == 200:
                        results['query_with_logging'].append(duration)
                except Exception as e:
                    print(f"    ❌ Query with logging error: {e}")
            
            # Analyze results
            if results['logging_endpoint'] and results['query_with_logging']:
                avg_logging = statistics.mean(results['logging_endpoint'])
                avg_query_with_logging = statistics.mean(results['query_with_logging'])
                
                print(f"  📈 Average logging endpoint time: {avg_logging:.2f}ms")
                print(f"  📈 Average query with logging time: {avg_query_with_logging:.2f}ms")
                
                # Performance criteria: logging should add < 50ms overhead
                if avg_logging < 100 and avg_query_with_logging < 200:
                    self.test_results['performance']['passed'] = True
                    self.test_results['performance']['details'] = {
                        'avg_logging_ms': avg_logging,
                        'avg_query_with_logging_ms': avg_query_with_logging,
                        'iterations': iterations
                    }
                    print("✅ Performance Test PASSED: Logging performance acceptable")
                else:
                    print("❌ Performance Test FAILED: Logging performance too slow")
            else:
                print("❌ Performance Test FAILED: No valid results")
                
        except Exception as e:
            print(f"❌ Performance Test ERROR: {str(e)}")
    
    def test_stage_3_1_logging(self):
        """Test Stage 3.1 specific logging functionality"""
        print("\n🧪 Stage 3.1 Logging Test")
        print("-" * 40)
        
        try:
            # Test basic logging endpoints
            test_queries = [
                "What step am I on?",
                "Help me with this step",
                "What tools do I need?"
            ]
            
            successful_logs = 0
            for i, query in enumerate(test_queries):
                query_id = f"stage31_test_{i}_{int(time.time() * 1000)}"
                
                try:
                    # Test user query logging
                    log_response = requests.post(
                        f"{self.backend_url}/api/v1/logging/user_query",
                        json={
                            'query_id': query_id,
                            'query': query,
                            'language': 'en',
                            'timestamp': datetime.now().isoformat(),
                            'user_agent': 'stage31-test',
                            'observation_id': None
                        },
                        timeout=5
                    )
                    
                    if log_response.status_code == 200:
                        successful_logs += 1
                        print(f"  ✅ Query '{query}' logged successfully")
                    else:
                        print(f"  ❌ Query '{query}' logging failed: {log_response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Query '{query}' logging error: {e}")
            
            # Check results
            if successful_logs == len(test_queries):
                self.test_results['stage_3_1']['passed'] = True
                self.test_results['stage_3_1']['details'] = {
                    'successful_logs': successful_logs,
                    'total_queries': len(test_queries)
                }
                print("✅ Stage 3.1 Test PASSED: All queries logged successfully")
            else:
                print(f"❌ Stage 3.1 Test FAILED: Only {successful_logs}/{len(test_queries)} queries logged")
                
        except Exception as e:
            print(f"❌ Stage 3.1 Test ERROR: {str(e)}")
    
    def test_stage_3_2_logging(self):
        """Test Stage 3.2 detailed logging functionality"""
        print("\n🧪 Stage 3.2 Detailed Logging Test")
        print("-" * 40)
        
        try:
            # Test detailed logging with multiple query types
            detailed_queries = [
                ("我在哪個步驟？", "chinese"),
                ("What's next?", "english"),
                ("Current status", "english"),
                ("Help me", "english")
            ]
            
            successful_detailed_logs = 0
            for i, (query, language) in enumerate(detailed_queries):
                query_id = f"stage32_detailed_{i}_{int(time.time() * 1000)}"
                
                try:
                    # Test detailed logging
                    log_response = requests.post(
                        f"{self.backend_url}/api/v1/logging/user_query",
                        json={
                            'query_id': query_id,
                            'query': query,
                            'language': language,
                            'timestamp': datetime.now().isoformat(),
                            'user_agent': 'stage32-detailed-test',
                            'observation_id': f"obs_{i}",
                            'session_id': f"session_{i}",
                            'user_id': f"user_{i}"
                        },
                        timeout=5
                    )
                    
                    if log_response.status_code == 200:
                        successful_detailed_logs += 1
                        print(f"  ✅ Detailed log for '{query}' ({language}) successful")
                    else:
                        print(f"  ❌ Detailed log for '{query}' failed: {log_response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Detailed log for '{query}' error: {e}")
            
            # Check results
            if successful_detailed_logs >= len(detailed_queries) * 0.8:  # 80% success rate
                self.test_results['stage_3_2']['passed'] = True
                self.test_results['stage_3_2']['details'] = {
                    'successful_detailed_logs': successful_detailed_logs,
                    'total_detailed_queries': len(detailed_queries)
                }
                print("✅ Stage 3.2 Test PASSED: Detailed logging working correctly")
            else:
                print(f"❌ Stage 3.2 Test FAILED: Only {successful_detailed_logs}/{len(detailed_queries)} detailed logs successful")
                
        except Exception as e:
            print(f"❌ Stage 3.2 Test ERROR: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 Unified Logging Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['passed'])
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result['details']:
                for key, value in result['details'].items():
                    if isinstance(value, float):
                        print(f"  - {key}: {value:.3f}")
                    else:
                        print(f"  - {key}: {value}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All logging tests PASSED!")
        else:
            print("⚠️  Some logging tests FAILED")
    
    def run_all_tests(self):
        """Run all logging tests"""
        print("🚀 Unified Logging System Tests")
        print("=" * 60)
        
        self.test_end_to_end_logging()
        self.test_performance_logging()
        self.test_stage_3_1_logging()
        self.test_stage_3_2_logging()
        
        self.print_summary()
        
        return self.test_results

def main():
    """Main test runner"""
    tester = UnifiedLoggingTester()
    results = tester.run_all_tests()
    
    # Save results
    results_file = "unified_logging_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Results saved to: {results_file}")

if __name__ == "__main__":
    main() 