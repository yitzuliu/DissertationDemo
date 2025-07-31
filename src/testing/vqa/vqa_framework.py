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
from collections import OrderedDict
import torch
import numpy as np
from PIL import Image
from tqdm import tqdm
import gc # Added for fallback model cleanup

# Import existing VLM infrastructure
try:
    # For module execution: python -m src.testing.vqa.vqa_test
    from ..vlm.vlm_tester import VLMModelLoader, clear_model_memory, get_memory_usage
except (ImportError, ValueError):
    # For direct script execution: python vqa_test.py
    from vlm.vlm_tester import VLMModelLoader, clear_model_memory, get_memory_usage

# Add imports for SmolVLM GGUF support
import requests
import subprocess
import base64
import io
import atexit
import signal
import psutil

if __name__ == "__main__":
    print("[WARNING] vqa_framework.py is a library module and should not be run directly.\nPlease run vqa_test.py or use this module as an import.")
    import sys
    sys.exit(1)

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
            # Default to materials/vqa2
            base_dir = Path(__file__).parent.parent.parent  # src/testing/
            possible_paths = [
                base_dir / "materials" / "vqa2",  # src/testing/materials/vqa2
                Path("materials/vqa2"),
                Path("./materials/vqa2")
            ]
            self.data_dir = None
            for path in possible_paths:
                if path.exists():
                    self.data_dir = path
                    break
            if self.data_dir is None:
                self.data_dir = base_dir / "materials" / "vqa2"
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
        
        # 🎯 OPTIMIZED MODEL CONFIGURATION: Same order as vlm_tester.py
        # Memory-intensive models first to avoid accumulation issues
        self.models_config = OrderedDict([
            # 1️⃣ Phi-3.5 first - Most memory-intensive, run when system is cleanest
            ("phi35_vision", {
                "loader": VLMModelLoader.load_phi3_vision,
                "model_id": "mlx-community/Phi-3.5-vision-instruct-4bit",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), requires 'pip install mlx-vlm'",
                "priority": 1,
                "memory_intensive": True
            }),
            # 2️⃣ LLaVA second - Also memory-intensive MLX model
            ("llava_mlx", {
                "loader": VLMModelLoader.load_llava_mlx,
                "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), requires 'pip install mlx-vlm'",
                "priority": 2,
                "memory_intensive": True
            }),
            # 3️⃣ SmolVLM2 MLX version - Medium memory usage
            ("smolvlm_v2_instruct", {
                "loader": VLMModelLoader.load_smolvlm2_video,
                "model_id": "mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                "note": "MLX-optimized for Apple Silicon (M1/M2/M3), falls back to original SmolVLM2 if MLX not available or incompatible",
                "priority": 3,
                "memory_intensive": False
            }),
            # 4️⃣ Lightweight models last - Least memory usage
            ("smolvlm_instruct", {
                "loader": VLMModelLoader.load_smolvlm_gguf,
                "model_id": "ggml-org/SmolVLM-500M-Instruct-GGUF",
                "api_endpoint": "http://localhost:8080/v1/chat/completions",
                "note": "GGUF version via HTTP API (consistent with production deployment)",
                "priority": 4,
                "memory_intensive": False
            }),
            ("moondream2", {
                "loader": VLMModelLoader.load_moondream2,
                "model_id": "vikhyatk/moondream2",
                "note": "Lightweight vision-only model for Apple Silicon",
                "priority": 5,
                "memory_intensive": False
            })
        ])
        
        # Image cache
        self.image_cache = {}
        
        # Server process tracking for cleanup
        self.server_process = None
        
        # Register cleanup handlers
        atexit.register(self._cleanup_on_exit)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print(f"✅ VQA Framework initialized")
        print(f"   📁 Data directory: {self.data_dir}")
        print(f"   📊 Results directory: {self.results_dir}")
        print(f"   🎯 Model order: {list(self.models_config.keys())}")
    
    def ensure_smolvlm_server(self):
        """Ensure SmolVLM server is running (consistent with vlm_tester.py)"""
        print("🔄 Checking SmolVLM server status...")
        
        # Check if server is already running
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                print("✅ SmolVLM server is already running")
                return True
        except requests.exceptions.RequestException:
            pass
        
        # Check if port 8080 is occupied
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8080))
            sock.close()
            
            if result == 0:
                print("⚠️ Port 8080 is occupied, attempting to close existing process...")
                # Try to kill process on port 8080
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
                                time.sleep(2)  # Wait for process to terminate
                except Exception as e:
                    print(f"⚠️ Failed to kill process on port 8080: {e}")
        except Exception as e:
            print(f"⚠️ Error checking port 8080: {e}")
        
        # Try to start server (up to 3 attempts) - consistent with vlm_tester.py
        for attempt in range(1, 4):
            print(f"🔄 Attempt {attempt}/3: Starting SmolVLM server...")
            try:
                # Use same command as vlm_tester.py and vlm_context_tester.py
                cmd = [
                    "llama-server",
                    "-hf", "ggml-org/SmolVLM-500M-Instruct-GGUF",
                    "-ngl", "99",
                    "--port", "8080"
                ]
                
                # Start server in background
                server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Track server process for cleanup
                self.server_process = server_process
                
                # Wait for server to start (up to 30 seconds)
                for i in range(30):
                    time.sleep(2)
                    try:
                        response = requests.get("http://localhost:8080/health", timeout=5)
                        if response.status_code == 200:
                            print(f"✅ SmolVLM server started successfully on attempt {attempt}")
                            return True
                    except requests.exceptions.RequestException:
                        continue
                
                # If we get here, server didn't start
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
    
    def _cleanup_on_exit(self):
        """Cleanup function called on program exit"""
        print("\n🧹 Cleaning up VQA Framework resources...")
        self._cleanup_smolvlm_server()
        print("✅ VQA Framework cleanup completed")
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals (Ctrl+C)"""
        print(f"\n⚠️ Received signal {signum}, cleaning up...")
        self._cleanup_smolvlm_server()
        sys.exit(0)
    
    def _cleanup_smolvlm_server(self):
        """Clean up SmolVLM server process"""
        try:
            # Kill any process on port 8080
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
                        print(f"🔄 Killing SmolVLM server process {pid}...")
                        try:
                            subprocess.run(["kill", "-9", pid.strip()], timeout=10)
                            time.sleep(1)
                        except Exception as e:
                            print(f"⚠️ Failed to kill process {pid}: {e}")
                
                # Verify cleanup
                time.sleep(2)
                try:
                    response = requests.get("http://localhost:8080/health", timeout=2)
                    if response.status_code == 200:
                        print("⚠️ SmolVLM server still running, attempting force kill...")
                        subprocess.run(["pkill", "-f", "llama-server"], timeout=10)
                except requests.exceptions.RequestException:
                    print("✅ SmolVLM server successfully stopped")
        except Exception as e:
            print(f"⚠️ Error during server cleanup: {e}")
    
    def cleanup(self):
        """Manual cleanup method"""
        self._cleanup_smolvlm_server()
    
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
            # Ensure SmolVLM server is running for GGUF models
            if model_name == "smolvlm_instruct":
                if not self.ensure_smolvlm_server():
                    return {"error": "SmolVLM server is not available"}
            
            # Load model
            print("📥 Loading model...")
            model_loader = self.models_config[model_name]["loader"]
            load_start = time.time()
            load_result = model_loader()
            load_time = time.time() - load_start
            
            # Handle different return types
            if isinstance(load_result, tuple) and len(load_result) == 2:
                if load_result[0] == "smolvlm_gguf":
                    # GGUF model via HTTP API
                    model = {"type": "smolvlm_gguf", "api_endpoint": load_result[1]}
                    processor = None
                    print(f"✅ SmolVLM GGUF model ready via HTTP API in {load_time:.2f}s")
                else:
                    # Standard model
                    model, processor = load_result
                    print(f"✅ Model loaded in {load_time:.2f}s")
            else:
                # Fallback for other return types
                model, processor = load_result, None
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
            if isinstance(model, dict) and model.get("type") == "smolvlm_gguf":
                # GGUF model doesn't need memory cleanup
                print("  ℹ️ SmolVLM GGUF model (HTTP API) - no memory cleanup needed")
            else:
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
                    
                    # Special handling for yes/no questions
                    if gt_answer_lower in ['yes', 'no']:
                        # For yes/no questions, determine model's yes/no response
                        yes_keywords = ['yes', 'yeah', 'yep', 'correct', 'true', 'right', 'sure', 'okay']
                        no_keywords = ['no', 'nope', 'not', 'false', 'wrong', 'incorrect', 'negative']
                        
                        model_yes = any(keyword in model_answer_lower for keyword in yes_keywords)
                        model_no = any(keyword in model_answer_lower for keyword in no_keywords)
                        
                        if gt_answer_lower == 'yes':
                            is_correct = model_yes and not model_no
                        else:  # gt_answer_lower == 'no'
                            is_correct = model_no and not model_yes
                    else:
                        # For non-yes/no questions, use standard logic
                        is_correct = gt_answer_lower in model_answer_lower
                    
                    if is_correct:
                        correct_answers += 1
                    
                    # VQA accuracy - use single standard answer for consistency
                    vqa_accuracy = self._calculate_vqa_accuracy(model_answer, [gt_answer])
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
                        'inference_time': inference_time,
                        'debug_info': {
                            'model_answer_lower': self._preprocess_answer(model_answer),
                            'gt_answer_lower': self._preprocess_answer(gt_answer),
                            'is_yes_no_question': gt_answer.lower() in ['yes', 'no']
                        }
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
                    
                    # MLX-VLM may return tuple or string, need to parse
                    if isinstance(response, tuple) and len(response) >= 1:
                        # If it's a tuple, take the first element as text response
                        text_response = str(response[0])
                    else:
                        # If it's a string, use directly
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
                # SmolVLM processing - unified GGUF HTTP API approach
                if (isinstance(model, dict) and model.get("type") == "smolvlm_gguf") or (hasattr(model, 'model_type') and model.model_type == "smolvlm_gguf"):
                    # GGUF model via HTTP API (consistent with vlm_tester.py and vlm_context_tester.py)
                    try:
                        print("  🚀 Using SmolVLM GGUF via HTTP API...")
                        
                        # Convert image to base64
                        img_buffer = io.BytesIO()
                        image.save(img_buffer, format='JPEG')
                        img_str = base64.b64encode(img_buffer.getvalue()).decode()
                        
                        # Prepare OpenAI-compatible payload
                        payload = {
                            "model": "ggml-org/SmolVLM-500M-Instruct-GGUF",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{img_str}"
                                            }
                                        },
                                        {
                                            "type": "text",
                                            "text": question
                                        }
                                    ]
                                }
                            ],
                            "max_tokens": unified_generation_params["max_new_tokens"],
                            "temperature": 0.0
                        }
                        
                        # Send request to SmolVLM server
                        api_endpoint = model["api_endpoint"] if isinstance(model, dict) else model.api_endpoint
                        response = requests.post(
                            api_endpoint,
                            json=payload,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            try:
                                result = response.json()
                                if "choices" in result and len(result["choices"]) > 0:
                                    content = result["choices"][0]["message"]["content"]
                                    if content and content.strip():
                                        return content.strip()
                                    else:
                                        return "Empty response content"
                                else:
                                    return f"No choices in response: {result}"
                            except json.JSONDecodeError as e:
                                return f"Invalid JSON response: {response.text[:100]}"
                        else:
                            return f"HTTP error {response.status_code}: {response.text[:100]}"
                            
                    except Exception as e:
                        print(f"  ⚠️ SmolVLM GGUF inference failed: {e}")
                        return f"SmolVLM GGUF inference error: {str(e)}"
                else:
                    # Fallback for other SmolVLM versions (SmolVLM2, etc.)
                    if hasattr(model, '_is_mlx_model'):
                        # MLX version SmolVLM2 inference - use subprocess method (consistent with vlm_tester.py)
                        try:
                            import subprocess
                            import tempfile
                            
                            print("  🚀 Using MLX-VLM command line for SmolVLM2...")
                            
                            # Create temporary image file
                            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                                temp_image_path = tmp_file.name
                                image.save(temp_image_path)
                            
                            try:
                                # Use MLX-VLM command line tool (same as vlm_tester.py)
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
                                    # Parse output, extract generated text (same as vlm_tester.py)
                                    output_lines = result.stdout.split('\n')
                                    generated_text = ""
                                    
                                    # Keep full Assistant response
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
                                    return f"MLX-VLM SmolVLM2 command failed: {result.stderr}"
                                    
                            finally:
                                # Clean up temporary file
                                if os.path.exists(temp_image_path):
                                    os.remove(temp_image_path)
                            
                        except Exception as e:
                            print(f"  ⚠️ MLX-VLM SmolVLM2 inference failed: {e}")
                            return f"MLX-VLM SmolVLM2 inference error: {str(e)}"
                    else:
                        # Standard SmolVLM inference method
                        try:
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
                        except Exception as e:
                            print(f"  ⚠️ Standard SmolVLM inference failed: {e}")
                            return f"Standard SmolVLM inference error: {str(e)}"
                
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
        
        # Remove all punctuation marks for better matching
        import re
        answer = re.sub(r'[^\w\s]', ' ', answer)
        
        # Normalize whitespace
        answer = ' '.join(answer.split())
        
        # Handle common contractions and variations
        answer = answer.replace("'t", " not")
        answer = answer.replace("'re", " are")
        answer = answer.replace("'s", " is")
        answer = answer.replace("'ve", " have")
        answer = answer.replace("'ll", " will")
        answer = answer.replace("'d", " would")
        answer = answer.replace("n't", " not")
        answer = answer.replace("i'm", "i am")
        answer = answer.replace("it's", "it is")
        answer = answer.replace("don't", "do not")
        answer = answer.replace("can't", "cannot")
        answer = answer.replace("won't", "will not")
        
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
            # Use word boundaries to avoid partial matches
            answer = re.sub(r'\b' + word + r'\b', digit, answer)
        
        return answer
    
    def _calculate_vqa_accuracy(self, prediction: str, ground_truth_answers: List[str]) -> float:
        """Calculate VQA accuracy using standard VQA 2.0 evaluation method"""
        if not prediction or not ground_truth_answers:
            return 0.0
        
        prediction_lower = self._preprocess_answer(prediction)
        
        # Special handling for yes/no questions
        yes_no_keywords = {
            'yes': ['yes', 'yeah', 'yep', 'correct', 'true', 'right', 'sure', 'okay'],
            'no': ['no', 'nope', 'not', 'false', 'wrong', 'incorrect', 'negative']
        }
        
        # Check if this is a yes/no question by examining ground truth
        gt_lower = [self._preprocess_answer(gt) for gt in ground_truth_answers]
        is_yes_no_question = any(gt in ['yes', 'no'] for gt in gt_lower)
        
        if is_yes_no_question:
            # For yes/no questions, determine model's yes/no response
            model_yes = any(keyword in prediction_lower for keyword in yes_no_keywords['yes'])
            model_no = any(keyword in prediction_lower for keyword in yes_no_keywords['no'])
            
            # Determine ground truth yes/no
            gt_yes = any(gt == 'yes' for gt in gt_lower)
            gt_no = any(gt == 'no' for gt in gt_lower)
            
            # Calculate accuracy - ensure consistency with simple accuracy
            if gt_yes and model_yes and not model_no:
                return 1.0  # Correct yes answer
            elif gt_no and model_no and not model_yes:
                return 1.0  # Correct no answer
            elif gt_yes and model_no and not model_yes:
                return 0.0  # Wrong no answer (should be yes)
            elif gt_no and model_yes and not model_no:
                return 0.0  # Wrong yes answer (should be no)
            else:
                # Ambiguous or unclear response - give partial credit only if there's some indication
                if model_yes and model_no:
                    # Both yes and no keywords present - very unclear
                    return 0.1
                elif not model_yes and not model_no:
                    # No clear yes/no keywords - unclear response
                    return 0.2
                else:
                    # Some indication but not clear - minimal credit
                    return 0.3
        
        # For non-yes/no questions, use improved matching logic
        # Since we now use single ground truth answer, we can be more precise
        gt_answer = ground_truth_answers[0]  # Use single standard answer
        gt_answer_lower = self._preprocess_answer(gt_answer)
        
        # Improved matching logic:
        # 1. Exact match (highest score)
        if gt_answer_lower == prediction_lower:
            return 1.0
        
        # 2. Word-level matching (high score)
        gt_words = set(gt_answer_lower.split())
        pred_words = set(prediction_lower.split())
        
        if gt_words and pred_words:
            # Calculate word overlap
            common_words = gt_words.intersection(pred_words)
            word_overlap = len(common_words) / len(gt_words)
            
            # If all ground truth words are present, give high score
            if word_overlap >= 1.0:
                return 0.9
            # If most ground truth words are present, give medium score
            elif word_overlap >= 0.7:
                return 0.7
            # If some ground truth words are present, give low score
            elif word_overlap >= 0.3:
                return 0.3
        
        # 3. Substring matching (lower score)
        if gt_answer_lower in prediction_lower:
            return 0.5
        
        # 4. No match
        return 0.0
    
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
