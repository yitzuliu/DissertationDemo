# SmolVLM2 Testing Guide 🤏

This guide provides everything you need to test the SmolVLM2 model with various capabilities including image description, visual QA, multi-image processing, and video inference.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r smolvlm2_requirements.txt
```

If you're on macOS and want to use MLX for faster inference:
```bash
pip install mlx-vlm
```

### 2. Quick Test (Recommended)

For a simple, fast test:
```bash
python quick_test_smolvlm2.py
```

### 3. Comprehensive Test Suite

For extensive testing with multiple capabilities:
```bash
python test_smolvlm2.py
```

## What You Can Test

### 🖼️ Image Description
- Single image analysis and detailed descriptions
- Object detection and scene understanding
- Color and composition analysis

### ❓ Visual Question Answering
- Ask specific questions about images
- Interactive Q&A sessions
- Context-aware responses

### 🎭 Creative Tasks
- Generate stories inspired by images
- Create poems based on visual content
- Imaginative scenarios and narratives

### 📸 Multiple Image Processing
- Compare and contrast multiple images
- Find relationships between images
- Cross-image reasoning

### 🎬 Video Analysis
Available through the dedicated video inference script:
```bash
python src/models/smolvlm2/smollm/tools/smolvlm_local_inference/SmolVLM_video_inference.py
```

## Available Test Scripts

### 1. `quick_test_smolvlm2.py`
- Lightweight, single-image test
- Good for verification and quick demos
- Minimal resource usage

### 2. `test_smolvlm2.py`
- Comprehensive test suite
- Multiple test scenarios
- Performance timing included
- Includes online image testing

### 3. Video Inference Script
- Located in: `src/models/smolvlm2/smollm/tools/smolvlm_local_inference/SmolVLM_video_inference.py`
- Supports video file processing
- Extracts frames intelligently
- Generates video descriptions

## Model Capabilities

SmolVLM2 is a compact multimodal model that can:

- **Process images and text**: Handle arbitrary sequences of image and text inputs
- **Multiple images**: Work with multiple images in a single conversation
- **Efficient on-device**: Designed for local inference with good performance
- **Text-only mode**: Can function as a pure language model without visual inputs
- **Video understanding**: Basic video analysis through frame extraction

## Performance Expectations

- **Model Size**: Compact (~2B parameters)
- **Memory Usage**: ~4-8GB GPU memory (depending on configuration)
- **Speed**: Fast inference, especially with optimizations like Flash Attention 2
- **Quality**: Strong performance on multimodal tasks despite compact size

## Troubleshooting

### Common Issues

1. **Out of Memory**
   ```bash
   # Use CPU if GPU memory is insufficient
   export CUDA_VISIBLE_DEVICES=""
   ```

2. **Model Download Issues**
   - Ensure stable internet connection
   - The model (~2GB) will be downloaded on first use
   - Check Hugging Face Hub access

3. **Flash Attention Errors**
   - Flash Attention 2 requires compatible CUDA setup
   - The script automatically falls back to eager attention if needed

4. **Image Loading Issues**
   - Ensure PIL/Pillow is properly installed
   - Check image file formats (JPEG, PNG supported)
   - Verify image paths are correct

### Performance Tips

1. **GPU Usage**
   - Use CUDA if available for best performance
   - Enable Flash Attention 2 for faster inference

2. **Memory Optimization**
   - Use `torch.bfloat16` for reduced memory usage
   - Batch smaller images together

3. **MLX on Mac**
   ```bash
   pip install mlx-vlm
   python -m mlx_vlm.chat_ui --model mlx-community/SmolVLM-Instruct-8bit
   ```

## Test Images

The scripts use test images from:
- `src/models/phi3_vision/debug/images/`

Available test images:
- `test_image.png`
- `sample.jpg`
- `test.jpg`
- `IMG_0119.JPG`

## Example Output

```
🚀 Quick SmolVLM2 Test
----------------------------------------
Using device: cuda
📸 Using image: src/models/phi3_vision/debug/images/test_image.png
Loading model...
Processing image...
Generating response...

✅ Response:
The image shows a beautiful landscape with mountains in the background and a clear blue sky. There's a winding path leading through green fields, with some trees scattered around the area. The lighting suggests it's either early morning or late afternoon, creating a peaceful and serene atmosphere.
```

## Advanced Usage

### Custom Prompts

You can modify the test scripts to use your own prompts:

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "Your custom question here"}
        ]
    }
]
```

### Multiple Images

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "image"},
            {"type": "text", "text": "Compare these images"}
        ]
    }
]
```

## Resources

- **Model on Hugging Face**: [HuggingFaceTB/SmolVLM-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-Instruct)
- **SmolVLM Blog Post**: https://huggingface.co/blog/smolvlm
- **SmolLM2 Collection**: https://huggingface.co/collections/HuggingFaceTB/smollm2-6723884218bcda64b34d7db9

## Next Steps

After testing, you can:
1. Fine-tune the model on your specific use case
2. Integrate into your applications
3. Explore video inference capabilities
4. Deploy for production use

Happy testing! 🎉 