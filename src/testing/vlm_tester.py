#!/usr/bin/env python3
"""
VLM 模型測試程式
MacBook Air M3 (16GB) 優化版本 - 逐一載入模型避免記憶體溢出
"""

import os
import time
import json
import gc
import signal
import threading
import psutil
from datetime import datetime
from pathlib import Path
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForVision2Seq, AutoModelForCausalLM, AutoModelForImageTextToText
from transformers.pipelines import pipeline

# 記憶體監控 [[memory:2405482]]
def activate_virtual_env():
    """確保虛擬環境已啟動"""
    print("請確保已啟動虛擬環境: source ai_vision_env/bin/activate")

def get_memory_usage():
    """獲取當前記憶體使用量（GB）"""
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 ** 3)  # 轉換為 GB

def clear_model_memory(model, processor):
    """清理模型記憶體"""
    print("清理模型記憶體...")
    del model, processor
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    time.sleep(2)  # 讓系統有時間清理記憶體

class TimeoutError(Exception):
    """超時錯誤"""
    pass

def run_with_timeout(func, timeout_seconds=120):
    """在指定時間內執行函數，超時則拋出異常"""
    result = []
    exception = []
    
    def target():
        try:
            result.append(func())
        except Exception as e:
            exception.append(e)
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        # 超時了，但 Python 無法強制終止線程，只能拋出異常
        raise TimeoutError(f"推理超時（{timeout_seconds}秒）")
    
    if exception:
        raise exception[0]
    
    return result[0] if result else None

# 模型載入器類
class VLMModelLoader:
    """VLM 模型載入器 - 根據 active_model.md 實現"""
    
    @staticmethod
    def load_smolvlm2_video(model_id="HuggingFaceTB/SmolVLM2-500M-Video-Instruct"):
        """載入 SmolVLM2-500M-Video-Instruct"""
        print(f"載入 {model_id}...")
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForImageTextToText.from_pretrained(model_id)
        return model, processor
    
    @staticmethod
    def load_smolvlm_instruct(model_id="HuggingFaceTB/SmolVLM-500M-Instruct"):
        """載入 SmolVLM-500M-Instruct"""
        print(f"載入 {model_id}...")
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForVision2Seq.from_pretrained(model_id)
        return model, processor
    
    @staticmethod
    def load_moondream2(model_id="vikhyatk/moondream2"):
        """載入 Moondream2 - 使用特殊 API（模型不支持標準 pipeline）"""
        print(f"載入 {model_id}...")
        # Moondream2 有自定義配置，無法使用標準 pipeline，需使用原始方式
        from transformers import AutoTokenizer
        model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # 將模型移動到適當的設備
        if torch.backends.mps.is_available():
            model = model.to('mps')
        
        return model, tokenizer
    
    @staticmethod
    def load_llava_mlx(model_id="mlx-community/llava-v1.6-mistral-7b-4bit"):
        """載入 MLX-LLaVA (Apple Silicon optimized)"""
        print(f"載入 MLX-LLaVA {model_id}...")
        try:
            from mlx_vlm import load
            print("正在載入 MLX 優化的 LLaVA 模型...")
            model, processor = load(model_id)
            print("MLX-LLaVA 載入成功!")
            return model, processor
        except ImportError as e:
            print("MLX-VLM 未安裝。請運行: pip install mlx-vlm")
            print("回退到原始 transformers 方法...")
            raise RuntimeError("MLX-VLM 套件未安裝，無法使用 MLX 優化")
        except Exception as e:
            print(f"MLX-LLaVA 載入失敗: {str(e)}")
            raise RuntimeError(f"MLX-LLaVA 模型載入失敗: {str(e)}")
    
    @staticmethod
    def load_phi3_vision(model_id="lokinfey/Phi-3.5-vision-mlx-int4"):
        """Load Phi-3.5-Vision-Instruct using MLX (Apple Silicon optimized)"""
        print(f"Loading {model_id} with MLX framework...")
        try:
            # Use MLX-VLM for Apple Silicon optimization
            import mlx.core as mx
            from mlx_vlm import load, generate
            from mlx_vlm.utils import load_config
            
            print("Loading MLX-optimized Phi-3.5-Vision model...")
            model, processor = load(model_id, trust_remote_code=True)
            print("MLX model loaded successfully!")
            
            return model, processor
            
        except ImportError as e:
            print("MLX-VLM not installed. Installing MLX-VLM...")
            print("Please run: pip install mlx-vlm")
            print("Falling back to original transformers approach...")
            
            # Fallback to original approach if MLX not available
            from transformers import AutoModelForCausalLM, AutoProcessor
            print("Using memory-optimized loading for Apple Silicon...")
            model = AutoModelForCausalLM.from_pretrained(
                "microsoft/Phi-3.5-vision-instruct", 
                trust_remote_code=True,
                torch_dtype=torch.float16,
                _attn_implementation="eager",  # Disable FlashAttention2
                device_map="cpu",  # Force CPU to avoid memory issues
                low_cpu_mem_usage=True  # Use less CPU memory
            )
            processor = AutoProcessor.from_pretrained("microsoft/Phi-3.5-vision-instruct", trust_remote_code=True)
            return model, processor
            
        except Exception as e:
            print(f"MLX loading failed: {str(e)}")
            print("Falling back to original transformers approach...")
            
            # Fallback to original approach
            from transformers import AutoModelForCausalLM, AutoProcessor
            print("Using memory-optimized loading for Apple Silicon...")
            model = AutoModelForCausalLM.from_pretrained(
                "microsoft/Phi-3.5-vision-instruct", 
                trust_remote_code=True,
                torch_dtype=torch.float16,
                _attn_implementation="eager",  # Disable FlashAttention2
                device_map="cpu",  # Force CPU to avoid memory issues
                low_cpu_mem_usage=True  # Use less CPU memory
            )
            processor = AutoProcessor.from_pretrained("microsoft/Phi-3.5-vision-instruct", trust_remote_code=True)
            return model, processor

class VLMTester:
    """VLM 測試器"""
    
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
        
        # 測試模型配置
        self.models_config = {
            "SmolVLM2-500M-Video-Instruct": {
                "loader": VLMModelLoader.load_smolvlm2_video,
                "model_id": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            },
            "SmolVLM-500M-Instruct": {
                "loader": VLMModelLoader.load_smolvlm_instruct,
                "model_id": "HuggingFaceTB/SmolVLM-500M-Instruct"
            },
            "Moondream2": {
                "loader": VLMModelLoader.load_moondream2,
                "model_id": "vikhyatk/moondream2"
            },
            "LLaVA-v1.6-Mistral-7B-MLX": {
                "loader": VLMModelLoader.load_llava_mlx,
                "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), requires 'pip install mlx-vlm'"
            },
            "Phi-3.5-Vision-Instruct": {
                "loader": VLMModelLoader.load_phi3_vision,
                "model_id": "lokinfey/Phi-3.5-vision-mlx-int4",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), requires 'pip install mlx-vlm'"
            }
        }
        
        # 📏 統一測試條件
        self.prompt = "Describe what you see in this image in detail."
        self.unified_max_tokens = 100  # 統一生成長度
        self.unified_image_size = 1024  # 統一圖像最大尺寸
    
    def get_test_images(self):
        """獲取測試圖像列表"""
        # 支援從不同目錄執行程式
        possible_paths = [
            Path("src/testing/testing_material/images"),  # 從專案根目錄執行
            Path("testing_material/images"),              # 從 src/testing 目錄執行
            Path("./testing_material/images")             # 當前目錄
        ]
        
        images_dir = None
        for path in possible_paths:
            if path.exists():
                images_dir = path
                break
        
        if images_dir is None:
            print(f"警告：圖像資料夾不存在，嘗試了以下路徑：")
            for path in possible_paths:
                print(f"  {path}")
            return []
        
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(images_dir.glob(ext))
            image_files.extend(images_dir.glob(ext.upper()))
        
        return sorted(image_files)
    
    def test_single_model(self, model_name, config):
        """測試單一模型"""
        print(f"\n{'='*50}")
        print(f"開始測試模型: {model_name}")
        print(f"{'='*50}")
        
        # 記錄載入前記憶體
        memory_before = get_memory_usage()
        print(f"載入前記憶體使用: {memory_before:.2f} GB")
        
        # 載入模型
        start_time = time.time()
        try:
            model, processor = config["loader"]()
            load_time = time.time() - start_time
            
            # 記錄載入後記憶體
            memory_after = get_memory_usage()
            print(f"載入後記憶體使用: {memory_after:.2f} GB")
            print(f"模型載入時間: {load_time:.2f} 秒")
            
            # 初始化模型結果
            model_results = {
                "model_id": config["model_id"],
                "load_time": load_time,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_diff": memory_after - memory_before,
                "images": {},
                "total_inference_time": 0,
                "successful_inferences": 0,
                "failed_inferences": 0
            }
            
            # 獲取測試圖像
            test_images = self.get_test_images()
            if not test_images:
                print("警告：沒有找到測試圖像")
                model_results["error"] = "No test images found"
                return model_results
            
            print(f"找到 {len(test_images)} 張測試圖像")
            
            # 測試每張圖像
            for image_path in test_images:
                try:
                    image_result = self.test_single_image(model, processor, image_path, model_name)
                    model_results["images"][image_path.name] = image_result
                    
                    # 💡 FIX: Improved failure detection for more accurate reporting
                    is_failure = image_result.get("error") is not None or \
                                 ("inference failed" in image_result.get("response", "").lower())
                    
                    if not is_failure:
                        model_results["successful_inferences"] += 1
                        model_results["total_inference_time"] += image_result["inference_time"]
                    else:
                        model_results["failed_inferences"] += 1
                        
                except Exception as e:
                    print(f"測試圖像 {image_path.name} 時發生錯誤: {str(e)}")
                    model_results["images"][image_path.name] = {
                        "error": str(e),
                        "inference_time": 0
                    }
                    model_results["failed_inferences"] += 1
            
            # 計算平均推理時間
            if model_results["successful_inferences"] > 0:
                model_results["avg_inference_time"] = model_results["total_inference_time"] / model_results["successful_inferences"]
            else:
                model_results["avg_inference_time"] = 0
                
            print(f"模型 {model_name} 測試完成")
            print(f"成功: {model_results['successful_inferences']}, 失敗: {model_results['failed_inferences']}")
            print(f"平均推理時間: {model_results['avg_inference_time']:.2f} 秒")
            
        except Exception as e:
            print(f"載入模型 {model_name} 時發生錯誤: {str(e)}")
            model_results = {
                "model_id": config["model_id"],
                "load_error": str(e),
                "memory_before": memory_before,
                "memory_after": memory_before,  # 載入失敗，記憶體無變化
                "memory_diff": 0
            }
            
            # 清理記憶體（即使載入失敗也要清理）
            gc.collect()
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            
            return model_results
        
        # 清理模型記憶體
        clear_model_memory(model, processor)
        
        # 檢查記憶體清理效果
        memory_after_cleanup = get_memory_usage()
        print(f"清理後記憶體使用: {memory_after_cleanup:.2f} GB")
        model_results["memory_after_cleanup"] = memory_after_cleanup
        
        return model_results
    
    def test_single_image(self, model, processor, image_path, model_name):
        """測試單張圖像（包含優化的超時機制）"""
        print(f"測試圖像: {image_path.name}")
        
        temp_image_path_for_fix = None
        try:
            # 載入並優化圖像
            image = Image.open(image_path).convert('RGB')
            
            # 根據需要，設定當前推理應使用的圖像路徑
            current_image_path = str(image_path)
            
            # 📏 統一圖像預處理（所有模型一致）
            original_size = image.size
            if max(image.size) > self.unified_image_size:
                ratio = self.unified_image_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"  📏 統一縮放: {original_size} → {image.size}")
            
            image_info = {
                "original_size": original_size,
                "processed_size": image.size,
                "mode": image.mode,
                "file_size": os.path.getsize(current_image_path)
            }
            
            # 📏 統一生成參數（所有模型一致）
            unified_generation_params = {
                "max_new_tokens": self.unified_max_tokens,
                "do_sample": False
            }
            
            # ⏱️ Adjust timeout based on model technical characteristics (does not affect comparison fairness)
            def get_timeout(model_name):
                if "LLaVA" in model_name:
                    return 180  # CPU inference needs more time
                elif "Phi-3.5" in model_name:
                    return 180  # Give more time for both MLX and fallback transformers
                else:
                    return 60   # Small models fast inference
            
            timeout_seconds = get_timeout(model_name)
            print(f"  📏 統一參數: {unified_generation_params}")
            print(f"  ⏱️ 超時設定: {timeout_seconds}秒")
            
            # 定義推理函數
            def do_inference():
                # 根據模型類型使用不同的推理方式
                if "Moondream2" in model_name:
                    # Moondream2 特殊 API（模型限制，但保持統一測試條件）
                    # 先將圖像移動到正確的設備
                    device = next(model.parameters()).device
                    enc_image = model.encode_image(image)
                    if hasattr(enc_image, 'to'):
                        enc_image = enc_image.to(device)
                    # 使用統一提示詞，但無法控制 max_tokens（API 限制）
                    return model.answer_question(enc_image, self.prompt, processor)
                elif "Phi-3.5" in model_name:
                    # Check if this is an MLX model or transformers model
                    try:
                        # Use MLX inference - it's much faster than transformers
                        
                        # Try MLX inference first
                        from mlx_vlm import generate
                        print("  🚀 Using MLX inference for Phi-3.5-Vision...")
                        
                        # Try simpler prompt format that works better with quantized models
                        mlx_prompt = f"<|image_1|>\\nUser: {self.prompt}\\nAssistant:"
                        response = generate(
                            model=model, 
                            processor=processor, 
                            image=current_image_path, 
                            prompt=mlx_prompt,
                            max_tokens=unified_generation_params["max_new_tokens"],
                            temp=0.7,  # Increase temperature for more diverse output
                            repetition_penalty=1.2,  # Stronger repetition penalty
                            top_p=0.9,  # Add nucleus sampling
                            verbose=False  # Reduce MLX verbosity
                        )
                        
                        # Handle MLX response format (might be tuple with text and metadata)
                        if isinstance(response, tuple) and len(response) >= 2:
                            # MLX returns (text, metadata_dict) - extract just the text
                            text_response = response[0]
                        elif isinstance(response, list) and len(response) > 0:
                            # Extract just the text part if it's a list
                            text_response = response[0] if isinstance(response[0], str) else str(response[0])
                        else:
                            text_response = str(response)
                        
                        # Clean up repetitive tokens and unwanted text
                        text_response = text_response.replace("<|end|><|endoftext|>", " ").replace("<|end|>", " ").replace("<|endoftext|>", " ")
                        # Remove any trailing questions that might be part of the model's training data
                        if "1. What is meant by" in text_response:
                            text_response = text_response.split("1. What is meant by")[0].strip()
                        text_response = ' '.join(text_response.split())  # Clean up whitespace
                        
                        return text_response
                        
                    except (ImportError, AttributeError, TypeError, Exception) as e:
                        print(f"  ⚠️ MLX inference failed ({e}), loading transformers model...")
                        
                        # Load transformers model for fallback (MLX model can't be used with transformers)
                        from transformers import AutoModelForCausalLM, AutoProcessor
                        print("  📥 Loading transformers Phi-3.5-Vision for fallback...")
                        
                        fallback_model = AutoModelForCausalLM.from_pretrained(
                            "microsoft/Phi-3.5-vision-instruct", 
                            trust_remote_code=True,
                            torch_dtype=torch.float16,
                            _attn_implementation="eager",  # Disable FlashAttention2
                            device_map="cpu",  # Force CPU to avoid memory issues
                            low_cpu_mem_usage=True  # Use less CPU memory
                        )
                        fallback_processor = AutoProcessor.from_pretrained("microsoft/Phi-3.5-vision-instruct", trust_remote_code=True)
                        
                        # Phi-3.5 Vision special format (model compatibility requirement)
                        messages = [
                            {"role": "user", "content": f"<|image_1|>\\n{self.prompt}"}
                        ]
                        
                        prompt = fallback_processor.tokenizer.apply_chat_template(
                            messages, 
                            tokenize=False, 
                            add_generation_prompt=True
                        )
                        
                        inputs = fallback_processor(prompt, [image], return_tensors="pt")
                        
                        # Move to correct device
                        device = next(fallback_model.parameters()).device
                        inputs = {k: v.to(device) for k, v in inputs.items()}
                        
                        # Technical fix: avoid DynamicCache error
                        with torch.no_grad():
                            outputs = fallback_model.generate(
                                **inputs, 
                                **unified_generation_params,  # Use unified parameters
                                use_cache=False,  # Disable cache to avoid DynamicCache error
                                pad_token_id=fallback_processor.tokenizer.eos_token_id
                            )
                        
                        result = fallback_processor.decode(outputs[0], skip_special_tokens=True)
                        
                        # Clean up fallback model
                        del fallback_model, fallback_processor
                        gc.collect()
                        if torch.backends.mps.is_available():
                            torch.mps.empty_cache()
                        
                        return result
                elif "LLaVA" in model_name:
                    # Check if this is MLX-LLaVA or standard LLaVA
                    if "MLX" in model_name:
                        # MLX-LLaVA inference
                        try:
                            from mlx_vlm import generate
                            print("  🚀 Using MLX-VLM for LLaVA...")
                            # Simple prompt for MLX-LLaVA
                            response = generate(
                                model, 
                                processor, 
                                self.prompt, 
                                image=current_image_path,
                                max_tokens=unified_generation_params["max_new_tokens"],
                                verbose=False
                            )
                            
                            # Handle MLX-VLM response format (tuple with text and metadata)
                            if isinstance(response, tuple) and len(response) >= 1:
                                # Extract just the text part
                                text_response = response[0] if response[0] else ""
                            else:
                                text_response = str(response) if response else ""
                            
                            return text_response
                        except Exception as e:
                            print(f"  ⚠️ MLX-VLM failed: {e}")
                            # Fallback: Return descriptive error but don't crash
                            return f"MLX-VLM inference failed: {str(e)}"
                    else:
                        # Standard LLaVA Pipeline 方式
                        messages = [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "image", "image": image},  # 使用本地圖像格式（與 SmolVLM 一致）
                                    {"type": "text", "text": self.prompt}  # 使用統一提示詞
                                ]
                            },
                        ]
                        # 🚀 優化：添加生成參數控制
                        response = model(
                            text=messages, 
                            **unified_generation_params,  # 使用統一參數
                            return_full_text=False  # 只返回生成部分
                        )
                        if isinstance(response, list) and len(response) > 0:
                            return response[0].get('generated_text', str(response))
                        else:
                            return str(response)
                elif "SmolVLM" in model_name:
                    # SmolVLM 優化方式
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "image", "image": image},
                                {"type": "text", "text": self.prompt}
                            ]
                        }
                    ]
                    input_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    inputs = processor(text=input_text, images=image, return_tensors="pt")
                    with torch.no_grad():
                        outputs = model.generate(**inputs, **unified_generation_params)  # 使用統一參數
                    return processor.decode(outputs[0], skip_special_tokens=True)
                else:
                    # 傳統方式
                    inputs = processor(text=self.prompt, images=image, return_tensors="pt")
                    with torch.no_grad():
                        outputs = model.generate(**inputs, **unified_generation_params)  # 使用統一參數
                    return processor.decode(outputs[0], skip_special_tokens=True)
            
            # ⏱️ 執行帶超時的推理
            start_time = time.time()
            try:
                response_text = run_with_timeout(do_inference, timeout_seconds=timeout_seconds)
                if response_text is None:
                    response_text = ""
                    
                inference_time = time.time() - start_time
                
                # 💡 FIX: Properly separate successful responses from error messages
                error_message = None
                final_response = response_text
                if "inference failed" in response_text.lower():
                    error_message = response_text
                    final_response = ""  # Response should be empty on error
                    print(f"  ❌ Detected inference failure: {error_message}")

                result = {
                    "inference_time": inference_time,
                    "response": final_response,
                    "image_info": image_info,
                    "error": error_message,  # Correctly populate the error field
                    "unified_test": True,
                    "generation_params": unified_generation_params,
                    "timeout_used": timeout_seconds
                }
                
                print(f"  ✅ 推理時間: {inference_time:.2f} 秒")
                print(f"  📝 回應長度: {len(final_response)} 字元")
                
                return result
                
            except TimeoutError as e:
                inference_time = time.time() - start_time
                print(f"  ⚠️ {str(e)}")
                return {
                    "inference_time": inference_time,
                    "response": "",
                    "image_info": image_info,
                    "error": str(e),
                    "unified_test": True  # 標記使用統一測試條件
                }
            
        except Exception as e:
            print(f"  ❌ 錯誤: {str(e)}")
            return {
                "inference_time": 0,
                "response": "",
                "image_info": {},
                "error": str(e),
                "unified_test": True  # 標記使用統一測試條件（即使失敗）
            }
        finally:
            # 清理臨時文件（如果存在）
            if temp_image_path_for_fix:
                os.remove(temp_image_path_for_fix)
    
    def run_all_tests(self):
        """執行所有模型的測試"""
        print("開始 VLM 模型測試")
        print(f"系統資訊: MacBook Air M3, 16GB")
        print(f"MPS 可用: {torch.backends.mps.is_available()}")
        
        # 檢查測試圖像
        test_images = self.get_test_images()
        print(f"找到 {len(test_images)} 張測試圖像")
        
        if not test_images:
            print("錯誤：沒有找到測試圖像，請將圖像放置於 src/testing/testing_material/images/")
            return
        
        total_start_time = time.time()
        
        # 逐一測試每個模型
        for model_name, config in self.models_config.items():
            try:
                model_results = self.test_single_model(model_name, config)
                self.results["models"][model_name] = model_results
                
                # 儲存中間結果（防止測試中斷丟失數據）
                self.save_results(f"intermediate_{model_name}")
                
            except Exception as e:
                print(f"測試模型 {model_name} 時發生嚴重錯誤: {str(e)}")
                self.results["models"][model_name] = {
                    "severe_error": str(e)
                }
        
        # 記錄總測試時間
        total_time = time.time() - total_start_time
        self.results["total_test_time"] = total_time
        print(f"\n所有測試完成，總時間: {total_time:.2f} 秒")
        
        # 儲存最終結果
        self.save_results()
    
    def save_results(self, suffix=""):
        """儲存測試結果"""
        # 支援從不同目錄執行程式
        possible_results_dirs = [
            Path("src/testing/results"),  # 從專案根目錄執行
            Path("results"),              # 從 src/testing 目錄執行
            Path("./results")             # 當前目錄
        ]
        
        # 使用第一個可行的路徑，如果都不存在則創建第二個
        results_dir = possible_results_dirs[1] if Path("testing_material").exists() else possible_results_dirs[0]
        results_dir.mkdir(parents=True, exist_ok=True)
        
        if suffix:
            filename = f"test_results_{suffix}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        filepath = results_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"結果已儲存至: {filepath}")
        except Exception as e:
            print(f"儲存結果時發生錯誤: {str(e)}")

def main():
    """主函數"""
    print("VLM 模型測試程式")
    print("="*50)
    
    # 檢查虛擬環境
    activate_virtual_env()
    
    # 建立測試器
    tester = VLMTester()
    
    # 檢查命令行參數是否要測試單一模型
    import sys
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        if model_name in tester.models_config:
            print(f"測試單一模型: {model_name}")
            model_results = tester.test_single_model(model_name, tester.models_config[model_name])
            tester.results["models"][model_name] = model_results
            tester.save_results(f"single_{model_name}")
        else:
            print(f"錯誤：找不到模型 {model_name}")
            print(f"可用的模型：{list(tester.models_config.keys())}")
            return
    else:
        # 執行所有模型測試
        tester.run_all_tests()
    
    print("\n測試完成！")
    print("結果文件位於: src/testing/results/")

if __name__ == "__main__":
    main() 