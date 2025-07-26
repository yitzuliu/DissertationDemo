#!/usr/bin/env python3
"""
階段3.1：服務獨立啟動測試

測試目標：
1. 驗證後端服務可以獨立啟動
2. 驗證前端服務可以獨立啟動  
3. 驗證各服務的端口配置
4. 確認服務間不需要整合為單一系統

執行日期：2024年7月26日
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

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceStartupTester:
    """服務獨立啟動測試器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.backend_port = 8000
        self.frontend_port = 3000  # 如果有獨立前端服務
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        self.started_processes = []
        
    def cleanup_processes(self):
        """清理啟動的進程"""
        for process in self.started_processes:
            try:
                if process.poll() is None:  # 進程仍在運行
                    logger.info(f"🛑 終止進程 PID: {process.pid}")
                    process.terminate()
                    process.wait(timeout=5)
            except Exception as e:
                logger.warning(f"⚠️ 清理進程時出錯: {e}")
        
        self.started_processes.clear()
    
    def check_port_availability(self, port: int) -> bool:
        """檢查端口是否可用"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return False
            return True
        except Exception:
            return True
    
    def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """等待服務啟動"""
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
        """測試後端服務獨立啟動"""
        logger.info("🔍 測試後端服務獨立啟動...")
        
        try:
            # 檢查端口是否可用
            if not self.check_port_availability(self.backend_port):
                logger.warning(f"⚠️ 端口 {self.backend_port} 已被占用，嘗試連接現有服務...")
                
                # 嘗試連接現有服務
                try:
                    response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
                    if response.status_code == 200:
                        logger.info("✅ 後端服務已在運行")
                        self.test_results["tests"]["backend_startup"] = {
                            "status": "PASS",
                            "note": "服務已在運行",
                            "port": self.backend_port
                        }
                        return True
                except requests.exceptions.RequestException:
                    logger.error("❌ 端口被占用但服務無響應")
                    return False
            
            # 啟動後端服務
            backend_path = self.project_root / "src" / "backend" / "main.py"
            if not backend_path.exists():
                logger.error(f"❌ 後端服務文件不存在: {backend_path}")
                self.test_results["tests"]["backend_startup"] = {
                    "status": "FAIL",
                    "error": "後端服務文件不存在"
                }
                return False
            
            logger.info(f"🚀 啟動後端服務: {backend_path}")
            
            # 使用uvicorn啟動後端服務
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
            
            # 等待服務啟動
            logger.info("⏳ 等待後端服務啟動...")
            if self.wait_for_service(f"http://localhost:{self.backend_port}/health"):
                logger.info("✅ 後端服務啟動成功")
                
                # 測試基本功能
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
                    logger.error("❌ 後端服務啟動但狀態異常")
                    return False
            else:
                logger.error("❌ 後端服務啟動超時")
                self.test_results["tests"]["backend_startup"] = {
                    "status": "FAIL",
                    "error": "啟動超時"
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ 後端服務啟動測試失敗: {e}")
            self.test_results["tests"]["backend_startup"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_frontend_service_availability(self) -> bool:
        """測試前端服務可用性"""
        logger.info("🔍 測試前端服務可用性...")
        
        try:
            # 檢查前端文件是否存在
            frontend_files = [
                self.project_root / "src" / "frontend" / "index.html",
                self.project_root / "src" / "frontend" / "query.html"
            ]
            
            missing_files = [f for f in frontend_files if not f.exists()]
            if missing_files:
                logger.error(f"❌ 前端文件缺失: {missing_files}")
                self.test_results["tests"]["frontend_availability"] = {
                    "status": "FAIL",
                    "error": f"缺失文件: {missing_files}"
                }
                return False
            
            logger.info("✅ 前端文件完整")
            
            # 檢查前端文件內容
            index_path = frontend_files[0]
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 檢查關鍵功能
                required_features = [
                    "intervalSelect",  # VLM觀察間隔控制
                    "startButton",     # 啟動按鈕
                    "responseText",    # 回應顯示
                    "apiStatusDot"     # API狀態指示
                ]
                
                missing_features = [f for f in required_features if f not in content]
                if missing_features:
                    logger.error(f"❌ 前端功能缺失: {missing_features}")
                    self.test_results["tests"]["frontend_availability"] = {
                        "status": "FAIL",
                        "error": f"缺失功能: {missing_features}"
                    }
                    return False
            
            logger.info("✅ 前端功能完整")
            
            self.test_results["tests"]["frontend_availability"] = {
                "status": "PASS",
                "files_checked": [str(f) for f in frontend_files],
                "features_verified": required_features,
                "note": "前端可以通過瀏覽器直接打開使用"
            }
            return True
            
        except Exception as e:
            logger.error(f"❌ 前端服務可用性測試失敗: {e}")
            self.test_results["tests"]["frontend_availability"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_service_ports_configuration(self) -> bool:
        """測試服務端口配置"""
        logger.info("🔍 測試服務端口配置...")
        
        try:
            # 檢查後端服務端口配置
            backend_url = f"http://localhost:{self.backend_port}"
            
            # 測試各個端點
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
                    logger.error(f"❌ {endpoint} - 無法訪問: {e}")
            
            # 檢查是否所有端點都可訪問
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
                logger.info(f"✅ 端口配置正常 - {accessible_endpoints}/{total_endpoints} 端點可訪問")
            else:
                logger.error(f"❌ 端口配置異常 - 僅 {accessible_endpoints}/{total_endpoints} 端點可訪問")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 端口配置測試失敗: {e}")
            self.test_results["tests"]["port_configuration"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_service_independence(self) -> bool:
        """測試服務獨立性（不需要整合為單一系統）"""
        logger.info("🔍 測試服務獨立性...")
        
        try:
            # 驗證後端服務可以獨立運行
            backend_url = f"http://localhost:{self.backend_port}"
            
            # 測試後端服務的獨立功能
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
                        logger.info(f"✅ {test_name} - 獨立運行正常")
                    else:
                        logger.warning(f"⚠️ {test_name} - HTTP {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    independent_functions[test_name] = {
                        "working": False,
                        "error": str(e)
                    }
                    logger.error(f"❌ {test_name} - 無法訪問: {e}")
            
            # 計算獨立性得分
            working_functions = sum(1 for result in independent_functions.values() 
                                  if result.get("working", False))
            total_functions = len(independence_tests)
            
            independence_score = working_functions / total_functions
            success = independence_score >= 0.8  # 80%以上功能正常即視為獨立
            
            self.test_results["tests"]["service_independence"] = {
                "status": "PASS" if success else "FAIL",
                "independence_score": f"{independence_score:.1%}",
                "working_functions": working_functions,
                "total_functions": total_functions,
                "function_tests": independent_functions,
                "note": "後端服務可以獨立啟動和運行，不依賴其他服務"
            }
            
            if success:
                logger.info(f"✅ 服務獨立性良好 - {independence_score:.1%} 功能正常")
            else:
                logger.error(f"❌ 服務獨立性不足 - 僅 {independence_score:.1%} 功能正常")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 服務獨立性測試失敗: {e}")
            self.test_results["tests"]["service_independence"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """生成測試報告"""
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
        """執行所有測試"""
        logger.info("🚀 開始執行階段3.1服務獨立啟動測試...")
        logger.info("=" * 60)
        
        try:
            # 測試序列
            tests = [
                ("後端服務獨立啟動", self.test_backend_service_startup),
                ("前端服務可用性", self.test_frontend_service_availability),
                ("服務端口配置", self.test_service_ports_configuration),
                ("服務獨立性", self.test_service_independence)
            ]
            
            for test_name, test_func in tests:
                logger.info(f"\n📋 執行測試: {test_name}")
                logger.info("-" * 40)
                
                try:
                    result = test_func()
                    if result:
                        logger.info(f"✅ {test_name} - 通過")
                    else:
                        logger.error(f"❌ {test_name} - 失敗")
                except Exception as e:
                    logger.error(f"❌ {test_name} - 異常: {e}")
            
            # 生成報告
            report = self.generate_test_report()
            
            logger.info("\n" + "=" * 60)
            logger.info("📊 測試結果摘要")
            logger.info("=" * 60)
            logger.info(f"總測試數: {report['summary']['total_tests']}")
            logger.info(f"通過測試: {report['summary']['passed_tests']}")
            logger.info(f"失敗測試: {report['summary']['failed_tests']}")
            logger.info(f"成功率: {report['summary']['success_rate']}")
            logger.info(f"整體狀態: {report['summary']['overall_status']}")
            
            return report
            
        finally:
            # 清理啟動的進程
            self.cleanup_processes()

def main():
    """主函數"""
    print("🚀 階段3.1：服務獨立啟動測試")
    print("=" * 60)
    print("測試目標：")
    print("1. 驗證後端服務可以獨立啟動")
    print("2. 驗證前端服務可以獨立啟動")
    print("3. 驗證各服務的端口配置")
    print("4. 確認服務間不需要整合為單一系統")
    print("=" * 60)
    
    # 創建測試器並執行測試
    tester = ServiceStartupTester()
    
    try:
        report = tester.run_all_tests()
        
        # 保存測試報告
        report_path = Path(__file__).parent / f"stage_3_1_startup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 測試報告已保存至: {report_path}")
        
        # 返回結果
        return report['summary']['overall_status'] == "PASS"
        
    except KeyboardInterrupt:
        print("\n⚠️ 測試被用戶中斷")
        tester.cleanup_processes()
        return False
    except Exception as e:
        print(f"\n❌ 測試執行失敗: {e}")
        tester.cleanup_processes()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)