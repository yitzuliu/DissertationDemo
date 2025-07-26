#!/usr/bin/env python3
"""
階段3.1：正確的服務啟動和通信測試流程

按照正確順序：
1. 啟動模型服務 (SmolVLM on port 8080)
2. 啟動後端服務 (Backend on port 8000) 
3. 測試服務間通信功能
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path

class Stage31ProperTester:
    def __init__(self):
        self.model_port = 8080
        self.backend_port = 8000
        self.model_process = None
        self.backend_process = None
        self.max_retries = 3
        
        # 虛擬環境設置
        self.base_dir = Path(__file__).parent.parent.parent
        self.venv_path = self.base_dir / "ai_vision_env"
        self.python_executable = self.venv_path / "bin" / "python"
        
        if not self.python_executable.exists():
            print(f"⚠️ 虛擬環境Python路徑不存在: {self.python_executable}")
            print(f"將使用系統Python: {sys.executable}")
            self.python_executable = sys.executable
        
    def kill_port(self, port):
        """強制關閉占用端口的進程"""
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], 
                capture_output=True, text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(["kill", "-9", pid])
                print(f"✅ 已強制關閉端口 {port} 的進程")
                time.sleep(2)
        except Exception as e:
            print(f"⚠️ 清理端口 {port} 時出錯: {e}")
    
    def start_model_service(self):
        """第一步：啟動模型服務 (run_smolvlm.py)"""
        print("🚀 第一步：啟動模型服務 (SmolVLM)")
        print("=" * 50)
        
        # 使用絕對路徑確保正確找到腳本
        model_script = self.base_dir / "src/models/smolvlm/run_smolvlm.py"
        if not model_script.exists():
            print(f"❌ 模型啟動腳本不存在: {model_script}")
            return False
        
        print(f"🐍 使用Python: {self.python_executable}")
        print(f"📄 模型腳本: {model_script}")
        
        for attempt in range(self.max_retries):
            print(f"📋 嘗試 {attempt + 1}/{self.max_retries} 啟動模型服務...")
            
            # 清理端口
            self.kill_port(self.model_port)
            
            try:
                # 設置環境變量，激活虛擬環境
                env = os.environ.copy()
                if self.venv_path.exists():
                    env["VIRTUAL_ENV"] = str(self.venv_path)
                    env["PATH"] = f"{self.venv_path / 'bin'}:{env.get('PATH', '')}"
                
                # 啟動模型服務
                self.model_process = subprocess.Popen(
                    [str(self.python_executable), str(model_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    cwd=str(model_script.parent)
                )
                
                # 等待啟動
                print("⏳ 等待模型服務啟動...")
                time.sleep(20)  # SmolVLM需要更長時間啟動
                
                # 檢查服務狀態
                if self.check_model_service():
                    print("✅ 模型服務啟動成功")
                    return True
                else:
                    print(f"❌ 嘗試 {attempt + 1} 失敗")
                    if self.model_process:
                        self.model_process.terminate()
                        
            except Exception as e:
                print(f"❌ 啟動模型服務時出錯: {e}")
        
        print("❌ 模型服務啟動失敗，已達最大重試次數")
        return False
    
    def check_model_service(self):
        """檢查模型服務是否正常運行"""
        try:
            # 檢查進程狀態
            if self.model_process and self.model_process.poll() is not None:
                print("❌ 模型進程已終止")
                return False
            
            # 檢查端口響應 - llama-server通常監聽在根路徑
            try:
                response = requests.get(f"http://localhost:{self.model_port}/v1/models", timeout=10)
                if response.status_code == 200:
                    print("✅ 模型服務 /v1/models 端點響應正常")
                    return True
            except Exception as e:
                print(f"⚠️ /v1/models 檢查失敗: {e}")
            
            # 備用檢查：嘗試根路徑
            try:
                response = requests.get(f"http://localhost:{self.model_port}/", timeout=5)
                if response.status_code in [200, 404]:  # 404也表示服務在運行
                    print("✅ 模型服務根路徑響應正常")
                    return True
            except Exception as e:
                print(f"⚠️ 根路徑檢查失敗: {e}")
            
            return False
        except Exception as e:
            print(f"❌ 檢查模型服務時出錯: {e}")
            return False
    
    def start_backend_service(self):
        """第二步：啟動後端服務 (main.py)"""
        print("\n🚀 第二步：啟動後端服務")
        print("=" * 50)
        
        # 使用絕對路徑確保正確找到腳本
        backend_script = self.base_dir / "src/backend/main.py"
        if not backend_script.exists():
            print(f"❌ 後端啟動腳本不存在: {backend_script}")
            return False
        
        print(f"🐍 使用Python: {self.python_executable}")
        print(f"📄 後端腳本: {backend_script}")
        
        for attempt in range(self.max_retries):
            print(f"📋 嘗試 {attempt + 1}/{self.max_retries} 啟動後端服務...")
            
            # 清理端口
            self.kill_port(self.backend_port)
            
            try:
                # 設置環境變量，激活虛擬環境
                env = os.environ.copy()
                if self.venv_path.exists():
                    env["VIRTUAL_ENV"] = str(self.venv_path)
                    env["PATH"] = f"{self.venv_path / 'bin'}:{env.get('PATH', '')}"
                    env["PYTHONPATH"] = str(self.base_dir / "src")
                
                # 啟動後端服務 - 使用uvicorn命令
                self.backend_process = subprocess.Popen(
                    [str(self.python_executable), "-m", "uvicorn", "main:app", 
                     "--host", "127.0.0.1", "--port", str(self.backend_port), "--reload"],
                    cwd=str(backend_script.parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env
                )
                
                # 等待啟動
                print("⏳ 等待後端服務啟動...")
                time.sleep(10)  # 給更多時間讓後端啟動
                
                # 檢查服務狀態
                if self.check_backend_service():
                    print("✅ 後端服務啟動成功")
                    return True
                else:
                    print(f"❌ 嘗試 {attempt + 1} 失敗")
                    if self.backend_process:
                        self.backend_process.terminate()
                        time.sleep(2)
                        
            except Exception as e:
                print(f"❌ 啟動後端服務時出錯: {e}")
        
        print("❌ 後端服務啟動失敗，已達最大重試次數")
        return False
    
    def check_backend_service(self):
        """檢查後端服務是否正常運行"""
        try:
            # 檢查進程狀態
            if self.backend_process and self.backend_process.poll() is not None:
                print("❌ 後端進程已終止")
                if self.backend_process.stderr:
                    stderr_output = self.backend_process.stderr.read()
                    if stderr_output:
                        print(f"❌ 後端錯誤信息: {stderr_output[:200]}...")
                return False
            
            # 檢查端口響應
            response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 後端健康檢查端點響應正常")
                return True
            else:
                print(f"❌ 後端健康檢查返回: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 檢查後端服務時出錯: {e}")
            return False
    
    def test_service_communication(self):
        """第三步：測試服務間通信功能"""
        print("\n🚀 第三步：測試服務間通信功能")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 0
        
        # 測試1：後端健康檢查
        total_tests += 1
        print("📋 測試1：後端健康檢查...")
        try:
            response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 後端健康檢查通過")
                tests_passed += 1
            else:
                print(f"❌ 後端健康檢查失敗: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ 後端健康檢查連接失敗: {e}")
        
        # 測試2：後端狀態端點
        total_tests += 1
        print("📋 測試2：後端狀態端點...")
        try:
            response = requests.get(f"http://localhost:{self.backend_port}/status", timeout=5)
            if response.status_code == 200:
                print("✅ 後端狀態端點正常")
                tests_passed += 1
            else:
                print(f"❌ 後端狀態端點失敗: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ 後端狀態端點連接失敗: {e}")
        
        # 測試3：模型服務通信（通過後端）
        total_tests += 1
        print("📋 測試3：模型服務通信...")
        try:
            test_data = {
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Hello, can you see this message?"}
                        ]
                    }
                ]
            }
            response = requests.post(
                f"http://localhost:{self.backend_port}/v1/chat/completions",
                json=test_data,
                timeout=30
            )
            if response.status_code == 200:
                print("✅ 模型服務通信正常")
                tests_passed += 1
            else:
                print(f"❌ 模型服務通信失敗: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ 模型服務通信連接失敗: {e}")
        
        # 測試4：State Tracker端點
        total_tests += 1
        print("📋 測試4：State Tracker端點...")
        try:
            response = requests.get(f"http://localhost:{self.backend_port}/api/v1/state", timeout=5)
            if response.status_code == 200:
                print("✅ State Tracker端點正常")
                tests_passed += 1
            else:
                print(f"❌ State Tracker端點失敗: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   錯誤詳情: {error_detail}")
                except:
                    print(f"   響應內容: {response.text[:200]}")
        except Exception as e:
            print(f"❌ State Tracker端點連接失敗: {e}")
        
        # 測試5：State Tracker VLM處理端點
        total_tests += 1
        print("📋 測試5：State Tracker VLM處理...")
        try:
            test_vlm_data = {
                "text": "用戶正在準備咖啡豆和研磨設備"
            }
            response = requests.post(
                f"http://localhost:{self.backend_port}/api/v1/state/process",
                json=test_vlm_data,
                timeout=10
            )
            if response.status_code == 200:
                print("✅ State Tracker VLM處理正常")
                tests_passed += 1
            else:
                print(f"❌ State Tracker VLM處理失敗: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   錯誤詳情: {error_detail}")
                except:
                    print(f"   響應內容: {response.text[:200]}")
        except Exception as e:
            print(f"❌ State Tracker VLM處理連接失敗: {e}")
        
        # 測試6：State Tracker 即時查詢
        total_tests += 1
        print("📋 測試6：State Tracker 即時查詢...")
        try:
            test_query_data = {
                "query": "我現在在哪一步？"
            }
            response = requests.post(
                f"http://localhost:{self.backend_port}/api/v1/state/query",
                json=test_query_data,
                timeout=5
            )
            if response.status_code == 200:
                print("✅ State Tracker 即時查詢正常")
                tests_passed += 1
            else:
                print(f"❌ State Tracker 即時查詢失敗: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   錯誤詳情: {error_detail}")
                except:
                    print(f"   響應內容: {response.text[:200]}")
        except Exception as e:
            print(f"❌ State Tracker 即時查詢連接失敗: {e}")
        
        # 顯示測試結果
        print(f"\n📊 測試結果摘要:")
        print(f"   通過測試: {tests_passed}/{total_tests}")
        print(f"   成功率: {(tests_passed/total_tests*100):.1f}%")
        
        return tests_passed == total_tests
    
    def cleanup(self):
        """清理進程"""
        print("\n🧹 清理進程...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.model_process:
            self.model_process.terminate()
            try:
                self.model_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.model_process.kill()
        
        print("✅ 清理完成")
    
    def run_full_test(self):
        """執行完整的階段3.1測試"""
        print("🎯 階段3.1：正確的服務啟動和通信測試")
        print("=" * 60)
        
        try:
            # 第一步：啟動模型服務
            if not self.start_model_service():
                print("❌ 階段3.1測試失敗：模型服務啟動失敗")
                return False
            
            # 第二步：啟動後端服務
            if not self.start_backend_service():
                print("❌ 階段3.1測試失敗：後端服務啟動失敗")
                return False
            
            # 第三步：測試服務間通信
            if self.test_service_communication():
                print("\n✅ 階段3.1測試成功完成！")
                print("🎯 所有服務正常運行，通信功能正常")
                return True
            else:
                print("\n⚠️ 階段3.1部分測試失敗")
                print("🔧 服務啟動成功，但通信功能有問題")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️ 測試被用戶中斷")
            return False
        finally:
            self.cleanup()

def main():
    tester = Stage31ProperTester()
    success = tester.run_full_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()