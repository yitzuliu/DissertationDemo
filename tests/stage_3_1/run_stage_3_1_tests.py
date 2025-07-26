#!/usr/bin/env python3
"""
階段3.1：服務間通信驗證與啟動測試 - 主執行腳本

這個腳本會執行階段3.1的所有測試任務：
1. 服務獨立啟動測試
2. 服務間通信驗證測試
3. 生成綜合測試報告

執行日期：2024年7月26日
"""

import asyncio
import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加當前目錄到Python路徑
sys.path.append(str(Path(__file__).parent))

from test_service_startup import ServiceStartupTester
from test_service_communication import ServiceCommunicationTester

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Stage31TestRunner:
    """階段3.1測試執行器"""
    
    def __init__(self):
        self.test_results = {
            "stage": "3.1",
            "stage_name": "服務間通信驗證與啟動測試",
            "execution_date": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
    
    async def run_startup_tests(self) -> Dict[str, Any]:
        """執行服務啟動測試"""
        logger.info("🚀 執行服務啟動測試...")
        
        startup_tester = ServiceStartupTester()
        startup_results = startup_tester.run_all_tests()
        
        self.test_results["tests"]["startup_tests"] = startup_results
        return startup_results
    
    async def run_communication_tests(self) -> Dict[str, Any]:
        """執行服務通信測試"""
        logger.info("🔗 執行服務通信測試...")
        
        comm_tester = ServiceCommunicationTester()
        comm_results = await comm_tester.run_all_tests()
        
        self.test_results["tests"]["communication_tests"] = comm_results
        return comm_results
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成綜合測試報告"""
        logger.info("📊 生成綜合測試報告...")
        
        # 統計所有測試結果
        all_tests = {}
        
        # 合併啟動測試結果
        if "startup_tests" in self.test_results["tests"]:
            startup_tests = self.test_results["tests"]["startup_tests"].get("tests", {})
            for test_name, result in startup_tests.items():
                all_tests[f"startup_{test_name}"] = result
        
        # 合併通信測試結果
        if "communication_tests" in self.test_results["tests"]:
            comm_tests = self.test_results["tests"]["communication_tests"].get("tests", {})
            for test_name, result in comm_tests.items():
                all_tests[f"communication_{test_name}"] = result
        
        # 計算總體統計
        total_tests = len(all_tests)
        passed_tests = sum(1 for test in all_tests.values() if test.get("status") == "PASS")
        failed_tests = total_tests - passed_tests
        
        # 按類別統計
        startup_passed = sum(1 for name, test in all_tests.items() 
                           if name.startswith("startup_") and test.get("status") == "PASS")
        startup_total = sum(1 for name in all_tests.keys() if name.startswith("startup_"))
        
        comm_passed = sum(1 for name, test in all_tests.items() 
                         if name.startswith("communication_") and test.get("status") == "PASS")
        comm_total = sum(1 for name in all_tests.keys() if name.startswith("communication_"))
        
        # 生成摘要
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            "overall_status": "PASS" if passed_tests == total_tests else "FAIL",
            "categories": {
                "startup_tests": {
                    "passed": startup_passed,
                    "total": startup_total,
                    "success_rate": f"{(startup_passed/startup_total*100):.1f}%" if startup_total > 0 else "0%"
                },
                "communication_tests": {
                    "passed": comm_passed,
                    "total": comm_total,
                    "success_rate": f"{(comm_passed/comm_total*100):.1f}%" if comm_total > 0 else "0%"
                }
            }
        }
        
        # 生成階段3.1完成狀態
        stage_3_1_status = {
            "stage": "3.1",
            "task_name": "服務間通信驗證與啟動測試",
            "completion_status": "COMPLETED" if self.test_results["summary"]["overall_status"] == "PASS" else "FAILED",
            "completion_date": datetime.now().isoformat(),
            "test_summary": self.test_results["summary"],
            "key_achievements": self._generate_achievements(),
            "issues_found": self._generate_issues(all_tests),
            "next_steps": self._generate_next_steps()
        }
        
        self.test_results["stage_3_1_status"] = stage_3_1_status
        
        return self.test_results
    
    def _generate_achievements(self) -> list:
        """生成關鍵成就列表"""
        achievements = []
        
        # 檢查各項測試成就
        startup_tests = self.test_results["tests"].get("startup_tests", {}).get("tests", {})
        comm_tests = self.test_results["tests"].get("communication_tests", {}).get("tests", {})
        
        if startup_tests.get("backend_startup", {}).get("status") == "PASS":
            achievements.append("✅ 後端服務可以獨立啟動和運行")
        
        if startup_tests.get("frontend_availability", {}).get("status") == "PASS":
            achievements.append("✅ 前端服務文件完整且功能可用")
        
        if startup_tests.get("service_independence", {}).get("status") == "PASS":
            achievements.append("✅ 服務獨立性驗證通過，不需要整合為單一系統")
        
        if comm_tests.get("end_to_end_flow", {}).get("status") == "PASS":
            achievements.append("✅ 端到端數據流驗證成功：VLM文字 → State Tracker → 前端顯示")
        
        if comm_tests.get("vlm_processing_1", {}).get("status") == "PASS":
            achievements.append("✅ VLM → State Tracker 數據傳輸通道正常")
        
        if comm_tests.get("user_query_1", {}).get("status") == "PASS":
            achievements.append("✅ 前端 → 後端 → 前端 查詢響應通道正常")
        
        return achievements
    
    def _generate_issues(self, all_tests: Dict[str, Any]) -> list:
        """生成發現的問題列表"""
        issues = []
        
        for test_name, result in all_tests.items():
            if result.get("status") == "FAIL":
                error = result.get("error", "未知錯誤")
                issues.append(f"❌ {test_name}: {error}")
        
        return issues
    
    def _generate_next_steps(self) -> list:
        """生成下一步建議"""
        next_steps = []
        
        if self.test_results["summary"]["overall_status"] == "PASS":
            next_steps.extend([
                "🎯 階段3.1已完成，可以進入階段3.2：雙循環跨服務協調與穩定性",
                "📋 建議執行階段3.2測試：驗證潛意識循環和即時響應循環的跨服務協同",
                "🔄 可以開始測試VLM觀察間隔控制（2/3/5秒）的實際效果"
            ])
        else:
            next_steps.extend([
                "🔧 需要修復失敗的測試項目",
                "📝 檢查服務配置和端口設置",
                "🔄 重新執行測試直到所有項目通過"
            ])
        
        return next_steps
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """執行所有階段3.1測試"""
        logger.info("🚀 開始執行階段3.1：服務間通信驗證與啟動測試")
        logger.info("=" * 80)
        
        try:
            # 1. 執行服務啟動測試
            logger.info("\n📋 第一部分：服務獨立啟動測試")
            logger.info("-" * 50)
            await self.run_startup_tests()
            
            # 2. 執行服務通信測試
            logger.info("\n📋 第二部分：服務間通信驗證測試")
            logger.info("-" * 50)
            await self.run_communication_tests()
            
            # 3. 生成綜合報告
            logger.info("\n📋 第三部分：生成綜合測試報告")
            logger.info("-" * 50)
            comprehensive_report = self.generate_comprehensive_report()
            
            # 4. 顯示結果摘要
            self._display_final_summary()
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"❌ 階段3.1測試執行失敗: {e}")
            self.test_results["summary"] = {
                "overall_status": "FAIL",
                "error": str(e)
            }
            return self.test_results
    
    def _display_final_summary(self):
        """顯示最終摘要"""
        summary = self.test_results["summary"]
        
        logger.info("\n" + "=" * 80)
        logger.info("🎯 階段3.1：服務間通信驗證與啟動測試 - 最終結果")
        logger.info("=" * 80)
        
        logger.info(f"📊 總體統計:")
        logger.info(f"   總測試數: {summary['total_tests']}")
        logger.info(f"   通過測試: {summary['passed_tests']}")
        logger.info(f"   失敗測試: {summary['failed_tests']}")
        logger.info(f"   成功率: {summary['success_rate']}")
        logger.info(f"   整體狀態: {summary['overall_status']}")
        
        logger.info(f"\n📋 分類統計:")
        categories = summary.get("categories", {})
        for category, stats in categories.items():
            logger.info(f"   {category}: {stats['passed']}/{stats['total']} ({stats['success_rate']})")
        
        # 顯示關鍵成就
        achievements = self.test_results.get("stage_3_1_status", {}).get("key_achievements", [])
        if achievements:
            logger.info(f"\n🏆 關鍵成就:")
            for achievement in achievements:
                logger.info(f"   {achievement}")
        
        # 顯示發現的問題
        issues = self.test_results.get("stage_3_1_status", {}).get("issues_found", [])
        if issues:
            logger.info(f"\n⚠️ 發現的問題:")
            for issue in issues:
                logger.info(f"   {issue}")
        
        # 顯示下一步建議
        next_steps = self.test_results.get("stage_3_1_status", {}).get("next_steps", [])
        if next_steps:
            logger.info(f"\n🎯 下一步建議:")
            for step in next_steps:
                logger.info(f"   {step}")
        
        logger.info("=" * 80)

async def main():
    """主函數"""
    print("🚀 階段3.1：服務間通信驗證與啟動測試")
    print("=" * 80)
    print("測試範圍：")
    print("1. 驗證模型服務（VLM觀察間隔控制）→ 後端服務（State Tracker）的數據傳輸通道")
    print("2. 驗證後端服務（State Tracker + RAG）→ 前端服務的查詢響應通道")
    print("3. 驗證前端服務 → 後端服務的用戶查詢傳輸通道")
    print("4. 測試分別啟動：模型服務、後端服務、前端服務的獨立啟動")
    print("5. 確認各服務的端口通信正常（不需要整合為單一系統）")
    print("6. 驗證服務間的基礎數據流：VLM文字 → State Tracker → 前端顯示")
    print("=" * 80)
    
    # 創建測試執行器
    runner = Stage31TestRunner()
    
    try:
        # 執行所有測試
        comprehensive_report = await runner.run_all_tests()
        
        # 保存綜合測試報告
        report_path = Path(__file__).parent / f"STAGE_3_1_COMPREHENSIVE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 綜合測試報告已保存至: {report_path}")
        
        # 創建階段完成標記文件
        if comprehensive_report["summary"]["overall_status"] == "PASS":
            completion_file = Path(__file__).parent.parent.parent / "STAGE_3_1_COMPLETE.md"
            with open(completion_file, 'w', encoding='utf-8') as f:
                f.write(f"""# 階段3.1完成標記

## 階段信息
- **階段**: 3.1 服務間通信驗證與啟動測試
- **完成日期**: {datetime.now().strftime('%Y年%m月%d日')}
- **狀態**: ✅ 完成

## 測試結果摘要
- **總測試數**: {comprehensive_report["summary"]["total_tests"]}
- **通過測試**: {comprehensive_report["summary"]["passed_tests"]}
- **成功率**: {comprehensive_report["summary"]["success_rate"]}

## 關鍵成就
""")
                achievements = comprehensive_report.get("stage_3_1_status", {}).get("key_achievements", [])
                for achievement in achievements:
                    f.write(f"{achievement}\n")
                
                f.write(f"""
## 下一步
可以進入階段3.2：雙循環跨服務協調與穩定性測試

## 詳細報告
詳細測試報告請查看: {report_path.name}
""")
            
            print(f"✅ 階段3.1完成標記已創建: {completion_file}")
        
        # 返回結果
        return comprehensive_report["summary"]["overall_status"] == "PASS"
        
    except KeyboardInterrupt:
        print("\n⚠️ 測試被用戶中斷")
        return False
    except Exception as e:
        print(f"\n❌ 測試執行失敗: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)