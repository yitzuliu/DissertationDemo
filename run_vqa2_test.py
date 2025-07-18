#!/usr/bin/env python3
"""
VQA 2.0 Quick Test Runner - 優化版本
快速VQA 2.0評估腳本，支持小批量圖像下載和詳細結果分析

Usage:
    python run_vqa2_test.py --num_questions 20
    python run_vqa2_test.py --num_questions 20 --explanation
    
Author: AI Manual Assistant Team  
Date: 2025-01-27
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add project src to path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

try:
    from testing.vqa2_tester import VQA2Tester
    from testing.vqa2_config import VQA2_CONFIG
    from testing.vqa2_utils import print_vqa2_analysis, save_vqa2_results
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("請確認您在正確的目錄中，並且所有VQA 2.0文件都已創建")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Run VQA 2.0 evaluation with optimized image downloading')
    
    # Basic options
    parser.add_argument('--num_questions', type=int, default=20,
                       help='Number of questions to test (default: 20 for fast testing)')
    parser.add_argument('--models', nargs='+', 
                       default=['SmolVLM-Instruct'],
                       help='Models to test (default: SmolVLM-Instruct)')
    
    # Download options
    parser.add_argument('--force_download', action='store_true',
                       help='Force re-download of images')
    parser.add_argument('--sample_only', action='store_true', default=True,
                       help='Use optimized sample download for small batches (default: True)')
    parser.add_argument('--fallback_images', action='store_true',
                       help='Generate fallback images if COCO download fails')
    
    # Output options
    parser.add_argument('--output_dir', default='results',
                       help='Output directory for results')
    parser.add_argument('--save_detailed', action='store_true', default=True,
                       help='Save detailed results with evaluation metrics')
    
    # Testing options
    parser.add_argument('--explanation', action='store_true',
                       help='Show explanation of results format before testing')
    
    args = parser.parse_args()
    
    if args.explanation:
        print("📚 正在顯示VQA 2.0結果格式說明...")
        explain_script = project_root / "src" / "testing" / "example_vqa2_results.py"
        if explain_script.exists():
            os.system(f"python {explain_script}")
        else:
            print("說明文件未找到，繼續測試...")
        print("\n" + "="*60)
        input("按Enter鍵繼續測試，或Ctrl+C退出...")
    
    print("🚀 啟動VQA 2.0快速測試")
    print(f"📊 測試問題數：{args.num_questions}")
    print(f"🤖 測試模型：{', '.join(args.models)}")
    
    if args.num_questions <= 50:
        print("⚡ 使用優化下載模式（單張圖像下載）")
    else:
        print("📦 使用完整數據集下載模式")
    
    # Initialize tester with optimized settings
    try:
        tester = VQA2Tester(
            data_dir="data/vqa2",
            results_dir=args.output_dir,
            download_images=True
        )
        print("✅ VQA2Tester 初始化成功")
    except Exception as e:
        print(f"❌ VQA2Tester 初始化失敗: {e}")
        return 1
    
    start_time = time.time()
    
    try:
        # Run evaluation
        print("\n📝 開始VQA 2.0評估...")
        results = tester.run_evaluation(
            models_to_test=args.models,
            num_questions=args.num_questions,
            save_results=True
        )
        
        # Print summary
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
            
            # Performance assessment
            if vqa_accuracy >= 0.6:
                assessment = "🏆 表現優秀"
            elif vqa_accuracy >= 0.4:
                assessment = "🎯 表現中等"
            else:
                assessment = "🔧 需要改進"
            print(f"   {assessment}")
        
        # Show file locations
        print(f"\n📁 詳細結果已保存到：{args.output_dir}/")
        print("   - JSON格式：完整結果數據")
        print("   - TXT格式：可讀摘要") 
        print("   - CSV格式：錯誤分析（如有）")
        
        total_time = time.time() - start_time
        print(f"\n⏱️  總測試時間：{total_time:.1f}秒")
        
        # Quick analysis tips
        print("\n💡 結果分析提示：")
        print("1. VQA準確度比簡單準確度更準確（考慮標註者一致性）")
        print("2. 檢查detailed results中的evaluation_details了解錯誤類型")
        print("3. 比較不同模型在不同問題類型上的表現")
        print("4. 注意confidence與accuracy的相關性")
        
    except KeyboardInterrupt:
        print("\n⚠️  測試被使用者中斷")
        return 1
    except Exception as e:
        print(f"\n❌ 測試失敗：{str(e)}")
        print("\n🔧 troubleshooting建議：")
        print("1. 檢查網絡連接（下載COCO圖像需要）")
        print("2. 確認模型可用性")
        print("3. 檢查磁盤空間")
        print("4. 嘗試使用 --fallback_images 選項")
        return 1
    
    return 0

def run_quick_vqa2_test():
    """舊版本兼容性函數"""
    print("🔄 使用新版測試腳本...")
    return main()

if __name__ == "__main__":
    sys.exit(main())
    """Run a quick VQA 2.0 test with sample data"""
    print("🚀 Starting VQA 2.0 Quick Test")
    print("=" * 50)
    
    # Initialize tester
        # Remove old code that has syntax errors
        pass  # This section will be replaced by the new main function
    
    # Save results
    output_dir = Path("logs/vqa2_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"quick_test_{timestamp}.json"
    
    summary_results = {
        'test_type': 'quick_test',
        'timestamp': timestamp,
        'sample_size': len(sample_questions),
        'models_tested': list(results.keys()),
        'results': results,
        'config': {
            'max_questions_per_model': 10,
            'dataset': 'VQA 2.0 validation sample'
        }
    }
    
    save_vqa2_results(summary_results, results_file)
    
    # Print summary
    print("\n📋 Test Summary")
    print("=" * 30)
    
    best_accuracy = 0
    best_model = None
    
    for model_name, model_results in results.items():
        accuracy = model_results.get('accuracy', 0)
        print(f"{model_name}: {accuracy:.3f} accuracy")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model_name
    
    if best_model:
        print(f"\n🏆 Best performing model: {best_model} ({best_accuracy:.3f})")
    
    print(f"\n💾 Full results saved to: {results_file}")
    print("\n✅ Quick test completed!")

def run_sample_analysis_only():
    """Run only sample data analysis without model testing"""
    print("📊 VQA 2.0 Sample Analysis Only")
    print("=" * 40)
    
    try:
        tester = VQA2Tester()
        
        # Load or create sample data
        sample_questions, sample_annotations = tester.load_sample_data(sample_size=50)
        
        # Analyze sample
        analysis = tester.analyze_sample(sample_questions, sample_annotations)
        print_vqa2_analysis(analysis)
        
        # Show some example questions
        print("\n🔍 Example Questions:")
        print("-" * 30)
        
        for i, question in enumerate(sample_questions[:3]):
            question_id = question['question_id']
            question_text = question['question']
            
            print(f"\nExample {i+1}:")
            print(f"  Question: {question_text}")
            
            if question_id in sample_annotations:
                annotation = sample_annotations[question_id]
                answer = annotation['multiple_choice_answer']
                print(f"  Answer: {answer}")
        
        print("\n✅ Sample analysis completed!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

def show_help():
    """Show help information"""
    print("🔧 VQA 2.0 Test Runner Help")
    print("=" * 40)
    print("\nAvailable commands:")
    print("  python run_vqa2_test.py              - Run quick test (default)")
    print("  python run_vqa2_test.py --analysis  - Run analysis only")
    print("  python run_vqa2_test.py --help      - Show this help")
    print("\nFor full testing, use:")
    print("  python vqa2_tester.py")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if '--help' in sys.argv or '-h' in sys.argv:
            show_help()
            return
        elif '--analysis' in sys.argv:
            run_sample_analysis_only()
            return
    
    # Default: run quick test
    run_quick_vqa2_test()

if __name__ == "__main__":
    main()
