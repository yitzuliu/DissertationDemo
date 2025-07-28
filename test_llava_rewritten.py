#!/usr/bin/env python3
"""
測試重寫的 LLaVA-MLX 實現
"""

import sys
import os
sys.path.append('src/testing/vlm')

def test_llava_loading():
    """測試 LLaVA 模型加載"""
    print("🧪 測試 LLaVA 模型加載...")
    
    try:
        from vlm_tester import VLMModelLoader
        
        # 測試加載 LLaVA
        print("📥 加載 LLaVA-MLX 模型...")
        model, processor = VLMModelLoader.load_llava_mlx()
        
        print("✅ LLaVA 模型加載成功!")
        print(f"   模型類型: {type(model)}")
        print(f"   處理器類型: {type(processor)}")
        print(f"   MLX 標記: {hasattr(model, '_is_mlx_model')}")
        
        return True, model, processor
        
    except Exception as e:
        print(f"❌ LLaVA 模型加載失敗: {e}")
        return False, None, None

def test_llava_inference(model, processor):
    """測試 LLaVA 推理"""
    print("\n🧪 測試 LLaVA 推理...")
    
    try:
        from vlm_tester import VLMTester
        from PIL import Image
        import tempfile
        
        # 創建測試圖片
        test_image = Image.new('RGB', (224, 224), color='red')
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            temp_image_path = tmp_file.name
            test_image.save(temp_image_path)
        
        # 創建測試器
        tester = VLMTester()
        
        # 測試圖片推理
        print("🖼️ 測試圖片推理...")
        image_result = tester.test_single_image(
            model, processor, 
            temp_image_path, 
            "LLaVA-v1.6-Mistral-7B-MLX"
        )
        
        print(f"   推理時間: {image_result.get('inference_time', 0):.2f} 秒")
        print(f"   回應長度: {len(image_result.get('response', ''))}")
        print(f"   錯誤: {image_result.get('error', 'None')}")
        
        # 測試文字推理
        print("\n🔤 測試文字推理...")
        text_response = tester._test_llava_text_only(
            model, processor, 
            "What is the capital of France?"
        )
        
        print(f"   文字回應: {text_response[:100]}...")
        
        # 清理
        os.remove(temp_image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ LLaVA 推理測試失敗: {e}")
        return False

def test_llava_full_workflow():
    """測試完整的 LLaVA 工作流程"""
    print("\n🧪 測試完整 LLaVA 工作流程...")
    
    try:
        from vlm_tester import VLMTester
        
        # 創建測試器
        tester = VLMTester()
        
        # 獲取 LLaVA 配置
        llava_config = tester.models_config.get("LLaVA-v1.6-Mistral-7B-MLX")
        if not llava_config:
            print("❌ LLaVA 配置未找到")
            return False
        
        print("📋 LLaVA 配置:")
        print(f"   模型 ID: {llava_config['model_id']}")
        print(f"   優先級: {llava_config['priority']}")
        print(f"   記憶體密集: {llava_config['memory_intensive']}")
        
        # 測試單個模型
        print("\n🔄 運行單個模型測試...")
        model_results = tester.test_single_model("LLaVA-v1.6-Mistral-7B-MLX", llava_config)
        
        print("📊 測試結果:")
        print(f"   加載時間: {model_results.get('load_time', 0):.2f} 秒")
        print(f"   成功推理: {model_results.get('successful_inferences', 0)}")
        print(f"   失敗推理: {model_results.get('failed_inferences', 0)}")
        print(f"   文字支持: {model_results.get('text_only_capability', {}).get('text_only_supported', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整工作流程測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 LLaVA-MLX 重寫版本測試")
    print("=" * 50)
    
    # 測試加載
    success, model, processor = test_llava_loading()
    if not success:
        print("\n💥 LLaVA 加載失敗，停止測試")
        return False
    
    # 測試推理
    if not test_llava_inference(model, processor):
        print("\n💥 LLaVA 推理測試失敗")
        return False
    
    # 測試完整工作流程
    if not test_llava_full_workflow():
        print("\n💥 完整工作流程測試失敗")
        return False
    
    print("\n🎉 所有 LLaVA 測試通過!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)