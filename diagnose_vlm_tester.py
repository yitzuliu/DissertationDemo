#!/usr/bin/env python3
"""
診斷腳本：分析 vlm_tester.py 重複執行的問題
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

def analyze_test_results():
    """分析測試結果文件"""
    print("🔍 分析測試結果...")
    
    results_dir = Path("src/testing/results")
    if not results_dir.exists():
        print("❌ 結果目錄不存在")
        return
    
    # 找到所有測試結果文件
    result_files = list(results_dir.glob("test_results_*.json"))
    result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"📊 找到 {len(result_files)} 個結果文件")
    
    for i, file_path in enumerate(result_files[:5]):  # 只檢查最近5個
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = data.get("test_timestamp", "未知")
            total_time = data.get("total_test_time", 0)
            models_tested = len(data.get("models", {}))
            
            print(f"  {i+1}. {file_path.name}")
            print(f"     時間戳: {timestamp}")
            print(f"     總測試時間: {total_time:.2f} 秒")
            print(f"     測試模型數: {models_tested}")
            
            # 檢查是否有異常
            if models_tested == 0:
                print("     ⚠️ 警告: 沒有測試任何模型")
            
            if total_time > 500:  # 超過8分鐘
                print("     ⚠️ 警告: 測試時間異常長")
            
            print()
            
        except Exception as e:
            print(f"  ❌ 無法讀取 {file_path.name}: {e}")

def check_llava_responses():
    """檢查 LLaVA 回應是否異常"""
    print("🔍 檢查 LLaVA 回應...")
    
    results_file = Path("src/testing/results/test_results_20250728_162034.json")
    if not results_file.exists():
        print("❌ 測試結果文件不存在")
        return
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        llava_data = data.get("models", {}).get("LLaVA-v1.6-Mistral-7B-MLX", {})
        if not llava_data:
            print("❌ 沒有找到 LLaVA 測試數據")
            return
        
        images = llava_data.get("images", {})
        responses = []
        
        for image_name, image_data in images.items():
            response = image_data.get("response", "")
            responses.append((image_name, response))
            print(f"📷 {image_name}:")
            print(f"   回應: {response[:100]}...")
            print()
        
        # 檢查是否所有回應都相同
        if len(set(r[1] for r in responses)) == 1:
            print("⚠️ 警告: 所有 LLaVA 回應都相同，可能存在狀態污染問題")
        else:
            print("✅ LLaVA 回應正常，每張圖片都有不同回應")
            
    except Exception as e:
        print(f"❌ 分析 LLaVA 回應時出錯: {e}")

def check_running_processes():
    """檢查是否有相關進程在運行"""
    print("🔍 檢查運行中的進程...")
    
    try:
        import psutil
        
        # 檢查 Python 進程
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('vlm_tester' in arg for arg in cmdline):
                        python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if python_processes:
            print(f"⚠️ 找到 {len(python_processes)} 個相關 Python 進程:")
            for proc in python_processes:
                print(f"   PID: {proc['pid']}, 命令: {' '.join(proc['cmdline'])}")
        else:
            print("✅ 沒有找到相關的運行中進程")
        
        # 檢查端口 8080
        connections = psutil.net_connections()
        port_8080_used = any(conn.laddr.port == 8080 for conn in connections if conn.laddr)
        
        if port_8080_used:
            print("⚠️ 端口 8080 正在被使用 (SmolVLM 服務器可能在運行)")
        else:
            print("✅ 端口 8080 未被使用")
            
    except ImportError:
        print("❌ 需要 psutil 來檢查進程")
    except Exception as e:
        print(f"❌ 檢查進程時出錯: {e}")

def main():
    """主函數"""
    print("🚀 VLM Tester 診斷工具")
    print("=" * 50)
    
    analyze_test_results()
    print("-" * 30)
    check_llava_responses()
    print("-" * 30)
    check_running_processes()
    
    print("\n📋 診斷總結:")
    print("1. 檢查測試結果文件的時間戳，看是否有重複執行")
    print("2. LLaVA 回應相同可能是狀態污染，已修正重載邏輯")
    print("3. 如果有多個 vlm_tester 進程，可能是之前的測試沒有正常結束")
    print("4. SmolVLM 服務器可能會在後台持續運行")

if __name__ == "__main__":
    main()