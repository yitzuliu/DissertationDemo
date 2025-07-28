# VLM Model Loading Reference Guide

## 📊 **Quick Summary** (2025-07-28)

### **Capability Overview**
| Model | Vision | Pure Text | Avg Inference (s) | Load Time (s) | Memory Diff (GB) | Status |
|-------|--------|-----------|-------------------|---------------|------------------|--------|
| SmolVLM-500M-Instruct (GGUF) | ✅ | ✅ | 0.32 | 2.04 | 0.07 | **Production Ready** |
| SmolVLM2-500M-Video-Instruct | ✅ | ✅ | 6.20 | 1.02 | 0.06 | Best Overall |
| Moondream2 | ✅ | ❌ | 5.89 | 5.34 | -1.15 | Vision-Only |
| LLaVA-v1.6-Mistral-7B-MLX | ✅ | ✅ | 6.70 | 3.05 | -0.40 | State Issues |
| Phi-3.5-Vision-Instruct | ✅ | ✅ | 10.10 | 1.52 | 0.28 | Balanced |

---

## **Model Loading Methods**

### SmolVLM-500M-Instruct (GGUF) - **Recommended**
```python
# Unified GGUF approach via HTTP API (Production Ready)
model_id = "ggml-org/SmolVLM-500M-Instruct-GGUF"
api_endpoint = "http://localhost:8080/v1/chat/completions"
# Load time: 2.04s | Avg Inference: 0.32s | Memory Diff: 0.07GB
# Features: Automatic server management, port cleanup, unified API
```

### SmolVLM2-500M-Video-Instruct
```python
model_id = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"
# Load time: 1.02s | Avg Inference: 6.20s | Memory Diff: 0.06GB
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
- **Production Ready:** SmolVLM-500M-Instruct (GGUF) - **Fastest inference, unified API, automatic server management**
- **Best Overall:** SmolVLM2-500M-Video-Instruct (fast, accurate, MLX optimized)
- **Best Context:** SmolVLM-500M-Instruct (GGUF) - **Best context retention with production stability**
- **Best Vision-Only:** Moondream2 (vision tasks, no text-only)
- **Balanced:** Phi-3.5-Vision-Instruct (good all-around, moderate speed)
- **Avoid for Production:** LLaVA-v1.6-Mistral-7B-MLX (state issues, incomplete context)

---

## **Known Issues**
- LLaVA-MLX: Model state may become corrupted after multiple inferences; requires reloading.
- Moondream2: Cannot process text-only prompts; vision-only model.
- All models: Context retention remains limited for multi-turn tasks.

## **Recent Improvements** (2025-07-28)
- ✅ **SmolVLM GGUF Unification**: All test scripts now use unified GGUF approach via HTTP API
- ✅ **Port Safety**: Automatic cleanup of SmolVLM server processes on exit
- ✅ **Server Management**: Automatic startup, port conflict resolution, and retry mechanisms
- ✅ **Performance**: SmolVLM GGUF shows 10x faster inference (0.32s vs 3.40s)
- ✅ **Memory Efficiency**: Reduced memory usage (0.07GB vs 1.95GB)
- ✅ **Production Stability**: Consistent with production deployment architecture

---

**Last Updated:** 2025-07-28 12:30:00  
**Test Environment:** MacBook Air M3 (16GB RAM)  
**Unified Architecture:** SmolVLM GGUF via HTTP API with automatic server management