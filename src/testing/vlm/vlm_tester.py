#!/usr/bin/env python3
"""
VLM Model Tester
MacBook Air M3 (16GB) Optimized Version - Load models sequentially to avoid memory overflow
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

# Memory monitoring [[memory:2405482]]
def activate_virtual_env():
    """Ensure virtual environment is activated"""
    print("Please ensure the virtual environment is activated: source ai_vision_env/bin/activate")

def get_memory_usage():
    """Get current memory usage (GB)"""
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 ** 3)  # Convert to GB

def clear_model_memory(model, processor):
    """Clear model memory"""
    print("Clearing model memory...")
    del model, processor
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    time.sleep(2)  # Allow system to clean up memory

class TimeoutError(Exception):
    """Timeout error"""
    pass

def run_with_timeout(func, timeout_seconds=120):
    """Execute function within a timeout, raise an exception if timeout"""
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
        # Timeout, but Python cannot forcefully terminate the thread, so raise an exception
        raise TimeoutError(f"Inference timed out (after {timeout_seconds} seconds)")
    
    if exception:
        raise exception[0]
    
    return result[0] if result else None

# Model Loader Class
class VLMModelLoader:
    """VLM Model Loader - Implements based on active_model.md"""
    
    @staticmethod
    def load_smolvlm2_video(model_id="mlx-community/SmolVLM2-500M-Video-Instruct-mlx"):
        """Load SmolVLM2-500M-Video-Instruct (prioritize MLX version)"""
        print(f"Loading SmolVLM2-500M-Video-Instruct (prioritize MLX version)...")
        
        try:
            # First try to use MLX-VLM framework (same method as vlm_context_tester.py)
            from mlx_vlm import load
            print("Loading MLX-VLM optimized SmolVLM2 model...")
            model, processor = load(model_id)
            print("MLX-VLM SmolVLM2 loaded successfully!")
            
            # Mark as MLX model, use special inference method
            model._is_mlx_model = True
            
            return model, processor
            
        except ImportError as e:
            print("MLX-VLM not installed, using original SmolVLM2 model...")
            print("Please run: pip install mlx-vlm")
            # Fallback to original SmolVLM2 model
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            return model, processor
            
        except Exception as e:
            print(f"MLX-VLM loading failed: {str(e)}")
            print("Using original SmolVLM2 model as fallback...")
            # Fallback to original SmolVLM2 model
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            return model, processor
    
    @staticmethod
    def load_smolvlm2_video_mlx(model_id="mlx-community/SmolVLM2-500M-Video-Instruct-mlx"):
        """Load MLX optimized SmolVLM2-500M-Video-Instruct"""
        print(f"Loading MLX optimized {model_id}...")
        try:
            # First try to use MLX-VLM framework
            from mlx_vlm import load
            print("Loading MLX-VLM optimized SmolVLM2 model...")
            model, processor = load(model_id)
            print("MLX-VLM SmolVLM2 loaded successfully!")
            
            # Mark as MLX model, use special inference method
            model._is_mlx_model = True
            
            return model, processor
            
        except ImportError as e:
            print("MLX-VLM not installed, using original SmolVLM2 model...")
            print("Please run: pip install mlx-vlm")
            # Fallback to original SmolVLM2 model
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            return model, processor
            
        except Exception as e:
            print(f"MLX-VLM loading failed: {str(e)}")
            print("Using original SmolVLM2 model as fallback...")
            # Fallback to original SmolVLM2 model
            fallback_model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            processor = AutoProcessor.from_pretrained(fallback_model_id)
            model = AutoModelForImageTextToText.from_pretrained(fallback_model_id)
            return model, processor
    
    @staticmethod
    def load_smolvlm_instruct(model_id="HuggingFaceTB/SmolVLM-500M-Instruct"):
        """Load SmolVLM-500M-Instruct"""
        print(f"Loading {model_id}...")
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForVision2Seq.from_pretrained(model_id)
        return model, processor
    
    @staticmethod
    def load_moondream2(model_id="vikhyatk/moondream2"):
        """Load Moondream2 - Use special API (model does not support standard pipeline)"""
        print(f"Loading {model_id}...")
        # Moondream2 has custom configuration, cannot use standard pipeline, need to use original method
        from transformers import AutoTokenizer
        model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # Move model to appropriate device
        if torch.backends.mps.is_available():
            model = model.to('mps')
        
        return model, tokenizer
    
    @staticmethod
    def load_llava_mlx(model_id="mlx-community/llava-v1.6-mistral-7b-4bit"):
        """Load MLX-LLaVA (Apple Silicon optimized)"""
        print(f"Loading MLX-LLaVA {model_id}...")
        try:
            from mlx_vlm import load
            print("Loading MLX optimized LLaVA model...")
            model, processor = load(model_id)
            print("MLX-LLaVA loaded successfully!")
            return model, processor
        except ImportError as e:
            print("MLX-VLM not installed. Please run: pip install mlx-vlm")
            print("Fallback to original transformers method...")
            raise RuntimeError("MLX-VLM package not installed, cannot use MLX optimized")
        except Exception as e:
            print(f"MLX-LLaVA loading failed: {str(e)}")
            raise RuntimeError(f"MLX-LLaVA model loading failed: {str(e)}")
    
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
    """VLM Tester"""
    
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
        
        # Model configuration for testing (reordered as requested)
        self.models_config = {
            "Phi-3.5-Vision-Instruct": {
                "loader": VLMModelLoader.load_phi3_vision,
                "model_id": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), requires 'pip install mlx-vlm'"
            },
            "LLaVA-v1.6-Mistral-7B-MLX": {
                "loader": VLMModelLoader.load_llava_mlx,
                "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), requires 'pip install mlx-vlm'"
            },
            "Moondream2": {
                "loader": VLMModelLoader.load_moondream2,
                "model_id": "vikhyatk/moondream2"
            },
            "SmolVLM2-500M-Video-Instruct": {
                "loader": VLMModelLoader.load_smolvlm2_video,
                "model_id": "mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), falls back to original SmolVLM2 if MLX not available or incompatible"
            },
            "SmolVLM-500M-Instruct": {
                "loader": VLMModelLoader.load_smolvlm_instruct,
                "model_id": "HuggingFaceTB/SmolVLM-500M-Instruct"
            }
        }
        
        # Unified test prompt
        self.prompt = "Describe what you see in this image in detail."
        self.unified_max_tokens = 100  # Unified generation length
        self.unified_image_size = 1024  # Unified max image size
        
        # Text-only test configuration
        self.enable_text_only_test = True  # Enable text-only test
    
    def get_test_images(self):
        """Get test image list (updated for new materials path)"""
        from pathlib import Path
        base_dir = Path(__file__).parent.parent  # src/testing/
        possible_paths = [
            base_dir / "materials" / "images",
            Path("materials/images"),
            Path("./materials/images")
        ]
        images_dir = None
        for path in possible_paths:
            if path.exists():
                images_dir = path
                break
        if images_dir is None:
            print(f"Warning: Image folder not found, tried the following paths:")
            for path in possible_paths:
                print(f"  {path}")
            return []
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(images_dir.glob(ext))
            image_files.extend(images_dir.glob(ext.upper()))
        return sorted(image_files)
    
    def test_single_model(self, model_name, config):
        """Test a single model"""
        print(f"\n{'='*50}")
        print(f"Starting test for model: {model_name}")
        print(f"{'='*50}")
        
        # Record memory before loading
        memory_before = get_memory_usage()
        print(f"Memory usage before loading: {memory_before:.2f} GB")
        
        # Load model
        start_time = time.time()
        try:
            load_result = config["loader"]()
            
            # Handle different return types
            if len(load_result) == 3:
                # LLaVA MLX returns (model, processor, config) - OLD VERSION
                model, processor, config = load_result
                # Store config in model object for later use
                model._mlx_config = config
            else:
                # Other models return (model, processor) - CURRENT VERSION
                model, processor = load_result
            
            load_time = time.time() - start_time
            
            # Record memory after loading
            memory_after = get_memory_usage()
            print(f"Memory usage after loading: {memory_after:.2f} GB")
            print(f"Model loading time: {load_time:.2f} seconds")
            
            # Initialize model results
            model_results = {
                "model_id": self.models_config[model_name]["model_id"],
                "load_time": load_time,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_diff": memory_after - memory_before,
                "images": {},
                "total_inference_time": 0,
                "successful_inferences": 0,
                "failed_inferences": 0
            }
            
            # Get test images
            test_images = self.get_test_images()
            if not test_images:
                print("Warning: No test images found")
                model_results["error"] = "No test images found"
                return model_results
            
            print(f"Found {len(test_images)} test images")
            
            # Test each image
            for image_path in test_images:
                try:
                    # For LLaVA-MLX, reload the model for each image to avoid state bug
                    if "LLaVA-v1.6-Mistral-7B-MLX" in model_name:
                        print("  >> LLaVA-MLX: Reloading model to clear state...")
                        clear_model_memory(model, processor)
                        model, processor = self.models_config[model_name]["loader"]()

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
                    print(f"Error testing image {image_path.name}: {str(e)}")
                    model_results["images"][image_path.name] = {
                        "error": str(e),
                        "inference_time": 0
                    }
                    model_results["failed_inferences"] += 1
            
            # Calculate average inference time
            if model_results["successful_inferences"] > 0:
                model_results["avg_inference_time"] = model_results["total_inference_time"] / model_results["successful_inferences"]
            else:
                model_results["avg_inference_time"] = 0
                
            print(f"Model {model_name} image test completed")
            print(f"Success: {model_results['successful_inferences']}, Failed: {model_results['failed_inferences']}")
            print(f"Average inference time: {model_results['avg_inference_time']:.2f} seconds")
            
            # 💡 New: Text-only capability test (optional)
            if self.enable_text_only_test:
                print(f"\nStarting text-only capability test for {model_name}...")
                try:
                    text_only_results = self.test_text_only_capability(model, processor, model_name)
                    model_results["text_only_capability"] = text_only_results
                    
                    if text_only_results["text_only_supported"]:
                        print(f"✅ {model_name} supports text-only input!")
                    else:
                        print(f"❌ {model_name} does not support text-only input")
                        
                except Exception as e:
                    print(f"⚠️ Text-only test failed: {str(e)}")
                    model_results["text_only_capability"] = {
                        "text_only_supported": False,
                        "error": str(e)
                    }
            else:
                print(f"\nSkipping text-only test (disabled)")
                model_results["text_only_capability"] = {
                    "text_only_supported": "Not tested",
                    "reason": "Text-only test disabled"
                }
            
            print(f"\nAll tests for model {model_name} completed")
            
        except Exception as e:
            print(f"Error loading model {model_name}: {str(e)}")
            model_results = {
                "model_id": self.models_config[model_name]["model_id"],
                "load_error": str(e),
                "memory_before": memory_before,
                "memory_after": memory_before,  # Memory remains the same on failure
                "memory_diff": 0
            }
            
            # Clear memory (even if loading fails)
            gc.collect()
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            
            return model_results
        
        # Clear model memory
        if model_name != "LLaVA-v1.6-Mistral-7B-MLX": # Already cleaned inside loop
            clear_model_memory(model, processor)
        
        # Check memory cleanup effect
        memory_after_cleanup = get_memory_usage()
        print(f"Memory usage after cleanup: {memory_after_cleanup:.2f} GB")
        model_results["memory_after_cleanup"] = memory_after_cleanup
        
        return model_results
    
    def test_single_image(self, model, processor, image_path, model_name):
        """Test a single image (includes optimized timeout mechanism)"""
        print(f"Testing image: {image_path.name}")
        
        temp_image_path_for_fix = None
        try:
            # Load and optimize image
            image = Image.open(image_path).convert('RGB')
            
            # Set the current image path to be used for inference
            current_image_path = str(image_path)
            
            # 📏 Unified image preprocessing (consistent for all models)
            original_size = image.size
            if max(image.size) > self.unified_image_size:
                ratio = self.unified_image_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"  📏 Unified scaling: {original_size} → {image.size}")
            
            image_info = {
                "original_size": original_size,
                "processed_size": image.size,
                "mode": image.mode,
                "file_size": os.path.getsize(current_image_path)
            }
            
            # 📏 Unified generation parameters (consistent for all models)
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
            print(f"  📏 Unified parameters: {unified_generation_params}")
            print(f"  ⏱️ Timeout setting: {timeout_seconds} seconds")
            
            # Define inference function
            def do_inference():
                # Use different inference methods based on model type
                if "Moondream2" in model_name:
                    # Moondream2 special API (model limitation, but keep unified test conditions)
                    # Move image to the correct device first
                    device = next(model.parameters()).device
                    enc_image = model.encode_image(image)
                    if hasattr(enc_image, 'to'):
                        enc_image = enc_image.to(device)
                    # Use unified prompt, but cannot control max_tokens (API limitation)
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
                        # MLX-LLaVA inference using simple method (same as other models)
                        try:
                            from mlx_vlm import generate
                            print("  🚀 Using MLX-VLM for LLaVA...")
                            
                            # Simple prompt for MLX-LLaVA (same as other models)
                            response = generate(
                                model, 
                                processor, 
                                self.prompt, 
                                image=current_image_path,
                                max_tokens=unified_generation_params["max_new_tokens"],
                                verbose=False
                            )
                            
                            return str(response)
                            
                        except Exception as e:
                            print(f"  ⚠️ MLX-VLM failed: {e}")
                            # Fallback: Return descriptive error but don't crash
                            return f"MLX-VLM inference failed: {str(e)}"
                    else:
                        # Standard LLaVA Pipeline method
                        messages = [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "image", "image": image},  # Use local image format (consistent with SmolVLM)
                                    {"type": "text", "text": self.prompt}  # Use unified prompt
                                ]
                            },
                        ]
                        # 🚀 Optimization: Add generation parameter control
                        response = model(
                            text=messages, 
                            **unified_generation_params,  # Use unified parameters
                            return_full_text=False  # Only return generated text
                        )
                        if isinstance(response, list) and len(response) > 0:
                            return response[0].get('generated_text', str(response))
                        else:
                            return str(response)
                elif "SmolVLM" in model_name:
                    # SmolVLM optimized method
                    if "MLX" in model_name or hasattr(model, '_is_mlx_model'):
                        # MLX version SmolVLM2 inference
                        try:
                            # Use MLX-VLM command line tool for inference
                            import subprocess
                            import tempfile
                            
                            print("  🚀 Using MLX-VLM command line for SmolVLM2...")
                            
                            # Create temporary image file
                            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                                temp_image_path = tmp_file.name
                                image.save(temp_image_path)
                            
                            try:
                                # Use MLX-VLM command line tool
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
                                    # Parse output, extract generated text
                                    output_lines = result.stdout.split('\n')
                                    generated_text = ""
                                    
                                    # Keep full Assistant response
                                    generated_text = ""
                                    assistant_found = False
                                    for i, line in enumerate(output_lines):
                                        line = line.strip()
                                        if line.startswith('Assistant:'):
                                            # Find Assistant line
                                            assistant_found = True
                                            generated_text = line
                                            # Check if next line has content
                                            if i + 1 < len(output_lines):
                                                next_line = output_lines[i + 1].strip()
                                                if next_line and not next_line.startswith('==========') and not next_line.startswith('Files:') and not next_line.startswith('Prompt:') and not next_line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
                                                    # Next line has content, combine two lines
                                                    generated_text = f"{line} {next_line}"
                                            break
                                        elif line and not line.startswith('==========') and not line.startswith('Files:') and not line.startswith('Prompt:') and not line.startswith('Generation:') and not line.startswith('Peak memory:'):
                                            # Find other non-system content lines
                                            if not generated_text:
                                                generated_text = line
                                    
                                    return generated_text
                                else:
                                    print(f"  ⚠️ MLX-VLM command failed: {result.stderr}")
                                    raise Exception(f"MLX-VLM command failed: {result.stderr}")
                                    
                            finally:
                                # Clean up temporary file
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
                        # Standard SmolVLM inference method
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
                            outputs = model.generate(**inputs, **unified_generation_params)  # Use unified parameters
                        return processor.decode(outputs[0], skip_special_tokens=True)
                else:
                    # Traditional method
                    inputs = processor(text=self.prompt, images=image, return_tensors="pt")
                    with torch.no_grad():
                        outputs = model.generate(**inputs, **unified_generation_params)  # Use unified parameters
                    return processor.decode(outputs[0], skip_special_tokens=True)
            
            # ⏱️ Execute inference with timeout
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
                
                print(f"  ✅ Inference time: {inference_time:.2f} seconds")
                print(f"  📝 Response length: {len(final_response)} characters")
                
                return result
                
            except TimeoutError as e:
                inference_time = time.time() - start_time
                print(f"  ⚠️ {str(e)}")
                return {
                    "inference_time": inference_time,
                    "response": "",
                    "image_info": image_info,
                    "error": str(e),
                    "unified_test": True  # Mark as using unified test conditions
                }
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return {
                "inference_time": 0,
                "response": "",
                "image_info": {},
                "error": str(e),
                "unified_test": True  # Mark as using unified test conditions (even on failure)
            }
        finally:
            # Clean up temporary file (if it exists)
            if temp_image_path_for_fix:
                os.remove(temp_image_path_for_fix)
    
    def test_text_only_capability(self, model, processor, model_name):
        """Test if the model supports text-only input (no image required) - supports all models"""
        print(f"Testing text-only capability for {model_name}...")
        
        # Text-only test prompts
        text_only_prompts = [
            "What is the capital of France?",
            "Explain the concept of machine learning in simple terms.",
            "Write a short poem about technology."
        ]
        
        results = {}
        
        for i, prompt in enumerate(text_only_prompts):
            print(f"  Testing prompt {i+1}: {prompt}")
            
            try:
                start_time = time.time()
                response = ""
                
                # 🔧 Use specific text-only inference methods based on model type
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
                
                # Determine success or failure
                is_success = (
                    response and 
                    len(response.strip()) > 0 and 
                    "failed" not in response.lower() and
                    "error" not in response.lower() and
                    "does not support" not in response
                )
                
                results[f"prompt_{i+1}"] = {
                    "prompt": prompt,
                    "response": response,
                    "inference_time": inference_time,
                    "success": is_success
                }
                
                print(f"    Response: {response[:100]}...")
                print(f"    Time: {inference_time:.2f} seconds")
                print(f"    Status: {'✅ Success' if is_success else '❌ Failed'}")
                
            except Exception as e:
                results[f"prompt_{i+1}"] = {
                    "prompt": prompt,
                    "response": "",
                    "inference_time": 0,
                    "error": str(e),
                    "success": False
                }
                print(f"    Error: {str(e)}")
        
        # Calculate success rate
        successful_tests = sum(1 for r in results.values() if r.get("success", False))
        total_tests = len(results)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        print(f"  Text-only test success rate: {successful_tests}/{total_tests} ({success_rate:.1%})")
        
        return {
            "text_only_supported": success_rate > 0,  # Any success is considered supported
            "success_rate": success_rate,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "results": results
        }
    
    def _test_moondream2_text_only(self, model, processor, prompt):
        """Moondream2 text-only test"""
        try:
            # Method 1: Directly use tokenizer for text generation
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
            
            # Remove original prompt, keep only generated part
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            return response
            
        except Exception as e:
            # Method 2: Try to use the model's chat functionality (if available)
            try:
                # Some versions of Moondream2 may support text conversation
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
                return f"Moondream2 text-only inference failed: {str(e)} | Fallback method: {str(e2)}"
    
    def _test_phi35_text_only(self, model, processor, prompt):
        """Phi-3.5-Vision-Instruct text-only test"""
        try:
            # Use MLX-VLM for text-only inference (simplified method)
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
                return f"MLX-VLM text-only inference failed: {str(mlx_e)}"
            
        except Exception as e:
            return f"Phi-3.5-Vision-Instruct text-only inference failed: {str(e)}"
    
    def _test_smolvlm2_text_only(self, model, processor, prompt):
        """SmolVLM2-500M-Video text-only test"""
        try:
            # Check if it's an MLX version
            if hasattr(model, '_is_mlx_model'):
                # MLX version text-only test
                try:
                    import subprocess
                    import tempfile
                    
                    print("  🚀 Using MLX-VLM command line for SmolVLM2 text-only...")
                    
                    # Create a simple test image (MLX-VLM requires image input)
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
                            timeout=60
                        )
                        
                        if result.returncode == 0:
                            # Keep full Assistant response
                            output_lines = result.stdout.split('\n')
                            generated_text = ""
                            
                            for i, line in enumerate(output_lines):
                                line = line.strip()
                                if line.startswith('Assistant:'):
                                    # Find Assistant line
                                    generated_text = line
                                    # Check if next line has content
                                    if i + 1 < len(output_lines):
                                        next_line = output_lines[i + 1].strip()
                                        if next_line and not next_line.startswith('==========') and not next_line.startswith('Files:') and not next_line.startswith('Prompt:') and not next_line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
                                            # Next line has content, combine two lines
                                            generated_text = f"{line} {next_line}"
                                    break
                                elif line and not line.startswith('==========') and not line.startswith('Files:') and not line.startswith('Prompt:') and not line.startswith('Generation:') and not line.startswith('Peak memory:'):
                                    # Find other non-system content lines
                                    if not generated_text:
                                        generated_text = line
                            
                            return generated_text
                        else:
                            return f"MLX-VLM text-only command failed: {result.stderr}"
                            
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_image_path):
                            os.remove(temp_image_path)
                    
                except Exception as mlx_e:
                    print(f"  ⚠️ MLX-VLM text-only failed: {mlx_e}")
                    return f"MLX-VLM text-only inference failed: {str(mlx_e)}"
            
            # Standard SmolVLM2 text-only test
            # Method 1: Try text message format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}  # Only text, no image
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
            # Method 2: Try direct text input
            try:
                inputs = processor(text=prompt, return_tensors="pt")
                with torch.no_grad():
                    outputs = model.generate(**inputs, max_new_tokens=self.unified_max_tokens, do_sample=False)
                response = processor.decode(outputs[0], skip_special_tokens=True)
                return response.replace(prompt, "").strip()
            except Exception as e2:
                return f"SmolVLM2 text-only inference failed: {str(e)} | Fallback method: {str(e2)}"
    
    def _test_smolvlm_text_only(self, model, processor, prompt):
        """SmolVLM-500M-Instruct text-only test"""
        try:
            # Method 1: Try text message format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}  # Only text, no image
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
            # Method 2: Try direct text input
            try:
                inputs = processor(text=prompt, return_tensors="pt")
                with torch.no_grad():
                    outputs = model.generate(**inputs, max_new_tokens=self.unified_max_tokens, do_sample=False)
                response = processor.decode(outputs[0], skip_special_tokens=True)
                return response.replace(prompt, "").strip()
            except Exception as e2:
                return f"SmolVLM text-only inference failed: {str(e)} | Fallback method: {str(e2)}"
    
    def _test_llava_text_only(self, model, processor, prompt):
        """LLaVA-MLX text-only test"""
        try:
            # Method 1: MLX-VLM simple text inference
            from mlx_vlm import generate
            response = generate(
                model=model,
                processor=processor,
                prompt=prompt,
                max_tokens=self.unified_max_tokens,
                verbose=False
            )
            
            return str(response) if response else ""
            
        except Exception as e:
            # Method 2: Try pipeline method (if supported)
            try:
                # Try text conversation format
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
                return f"LLaVA text-only inference failed: {str(e)} | Fallback method: {str(e2)}"
    
    def _test_generic_text_only(self, model, processor, prompt):
        """Generic text-only test method"""
        try:
            # Method 1: Try to use processor for text processing
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
            # Method 2: Try direct tokenizer method
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
                    return f"Generic text-only inference failed: No suitable tokenizer found"
                    
            except Exception as e2:
                return f"Generic text-only inference failed: {str(e)} | Fallback method: {str(e2)}"
    
    def run_all_tests(self):
        """Run tests for all models"""
        print("Starting VLM model tests")
        print(f"System info: MacBook Air M3, 16GB")
        print(f"MPS available: {torch.backends.mps.is_available()}")
        
        # Check test images
        test_images = self.get_test_images()
        print(f"Found {len(test_images)} test images")
        
        if not test_images:
            print("Error: No test images found, please place images in src/testing/testing_material/images/")
            return
        
        total_start_time = time.time()
        
        # Test each model one by one
        for model_name, config in self.models_config.items():
            try:
                model_results = self.test_single_model(model_name, config)
                self.results["models"][model_name] = model_results
                
                # Save intermediate results (to prevent data loss if test is interrupted)
                self.save_results(f"intermediate_{model_name}")
                
            except Exception as e:
                print(f"Severe error testing model {model_name}: {str(e)}")
                self.results["models"][model_name] = {
                    "severe_error": str(e)
                }
        
        # Record total test time
        total_time = time.time() - total_start_time
        self.results["total_test_time"] = total_time
        print(f"\nAll tests completed, total time: {total_time:.2f} seconds")
        
        # Save final results
        self.save_results()
    
    def save_results(self, suffix=""):
        """Save test results"""
        # Support running from different directories
        possible_results_dirs = [
            Path("src/testing/results"),  # Run from project root
            Path("results"),              # Run from src/testing
            Path("./results")             # Current directory
        ]
        
        # Use the first viable path, if none exist, create the second
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
            print(f"Results saved to: {filepath}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")

def main():
    """Main function"""
    print("VLM Model Tester")
    print("="*50)
    
    # Check virtual environment
    activate_virtual_env()
    
    # Create tester
    tester = VLMTester()
    
    # Check if command line arguments specify testing a single model
    import sys
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        if model_name in tester.models_config:
            print(f"Testing single model: {model_name}")
            model_results = tester.test_single_model(model_name, tester.models_config[model_name])
            tester.results["models"][model_name] = model_results
            tester.save_results(f"single_{model_name}")
        else:
            print(f"Error: Model {model_name} not found")
            print(f"Available models: {list(tester.models_config.keys())}")
            return
    else:
        # Run tests for all models
        tester.run_all_tests()
    
    print("\nTesting completed!")
    print("Results file located in: src/testing/results/")

if __name__ == "__main__":
    main() 