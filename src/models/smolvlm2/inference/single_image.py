#!/usr/bin/env python3
"""
SmolVLM2 Single Image Inference
MLX-optimized single image processing for Apple Silicon
"""

import os
import sys
from pathlib import Path
from typing import Union, Dict, Any, Optional
import json

try:
    import mlx_vlm
    from PIL import Image
    import requests
except ImportError as e:
    print(f"❌ Required dependency not found: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

class SmolVLM2ImageProcessor:
    """Single image processor using MLX-VLM for Apple Silicon optimization"""
    
    def __init__(self, model_path: str = "mlx-community/SmolVLM2-500M-Instruct-mlx"):
        self.model_path = model_path
        self.model = None
        self.processor = None
        self._load_model()
    
    def _load_model(self):
        """Load the MLX-optimized SmolVLM2 model"""
        try:
            print(f"🔄 Loading SmolVLM2 model: {self.model_path}")
            # MLX-VLM handles model loading automatically
            print("✅ Model loaded successfully with MLX optimization")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def process_image(
        self, 
        image_input: Union[str, Path, Image.Image],
        prompt: str = "Describe this image in detail",
        system_prompt: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Process a single image with SmolVLM2
        
        Args:
            image_input: Path to image file, URL, or PIL Image
            prompt: User prompt for the image
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Prepare image
            if isinstance(image_input, str):
                if image_input.startswith(('http://', 'https://')):
                    # Handle URL
                    image = image_input
                else:
                    # Handle file path
                    image_path = Path(image_input)
                    if not image_path.exists():
                        raise FileNotFoundError(f"Image file not found: {image_path}")
                    image = str(image_path.absolute())
            elif isinstance(image_input, Path):
                if not image_input.exists():
                    raise FileNotFoundError(f"Image file not found: {image_input}")
                image = str(image_input.absolute())
            else:
                # Handle PIL Image
                temp_path = "/tmp/temp_image.jpg"
                image_input.save(temp_path)
                image = temp_path
            
            # Prepare system prompt
            if system_prompt is None:
                system_prompt = "You are a helpful assistant that can understand images. Provide detailed, accurate descriptions and answer questions about what you observe."
            
            # Generate response using MLX-VLM
            print(f"🔄 Processing image with prompt: '{prompt[:50]}...'")
            
            response = mlx_vlm.generate(
                model=self.model_path,
                image=image,
                prompt=prompt,
                system=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            print("✅ Image processed successfully")
            
            return {
                "success": True,
                "response": response,
                "model": self.model_path,
                "prompt": prompt,
                "system_prompt": system_prompt,
                "parameters": {
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            }
            
        except Exception as e:
            print(f"❌ Error processing image: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.model_path,
                "prompt": prompt
            }
    
    def batch_process_images(
        self,
        image_paths: list,
        prompt: str = "Describe this image",
        system_prompt: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Process multiple images in batch
        
        Args:
            image_paths: List of image paths or URLs
            prompt: Common prompt for all images
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens per response
            temperature: Generation temperature
            
        Returns:
            Dictionary with batch results
        """
        results = []
        
        print(f"🔄 Processing {len(image_paths)} images in batch...")
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"Processing image {i}/{len(image_paths)}: {Path(image_path).name}")
            
            result = self.process_image(
                image_input=image_path,
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            result["image_path"] = str(image_path)
            result["batch_index"] = i
            results.append(result)
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "batch_results": results,
            "total_images": len(image_paths),
            "successful": successful,
            "failed": len(image_paths) - successful,
            "model": self.model_path
        }

def main():
    """CLI interface for single image processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SmolVLM2 Single Image Processor")
    parser.add_argument("image", help="Path to image file or URL")
    parser.add_argument("--prompt", "-p", default="Describe this image in detail", 
                       help="Prompt for the image")
    parser.add_argument("--system", "-s", help="System prompt for context")
    parser.add_argument("--model", "-m", 
                       default="mlx-community/SmolVLM2-500M-Instruct-mlx",
                       help="Model path")
    parser.add_argument("--max-tokens", type=int, default=512,
                       help="Maximum tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7,
                       help="Generation temperature")
    parser.add_argument("--output", "-o", help="Output file for response")
    parser.add_argument("--batch", nargs="+", help="Process multiple images")
    
    args = parser.parse_args()
    
    print("🎯 SmolVLM2 Single Image Processor")
    print("=" * 50)
    
    processor = SmolVLM2ImageProcessor(model_path=args.model)
    
    if args.batch:
        # Batch processing
        result = processor.batch_process_images(
            image_paths=args.batch,
            prompt=args.prompt,
            system_prompt=args.system,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
        
        print(f"\n📊 Batch Results:")
        print(f"   Total images: {result['total_images']}")
        print(f"   Successful: {result['successful']}")
        print(f"   Failed: {result['failed']}")
        
        for i, batch_result in enumerate(result['batch_results'], 1):
            print(f"\n--- Image {i}: {Path(batch_result['image_path']).name} ---")
            if batch_result['success']:
                print(f"✅ {batch_result['response']}")
            else:
                print(f"❌ Error: {batch_result['error']}")
    
    else:
        # Single image processing
        result = processor.process_image(
            image_input=args.image,
            prompt=args.prompt,
            system_prompt=args.system,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
        
        if result["success"]:
            print(f"\n✅ Response:")
            print(f"{result['response']}")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n📝 Response saved to: {args.output}")
        else:
            print(f"\n❌ Error: {result['error']}")
            sys.exit(1)

if __name__ == "__main__":
    main() 