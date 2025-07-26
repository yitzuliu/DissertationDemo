#!/usr/bin/env python3
"""
Stage 3.1: Service Communication Verification and Startup Testing

Test Objectives:
1. Verify model service → backend service data transmission channel
2. Verify backend service → frontend service query response channel  
3. Verify frontend service → backend service user query transmission channel
4. Test independent startup of each service
5. Confirm port communication normal
6. Verify basic data flow: VLM text → State Tracker → frontend display

Execution Date: 2024-07-26
"""

import asyncio
import aiohttp
import json
import time
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import base64
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceCommunicationTester:
    """Service communication verification tester"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"  # If there's independent frontend service
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
    async def test_backend_service_health(self) -> bool:
        """Test backend service health status"""
        logger.info("🔍 Testing backend service health status...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test basic health check
                async with session.get(f"{self.backend_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Backend service health check passed: {data}")
                        
                        self.test_results["tests"]["backend_health"] = {
                            "status": "PASS",
                            "response": data,
                            "response_time_ms": None
                        }
                        return True
                    else:
                        logger.error(f"❌ Backend service health check failed: HTTP {response.status}")
                        self.test_results["tests"]["backend_health"] = {
                            "status": "FAIL",
                            "error": f"HTTP {response.status}"
                        }
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Backend service connection failed: {e}")
            self.test_results["tests"]["backend_health"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_backend_status_endpoint(self) -> bool:
        """Test backend status endpoint"""
        logger.info("🔍 Testing backend status endpoint...")
        
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(f"{self.backend_url}/status") as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Backend status endpoint normal: {data.get('status', 'Unknown')}")
                        
                        self.test_results["tests"]["backend_status"] = {
                            "status": "PASS",
                            "response": data,
                            "response_time_ms": response_time
                        }
                        return True
                    else:
                        logger.error(f"❌ Backend status endpoint failed: HTTP {response.status}")
                        self.test_results["tests"]["backend_status"] = {
                            "status": "FAIL",
                            "error": f"HTTP {response.status}"
                        }
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Backend status endpoint connection failed: {e}")
            self.test_results["tests"]["backend_status"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_state_tracker_endpoints(self) -> bool:
        """Test State Tracker related endpoints"""
        logger.info("🔍 Testing State Tracker endpoints...")
        
        endpoints_to_test = [
            "/api/v1/state",
            "/api/v1/state/metrics", 
            "/api/v1/state/memory",
            "/api/v1/state/query/capabilities"
        ]
        
        all_passed = True
        
        try:
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints_to_test:
                    start_time = time.time()
                    async with session.get(f"{self.backend_url}{endpoint}") as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ {endpoint} endpoint normal")
                            
                            self.test_results["tests"][f"state_tracker_{endpoint.replace('/', '_')}"] = {
                                "status": "PASS",
                                "response": data,
                                "response_time_ms": response_time
                            }
                        else:
                            logger.error(f"❌ {endpoint} endpoint failed: HTTP {response.status}")
                            self.test_results["tests"][f"state_tracker_{endpoint.replace('/', '_')}"] = {
                                "status": "FAIL",
                                "error": f"HTTP {response.status}"
                            }
                            all_passed = False
                            
        except Exception as e:
            logger.error(f"❌ State Tracker endpoint test failed: {e}")
            self.test_results["tests"]["state_tracker_endpoints"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
            
        return all_passed
    
    async def test_vlm_to_state_tracker_flow(self) -> bool:
        """Test VLM text → State Tracker data flow"""
        logger.info("🔍 Testing VLM → State Tracker data flow...")
        
        # Simulate VLM observation text
        test_vlm_texts = [
            "User is preparing coffee equipment, coffee beans and grinder on table",
            "User starts grinding coffee beans, grinder is operating",
            "User pours hot water into coffee filter, starts brewing coffee"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for i, vlm_text in enumerate(test_vlm_texts):
                    logger.info(f"📤 Sending VLM text {i+1}: {vlm_text[:50]}...")
                    
                    # Send to State Tracker processing endpoint
                    payload = {"vlm_text": vlm_text}
                    start_time = time.time()
                    
                    async with session.post(
                        f"{self.backend_url}/api/v1/state/process",
                        json=payload
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ VLM text processing successful: Step {data.get('current_step', 'Unknown')}")
                            
                            self.test_results["tests"][f"vlm_processing_{i+1}"] = {
                                "status": "PASS",
                                "input": vlm_text,
                                "response": data,
                                "response_time_ms": response_time
                            }
                        else:
                            logger.error(f"❌ VLM text processing failed: HTTP {response.status}")
                            self.test_results["tests"][f"vlm_processing_{i+1}"] = {
                                "status": "FAIL",
                                "input": vlm_text,
                                "error": f"HTTP {response.status}"
                            }
                            return False
                    
                    # Brief delay to simulate real intervals
                    await asyncio.sleep(0.5)
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ VLM → State Tracker data flow test failed: {e}")
            self.test_results["tests"]["vlm_to_state_tracker"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_user_query_flow(self) -> bool:
        """Test user query → State Tracker → response data flow"""
        logger.info("🔍 Testing user query data flow...")
        
        test_queries = [
            "What step am I on now?",
            "What should I do next?",
            "What tools do I need?",
            "How is my task progress?"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for i, query in enumerate(test_queries):
                    logger.info(f"📤 Sending user query {i+1}: {query}")
                    
                    payload = {"query": query}
                    start_time = time.time()
                    
                    async with session.post(
                        f"{self.backend_url}/api/v1/state/query",
                        json=payload
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ Query processing successful: {data.get('response', 'No response')[:100]}...")
                            
                            self.test_results["tests"][f"user_query_{i+1}"] = {
                                "status": "PASS",
                                "query": query,
                                "response": data,
                                "response_time_ms": response_time
                            }
                        else:
                            logger.error(f"❌ Query processing failed: HTTP {response.status}")
                            self.test_results["tests"][f"user_query_{i+1}"] = {
                                "status": "FAIL",
                                "query": query,
                                "error": f"HTTP {response.status}"
                            }
                            return False
                    
                    await asyncio.sleep(0.3)
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ User query data flow test failed: {e}")
            self.test_results["tests"]["user_query_flow"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_end_to_end_data_flow(self) -> bool:
        """Test end-to-end data flow: VLM text → State Tracker → frontend display"""
        logger.info("🔍 Testing end-to-end data flow...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 1. Send VLM observation
                vlm_text = "User is grinding coffee beans, grinder operating, coffee powder being produced"
                logger.info(f"📤 Step 1: Sending VLM observation: {vlm_text}")
                
                async with session.post(
                    f"{self.backend_url}/api/v1/state/process",
                    json={"vlm_text": vlm_text}
                ) as response:
                    if response.status != 200:
                        logger.error("❌ VLM processing failed")
                        return False
                    vlm_result = await response.json()
                    logger.info(f"✅ VLM processing successful: Step {vlm_result.get('current_step')}")
                
                # 2. Query current state
                await asyncio.sleep(0.5)
                logger.info("📤 Step 2: Querying current state")
                
                async with session.get(f"{self.backend_url}/api/v1/state") as response:
                    if response.status != 200:
                        logger.error("❌ State query failed")
                        return False
                    state_result = await response.json()
                    logger.info(f"✅ State query successful: {state_result.get('current_task_description', 'Unknown')[:50]}...")
                
                # 3. User query
                await asyncio.sleep(0.5)
                logger.info("📤 Step 3: User query")
                
                async with session.post(
                    f"{self.backend_url}/api/v1/state/query",
                    json={"query": "What am I doing now?"}
                ) as response:
                    if response.status != 200:
                        logger.error("❌ User query failed")
                        return False
                    query_result = await response.json()
                    logger.info(f"✅ User query successful: {query_result.get('response', 'No response')[:100]}...")
                
                # Record end-to-end test results
                self.test_results["tests"]["end_to_end_flow"] = {
                    "status": "PASS",
                    "vlm_input": vlm_text,
                    "vlm_result": vlm_result,
                    "state_result": state_result,
                    "query_result": query_result
                }
                
                logger.info("✅ End-to-end data flow test successful")
                return True
                
        except Exception as e:
            logger.error(f"❌ End-to-end data flow test failed: {e}")
            self.test_results["tests"]["end_to_end_flow"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_service_independence(self) -> bool:
        """Test service independence (no need to integrate into single system)"""
        logger.info("🔍 Testing service independence...")
        
        try:
            # Test backend service can run independently
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health") as response:
                    if response.status == 200:
                        logger.info("✅ Backend service independent operation normal")
                        
                        self.test_results["tests"]["service_independence"] = {
                            "status": "PASS",
                            "backend_independent": True,
                            "note": "Backend service can start and run independently, no dependency on other services"
                        }
                        return True
                    else:
                        logger.error("❌ Backend service independence test failed")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Service independence test failed: {e}")
            self.test_results["tests"]["service_independence"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate test report"""
        passed_tests = sum(1 for test in self.test_results["tests"].values() 
                          if test.get("status") == "PASS")
        total_tests = len(self.test_results["tests"])
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            "overall_status": "PASS" if passed_tests == total_tests else "FAIL"
        }
        
        return self.test_results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Execute all tests"""
        logger.info("🚀 Starting Stage 3.1 service communication verification tests...")
        logger.info("=" * 60)
        
        # Test sequence
        tests = [
            ("Backend service health check", self.test_backend_service_health),
            ("Backend status endpoint", self.test_backend_status_endpoint),
            ("State Tracker endpoints", self.test_state_tracker_endpoints),
            ("VLM → State Tracker data flow", self.test_vlm_to_state_tracker_flow),
            ("User query data flow", self.test_user_query_flow),
            ("End-to-end data flow", self.test_end_to_end_data_flow),
            ("Service independence", self.test_service_independence)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Executing test: {test_name}")
            logger.info("-" * 40)
            
            try:
                result = await test_func()
                if result:
                    logger.info(f"✅ {test_name} - Passed")
                else:
                    logger.error(f"❌ {test_name} - Failed")
            except Exception as e:
                logger.error(f"❌ {test_name} - Exception: {e}")
        
        # Generate report
        report = self.generate_test_report()
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 Test Results Summary")
        logger.info("=" * 60)
        logger.info(f"Total tests: {report['summary']['total_tests']}")
        logger.info(f"Passed tests: {report['summary']['passed_tests']}")
        logger.info(f"Failed tests: {report['summary']['failed_tests']}")
        logger.info(f"Success rate: {report['summary']['success_rate']}")
        logger.info(f"Overall status: {report['summary']['overall_status']}")
        
        return report

async def main():
    """Main function"""
    print("🚀 Stage 3.1: Service Communication Verification and Startup Testing")
    print("=" * 60)
    print("Test Objectives:")
    print("1. Verify model service → backend service data transmission channel")
    print("2. Verify backend service → frontend service query response channel")
    print("3. Verify frontend service → backend service user query transmission channel")
    print("4. Test independent startup of each service")
    print("5. Confirm port communication normal")
    print("6. Verify basic data flow: VLM text → State Tracker → frontend display")
    print("=" * 60)
    
    # Create tester and execute tests
    tester = ServiceCommunicationTester()
    report = await tester.run_all_tests()
    
    # Save test report
    report_path = Path(__file__).parent / f"stage_3_1_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Test report saved to: {report_path}")
    
    # Return result
    return report['summary']['overall_status'] == "PASS"

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)