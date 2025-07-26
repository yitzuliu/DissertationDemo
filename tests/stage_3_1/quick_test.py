#!/usr/bin/env python3
"""
階段3.1快速驗證測試

快速驗證服務間通信的基本功能
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path

def test_backend_basic():
    """基本後端服務測試"""
    print("🚀 階段3.1快速驗證測試")
    print("=" * 50)
    
    # 1. 測試後端服務啟動
    print("📋 1. 測試後端服務啟動...")
    
    backend_dir = Path(__file__).parent.parent.parent / "src" / "backend"
    
    try:
        # 啟動後端服務
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ 等待服務啟動...")
        time.sleep(8)
        
        if process.poll() is None:
            print("✅ 後端服務啟動成功")
            
            # 2. 測試健康檢查
            print("\n📋 2. 測試健康檢查端點...")
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ 健康檢查通過")
                    print(f"   響應: {response.json()}")
                else:
                    print(f"❌ 健康檢查失敗: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ 健康檢查連接失敗: {e}")
            
            # 3. 測試狀態端點
            print("\n📋 3. 測試狀態端點...")
            try:
                response = requests.get("http://127.0.0.1:8000/status", timeout=5)
                if response.status_code == 200:
                    print("✅ 狀態端點正常")
                    data = response.json()
                    print(f"   狀態: {data.get('status', 'Unknown')}")
                else:
                    print(f"❌ 狀態端點失敗: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ 狀態端點連接失敗: {e}")
            
            # 4. 測試State Tracker端點
            print("\n📋 4. 測試State Tracker端點...")
            try:
                response = requests.get("http://127.0.0.1:8000/api/v1/state", timeout=5)
                if response.status_code == 200:
                    print("✅ State Tracker端點正常")
                    data = response.json()
                    print(f"   當前步驟: {data.get('current_step', 'None')}")
                else:
                    print(f"❌ State Tracker端點失敗: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ State Tracker端點連接失敗: {e}")
            
            # 5. 測試VLM文字處理
            print("\n📋 5. 測試VLM文字處理...")
            try:
                test_data = {"vlm_text": "用戶正在準備咖啡器具，桌上有咖啡豆和磨豆機"}
                response = requests.post("http://127.0.0.1:8000/api/v1/state/process", 
                                       json=test_data, timeout=10)
                if response.status_code == 200:
                    print("✅ VLM文字處理成功")
                    data = response.json()
                    print(f"   處理結果: 步驟 {data.get('current_step', 'Unknown')}")
                else:
                    print(f"❌ VLM文字處理失敗: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ VLM文字處理連接失敗: {e}")
            
            # 6. 測試用戶查詢
            print("\n📋 6. 測試用戶查詢...")
            try:
                query_data = {"query": "我現在在第幾步？"}
                response = requests.post("http://127.0.0.1:8000/api/v1/state/query", 
                                       json=query_data, timeout=10)
                if response.status_code == 200:
                    print("✅ 用戶查詢處理成功")
                    data = response.json()
                    print(f"   查詢回應: {data.get('response', 'No response')[:100]}...")
                else:
                    print(f"❌ 用戶查詢處理失敗: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ 用戶查詢處理連接失敗: {e}")
            
        else:
            print("❌ 後端服務啟動失敗")
            stdout, stderr = process.communicate()
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
        
        # 清理進程
        if process.poll() is None:
            process.terminate()
            process.wait()
        
        print("\n" + "=" * 50)
        print("🎯 階段3.1快速驗證完成")
        print("如果上述測試大部分通過，說明服務間通信基本正常")
        print("可以繼續進行完整的階段3.1測試")
        
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")
        return False

if __name__ == "__main__":
    test_backend_basic()