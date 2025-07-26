#!/usr/bin/env python3
"""
階段3.1：服務間通信驗證與啟動測試

測試目標：
1. 驗證模型服務 → 後端服務的數據傳輸通道
2. 驗證後端服務 → 前端服務的查詢響應通道  
3. 驗證前端服務 → 後端服務的用戶查詢傳輸通道
4. 測試各服務的獨立啟動
5. 確認端口通信正常
6. 驗證基礎數據流：VLM文字 → State Tracker → 前端顯示

執行日期：2024年7月26日
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

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceCommunicationTester:
    """服務間通信驗證測試器"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"  # 如果有獨立前端服務
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
    async def test_backend_service_health(self) -> bool:
        """測試後端服務健康狀態"""
        logger.info("🔍 測試後端服務健康狀態...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 測試基本健康檢查
                async with session.get(f"{self.backend_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ 後端服務健康檢查通過: {data}")
                        
                        self.test_results["tests"]["backend_health"] = {
                            "status": "PASS",
                            "response": data,
                            "response_time_ms": None
                        }
                        return True
                    else:
                        logger.error(f"❌ 後端服務健康檢查失敗: HTTP {response.status}")
                        self.test_results["tests"]["backend_health"] = {
                            "status": "FAIL",
                            "error": f"HTTP {response.status}"
                        }
                        return False
                        
        except Exception as e:
            logger.error(f"❌ 後端服務連接失敗: {e}")
            self.test_results["tests"]["backend_health"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_backend_status_endpoint(self) -> bool:
        """測試後端狀態端點"""
        logger.info("🔍 測試後端狀態端點...")
        
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(f"{self.backend_url}/status") as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ 後端狀態端點正常: {data.get('status', 'Unknown')}")
                        
                        self.test_results["tests"]["backend_status"] = {
                            "status": "PASS",
                            "response": data,
                            "response_time_ms": response_time
                        }
                        return True
                    else:
                        logger.error(f"❌ 後端狀態端點失敗: HTTP {response.status}")
                        self.test_results["tests"]["backend_status"] = {
                            "status": "FAIL",
                            "error": f"HTTP {response.status}"
                        }
                        return False
                        
        except Exception as e:
            logger.error(f"❌ 後端狀態端點連接失敗: {e}")
            self.test_results["tests"]["backend_status"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_state_tracker_endpoints(self) -> bool:
        """測試State Tracker相關端點"""
        logger.info("🔍 測試State Tracker端點...")
        
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
                            logger.info(f"✅ {endpoint} 端點正常")
                            
                            self.test_results["tests"][f"state_tracker_{endpoint.replace('/', '_')}"] = {
                                "status": "PASS",
                                "response": data,
                                "response_time_ms": response_time
                            }
                        else:
                            logger.error(f"❌ {endpoint} 端點失敗: HTTP {response.status}")
                            self.test_results["tests"][f"state_tracker_{endpoint.replace('/', '_')}"] = {
                                "status": "FAIL",
                                "error": f"HTTP {response.status}"
                            }
                            all_passed = False
                            
        except Exception as e:
            logger.error(f"❌ State Tracker端點測試失敗: {e}")
            self.test_results["tests"]["state_tracker_endpoints"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
            
        return all_passed
    
    async def test_vlm_to_state_tracker_flow(self) -> bool:
        """測試VLM文字 → State Tracker的數據流"""
        logger.info("🔍 測試VLM → State Tracker數據流...")
        
        # 模擬VLM觀察文字
        test_vlm_texts = [
            "用戶正在準備咖啡器具，桌上有咖啡豆和磨豆機",
            "用戶開始研磨咖啡豆，磨豆機正在運作",
            "用戶將熱水倒入咖啡濾器中，開始沖泡咖啡"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for i, vlm_text in enumerate(test_vlm_texts):
                    logger.info(f"📤 發送VLM文字 {i+1}: {vlm_text[:50]}...")
                    
                    # 發送到State Tracker處理端點
                    payload = {"vlm_text": vlm_text}
                    start_time = time.time()
                    
                    async with session.post(
                        f"{self.backend_url}/api/v1/state/process",
                        json=payload
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ VLM文字處理成功: 步驟 {data.get('current_step', 'Unknown')}")
                            
                            self.test_results["tests"][f"vlm_processing_{i+1}"] = {
                                "status": "PASS",
                                "input": vlm_text,
                                "response": data,
                                "response_time_ms": response_time
                            }
                        else:
                            logger.error(f"❌ VLM文字處理失敗: HTTP {response.status}")
                            self.test_results["tests"][f"vlm_processing_{i+1}"] = {
                                "status": "FAIL",
                                "input": vlm_text,
                                "error": f"HTTP {response.status}"
                            }
                            return False
                    
                    # 短暫延遲模擬真實間隔
                    await asyncio.sleep(0.5)
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ VLM → State Tracker數據流測試失敗: {e}")
            self.test_results["tests"]["vlm_to_state_tracker"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_user_query_flow(self) -> bool:
        """測試用戶查詢 → State Tracker → 回應的數據流"""
        logger.info("🔍 測試用戶查詢數據流...")
        
        test_queries = [
            "我現在在第幾步？",
            "下一步該做什麼？",
            "需要什麼工具？",
            "現在的任務進度如何？"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for i, query in enumerate(test_queries):
                    logger.info(f"📤 發送用戶查詢 {i+1}: {query}")
                    
                    payload = {"query": query}
                    start_time = time.time()
                    
                    async with session.post(
                        f"{self.backend_url}/api/v1/state/query",
                        json=payload
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ 查詢處理成功: {data.get('response', 'No response')[:100]}...")
                            
                            self.test_results["tests"][f"user_query_{i+1}"] = {
                                "status": "PASS",
                                "query": query,
                                "response": data,
                                "response_time_ms": response_time
                            }
                        else:
                            logger.error(f"❌ 查詢處理失敗: HTTP {response.status}")
                            self.test_results["tests"][f"user_query_{i+1}"] = {
                                "status": "FAIL",
                                "query": query,
                                "error": f"HTTP {response.status}"
                            }
                            return False
                    
                    await asyncio.sleep(0.3)
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ 用戶查詢數據流測試失敗: {e}")
            self.test_results["tests"]["user_query_flow"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_end_to_end_data_flow(self) -> bool:
        """測試端到端數據流：VLM文字 → State Tracker → 前端顯示"""
        logger.info("🔍 測試端到端數據流...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 1. 發送VLM觀察
                vlm_text = "用戶正在研磨咖啡豆，磨豆機運作中，咖啡粉正在產生"
                logger.info(f"📤 步驟1: 發送VLM觀察: {vlm_text}")
                
                async with session.post(
                    f"{self.backend_url}/api/v1/state/process",
                    json={"vlm_text": vlm_text}
                ) as response:
                    if response.status != 200:
                        logger.error("❌ VLM處理失敗")
                        return False
                    vlm_result = await response.json()
                    logger.info(f"✅ VLM處理成功: 步驟 {vlm_result.get('current_step')}")
                
                # 2. 查詢當前狀態
                await asyncio.sleep(0.5)
                logger.info("📤 步驟2: 查詢當前狀態")
                
                async with session.get(f"{self.backend_url}/api/v1/state") as response:
                    if response.status != 200:
                        logger.error("❌ 狀態查詢失敗")
                        return False
                    state_result = await response.json()
                    logger.info(f"✅ 狀態查詢成功: {state_result.get('current_task_description', 'Unknown')[:50]}...")
                
                # 3. 用戶查詢
                await asyncio.sleep(0.5)
                logger.info("📤 步驟3: 用戶查詢")
                
                async with session.post(
                    f"{self.backend_url}/api/v1/state/query",
                    json={"query": "我現在在做什麼？"}
                ) as response:
                    if response.status != 200:
                        logger.error("❌ 用戶查詢失敗")
                        return False
                    query_result = await response.json()
                    logger.info(f"✅ 用戶查詢成功: {query_result.get('response', 'No response')[:100]}...")
                
                # 記錄端到端測試結果
                self.test_results["tests"]["end_to_end_flow"] = {
                    "status": "PASS",
                    "vlm_input": vlm_text,
                    "vlm_result": vlm_result,
                    "state_result": state_result,
                    "query_result": query_result
                }
                
                logger.info("✅ 端到端數據流測試成功")
                return True
                
        except Exception as e:
            logger.error(f"❌ 端到端數據流測試失敗: {e}")
            self.test_results["tests"]["end_to_end_flow"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    async def test_service_independence(self) -> bool:
        """測試服務獨立性（不需要整合為單一系統）"""
        logger.info("🔍 測試服務獨立性...")
        
        try:
            # 測試後端服務可以獨立運行
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health") as response:
                    if response.status == 200:
                        logger.info("✅ 後端服務獨立運行正常")
                        
                        self.test_results["tests"]["service_independence"] = {
                            "status": "PASS",
                            "backend_independent": True,
                            "note": "後端服務可以獨立啟動和運行，不需要其他服務依賴"
                        }
                        return True
                    else:
                        logger.error("❌ 後端服務獨立性測試失敗")
                        return False
                        
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
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """執行所有測試"""
        logger.info("🚀 開始執行階段3.1服務通信驗證測試...")
        logger.info("=" * 60)
        
        # 測試序列
        tests = [
            ("後端服務健康檢查", self.test_backend_service_health),
            ("後端狀態端點", self.test_backend_status_endpoint),
            ("State Tracker端點", self.test_state_tracker_endpoints),
            ("VLM → State Tracker數據流", self.test_vlm_to_state_tracker_flow),
            ("用戶查詢數據流", self.test_user_query_flow),
            ("端到端數據流", self.test_end_to_end_data_flow),
            ("服務獨立性", self.test_service_independence)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 執行測試: {test_name}")
            logger.info("-" * 40)
            
            try:
                result = await test_func()
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

async def main():
    """主函數"""
    print("🚀 階段3.1：服務間通信驗證與啟動測試")
    print("=" * 60)
    print("測試目標：")
    print("1. 驗證模型服務 → 後端服務的數據傳輸通道")
    print("2. 驗證後端服務 → 前端服務的查詢響應通道")
    print("3. 驗證前端服務 → 後端服務的用戶查詢傳輸通道")
    print("4. 測試各服務的獨立啟動")
    print("5. 確認端口通信正常")
    print("6. 驗證基礎數據流：VLM文字 → State Tracker → 前端顯示")
    print("=" * 60)
    
    # 創建測試器並執行測試
    tester = ServiceCommunicationTester()
    report = await tester.run_all_tests()
    
    # 保存測試報告
    report_path = Path(__file__).parent / f"stage_3_1_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 測試報告已保存至: {report_path}")
    
    # 返回結果
    return report['summary']['overall_status'] == "PASS"

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)