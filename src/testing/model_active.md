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
**HuggingFace ID**: `HuggingFaceTB/SmolVLM2-500M-Video-Instruct`

#### **Loading Method**
```python
from transformers import AutoProcessor, AutoModelForImageTextToText

def load_smolvlm2_video(model_id="HuggingFaceTB/SmolVLM2-500M-Video-Instruct"):
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForImageTextToText.from_pretrained(model_id)
    return model, processor
```

#### **Inference Method**
```python
# Vision + Text
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

# Pure Text
messages = [
    {
        "role": "user",
        "content": [{"type": "text", "text": "What is the capital of France?"}]
    }
]
# Same processing as above, but without image
```

#### **Performance**
- **Load Time**: 4.71s
- **Inference**: 6.61s avg
- **Pure Text**: 3.70s avg
- **Best Use**: Multi-media applications

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
    model, processor = load(model_id)
    return model, processor
```

#### **Inference Method**
```python
from mlx_vlm import generate

# Vision + Text
response = generate(
    model=model,
    processor=processor,
    prompt="Describe this image in detail",
    image="path/to/image.jpg",
    max_tokens=100,
    temp=0.7,
    verbose=False
)

# Pure Text
response = generate(
    model=model,
    processor=processor,
    prompt="What is the capital of France?",
    max_tokens=100,
    verbose=False
)
```

#### **Performance**
- **Load Time**: ~3.0s
- **Vision Inference**: ~8.0s avg
- **Text Generation**: ~3.0s avg
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
1. **LLaVA-MLX**: 3.04s
2. **Phi-3.5-Vision**: 3.01s
3. **SmolVLM-500M**: 3.81s
4. **SmolVLM2-Video**: 4.71s
5. **Moondream2**: 5.56s

### **Inference Speed**
1. **Moondream2**: 6.61s avg
2. **SmolVLM-500M**: 6.51s avg
3. **SmolVLM2-Video**: 6.61s avg
4. **LLaVA-MLX**: 8.57s avg
5. **Phi-3.5-Vision**: 8.0s avg

### **Pure Text Speed**
1. **SmolVLM-500M**: 1.72s avg
2. **SmolVLM2-Video**: 3.70s avg
3. **LLaVA-MLX**: 4.08s avg
4. **Phi-3.5-Vision**: 3.0s avg
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