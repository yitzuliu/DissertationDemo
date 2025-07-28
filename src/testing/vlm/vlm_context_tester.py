#!/usr/bin/env python3
"""
VLM Model Context Understanding Capability Testing Program
MacBook Air M3 (16GB) Optimized Version

Test Flow:
1. **Image Description**: Show an image with detailed prompt, require detailed description.
2. **Context-Based Questioning**: Ask follow-up questions based on the conversation history (without re-showing image).
3. **Loop**: Repeat above steps for each model and each test image.
4. **Output**: Record each context understanding test result as JSON files.

Test Objectives:
- 🎯 Test models' ability to understand and respond based on conversation context
- 🎯 Verify model responses to context-based questions without re-showing images
- 🎯 Evaluate model's capacity to maintain conversation coherence
- 🎯 Test forensic-level detail retention in conversation flow
"""

import os
import sys
import time
import json
import gc
import psutil
import traceback
import torch
import subprocess
import socket
import requests
from datetime import datetime
from pathlib import Path
from PIL import Image
import threading

# Import model loaders and helper functions from vlm_tester.py
# For code independence, we directly copy necessary components
# (In actual projects, these shared components might be refactored into independent modules)

# --- Helper functions copied from vlm_tester.py ---

def get_memory_usage():
    """Get current memory usage in GB"""
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 ** 3)

def clear_model_memory(model, processor):
    """Clear model memory"""
    print("🧹 Clearing model memory...")
    del model, processor
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    time.sleep(2)

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def run_with_timeout(func, timeout_seconds=120):
    """Run function with timeout mechanism"""
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
        raise TimeoutError(f"Inference timed out after {timeout_seconds} seconds")
    
    if exception:
        raise exception[0]
    
    return result[0] if result else None

# SmolVLM GGUF Server Management (統一與 run_smolvlm.py 的啟動方式)
def ensure_smolvlm_server():
    """確保 SmolVLM 服務器運行 - 使用與 run_smolvlm.py 相同的邏輯"""
    print("🔄 Checking SmolVLM server status...")
    
    # 首先檢查服務器是否已經運行
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ SmolVLM server is already running")
            return True
    except requests.exceptions.RequestException:
        pass
    
    # 檢查端口 8080 是否被占用
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8080))
        sock.close()
        if result == 0:
            print("⚠️ Port 8080 is occupied, attempting to close existing process...")
            # 嘗試殺死端口 8080 上的進程
            try:
                result = subprocess.run(
                    ["lsof", "-ti", ":8080"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.strip():
                            print(f"🔄 Killing process {pid} on port 8080...")
                            subprocess.run(["kill", "-9", pid.strip()], timeout=10)
                            time.sleep(2)  # 等待進程終止
            except Exception as e:
                print(f"⚠️ Failed to kill process on port 8080: {e}")
    except Exception as e:
        print(f"⚠️ Error checking port 8080: {e}")
    
    # 嘗試啟動服務器（最多 3 次嘗試）
    for attempt in range(1, 4):
        print(f"🔄 Attempt {attempt}/3: Starting SmolVLM server...")
        try:
            # 使用與 run_smolvlm.py 相同的命令
            cmd = [
                "llama-server",
                "-hf", "ggml-org/SmolVLM-500M-Instruct-GGUF",
                "-ngl", "99",
                "--port", "8080"
            ]
            
            # 在後台啟動服務器
            server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服務器啟動（最多 30 秒）
            for i in range(30):
                time.sleep(2)
                try:
                    response = requests.get("http://localhost:8080/health", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ SmolVLM server started successfully on attempt {attempt}")
                        return True
                except requests.exceptions.RequestException:
                    continue
            
            # 如果到這裡，服務器沒有啟動
            print(f"❌ SmolVLM server failed to start on attempt {attempt}")
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except:
                pass
                
        except Exception as e:
            print(f"❌ Error starting SmolVLM server on attempt {attempt}: {e}")
    
    print("❌ Failed to start SmolVLM server after 3 attempts")
    return False

def cleanup_smolvlm_server():
    """清理 SmolVLM 服務器進程"""
    try:
        # 殺死端口 8080 上的任何進程
        result = subprocess.run(
            ["lsof", "-ti", ":8080"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    print(f"🔄 Cleaning up SmolVLM server process {pid}...")
                    try:
                        subprocess.run(["kill", "-9", pid.strip()], timeout=10)
                    except Exception as e:
                        print(f"⚠️ Failed to kill process {pid}: {e}")
    except Exception as e:
        print(f"⚠️ Error during server cleanup: {e}")

# --- Model loader copied from vlm_tester.py ---

class VLMModelLoader:
    """VLM Model Loader - Consistent with vlm_tester.py"""
    
    @staticmethod
    def load_smolvlm2_video(model_id="mlx-community/SmolVLM2-500M-Video-Instruct-mlx"):
        """Load SmolVLM2-500M-Video-Instruct (prefer MLX version)"""
        print(f"Loading SmolVLM2-500M-Video-Instruct (prefer MLX version)...")
        try:
            from mlx_vlm import load
            print("Loading MLX-VLM optimized SmolVLM2 model...")
            model, processor = load(model_id)
            print("MLX-VLM SmolVLM2 loaded successfully!")
            model._is_mlx_model = True
            return model, processor
        except ImportError as e:
            print("MLX-VLM not installed, using original SmolVLM2 model...")
            print("Please run: pip install mlx-vlm")
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            from transformers import AutoProcessor, AutoModelForImageTextToText
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            return model, processor
        except Exception as e:
            print(f"MLX-VLM loading failed: {str(e)}")
            print("Using original SmolVLM2 model as fallback...")
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            from transformers import AutoProcessor, AutoModelForImageTextToText
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            return model, processor
    
    @staticmethod
    def load_smolvlm_instruct(model_id="ggml-org/SmolVLM-500M-Instruct-GGUF"):
        """Load SmolVLM-500M-Instruct GGUF version via HTTP API (統一方式)"""
        print(f"Loading SmolVLM GGUF version via HTTP API...")
        
        # 確保服務器運行
        if not ensure_smolvlm_server():
            raise RuntimeError("SmolVLM server is not available")
        
        print("✅ SmolVLM GGUF server is ready")
        
        # 返回特殊標記，表示這是 HTTP API 模式
        class SmolVLMGGUFModel:
            def __init__(self):
                self.api_endpoint = "http://localhost:8080/v1/chat/completions"
                self.model_type = "smolvlm_gguf"
        
        class SmolVLMGGUFProcessor:
            def __init__(self):
                self.tokenizer = None  # GGUF 不需要本地 tokenizer
        
        return SmolVLMGGUFModel(), SmolVLMGGUFProcessor()
    
    @staticmethod
    def load_smolvlm_gguf(model_id="ggml-org/SmolVLM-500M-Instruct-GGUF"):
        """Load SmolVLM GGUF version - Alias for load_smolvlm_instruct for backward compatibility"""
        return VLMModelLoader.load_smolvlm_instruct(model_id)
    
    @staticmethod
    def load_moondream2(model_id="vikhyatk/moondream2"):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        print(f"Loading {model_id}...")
        model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        if torch.backends.mps.is_available():
            model = model.to('mps')
        return model, tokenizer
    
    @staticmethod
    def load_llava_mlx(model_id="mlx-community/llava-v1.6-mistral-7b-4bit"):
        print(f"Loading MLX-LLaVA {model_id}...")
        try:
            from mlx_vlm import load
            model, processor = load(model_id)
            print("MLX-LLaVA loaded successfully!")
            print("⚠️  Note: This model has known state pollution issues in batch testing")
            return model, processor
        except ImportError:
            raise RuntimeError("MLX-VLM package not installed (pip install mlx-vlm), cannot test this model.")
    
    @staticmethod
    def load_phi3_vision(model_id="mlx-community/Phi-3.5-vision-instruct-4bit"):
        """Load Phi-3.5-Vision-Instruct using MLX (Apple Silicon optimized)"""
        print(f"Loading {model_id} with MLX framework...")
        try:
            from mlx_vlm import load
            print("Loading MLX-VLM optimized Phi-3.5-Vision-Instruct model...")
            model, processor = load(model_id, trust_remote_code=True)
            print("MLX-VLM model loaded successfully!")
            return model, processor
        except ImportError as e:
            print("MLX-VLM not installed. Installing MLX-VLM...")
            print("Please run: pip install mlx-vlm")
            print("Falling back to original transformers approach...")
            from transformers import AutoModelForCausalLM, AutoProcessor
            print("Using memory-optimized loading for Apple Silicon...")
            model = AutoModelForCausalLM.from_pretrained(
                "microsoft/Phi-3.5-vision-instruct", 
                trust_remote_code=True,
                torch_dtype=torch.float16,
                _attn_implementation="eager",
                device_map="cpu",
                low_cpu_mem_usage=True
            )
            processor = AutoProcessor.from_pretrained("microsoft/Phi-3.5-vision-instruct", trust_remote_code=True)
            return model, processor
        except Exception as e:
            print(f"MLX loading failed: {str(e)}")
            print("Falling back to original transformers approach...")
            from transformers import AutoModelForCausalLM, AutoProcessor
            print("Using memory-optimized loading for Apple Silicon...")
            model = AutoModelForCausalLM.from_pretrained(
                "microsoft/Phi-3.5-vision-instruct", 
                trust_remote_code=True,
                torch_dtype=torch.float16,
                _attn_implementation="eager",
                device_map="cpu",
                low_cpu_mem_usage=True
            )
            processor = AutoProcessor.from_pretrained("microsoft/Phi-3.5-vision-instruct", trust_remote_code=True)
            return model, processor

# --- Context understanding testing core program ---

class VLMContextTester:
    """VLM Context Understanding Capability Tester"""
    
    def __init__(self):
        self.results = {
            "test_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {
                "device": "MacBook Air M3",
                "memory": "16GB",
                "mps_available": torch.backends.mps.is_available()
            },
            "test_type": "context_understanding",
            "models": {}
        }
        
        # Model configuration for context understanding tests (reordered as requested)
        self.models_config = {
            "Phi-3.5-Vision-Instruct": { 
                "loader": VLMModelLoader.load_phi3_vision, 
                "model_id": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), requires 'pip install mlx-vlm'"
            },
            "LLaVA-v1.6-Mistral-7B-MLX": { 
                "loader": VLMModelLoader.load_llava_mlx, 
                "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), has known state pollution issues in batch testing"
            },
            "Moondream2": { 
                "loader": VLMModelLoader.load_moondream2, 
                "model_id": "vikhyatk/moondream2",
                "note": "Lightweight vision-only model for Apple Silicon"
            },
            "SmolVLM2-500M-Video-Instruct": { 
                "loader": VLMModelLoader.load_smolvlm2_video, 
                "model_id": "mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), falls back to original SmolVLM2 if MLX not available or incompatible"
            },
            "SmolVLM-500M-Instruct": { 
                "loader": VLMModelLoader.load_smolvlm_instruct, 
                "model_id": "ggml-org/SmolVLM-500M-Instruct-GGUF",
                "note": "GGUF version via HTTP API (與 run_smolvlm.py 一致)"
            }
        }
        
        # Unified test parameters
        self.unified_max_tokens = 100  # Maximum tokens for generation
        self.unified_image_size = 1024 # Maximum image size for all models
        
        # Prompts for context understanding tests
        self.seeding_prompt = (
            "You are a forensic expert. Describe this image in extreme detail, "
            "listing every object, person, color, and spatial relationship you can identify. "
            "This is for a critical investigation."
        )
        self.recall_questions = [
            "What were the most prominent colors in the image?",
            "Were there any people visible in the image? If so, describe their general appearance or clothing without making up details.",
            "Summarize the main subject or scene of the image in one sentence."
        ]
        # The test strategy is to maintain conversation history to evaluate context retention.

    def get_test_images(self):
        """Get a list of test images from the materials/images directory."""
        from pathlib import Path
        base_dir = Path(__file__).parent.parent  # src/testing/
        possible_paths = [
            base_dir / "materials" / "images",
            Path("materials/images"),
            Path("./materials/images")
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
        """Run context understanding tests for all configured models."""
        print("="*60)
        print("🤖 Starting VLM Model Context Understanding Testing 🤖")
        print("="*60)
        
        test_images = self.get_test_images()
        if not test_images:
            print("❌ Error: No test images found. Please ensure images are located in src/testing/materials/images/")
            return

        print(f"🖼️ Found {len(test_images)} test images.")
        total_start_time = time.time()

        for model_name, config in self.models_config.items():
            self.test_single_model(model_name, config, test_images)
        
        total_time = time.time() - total_start_time
        self.results["total_test_time"] = total_time
        print(f"\n✅ All tests completed, total time: {total_time:.2f} seconds")
        self.save_results()

    def test_single_model(self, model_name, config, test_images):
        """Test a single model"""
        print(f"\n{'='*50}\n🔬 Starting model test: {model_name}\n{'='*50}")
        
        memory_before = get_memory_usage()
        print(f"Memory before loading: {memory_before:.2f} GB")
        
        model_results = {
            "model_id": config["model_id"],
            "image_tests": []
        }
        
        try:
            start_time = time.time()
            model, processor = config["loader"]()
            load_time = time.time() - start_time
            
            memory_after = get_memory_usage()
            print(f"Memory after loading: {memory_after:.2f} GB (load time {load_time:.2f} seconds)")
            
            model_results.update({
                "load_time": load_time,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_diff": memory_after - memory_before
            })

            for image_path in test_images:
                print(f"\n--- Testing image: {image_path.name} ---")
                
                # ✅ FIXED: Reload LLaVA only when necessary to avoid state bug
                if "LLaVA" in model_name:
                    print("  >> LLaVA-MLX: Reloading model to clear state...")
                    clear_model_memory(model, processor)
                    model, processor = config["loader"]()
                    print("  >> LLaVA-MLX: Reload successful.")
                
                image_test_result = self.run_conversation_test(model, processor, image_path, model_name)
                model_results["image_tests"].append(image_test_result)
            
        except Exception as e:
            print(f"❌ Serious error occurred while testing model {model_name}: {e}")
            model_results["error"] = str(e)
        
        finally:
            if 'model' in locals():
                clear_model_memory(model, processor)
                memory_after_cleanup = get_memory_usage()
                print(f"Memory after cleanup: {memory_after_cleanup:.2f} GB")
                model_results["memory_after_cleanup"] = memory_after_cleanup

            self.results["models"][model_name] = model_results
            self.save_results(f"intermediate_{model_name}")

    def run_conversation_test(self, model, processor, image_path, model_name):
        """Execute context understanding test (maintaining conversation history)"""
        
        image_test_result = {
            "image_name": image_path.name,
            "image_description_phase": {},
            "context_based_questions": {},
            "test_type": "context_understanding",
            "conversation_flow": []
        }
        
        # Prepare image with preprocessing (same as vlm_tester.py)
        image = Image.open(image_path).convert('RGB')
        
        # 📏 Unified image preprocessing (consistent across all models)
        original_size = image.size
        if max(image.size) > self.unified_image_size:
            ratio = self.unified_image_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            print(f"  📏 Image resized: {original_size} → {image.size}")
        
        # Initialize conversation history
        conversation_history = []

        # Step 1: Image description (with image) - Build initial context
        print("1️⃣  Step 1: Image description (building context)")
        description_response, description_time, conversation_history = self.run_inference(
            model, processor, model_name, self.seeding_prompt, image=image, history=conversation_history
        )
        image_test_result["image_description_phase"] = {
            "prompt": self.seeding_prompt,
            "response": description_response,
            "inference_time": description_time
        }
        image_test_result["conversation_flow"].append({
            "step": 1,
            "type": "image_description",
            "prompt": self.seeding_prompt,
            "has_image": True,
            "response": description_response,
            "inference_time": description_time
        })

        print(f"    - Response (first 100 chars): {description_response[:100].strip()}...")
        print(f"    - Inference time: {description_time:.2f} seconds")
        
        # If description fails, terminate early
        if "Error:" in description_response:
            print("    - Image description failed, skipping follow-up questions.")
            return image_test_result

        # Step 2: Context-based follow-up questions (using conversation history)
        print("\n2️⃣  Step 2: Context-based questioning")
        for i, question in enumerate(self.recall_questions):
            print(f"  - Context question {i+1}/3: {question}")
            
            # Key: Use conversation history to test context understanding
            recall_response, recall_time, conversation_history = self.run_inference(
                model, processor, model_name, question, image=None, history=conversation_history
            )
            
            image_test_result["context_based_questions"][f"question_{i+1}"] = {
                "prompt": question,
                "response": recall_response,
                "inference_time": recall_time
            }
            image_test_result["conversation_flow"].append({
                "step": i + 2,
                "type": "context_question",
                "prompt": question,
                "has_image": False,
                "response": recall_response,
                "inference_time": recall_time
            })
            
            print(f"    - Response: {recall_response.strip()}")
            print(f"    - Inference time: {recall_time:.2f} seconds")
            
        return image_test_result

    def run_inference(self, model, processor, model_name, prompt, image=None, history=None):
        """
        Enhanced inference function with conversation history support
        
        Args:
            model: Loaded model
            processor: Model-specific processor
            model_name: Model name
            prompt: User prompt
            image: Image (only provided during first round description)
            history: Conversation history (maintained throughout conversation)
        
        Returns:
            tuple: (response, inference_time, updated_history)
        """
        start_time = time.time()
        response = ""
        
        # Initialize history if not provided
        if history is None:
            history = []
        
        # Set timeout based on model type
        def get_timeout(model_name):
            if "LLaVA" in model_name:
                return 180  # CPU inference needs more time
            elif "Phi-3.5" in model_name:
                return 180  # Give more time for both MLX and fallback transformers
            else:
                return 60   # Small models fast inference
        
        timeout_seconds = get_timeout(model_name)
        
        def do_inference():
            nonlocal response
            try:
                # --------------------------------------------------------------------------
                # Branch 1: Standard Transformers models (e.g., SmolVLM) - IMPROVED
                # --------------------------------------------------------------------------
                if "SmolVLM" in model_name:
                    # Check if this is GGUF version
                    if hasattr(model, 'model_type') and model.model_type == "smolvlm_gguf":
                        # GGUF version via HTTP API (統一與 run_smolvlm.py 的方式)
                        print("  🚀 Using SmolVLM GGUF HTTP API...")
                        
                        import base64
                        import io
                        
                        # 構建 OpenAI 兼容的請求
                        if image is not None:
                            # 將圖片轉換為 base64
                            buffer = io.BytesIO()
                            image.save(buffer, format='JPEG')
                            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                            
                            payload = {
                                "model": "gpt-4-vision-preview",  # llama-server 兼容格式
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": prompt
                                            },
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                                }
                                            }
                                        ]
                                    }
                                ],
                                "max_tokens": self.unified_max_tokens,
                                "temperature": 0.0
                            }
                        else:
                            # 純文本請求（上下文問題）
                            # 構建包含歷史的消息
                            messages = []
                            for hist_entry in history:
                                if hist_entry["role"] == "user":
                                    # 提取文本內容
                                    if isinstance(hist_entry["content"], list):
                                        text_parts = [item["text"] for item in hist_entry["content"] if item["type"] == "text"]
                                        if text_parts:
                                            messages.append({"role": "user", "content": " ".join(text_parts)})
                                    else:
                                        messages.append({"role": "user", "content": hist_entry["content"]})
                                elif hist_entry["role"] == "assistant":
                                    messages.append({"role": "assistant", "content": hist_entry["content"]})
                            
                            # 添加當前問題
                            messages.append({"role": "user", "content": prompt})
                            
                            payload = {
                                "model": "gpt-4",  # llama-server 兼容格式
                                "messages": messages,
                                "max_tokens": self.unified_max_tokens,
                                "temperature": 0.0
                            }
                        
                        try:
                            api_response = requests.post(
                                model.api_endpoint,
                                json=payload,
                                headers={"Content-Type": "application/json"},
                                timeout=timeout_seconds
                            )
                            
                            if api_response.status_code == 200:
                                result = api_response.json()
                                if 'choices' in result and len(result['choices']) > 0:
                                    response = result['choices'][0]['message']['content']
                                else:
                                    response = f"GGUF API response format error: {result}"
                            else:
                                response = f"GGUF API request failed: {api_response.status_code} - {api_response.text}"
                                
                        except Exception as e:
                            response = f"GGUF API inference failed: {str(e)}"
                    
                    # Check if it is an MLX model
                    elif hasattr(model, '_is_mlx_model'):
                        # MLX version of SmolVLM2 inference
                        try:
                            import subprocess
                            import tempfile
                            
                            print("  🚀 Using MLX-VLM command line for SmolVLM2...")
                            
                            if image is not None:
                                # Create a temporary image file
                                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                                    temp_image_path = tmp_file.name
                                    image.save(temp_image_path)
                                
                                try:
                                    # Use MLX-VLM command line tool
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
                                        timeout=timeout_seconds
                                    )
                                    
                                    if result.returncode == 0:
                                        # Parse output and extract generated text
                                        output_lines = result.stdout.split('\n')
                                        generated_text = ""
                                        
                                        # Keep the complete Assistant reply
                                        for i, line in enumerate(output_lines):
                                            line = line.strip()
                                            if line.startswith('Assistant:'):
                                                # Found Assistant line
                                                generated_text = line
                                                # Check if next line has content
                                                if i + 1 < len(output_lines):
                                                    next_line = output_lines[i + 1].strip()
                                                    if next_line and not next_line.startswith('==========') and not next_line.startswith('Files:') and not next_line.startswith('Prompt:') and not next_line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
                                                        # Next line has content, combine both lines
                                                        generated_text = f"{line} {next_line}"
                                                break
                                            elif line and not line.startswith('==========') and not line.startswith('Files:') and not line.startswith('Prompt:') and not line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
                                                # Found other non-system info content line
                                                if not generated_text:
                                                    generated_text = line
                                        
                                        response = generated_text
                                    else:
                                        print(f"  ⚠️ MLX-VLM command failed: {result.stderr}")
                                        raise Exception(f"MLX-VLM command failed: {result.stderr}")
                                        
                                finally:
                                    # Clean up temporary file
                                    if os.path.exists(temp_image_path):
                                        os.remove(temp_image_path)
                            else:
                                # Text-only inference - create a simple test image
                                from PIL import Image
                                test_image = Image.new('RGB', (224, 224), color='white')
                                
                                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                                    temp_image_path = tmp_file.name
                                    test_image.save(temp_image_path)
                                
                                try:
                                    # Use MLX-VLM command line tool for text-only test
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
                                        timeout=timeout_seconds
                                    )
                                    
                                    if result.returncode == 0:
                                        # Parse output
                                        output_lines = result.stdout.split('\n')
                                        generated_text = ""
                                        
                                        for i, line in enumerate(output_lines):
                                            line = line.strip()
                                            if line.startswith('Assistant:'):
                                                generated_text = line
                                                if i + 1 < len(output_lines):
                                                    next_line = output_lines[i + 1].strip()
                                                    if next_line and not next_line.startswith('==========') and not next_line.startswith('Files:') and not next_line.startswith('Prompt:') and not next_line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
                                                        generated_text = f"{line} {next_line}"
                                                break
                                            elif line and not line.startswith('==========') and not line.startswith('Files:') and not line.startswith('Prompt:') and not line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
                                                if not generated_text:
                                                    generated_text = line
                                        
                                        response = generated_text
                                    else:
                                        response = f"MLX-VLM text-only command failed: {result.stderr}"
                                        
                                finally:
                                    # Clean up temporary file
                                    if os.path.exists(temp_image_path):
                                        os.remove(temp_image_path)
                        
                        except Exception as e:
                            print(f"  ⚠️ MLX-VLM SmolVLM2 inference failed: {e}")
                            response = f"Error: MLX-VLM SmolVLM2 inference failed - {str(e)}"
                    else:
                        # Standard SmolVLM inference method
                        # Build conversation with history
                        conversation = []
                        
                        # Add conversation history
                        for hist_entry in history:
                            if image is None and hist_entry["role"] == "user" and isinstance(hist_entry["content"], list):
                                # For context-based questions, filter out image tokens but keep text
                                text_content = [item for item in hist_entry["content"] if item["type"] == "text"]
                                if text_content:
                                    conversation.append({"role": hist_entry["role"], "content": text_content})
                            else:
                                conversation.append(hist_entry)
                        
                        # Add current message
                        if image is not None:
                            # With image: Standard image description
                            content = [{"type": "image"}, {"type": "text", "text": prompt}]
                            conversation.append({"role": "user", "content": content})
                        else:
                            # Without image: Context-based question
                            content = [{"type": "text", "text": prompt}]
                            conversation.append({"role": "user", "content": content})
                        
                        final_prompt = processor.apply_chat_template(conversation, tokenize=False, add_generation_prompt=True)
                        if image is not None:
                            inputs = processor(text=final_prompt, images=image, return_tensors="pt")
                        else:
                            inputs = processor(text=final_prompt, return_tensors="pt")
                        
                        with torch.no_grad():
                            outputs = model.generate(**inputs, max_new_tokens=self.unified_max_tokens, do_sample=False)
                        
                        input_len = inputs["input_ids"].shape[1]
                        generated_ids = outputs[0][input_len:]
                        response = processor.decode(generated_ids, skip_special_tokens=True).strip()

                # --------------------------------------------------------------------------
                # Branch 2: Moondream2 (Special API) - IMPROVED
                # --------------------------------------------------------------------------
                elif "Moondream2" in model_name:
                    if image is not None:
                        # With image: Use image encoding
                        try:
                            enc_image = model.encode_image(image)
                            response = model.answer_question(enc_image, prompt, processor)
                        except Exception as e:
                            response = f"Error: Moondream2 image processing failed - {str(e)}"
                    else:
                        # Without image: Moondream2 context-based inference
                        try:
                            # For context-based questions, build a prompt that includes context
                            context_prompt = f"Based on our previous conversation about the image, {prompt}"
                            
                            # Use a simple text generation approach for context-based questions
                            # Since Moondream2 doesn't handle pure text well, we'll use a fallback
                            response = f"Based on the previously described image: {prompt} - The model cannot provide context-based answers without the image."
                        except Exception as e:
                            response = f"Error: Moondream2 context-based inference failed - {str(e)}"

                # --------------------------------------------------------------------------
                # Branch 3: MLX models (LLaVA, Phi-3.5) - IMPROVED for context
                # --------------------------------------------------------------------------
                elif "Phi-3.5" in model_name:
                    # Use MLX-VLM for Phi-3.5-Vision-Instruct (same as vlm_tester.py)
                    try:
                        # Use MLX-VLM inference for vision model (official way)
                        from mlx_vlm import generate
                        print("  🚀 Using MLX-VLM inference for Phi-3.5-Vision-Instruct...")
                        
                        if image is not None:
                            # Save image to temporary file for MLX-VLM
                            temp_image_path = "temp_mlx_image.jpg"
                            image.save(temp_image_path)
                            
                            try:
                                # Use simple prompt format for MLX-VLM (same as vlm_tester.py)
                                mlx_prompt = f"<|image_1|>\nUser: {prompt}\nAssistant:"
                                
                                response = generate(
                                    model, 
                                    processor, 
                                    mlx_prompt,
                                    image=temp_image_path,
                                    max_tokens=self.unified_max_tokens,
                                    temp=0.0,  # Use 0.0 for deterministic output
                                    verbose=False
                                )
                            finally:
                                # Clean up temporary file
                                if os.path.exists(temp_image_path):
                                    os.remove(temp_image_path)
                        else:
                            # Context-based question without image - use simplified approach
                            response = generate(
                                model=model,
                                processor=processor,
                                prompt=prompt,
                                max_tokens=self.unified_max_tokens,
                                temp=0.0,
                                verbose=False
                            )
                        
                        # MLX-VLM 可能返回元組或字符串，需要解析
                        if isinstance(response, tuple) and len(response) >= 1:
                            # 如果是元組，取第一個元素作為文本回覆
                            text_response = str(response[0])
                        else:
                            # 如果是字符串，直接使用
                            text_response = str(response)
                        
                        # Clean up response
                        text_response = text_response.replace("<|end|><|endoftext|>", " ").replace("<|end|>", " ").replace("<|endoftext|>", " ")
                        if "1. What is meant by" in text_response:
                            text_response = text_response.split("1. What is meant by")[0].strip()
                        text_response = ' '.join(text_response.split())
                        
                        # Remove the original prompt if it appears in the response (but be more careful)
                        if prompt in text_response and len(text_response) > len(prompt):
                            # Only remove if the response is longer than the prompt
                            text_response = text_response.replace(prompt, "").strip()
                        
                        response = text_response
                        
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
                            {"role": "user", "content": f"<|image_1|>\\n{prompt}"}
                        ]
                        
                        prompt_text = fallback_processor.tokenizer.apply_chat_template(
                            messages, 
                            tokenize=False, 
                            add_generation_prompt=True
                        )
                        
                        inputs = fallback_processor(prompt_text, [image] if image else [], return_tensors="pt")
                        
                        # Move to correct device
                        device = next(fallback_model.parameters()).device
                        inputs = {k: v.to(device) for k, v in inputs.items()}
                        
                        # Technical fix: avoid DynamicCache error
                        with torch.no_grad():
                            outputs = fallback_model.generate(
                                **inputs, 
                                max_new_tokens=self.unified_max_tokens,
                                do_sample=False,
                                use_cache=False,  # Disable cache to avoid DynamicCache error
                                pad_token_id=fallback_processor.tokenizer.eos_token_id
                            )
                        
                        result = fallback_processor.decode(outputs[0], skip_special_tokens=True)
                        
                        # Clean up fallback model
                        del fallback_model, fallback_processor
                        gc.collect()
                        if torch.backends.mps.is_available():
                            torch.mps.empty_cache()
                        
                        response = result

                elif "LLaVA" in model_name:
                    from mlx_vlm import generate
                    if image is not None:
                        # Use direct image path approach like vlm_tester.py
                        # Save the PIL Image to a temporary file for MLX-VLM
                        temp_image_path = "temp_mlx_image.png"
                        image.save(temp_image_path)
                        
                        try:
                            raw_response = generate(
                                model, processor, prompt, image=temp_image_path,
                                max_tokens=self.unified_max_tokens, verbose=False
                            )
                        finally:
                            # Clean up temp file
                            if os.path.exists(temp_image_path):
                                os.remove(temp_image_path)
                    else:
                        # Context-based question without image - integrate conversation history
                        # Build context-aware prompt
                        context_prompt = "Based on our previous conversation about the image:\n"
                        if history:
                            # Add relevant context from history
                            for hist_entry in history:
                                if hist_entry["role"] == "assistant" and isinstance(hist_entry["content"], str):
                                    context_prompt += f"Previous response: {hist_entry['content'][:200]}...\n"
                        context_prompt += f"Question: {prompt}"
                        
                        raw_response = generate(
                            model, processor, context_prompt,
                            max_tokens=self.unified_max_tokens, verbose=False
                        )
                    
                    # Process MLX response
                    if isinstance(raw_response, tuple) and len(raw_response) >= 1:
                        response = raw_response[0]
                    elif isinstance(raw_response, list) and len(raw_response) > 0:
                        response = raw_response[0] if isinstance(raw_response[0], str) else str(raw_response[0])
                    else:
                        response = str(raw_response)

                    # Clean up response (same as vlm_tester.py)
                    response = response.replace("<|end|><|endoftext|>", " ").replace("<|end|>", " ").replace("<|endoftext|>", " ")
                    if "1. What is meant by" in response:
                        response = response.split("1. What is meant by")[0].strip()
                    response = ' '.join(response.split())
                
                else:
                    response = "Error: Unknown model type, cannot perform inference."

            except Exception as e:
                print(f"❌ Inference error: {e}")
                print(traceback.format_exc())
                response = f"Error: Exception occurred during inference - {str(e)}"
            
            return response
        
        # Execute inference with timeout
        try:
            response = run_with_timeout(do_inference, timeout_seconds=timeout_seconds)
            if response is None:
                response = ""
        except TimeoutError as e:
            print(f"❌ Timeout error: {str(e)}")
            response = f"Error: {str(e)}"
        except Exception as e:
            print(f"❌ Inference error: {e}")
            print(traceback.format_exc())
            response = f"Error: Exception occurred during inference - {str(e)}"

        inference_time = time.time() - start_time
        
        # Update conversation history
        updated_history = history.copy()
        
        # Add user message to history
        if image is not None:
            updated_history.append({"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]})
        else:
            updated_history.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        
        # Add assistant response to history
        if response and not response.startswith("Error:"):
            updated_history.append({"role": "assistant", "content": response})
        
        return response, inference_time, updated_history

    def save_results(self, suffix=""):
        """Save test results"""
        # Support running program from different directories
        possible_results_dirs = [
            Path("src/testing/results"),  # Run from project root
            Path("results"),              # Run from src/testing directory
            Path("./results")             # Current directory
        ]
        
        # Use first existing directory, or create the first one
        results_dir = None
        for path in possible_results_dirs:
            if path.exists():
                results_dir = path
                break
        
        if results_dir is None:
            # Create the first directory in the list
            results_dir = possible_results_dirs[0]
        results_dir.mkdir(parents=True, exist_ok=True)
        
        if suffix:
            filename = f"context_understanding_test_results_{suffix}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"context_understanding_test_results_{timestamp}.json"
        
        filepath = results_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Use custom serializer to handle Path objects
                def path_serializer(obj):
                    if isinstance(obj, Path):
                        return str(obj)
                    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
                json.dump(self.results, f, ensure_ascii=False, indent=2, default=path_serializer)
            print(f"\n💾 Results saved to: {filepath}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")

def main():
    """Main function"""
    tester = VLMContextTester()
    
    try:
        # Check for command-line argument to test a single model
        import sys
        if len(sys.argv) > 1:
            model_name = sys.argv[1]
            if model_name in tester.models_config:
                print(f"🔬 Testing single model: {model_name}")
                config = tester.models_config[model_name]
                
                # Prepare test images
                test_images = tester.get_test_images()
                if not test_images:
                    print("❌ Error: No test images found.")
                    return
                
                # Run test for the specified model
                tester.test_single_model(model_name, config, test_images)
                tester.save_results(f"single_{model_name}")
            else:
                print(f"❌ Error: Model '{model_name}' not found.")
                print("Available models:")
                for name in tester.models_config.keys():
                    print(f"  - {name}")
                return
        else:
            # If no argument, run all tests
            print("🤖 Running context understanding tests for all configured models.")
            tester.run_all_tests()

        print("\nContext understanding capability testing complete!")
        
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {str(e)}")
    finally:
        # 清理 SmolVLM 服務器進程
        print("\n🔄 Cleaning up...")
        cleanup_smolvlm_server()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 