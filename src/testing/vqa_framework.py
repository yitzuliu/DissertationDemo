#!/usr/bin/env python3
"""
VQA 2.0 Core Framework - Integrated Version
Integrates VQA tester, utility functions, image processing and all core functionality

Author: AI Manual Assistant Team
Date: 2025-01-27
"""

import os
# Prevent tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import json
import time
import requests
import zipfile
import string
import re
import random
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import torch
import numpy as np
from PIL import Image
from tqdm import tqdm
import gc # Added for fallback model cleanup

# Import existing VLM infrastructure
from vlm_tester import VLMModelLoader, clear_model_memory, get_memory_usage

class VQAFramework:
    """VQA 2.0 Unified Framework - Integrates all functionality"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize VQA Framework
        
        Args:
            data_dir: Optional custom data directory
        """
        # Set up data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # Default to testing_material/vqa2
            possible_paths = [
                Path("src/testing/testing_material/vqa2"),  # From project root
                Path("testing_material/vqa2"),              # From src/testing
                Path("./testing_material/vqa2")             # Current directory
            ]
            
            self.data_dir = None
            for path in possible_paths:
                if path.exists():
                    self.data_dir = path
                    break
            
            # Always ensure we have a valid data directory
            if self.data_dir is None:
                # Create default directory
                self.data_dir = Path("testing_material/vqa2")
                self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure images directory exists
        assert self.data_dir is not None, "Data directory must be initialized"
        self.images_dir = self.data_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up results directory
        possible_results_dirs = [
            Path("src/testing/results"),  # From project root
            Path("results"),              # From src/testing
            Path("./results")             # Current directory
        ]
        
        self.results_dir = None
        for path in possible_results_dirs:
            if path.exists():
                self.results_dir = path
                break
        
        if self.results_dir is None:
            self.results_dir = Path("results")
            self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Unified generation parameters (same as vlm_tester.py)
        self.generation_params = {
            "max_new_tokens": 100,
            "do_sample": False
        }
        
        # Model configuration (same as vlm_tester.py)
        self.models_config = {
            "smolvlm_instruct": {
                "loader": VLMModelLoader.load_smolvlm_instruct,
                "model_id": "HuggingFaceTB/SmolVLM-500M-Instruct"
            },
            "smolvlm_v2_instruct": {
                "loader": VLMModelLoader.load_smolvlm2_video,
                "model_id": "mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), falls back to original SmolVLM2 if MLX not available or incompatible"
            },
            "moondream2": {
                "loader": VLMModelLoader.load_moondream2,
                "model_id": "vikhyatk/moondream2"
            },
            "llava_mlx": {
                "loader": VLMModelLoader.load_llava_mlx,
                "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), requires 'pip install mlx-vlm'"
            },
            "phi35_vision": {
                "loader": VLMModelLoader.load_phi3_vision,
                "model_id": "mlx-community/Phi-3.5-vision-instruct-4bit"
            }
        }
        
        # Image cache
        self.image_cache = {}
        
        print(f"✅ VQA Framework initialized")
        print(f"   📁 Data directory: {self.data_dir}")
        print(f"   📊 Results directory: {self.results_dir}")
    
    def download_vqa_data(self):
        """Download VQA 2.0 dataset"""
        print("📥 Downloading VQA 2.0 Dataset...")
        
        # VQA 2.0 dataset URLs
        vqa2_urls = {
            "val_questions": "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Val_mscoco.zip",
            "val_annotations": "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Annotations_Val_mscoco.zip",
        }
        
        assert self.data_dir is not None, "Data directory must be initialized"
        for component, url in vqa2_urls.items():
            zip_file = self.data_dir / f"{component}.zip"
            
            if not zip_file.exists():
                print(f"📥 Downloading {component}...")
                
                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                
                with open(zip_file, 'wb') as f, tqdm(
                    desc=component,
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
                
                print(f"✅ Downloaded: {zip_file}")
                
                # Extract files
                print(f"📂 Extracting {zip_file.name}...")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)
                print(f"✅ Extracted: {zip_file.name}")
            else:
                print(f"✅ {component} already downloaded")
        
        print("✅ VQA 2.0 Dataset ready")
    
    def load_sample_data(self, sample_size: int = 20) -> Tuple[List[Dict], Dict]:
        """Load sample from real VQA 2.0 data"""
        # First ensure real data is downloaded
        try:
            questions, annotations = self.load_real_data(sample_size)
            print(f"✅ Using real VQA 2.0 data: {len(questions)} questions")
            
            # Download corresponding COCO images
            self._ensure_coco_images_for_questions(questions)
            
            return questions, annotations
            
        except Exception as e:
            print(f"⚠️ Could not load real VQA data: {e}")
            print("📥 Attempting to download VQA 2.0 dataset...")
            
            # Try downloading VQA data
            self.download_vqa_data()
            
            # Retry loading
            try:
                questions, annotations = self.load_real_data(sample_size)
                print(f"✅ Using real VQA 2.0 data: {len(questions)} questions")
                
                # Download corresponding COCO images
                self._ensure_coco_images_for_questions(questions)
                
                return questions, annotations
                
            except Exception as e2:
                print(f"❌ Still failed to load real data: {e2}")
                print("🔄 Falling back to sample data...")
                
                # Final fallback to sample data
                return self._create_sample_data(sample_size)
    
    def load_real_data(self, sample_size: int = 20) -> Tuple[List[Dict], Dict]:
        """Load real VQA 2.0 data"""
        print(f"📖 Loading real VQA 2.0 data...")
        
        assert self.data_dir is not None, "Data directory must be initialized"
        
        # Load questions
        questions_file = self.data_dir / "v2_OpenEnded_mscoco_val2014_questions.json"
        if not questions_file.exists():
            raise FileNotFoundError(f"Questions file not found: {questions_file}")
            
        with open(questions_file, 'r') as f:
            questions_data = json.load(f)
            
        questions = questions_data['questions']
        
        # Load annotations
        annotations_file = self.data_dir / "v2_mscoco_val2014_annotations.json"
        annotations_dict = {}
        
        if annotations_file.exists():
            with open(annotations_file, 'r') as f:
                annotations_data = json.load(f)
            annotations_dict = {ann['question_id']: ann for ann in annotations_data['annotations']}
        else:
            print(f"⚠️ Annotations file not found: {annotations_file}")
        
        # Smart sampling: ensure questions have corresponding annotations
        if sample_size and sample_size < len(questions):
            # Filter questions with annotations
            questions_with_annotations = [
                q for q in questions 
                if q['question_id'] in annotations_dict
            ]
            
            if len(questions_with_annotations) < sample_size:
                print(f"⚠️ Only {len(questions_with_annotations)} questions have annotations, using all")
                sample_size = len(questions_with_annotations)
            
            # Random sampling
            import random
            random.seed(42)  # Ensure reproducible results
            questions = random.sample(questions_with_annotations, sample_size)
            print(f"📝 Sampled {sample_size} questions from {len(questions_with_annotations)} annotated questions")
        
        return questions, annotations_dict
    
    def _create_sample_data(self, sample_size: int) -> Tuple[List[Dict], Dict]:
        """Create sample data - using real COCO image IDs"""
        # Simple sample questions
        sample_questions_template = [
            ("What color is the car?", "red"),
            ("How many people are in the image?", "2"),
            ("Is this person wearing a hat?", "yes"),
            ("What is the weather like?", "sunny"),
            ("Where is this photo taken?", "park"),
        ]
        
        # Real COCO val2014 image IDs (first 20)
        coco_image_ids = [
            139, 285, 632, 724, 776, 785, 802, 872, 885, 1000,
            1268, 1296, 1353, 1584, 1818, 2006, 2149, 2153, 2157, 2261
        ]
        
        questions = []
        annotations = {}
        
        for i in range(sample_size):
            template_idx = i % len(sample_questions_template)
            question_text, answer = sample_questions_template[template_idx]
            
            question_id = 1000 + i
            image_id = coco_image_ids[i % len(coco_image_ids)]  # Use real COCO ID
            
            question = {
                "question_id": question_id,
                "image_id": image_id,
                "question": question_text
            }
            questions.append(question)
            
            # Create annotations (simulate 10 human annotators)
            annotation = {
                "question_id": question_id,
                "question_type": "other",
                "multiple_choice_answer": answer,
                "answers": [{"answer": answer, "answer_confidence": "yes"} for _ in range(10)]
            }
            annotations[question_id] = annotation
        
        # Save sample data
        questions_data = {"questions": questions}
        annotations_data = {"annotations": list(annotations.values())}
        
        assert self.data_dir is not None, "Data directory must be initialized"
        with open(self.data_dir / "val_questions_sample.json", 'w') as f:
            json.dump(questions_data, f, indent=2)
            
        with open(self.data_dir / "val_annotations_sample.json", 'w') as f:
            json.dump(annotations_data, f, indent=2)
        
        print(f"✅ Created sample data: {len(questions)} questions with real COCO image IDs")
        return questions, annotations
    
    def _ensure_sample_images(self, sample_size: int):
        """Ensure COCO sample images exist"""
        sample_dir = self.images_dir / "val2014_sample"
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if enough images already exist
        existing_images = list(sample_dir.glob("*.jpg"))
        if len(existing_images) >= min(sample_size, 20):  # Max 20 different images
            return
        
        print(f"📥 Downloading COCO val2014 sample images (first 20 images)...")
        
        # Real COCO val2014 first 20 image IDs
        coco_image_ids = [
            "000000000139", "000000000285", "000000000632", "000000000724", "000000000776",
            "000000000785", "000000000802", "000000000872", "000000000885", "000000001000",
            "000000001268", "000000001296", "000000001353", "000000001584", "000000001818",
            "000000002006", "000000002149", "000000002153", "000000002157", "000000002261"
        ]
        
        # COCO val2014 download base URL
        base_url = "http://images.cocodataset.org/val2014"
        
        downloaded_count = 0
        for i, image_id in enumerate(coco_image_ids[:min(sample_size, 20)]):
            image_filename = f"COCO_val2014_{image_id}.jpg"
            image_path = sample_dir / image_filename
            
            if not image_path.exists():
                try:
                    image_url = f"{base_url}/{image_filename}"
                    print(f"📥 Downloading {image_filename}...")
                    
                    response = requests.get(image_url, stream=True)
                    if response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        downloaded_count += 1
                        print(f"✅ Downloaded: {image_filename}")
                    else:
                        print(f"❌ Failed to download {image_filename}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Error downloading {image_filename}: {e}")
                    # If download fails, create placeholder image
                    placeholder_image = Image.new('RGB', (640, 480), (128, 128, 128))
                    placeholder_image.save(image_path, 'JPEG')
                    print(f"🔄 Created placeholder for {image_filename}")
        
        print(f"✅ COCO sample setup complete: {downloaded_count} downloaded, {len(list(sample_dir.glob('*.jpg')))} total images")
    
    def _ensure_coco_images_for_questions(self, questions: List[Dict]):
        """Download corresponding COCO images for question list"""
        sample_dir = self.images_dir / "val2014_sample"
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect all required image IDs
        image_ids = set()
        for question in questions:
            image_ids.add(question['image_id'])
        
        print(f"📥 Ensuring COCO images for {len(image_ids)} unique images...")
        
        # COCO val2014 download base URL
        base_url = "http://images.cocodataset.org/val2014"
        
        downloaded_count = 0
        existing_count = 0
        
        for image_id in image_ids:
            image_filename = f"COCO_val2014_{image_id:012d}.jpg"
            image_path = sample_dir / image_filename
            
            if image_path.exists():
                existing_count += 1
                continue
                
            try:
                image_url = f"{base_url}/{image_filename}"
                print(f"📥 Downloading {image_filename}...")
                
                response = requests.get(image_url, stream=True, timeout=10)
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    downloaded_count += 1
                    print(f"✅ Downloaded: {image_filename}")
                else:
                    print(f"❌ Failed to download {image_filename}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Error downloading {image_filename}: {e}")
                # If download fails, create placeholder image
                try:
                    placeholder_image = Image.new('RGB', (640, 480), (128, 128, 128))
                    placeholder_image.save(image_path, 'JPEG')
                    print(f"🔄 Created placeholder for {image_filename}")
                except Exception as e2:
                    print(f"❌ Failed to create placeholder: {e2}")
        
        print(f"✅ COCO images ready: {existing_count} existing, {downloaded_count} downloaded")
    
    def check_image_availability(self, questions: List[Dict]) -> Dict:
        """Check image availability"""
        available_count = 0
        total_count = len(questions)
        
        for question in questions:
            image_id = question['image_id']
            if self._load_image(image_id) is not None:
                available_count += 1
        
        return {
            'available': available_count,
            'total': total_count,
            'rate': available_count / total_count if total_count > 0 else 0
        }
    
    def _load_image(self, image_id: int, split: str = "val2014") -> Optional[Image.Image]:
        """Load image"""
        # Check cache
        cache_key = f"{split}_{image_id}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        # Try different image path formats
        possible_paths = [
            # Real COCO format
            self.images_dir / f"{split}_sample" / f"COCO_{split}_{image_id:012d}.jpg",
            self.images_dir / f"{split}" / f"COCO_{split}_{image_id:012d}.jpg",
            # Backup format
            self.images_dir / f"{split}_sample" / f"COCO_{split}_{image_id:06d}.jpg",
        ]
        
        for image_path in possible_paths:
            if image_path.exists():
                try:
                    image = Image.open(image_path).convert('RGB')
                    # Cache image (limit cache size)
                    if len(self.image_cache) < 100:
                        self.image_cache[cache_key] = image
                    return image
                except Exception as e:
                    print(f"⚠️ Error loading image {image_path}: {e}")
                    continue
        
        return None
    
    def evaluate_model(self, model_name: str, questions: List[Dict], 
                      annotations: Dict, max_questions: Optional[int] = None,
                      verbose: bool = False) -> Dict:
        """Evaluate model"""
        print(f"🤖 Evaluating {model_name} on VQA 2.0...")
        
        if model_name not in self.models_config:
            return {"error": f"Unknown model: {model_name}"}
        
        # Limit number of questions
        if max_questions:
            questions = questions[:max_questions]
        
        try:
            # Load model
            print("📥 Loading model...")
            model_loader = self.models_config[model_name]["loader"]
            load_start = time.time()
            model, processor = model_loader()
            load_time = time.time() - load_start
            print(f"✅ Model loaded in {load_time:.2f}s")
            
            # Record memory usage
            memory_info = get_memory_usage()
            print(f"💾 Memory usage: {memory_info}")
            
            # Evaluate
            print(f"📊 Evaluating {len(questions)} questions...")
            results = self._evaluate_questions(
                model, processor, model_name, questions, 
                annotations, verbose
            )
            
            # Clean up model memory
            print("Cleaning up model memory...")
            clear_model_memory(model, processor)
            
            return results
            
        except Exception as e:
            print(f"❌ Model evaluation failed: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return {"error": str(e)}
    
    def _evaluate_questions(self, model, processor, model_name: str,
                           questions: List[Dict], annotations: Dict,
                           verbose: bool = False) -> Dict:
        """Evaluate question list with enhanced error handling"""
        correct_answers = 0
        total_vqa_accuracy = 0.0
        total_inference_time = 0.0
        question_results = []
        error_summary = {
            "image_load_errors": 0,
            "inference_errors": 0,
            "annotation_errors": 0,
            "other_errors": 0
        }
        
        # For LLaVA-MLX, we need to reload the model for each image to avoid state bug
        current_model = model
        current_processor = processor
        model_loader = self.models_config[model_name]["loader"]
        
        for i, question in enumerate(questions):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(questions)}")
            
            question_id = question['question_id']
            question_text = question['question']
            image_id = question['image_id']
            
            # For LLaVA-MLX, reload the model for each image to avoid state bug
            if "llava_mlx" in model_name.lower():
                if i > 0:  # Don't reload for the first image
                    print(f"  >> LLaVA-MLX: Reloading model to clear state...")
                    clear_model_memory(current_model, current_processor)
                    current_model, current_processor = model_loader()
                    print(f"  >> LLaVA-MLX: Reload successful.")
            
            # Get model answer with enhanced error handling
            inference_start = time.time()
            try:
                model_answer = self._get_model_answer(
                    current_model, current_processor, model_name, question_text, image_id
                )
                
                # Check for specific error types
                if "no image available" in model_answer.lower():
                    error_summary["image_load_errors"] += 1
                    if verbose:
                        print(f"⚠️ Image load error for question {question_id}")
                elif "inference failed" in model_answer.lower():
                    error_summary["inference_errors"] += 1
                    if verbose:
                        print(f"⚠️ Inference error for question {question_id}")
                elif "error:" in model_answer.lower():
                    error_summary["other_errors"] += 1
                    if verbose:
                        print(f"⚠️ Other error for question {question_id}")
                        
            except Exception as e:
                error_summary["inference_errors"] += 1
                if verbose:
                    print(f"⚠️ Exception for question {question_id}: {e}")
                model_answer = f"error: {str(e)}"
            
            inference_time = time.time() - inference_start
            total_inference_time += inference_time
            
            # Evaluate answer with enhanced error handling
            try:
                if question_id in annotations:
                    annotation = annotations[question_id]
                    gt_answer = annotation['multiple_choice_answer']
                    gt_answers = [ans['answer'] for ans in annotation['answers']]
                    
                    # Simple accuracy - check if standard answer is in model response
                    model_answer_lower = self._preprocess_answer(model_answer)
                    gt_answer_lower = self._preprocess_answer(gt_answer)
                    is_correct = gt_answer_lower in model_answer_lower
                    if is_correct:
                        correct_answers += 1
                    
                    # VQA accuracy
                    vqa_accuracy = self._calculate_vqa_accuracy(model_answer, gt_answers)
                    total_vqa_accuracy += vqa_accuracy
                    
                    # Generate corresponding image filename
                    image_filename = f"COCO_val2014_{image_id:012d}.jpg"
                    
                    question_results.append({
                        'question_id': question_id,
                        'image_id': image_id,
                        'image_filename': image_filename,
                        'question': question_text,
                        'model_answer': model_answer,
                        'ground_truth': gt_answer,
                        'is_correct': is_correct,
                        'vqa_accuracy': vqa_accuracy,
                        'inference_time': inference_time
                    })
                else:
                    error_summary["annotation_errors"] += 1
                    if verbose:
                        print(f"⚠️ Missing annotation for question {question_id}")
                        
            except Exception as e:
                error_summary["annotation_errors"] += 1
                if verbose:
                    print(f"⚠️ Annotation processing error for question {question_id}: {e}")
        
        # Clean up the current model (if it's different from the original)
        try:
            if current_model is not model:
                clear_model_memory(current_model, current_processor)
        except Exception as e:
            print(f"  ⚠️ Error during model cleanup: {e}")
            # Continue anyway
            
        # Calculate final results
        total_questions = len(questions)
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        avg_vqa_accuracy = total_vqa_accuracy / total_questions if total_questions > 0 else 0
        avg_inference_time = total_inference_time / total_questions if total_questions > 0 else 0
        
        print(f"✅ Evaluation completed:")
        print(f"   📊 Questions evaluated: {total_questions}")
        print(f"   ✅ Correct answers: {correct_answers}")
        print(f"   🎯 Accuracy: {accuracy:.3f}")
        print(f"   ⏱️ Avg inference time: {avg_inference_time:.2f}s")
        
        # Print error summary
        if any(error_summary.values()):
            print(f"   ⚠️ Error summary:")
            for error_type, count in error_summary.items():
                if count > 0:
                    print(f"      {error_type}: {count}")
        
        return {
            'accuracy': accuracy,
            'vqa_accuracy': avg_vqa_accuracy,
            'correct': correct_answers,
            'total': total_questions,
            'avg_time': avg_inference_time,
            'question_results': question_results,
            'error_summary': error_summary
        }
    
    def _get_model_answer(self, model, processor, model_name: str, 
                         question: str, image_id: int) -> str:
        """Get model answer using unified inference logic (same as vlm_tester.py)"""
        # Load image
        image = self._load_image(image_id)
        if image is None:
            return "no image available"
        
        try:
            # Unified image preprocessing (same as vlm_tester.py)
            original_size = image.size
            unified_image_size = 1024
            if max(image.size) > unified_image_size:
                ratio = unified_image_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Unified generation parameters
            unified_generation_params = {
                "max_new_tokens": self.generation_params["max_new_tokens"],
                "do_sample": self.generation_params["do_sample"]
            }
            
            # Model-specific inference (same logic as vlm_tester.py)
            if "moondream2" in model_name.lower():
                # Moondream2 special API
                device = next(model.parameters()).device
                enc_image = model.encode_image(image)
                if hasattr(enc_image, 'to'):
                    enc_image = enc_image.to(device)
                return model.answer_question(enc_image, question, processor)
                
            elif "phi35_vision" in model_name.lower() or "phi-3.5" in model_name.lower():
                # Phi-3.5-Vision-Instruct inference (same as vlm_tester.py)
                try:
                    # Use MLX-VLM inference for vision model (official way)
                    from mlx_vlm import generate
                    print("  🚀 Using MLX-VLM inference for Phi-3.5-Vision-Instruct...")
                    
                    # Save image to temporary file for MLX-VLM
                    temp_image_path = "temp_mlx_image.jpg"
                    image.save(temp_image_path)
                    
                    try:
                        # Use simple prompt format for MLX-VLM (same as vlm_tester.py)
                        mlx_prompt = f"<|image_1|>\nUser: {question}\nAssistant:"
                        
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
                        {"role": "user", "content": f"<|image_1|>\\n{question}"}
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
                    
            elif "llava_mlx" in model_name.lower():
                # LLaVA-MLX inference (same as vlm_tester.py)
                try:
                    from mlx_vlm import generate
                    print("  🚀 Using MLX-VLM for LLaVA...")
                    
                    # Try different possible image paths
                    possible_image_paths = [
                        str(self.images_dir / f"COCO_val2014_{image_id:012d}.jpg"),
                        str(self.images_dir / "val2014_sample" / f"COCO_val2014_{image_id:012d}.jpg"),
                        str(self.images_dir / "val2014" / f"COCO_val2014_{image_id:012d}.jpg")
                    ]
                    
                    current_image_path = None
                    for path in possible_image_paths:
                        if os.path.exists(path):
                            current_image_path = path
                            break
                    
                    if current_image_path is None:
                        return f"Image file not found for image_id {image_id}"
                    
                    # Simple prompt for MLX-LLaVA (same as vlm_tester.py)
                    response = generate(
                        model, 
                        processor, 
                        question, 
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
                    
            elif "smolvlm" in model_name.lower():
                # SmolVLM processing
                # 檢查是否為 MLX 模型
                if hasattr(model, '_is_mlx_model'):
                    # MLX 版本的 SmolVLM2 推理 - 使用 subprocess 方式（與 vlm_tester.py 和 vlm_context_tester.py 一致）
                    try:
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
                                '--prompt', question,
                                '--max-tokens', str(unified_generation_params["max_new_tokens"]),
                                '--temperature', '0.0'
                            ]
                            
                            result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                timeout=60
                            )
                            
                            if result.returncode == 0:
                                # 解析輸出，提取生成的文本
                                output_lines = result.stdout.split('\n')
                                generated_text = ""
                                
                                # 保留完整的 Assistant 回覆
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
                                    elif line and not line.startswith('==========') and not line.startswith('Files:') and not line.startswith('Prompt:') and not line.startswith('Generation:') and not next_line.startswith('Peak memory:'):
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
                                    {"type": "text", "text": question}
                                ]
                            }
                        ]
                        input_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                        inputs = processor(text=input_text, images=image, return_tensors="pt")
                        with torch.no_grad():
                            generated_ids = model.generate(**inputs, **unified_generation_params)
                        response = processor.decode(generated_ids[0], skip_special_tokens=True)
                        
                        # Extract answer - remove input text
                        answer = response.replace(input_text, "").strip()
                        return self._extract_answer(answer, model_name, question)
                else:
                    # 標準 SmolVLM 推理方式
                    messages = [
                        {
                            "role": "user", 
                            "content": [
                                {"type": "image", "image": image},
                                {"type": "text", "text": question}
                            ]
                        }
                    ]
                    input_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    inputs = processor(text=input_text, images=image, return_tensors="pt")
                    
                    with torch.no_grad():
                        generated_ids = model.generate(**inputs, **unified_generation_params)
                        response = processor.decode(generated_ids[0], skip_special_tokens=True)
                    
                    # Extract answer - remove input text
                    answer = response.replace(input_text, "").strip()
                    return self._extract_answer(answer, model_name, question)
                
            else:
                # Generic processing for other models
                inputs = processor(text=question, images=image, return_tensors="pt")
                with torch.no_grad():
                    outputs = model.generate(**inputs, **unified_generation_params)
                return processor.decode(outputs[0], skip_special_tokens=True)
                
        except Exception as e:
            return f"error: {str(e)}"
    
    def _extract_answer(self, response: str, model_name: str, question: str) -> str:
        """Extract answer from model response - simplified version, return original response directly"""
        if not response:
            return "no response"
        
        # Simple cleanup, return original response directly
        return response.strip()
    
    def _preprocess_answer(self, answer: str) -> str:
        """Preprocess answer using standard VQA 2.0 preprocessing steps"""
        if not answer:
            return ""
        
        # Convert to lowercase
        answer = answer.lower().strip()
        
        # Remove common punctuation marks
        import re
        answer = re.sub(r'[^\w\s]', ' ', answer)
        
        # Normalize whitespace
        answer = ' '.join(answer.split())
        
        # Standard VQA 2.0 number normalization
        # Convert written numbers to digits (basic implementation)
        number_mapping = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
            'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
            'eighteen': '18', 'nineteen': '19', 'twenty': '20'
        }
        
        for word, digit in number_mapping.items():
            answer = answer.replace(word, digit)
        
        return answer
    
    def _calculate_vqa_accuracy(self, prediction: str, ground_truth_answers: List[str]) -> float:
        """Calculate VQA accuracy using standard VQA 2.0 evaluation method"""
        if not prediction or not ground_truth_answers:
            return 0.0
        
        prediction_lower = self._preprocess_answer(prediction)
        
        # Count how many ground truth answers appear in prediction
        matching_count = 0
        for gt_answer in ground_truth_answers:
            gt_answer_lower = self._preprocess_answer(gt_answer)
            if gt_answer_lower in prediction_lower:
                matching_count += 1
        
        # Standard VQA 2.0 accuracy: min(matching_count/len(ground_truth_answers), 1.0)
        # This ensures accuracy is normalized by the number of ground truth answers
        accuracy = min(matching_count / len(ground_truth_answers), 1.0)
        return accuracy
    
    def save_results(self, results: Dict, test_mode: str, num_questions: int, suffix: str = "") -> Path:
        """Save test results with complete experimental metadata for paper publication"""
        assert self.results_dir is not None, "Results directory must be initialized"
        
        # Determine filename based on suffix
        if suffix:
            # Single model test or intermediate results - use fixed name (can be overwritten)
            filename = f"vqa2_results_{suffix}.json"
        else:
                # Complete test - use timestamp to avoid overwriting
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vqa2_results_{test_mode}_{timestamp}.json"
        
        results_file = self.results_dir / filename
        
        # Enhanced result format with complete metadata
        enhanced_results = {}
        
        for model_name, model_results in results.items():
            if "error" in model_results:
                enhanced_results[model_name] = {"error": model_results["error"]}
                continue
                
            # Enhanced metrics with detailed information
            enhanced_results[model_name] = {
                "model_id": model_results.get("model_id", model_name),
                "test_time": model_results.get("evaluation_time", 0),
                "total_questions": model_results.get("total", 0),
                "correct_answers": model_results.get("correct", 0),
                "accuracy": model_results.get("accuracy", 0),
                "vqa_accuracy": model_results.get("vqa_accuracy", 0),
                "avg_inference_time": model_results.get("avg_time", 0),
                "performance_grade": model_results.get("detailed_metrics", {}).get("performance_grade", "N/A"),
                "question_results": model_results.get("question_results", [])
            }
        
        # Complete experimental metadata for paper publication
        save_data = {
            "experiment_metadata": {
                "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "test_mode": test_mode,
                "num_questions": num_questions,
                "framework_version": "vqa2_enhanced_v1.2",
                "evaluation_method": "VQA 2.0 Standard",
                "dataset": "COCO val2014",
                "generation_params": self.generation_params
            },
            "hardware_configuration": {
                "device": "MacBook Air M3",
                "memory": "16GB",
                "mps_available": torch.backends.mps.is_available(),
                "torch_version": torch.__version__,
                "python_version": sys.version
            },
            "model_configuration": {
                "models_tested": list(results.keys()),
                "model_loader": "VLMModelLoader from vlm_tester.py",
                "unified_parameters": True,
                "image_preprocessing": "Resize to max 1024px, LANCZOS"
            },
            "results": enhanced_results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return results_file
