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
from datetime import datetime
from pathlib import Path
from PIL import Image
import torch
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

# --- Model loader copied from vlm_tester.py ---

class VLMModelLoader:
    """VLM Model Loader - Consistent with vlm_tester.py"""
    
    @staticmethod
    def load_smolvlm2_video(model_id="HuggingFaceTB/SmolVLM2-500M-Video-Instruct"):
        from transformers import AutoProcessor, AutoModelForImageTextToText
        print(f"Loading {model_id}...")
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForImageTextToText.from_pretrained(model_id)
        return model, processor
    
    @staticmethod
    def load_smolvlm_instruct(model_id="HuggingFaceTB/SmolVLM-500M-Instruct"):
        from transformers import AutoProcessor, AutoModelForVision2Seq
        print(f"Loading {model_id}...")
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForVision2Seq.from_pretrained(model_id)
        return model, processor
    
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
            return model, processor
        except ImportError:
            raise RuntimeError("MLX-VLM package not installed (pip install mlx-vlm), cannot test this model.")
    
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
        
        # Test model configuration (same as vlm_tester.py)
        self.models_config = {
            "SmolVLM2-500M-Video-Instruct": { "loader": VLMModelLoader.load_smolvlm2_video, "model_id": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct" },
            "SmolVLM-500M-Instruct": { "loader": VLMModelLoader.load_smolvlm_instruct, "model_id": "HuggingFaceTB/SmolVLM-500M-Instruct" },
            "Moondream2": { "loader": VLMModelLoader.load_moondream2, "model_id": "vikhyatk/moondream2" },
            "LLaVA-v1.6-Mistral-7B-MLX": { "loader": VLMModelLoader.load_llava_mlx, "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit" },
            "Phi-3.5-Vision-Instruct": { "loader": VLMModelLoader.load_phi3_vision, "model_id": "lokinfey/Phi-3.5-vision-mlx-int4" }
        }
        
        # 📏 Unified test conditions
        self.unified_max_tokens = 100  # Match vlm_tester.py setting
        self.unified_image_size = 1024
        
        # 🧠 Context understanding test prompts (keeping original prompts unchanged)
        self.seeding_prompt = "You are a forensic expert. Describe this image in extreme detail, listing every object, person, color, and spatial relationship you can identify. This is for a critical investigation."
        self.recall_questions = [
            "What were the most prominent colors in the image?",
            "Were there any people visible in the image? If so, describe their general appearance or clothing without making up details.",
            "Summarize the main subject or scene of the image in one sentence."
        ]
        
        # 💡 Context understanding testing strategy
        # Maintain conversation history to test models' ability to understand context

    def get_test_images(self):
        """Get test image list (same as vlm_tester.py)"""
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
        """Execute context understanding tests for all models"""
        print("="*60)
        print("🤖 Starting VLM Model Context Understanding Testing 🤖")
        print("="*60)
        
        test_images = self.get_test_images()
        if not test_images:
            print("❌ Error: No test images found. Please ensure images are located in src/testing/testing_material/images/")
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
                
                # ✅ FIXED: Reload LLaVA for each image to avoid state bug (same as vlm_tester.py)
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
                    # Build conversation with history
                    conversation = []
                    
                    # Add conversation history (filter out image tokens for text-only questions)
                    for hist_entry in history:
                        if image is None:
                            # For text-only questions, filter out image tokens from history
                            if hist_entry["role"] == "user" and isinstance(hist_entry["content"], list):
                                text_content = [item for item in hist_entry["content"] if item["type"] != "image"]
                                if text_content:
                                    conversation.append({"role": hist_entry["role"], "content": text_content})
                            else:
                                conversation.append(hist_entry)
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
                        # Without image: Moondream2 doesn't handle pure text well with conversation history
                        # Try to use the prompt directly as it's context-based
                        try:
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
                            # Remove the original prompt from response
                            if prompt in response:
                                response = response.replace(prompt, "").strip()
                        except Exception as e:
                            response = f"Error: Moondream2 context-based inference failed - {str(e)}"

                # --------------------------------------------------------------------------
                # Branch 3: MLX models (LLaVA, Phi-3.5) - IMPROVED for context
                # --------------------------------------------------------------------------
                elif "Phi-3.5" in model_name:
                    # Check if this is an MLX model or transformers model
                    try:
                        # Use MLX inference - it's much faster than transformers
                        from mlx_vlm import generate
                        print("  🚀 Using MLX inference for Phi-3.5-Vision...")
                        
                        # Build simplified prompt for Phi-3.5
                        if image:
                            # Use simple format for image description
                            mlx_prompt = f"<|image_1|>\\nDescribe this image in detail:\\n"
                            temp_image_path = "temp_mlx_image.png"
                            image.save(temp_image_path)
                            response = generate(
                                model=model, 
                                processor=processor, 
                                image=temp_image_path, 
                                prompt=mlx_prompt,
                                max_tokens=self.unified_max_tokens,
                                temp=0.1,  # Very low temperature for focused output
                                repetition_penalty=1.5,  # Strong repetition penalty to avoid repeats
                                top_p=0.9,  # Lower top_p for more focused generation
                                verbose=False
                            )
                            if os.path.exists(temp_image_path):
                                os.remove(temp_image_path)
                        else:
                            # Context-based question - use simple format
                            mlx_prompt = f"Question: {prompt}\\nAnswer:"
                            response = generate(
                                model=model, 
                                processor=processor, 
                                prompt=mlx_prompt,
                                max_tokens=self.unified_max_tokens,
                                temp=0.1,  # Very low temperature for focused output
                                repetition_penalty=1.5,  # Strong repetition penalty to avoid repeats
                                top_p=0.9,  # Lower top_p for more focused generation
                                verbose=False
                            )
                        
                        # Handle MLX response format
                        if isinstance(response, tuple) and len(response) >= 2:
                            text_response = response[0]
                        elif isinstance(response, list) and len(response) > 0:
                            text_response = response[0] if isinstance(response[0], str) else str(response[0])
                        else:
                            text_response = str(response)
                        
                        # Enhanced cleaning for Phi-3.5 specific issues
                        text_response = text_response.replace("<|end|><|endoftext|>", " ").replace("<|end|>", " ").replace("<|endoftext|>", " ")
                        
                        # Remove training data artifacts
                        if "1. What is meant by" in text_response:
                            text_response = text_response.split("1. What is meant by")[0].strip()
                        
                        # Remove markdown artifacts and problem statements
                        if "# Problem" in text_response:
                            text_response = text_response.split("# Problem")[0].strip()
                        if "## Why is it important" in text_response:
                            text_response = text_response.split("## Why is it important")[0].strip()
                        
                        # Remove the original prompt from the response if it appears
                        if prompt in text_response:
                            text_response = text_response.replace(prompt, "").strip()
                        
                        # Remove common MLX prompt patterns
                        patterns_to_remove = [
                            "<|image_1|>",
                            "User:",
                            "Assistant:",
                            "\\nUser:",
                            "\\nAssistant:",
                            "Question:",
                            "Answer:"
                        ]
                        for pattern in patterns_to_remove:
                            text_response = text_response.replace(pattern, "").strip()
                        
                        # Remove repetitive sentences (fix for Phi-3.5 repetition issue)
                        sentences = text_response.split('.')
                        unique_sentences = []
                        seen_sentences = set()
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if sentence and sentence not in seen_sentences:
                                unique_sentences.append(sentence)
                                seen_sentences.add(sentence)
                        text_response = '. '.join(unique_sentences)
                        
                        # Clean up whitespace and ensure proper ending
                        text_response = ' '.join(text_response.split())
                        if text_response and not text_response.endswith('.'):
                            text_response += '.'
                        
                        response = text_response
                        
                    except Exception as e:
                        print(f"  ⚠️ MLX inference failed ({e}), using fallback...")
                        response = f"Error: MLX inference failed - {str(e)}"

                elif "LLaVA" in model_name:
                    from mlx_vlm import generate
                    if image is not None:
                        # Use direct image path approach like vlm_tester.py
                        # Save the processed image to a temporary file
                        temp_image_path = "temp_mlx_image.png"
                        image.save(temp_image_path)
                        try:
                            raw_response = generate(
                                model, processor, prompt, image=temp_image_path,
                                max_tokens=self.unified_max_tokens, verbose=False
                            )
                        finally:
                            if os.path.exists(temp_image_path):
                                os.remove(temp_image_path)
                    else:
                        # Context-based question without image
                        # Use a simple prompt format that works better with LLaVA
                        context_prompt = f"Question: {prompt}"
                        raw_response = generate(
                            model, processor, context_prompt,
                            max_tokens=self.unified_max_tokens, verbose=False
                        )
                    
                    # Process MLX response
                    if isinstance(raw_response, tuple) and len(raw_response) >= 2:
                        response = raw_response[0]
                    elif isinstance(raw_response, list) and len(raw_response) > 0:
                        response = raw_response[0] if isinstance(raw_response[0], str) else str(raw_response[0])
                    else:
                        response = str(raw_response)

                    # Clean up stop tokens
                    stop_tokens = ["<|end|>", "<|endoftext|>", "ASSISTANT:", "USER:", "<|im_end|>"]
                    for token in stop_tokens:
                        response = response.replace(token, "")
                    
                    response = response.replace("<|end|><|endoftext|>", " ")
                    
                    if "1. What is meant by" in response:
                        response = response.split("1. What is meant by")[0].strip()
                    
                    response = ' '.join(response.split()).strip()
                
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
            print(f"⚠️ {str(e)}")
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
        
        # Use first viable path
        results_dir = next((path for path in possible_results_dirs if path.is_dir() or path.parent.is_dir()), Path("results"))
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

if __name__ == "__main__":
    main() 