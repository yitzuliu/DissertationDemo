# VLM Model Loading Reference Guide

## 📊 **Quick Summary** (2025-07-22)

### **Capability Overview**
| Model | Vision | Pure Text | Avg Inference (s) | Load Time (s) | Memory Diff (GB) | Status |
|-------|--------|-----------|-------------------|---------------|------------------|--------|
| SmolVLM2-500M-Video-Instruct | ✅ | ✅ | 6.20 | 1.02 | 0.06 | Best Overall |
| SmolVLM-500M-Instruct | ✅ | ✅ | 3.40 | 4.07 | 1.95 | Best Context |
| Moondream2 | ✅ | ❌ | 5.89 | 5.34 | -1.15 | Vision-Only |
| LLaVA-v1.6-Mistral-7B-MLX | ✅ | ✅ | 6.70 | 3.05 | -0.40 | State Issues |
| Phi-3.5-Vision-Instruct | ✅ | ✅ | 10.10 | 1.52 | 0.28 | Balanced |

---

## **Model Loading Methods**

### SmolVLM2-500M-Video-Instruct
```python
model_id = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"
# Load time: 1.02s | Avg Inference: 6.20s | Memory Diff: 0.06GB
```

### SmolVLM-500M-Instruct
```python
model_id = "HuggingFaceTB/SmolVLM-500M-Instruct"
# Load time: 4.07s | Avg Inference: 3.40s | Memory Diff: 1.95GB
```

### Moondream2
```python
model_id = "vikhyatk/moondream2"
# Load time: 5.34s | Avg Inference: 5.89s | Memory Diff: -1.15GB
```

### LLaVA-v1.6-Mistral-7B-MLX
```python
model_id = "mlx-community/llava-v1.6-mistral-7b-4bit"
# Load time: 3.05s | Avg Inference: 6.70s | Memory Diff: -0.40GB
```

### Phi-3.5-Vision-Instruct
```python
model_id = "mlx-community/Phi-3.5-vision-instruct-4bit"
# Load time: 1.52s | Avg Inference: 10.10s | Memory Diff: 0.28GB
```

---

## **Recommendations**
- **Best Overall:** SmolVLM2-500M-Video-Instruct (fast, accurate, MLX optimized)
- **Best Context:** SmolVLM-500M-Instruct (best context retention)
- **Best Vision-Only:** Moondream2 (vision tasks, no text-only)
- **Balanced:** Phi-3.5-Vision-Instruct (good all-around, moderate speed)
- **Avoid for Production:** LLaVA-v1.6-Mistral-7B-MLX (state issues, incomplete context)

---

## **Known Issues**
- LLaVA-MLX: Model state may become corrupted after multiple inferences; requires reloading.
- Moondream2: Cannot process text-only prompts; vision-only model.
- All models: Context retention remains limited for multi-turn tasks.

---

**Last Updated:** 2025-07-22 13:01:28  
**Test Environment:** MacBook Air M3 (16GB RAM)