#!/usr/bin/env python3
"""
VQA 2.0 測試框架 - COCO真實數據版本
整合所有VQA 2.0測試功能，支持多種VLM模型，統一使用COCO真實數據

使用方法:
    python vqa_test.py --questions 20           # COCO真實數據測試（默認）
    python vqa_test.py --quick --questions 20   # 同上（顯式指定quick模式）
    python vqa_test.py --models moondream2 --questions 10  # 指定模型測試
    python vqa_test.py --help                   # 查看所有選項

Author: AI Manual Assistant Team
Date: 2025-01-27
"""

import sys
import time
import argparse
import json
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description="VQA 2.0 測試工具")
    
    # 測試模式（僅保留 quick 模式，使用 COCO 真實數據）
    parser.add_argument('--quick', action='store_true', default=True,
                       help='使用20張COCO真實圖像進行測試（默認模式）')
    
    # 測試參數
    parser.add_argument('--questions', type=int, default=20,
                       help='測試問題數量 (默認: 20，最多20張COCO圖像)')
    parser.add_argument('--models', nargs='+', 
                       default=['moondream2'],
                       choices=['smolvlm_instruct', 'smolvlm_v2_instruct', 'moondream2', 'llava_mlx', 'phi35_vision'],
                       help='要測試的模型列表')
    
    # 高級選項
    parser.add_argument('--verbose', action='store_true',
                       help='顯示詳細輸出')
    parser.add_argument('--save-results', action='store_true', default=True,
                       help='保存測試結果')
    
    args = parser.parse_args()
    
    print("🎯 VQA 2.0 測試框架")
    print("=" * 60)
    
    try:
        from vqa_framework import VQAFramework
        print("✅ 成功導入VQA框架")
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        print("請確認 vqa_framework.py 文件存在")
        return 1
    
    # 初始化框架
    try:
        framework = VQAFramework()
        print("✅ VQA框架初始化成功")
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        return 1
    
    # 顯示測試配置
    print(f"\n📊 測試配置:")
    print(f"   📝 問題數量: {args.questions}")
    print(f"   🤖 測試模型: {', '.join(args.models)}")
    print(f"   🎯 測試模式: COCO真實數據測試")
    
    start_time = time.time()
    
    try:
        # 使用 COCO 真實數據進行測試
        print(f"\n⚡ 運行COCO真實數據測試...")
        print("📝 使用20張COCO圖像和真實VQA數據")
        # 限制最多20個問題（對應20張COCO圖像）
        questions, annotations = framework.load_sample_data(min(args.questions, 20))
        print(f"✅ 使用最多20張COCO圖像: {len(questions)} 個問題")
        
        # 檢查圖片可用性
        print(f"\n🖼️ 檢查圖片可用性...")
        image_stats = framework.check_image_availability(questions)
        print(f"📈 圖片可用性: {image_stats['available']}/{image_stats['total']} ({image_stats['rate']:.1%})")
        
        # 運行評估
        print(f"\n🤖 開始模型評估...")
        all_results = {}
        
        for i, model_name in enumerate(args.models, 1):
            print(f"\n[{i}/{len(args.models)}] 評估模型: {model_name}")
            
            results = framework.evaluate_model(
                model_name=model_name,
                questions=questions,
                annotations=annotations,
                max_questions=args.questions,
                verbose=args.verbose
            )
            
            all_results[model_name] = results
        
        # 顯示結果摘要
        print("\n" + "="*60)
        print("📈 測試完成！結果摘要：")
        print("="*60)
        
        best_model = None
        best_vqa_accuracy = 0
        
        for model_name, results in all_results.items():
            if "error" in results:
                print(f"\n❌ {model_name}: 評估失敗 - {results['error']}")
                continue
                
            accuracy = results.get("accuracy", 0)
            vqa_accuracy = results.get("vqa_accuracy", 0)
            correct = results.get("correct", 0)
            total = results.get("total", 0)
            avg_time = results.get("avg_time", 0)
                
            if vqa_accuracy > best_vqa_accuracy:
                best_vqa_accuracy = vqa_accuracy
                best_model = model_name
            
            print(f"\n🤖 {model_name}:")
            print(f"   ✅ 正確答案：{correct}/{total}")
            print(f"   📊 簡單準確度：{accuracy:.1%}")
            print(f"   🎯 VQA準確度：{vqa_accuracy:.1%}")
            print(f"   ⏱️ 平均推理時間：{avg_time:.2f}秒")
            
            # 顯示問題和圖像對照信息
            if args.verbose and "question_results" in results:
                print(f"   📋 問題詳情:")
                for i, q_result in enumerate(results["question_results"][:5], 1):  # 只顯示前5個
                    q_id = q_result.get('question_id', 'N/A')
                    img_id = q_result.get('image_id', 'N/A')
                    img_file = q_result.get('image_filename', 'N/A')
                    is_correct = q_result.get('is_correct', False)
                    status = "✅" if is_correct else "❌"
                    print(f"      {i}. {status} Q{q_id} → 圖像{img_id} ({img_file})")
                if len(results["question_results"]) > 5:
                    print(f"      ... 及其他 {len(results['question_results'])-5} 個問題")
            
            # 表現評估
            if vqa_accuracy >= 0.6:
                assessment = "🏆 表現優秀"
            elif vqa_accuracy >= 0.4:
                assessment = "🎯 表現中等"
            else:
                assessment = "🔧 需要改進"
            print(f"   {assessment}")
        
        if best_model:
            print(f"\n🏆 最佳模型: {best_model} (VQA準確度: {best_vqa_accuracy:.1%})")
        
        # 保存結果
        if args.save_results and all_results:
            try:
                results_file = framework.save_results(all_results, "coco", args.questions)
                print(f"\n💾 結果已保存到: {results_file}")
            except Exception as e:
                print(f"\n⚠️ 保存結果失敗: {e}")
        
        total_time = time.time() - start_time
        print(f"\n⏱️ 總測試時間：{total_time:.1f}秒")
        print(f"\n✅ VQA 2.0測試成功完成！")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️ 測試被用戶中斷")
        return 1
    except Exception as e:
        print(f"\n❌ 測試失敗：{str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        print(f"\n🔧 故障排除建議：")
        print("1. 檢查網絡連接")
        print("2. 確認模型文件完整性")
        print("3. 檢查數據目錄權限")
        print("4. 使用 --verbose 查看詳細錯誤信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())
