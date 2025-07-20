#!/usr/bin/env python3
"""
VLM 模型測試程式
MacBook Air M3 (16GB) 優化版本 - 逐一載入模型避免記憶體溢出
"""

import os
import sys
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
    def load_smolvlm2_video(model_id="mlx-community/SmolVLM2-500M-Video-Instruct-mlx"):
        """載入 SmolVLM2-500M-Video-Instruct (優先使用 MLX 版本)"""
        print(f"載入 SmolVLM2-500M-Video-Instruct (優先使用 MLX 版本)...")
        
        try:
            # 首先嘗試使用 MLX-VLM 框架（與 vlm_context_tester.py 相同的方法）
            from mlx_vlm import load
            print("正在載入 MLX-VLM 優化的 SmolVLM2 模型...")
            model, processor = load(model_id)
            print("MLX-VLM SmolVLM2 載入成功!")
            
            # 標記為 MLX 模型，使用特殊的推理方式
            model._is_mlx_model = True
            
            return model, processor
            
        except ImportError as e:
            print("MLX-VLM 未安裝，使用原始 SmolVLM2 模型...")
            print("請運行: pip install mlx-vlm")
            # 回退到原始 SmolVLM2 模型
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            return model, processor
            
        except Exception as e:
            print(f"MLX-VLM 載入失敗: {str(e)}")
            print("使用原始 SmolVLM2 模型作為回退...")
            # 回退到原始 SmolVLM2 模型
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            return model, processor
    
    @staticmethod
    def load_smolvlm2_video_mlx(model_id="mlx-community/SmolVLM2-500M-Video-Instruct-mlx"):
        """載入 MLX 優化的 SmolVLM2-500M-Video-Instruct"""
        print(f"載入 MLX 優化的 {model_id}...")
        try:
            # 首先嘗試使用 MLX-VLM 框架
            from mlx_vlm import load
            print("正在載入 MLX-VLM 優化的 SmolVLM2 模型...")
            model, processor = load(model_id)
            print("MLX-VLM SmolVLM2 載入成功!")
            
            # 標記為 MLX 模型，使用特殊的推理方式
            model._is_mlx_model = True
            
            return model, processor
            
        except ImportError as e:
            print("MLX-VLM 未安裝，使用原始 SmolVLM2 模型...")
            print("請運行: pip install mlx-vlm")
            # 回退到原始 SmolVLM2 模型
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            return model, processor
            
        except Exception as e:
            print(f"MLX-VLM 載入失敗: {str(e)}")
            print("使用原始 SmolVLM2 模型作為回退...")
            # 回退到原始 SmolVLM2 模型
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
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
    def load_phi3_vision(model_id="mlx-community/Phi-3.5-vision-instruct-4bit"):
        """Load Phi-3.5-Vision-Instruct using MLX-VLM framework (Apple Silicon optimized)"""
        print(f"Loading {model_id} with MLX-VLM framework...")
        try:
            # Use MLX-VLM for Apple Silicon optimization (supports vision)
            from mlx_vlm import load
            
            print("Loading MLX-VLM optimized Phi-3.5-Vision-Instruct model...")
            model, processor = load(model_id, trust_remote_code=True)
            print("MLX-VLM model loaded successfully!")
            
            return model, processor
            
        except ImportError as e:
            print("MLX-VLM not installed. Please install MLX-VLM...")
            print("Please run: pip install mlx-vlm")
            print("Falling back to original transformers approach...")
            
            # Fallback to original approach if MLX-VLM not available
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
            processor = AutoProcessor.from_pretrained(
                "microsoft/Phi-3.5-vision-instruct", 
                trust_remote_code=True,
                num_crops=4  # For single-frame images
            )
            return model, processor
            
        except Exception as e:
            print(f"MLX-VLM loading failed: {str(e)}")
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
            processor = AutoProcessor.from_pretrained(
                "microsoft/Phi-3.5-vision-instruct", 
                trust_remote_code=True,
                num_crops=4  # For single-frame images
            )
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
                "model_id": "mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), falls back to original SmolVLM2 if MLX not available or incompatible"
            },
            "SmolVLM2-500M-Video-Instruct-MLX": {
                "loader": VLMModelLoader.load_smolvlm2_video_mlx,
                "model_id": "mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), falls back to original SmolVLM2 if MLX-VLM not available or incompatible"
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
                "model_id": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), requires 'pip install mlx-vlm'"
            }
        }
        
        # 📏 統一測試條件
        self.prompt = "Describe what you see in this image in detail."
        self.unified_max_tokens = 100  # 統一生成長度
        self.unified_image_size = 1024  # 統一圖像最大尺寸
        
        # 💡 純文字測試配置
        self.enable_text_only_test = True  # 是否啟用純文字測試
    
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
                    # For LLaVA-MLX, reload the model for each image to avoid state bug
                    if "LLaVA-v1.6-Mistral-7B-MLX" in model_name:
                        print("  >> LLaVA-MLX: Reloading model to clear state...")
                        clear_model_memory(model, processor)
                        model, processor = config["loader"]()

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
                
            print(f"模型 {model_name} 圖像測試完成")
            print(f"成功: {model_results['successful_inferences']}, 失敗: {model_results['failed_inferences']}")
            print(f"平均推理時間: {model_results['avg_inference_time']:.2f} 秒")
            
            # 💡 新增：純文字能力測試（可選）
            if self.enable_text_only_test:
                print(f"\n開始測試 {model_name} 純文字能力...")
                try:
                    text_only_results = self.test_text_only_capability(model, processor, model_name)
                    model_results["text_only_capability"] = text_only_results
                    
                    if text_only_results["text_only_supported"]:
                        print(f"✅ {model_name} 支援純文字輸入!")
                    else:
                        print(f"❌ {model_name} 不支援純文字輸入")
                        
                except Exception as e:
                    print(f"⚠️ 純文字測試發生錯誤: {str(e)}")
                    model_results["text_only_capability"] = {
                        "text_only_supported": False,
                        "error": str(e)
                    }
            else:
                print(f"\n跳過純文字測試（已停用）")
                model_results["text_only_capability"] = {
                    "text_only_supported": "未測試",
                    "reason": "純文字測試已停用"
                }
            
            print(f"\n模型 {model_name} 所有測試完成")
            
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
        if model_name != "LLaVA-v1.6-Mistral-7B-MLX": # Already cleaned inside loop
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
                    # Check if this is an MLX-VLM model or transformers model
                    try:
                        # Use MLX-VLM inference for vision model (official way)
                        from mlx_vlm import generate
                        print("  🚀 Using MLX-VLM inference for Phi-3.5-Vision-Instruct...")
                        
                        # Save image to temporary file for MLX-VLM
                        temp_image_path = "temp_mlx_image.jpg"
                        image.save(temp_image_path)
                        
                        try:
                            # Use simple prompt format for MLX-VLM (same as vlm_context_tester.py)
                            mlx_prompt = f"<|image_1|>\nUser: {self.prompt}\nAssistant:"
                            
                            response = generate(
                                model, 
                                processor, 
                                mlx_prompt,
                                image=temp_image_path,
                                max_tokens=unified_generation_params["max_new_tokens"],
                                temp=0.0,  # Use 0.0 for deterministic output
                                verbose=False
                            )
                        finally:
                            # Clean up temporary file
                            if os.path.exists(temp_image_path):
                                os.remove(temp_image_path)
                        
                        # MLX-VLM returns string directly, not tuple
                        text_response = str(response)
                        
                        # Clean up response
                        text_response = text_response.replace("<|end|><|endoftext|>", " ").replace("<|end|>", " ").replace("<|endoftext|>", " ")
                        if "1. What is meant by" in text_response:
                            text_response = text_response.split("1. What is meant by")[0].strip()
                        text_response = ' '.join(text_response.split())
                        
                        return text_response
                        
                    except (ImportError, AttributeError, TypeError, Exception) as e:
                        print(f"  ⚠️ MLX-VLM inference failed ({e}), loading transformers model...")
                        
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
                        fallback_processor = AutoProcessor.from_pretrained(
                            "microsoft/Phi-3.5-vision-instruct", 
                            trust_remote_code=True,
                            num_crops=4  # For single-frame images
                        )
                        
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
                            
                            # MLX-VLM returns string directly, not tuple
                            text_response = str(response)
                            
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
                    if "MLX" in model_name or hasattr(model, '_is_mlx_model'):
                        # MLX 版本的 SmolVLM2 推理
                        try:
                            # 使用 MLX-VLM 的命令行工具進行推理
                            import subprocess
                            import tempfile
                            
                            print("  🚀 Using MLX-VLM command line for SmolVLM2...")
                            
                            # 創建臨時圖像文件
                            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                                temp_image_path = tmp_file.name
                                image.save(temp_image_path)
                            
                            try:
                                # 使用 MLX-VLM 命令行工具
                                cmd = [
                                    sys.executable, '-m', 'mlx_vlm.generate',
                                    '--model', 'mlx-community/SmolVLM2-500M-Video-Instruct-mlx',
                                    '--image', temp_image_path,
                                    '--prompt', self.prompt,
                                    '--max-tokens', str(unified_generation_params["max_new_tokens"]),
                                    '--temperature', '0.0'
                                ]
                                
                                result = subprocess.run(
                                    cmd,
                                    capture_output=True,
                                    text=True,
                                    timeout=timeout_seconds
                                )
                                
                                if result.returncode == 0:
                                    # 解析輸出，提取生成的文本
                                    output_lines = result.stdout.split('\n')
                                    generated_text = ""
                                    
                                    # 保留完整的 Assistant 回覆
                                    generated_text = ""
                                    assistant_found = False
                                    for i, line in enumerate(output_lines):
                                        line = line.strip()
                                        if line.startswith('Assistant:'):
                                            # 找到 Assistant 行
                                            assistant_found = True
                                            generated_text = line
                                            # 檢查下一行是否有內容
                                            if i + 1 < len(output_lines):
                                                next_line = output_lines[i + 1].strip()
                                                if next_line and not next_line.startswith('==========') and not next_line.startswith('Files:') and not next_line.startswith('Prompt:') and not next_line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
                                                    # 下一行有內容，組合兩行
                                                    generated_text = f"{line} {next_line}"
                                            break
                                        elif line and not line.startswith('==========') and not line.startswith('Files:') and not line.startswith('Prompt:') and not line.startswith('Generation:') and not line.startswith('Peak memory:'):
                                            # 找到其他非系統信息的內容行
                                            if not generated_text:
                                                generated_text = line
                                    
                                    return generated_text
                                else:
                                    print(f"  ⚠️ MLX-VLM command failed: {result.stderr}")
                                    raise Exception(f"MLX-VLM command failed: {result.stderr}")
                                    
                            finally:
                                # 清理臨時文件
                                if os.path.exists(temp_image_path):
                                    os.remove(temp_image_path)
                            
                        except Exception as e:
                            print(f"  ⚠️ MLX-VLM SmolVLM2 inference failed: {e}")
                            # Fallback to standard SmolVLM method
                            print("  📥 Falling back to standard SmolVLM method...")
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
                                outputs = model.generate(**inputs, **unified_generation_params)
                            return processor.decode(outputs[0], skip_special_tokens=True)
                    else:
                        # 標準 SmolVLM 推理方式
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
    
    def test_text_only_capability(self, model, processor, model_name):
        """測試模型是否支援純文字輸入（不需要圖片）- 支援所有模型"""
        print(f"測試 {model_name} 純文字能力...")
        
        # 純文字測試提示
        text_only_prompts = [
            "What is the capital of France?",
            "Explain the concept of machine learning in simple terms.",
            "Write a short poem about technology."
        ]
        
        results = {}
        
        for i, prompt in enumerate(text_only_prompts):
            print(f"  測試提示 {i+1}: {prompt}")
            
            try:
                start_time = time.time()
                response = ""
                
                # 🔧 根據模型類型使用專門的純文字推理方式
                if "Moondream2" in model_name:
                    response = self._test_moondream2_text_only(model, processor, prompt)
                elif "Phi-3.5" in model_name:
                    response = self._test_phi35_text_only(model, processor, prompt)
                elif "SmolVLM2" in model_name:
                    response = self._test_smolvlm2_text_only(model, processor, prompt)
                elif "SmolVLM" in model_name:
                    response = self._test_smolvlm_text_only(model, processor, prompt)
                elif "LLaVA" in model_name:
                    response = self._test_llava_text_only(model, processor, prompt)
                else:
                    response = self._test_generic_text_only(model, processor, prompt)
                
                inference_time = time.time() - start_time
                
                # 判斷成功與否
                is_success = (
                    response and 
                    len(response.strip()) > 0 and 
                    "失敗" not in response and 
                    "failed" not in response.lower() and
                    "error" not in response.lower() and
                    "不支援" not in response
                )
                
                results[f"prompt_{i+1}"] = {
                    "prompt": prompt,
                    "response": response,
                    "inference_time": inference_time,
                    "success": is_success
                }
                
                print(f"    回應: {response[:100]}...")
                print(f"    時間: {inference_time:.2f}秒")
                print(f"    狀態: {'✅ 成功' if is_success else '❌ 失敗'}")
                
            except Exception as e:
                results[f"prompt_{i+1}"] = {
                    "prompt": prompt,
                    "response": "",
                    "inference_time": 0,
                    "error": str(e),
                    "success": False
                }
                print(f"    錯誤: {str(e)}")
        
        # 計算成功率
        successful_tests = sum(1 for r in results.values() if r.get("success", False))
        total_tests = len(results)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        print(f"  純文字測試成功率: {successful_tests}/{total_tests} ({success_rate:.1%})")
        
        return {
            "text_only_supported": success_rate > 0,  # 任何成功都視為支援
            "success_rate": success_rate,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "results": results
        }
    
    def _test_moondream2_text_only(self, model, processor, prompt):
        """Moondream2 純文字測試"""
        try:
            # 方法1: 直接使用 tokenizer 進行純文字生成
            inputs = processor(prompt, return_tensors="pt")
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=self.unified_max_tokens,
                    do_sample=False,
                    pad_token_id=processor.eos_token_id
                )
            
            response = processor.decode(outputs[0], skip_special_tokens=True)
            
            # 移除原始提示，只保留生成的部分
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            return response
            
        except Exception as e:
            # 方法2: 嘗試使用模型的 chat 功能（如果有）
            try:
                # 某些版本的 Moondream2 可能支援純文字對話
                device = next(model.parameters()).device
                inputs = processor(prompt, return_tensors="pt").to(device)
                
                with torch.no_grad():
                    outputs = model.generate(
                        inputs.input_ids,
                        max_new_tokens=self.unified_max_tokens,
                        do_sample=False,
                        pad_token_id=processor.eos_token_id
                    )
                
                response = processor.decode(outputs[0], skip_special_tokens=True)
                return response.replace(prompt, "").strip()
                
            except Exception as e2:
                return f"Moondream2 純文字推理失敗: {str(e)} | 備用方法: {str(e2)}"
    
    def _test_phi35_text_only(self, model, processor, prompt):
        """Phi-3.5-Vision-Instruct 純文字測試"""
        try:
            # 使用 MLX-VLM 進行純文字推理（簡化方式）
            try:
                from mlx_vlm import generate
                print("  🚀 Using MLX-VLM for Phi-3.5-Vision-Instruct text-only...")
                
                # Generate text output - use simple prompt for text-only
                response = generate(
                    model,
                    processor,
                    prompt,  # Use simple string prompt
                    max_tokens=self.unified_max_tokens,
                    temp=0.0,
                    verbose=False
                )
                return str(response)
                
            except Exception as mlx_e:
                return f"MLX-VLM 純文字推理失敗: {str(mlx_e)}"
            
        except Exception as e:
            return f"Phi-3.5-Vision-Instruct 純文字推理失敗: {str(e)}"
    
    def _test_smolvlm2_text_only(self, model, processor, prompt):
        """SmolVLM2-500M-Video 純文字測試"""
        try:
            # 檢查是否為 MLX 版本
            if hasattr(model, '_is_mlx_model'):
                # MLX 版本的純文字測試
                try:
                    import subprocess
                    import tempfile
                    
                    print("  🚀 Using MLX-VLM command line for SmolVLM2 text-only...")
                    
                    # 創建一個簡單的測試圖像（MLX-VLM 需要圖像輸入）
                    from PIL import Image
                    test_image = Image.new('RGB', (224, 224), color='white')
                    
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                        temp_image_path = tmp_file.name
                        test_image.save(temp_image_path)
                    
                    try:
                        # 使用 MLX-VLM 命令行工具進行純文字測試
                        cmd = [
                            sys.executable, '-m', 'mlx_vlm.generate',
                            '--model', 'mlx-community/SmolVLM2-500M-Video-Instruct-mlx',
                            '--image', temp_image_path,
                            '--prompt', prompt,
                            '--max-tokens', str(self.unified_max_tokens),
                            '--temperature', '0.0'
                        ]
                        
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        
                        if result.returncode == 0:
                            # 保留完整的 Assistant 回覆
                            output_lines = result.stdout.split('\n')
                            generated_text = ""
                            
                            for i, line in enumerate(output_lines):
                                line = line.strip()
                                if line.startswith('Assistant:'):
                                    # 找到 Assistant 行
                                    generated_text = line
                                    # 檢查下一行是否有內容
                                    if i + 1 < len(output_lines):
                                        next_line = output_lines[i + 1].strip()
                                        if next_line and not next_line.startswith('==========') and not next_line.startswith('Files:') and not next_line.startswith('Prompt:') and not next_line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
                                            # 下一行有內容，組合兩行
                                            generated_text = f"{line} {next_line}"
                                    break
                                elif line and not line.startswith('==========') and not line.startswith('Files:') and not line.startswith('Prompt:') and not line.startswith('Generation:') and not line.startswith('Peak memory:'):
                                    # 找到其他非系統信息的內容行
                                    if not generated_text:
                                        generated_text = line
                            
                            return generated_text
                        else:
                            return f"MLX-VLM text-only command failed: {result.stderr}"
                            
                    finally:
                        # 清理臨時文件
                        if os.path.exists(temp_image_path):
                            os.remove(temp_image_path)
                    
                except Exception as mlx_e:
                    print(f"  ⚠️ MLX-VLM text-only failed: {mlx_e}")
                    return f"MLX-VLM 純文字推理失敗: {str(mlx_e)}"
            
            # 標準 SmolVLM2 純文字測試
            # 方法1: 嘗試純文字消息格式
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}  # 只有文字，沒有圖像
                    ]
                }
            ]
            
            input_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=input_text, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=self.unified_max_tokens, do_sample=False)
            
            response = processor.decode(outputs[0], skip_special_tokens=True)
            return response.replace(input_text, "").strip()
            
        except Exception as e:
            # 方法2: 嘗試直接文字輸入
            try:
                inputs = processor(text=prompt, return_tensors="pt")
                with torch.no_grad():
                    outputs = model.generate(**inputs, max_new_tokens=self.unified_max_tokens, do_sample=False)
                response = processor.decode(outputs[0], skip_special_tokens=True)
                return response.replace(prompt, "").strip()
            except Exception as e2:
                return f"SmolVLM2 純文字推理失敗: {str(e)} | 備用方法: {str(e2)}"
    
    def _test_smolvlm_text_only(self, model, processor, prompt):
        """SmolVLM-500M-Instruct 純文字測試"""
        try:
            # 方法1: 嘗試純文字消息格式
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}  # 只有文字，沒有圖像
                    ]
                }
            ]
            
            input_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=input_text, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=self.unified_max_tokens, do_sample=False)
            
            response = processor.decode(outputs[0], skip_special_tokens=True)
            return response.replace(input_text, "").strip()
            
        except Exception as e:
            # 方法2: 嘗試直接文字輸入
            try:
                inputs = processor(text=prompt, return_tensors="pt")
                with torch.no_grad():
                    outputs = model.generate(**inputs, max_new_tokens=self.unified_max_tokens, do_sample=False)
                response = processor.decode(outputs[0], skip_special_tokens=True)
                return response.replace(prompt, "").strip()
            except Exception as e2:
                return f"SmolVLM 純文字推理失敗: {str(e)} | 備用方法: {str(e2)}"
    
    def _test_llava_text_only(self, model, processor, prompt):
        """LLaVA-MLX 純文字測試"""
        try:
            # 方法1: MLX-VLM 純文字推理
            from mlx_vlm import generate
            response = generate(
                model=model,
                processor=processor,
                prompt=prompt,
                max_tokens=self.unified_max_tokens,
                verbose=False
            )
            
            if isinstance(response, tuple) and len(response) >= 1:
                text_response = response[0] if response[0] else ""
            else:
                text_response = str(response) if response else ""
            
            return text_response
            
        except Exception as e:
            # 方法2: 嘗試 pipeline 方式（如果支援）
            try:
                # 嘗試純文字對話格式
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ]
                    },
                ]
                
                response = model(text=messages, max_new_tokens=self.unified_max_tokens, return_full_text=False)
                if isinstance(response, list) and len(response) > 0:
                    return response[0].get('generated_text', str(response))
                else:
                    return str(response)
                    
            except Exception as e2:
                return f"LLaVA 純文字推理失敗: {str(e)} | 備用方法: {str(e2)}"
    
    def _test_generic_text_only(self, model, processor, prompt):
        """通用純文字測試方法"""
        try:
            # 方法1: 嘗試使用 processor 進行純文字處理
            inputs = processor(text=prompt, return_tensors="pt")
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=self.unified_max_tokens,
                    do_sample=False
                )
            
            response = processor.decode(outputs[0], skip_special_tokens=True)
            return response.replace(prompt, "").strip()
            
        except Exception as e:
            # 方法2: 嘗試直接 tokenizer 方式
            try:
                if hasattr(processor, 'tokenizer'):
                    inputs = processor.tokenizer(prompt, return_tensors="pt")
                    device = next(model.parameters()).device
                    inputs = {k: v.to(device) for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        outputs = model.generate(
                            **inputs,
                            max_new_tokens=self.unified_max_tokens,
                            do_sample=False
                        )
                    
                    response = processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    return response.replace(prompt, "").strip()
                else:
                    return f"通用純文字推理失敗: 無法找到適當的 tokenizer"
                    
            except Exception as e2:
                return f"通用純文字推理失敗: {str(e)} | 備用方法: {str(e2)}"
    
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