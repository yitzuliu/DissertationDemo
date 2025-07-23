from pathlib import Path
import sys
import os
import tempfile
import base64
import gc
import torch
from io import BytesIO
from PIL import Image
from typing import Dict, Any, cast, Optional
from transformers.tokenization_utils import PreTrainedTokenizer

# Add project root to path for module imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.models.base_model import BaseVisionModel

class LlavaMlxModel(BaseVisionModel):
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name=model_name, config=config)
        
        # 統一配置鍵名的使用
        self.model_id = (
            self.config.get("model_path") or 
            self.config.get("model_id") or 
            "mlx-community/llava-v1.6-mistral-7b-4bit"
        )
        
        if self.model_id == model_name:
            self.model_id = "mlx-community/llava-v1.6-mistral-7b-4bit"
        
        print(f"🔧 LLaVA MLX Model initialized with model_path: {self.model_id}")
        
        self.model = None
        self.processor = None
        self.loaded = False
        self.stats = {"requests": 0, "total_time": 0.0}
        
        # 添加狀態追蹤 - 參考測試框架的單次推理模式
        self.inference_count = 0
        self.max_inferences_before_reload = 1  # 每次推理後重載模型

    def load_model(self):
        """Load LLaVA MLX model using MLX-VLM framework (參考 vlm_tester.py 的成功實現)"""
        print(f"Loading LLaVA MLX model: {self.model_id}...")
        try:
            from mlx_vlm import load
            print(f"🚀 Using MLX-VLM to load: {self.model_id}")
            
            # 參考 vlm_tester.py 的載入方式
            self.model, self.processor = load(self.model_id)
            self.loaded = True
            print("✅ LLaVA MLX model loaded successfully.")
            return True
        except ImportError as e:
            print(f"❌ MLX-VLM not available: {e}")
            raise RuntimeError("MLX-VLM is not installed. Please run: pip install mlx-vlm")
        except Exception as e:
            print(f"❌ Failed to load LLaVA MLX model: {e}")
            raise RuntimeError(f"Failed to load LLaVA MLX model from {self.model_id}: {e}")

    def predict(self, image: Any, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Predict method for compatibility with BaseVisionModel (參考 vlm_tester.py)"""
        try:
            # 確保輸入圖像是 PIL Image
            if not isinstance(image, Image.Image):
                if hasattr(image, 'shape'):  # numpy array
                    image = Image.fromarray(image)
                else:
                    raise ValueError("Invalid image format")
            
            # 獲取 max_tokens 參數
            max_tokens = 150  # 默認值
            if options and "max_tokens" in options:
                max_tokens = options["max_tokens"]
            
            # 調用 generate_response 方法
            response_text = self.generate_response(image, prompt, max_tokens)
            
            # 確保返回正確的格式
            return {
                "success": True,
                "response": {"text": response_text}
            }
            
        except Exception as e:
            print(f"❌ LLaVA MLX prediction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": {"text": f"Error: {str(e)}"}
            }

    def generate_response(self, image: Image.Image, prompt: str, max_tokens: int = 100) -> str:
        """Generate response with automatic model reloading - 參考測試框架的成功方法"""
        # 檢查是否需要重載模型來避免狀態累積
        if self.inference_count >= self.max_inferences_before_reload:
            print(f"🔄 Reloading model after {self.inference_count} inferences to prevent state issues")
            self.unload_model()
            if not self.load_model():
                return "Failed to reload model"
            self.inference_count = 0
        
        if not self.loaded or self.model is None or self.processor is None:
            if not self.load_model():
                return "Model failed to load"
        
        print(f"Generating response with LLaVA MLX (inference #{self.inference_count + 1})...")
        
        try:
            # 參考測試框架的圖像處理
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 使用測試框架驗證的尺寸處理
            unified_image_size = 1024
            original_size = image.size
            if max(image.size) > unified_image_size:
                ratio = unified_image_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"🔧 Resized image: {original_size} → {new_size}")
            
            # 使用唯一的臨時文件名避免衝突
            import uuid
            temp_image_path = f"temp_mlx_image_{uuid.uuid4().hex[:8]}.jpg"
            
            try:
                # 保存圖像 - 參考測試框架
                image.save(temp_image_path, 'JPEG', quality=95, optimize=True)
                print(f"💾 Saved image to: {temp_image_path}")

                from mlx_vlm import generate
                
                # 使用測試框架驗證的生成參數
                response = generate(
                    model=self.model,
                    processor=self.processor,
                    prompt=prompt,
                    image=temp_image_path,
                    max_tokens=max_tokens,
                    verbose=False
                )

                # 處理響應 - 參考測試框架
                if isinstance(response, tuple) and len(response) >= 1:
                    text_response = response[0] if response[0] else ""
                elif isinstance(response, list) and len(response) > 0:
                    text_response = response[0] if isinstance(response[0], str) else str(response[0])
                else:
                    text_response = str(response) if response else ""
                
                text_response = text_response.strip()
                if not text_response:
                    text_response = "No response generated"
                
                # 增加推理計數
                self.inference_count += 1
                
                print(f"✅ Generated response: {text_response[:100]}...")
                return text_response

            except Exception as e:
                print(f"❌ MLX generation error: {e}")
                # 發生錯誤時立即重載模型
                if "axis remapping" in str(e):
                    print("🔄 Axis remapping error detected - forcing model reload")
                    self.inference_count = self.max_inferences_before_reload
                return f"MLX inference failed: {str(e)}"
                
            finally:
                # 清理臨時文件
                try:
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
                        print(f"🗑️ Cleaned up temp file: {temp_image_path}")
                except Exception as cleanup_error:
                    print(f"⚠️ Warning: Could not clean up temp file: {cleanup_error}")

        except Exception as e:
            print(f"❌ Error during LLaVA MLX inference: {e}")
            # 發生錯誤時標記需要重載
            self.inference_count = self.max_inferences_before_reload
            return f"Inference failed: {str(e)}"

    def clear_cache(self):
        """Enhanced cache clearing with model state reset"""
        if self.model is None:
            return

        try:
            # 更積極的緩存清理
            if hasattr(self.model, 'language_model') and hasattr(self.model.language_model, 'model'):
                layers = self.model.language_model.model.layers
                for layer in layers:
                    if hasattr(layer, "self_attn"):
                        # 清理所有可能的緩存屬性
                        for cache_attr in ["cache", "kv_cache", "_cache", "past_key_values"]:
                            if hasattr(layer.self_attn, cache_attr):
                                delattr(layer.self_attn, cache_attr)
        except Exception as e:
            print(f"Cache clearing error: {e}")
        
        # 強制垃圾回收
        gc.collect()

    def unload_model(self) -> bool:
        """Enhanced model unloading"""
        try:
            # 清理緩存
            self.clear_cache()
            
            # 刪除模型對象
            if self.model is not None:
                del self.model
                self.model = None
            if self.processor is not None:
                del self.processor
                self.processor = None
            
            self.loaded = False
            self.inference_count = 0
            
            # 強制垃圾回收
            gc.collect()
            
            print("🗑️ Model unloaded successfully")
            return True
        except Exception as e:
            print(f"Error unloading LLaVA MLX model: {e}")
            return False

    def process_messages(self, messages):
        """Process messages in the format expected by the API"""
        prompt = "Describe the image."
        image_data_url = None

        user_content = messages[0].get("content", [])
        for item in user_content:
            if item.get("type") == "text":
                prompt = item.get("text", prompt)
            elif item.get("type") == "image_url":
                image_data_url = item["image_url"]["url"]

        if not image_data_url:
            raise ValueError("No image provided in the message content.")
        
        # Manually decode the base64 image data
        if image_data_url.startswith('data:image/'):
            base64_data = image_data_url.split(',')[1]
            image_bytes = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            return image, prompt
        else:
            raise ValueError("Unsupported image URL format. Please use base64 data URI.")

    def preprocess_image(self, image: Any) -> Any:
        """Preprocess image for LLaVA MLX model (unified preprocessing) - 實現抽象方法"""
        # 統一圖像預處理（參考 vlm_tester.py）
        if isinstance(image, Image.Image):
            original_size = image.size
            unified_image_size = 1024
            if max(image.size) > unified_image_size:
                ratio = unified_image_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
        return image
    
    def format_response(self, raw_response: Any) -> Dict[str, Any]:
        """Format response for API compatibility - 實現抽象方法"""
        if isinstance(raw_response, dict):
            return raw_response
        else:
            return {"response": raw_response}

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "model_id": self.model_id,
            "loaded": self.loaded,
            "framework": "MLX-VLM",
            "device": "Apple Silicon (M1/M2/M3)",
            "stats": self.stats
        }

if __name__ == '__main__':
    print("This script is not meant to be run directly. Use a runner script.")