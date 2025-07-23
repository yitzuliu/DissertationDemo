#!/usr/bin/env python3
"""
Unified Model Server

This script provides truly unified model launching and serving without requiring 
separate run scripts for each model. All models are launched and used through 
the same interface.

Usage:
python src/models/unified_model_server.py --model smolvlm2_500m_video_optimized
python src/models/unified_model_server.py --model moondream2_optimized --port 8081
"""

import argparse
import sys
import os
import json
import logging
import time
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, Union

from flask import Flask, request, jsonify
from PIL import Image
import torch

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class UnifiedModelLoader:
    """Unified Model Loader - Uses the same loading approach as testing framework"""
    
    @staticmethod
    def load_smolvlm2_video(model_id="HuggingFaceTB/SmolVLM2-500M-Video-Instruct"):
        """Load SmolVLM2-500M-Video-Instruct"""
        print(f"Loading SmolVLM2-Video {model_id}...")
        
        # 嘗試多種加載方法
        methods_to_try = [
            "causal_lm",
            "auto_model",
            "pipeline",
            "specific_class"
        ]
        
        for method in methods_to_try:
            try:
                if method == "causal_lm":
                    print("Trying AutoModelForCausalLM method...")
                    from transformers import AutoProcessor, AutoModelForCausalLM
                    import torch
                    
                    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                    model = AutoModelForCausalLM.from_pretrained(
                        model_id,
                        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                        device_map="auto" if torch.cuda.is_available() else None,
                        trust_remote_code=True
                    )
                    
                elif method == "auto_model":
                    print("Trying AutoModel method...")
                    from transformers import AutoProcessor, AutoModel
                    import torch
                    
                    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                    model = AutoModel.from_pretrained(
                        model_id,
                        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                        device_map="auto" if torch.cuda.is_available() else None,
                        trust_remote_code=True
                    )
                    
                elif method == "pipeline":
                    print("Trying pipeline method...")
                    from transformers import AutoProcessor, pipeline
                    import torch
                    
                    # 使用 pipeline 方式加載模型
                    pipe = pipeline(
                        "image-to-text",
                        model=model_id,
                        device="mps" if torch.backends.mps.is_available() and not torch.cuda.is_available() else "cuda" if torch.cuda.is_available() else "cpu",
                        trust_remote_code=True
                    )
                    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                    model = pipe.model
                    
                elif method == "specific_class":
                    print("Trying specific model class method...")
                    from transformers import AutoProcessor
                    import torch
                    
                    # 直接從 transformers 導入 SmolVLM 模型類
                    try:
                        from transformers.models.smolvlm.modeling_smolvlm import SmolVLMForConditionalGeneration
                        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                        model = SmolVLMForConditionalGeneration.from_pretrained(
                            model_id,
                            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                            device_map="auto" if torch.cuda.is_available() else None,
                            trust_remote_code=True
                        )
                    except ImportError:
                        # 如果找不到特定類，嘗試從模型文件夾加載
                        print("Specific class not found, trying to load from model folder...")
                        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                        
                        # 使用 AutoConfig 獲取模型類型
                        from transformers import AutoConfig
                        config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
                        model_type = getattr(config, "model_type", "")
                        
                        if model_type:
                            print(f"Detected model type: {model_type}")
                            # 根據模型類型選擇合適的類
                            if model_type == "smolvlm":
                                from transformers import AutoModelForCausalLM
                                model = AutoModelForCausalLM.from_pretrained(
                                    model_id,
                                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                                    device_map="auto" if torch.cuda.is_available() else None,
                                    trust_remote_code=True
                                )
                            else:
                                raise ImportError(f"Unsupported model type: {model_type}")
                        else:
                            raise ImportError("Could not determine model type")
                
                # 移動到適當的設備
                if torch.backends.mps.is_available() and not torch.cuda.is_available():
                    model = model.to('mps')
                    print("Using MPS (Apple Silicon) acceleration")
                elif torch.cuda.is_available():
                    model = model.to('cuda')
                    print("Using CUDA acceleration")
                
                print(f"SmolVLM2-Video loaded successfully using {method} method!")
                return model, processor
                
            except Exception as e:
                print(f"{method} method failed: {str(e)}")
                continue
        
        # 如果所有方法都失敗
        raise RuntimeError("All SmolVLM2-Video loading methods failed. Please check model compatibility and dependencies.")
    
    @staticmethod
    def load_moondream2(model_id="vikhyatk/moondream2"):
        """Load Moondream2"""
        print(f"Loading Moondream2 {model_id}...")
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # Move to appropriate device
            if torch.backends.mps.is_available():
                model = model.to('mps')
                print("Using MPS (Apple Silicon) acceleration")
            elif torch.cuda.is_available():
                model = model.to('cuda')
                print("Using CUDA acceleration")
            
            print("Moondream2 loaded successfully!")
            return model, tokenizer
            
        except Exception as e:
            print(f"Moondream2 loading failed: {str(e)}")
            raise RuntimeError(f"Moondream2 model loading failed: {str(e)}")
    
    @staticmethod
    def load_phi3_vision(model_id="mlx-community/Phi-3.5-vision-instruct-4bit"):
        """Load Phi-3.5-Vision using MLX-VLM or fallback methods"""
        print(f"Loading Phi3-Vision {model_id}...")
        
        # 定義多種加載方法
        methods_to_try = [
            "mlx_vlm",
            "transformers_auto",
            "pipeline",
            "specific_model_class"
        ]
        
        for method in methods_to_try:
            try:
                if method == "mlx_vlm":
                    print("Trying MLX-VLM method...")
                    try:
                        from mlx_vlm import load
                        
                        print("Loading MLX-VLM optimized Phi-3.5-Vision model...")
                        model, processor = load(model_id, trust_remote_code=True)
                        print("Phi3-Vision loaded successfully with MLX-VLM!")
                        return model, processor
                    except ImportError:
                        print("MLX-VLM not installed, skipping this method")
                        raise ImportError("MLX-VLM not installed")
                
                elif method == "transformers_auto":
                    print("Trying standard transformers method...")
                    from transformers import AutoProcessor, AutoModelForCausalLM
                    import torch
                    
                    # 使用 AutoModelForCausalLM 加載模型
                    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                    model = AutoModelForCausalLM.from_pretrained(
                        model_id,
                        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                        device_map="auto" if torch.cuda.is_available() else None,
                        trust_remote_code=True
                    )
                    
                    # 移動到適當的設備
                    if torch.backends.mps.is_available() and not torch.cuda.is_available():
                        model = model.to('mps')
                        print("Using MPS (Apple Silicon) acceleration")
                    elif torch.cuda.is_available():
                        model = model.to('cuda')
                        print("Using CUDA acceleration")
                    
                    print("Phi3-Vision loaded successfully using standard transformers!")
                    return model, processor
                
                elif method == "pipeline":
                    print("Trying pipeline method...")
                    from transformers import AutoProcessor, pipeline
                    import torch
                    
                    # 使用 pipeline 方式加載模型
                    pipe = pipeline(
                        "image-to-text",
                        model=model_id,
                        device="mps" if torch.backends.mps.is_available() and not torch.cuda.is_available() else "cuda" if torch.cuda.is_available() else "cpu",
                        trust_remote_code=True
                    )
                    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                    model = pipe.model
                    
                    print("Phi3-Vision loaded successfully using pipeline method!")
                    return model, processor
                
                elif method == "specific_model_class":
                    print("Trying specific model class method...")
                    from transformers import AutoProcessor, AutoConfig
                    import torch
                    
                    # 獲取模型配置
                    config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
                    model_type = getattr(config, "model_type", "")
                    
                    if model_type:
                        print(f"Detected model type: {model_type}")
                        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                        
                        # 根據模型類型選擇合適的類
                        if model_type == "phi":
                            from transformers.models.phi.modeling_phi import PhiForCausalLM
                            model = PhiForCausalLM.from_pretrained(
                                model_id,
                                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                                device_map="auto" if torch.cuda.is_available() else None,
                                trust_remote_code=True
                            )
                        elif model_type == "phi-msft":
                            from transformers.models.phi.modeling_phi import PhiForCausalLM
                            model = PhiForCausalLM.from_pretrained(
                                model_id,
                                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                                device_map="auto" if torch.cuda.is_available() else None,
                                trust_remote_code=True
                            )
                        else:
                            # 嘗試通用方法
                            from transformers import AutoModelForCausalLM
                            model = AutoModelForCausalLM.from_pretrained(
                                model_id,
                                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                                device_map="auto" if torch.cuda.is_available() else None,
                                trust_remote_code=True
                            )
                        
                        # 移動到適當的設備
                        if torch.backends.mps.is_available() and not torch.cuda.is_available():
                            model = model.to('mps')
                            print("Using MPS (Apple Silicon) acceleration")
                        elif torch.cuda.is_available():
                            model = model.to('cuda')
                            print("Using CUDA acceleration")
                        
                        print(f"Phi3-Vision loaded successfully using specific model class for {model_type}!")
                        return model, processor
                    else:
                        raise ValueError("Could not determine model type")
                
            except Exception as e:
                print(f"{method} method failed: {str(e)}")
                continue
        
        # 如果所有方法都失敗
        raise RuntimeError("All Phi3-Vision loading methods failed. Please check model compatibility and dependencies.")
    
    @staticmethod
    def load_smolvlm(model_id="HuggingFaceTB/SmolVLM-500M-Instruct"):
        """Load SmolVLM-500M-Instruct"""
        print(f"Loading SmolVLM {model_id}...")
        try:
            from transformers import AutoProcessor, AutoModel
            import torch
            
            # 使用 AutoModel 而不是 AutoModelForVision2Seq
            processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
            model = AutoModel.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            # Move to MPS if available (Apple Silicon)
            if torch.backends.mps.is_available() and not torch.cuda.is_available():
                model = model.to('mps')
                print("Using MPS (Apple Silicon) acceleration")
            
            print("SmolVLM loaded successfully!")
            return model, processor
            
        except Exception as e:
            print(f"SmolVLM loading failed: {str(e)}")
            # 嘗試備用加載方法
            try:
                print("Attempting alternative loading method...")
                from transformers import AutoProcessor, pipeline
                
                # 使用 pipeline 方式加載模型
                pipe = pipeline(
                    "image-to-text",
                    model=model_id,
                    device="mps" if torch.backends.mps.is_available() and not torch.cuda.is_available() else "cuda" if torch.cuda.is_available() else "cpu",
                    trust_remote_code=True
                )
                processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                model = pipe.model
                
                print("SmolVLM loaded successfully using pipeline method!")
                return model, processor
            except Exception as e2:
                print(f"Alternative loading method failed: {str(e2)}")
                raise RuntimeError(f"SmolVLM model loading failed: {str(e)}")
    
    @staticmethod
    def load_llava_mlx(model_id="mlx-community/llava-v1.6-mistral-7b-4bit"):
        """Load LLaVA MLX"""
        print(f"Loading LLaVA-MLX {model_id}...")
        try:
            try:
                from mlx_vlm import load
                
                print("Loading MLX optimized LLaVA model...")
                model, processor = load(model_id)
                print("LLaVA-MLX loaded successfully!")
                
                return model, processor
            except ImportError:
                # 如果 mlx_vlm 未安裝，嘗試使用標準 transformers 加載
                print("MLX-VLM not installed. Attempting to load with standard transformers...")
                from transformers import AutoProcessor, AutoModelForCausalLM
                import torch
                
                processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    trust_remote_code=True
                )
                
                # Move to MPS if available (Apple Silicon)
                if torch.backends.mps.is_available() and not torch.cuda.is_available():
                    model = model.to('mps')
                    print("Using MPS (Apple Silicon) acceleration")
                
                print("LLaVA-MLX loaded successfully using standard transformers!")
                return model, processor
            
        except Exception as e:
            print(f"LLaVA-MLX loading failed: {str(e)}")
            # 嘗試備用加載方法
            try:
                print("Attempting alternative loading method...")
                from transformers import AutoProcessor, pipeline
                
                # 使用 pipeline 方式加載模型
                pipe = pipeline(
                    "image-to-text",
                    model=model_id,
                    device="mps" if torch.backends.mps.is_available() and not torch.cuda.is_available() else "cuda" if torch.cuda.is_available() else "cpu",
                    trust_remote_code=True
                )
                processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                model = pipe.model
                
                print("LLaVA-MLX loaded successfully using pipeline method!")
                return model, processor
            except Exception as e2:
                print(f"Alternative loading method failed: {str(e2)}")
                raise RuntimeError(f"LLaVA-MLX model loading failed: {str(e)}")

class UnifiedModelServer:
    """Unified Model Server"""
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        self.model_name = model_name
        self.config = config
        self.model = None
        self.processor = None
        self.loaded = False
        
        # Setup Flask app
        self.app = Flask(__name__)
        self.setup_routes()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_routes(self):
        """Setup routes"""
        self.app.route('/', methods=['GET'])(self.root)
        self.app.route('/health', methods=['GET'])(self.health_check)
        self.app.route('/v1/chat/completions', methods=['POST'])(self.chat_completions)
    
    def load_model(self):
        """Load model"""
        try:
            self.logger.info(f"Loading model: {self.model_name}")
            
            if "smolvlm2" in self.model_name.lower():
                self.model, self.processor = UnifiedModelLoader.load_smolvlm2_video()
            elif "smolvlm" in self.model_name.lower():
                self.model, self.processor = UnifiedModelLoader.load_smolvlm()
            elif "moondream2" in self.model_name.lower():
                self.model, self.processor = UnifiedModelLoader.load_moondream2()
            elif "phi3" in self.model_name.lower():
                self.model, self.processor = UnifiedModelLoader.load_phi3_vision()
            elif "llava" in self.model_name.lower():
                self.model, self.processor = UnifiedModelLoader.load_llava_mlx()
            else:
                raise ValueError(f"Unsupported model: {self.model_name}")
            
            self.loaded = True
            self.logger.info(f"Model {self.model_name} loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model {self.model_name}: {e}")
            return False
    
    def predict(self, image: Image.Image, prompt: str) -> str:
        """Unified prediction interface"""
        if not self.loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            if "smolvlm2" in self.model_name.lower():
                return self._predict_smolvlm2(image, prompt)
            elif "smolvlm" in self.model_name.lower():
                return self._predict_smolvlm(image, prompt)
            elif "moondream2" in self.model_name.lower():
                return self._predict_moondream2(image, prompt)
            elif "phi3" in self.model_name.lower():
                return self._predict_phi3(image, prompt)
            elif "llava" in self.model_name.lower():
                return self._predict_llava(image, prompt)
            else:
                raise ValueError(f"Prediction not implemented for {self.model_name}")
                
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise
    
    def _predict_smolvlm2(self, image: Image.Image, prompt: str) -> str:
        """SmolVLM2 prediction with multiple fallback methods"""
        # 定義多種預測方法
        methods_to_try = [
            "standard_generate",
            "chat_template",
            "direct_generate",
            "pipeline_api",
            "model_specific_api"
        ]
        
        last_error = None
        
        for method in methods_to_try:
            try:
                print(f"Trying prediction method: {method}")
                
                if method == "standard_generate":
                    # 標準生成方法
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "image"},
                                {"type": "text", "text": prompt}
                            ]
                        }
                    ]
                    
                    # 檢查處理器是否有 apply_chat_template 方法
                    if hasattr(self.processor, "apply_chat_template"):
                        input_text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                        inputs = self.processor(text=input_text, images=[image], return_tensors="pt")
                        
                        # 移動到模型所在設備
                        device = next(self.model.parameters()).device
                        inputs = {k: v.to(device) for k, v in inputs.items()}
                        
                        with torch.no_grad():
                            outputs = self.model.generate(**inputs, max_new_tokens=100, do_sample=False)
                        
                        response = self.processor.decode(outputs[0], skip_special_tokens=True)
                        return response.replace(input_text, "").strip()
                    else:
                        raise ValueError("Processor does not have apply_chat_template method")
                
                elif method == "chat_template":
                    # 嘗試不同的聊天模板格式
                    if hasattr(self.processor, "tokenizer") and hasattr(self.processor.tokenizer, "apply_chat_template"):
                        messages = [
                            {"role": "user", "content": f"<image>\n{prompt}"}
                        ]
                        
                        input_text = self.processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                        inputs = self.processor(text=input_text, images=[image], return_tensors="pt")
                        
                        # 移動到模型所在設備
                        device = next(self.model.parameters()).device
                        inputs = {k: v.to(device) for k, v in inputs.items()}
                        
                        with torch.no_grad():
                            outputs = self.model.generate(**inputs, max_new_tokens=100, do_sample=False)
                        
                        response = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
                        return response.replace(input_text, "").strip()
                    else:
                        raise ValueError("Processor does not have tokenizer with apply_chat_template method")
                
                elif method == "direct_generate":
                    # 直接使用處理器處理圖像和文本
                    inputs = self.processor(images=[image], text=prompt, return_tensors="pt")
                    
                    # 移動到模型所在設備
                    device = next(self.model.parameters()).device
                    inputs = {k: v.to(device) for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        outputs = self.model.generate(**inputs, max_new_tokens=100, do_sample=False)
                    
                    if hasattr(self.processor, "decode"):
                        response = self.processor.decode(outputs[0], skip_special_tokens=True)
                    elif hasattr(self.processor, "tokenizer") and hasattr(self.processor.tokenizer, "decode"):
                        response = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    else:
                        from transformers import AutoTokenizer
                        tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolVLM2-500M-Video-Instruct")
                        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    
                    # 嘗試移除提示詞
                    if prompt in response:
                        response = response.replace(prompt, "").strip()
                    return response
                
                elif method == "pipeline_api":
                    # 使用 transformers pipeline API
                    from transformers import pipeline
                    import torch
                    
                    # 創建 pipeline
                    pipe = pipeline(
                        "image-to-text",
                        model=self.model,
                        tokenizer=self.processor if hasattr(self.processor, "tokenizer") else self.processor,
                        device="mps" if torch.backends.mps.is_available() and not torch.cuda.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
                    )
                    
                    # 使用 pipeline 生成文本
                    result = pipe(image, prompt=prompt)
                    if isinstance(result, list) and len(result) > 0:
                        return result[0]["generated_text"]
                    return str(result)
                
                elif method == "model_specific_api":
                    # 檢查模型是否有特定的 API
                    if hasattr(self.model, "generate_text"):
                        # 某些模型有直接的 generate_text 方法
                        response = self.model.generate_text(image, prompt)
                        return response
                    
                    # 檢查是否有 __call__ 方法
                    if callable(getattr(self.model, "__call__", None)):
                        result = self.model(image, prompt)
                        if isinstance(result, str):
                            return result
                        elif isinstance(result, dict) and "generated_text" in result:
                            return result["generated_text"]
                    
                    raise ValueError("Model does not have specific API methods")
                
            except Exception as e:
                print(f"{method} prediction method failed: {str(e)}")
                last_error = e
                continue
        
        # 如果所有方法都失敗，返回錯誤信息
        error_msg = f"All prediction methods failed. Last error: {str(last_error)}"
        print(error_msg)
        return f"Error: Could not generate response with SmolVLM2. Please try a different model or check model compatibility."
    
    def _predict_smolvlm(self, image: Image.Image, prompt: str) -> str:
        """SmolVLM prediction"""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        input_text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=input_text, images=[image], return_tensors="pt")
        
        # Move to same device as model
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=100, do_sample=False)
        
        response = self.processor.decode(outputs[0], skip_special_tokens=True)
        return response.replace(input_text, "").strip()
    
    def _predict_moondream2(self, image: Image.Image, prompt: str) -> str:
        """Moondream2 prediction"""
        # Moondream2 has special API
        encoded_image = self.model.encode_image(image)
        response = self.model.answer_question(encoded_image, prompt, self.processor)
        return response
    
    def _predict_phi3(self, image: Image.Image, prompt: str) -> str:
        """Phi3 Vision prediction with multiple fallback methods"""
        # 嘗試使用 MLX-VLM 生成
        try:
            try:
                from mlx_vlm import generate
                
                response = generate(
                    model=self.model,
                    processor=self.processor,
                    image=image,
                    prompt=prompt,
                    max_tokens=100,
                    temp=0.0,
                    verbose=False
                )
                return str(response)
            except ImportError:
                print("MLX-VLM not installed, trying standard methods")
                
            # 嘗試標準生成方法
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # 檢查處理器是否有 apply_chat_template 方法
            if hasattr(self.processor, "apply_chat_template"):
                input_text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = self.processor(text=input_text, images=[image], return_tensors="pt")
            elif hasattr(self.processor, "tokenizer") and hasattr(self.processor.tokenizer, "apply_chat_template"):
                input_text = self.processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = self.processor(text=input_text, images=[image], return_tensors="pt")
            else:
                # 直接處理
                inputs = self.processor(images=[image], text=prompt, return_tensors="pt")
            
            # 移動到模型所在設備
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_new_tokens=100, do_sample=False)
            
            # 解碼輸出
            if hasattr(self.processor, "decode"):
                response = self.processor.decode(outputs[0], skip_special_tokens=True)
            elif hasattr(self.processor, "tokenizer") and hasattr(self.processor.tokenizer, "decode"):
                response = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                from transformers import AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained("mlx-community/Phi-3.5-vision-instruct-4bit")
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 嘗試移除提示詞
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            return response
            
        except Exception as e:
            print(f"Standard prediction methods failed: {str(e)}")
            
            # 嘗試使用 pipeline
            try:
                from transformers import pipeline
                import torch
                
                pipe = pipeline(
                    "image-to-text",
                    model=self.model,
                    tokenizer=self.processor if hasattr(self.processor, "tokenizer") else self.processor,
                    device="mps" if torch.backends.mps.is_available() and not torch.cuda.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
                )
                
                result = pipe(image, prompt=prompt)
                if isinstance(result, list) and len(result) > 0:
                    return result[0]["generated_text"]
                return str(result)
                
            except Exception as e2:
                print(f"Pipeline method failed: {str(e2)}")
                return f"Error generating response with Phi-3.5-Vision: {str(e)}. Please try a different model."
    
    def _predict_llava(self, image: Image.Image, prompt: str) -> str:
        """LLaVA prediction"""
        from mlx_vlm import generate
        
        response = generate(
            model=self.model,
            processor=self.processor,
            image=image,
            prompt=prompt,
            max_tokens=100,
            temp=0.0,
            verbose=False
        )
        return str(response)
    
    def root(self):
        """Root endpoint"""
        return jsonify({
            "message": f"Unified Model Server - {self.model_name}",
            "model": self.model_name,
            "loaded": self.loaded,
            "version": "1.0.0"
        })
    
    def health_check(self):
        """Health check endpoint"""
        return jsonify({
            "status": "healthy" if self.loaded else "not_loaded",
            "model": self.model_name,
            "loaded": self.loaded
        })
    
    def chat_completions(self):
        """OpenAI-compatible chat completions endpoint"""
        try:
            if not self.loaded:
                return jsonify({"error": "Model not loaded"}), 500
            
            data = request.get_json()
            messages = data.get('messages', [])
            
            if not messages:
                return jsonify({"error": "No messages provided"}), 400
            
            # Extract image and text from messages
            image = None
            prompt = ""
            
            for message in messages:
                if message.get('role') == 'user':
                    content = message.get('content', [])
                    if isinstance(content, list):
                        for item in content:
                            if item.get('type') == 'text':
                                prompt = item.get('text', '')
                            elif item.get('type') == 'image_url':
                                # Decode base64 image
                                image_url = item.get('image_url', {}).get('url', '')
                                if image_url.startswith('data:image'):
                                    base64_data = image_url.split(',')[1]
                                    image_data = base64.b64decode(base64_data)
                                    image = Image.open(BytesIO(image_data))
                    elif isinstance(content, str):
                        prompt = content
            
            if not image:
                return jsonify({"error": "No image provided"}), 400
            
            if not prompt:
                return jsonify({"error": "No prompt provided"}), 400
            
            # Generate response
            response_text = self.predict(image, prompt)
            
            # Return OpenAI-compatible response
            return jsonify({
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": self.model_name,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }]
            })
            
        except Exception as e:
            self.logger.error(f"Chat completion error: {e}")
            return jsonify({"error": str(e)}), 500
    
    def run(self, host='0.0.0.0', port=8080):
        """Start server"""
        if not self.load_model():
            print("❌ Failed to load model")
            return False
        
        print(f"🚀 Starting unified model server for {self.model_name}")
        print(f"🌐 Server will be available at http://{host}:{port}")
        print(f"🔍 Health check: http://{host}:{port}/health")
        print(f"📡 API endpoint: http://{host}:{port}/v1/chat/completions")
        
        try:
            self.app.run(host=host, port=port, debug=False)
        except KeyboardInterrupt:
            print("\\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {e}")
            return False
        
        return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Unified Model Server")
    parser.add_argument('--model', '-m', required=True, help='Model name')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Server port')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    
    args = parser.parse_args()
    
    # Load model config (optional)
    config = {}
    
    # Create and run server
    server = UnifiedModelServer(args.model, config)
    success = server.run(host=args.host, port=args.port)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()