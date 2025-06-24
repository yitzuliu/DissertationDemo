#!/usr/bin/env python3
"""
SmolVLM2 Video Interface (Legacy - Deprecated)
This file has been reorganized. Use the new MLX-optimized video processing:
- inference/video_processing.py for video analysis
"""

# DEPRECATED: This approach uses transformers/torch
# NEW: Use MLX-optimized video processing for Apple Silicon

# Legacy approach (for reference only)
# messages = [
#     {
#         "role": "user",
#         "content": [
#             {"type": "video", "path": "path_to_video.mp4"},
#             {"type": "text", "text": "Describe this video in detail"}
#         ]
#     },
# ]
# 
# inputs = processor.apply_chat_template(
#     messages,
#     add_generation_prompt=True,
#     tokenize=True,
#     return_dict=True,
#     return_tensors="pt",
# ).to(model.device, dtype=torch.bfloat16)
# 
# generated_ids = model.generate(**inputs, do_sample=False, max_new_tokens=64)
# generated_texts = processor.batch_decode(
#     generated_ids,
#     skip_special_tokens=True,
# )
# 
# print(generated_texts[0])

# NEW MLX-optimized video processing example
print("⚠️  DEPRECATED: This file has been reorganized for Apple Silicon optimization")
print("🔄 Use the new MLX-optimized video processing:")
print()
print("Example usage:")
print("  python inference/video_processing.py video.mp4 \\")
print("    --prompt 'Describe this video in detail'")
print()
print("Or programmatically:")
print("  from inference.video_processing import SmolVLM2VideoProcessor")
print("  processor = SmolVLM2VideoProcessor()")
print("  result = processor.process_video('video.mp4', 'Describe this video')")
print("  print(result['response'])")
print()
print("📚 See README.md for complete video processing examples")

# Example of new message format (compatible with MLX-VLM)
def example_video_processing():
    """Example of new MLX-optimized video processing"""
    try:
        from inference.video_processing import SmolVLM2VideoProcessor
        
        processor = SmolVLM2VideoProcessor()
        
        result = processor.process_video(
            video_path="path_to_video.mp4",
            prompt="Describe this video in detail",
            system_prompt="Focus on key actions and important details",
            max_tokens=512,
            temperature=0.7
        )
        
        if result["success"]:
            print("✅ Video processed successfully:")
            print(result["response"])
        else:
            print(f"❌ Error: {result['error']}")
            
    except ImportError:
        print("❌ New video processing not available. Please install requirements:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    example_video_processing()
