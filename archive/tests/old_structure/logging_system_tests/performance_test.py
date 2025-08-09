#!/usr/bin/env python3
"""
Performance Test for Stage 3.1 Logging System

Test the performance impact of logging functionality
"""

import requests
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class LoggingPerformanceTester:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.results = {
            'logging_endpoint': [],
            'query_with_logging': [],
            'query_without_logging': []
        }
    
    def test_logging_endpoint_performance(self, iterations=100):
        """Test logging endpoint performance"""
        print(f"🧪 Testing logging endpoint performance ({iterations} iterations)...")
        
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
                
                end_time = time.time()
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code == 200:
                    self.results['logging_endpoint'].append(duration)
                else:
                    print(f"⚠️ Logging endpoint failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Logging endpoint error: {e}")
    
    def test_query_with_logging_performance(self, iterations=100):
        """Test query processing with logging performance"""
        print(f"🧪 Testing query with logging performance ({iterations} iterations)...")
        
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
                
                end_time = time.time()
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code == 200:
                    self.results['query_with_logging'].append(duration)
                else:
                    print(f"⚠️ Query with logging failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Query with logging error: {e}")
    
    def test_query_without_logging_performance(self, iterations=100):
        """Test query processing without logging performance (baseline)"""
        print(f"🧪 Testing query without logging performance ({iterations} iterations)...")
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{self.backend_url}/api/v1/state/query",
                    json={
                        'query': f'Performance test query {i}'
                        # No query_id - backward compatibility
                    },
                    timeout=10
                )
                
                end_time = time.time()
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code == 200:
                    self.results['query_without_logging'].append(duration)
                else:
                    print(f"⚠️ Query without logging failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Query without logging error: {e}")
    
    def run_concurrent_test(self, concurrent_users=10, queries_per_user=10):
        """Test concurrent user performance"""
        print(f"🧪 Testing concurrent performance ({concurrent_users} users, {queries_per_user} queries each)...")
        
        def user_workload(user_id):
            user_results = []
            for i in range(queries_per_user):
                start_time = time.time()
                
                try:
                    response = requests.post(
                        f"{self.backend_url}/api/v1/state/query",
                        json={
                            'query': f'Concurrent test query {user_id}_{i}',
                            'query_id': f"concurrent_{user_id}_{i}_{int(time.time() * 1000)}"
                        },
                        timeout=10
                    )
                    
                    end_time = time.time()
                    duration = (end_time - start_time) * 1000
                    
                    if response.status_code == 200:
                        user_results.append(duration)
                        
                except Exception as e:
                    print(f"❌ Concurrent test error (user {user_id}): {e}")
            
            return user_results
        
        all_results = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_workload, i) for i in range(concurrent_users)]
            
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        self.results['concurrent_test'] = all_results
        print(f"✅ Concurrent test completed: {len(all_results)} successful queries")
    
    def analyze_results(self):
        """Analyze and display performance results"""
        print("\n📊 Performance Analysis Results:")
        print("=" * 50)
        
        for test_name, durations in self.results.items():
            if not durations:
                print(f"❌ {test_name}: No data")
                continue
                
            avg_duration = statistics.mean(durations)
            median_duration = statistics.median(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            std_dev = statistics.stdev(durations) if len(durations) > 1 else 0
            
            print(f"\n📈 {test_name.upper()}:")
            print(f"   Count: {len(durations)}")
            print(f"   Average: {avg_duration:.2f}ms")
            print(f"   Median: {median_duration:.2f}ms")
            print(f"   Min: {min_duration:.2f}ms")
            print(f"   Max: {max_duration:.2f}ms")
            print(f"   Std Dev: {std_dev:.2f}ms")
        
        # Compare with/without logging
        if self.results['query_with_logging'] and self.results['query_without_logging']:
            with_logging_avg = statistics.mean(self.results['query_with_logging'])
            without_logging_avg = statistics.mean(self.results['query_without_logging'])
            overhead = ((with_logging_avg - without_logging_avg) / without_logging_avg) * 100
            
            print(f"\n🔍 LOGGING OVERHEAD ANALYSIS:")
            print(f"   Query without logging: {without_logging_avg:.2f}ms")
            print(f"   Query with logging: {with_logging_avg:.2f}ms")
            print(f"   Overhead: {overhead:.2f}%")
            
            if overhead < 5:
                print("   ✅ Performance impact: Minimal (< 5%)")
            elif overhead < 10:
                print("   ⚠️ Performance impact: Acceptable (< 10%)")
            else:
                print("   ❌ Performance impact: High (> 10%)")
    
    def run_all_tests(self):
        """Run all performance tests"""
        print("🚀 Stage 3.1 Performance Test")
        print("=" * 40)
        
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
        
        # Run tests
        self.test_logging_endpoint_performance(50)
        self.test_query_with_logging_performance(50)
        self.test_query_without_logging_performance(50)
        self.run_concurrent_test(5, 10)  # 5 users, 10 queries each
        
        # Analyze results
        self.analyze_results()
        
        return True

def main():
    tester = LoggingPerformanceTester()
    success = tester.run_all_tests()
    if success:
        print("\n🎉 Performance test completed successfully!")
    else:
        print("\n❌ Performance test failed!")

if __name__ == "__main__":
    main() 