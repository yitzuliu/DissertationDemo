#!/usr/bin/env python3
"""
簡化的後端服務啟動測試

用於快速驗證後端服務是否能正常啟動
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

def test_backend_startup():
    """測試後端服務啟動"""
    print("🚀 測試後端服務啟動...")
    
    # 設置工作目錄
    project_root = Path(__file__).parent.parent.parent
    backend_dir = project_root / "src" / "backend"
    
    print(f"📁 後端目錄: {backend_dir}")
    print(f"📁 工作目錄: {os.getcwd()}")
    
    # 檢查main.py是否存在
    main_py = backend_dir / "main.py"
    if not main_py.exists():
        print(f"❌ main.py不存在: {main_py}")
        return False
    
    print(f"✅ 找到main.py: {main_py}")
    
    # 嘗試導入測試
    try:
        print("🔍 測試Python導入...")
        
        # 添加路徑
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(backend_dir))
        
        # 嘗試導入
        os.chdir(backend_dir)
        
        # 測試基本導入
        import main
        print("✅ 成功導入main模塊")
        
        # 檢查app對象
        if hasattr(main, 'app'):
            print("✅ 找到FastAPI app對象")
        else:
            print("❌ 未找到FastAPI app對象")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 導入失敗: {e}")
        return False

def test_direct_uvicorn():
    """直接測試uvicorn啟動"""
    print("\n🚀 測試直接uvicorn啟動...")
    
    try:
        # 切換到backend目錄
        backend_dir = Path(__file__).parent.parent.parent / "src" / "backend"
        os.chdir(backend_dir)
        
        print(f"📁 當前目錄: {os.getcwd()}")
        
        # 啟動uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000",
            "--log-level", "info"
        ]
        
        print(f"🔧 執行命令: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待啟動
        print("⏳ 等待服務啟動...")
        time.sleep(10)
        
        # 檢查進程狀態
        if process.poll() is None:
            print("✅ 服務進程正在運行")
            
            # 測試連接
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ 健康檢查通過")
                    print(f"📄 響應: {response.json()}")
                    
                    # 終止進程
                    process.terminate()
                    process.wait()
                    return True
                else:
                    print(f"❌ 健康檢查失敗: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ 連接測試失敗: {e}")
        else:
            print("❌ 服務進程已退出")
            stdout, stderr = process.communicate()
            print(f"📄 stdout: {stdout}")
            print(f"📄 stderr: {stderr}")
        
        # 清理進程
        if process.poll() is None:
            process.terminate()
            process.wait()
        
        return False
        
    except Exception as e:
        print(f"❌ uvicorn啟動測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("🔍 階段3.1 - 後端服務啟動診斷")
    print("=" * 50)
    
    # 測試1: Python導入
    import_success = test_backend_startup()
    
    # 測試2: 直接uvicorn啟動
    if import_success:
        uvicorn_success = test_direct_uvicorn()
        
        if uvicorn_success:
            print("\n✅ 後端服務啟動測試成功")
            print("🎯 可以繼續執行階段3.1的完整測試")
            return True
        else:
            print("\n❌ uvicorn啟動失敗")
    else:
        print("\n❌ Python導入失敗")
    
    print("\n🔧 建議檢查:")
    print("1. 確認所有依賴已安裝")
    print("2. 檢查Python路徑配置")
    print("3. 驗證backend/utils模塊")
    print("4. 檢查state_tracker模塊")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)