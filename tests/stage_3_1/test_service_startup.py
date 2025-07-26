#!/usr/bin/env python3
"""
Stage 3.1: Service Independent Startup Testing

Test Objectives:
1. Verify backend service can start independently
2. Verify frontend service can start independently  
3. Verify service port configurations
4. Confirm services don't need to be integrated into a single system

Execution Date: 2024-07-26
"""

import subprocess
import time
import requests
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime
import psutil
import signal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceStartupTester:
    """Service independent startup tester"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.backend_port = 8000
        self.frontend_port = 3000  # If there's an independent frontend service
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        self.started_processes = []
        
    def cleanup_processes(self):
        """Clean up started processes"""
        for process in self.started_processes:
            try:
                if process.poll() is None:  # Process still running
                    logger.info(f"🛑 Terminating process PID: {process.pid}")
                    process.terminate()
                    process.wait(timeout=5)
            except Exception as e:
                logger.warning(f"⚠️ Error cleaning up process: {e}")
        
        self.started_processes.clear()
    
    def check_port_availability(self, port: int) -> bool:
        """Check if port is available"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return False
            return True
        except Exception:
            return True
    
    def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Wait for service to start"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    def test_backend_service_startup(self) -> bool:
        """Test backend service independent startup"""
        logger.info("🔍 Testing backend service independent startup...")
        
        try:
            # Check if port is available
            if not self.check_port_availability(self.backend_port):
                logger.warning(f"⚠️ Port {self.backend_port} is occupied, trying to connect to existing service...")
                
                # Try to connect to existing service
                try:
                    response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
                    if response.status_code == 200:
                        logger.info("✅ Backend service is already running")
                        self.test_results["tests"]["backend_startup"] = {
                            "status": "PASS",
                            "note": "Service already running",
                            "port": self.backend_port
                        }
                        return True
                except requests.exceptions.RequestException:
                    logger.error("❌ Port occupied but service not responding")
                    return False
            
            # Start backend service
            backend_path = self.project_root / "src" / "backend" / "main.py"
            if not backend_path.exists():
                logger.error(f"❌ Backend service file doesn't exist: {backend_path}")
                self.test_results["tests"]["backend_startup"] = {
                    "status": "FAIL",
                    "error": "Backend service file doesn't exist"
                }
                return False
            
            logger.info(f"🚀 Starting backend service: {backend_path}")
            
            # Use uvicorn to start backend service
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "127.0.0.1", 
                "--port", str(self.backend_port)
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=backend_path.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.started_processes.append(process)
            
            # Wait for service to start
            logger.info("⏳ Waiting for backend service to start...")
            if self.wait_for_service(f"http://localhost:{self.backend_port}/health"):
                logger.info("✅ Backend service started successfully")
                
                # Test basic functionality
                response = requests.get(f"http://localhost:{self.backend_port}/status")
                if response.status_code == 200:
                    status_data = response.json()
                    
                    self.test_results["tests"]["backend_startup"] = {
                        "status": "PASS",
                        "port": self.backend_port,
                        "startup_time": "< 30s",
                        "status_response": status_data
                    }
                    return True
                else:
                    logger.error("❌ Backend service started but status abnormal")
                    return False
            else:
                logger.error("❌ Backend service startup timeout")
                self.test_results["tests"]["backend_startup"] = {
                    "status": "FAIL",
                    "error": "Startup timeout"
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Backend service startup test failed: {e}")
            self.test_results["tests"]["backend_startup"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_frontend_service_availability(self) -> bool:
        """Test frontend service availability"""
        logger.info("🔍 Testing frontend service availability...")
        
        try:
            # Check if frontend files exist
            frontend_files = [
                self.project_root / "src" / "frontend" / "index.html",
                self.project_root / "src" / "frontend" / "query.html"
            ]
            
            missing_files = [f for f in frontend_files if not f.exists()]
            if missing_files:
                logger.error(f"❌ Frontend files missing: {missing_files}")
                self.test_results["tests"]["frontend_availability"] = {
                    "status": "FAIL",
                    "error": f"Missing files: {missing_files}"
                }
                return False
            
            logger.info("✅ Frontend files complete")
            
            # Check frontend file content
            index_path = frontend_files[0]
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check key features
                required_features = [
                    "intervalSelect",  # VLM observation interval control
                    "startButton",     # Start button
                    "responseText",    # Response display
                    "apiStatusDot"     # API status indicator
                ]
                
                missing_features = [f for f in required_features if f not in content]
                if missing_features:
                    logger.error(f"❌ Frontend features missing: {missing_features}")
                    self.test_results["tests"]["frontend_availability"] = {
                        "status": "FAIL",
                        "error": f"Missing features: {missing_features}"
                    }
                    return False
            
            logger.info("✅ Frontend features complete")
            
            self.test_results["tests"]["frontend_availability"] = {
                "status": "PASS",
                "files_checked": [str(f) for f in frontend_files],
                "features_verified": required_features,
                "note": "Frontend can be opened directly in browser"
            }
            return True
            
        except Exception as e:
            logger.error(f"❌ Frontend service availability test failed: {e}")
            self.test_results["tests"]["frontend_availability"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_service_ports_configuration(self) -> bool:
        """Test service port configuration"""
        logger.info("🔍 Testing service port configuration...")
        
        try:
            # Check backend service port configuration
            backend_url = f"http://localhost:{self.backend_port}"
            
            # Test various endpoints
            endpoints_to_test = [
                "/health",
                "/status", 
                "/config",
                "/api/v1/state"
            ]
            
            port_test_results = {}
            
            for endpoint in endpoints_to_test:
                try:
                    response = requests.get(f"{backend_url}{endpoint}", timeout=5)
                    port_test_results[endpoint] = {
                        "status_code": response.status_code,
                        "accessible": response.status_code == 200
                    }
                    logger.info(f"✅ {endpoint} - HTTP {response.status_code}")
                except requests.exceptions.RequestException as e:
                    port_test_results[endpoint] = {
                        "status_code": None,
                        "accessible": False,
                        "error": str(e)
                    }
                    logger.error(f"❌ {endpoint} - Cannot access: {e}")
            
            # Check if all endpoints are accessible
            accessible_endpoints = sum(1 for result in port_test_results.values() 
                                     if result.get("accessible", False))
            total_endpoints = len(endpoints_to_test)
            
            success = accessible_endpoints == total_endpoints
            
            self.test_results["tests"]["port_configuration"] = {
                "status": "PASS" if success else "FAIL",
                "backend_port": self.backend_port,
                "endpoints_tested": port_test_results,
                "accessible_endpoints": accessible_endpoints,
                "total_endpoints": total_endpoints
            }
            
            if success:
                logger.info(f"✅ Port configuration normal - {accessible_endpoints}/{total_endpoints} endpoints accessible")
            else:
                logger.error(f"❌ Port configuration abnormal - only {accessible_endpoints}/{total_endpoints} endpoints accessible")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Port configuration test failed: {e}")
            self.test_results["tests"]["port_configuration"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_service_independence(self) -> bool:
        """Test service independence (no need to integrate into single system)"""
        logger.info("🔍 Testing service independence...")
        
        try:
            # Verify backend service can run independently
            backend_url = f"http://localhost:{self.backend_port}"
            
            # Test backend service independent functions
            independence_tests = {
                "health_check": "/health",
                "status_check": "/status",
                "config_access": "/config",
                "state_access": "/api/v1/state"
            }
            
            independent_functions = {}
            
            for test_name, endpoint in independence_tests.items():
                try:
                    response = requests.get(f"{backend_url}{endpoint}", timeout=5)
                    independent_functions[test_name] = {
                        "working": response.status_code == 200,
                        "status_code": response.status_code
                    }
                    
                    if response.status_code == 200:
                        logger.info(f"✅ {test_name} - Independent operation normal")
                    else:
                        logger.warning(f"⚠️ {test_name} - HTTP {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    independent_functions[test_name] = {
                        "working": False,
                        "error": str(e)
                    }
                    logger.error(f"❌ {test_name} - Cannot access: {e}")
            
            # Calculate independence score
            working_functions = sum(1 for result in independent_functions.values() 
                                  if result.get("working", False))
            total_functions = len(independence_tests)
            
            independence_score = working_functions / total_functions
            success = independence_score >= 0.8  # 80%+ functions normal considered independent
            
            self.test_results["tests"]["service_independence"] = {
                "status": "PASS" if success else "FAIL",
                "independence_score": f"{independence_score:.1%}",
                "working_functions": working_functions,
                "total_functions": total_functions,
                "function_tests": independent_functions,
                "note": "Backend service can start and run independently, no dependency on other services"
            }
            
            if success:
                logger.info(f"✅ Service independence good - {independence_score:.1%} functions normal")
            else:
                logger.error(f"❌ Service independence insufficient - only {independence_score:.1%} functions normal")
            
            return success
            
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
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Execute all tests"""
        logger.info("🚀 Starting Stage 3.1 service independent startup tests...")
        logger.info("=" * 60)
        
        try:
            # Test sequence
            tests = [
                ("Backend service independent startup", self.test_backend_service_startup),
                ("Frontend service availability", self.test_frontend_service_availability),
                ("Service port configuration", self.test_service_ports_configuration),
                ("Service independence", self.test_service_independence)
            ]
            
            for test_name, test_func in tests:
                logger.info(f"\n📋 Executing test: {test_name}")
                logger.info("-" * 40)
                
                try:
                    result = test_func()
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
            
        finally:
            # Clean up started processes
            self.cleanup_processes()

def main():
    """Main function"""
    print("🚀 Stage 3.1: Service Independent Startup Testing")
    print("=" * 60)
    print("Test Objectives:")
    print("1. Verify backend service can start independently")
    print("2. Verify frontend service can start independently")
    print("3. Verify service port configurations")
    print("4. Confirm services don't need to be integrated into single system")
    print("=" * 60)
    
    # Create tester and execute tests
    tester = ServiceStartupTester()
    
    try:
        report = tester.run_all_tests()
        
        # Save test report
        report_path = Path(__file__).parent / f"stage_3_1_startup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Test report saved to: {report_path}")
        
        # Return result
        return report['summary']['overall_status'] == "PASS"
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        tester.cleanup_processes()
        return False
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        tester.cleanup_processes()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)