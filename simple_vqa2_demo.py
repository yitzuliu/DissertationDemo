#!/usr/bin/env python3
"""
VQA 2.0 簡單示例 - 20張圖像快速測試
演示如何使用VQA 2.0框架進行快速評估

使用方法:
    python simple_vqa2_demo.py
"""

import sys
import time
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def main():
    print("🚀 VQA 2.0 簡單示例 - 20張圖像快速測試")
    print("=" * 60)
    
    try:
        from testing.vqa2_tester import VQA2Tester
        print("✅ 成功導入VQA2Tester")
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        print("請確認VQA 2.0框架文件存在")
        return
    
    # 初始化測試器
    try:
        tester = VQA2Tester(data_dir="data/vqa2")
        print("✅ VQA2Tester 初始化成功")
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        return
    
    print("\n📊 準備測試數據...")
    print("- 將下載20個VQA 2.0問題")
    print("- 將下載對應的COCO圖像（優化模式）")
    print("- 預計下載時間：1-3分鐘（取決於網速）")
    
    start_time = time.time()
    
    try:
        # 運行小規模評估
        results = tester.run_evaluation(
            models_to_test=['smolvlm_instruct'],  # 修正模型名稱
            num_questions=20,
            save_results=True
        )
        
        # 顯示結果
        print("\n" + "="*60)
        print("📈 測試完成！結果摘要：")
        print("="*60)
        
        for model_name, model_results in results.items():
            if model_name == "test_metadata":
                continue
                
            accuracy = model_results.get("accuracy", 0)
            vqa_accuracy = model_results.get("average_vqa_accuracy", 0)
            correct = model_results.get("correct_answers", 0)
            total = model_results.get("total_questions", 0)
            avg_time = model_results.get("average_inference_time", 0)
            
            print(f"\n🤖 {model_name}:")
            print(f"   ✅ 正確答案：{correct}/{total}")
            print(f"   📊 簡單準確度：{accuracy:.1%}")
            print(f"   🎯 VQA準確度：{vqa_accuracy:.1%}")
            print(f"   ⏱️  平均推理時間：{avg_time:.2f}秒")
            
            # 表現評估
            if vqa_accuracy >= 0.6:
                assessment = "🏆 表現優秀"
            elif vqa_accuracy >= 0.4:
                assessment = "🎯 表現中等"
            else:
                assessment = "🔧 需要改進"
            print(f"   {assessment}")
        
        total_time = time.time() - start_time
        print(f"\n⏱️  總測試時間：{total_time:.1f}秒")
        
        print("\n💡 關於結果驗證：")
        print("1. VQA準確度使用官方評估協議，比簡單準確度更準確")
        print("2. 詳細結果保存在 results/ 目錄中")
        print("3. 可以查看每個問題的詳細評估信息")
        print("4. 模型回答會經過標準化處理後與標準答案比較")
        
        print("\n📁 結果文件位置：")
        print("- results/*.json - 完整結果數據")
        print("- results/*.txt - 可讀摘要")
        
        print("\n✅ 測試成功完成！")
        
    except Exception as e:
        print(f"\n❌ 測試失敗：{str(e)}")
        print("\n🔧 可能的解決方案：")
        print("1. 檢查網絡連接")
        print("2. 確認有足夠磁盤空間")
        print("3. 檢查模型文件是否完整")

if __name__ == "__main__":
    main()
