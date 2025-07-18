#!/usr/bin/env python3
"""
VQA 2.0 核心框架 - 整合版本
整合了VQA測試器、工具函數、圖像處理等所有核心功能

Author: AI Manual Assistant Team
Date: 2025-01-27
"""

import os
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

# Import existing VLM infrastructure
from vlm_tester import VLMModelLoader, clear_model_memory, get_memory_usage

class VQAFramework:
    """VQA 2.0 統一框架 - 整合所有功能"""
    
    def __init__(self, data_dir: str = None):
        """初始化VQA框架
        
        Args:
            data_dir: VQA數據目錄路徑
        """
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "testing_material" / "vqa2"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.images_dir = self.data_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # VQA 2.0 數據集URLs
        self.vqa2_urls = {
            "val_questions": "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Val_mscoco.zip",
            "val_annotations": "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Annotations_Val_mscoco.zip",
        }
        
        # 支持的模型配置
        self.models_config = {
            "smolvlm_instruct": {
                "loader": VLMModelLoader.load_smolvlm_instruct,
                "model_id": "HuggingFaceTB/SmolVLM-500M-Instruct"
            },
            "smolvlm_v2_instruct": {
                "loader": VLMModelLoader.load_smolvlm2_video,
                "model_id": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
            },
            "moondream2": {
                "loader": VLMModelLoader.load_moondream2,
                "model_id": "vikhyatk/moondream2"
            },
            "llava_mlx": {
                "loader": VLMModelLoader.load_llava_mlx,
                "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit"
            },
            "phi35_vision": {
                "loader": VLMModelLoader.load_phi3_vision,
                "model_id": "lokinfey/Phi-3.5-vision-mlx-int4"
            }
        }
        
        # 生成參數
        self.generation_params = {
            "max_new_tokens": 50,
            "do_sample": False
        }
        
        # 圖像緩存
        self.image_cache = {}
        
        print(f"🧪 VQA 2.0 Framework Initialized")
        print(f"📁 Data directory: {self.data_dir}")
    
    def download_vqa_data(self):
        """下載VQA 2.0數據集"""
        print("📥 Downloading VQA 2.0 Dataset...")
        
        for component, url in self.vqa2_urls.items():
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
                
                # 解壓文件
                print(f"📂 Extracting {zip_file.name}...")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)
                print(f"✅ Extracted: {zip_file.name}")
            else:
                print(f"✅ {component} already downloaded")
        
        print("✅ VQA 2.0 Dataset ready")
    
    def load_sample_data(self, sample_size: int = 20) -> Tuple[List[Dict], Dict]:
        """加載真實VQA 2.0數據的樣本"""
        # 首先確保真實數據已下載
        try:
            questions, annotations = self.load_real_data(sample_size)
            print(f"✅ Using real VQA 2.0 data: {len(questions)} questions")
            
            # 下載對應的COCO圖像
            self._ensure_coco_images_for_questions(questions)
            
            return questions, annotations
            
        except Exception as e:
            print(f"⚠️ Could not load real VQA data: {e}")
            print("📥 Attempting to download VQA 2.0 dataset...")
            
            # 嘗試下載VQA數據
            self.download_vqa_data()
            
            # 重新嘗試加載
            try:
                questions, annotations = self.load_real_data(sample_size)
                print(f"✅ Using real VQA 2.0 data: {len(questions)} questions")
                
                # 下載對應的COCO圖像
                self._ensure_coco_images_for_questions(questions)
                
                return questions, annotations
                
            except Exception as e2:
                print(f"❌ Still failed to load real data: {e2}")
                print("� Falling back to sample data...")
                
                # 最後回退到樣本數據
                return self._create_sample_data(sample_size)
    
    def load_real_data(self, sample_size: int = 20) -> Tuple[List[Dict], Dict]:
        """加載真實VQA 2.0數據"""
        print(f"📖 Loading real VQA 2.0 data...")
        
        # 加載問題
        questions_file = self.data_dir / "v2_OpenEnded_mscoco_val2014_questions.json"
        if not questions_file.exists():
            raise FileNotFoundError(f"Questions file not found: {questions_file}")
            
        with open(questions_file, 'r') as f:
            questions_data = json.load(f)
            
        questions = questions_data['questions']
        
        # 加載標註
        annotations_file = self.data_dir / "v2_mscoco_val2014_annotations.json"
        annotations_dict = {}
        
        if annotations_file.exists():
            with open(annotations_file, 'r') as f:
                annotations_data = json.load(f)
            annotations_dict = {ann['question_id']: ann for ann in annotations_data['annotations']}
        else:
            print(f"⚠️ Annotations file not found: {annotations_file}")
        
        # 智能採樣：確保問題有對應的標註
        if sample_size and sample_size < len(questions):
            # 篩選有標註的問題
            questions_with_annotations = [
                q for q in questions 
                if q['question_id'] in annotations_dict
            ]
            
            if len(questions_with_annotations) < sample_size:
                print(f"⚠️ Only {len(questions_with_annotations)} questions have annotations, using all")
                sample_size = len(questions_with_annotations)
            
            # 隨機採樣
            import random
            random.seed(42)  # 確保結果可重現
            questions = random.sample(questions_with_annotations, sample_size)
            print(f"📝 Sampled {sample_size} questions from {len(questions_with_annotations)} annotated questions")
        
        return questions, annotations_dict
    
    def _create_sample_data(self, sample_size: int) -> Tuple[List[Dict], Dict]:
        """創建樣本數據 - 使用真實COCO圖像ID"""
        # 簡單的樣本問題
        sample_questions_template = [
            ("What color is the car?", "red"),
            ("How many people are in the image?", "2"),
            ("Is this person wearing a hat?", "yes"),
            ("What is the weather like?", "sunny"),
            ("Where is this photo taken?", "park"),
        ]
        
        # 真實COCO val2014 圖像ID（前20個）
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
            image_id = coco_image_ids[i % len(coco_image_ids)]  # 使用真實COCO ID
            
            question = {
                "question_id": question_id,
                "image_id": image_id,
                "question": question_text
            }
            questions.append(question)
            
            # 創建標註（模擬10個人工標註者）
            annotation = {
                "question_id": question_id,
                "question_type": "other",
                "multiple_choice_answer": answer,
                "answers": [{"answer": answer, "answer_confidence": "yes"} for _ in range(10)]
            }
            annotations[question_id] = annotation
        
        # 保存樣本數據
        questions_data = {"questions": questions}
        annotations_data = {"annotations": list(annotations.values())}
        
        with open(self.data_dir / "val_questions_sample.json", 'w') as f:
            json.dump(questions_data, f, indent=2)
            
        with open(self.data_dir / "val_annotations_sample.json", 'w') as f:
            json.dump(annotations_data, f, indent=2)
        
        print(f"✅ Created sample data: {len(questions)} questions with real COCO image IDs")
        return questions, annotations
    
    def _ensure_sample_images(self, sample_size: int):
        """確保COCO樣本圖像存在"""
        sample_dir = self.images_dir / "val2014_sample"
        sample_dir.mkdir(exist_ok=True)
        
        # 檢查是否已有足夠的圖像
        existing_images = list(sample_dir.glob("*.jpg"))
        if len(existing_images) >= min(sample_size, 20):  # 最多20張不同圖像
            return
        
        print(f"📥 Downloading COCO val2014 sample images (first 20 images)...")
        
        # COCO val2014 前20張圖像的真實ID
        coco_image_ids = [
            "000000000139", "000000000285", "000000000632", "000000000724", "000000000776",
            "000000000785", "000000000802", "000000000872", "000000000885", "000000001000",
            "000000001268", "000000001296", "000000001353", "000000001584", "000000001818",
            "000000002006", "000000002149", "000000002153", "000000002157", "000000002261"
        ]
        
        # COCO val2014 下載基礎URL
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
                    # 如果下載失敗，創建佔位符圖像
                    placeholder_image = Image.new('RGB', (640, 480), (128, 128, 128))
                    placeholder_image.save(image_path, 'JPEG')
                    print(f"🔄 Created placeholder for {image_filename}")
        
        print(f"✅ COCO sample setup complete: {downloaded_count} downloaded, {len(list(sample_dir.glob('*.jpg')))} total images")
    
    def _ensure_coco_images_for_questions(self, questions: List[Dict]):
        """為問題列表下載對應的COCO圖像"""
        sample_dir = self.images_dir / "val2014_sample"
        sample_dir.mkdir(exist_ok=True)
        
        # 收集所有需要的圖像ID
        image_ids = set()
        for question in questions:
            image_ids.add(question['image_id'])
        
        print(f"📥 Ensuring COCO images for {len(image_ids)} unique images...")
        
        # COCO val2014 下載基礎URL
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
                # 如果下載失敗，創建佔位符圖像
                try:
                    placeholder_image = Image.new('RGB', (640, 480), (128, 128, 128))
                    placeholder_image.save(image_path, 'JPEG')
                    print(f"🔄 Created placeholder for {image_filename}")
                except Exception as e2:
                    print(f"❌ Failed to create placeholder: {e2}")
        
        print(f"✅ COCO images ready: {existing_count} existing, {downloaded_count} downloaded")
    
    def check_image_availability(self, questions: List[Dict]) -> Dict:
        """檢查圖像可用性"""
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
        """加載圖像"""
        # 檢查緩存
        cache_key = f"{split}_{image_id}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        # 嘗試不同的圖像路徑格式
        possible_paths = [
            # 真實COCO格式
            self.images_dir / f"{split}_sample" / f"COCO_{split}_{image_id:012d}.jpg",
            self.images_dir / f"{split}" / f"COCO_{split}_{image_id:012d}.jpg",
            # 備用格式
            self.images_dir / f"{split}_sample" / f"COCO_{split}_{image_id:06d}.jpg",
        ]
        
        for image_path in possible_paths:
            if image_path.exists():
                try:
                    image = Image.open(image_path).convert('RGB')
                    # 緩存圖像（限制緩存大小）
                    if len(self.image_cache) < 100:
                        self.image_cache[cache_key] = image
                    return image
                except Exception as e:
                    print(f"⚠️ Error loading image {image_path}: {e}")
                    continue
        
        return None
    
    def evaluate_model(self, model_name: str, questions: List[Dict], 
                      annotations: Dict, max_questions: int = None,
                      verbose: bool = False) -> Dict:
        """評估模型"""
        print(f"🤖 Evaluating {model_name} on VQA 2.0...")
        
        if model_name not in self.models_config:
            return {"error": f"Unknown model: {model_name}"}
        
        # 限制問題數量
        if max_questions:
            questions = questions[:max_questions]
        
        try:
            # 加載模型
            print("📥 Loading model...")
            model_loader = self.models_config[model_name]["loader"]
            load_start = time.time()
            model, processor = model_loader()
            load_time = time.time() - load_start
            print(f"✅ Model loaded in {load_time:.2f}s")
            
            # 記錄記憶體使用
            memory_info = get_memory_usage()
            print(f"💾 Memory usage: {memory_info}")
            
            # 評估
            print(f"📊 Evaluating {len(questions)} questions...")
            results = self._evaluate_questions(
                model, processor, model_name, questions, 
                annotations, verbose
            )
            
            # 清理模型記憶體
            print("清理模型記憶體...")
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
        """評估問題列表"""
        correct_answers = 0
        total_vqa_accuracy = 0.0
        total_inference_time = 0.0
        question_results = []
        
        for i, question in enumerate(questions):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(questions)}")
            
            question_id = question['question_id']
            question_text = question['question']
            image_id = question['image_id']
            
            # 獲取模型答案
            inference_start = time.time()
            try:
                model_answer = self._get_model_answer(
                    model, processor, model_name, question_text, image_id
                )
            except Exception as e:
                if verbose:
                    print(f"⚠️ Error getting answer for question {question_id}: {e}")
                model_answer = "error"
            
            inference_time = time.time() - inference_start
            total_inference_time += inference_time
            
            # 評估答案
            if question_id in annotations:
                annotation = annotations[question_id]
                gt_answer = annotation['multiple_choice_answer']
                gt_answers = [ans['answer'] for ans in annotation['answers']]
                
                # 簡單準確度 - 檢查標準答案是否在模型回答中
                model_answer_lower = self._preprocess_answer(model_answer)
                gt_answer_lower = self._preprocess_answer(gt_answer)
                is_correct = gt_answer_lower in model_answer_lower
                if is_correct:
                    correct_answers += 1
                
                # VQA準確度
                vqa_accuracy = self._calculate_vqa_accuracy(model_answer, gt_answers)
                total_vqa_accuracy += vqa_accuracy
                
                # 生成對應的圖像文件名
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
            
        # 計算最終結果
        total_questions = len(questions)
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        avg_vqa_accuracy = total_vqa_accuracy / total_questions if total_questions > 0 else 0
        avg_inference_time = total_inference_time / total_questions if total_questions > 0 else 0
        
        print(f"✅ Evaluation completed:")
        print(f"   📊 Questions evaluated: {total_questions}")
        print(f"   ✅ Correct answers: {correct_answers}")
        print(f"   🎯 Accuracy: {accuracy:.3f}")
        print(f"   ⏱️ Avg inference time: {avg_inference_time:.2f}s")
        
        return {
            'accuracy': accuracy,
            'vqa_accuracy': avg_vqa_accuracy,
            'correct': correct_answers,
            'total': total_questions,
            'avg_time': avg_inference_time,
            'question_results': question_results
        }
    
    def _get_model_answer(self, model, processor, model_name: str, 
                         question: str, image_id: int) -> str:
        """獲取模型答案"""
        # 加載圖像
        image = self._load_image(image_id)
        if image is None:
            return "no image available"
        
        try:
            if "smolvlm" in model_name.lower():
                # SmolVLM處理 - 使用正確的格式
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
                    generated_ids = model.generate(**inputs, **self.generation_params)
                    response = processor.decode(generated_ids[0], skip_special_tokens=True)
                
                # 提取答案 - 移除輸入文本
                answer = response.replace(input_text, "").strip()
                return self._extract_answer(answer, model_name, question)
                
            elif "moondream" in model_name.lower():
                # Moondream處理  
                answer = model.answer_question(image, question, processor)
                return answer
                
            else:
                return "model not supported"
                
        except Exception as e:
            return f"error: {str(e)}"
    
    def _extract_answer(self, response: str, model_name: str, question: str) -> str:
        """從模型響應中提取答案 - 簡化版本，直接返回原始回答"""
        if not response:
            return "no response"
        
        # 簡單清理，直接返回原始回答
        return response.strip()
    
    def _preprocess_answer(self, answer: str) -> str:
        """預處理答案 - 簡化版本"""
        if not answer:
            return ""
        
        # 轉小寫，保持簡單
        return answer.lower().strip()
    
    def _calculate_vqa_accuracy(self, prediction: str, ground_truth_answers: List[str]) -> float:
        """計算VQA準確度 - 檢查任何標準答案是否在預測中"""
        if not prediction or not ground_truth_answers:
            return 0.0
        
        prediction_lower = self._preprocess_answer(prediction)
        
        # 計算有多少個標準答案在預測中出現
        matching_count = 0
        for gt_answer in ground_truth_answers:
            gt_answer_lower = self._preprocess_answer(gt_answer)
            if gt_answer_lower in prediction_lower:
                matching_count += 1
        
        # VQA準確度：min(匹配數/3, 1.0)
        accuracy = min(matching_count / 3.0, 1.0)
        return accuracy
    
    def save_results(self, results: Dict, test_mode: str, num_questions: int) -> Path:
        """保存測試結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"vqa2_results_{test_mode}_{timestamp}.json"
        
        # 準備保存的數據
        save_data = {
            "test_metadata": {
                "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "test_mode": test_mode,
                "num_questions": num_questions,
                "framework_version": "unified_v1.1",
                "image_reference_note": "每個問題的 image_id 對應 image_filename，圖像文件位於 testing_material/vqa2/images/val2014_sample/ 目錄"
            },
            "results": results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return results_file
