#!/usr/bin/env python3
"""
快速模型切換腳本

使用方式:
python switch_model.py                    # 互動式選擇
python switch_model.py --model moondream2_optimized  # 直接切換
python switch_model.py --quick           # 切換到最快模型
python switch_model.py --best            # 切換到最佳模型
"""

import argparse
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

class ModelSwitcher:
    """模型切換器"""
    
    def __init__(self):
        self.models = {
            "1": {
                "name": "smolvlm2_500m_video_optimized",
                "description": "SmolVLM2 優化版 (最佳性能)",
                "performance": "66.0% 準確率, 6.61s 推理, 2.08GB 記憶體"
            },
            "2": {
                "name": "moondream2_optimized", 
                "description": "Moondream2 優化版 (最快速度)",
                "performance": "56.0% 準確率, 4.06s 推理, 0.10GB 記憶體"
            },
            "3": {
                "name": "phi3_vision_optimized",
                "description": "Phi3 Vision 優化版 (詳細分析)",
                "performance": "60.0% 準確率, 13.61s 推理, 1.53GB 記憶體"
            },
            "4": {
                "name": "smolvlm",
                "description": "SmolVLM 標準版",
                "performance": "64.0% 準確率, 5.98s 推理, 1.58GB 記憶體"
            },
            "5": {
                "name": "moondream2",
                "description": "Moondream2 標準版",
                "performance": "基礎性能版本"
            }
        }
    
    def show_models(self):
        """顯示可用模型"""
        print("🤖 可用的模型:")
        print("=" * 60)
        for key, model in self.models.items():
            print(f"{key}. {model['description']}")
            print(f"   性能: {model['performance']}")
            print()
    
    def interactive_select(self):
        """互動式模型選擇"""
        self.show_models()
        
        while True:
            try:
                choice = input("請選擇模型 (1-5) 或 'q' 退出: ").strip()
                
                if choice.lower() == 'q':
                    print("👋 退出模型切換")
                    return None
                
                if choice in self.models:
                    return self.models[choice]["name"]
                else:
                    print("❌ 無效選擇，請輸入 1-5 或 'q'")
                    
            except KeyboardInterrupt:
                print("\\n👋 退出模型切換")
                return None
    
    def switch_model(self, model_name):
        """切換到指定模型"""
        if not any(model["name"] == model_name for model in self.models.values()):
            print(f"❌ 未知模型: {model_name}")
            return False
        
        print(f"🔄 切換到模型: {model_name}")
        
        # 檢查是否有模型在運行
        self.check_and_stop_existing()
        
        # 啟動新模型
        try:
            print(f"🚀 啟動模型: {model_name}")
            cmd = [sys.executable, "src/models/model_launcher.py", "--model", model_name]
            
            # 啟動模型服務器
            process = subprocess.Popen(cmd, cwd=Path.cwd())
            
            print(f"✅ 模型 {model_name} 啟動中...")
            print("📋 提示:")
            print("  - 等待模型完全載入後再使用")
            print("  - 按 Ctrl+C 可停止模型")
            print("  - 模型服務地址: http://localhost:8080")
            
            # 等待用戶中斷
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\\n🛑 正在停止模型...")
                process.terminate()
                process.wait()
                print("✅ 模型已停止")
            
            return True
            
        except Exception as e:
            print(f"❌ 啟動模型失敗: {e}")
            return False
    
    def check_and_stop_existing(self):
        """檢查並停止現有模型"""
        try:
            # 檢查端口8080是否被占用
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8080))
            sock.close()
            
            if result == 0:
                print("⚠️ 檢測到端口8080被占用")
                response = input("是否要停止現有模型? (y/N): ").strip().lower()
                if response == 'y':
                    print("🛑 請手動停止現有模型 (在模型終端按 Ctrl+C)")
                    input("停止後按 Enter 繼續...")
                else:
                    print("❌ 取消切換")
                    return False
        except ImportError:
            print("⚠️ 無法檢查端口狀態，請確保沒有其他模型在運行")
        
        return True

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="AI Manual Assistant - 快速模型切換")
    parser.add_argument('--model', '-m', help='直接切換到指定模型')
    parser.add_argument('--quick', '-q', action='store_true', help='切換到最快模型 (moondream2_optimized)')
    parser.add_argument('--best', '-b', action='store_true', help='切換到最佳模型 (smolvlm2_500m_video_optimized)')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有可用模型')
    
    args = parser.parse_args()
    
    switcher = ModelSwitcher()
    
    if args.list:
        switcher.show_models()
        return
    
    if args.quick:
        model_name = "moondream2_optimized"
        print("⚡ 切換到最快模型")
    elif args.best:
        model_name = "smolvlm2_500m_video_optimized"
        print("🏆 切換到最佳模型")
    elif args.model:
        model_name = args.model
    else:
        # 互動式選擇
        model_name = switcher.interactive_select()
        if not model_name:
            return
    
    # 執行切換
    success = switcher.switch_model(model_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()