# VLM Model Loading Reference Guide

## 📊 **Quick Summary** (2025-07-22)

### **Capability Overview**
| Model | Vision | Pure Text | Avg Inference (s) | Load Time (s) | Memory Diff (GB) | Status |
|-------|--------|-----------|-------------------|---------------|------------------|--------|
| SmolVLM2-500M-Video-Instruct | ✅ | ✅ | 6.45 | 0.90 | 0.29 | Best Overall |
| SmolVLM-500M-Instruct | ✅ | ✅ | 11.08 | 3.22 | 1.94 | Best VQA |
| Moondream2 | ✅ | ❌ | 6.39 | 6.46 | -0.82 | Vision-Only |
| LLaVA-v1.6-Mistral-7B-MLX | ✅ | ✅ | 22.39 | 2.92 | -0.42 | State Issues |
| Phi-3.5-Vision-Instruct | ✅ | ✅ | 37.75 | 3.20 | -0.02 | Balanced |

---

## **Model Loading Methods**

### SmolVLM2-500M-Video-Instruct
```python
model_id = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"
# Load time: 0.90s | Avg Inference: 6.45s | Memory Diff: 0.29GB
```

### SmolVLM-500M-Instruct
```python
model_id = "HuggingFaceTB/SmolVLM-500M-Instruct"
# Load time: 3.22s | Avg Inference: 11.08s | Memory Diff: 1.94GB
```

### Moondream2
```python
model_id = "vikhyatk/moondream2"
# Load time: 6.46s | Avg Inference: 6.39s | Memory Diff: -0.82GB
```

### LLaVA-v1.6-Mistral-7B-MLX
```python
model_id = "mlx-community/llava-v1.6-mistral-7b-4bit"
# Load time: 2.92s | Avg Inference: 22.39s | Memory Diff: -0.42GB
```

### Phi-3.5-Vision-Instruct
```python
model_id = "mlx-community/Phi-3.5-vision-instruct-4bit"
# Load time: 3.20s | Avg Inference: 37.75s | Memory Diff: -0.02GB
```

---

## **Recommendations**
- **Best Overall:** SmolVLM2-500M-Video-Instruct (fast, accurate, MLX optimized)
- **Best VQA:** SmolVLM-500M-Instruct (highest VQA accuracy)
- **Best Vision-Only:** Moondream2 (vision tasks, no text-only)
- **Balanced:** Phi-3.5-Vision-Instruct (good all-around, slower)
- **Avoid for Production:** LLaVA-v1.6-Mistral-7B-MLX (slow, state issues)

---

## **Known Issues**
- LLaVA-MLX: Model state may become corrupted after multiple inferences; requires reloading.
- Moondream2: Cannot process text-only prompts; vision-only model.
- All models: Context retention remains limited for multi-turn tasks.

---

**Last Updated:** 2025-07-22  
**Test Environment:** MacBook Air M3 (16GB RAM)