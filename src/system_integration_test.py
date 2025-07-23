#!/usr/bin/env python3
"""
AI Manual Assistant - 系統整合測試

這個腳本測試整個系統的集成，包括：
- 後端服務器
- 模型配置
- 模型啟動器
- API 端點
- 前端配置

使用方式:
python src/system_integration_test.py
python src/system_integration_test.py --quick  # 快速測試
"""

import argparse
import sys
import os
import time
import requests
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

class SystemIntegrationTester:
    """系統整合測試器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
    
    def log_test(self, test_name: str, status: str, message: str = "", details: Dict = None):
        """記錄測試結果"""
        self.results["tests"][test_name] = {
            "status": status,
            "message": message,
            "details": details or {}
        }
        
        self.results["summary"]["total"] += 1
        if status == "PASS":
            self.results["summary"]["passed"] += 1
            print(f"✅ {test_name}: {message}")
        elif status == "FAIL":
            self.results["summary"]["failed"] += 1
            print(f"❌ {test_name}: {message}")
        elif status == "WARN":
            self.results["summary"]["warnings"] += 1
            print(f"⚠️ {test_name}: {message}")
    
    def test_project_structure(self):
        """測試專案結構"""
        print("🔍 測試專案結構...")
        
        required_dirs = [
            "src/backend",
            "src/frontend", 
            "src/models",
            "src/config",
            "src/testing",
            "logs"
        ]
        
        required_files = [
            "src/backend/main.py",
            "src/config/app_config.json",
            "src/models/model_launcher.py",
            "requirements.txt"
        ]
        
        # 檢查目錄
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.log_test("project_structure_dirs", "FAIL", 
                         f"缺少目錄: {', '.join(missing_dirs)}")
        else:
            self.log_test("project_structure_dirs", "PASS", "所有必需目錄存在")
        
        # 檢查文件
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test("project_structure_files", "FAIL",
                         f"缺少文件: {', '.join(missing_files)}")
        else:
            self.log_test("project_structure_files", "PASS", "所有必需文件存在")
    
    def test_configuration_system(self):
        """測試配置系統"""
        print("🔍 測試配置系統...")
        
        try:
            # 測試配置驗證器
            result = subprocess.run(
                [sys.executable, "src/config/validate_model_configs.py"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_test("config_validation", "PASS", "配置驗證通過")
            else:
                self.log_test("config_validation", "WARN", 
                             f"配置驗證有警告: {result.stdout[-200:]}")
            
        except Exception as e:
            self.log_test("config_validation", "FAIL", f"配置驗證失敗: {e}")
        
        # 測試主配置文件
        try:
            config_path = self.project_root / "src/config/app_config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            required_keys = ["active_model", "server", "frontend"]
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                self.log_test("app_config", "FAIL", 
                             f"主配置缺少字段: {', '.join(missing_keys)}")
            else:
                self.log_test("app_config", "PASS", 
                             f"主配置正常，活躍模型: {config['active_model']}")
                
        except Exception as e:
            self.log_test("app_config", "FAIL", f"主配置讀取失敗: {e}")
    
    def test_backend_system(self):
        """測試後端系統"""
        print("🔍 測試後端系統...")
        
        try:
            # 測試後端導入
            sys.path.append(str(self.project_root / "src/backend"))
            import main
            
            self.log_test("backend_import", "PASS", "後端模組導入成功")
            
            # 測試 FastAPI 應用創建
            app = main.app
            routes = [route.path for route in app.routes if hasattr(route, 'path')]
            expected_routes = ['/', '/health', '/config', '/status', '/v1/chat/completions']
            
            missing_routes = [route for route in expected_routes if route not in routes]
            if missing_routes:
                self.log_test("backend_routes", "FAIL",
                             f"缺少路由: {', '.join(missing_routes)}")
            else:
                self.log_test("backend_routes", "PASS", 
                             f"所有路由已註冊 ({len(routes)} 個)")
            
            # 測試配置管理器
            active_model = main.ACTIVE_MODEL
            model_server_url = main.MODEL_SERVER_URL
            
            self.log_test("backend_config", "PASS",
                         f"後端配置正常，活躍模型: {active_model}, 服務器: {model_server_url}")
            
        except Exception as e:
            self.log_test("backend_system", "FAIL", f"後端系統測試失敗: {e}")
    
    def test_model_launcher(self):
        """測試模型啟動器"""
        print("🔍 測試模型啟動器...")
        
        try:
            # 測試模型列表
            result = subprocess.run(
                [sys.executable, "src/models/model_launcher.py", "--list"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 計算可用模型數量
                output_lines = result.stdout.split('\n')
                model_count = len([line for line in output_lines if line.strip().startswith('✅')])
                self.log_test("model_launcher_list", "PASS", 
                             f"模型啟動器正常，發現 {model_count} 個可用模型")
            else:
                self.log_test("model_launcher_list", "FAIL", 
                             f"模型列表失敗: {result.stderr}")
            
            # 測試模型狀態檢查
            result = subprocess.run(
                [sys.executable, "src/models/model_launcher.py", 
                 "--status", "smolvlm2_500m_video_optimized"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_test("model_status_check", "PASS", "模型狀態檢查正常")
            else:
                self.log_test("model_status_check", "WARN", 
                             f"模型狀態檢查有問題: {result.stderr}")
                
        except Exception as e:
            self.log_test("model_launcher", "FAIL", f"模型啟動器測試失敗: {e}")
    
    def test_dependencies(self):
        """測試依賴"""
        print("🔍 測試系統依賴...")
        
        required_packages = {
            "fastapi": "FastAPI",
            "uvicorn": "Uvicorn", 
            "torch": "PyTorch",
            "transformers": "Transformers",
            "PIL": "Pillow",
            "flask": "Flask",
            "httpx": "HTTPX",
            "pydantic": "Pydantic"
        }
        
        missing_packages = []
        available_packages = []
        
        for package, name in required_packages.items():
            try:
                __import__(package)
                available_packages.append(name)
            except ImportError:
                missing_packages.append(name)
        
        if missing_packages:
            self.log_test("dependencies", "FAIL",
                         f"缺少依賴: {', '.join(missing_packages)}")
        else:
            self.log_test("dependencies", "PASS",
                         f"所有依賴已安裝 ({len(available_packages)} 個)")
        
        # 檢查可選依賴
        optional_packages = {
            "mlx_vlm": "MLX-VLM (Apple Silicon 優化)",
            "cv2": "OpenCV (圖像處理)",
            "chromadb": "ChromaDB (RAG 支援)"
        }
        
        available_optional = []
        for package, name in optional_packages.items():
            try:
                __import__(package)
                available_optional.append(name)
            except ImportError:
                pass
        
        if available_optional:
            self.log_test("optional_dependencies", "PASS",
                         f"可選依賴: {', '.join(available_optional)}")
        else:
            self.log_test("optional_dependencies", "WARN", "沒有安裝可選依賴")
    
    def test_frontend_structure(self):
        """測試前端結構"""
        print("🔍 測試前端結構...")
        
        frontend_files = [
            "src/frontend/index.html",
            "src/frontend/css/main.css",
            "src/frontend/js/main.js"
        ]
        
        existing_files = []
        missing_files = []
        
        for file_path in frontend_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test("frontend_structure", "WARN",
                         f"前端文件缺失: {', '.join(missing_files)}")
        else:
            self.log_test("frontend_structure", "PASS",
                         f"前端結構完整 ({len(existing_files)} 個文件)")
    
    def test_testing_framework(self):
        """測試測試框架"""
        print("🔍 測試測試框架...")
        
        testing_files = [
            "src/testing/vqa/vqa_framework.py",
            "src/testing/vqa/vqa_test.py",
            "src/testing/vlm/vlm_tester.py"
        ]
        
        existing_files = []
        for file_path in testing_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
        
        if len(existing_files) == len(testing_files):
            self.log_test("testing_framework", "PASS", "測試框架完整")
        else:
            self.log_test("testing_framework", "WARN", 
                         f"測試框架不完整 ({len(existing_files)}/{len(testing_files)})")
    
    def run_quick_test(self):
        """運行快速測試"""
        print("🚀 運行快速系統測試...")
        print("=" * 60)
        
        self.test_project_structure()
        self.test_configuration_system()
        self.test_dependencies()
        self.test_model_launcher()
    
    def run_full_test(self):
        """運行完整測試"""
        print("🚀 運行完整系統整合測試...")
        print("=" * 60)
        
        self.test_project_structure()
        self.test_configuration_system()
        self.test_backend_system()
        self.test_model_launcher()
        self.test_dependencies()
        self.test_frontend_structure()
        self.test_testing_framework()
    
    def print_summary(self):
        """打印測試摘要"""
        print("\n" + "=" * 60)
        print("📊 系統整合測試摘要")
        print("=" * 60)
        
        summary = self.results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        warnings = summary["warnings"]
        
        print(f"總測試數: {total}")
        print(f"✅ 通過: {passed}")
        print(f"❌ 失敗: {failed}")
        print(f"⚠️ 警告: {warnings}")
        
        if failed == 0:
            if warnings == 0:
                print("\n🎉 所有測試通過！系統準備就緒！")
                status = "EXCELLENT"
            else:
                print("\n✅ 系統基本正常，有一些警告需要注意")
                status = "GOOD"
        else:
            print(f"\n❌ 有 {failed} 個測試失敗，需要修復")
            status = "NEEDS_ATTENTION"
        
        # 提供建議
        print("\n📋 建議:")
        if failed > 0:
            print("1. 修復失敗的測試項目")
            print("2. 檢查錯誤日誌")
            print("3. 重新運行測試")
        elif warnings > 0:
            print("1. 檢查警告項目")
            print("2. 安裝可選依賴以獲得更好性能")
            print("3. 完善缺失的組件")
        else:
            print("1. 系統已準備就緒，可以開始使用")
            print("2. 運行: python src/models/model_launcher.py --list")
            print("3. 啟動推薦模型開始體驗")
        
        return status
    
    def save_results(self):
        """保存測試結果"""
        results_dir = self.project_root / "logs"
        results_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"system_integration_test_{timestamp}.json"
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"\n📄 測試結果已保存: {results_file}")
        except Exception as e:
            print(f"\n⚠️ 無法保存測試結果: {e}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="AI Manual Assistant - 系統整合測試",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--quick', '-q', action='store_true', 
                       help='運行快速測試 (跳過詳細檢查)')
    parser.add_argument('--save', '-s', action='store_true',
                       help='保存測試結果到文件')
    
    args = parser.parse_args()
    
    tester = SystemIntegrationTester()
    
    try:
        if args.quick:
            tester.run_quick_test()
        else:
            tester.run_full_test()
        
        status = tester.print_summary()
        
        if args.save:
            tester.save_results()
        
        # 根據測試結果設置退出碼
        if status == "NEEDS_ATTENTION":
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 測試被用戶中斷")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()