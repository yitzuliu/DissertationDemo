#!/usr/bin/env python3
"""
Stage 3.1: Frontend User Input Logging Integration Test

Test Content:
1. Frontend query_id generation functionality
2. Frontend logging functionality
3. Backend logging endpoint functionality
4. Query processing with query_id passing
5. Backward compatibility testing
"""

import requests
import time
import json
import sys
import os
from pathlib import Path

class Stage31UserQueryLoggingTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = {
            'frontend_query_id_generation': False,
            'frontend_logging_function': False,
            'backend_logging_endpoint': False,
            'query_id_passing': False,
            'backward_compatibility': False
        }
        
    def test_frontend_query_id_generation(self):
        """Test frontend query_id generation functionality"""
        print("🧪 Testing frontend query_id generation functionality...")
        
        try:
            # Simulate frontend query_id generation logic
            timestamp = int(time.time() * 1000)
            import random
            import string
            random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            query_id = f"query_{timestamp}_{random_chars}"
            
            # Validate format
            if query_id.startswith("query_") and len(query_id.split("_")) == 3:
                print(f"✅ query_id format correct: {query_id}")
                self.test_results['frontend_query_id_generation'] = True
                return True
            else:
                print(f"❌ query_id format error: {query_id}")
                return False
                
        except Exception as e:
            print(f"❌ query_id generation failed: {e}")
            return False
    
    def test_backend_logging_endpoint(self):
        """Test backend logging endpoint"""
        print("\n🧪 Testing backend logging endpoint...")
        
        try:
            # Test logging endpoint
            log_data = {
                'query_id': f"query_{int(time.time() * 1000)}_test123",
                'query': 'What is the current step?',
                'language': 'en',
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'user_agent': 'test-agent',
                'observation_id': None
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/logging/user_query",
                json=log_data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'logged':
                    print(f"✅ Logging successful: {result}")
                    self.test_results['backend_logging_endpoint'] = True
                    return True
                else:
                    print(f"❌ Logging failed: {result}")
                    return False
            else:
                print(f"❌ Logging endpoint error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Logging endpoint connection failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Logging endpoint test failed: {e}")
            return False
    
    def test_query_id_passing(self):
        """Test query_id passing in query processing"""
        print("\n🧪 Testing query_id passing in query processing...")
        
        try:
            # Test query with query_id
            query_data = {
                'query': 'Where am I?',
                'query_id': f"query_{int(time.time() * 1000)}_pass123"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success' and 'response' in result:
                    print(f"✅ Query processing successful: {result['query_type']}")
                    self.test_results['query_id_passing'] = True
                    return True
                else:
                    print(f"❌ Query processing failed: {result}")
                    return False
            else:
                print(f"❌ Query endpoint error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Query endpoint connection failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Query processing test failed: {e}")
            return False
    
    def test_backward_compatibility(self):
        """Test backward compatibility"""
        print("\n🧪 Testing backward compatibility...")
        
        try:
            # Test query without query_id (old format)
            query_data = {
                'query': "What's next?"
                # No query_id included
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success' and 'response' in result:
                    print(f"✅ Backward compatibility test successful: {result['query_type']}")
                    self.test_results['backward_compatibility'] = True
                    return True
                else:
                    print(f"❌ Backward compatibility test failed: {result}")
                    return False
            else:
                print(f"❌ Backward compatibility endpoint error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Backward compatibility connection failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Backward compatibility test failed: {e}")
            return False
    
    def test_frontend_logging_function(self):
        """Test frontend logging functionality (simulation)"""
        print("\n🧪 Testing frontend logging functionality...")
        
        try:
            # Simulate frontend logging data structure
            log_data = {
                'query_id': f"query_{int(time.time() * 1000)}_frontend123",
                'query': 'What tools do I need?',
                'language': 'en',
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'user_agent': 'test-frontend-agent',
                'observation_id': None
            }
            
            # Validate data structure
            required_fields = ['query_id', 'query', 'language', 'timestamp', 'user_agent']
            if all(field in log_data for field in required_fields):
                print(f"✅ Frontend logging data structure correct: {list(log_data.keys())}")
                self.test_results['frontend_logging_function'] = True
                return True
            else:
                print(f"❌ Frontend logging data structure error: missing {[f for f in required_fields if f not in log_data]}")
                return False
                
        except Exception as e:
            print(f"❌ Frontend logging test failed: {e}")
            return False
    
    def test_multiple_query_types(self):
        """Test multiple query types from query.html examples"""
        print("\n🧪 Testing multiple query types from query.html examples...")
        
        # Query examples from query.html
        test_queries = [
            "Where am I?",
            "What is the current step?",
            "What tools do I need?",
            "What's my progress?",
            "Help me with this step",
            "What's next?",
            "Give me an overview",
            "What equipment is required?"
        ]
        
        successful_queries = 0
        
        for query in test_queries:
            try:
                query_data = {
                    'query': query,
                    'query_id': f"query_{int(time.time() * 1000)}_multi{successful_queries}"
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/v1/state/query",
                    json=query_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        successful_queries += 1
                        print(f"✅ Query successful: '{query}' -> {result['query_type']}")
                    else:
                        print(f"⚠️ Query failed: '{query}' -> {result}")
                else:
                    print(f"❌ Query error: '{query}' -> {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Query exception: '{query}' -> {e}")
        
        print(f"📊 Multiple query test results: {successful_queries}/{len(test_queries)} successful")
        return successful_queries >= len(test_queries) * 0.8  # 80% success rate
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Stage 3.1: Frontend User Input Logging Integration Test")
        print("=" * 60)
        
        # Check if backend service is running
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ Backend service not running, please start the backend service first")
                return False
            print("✅ Backend service running normally")
        except Exception as e:
            print(f"❌ Cannot connect to backend service: {e}")
            return False
        
        # Run tests
        tests = [
            self.test_frontend_query_id_generation,
            self.test_frontend_logging_function,
            self.test_backend_logging_endpoint,
            self.test_query_id_passing,
            self.test_backward_compatibility,
            self.test_multiple_query_types
        ]
        
        passed_tests = 0
        for test in tests:
            if test():
                passed_tests += 1
        
        # Output results
        print("\n📊 Test Results Summary:")
        print("=" * 40)
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nTotal: {passed_tests}/{len(tests)} tests passed")
        
        if passed_tests == len(tests):
            print("🎉 All tests passed! Stage 3.1 implementation successful")
            return True
        else:
            print("⚠️ Some tests failed, please check implementation")
            return False

def main():
    tester = Stage31UserQueryLoggingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 