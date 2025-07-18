#!/usr/bin/env python3
"""
VQA 2.0 快速測試腳本 - 簡化版本
支持小批量圖像下載和詳細結果分析

使用方法:
    python quick_vqa2_test.py                    # 使用默認設置（20題）
    python quick_vqa2_test.py --num_questions 20 # 指定問題數量
    python quick_vqa2_test.py --explanation      # 先顯示結果格式說明
    
Author: AI Assistant
Date: 2025-01-27
"""

import argparse
import sys
import time
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def main():
    parser = argparse.ArgumentParser(description='VQA 2.0 快速評估')
    
    # 基本選項
    parser.add_argument('--num_questions', type=int, default=20,
                       help='測試問題數量（默認: 20）')
    parser.add_argument('--models', nargs='+', 
                       default=['SmolVLM-Instruct'],
                       help='測試模型（默認: SmolVLM-Instruct）')
    
    # 下載選項
    parser.add_argument('--force_download', action='store_true',
                       help='強制重新下載圖像')
    parser.add_argument('--fallback_images', action='store_true',
                       help='COCO下載失敗時生成替代圖像')
    
    # 輸出選項
    parser.add_argument('--output_dir', default='results',
                       help='結果輸出目錄')
    
    # 測試選項
    parser.add_argument('--explanation', action='store_true',
                       help='測試前顯示結果格式說明')
    
    args = parser.parse_args()
    
    # 顯示結果格式說明
    if args.explanation:
        show_result_explanation()
        print("\n" + "="*60)
        try:
            input("按Enter鍵繼續測試，或Ctrl+C退出...")
        except KeyboardInterrupt:
            print("\n退出測試")
            return 0
    
    print("🚀 啟動VQA 2.0快速測試")
    print(f"📊 測試問題數：{args.num_questions}")
    print(f"🤖 測試模型：{', '.join(args.models)}")
    
    if args.num_questions <= 50:
        print("⚡ 使用優化下載模式（小批量圖像）")
    else:
        print("📦 使用完整數據集下載")
    
    # 導入並初始化VQA2Tester
    try:
        from testing.vqa2_tester import VQA2Tester
        
        tester = VQA2Tester(
            data_dir="data/vqa2"
        )
        print("✅ VQA2Tester 初始化成功")
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        print("請確認VQA 2.0框架已正確安裝")
        return 1
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        return 1
    
    start_time = time.time()
    
    try:
        # 運行評估
        print("\n📝 開始VQA 2.0評估...")
        results = tester.run_evaluation(
            models_to_test=args.models,
            num_questions=args.num_questions,
            save_results=True
        )
        
        # 顯示結果摘要
        print_results_summary(results, time.time() - start_time, args.output_dir)
        
    except KeyboardInterrupt:
        print("\n⚠️  測試被用戶中斷")
        return 1
    except Exception as e:
        print(f"\n❌ 測試失敗：{str(e)}")
        print_troubleshooting_tips()
        return 1
    
    return 0

def show_result_explanation():
    """顯示VQA 2.0結果格式說明"""
    print("🔍 VQA 2.0 測試結果格式說明")
    print("=" * 60)
    
    print("\n📊 您將獲得的結果包括：")
    print("1. 整體統計：準確度、VQA準確度、推理時間")
    print("2. 詳細評估：每個問題的模型回答和正確性")
    print("3. 錯誤分析：錯誤類型分布和改進建議")
    
    print("\n🎯 VQA準確度計算方法：")
    print("- 使用官方VQA 2.0評估協議")
    print("- 公式：min(相同答案的標註者數 / 3, 1.0)")
    print("- 比簡單準確度更準確，因為考慮了標註者一致性")
    
    print("\n📈 結果驗證方法：")
    print("- VQA準確度 ≥ 60%：表現優秀")
    print("- VQA準確度 40-60%：表現中等")  
    print("- VQA準確度 < 40%：需要改進")
    
    print("\n📁 結果文件：")
    print("- JSON格式：完整結果數據")
    print("- TXT格式：可讀摘要")
    print("- CSV格式：錯誤分析")

def print_results_summary(results, total_time, output_dir):
    """顯示結果摘要"""
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
    
    # 顯示文件位置
    print(f"\n📁 詳細結果已保存到：{output_dir}/")
    print("   - JSON格式：完整結果數據")
    print("   - TXT格式：可讀摘要")
    print("   - CSV格式：錯誤分析（如有）")
    
    print(f"\n⏱️  總測試時間：{total_time:.1f}秒")
    
    # 分析提示
    print("\n💡 結果分析提示：")
    print("1. VQA準確度比簡單準確度更準確（考慮標註者一致性）")
    print("2. 檢查detailed results了解具體錯誤類型")
    print("3. 比較不同模型在不同問題類型上的表現")
    print("4. 關注高信心度回答的準確性")

def print_troubleshooting_tips():
    """顯示故障排除建議"""
    print("\n🔧 故障排除建議：")
    print("1. 檢查網絡連接（需要下載COCO圖像）")
    print("2. 確認模型文件完整性")
    print("3. 檢查磁盤空間（圖像下載需要空間）")
    print("4. 嘗試使用 --fallback_images 選項")
    print("5. 使用更小的 --num_questions 值測試")

if __name__ == "__main__":
    sys.exit(main())
