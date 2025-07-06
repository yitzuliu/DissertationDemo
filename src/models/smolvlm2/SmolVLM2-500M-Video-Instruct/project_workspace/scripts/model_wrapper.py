#!/usr/bin/env python3
"""
SmolVLM2-500M-Video-Instruct Custom Model Wrapper
Project Workspace Script - Enhanced model access and utilities
"""

import torch
import time
import os
from pathlib import Path
from typing import Union, List, Dict, Optional
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText

class SmolVLM2Wrapper:
    """
    Enhanced wrapper for SmolVLM2-500M-Video-Instruct model
    Provides simplified interface and additional utilities
    """
    
    def __init__(self, model_path: str = "..", device: str = "auto"):
        """
        Initialize the SmolVLM2 wrapper
        
        Args:
            model_path: Path to model directory (default: parent directory)
            device: Device to use ('auto', 'mps', 'cuda', 'cpu')
        """
        self.model_path = model_path
        self.device = self._setup_device(device)
        self.processor = None
        self.model = None
        self.load_time = None
        
    def _setup_device(self, device: str) -> str:
        """Setup optimal device for inference"""
        if device == "auto":
            if torch.backends.mps.is_available():
                return "mps"
            elif torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        return device
    
    def load_model(self, verbose: bool = True) -> Dict[str, float]:
        """
        Load the model and processor
        
        Args:
            verbose: Whether to print loading progress
            
        Returns:
            Dictionary with loading times
        """
        if verbose:
            print(f"🔧 Loading SmolVLM2 model from: {self.model_path}")
            print(f"📱 Using device: {self.device}")
        
        start_time = time.time()
        
        # Load processor
        processor_start = time.time()
        self.processor = AutoProcessor.from_pretrained(self.model_path)
        processor_time = time.time() - processor_start
        
        # Load model
        model_start = time.time()
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,
            device_map=self.device
        )
        model_time = time.time() - model_start
        
        self.load_time = time.time() - start_time
        
        if verbose:
            print(f"✅ Processor loaded: {processor_time:.2f}s")
            print(f"✅ Model loaded: {model_time:.2f}s")
            print(f"✅ Total time: {self.load_time:.2f}s")
            print(f"✅ Ready for inference!\n")
        
        return {
            'processor_time': processor_time,
            'model_time': model_time,
            'total_time': self.load_time
        }
    
    def text_query(self, prompt: str, max_tokens: int = 100, temperature: float = 0.1) -> Dict:
        """
        Process text-only query
        
        Args:
            prompt: Text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.model or not self.processor:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        start_time = time.time()
        
        messages = [{
            "role": "user", 
            "content": [{"type": "text", "text": prompt}]
        }]
        
        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.device, dtype=torch.bfloat16)
        
        generated_ids = self.model.generate(
            **inputs,
            do_sample=temperature > 0,
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        
        response = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]
        
        # Clean response (remove prompt echo)
        clean_response = response.split("Assistant:")[-1].strip() if "Assistant:" in response else response
        
        inference_time = time.time() - start_time
        
        return {
            'prompt': prompt,
            'response': clean_response,
            'inference_time': inference_time,
            'token_count': len(generated_ids[0]),
            'device': self.device
        }
    
    def image_query(self, image: Union[str, Image.Image], prompt: str, 
                   max_tokens: int = 100, temperature: float = 0.1) -> Dict:
        """
        Process image + text query
        
        Args:
            image: Image file path or PIL Image object
            prompt: Text prompt about the image
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.model or not self.processor:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        start_time = time.time()
        
        # Handle image input
        if isinstance(image, str):
            image = Image.open(image)
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        }]
        
        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.device, dtype=torch.bfloat16)
        
        generated_ids = self.model.generate(
            **inputs,
            do_sample=temperature > 0,
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        
        response = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]
        
        # Clean response
        clean_response = response.split("Assistant:")[-1].strip() if "Assistant:" in response else response
        
        inference_time = time.time() - start_time
        
        return {
            'prompt': prompt,
            'response': clean_response,
            'inference_time': inference_time,
            'token_count': len(generated_ids[0]),
            'image_size': image.size if hasattr(image, 'size') else None,
            'device': self.device
        }
    
    def batch_process(self, tasks: List[Dict], verbose: bool = True) -> List[Dict]:
        """
        Process multiple tasks in batch
        
        Args:
            tasks: List of task dictionaries with 'type', 'prompt', and optional 'image'
            verbose: Whether to show progress
            
        Returns:
            List of results
        """
        results = []
        
        for i, task in enumerate(tasks):
            if verbose:
                print(f"Processing task {i+1}/{len(tasks)}: {task.get('type', 'unknown')}")
            
            try:
                if task['type'] == 'text':
                    result = self.text_query(task['prompt'])
                elif task['type'] == 'image':
                    result = self.image_query(task['image'], task['prompt'])
                else:
                    raise ValueError(f"Unknown task type: {task['type']}")
                
                result['task_id'] = i
                result['success'] = True
                results.append(result)
                
            except Exception as e:
                results.append({
                    'task_id': i,
                    'success': False,
                    'error': str(e),
                    'task': task
                })
        
        return results
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        if not self.model:
            return {"status": "Model not loaded"}
        
        return {
            "model_path": self.model_path,
            "device": self.device,
            "load_time": self.load_time,
            "model_dtype": str(next(self.model.parameters()).dtype),
            "model_device": str(next(self.model.parameters()).device),
            "processor_type": type(self.processor).__name__,
            "status": "Ready"
        }

# Example usage
if __name__ == "__main__":
    # Initialize wrapper
    wrapper = SmolVLM2Wrapper()
    
    # Load model
    load_times = wrapper.load_model()
    
    # Test text processing
    print("📝 Testing text processing...")
    text_result = wrapper.text_query("What are the primary colors in art?")
    print(f"Response: {text_result['response'][:100]}...")
    print(f"Time: {text_result['inference_time']:.2f}s\n")
    
    # Test image processing (if test image available)
    try:
        from PIL import Image, ImageDraw
        
        print("🖼️  Testing image processing...")
        # Create test image
        img = Image.new('RGB', (300, 200), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.ellipse([100, 50, 200, 150], fill='red')
        
        image_result = wrapper.image_query(img, "What do you see in this image?")
        print(f"Response: {image_result['response'][:100]}...")
        print(f"Time: {image_result['inference_time']:.2f}s\n")
        
    except Exception as e:
        print(f"Image test skipped: {e}\n")
    
    # Show model info
    print("ℹ️  Model Information:")
    info = wrapper.get_model_info()
    for key, value in info.items():
        print(f"   {key}: {value}") 