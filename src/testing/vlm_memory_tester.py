#!/usr/bin/env python3
"""
VLM 模型短期對話記憶測試程式
MacBook Air M3 (16GB) 優化版本

測試流程:
1.  **記憶植入 (Memory Seeding)**: 向模型展示一張圖片和一個詳細的提示詞，要求其詳細描述。
2.  **記憶回溯 (Memory Recall)**: 不再次展示圖片，連續問三個關於剛剛圖片內容的通用性問題。
3.  **循環**: 為每個模型的每張測試圖片重複以上步驟。
4.  **輸出**: 將完整的對話歷史記錄為 JSON 檔案。
"""

import os
import time
import json
import gc
import psutil
from datetime import datetime
from pathlib import Path
from PIL import Image
import torch

# 引入 vlm_tester.py 中的模型載入器和輔助函數
# 為了保持程式碼獨立性，我們直接從該檔案複製必要組件
# (在實際專案中，可能會將這些共享組件重構為獨立模組)

# --- 從 vlm_tester.py 複製的輔助函數 ---

def get_memory_usage():
    """獲取當前記憶體使用量（GB）"""
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 ** 3)

def clear_model_memory(model, processor):
    """清理模型記憶體"""
    print("🧹 清理模型記憶體...")
    del model, processor
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    time.sleep(2)

# --- 從 vlm_tester.py 複製的模型載入器 ---

class VLMModelLoader:
    """VLM 模型載入器 - 與 vlm_tester.py 保持一致"""
    
    @staticmethod
    def load_smolvlm2_video(model_id="HuggingFaceTB/SmolVLM2-500M-Video-Instruct"):
        from transformers import AutoProcessor, AutoModelForImageTextToText
        print(f"載入 {model_id}...")
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForImageTextToText.from_pretrained(model_id)
        return model, processor
    
    @staticmethod
    def load_smolvlm_instruct(model_id="HuggingFaceTB/SmolVLM-500M-Instruct"):
        from transformers import AutoProcessor, AutoModelForVision2Seq
        print(f"載入 {model_id}...")
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForVision2Seq.from_pretrained(model_id)
        return model, processor
    
    @staticmethod
    def load_moondream2(model_id="vikhyatk/moondream2"):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        print(f"載入 {model_id}...")
        model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        if torch.backends.mps.is_available():
            model = model.to('mps')
        return model, tokenizer
    
    @staticmethod
    def load_llava_mlx(model_id="mlx-community/llava-v1.6-mistral-7b-4bit"):
        print(f"載入 MLX-LLaVA {model_id}...")
        try:
            from mlx_vlm import load
            model, processor = load(model_id)
            print("MLX-LLaVA 載入成功!")
            return model, processor
        except ImportError:
            raise RuntimeError("MLX-VLM 套件未安裝 (pip install mlx-vlm)，無法測試此模型。")
    
    @staticmethod
    def load_phi3_vision(model_id="lokinfey/Phi-3.5-vision-mlx-int4"):
        print(f"載入 MLX Phi-3.5-Vision {model_id}...")
        try:
            from mlx_vlm import load
            model, processor = load(model_id, trust_remote_code=True)
            print("MLX Phi-3.5-Vision 載入成功!")
            return model, processor
        except ImportError:
            raise RuntimeError("MLX-VLM 套件未安裝 (pip install mlx-vlm)，無法測試此模型。")

# --- 新的記憶力測試核心程式 ---

class VLMMemoryTester:
    """VLM 記憶力測試器"""
    
    def __init__(self):
        self.results = {
            "test_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {
                "device": "MacBook Air M3",
                "memory": "16GB",
                "mps_available": torch.backends.mps.is_available()
            },
            "models": {}
        }
        
        # 測試模型配置 (與 vlm_tester.py 相同)
        self.models_config = {
            "SmolVLM2-500M-Video-Instruct": { "loader": VLMModelLoader.load_smolvlm2_video, "model_id": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct" },
            "SmolVLM-500M-Instruct": { "loader": VLMModelLoader.load_smolvlm_instruct, "model_id": "HuggingFaceTB/SmolVLM-500M-Instruct" },
            "Moondream2": { "loader": VLMModelLoader.load_moondream2, "model_id": "vikhyatk/moondream2" },
            "LLaVA-v1.6-Mistral-7B-MLX": { "loader": VLMModelLoader.load_llava_mlx, "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit" },
            "Phi-3.5-Vision-Instruct": { "loader": VLMModelLoader.load_phi3_vision, "model_id": "lokinfey/Phi-3.5-vision-mlx-int4" }
        }
        
        # 📏 統一測試條件
        self.unified_max_tokens = 250
        self.unified_image_size = 1024
        
        # 🧠 記憶力測試提示詞
        self.seeding_prompt = "You are a forensic expert. Describe this image in extreme detail, listing every object, person, color, and spatial relationship you can identify. This is for a critical investigation."
        self.recall_questions = [
            "Based on the description you just gave me, what were the most prominent colors in the image?",
            "Were there any people visible in the image? If so, describe their general appearance or clothing without making up details.",
            "Summarize the main subject or scene of the image in one sentence."
        ]
        
        # 💡 核心概念修正 (ID: fix-concept)
        # 建立一個純黑色的空白圖片，用於在追問階段滿足 processor 的技術要求，同時不洩漏原始圖像資訊
        self.black_image = Image.new('RGB', (224, 224), 'black')

    def get_test_images(self):
        """獲取測試圖像列表 (與 vlm_tester.py 相同)"""
        possible_paths = [
            Path("src/testing/testing_material/images"),
            Path("testing_material/images"),
            Path("./testing_material/images")
        ]
        images_dir = next((path for path in possible_paths if path.exists()), None)
        if not images_dir:
            return []
        
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(images_dir.glob(ext))
            image_files.extend(images_dir.glob(ext.upper()))
        return sorted(image_files)

    def run_all_tests(self):
        """執行所有模型的記憶力測試"""
        print("="*60)
        print("🤖 開始 VLM 模型短期對話記憶測試 🤖")
        print("="*60)
        
        test_images = self.get_test_images()
        if not test_images:
            print("❌ 錯誤：找不到測試圖像。請確保圖像位於 src/testing/testing_material/images/")
            return

        print(f"🖼️ 找到 {len(test_images)} 張測試圖像。")
        total_start_time = time.time()

        for model_name, config in self.models_config.items():
            self.test_single_model(model_name, config, test_images)
        
        total_time = time.time() - total_start_time
        self.results["total_test_time"] = total_time
        print(f"\n✅ 所有測試完成，總時間: {total_time:.2f} 秒")
        self.save_results()

    def test_single_model(self, model_name, config, test_images):
        """測試單一模型"""
        print(f"\n{'='*50}\n🔬 開始測試模型: {model_name}\n{'='*50}")
        
        memory_before = get_memory_usage()
        print(f"載入前記憶體: {memory_before:.2f} GB")
        
        model_results = {
            "model_id": config["model_id"],
            "image_tests": []
        }
        
        try:
            start_time = time.time()
            model, processor = config["loader"]()
            load_time = time.time() - start_time
            
            memory_after = get_memory_usage()
            print(f"載入後記憶體: {memory_after:.2f} GB (耗時 {load_time:.2f} 秒)")
            
            model_results.update({
                "load_time": load_time,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_diff": memory_after - memory_before
            })

            for image_path in test_images:
                print(f"\n--- 測試圖像: {image_path.name} ---")
                image_test_result = self.run_conversation_test(model, processor, image_path, model_name)
                model_results["image_tests"].append(image_test_result)
            
        except Exception as e:
            print(f"❌ 測試模型 {model_name} 時發生嚴重錯誤: {e}")
            model_results["error"] = str(e)
        
        finally:
            if 'model' in locals():
                clear_model_memory(model, processor)
                memory_after_cleanup = get_memory_usage()
                print(f"清理後記憶體: {memory_after_cleanup:.2f} GB")
                model_results["memory_after_cleanup"] = memory_after_cleanup

            self.results["models"][model_name] = model_results
            self.save_results(f"intermediate_{model_name}")

    def run_conversation_test(self, model, processor, image_path, model_name):
        """執行完整的單圖對話測試（植入 -> 追問）"""
        
        image_test_result = {
            "image_name": image_path.name,
            "seeding_phase": {},
            "recall_phase": {},
            "full_conversation_history": [],
            "debug_info": {} # 用於儲存額外的調試資訊
        }
        
        # 準備圖像
        image = Image.open(image_path).convert('RGB')
        
        # LLaVA 的狀態問題需要每次都重新載入模型來解決
        if "LLaVA" in model_name:
            print("  >> LLaVA-MLX: Reloading model to clear state before new conversation...")
            try:
                config = self.models_config[model_name]
                # 確保舊模型和處理器被正確清理
                if 'model' in locals() and model is not None:
                    clear_model_memory(model, processor)
                model, processor = config["loader"]()
                print("  >> LLaVA-MLX: Reload successful.")
            except Exception as e:
                print(f"  >> LLaVA-MLX: Reload failed: {e}")
                image_test_result["error"] = f"LLaVA reload failed: {e}"
                return image_test_result

        # 步驟一: 記憶植入
        print("1️⃣  步驟 1: 記憶植入 (Seeding)")
        seeding_response, seeding_time, conversation_history = self.run_inference(
            model, processor, model_name, self.seeding_prompt, image=image, history=[]
        )
        image_test_result["seeding_phase"] = {
            "prompt": self.seeding_prompt,
            "response": seeding_response,
            "inference_time": seeding_time
        }
        image_test_result["full_conversation_history"] = conversation_history
        image_test_result["debug_info"]["seeding_prompt"] = conversation_history[-2] if len(conversation_history) > 1 else {}

        print(f"    - 回應 (前100字): {seeding_response[:100].strip()}...")
        print(f"    - 推理時間: {seeding_time:.2f} 秒")
        
        # 如果植入失敗，提前終止
        if "錯誤：" in seeding_response:
            print("    - 植入失敗，跳過追問。")
            return image_test_result

        # 步驟二: 記憶回溯
        print("\n2️⃣  步驟 2: 記憶回溯 (Recall)")
        for i, question in enumerate(self.recall_questions):
            print(f"  - 追問 {i+1}/3: {question}")
            
            # 依賴 run_inference 內部邏輯來正確處理歷史和圖片
            recall_response, recall_time, conversation_history = self.run_inference(
                model, processor, model_name, question, image=image, history=conversation_history
            )
            
            image_test_result["recall_phase"][f"question_{i+1}"] = {
                "prompt": question,
                "response": recall_response,
                "inference_time": recall_time
            }
            image_test_result["full_conversation_history"] = conversation_history
            image_test_result["debug_info"][f"recall_prompt_{i+1}"] = conversation_history[-2] if len(conversation_history) > 1 else {}
            
            print(f"    - 回應: {recall_response.strip()}")
            print(f"    - 推理時間: {recall_time:.2f} 秒")
            
        return image_test_result

    def run_inference(self, model, processor, model_name, prompt, image, history):
        """
        通用推理函數（已重構）
        為每一類模型實現了各自正確的、符合其官方範例的對話狀態管理方法。
        """
        start_time = time.time()
        response = ""
        new_history = list(history)
        
        try:
            # --------------------------------------------------------------------------
            # 分支 1: 標準 Transformers 模型 (e.g., SmolVLM)
            # --------------------------------------------------------------------------
            if "SmolVLM" in model_name:
                # 關鍵修正 (ID: fix-smolvlm)
                is_seeding_prompt = not history
                
                content = [{"type": "text", "text": prompt}]
                if is_seeding_prompt:
                    content.insert(0, {"type": "image"}) # 僅在第一輪添加圖像佔位符
                
                new_history.append({"role": "user", "content": content})
                final_prompt = processor.apply_chat_template(new_history, tokenize=False, add_generation_prompt=True)

                # 根據階段選擇使用的圖片：第一次用真實圖片，追問用黑畫面
                image_to_use = image if is_seeding_prompt else self.black_image
                
                inputs = processor(text=final_prompt, images=image_to_use, return_tensors="pt")
                with torch.no_grad():
                    outputs = model.generate(**inputs, max_new_tokens=self.unified_max_tokens, do_sample=False)
                
                input_len = inputs["input_ids"].shape[1]
                generated_ids = outputs[0][input_len:]
                response = processor.decode(generated_ids, skip_special_tokens=True).strip()
                
                # 更新歷史記錄
                new_history.append({"role": "assistant", "content": response})

            # --------------------------------------------------------------------------
            # 分支 2: Moondream2 (特殊 API - 上下文注入策略)
            # --------------------------------------------------------------------------
            elif "Moondream2" in model_name:
                # 關鍵修正 (ID: fix-moondream)
                enc_image = model.encode_image(image) # 始終使用原始圖片的嵌入
                is_seeding_prompt = not history

                if is_seeding_prompt:
                    final_prompt = prompt
                else:
                    last_response = ""
                    if history and history[-1]["role"] == "assistant":
                        last_response = history[-1]["content"]
                    final_prompt = f"Based on your previous description of an image which was: '{last_response}'. Now, please answer this new question: {prompt}"
                
                response = model.answer_question(enc_image, final_prompt, processor)
                new_history.append({"role": "user", "content": prompt})
                new_history.append({"role": "assistant", "content": response})

            # --------------------------------------------------------------------------
            # 分支 3: MLX 模型 (e.g., LLaVA, Phi-3.5 - 官方對話模板策略)
            # --------------------------------------------------------------------------
            elif "LLaVA" in model_name or "Phi-3.5" in model_name:
                # 關鍵修正 (ID: fix-mlx)
                from mlx_vlm import generate
                
                is_seeding_prompt = not history
                
                # 1. 構建標準 messages 列表
                current_turn = {"role": "user", "content": prompt}
                if is_seeding_prompt and "Phi-3.5" in model_name:
                    current_turn["content"] = f"<|image_1|>\n{prompt}"
                
                messages_for_template = history + [current_turn]
                
                # 2. 使用官方模板生成 final_prompt
                final_prompt = processor.tokenizer.apply_chat_template(
                    messages_for_template, 
                    tokenize=False, 
                    add_generation_prompt=True
                )

                gen_kwargs = {
                    "model": model,
                    "processor": processor,
                    "prompt": final_prompt,
                    "max_tokens": self.unified_max_tokens,
                    "verbose": False
                }
                
                # MLX 追問時，完全不提供 image 參數
                if is_seeding_prompt:
                    temp_image_path = "temp_mlx_image.png"
                    image.save(temp_image_path)
                    gen_kwargs["image"] = temp_image_path
                
                raw_response = generate(**gen_kwargs)
                
                if 'image' in gen_kwargs and os.path.exists(gen_kwargs['image']):
                    os.remove(gen_kwargs['image'])

                # 關鍵修正 (ID: fix-mlx-tuple-bug) - 正確處理 tuple 並清理 response
                if isinstance(raw_response, tuple):
                    response_text = raw_response[0]
                else:
                    response_text = str(raw_response)

                # mlx_vlm.generate 只返回生成的部分，不需要從完整 prompt 中替換
                # 我們只需要清理可能殘留的特殊 token
                stop_tokens = ["<|end|>", "<|endoftext|>", "ASSISTANT:", "USER:", "<|im_end|>"]
                clean_response = response_text
                for token in stop_tokens:
                    clean_response = clean_response.replace(token, "")
                response = clean_response.strip()
                
                # 更新歷史記錄
                new_history.append(current_turn)
                new_history.append({"role": "assistant", "content": response})
            
            else:
                response = "錯誤：未知的模型類型，無法進行推理。"
            
            # 豐富 debug_info (ID: refine-json)
            if not new_history[-2].get('debug_info'):
                 new_history[-2]['debug_info'] = {}
            new_history[-2]['debug_info']['final_prompt_to_model'] = final_prompt
            if 'image_to_use' in locals() and image_to_use == self.black_image:
                 new_history[-2]['debug_info']['used_black_image_test'] = True


        except Exception as e:
            import traceback
            print(traceback.format_exc())
            response = f"錯誤：推理過程中發生異常 - {str(e)}"
            # 發生錯誤時，也要更新歷史記錄以反映錯誤
            if not new_history or new_history[-1]['role'] != 'user':
                 new_history.append({"role": "user", "content": prompt})
            new_history.append({"role": "assistant", "content": response})

        inference_time = time.time() - start_time
        return response, inference_time, new_history

    def save_results(self, suffix=""):
        """儲存測試結果"""
        # 支援從不同目錄執行程式
        possible_results_dirs = [
            Path("src/testing/results"),  # 從專案根目錄執行
            Path("results"),              # 從 src/testing 目錄執行
            Path("./results")             # 當前目錄
        ]
        
        # 使用第一個可行的路徑
        results_dir = next((path for path in possible_results_dirs if path.is_dir() or path.parent.is_dir()), Path("results"))
        results_dir.mkdir(parents=True, exist_ok=True)
        
        if suffix:
            filename = f"memory_test_results_{suffix}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_test_results_{timestamp}.json"
        
        filepath = results_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # 使用自定義序列化器來處理 Path 對象
                def path_serializer(obj):
                    if isinstance(obj, Path):
                        return str(obj)
                    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
                json.dump(self.results, f, ensure_ascii=False, indent=2, default=path_serializer)
            print(f"\n💾 結果已儲存至: {filepath}")
        except Exception as e:
            print(f"❌ 儲存結果時發生錯誤: {e}")

def main():
    """主函數"""
    tester = VLMMemoryTester()
    tester.run_all_tests()
    print("\n記憶力測試完成！")

if __name__ == "__main__":
    main() 