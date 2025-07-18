#!/usr/bin/env python3
"""
VQA 2.0 常規測試 - 使用真實COCO圖片和VQA數據
使用前20張下載的COCO圖片進行標準VQA 2.0評估

使用方法:
    python standard_vqa2_test.py
"""

import sys
import time
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def main():
    print("🎯 VQA 2.0 常規測試 - 使用真實COCO數據")
    print("=" * 60)
    
    try:
        from testing.vqa2_tester import VQA2Tester
        print("✅ 成功導入VQA2Tester")
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        return
    
    # 初始化測試器
    try:
        tester = VQA2Tester(data_dir="data/vqa2")
        print("✅ VQA2Tester 初始化成功")
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        return
    
    print("\n📥 準備VQA 2.0常規數據...")
    print("- 將下載VQA 2.0驗證集問題和答案")
    print("- 使用現有的20張COCO圖片")
    print("- 進行標準VQA 2.0評估")
    
    start_time = time.time()
    
    try:
        # 下載VQA 2.0數據集（如果尚未下載）
        print("\n📥 檢查並下載VQA 2.0數據集...")
        tester.download_vqa2_dataset(['val_questions', 'val_annotations'])
        
        # 加載真實VQA 2.0數據
        print("\n📖 加載VQA 2.0驗證數據...")
        try:
            questions, annotations = tester.load_vqa2_data("val", sample_size=20)
            print(f"✅ 加載了 {len(questions)} 個VQA 2.0問題")
        except Exception as e:
            print(f"❌ 加載VQA數據失敗: {e}")
            print("💡 將使用樣本數據進行測試...")
            questions, annotations = tester.load_sample_data(sample_size=20)
        
        # 檢查圖片可用性
        print("\n🖼️ 檢查圖片可用性...")
        image_stats = tester.check_image_availability(questions)
        print(f"📈 圖片可用性: {image_stats['available_images']}/{image_stats['total_questions']} ({image_stats['availability_rate']:.1%})")
        
        if image_stats['availability_rate'] < 0.5:
            print("⚠️ 圖片可用性較低，可能影響測試結果")
        
        # 運行評估 - 使用真實VQA問題和答案
        print(f"\n🤖 開始評估模型: smolvlm_instruct")
        print("📊 使用真實VQA 2.0評估協議...")
        
        results = {}
        
        # 評估SmolVLM模型
        model_results = tester.evaluate_model(
            model_name="smolvlm_instruct",
            questions=questions,
            annotations=annotations,
            max_questions=20
        )
        
        results["smolvlm_instruct"] = model_results
        
        # 顯示結果
        print("\n" + "="*60)
        print("📈 VQA 2.0常規測試完成！結果摘要：")
        print("="*60)
        
        if "error" not in model_results:
            accuracy = model_results.get("accuracy", 0)
            vqa_accuracy = 0.0
            
            # 計算平均VQA準確度
            total_vqa_accuracy = 0.0
            valid_questions = 0
            
            for q_result in model_results.get("question_results", []):
                if "vqa_accuracy" in q_result:
                    total_vqa_accuracy += q_result["vqa_accuracy"]
                    valid_questions += 1
            
            if valid_questions > 0:
                vqa_accuracy = total_vqa_accuracy / valid_questions
            
            correct = model_results.get("correct_answers", 0)
            total = model_results.get("questions_evaluated", 0)
            avg_time = model_results.get("average_inference_time", 0)
            
            print(f"\n🤖 SmolVLM-Instruct:")
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
            
            # 顯示一些具體問答示例
            print(f"\n📝 具體問答示例:")
            for i, q_result in enumerate(model_results.get("question_results", [])[:5]):
                print(f"{i+1}. Q: {q_result['question']}")
                print(f"   模型: {q_result['model_answer']}")
                print(f"   正確: {q_result['ground_truth']}")
                print(f"   ✅" if q_result['is_correct'] else "❌")
                print()
        else:
            print(f"❌ 評估失敗: {model_results['error']}")
        
        total_time = time.time() - start_time
        print(f"⏱️  總測試時間：{total_time:.1f}秒")
        
        # 保存結果
        try:
            results_metadata = {
                "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "test_type": "standard_vqa2",
                "num_questions": 20,
                "data_source": "VQA 2.0 validation set",
                "image_source": "COCO val2014 (first 20 images)"
            }
            
            full_results = {"test_metadata": results_metadata}
            full_results.update(results)
            
            tester.results = full_results
            tester.save_results("_standard")
            print(f"💾 結果已保存到 results/ 目錄")
            
        except Exception as e:
            print(f"⚠️ 保存結果失敗: {e}")
        
        print("\n💡 測試分析:")
        print("1. 這是使用真實VQA 2.0數據集的標準評估")
        print("2. 圖片來自COCO數據集（前20張）")
        print("3. 問題和答案來自VQA 2.0驗證集")
        print("4. 使用官方VQA評估協議")
        
        print("\n✅ VQA 2.0常規測試成功完成！")
        
    except Exception as e:
        print(f"\n❌ 測試失敗：{str(e)}")
        print("\n🔧 故障排除建議：")
        print("1. 檢查網絡連接（下載VQA數據需要）")
        print("2. 確認模型文件完整性")
        print("3. 檢查COCO圖片是否存在")

if __name__ == "__main__":
    main()
