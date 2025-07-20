# VLM Model Loading Reference Guide

## 📊 **Quick Summary** (2025-07-18)

### **Capability Overview**
| Model | Vision | Pure Text | Context | Framework | Status |
|-------|--------|-----------|---------|-----------|--------|
| **SmolVLM-500M-Instruct** | ✅ 100% | ✅ 100% | ⚠️ 33% | Transformers | ✅ Reliable |
| **SmolVLM2-500M-Video** | ✅ 100% | ✅ 100% | ❌ 10% | Transformers | ✅ Reliable |
| **Moondream2** | ✅ 100% | ❌ 0% | ❌ 0% | Transformers | ✅ Vision-Only |
| **LLaVA-v1.6-Mistral-7B-MLX** | ✅ 100% | ✅ 100% | ⚠️ 20% | MLX | ⚠️ State Issues |
| **Phi-3.5-Vision-Instruct** | ✅ 100% | ✅ 100% | ❌ 0% | MLX-VLM | ✅ Optimized |

### **Key Notes**
- **Local Images**: All models adapted for local image processing
- **Unified Parameters**: `max_new_tokens=100, do_sample=false`
- **MLX Required**: For Apple Silicon (M1/M2/M3) optimization
- **Image Preprocessing**: Max 1024px, aspect ratio preserved

## 🚀 **Model Implementation Guide**

### **1. SmolVLM2-500M-Video-Instruct**
**HuggingFace ID**: `mlx-community/SmolVLM2-500M-Video-Instruct-mlx`

#### **Loading Method**
```python
from mlx_vlm import load

def load_smolvlm2_video(model_id="mlx-community/SmolVLM2-500M-Video-Instruct-mlx"):
    try:
        # 優先使用 MLX-VLM 框架
        from mlx_vlm import load
        model, processor = load(model_id)
        model._is_mlx_model = True
        return model, processor
    except ImportError:
        # 回退到原始版本
        fallback_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
        from transformers import AutoProcessor, AutoModelForImageTextToText
        processor = AutoProcessor.from_pretrained(fallback_id)
        model = AutoModelForImageTextToText.from_pretrained(fallback_id)
        return model, processor
```

#### **Inference Method**
```python
# MLX 版本推理
if hasattr(model, '_is_mlx_model'):
    import subprocess
    import tempfile
    
    # 創建臨時圖像文件
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        temp_image_path = tmp_file.name
        image.save(temp_image_path)
    
    # 使用 MLX-VLM 命令行工具
    cmd = [
        sys.executable, '-m', 'mlx_vlm.generate',
        '--model', 'mlx-community/SmolVLM2-500M-Video-Instruct-mlx',
        '--image', temp_image_path,
        '--prompt', prompt,
        '--max-tokens', '100',
        '--temperature', '0.0'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    # 解析輸出...
else:
    # 標準 transformers 推理
    messages = [
        {
            "role": "user", 
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        }
    ]
    input_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=input_text, images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100, do_sample=False)
    response = processor.decode(outputs[0], skip_special_tokens=True)
```

#### **Performance**
- **Load Time**: 0.53s (MLX optimized)
- **Inference**: 5.75s avg (MLX optimized)
- **Pure Text**: 5.37s avg (MLX optimized)
- **Best Use**: Multi-media applications with Apple Silicon optimization

---

### **2. SmolVLM-500M-Instruct**
**HuggingFace ID**: `HuggingFaceTB/SmolVLM-500M-Instruct`

#### **Loading Method**
```python
from transformers import AutoProcessor, AutoModelForVision2Seq

def load_smolvlm_instruct(model_id="HuggingFaceTB/SmolVLM-500M-Instruct"):
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForVision2Seq.from_pretrained(model_id)
    return model, processor
```

#### **Inference Method**
```python
# Identical to SmolVLM2-Video (same message format)
```

#### **Performance**
- **Load Time**: 3.81s
- **Inference**: 6.51s avg
- **Pure Text**: 1.72s avg (fastest)
- **Best Use**: Fast Q&A, real-time chat

---

### **3. Moondream2**
**HuggingFace ID**: `vikhyatk/moondream2`

#### **Loading Method**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_moondream2(model_id="vikhyatk/moondream2"):
    model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    if torch.backends.mps.is_available():
        model = model.to('mps')
    
    return model, tokenizer
```

#### **Inference Method**
```python
# Special API (cannot use standard pipeline)
device = next(model.parameters()).device
enc_image = model.encode_image(image)
if hasattr(enc_image, 'to'):
    enc_image = enc_image.to(device)
response = model.answer_question(enc_image, prompt, processor)
```

#### **Limitations**
- **Pure Text**: Not supported (architecture requires `image_embeds`)
- **Parameters**: Cannot fully unify generation parameters

#### **Performance**
- **Load Time**: 5.56s
- **Inference**: 6.61s avg (fastest vision)
- **Best Use**: Vision-only tasks

---

### **4. LLaVA-v1.6-Mistral-7B-MLX**
**HuggingFace ID**: `mlx-community/llava-v1.6-mistral-7b-4bit`

#### **Requirements**
```bash
pip install mlx-vlm
```

#### **Loading Method**
```python
from mlx_vlm import load

def load_llava_mlx(model_id="mlx-community/llava-v1.6-mistral-7b-4bit"):
    model, processor = load(model_id)
    return model, processor
```

#### **Inference Method**
```python
from mlx_vlm import generate

# Vision + Text
response = generate(
    model, processor, prompt, 
    image=str(image_path),
    max_tokens=100,
    verbose=False
)

# Pure Text
response = generate(
    model, processor, "Write a poem about technology",
    max_tokens=100,
    verbose=False
)
```

#### **Known Issues**
- **Synthetic Images**: Processing bug with geometric images
- **State Memory**: Same response for different images
- **Solution**: Exclusion list for problematic images

#### **Performance**
- **Load Time**: 3.04s (fastest)
- **Inference**: 8.57s avg
- **Pure Text**: 4.08s avg
- **Best Use**: Creative writing, poetry

---

### **5. Phi-3.5-Vision-Instruct**
**HuggingFace ID**: `mlx-community/Phi-3.5-vision-instruct-4bit`

#### **Requirements**
```bash
pip install mlx-vlm
```

#### **Loading Method**
```python
from mlx_vlm import load

def load_phi3_vision(model_id="mlx-community/Phi-3.5-vision-instruct-4bit"):
    model, processor = load(model_id, trust_remote_code=True)
    return model, processor
```

#### **Inference Method**
```python
from mlx_vlm import generate

# Vision + Text (Simplified - No load_config required)
response = generate(
    model=model,
    processor=processor,
    prompt="Describe this image in detail",
    image="path/to/image.jpg",
    max_tokens=100,
    temp=0.0,
    verbose=False
)

# Pure Text
response = generate(
    model=model,
    processor=processor,
    prompt="What is the capital of France?",
    max_tokens=100,
    temp=0.0,
    verbose=False
)
```

#### **Key Improvements (2025-07-18)**
- **✅ Simplified Inference**: Removed unnecessary `load_config` calls
- **✅ No Manual Confirmation**: Eliminated interactive prompts
- **✅ Consistent Implementation**: All files use same inference method
- **✅ Optimized Performance**: Faster loading and inference

#### **Performance**
- **Load Time**: 1.38s (optimized)
- **Vision Inference**: 10.00s avg (improved)
- **Text Generation**: 5.30s avg (improved)
- **Best Use**: Vision-language tasks, educational applications

## 🛠️ **Technical Notes**

### **Apple Silicon Optimization**
- **MLX Framework**: Required for LLaVA (mlx-vlm) and Phi-3.5-Vision (mlx-vlm)
- **Installation**: `pip install mlx-vlm`
- **Performance**: 98%+ speed improvement vs transformers
- **Memory**: More efficient usage with INT4 quantization

### **Local Image Adaptation**
- **Standard Format**: `{"type": "image", "image": image_object}`
- **Phi-3.5-Vision**: Uses `str(image_path)` instead
- **Preprocessing**: Unified scaling to max 1024px
- **Support**: JPG, JPEG, PNG, BMP

### **Memory Management**
- **Sequential Loading**: One model at a time
- **Cleanup**: `del model, gc.collect(), torch.mps.empty_cache()`
- **Timeout**: 60s (small), 180s (large models)

## 📊 **Performance Comparison**

### **Loading Speed**
1. **Phi-3.5-Vision**: 1.38s (optimized)
2. **LLaVA-MLX**: 3.04s
3. **SmolVLM-500M**: 3.81s
4. **SmolVLM2-Video**: 4.71s
5. **Moondream2**: 5.56s

### **Inference Speed**
1. **Moondream2**: 6.61s avg
2. **SmolVLM-500M**: 6.51s avg
3. **SmolVLM2-Video**: 6.61s avg
4. **LLaVA-MLX**: 8.57s avg
5. **Phi-3.5-Vision**: 13.61s avg

### **Pure Text Speed**
1. **SmolVLM-500M**: 1.72s avg
2. **Phi-3.5-Vision**: 6.49s avg
3. **SmolVLM2-Video**: 3.70s avg
4. **LLaVA-MLX**: 4.08s avg
5. **Moondream2**: Not supported

## 🎯 **Recommendations**

### **Best Use Cases**
- **General Purpose**: SmolVLM-500M-Instruct
- **Fast Q&A**: SmolVLM-500M-Instruct
- **Creative Writing**: LLaVA-MLX
- **Educational**: Phi-3.5-Vision-Instruct
- **Vision-Only**: Moondream2

### **Avoid**
- **LLaVA-MLX**: State memory issues
- **Transformers Phi-3.5**: Complete failure on Apple Silicon