# VLM Model Loading Reference Guide

## 📊 **Quick Summary** (2025-07-28)

### **Capability Overview**
| Model | Vision | Pure Text | Avg Inference (s) | Load Time (s) | Memory Diff (GB) | Status |
|-------|--------|-----------|-------------------|---------------|------------------|--------|
| **Moondream2** | ✅ | ❌ | 11.58 | 5.34 | -1.15 | **Best Overall** |
| SmolVLM-500M-Instruct (GGUF) | ✅ | ✅ | **0.93** | 2.04 | 0.07 | **Fastest** |
| SmolVLM2-500M-Video-Instruct | ✅ | ✅ | 9.80 | 1.02 | 0.06 | Fast & Accurate |
| Phi-3.5-Vision-Instruct | ✅ | ✅ | 10.54 | 1.52 | 0.28 | Balanced |
| LLaVA-v1.6-Mistral-7B-MLX | ✅ | ✅ | 21.93 | 2.17 | 0.46 | **Issues** |

---

## **Model Loading Methods**

### **Moondream2** - **Best Overall Performance**
```python
model_id = "vikhyatk/moondream2"
# Load time: 5.34s | Avg Inference: 11.58s | Memory Diff: -1.15GB
# Features: Fastest inference, best accuracy, vision-only
# VQA Accuracy: 52.5% | Simple Accuracy: 60.0%
```

### **SmolVLM-500M-Instruct (GGUF)** - **Fastest**
```python
# Unified GGUF approach via HTTP API (Production Ready)
model_id = "ggml-org/SmolVLM-500M-Instruct-GGUF"
api_endpoint = "http://localhost:8080/v1/chat/completions"
# Load time: 2.04s | Avg Inference: 0.93s | Memory Diff: 0.07GB
# Features: Automatic server management, port cleanup, unified API
# VQA Accuracy: 39.5% | Simple Accuracy: 40.0%
```

### **SmolVLM2-500M-Video-Instruct** - **Fast & Accurate**
```python
model_id = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"
# Load time: 1.02s | Avg Inference: 9.80s | Memory Diff: 0.06GB
# VQA Accuracy: 51.5% | Simple Accuracy: 60.0%
```

### **Phi-3.5-Vision-Instruct** - **Balanced**
```python
model_id = "mlx-community/Phi-3.5-vision-instruct-4bit"
# Load time: 1.52s | Avg Inference: 10.54s | Memory Diff: 0.28GB
# VQA Accuracy: 42.5% | Simple Accuracy: 40.0%
```

### **LLaVA-v1.6-Mistral-7B-MLX** - **Issues**
```python
model_id = "mlx-community/llava-v1.6-mistral-7b-4bit"
# Load time: 2.17s | Avg Inference: 21.93s | Memory Diff: 0.46GB
# VQA Accuracy: 27.0% | Simple Accuracy: 25.0%
```

---

## **Recommendations**
- **Best Overall:** **Moondream2** - Highest accuracy, balanced speed
- **Fastest:** SmolVLM-500M-Instruct (GGUF) - **Fastest inference, unified API, automatic server management**
- **Best Context:** SmolVLM-500M-Instruct (GGUF) - **Best context retention with production stability**
- **Fast & Accurate:** SmolVLM2-500M-Video-Instruct (good balance of speed and accuracy)
- **Balanced:** Phi-3.5-Vision-Instruct (good all-around, moderate speed)
- **Avoid for Production:** LLaVA-v1.6-Mistral-7B-MLX (dimension errors after first inference, batch inference issues)

---

## **Known Issues**
- **LLaVA-MLX**: 
  - Model state becomes corrupted after first inference; subsequent inferences fail with dimension errors
  - Error: "input operand has more dimensions than allowed by the axis remapping"
  - Workaround: Reload model for each image (implemented in vlm_tester.py)
  - Text-only inference works correctly
  - Poor VQA performance (27.0% accuracy)
- **Moondream2**: Cannot process text-only prompts; vision-only model.
- **All models**: Context retention remains limited for multi-turn tasks.

## **Recent Improvements** (2025-07-28)
- ✅ **Moondream2 Performance**: Now the best overall performer with 60.0% accuracy
- ✅ **SmolVLM GGUF Unification**: All test scripts now use unified GGUF approach via HTTP API
- ✅ **Port Safety**: Automatic cleanup of SmolVLM server processes on exit
- ✅ **Server Management**: Automatic startup, port conflict resolution, and retry mechanisms
- ✅ **Performance**: SmolVLM GGUF shows consistent performance with production deployment
- ✅ **Memory Efficiency**: Reduced memory usage across all models
- ✅ **Production Stability**: Consistent with production deployment architecture

## **Performance Rankings** (Updated 2025-07-28)

### **Speed Rankings**
1. **SmolVLM GGUF:** 0.93s avg inference
2. **SmolVLM2-MLX:** 9.80s avg inference
3. **Phi-3.5-MLX:** 10.54s avg inference
4. **Moondream2:** 11.58s avg inference
5. **LLaVA-MLX:** 21.93s avg inference

### **Accuracy Rankings**
1. **Moondream2:** 60.0% simple accuracy
2. **SmolVLM2-MLX:** 60.0% simple accuracy
3. **Phi-3.5-MLX:** 42.5% VQA accuracy
4. **SmolVLM GGUF:** 40.0% simple accuracy, 39.5% VQA accuracy
5. **LLaVA-MLX:** 25.0% simple accuracy

---

**Last Updated:** 2025-07-28 21:48:39  
**Test Environment:** MacBook Air M3 (16GB RAM)  
**Unified Architecture:** SmolVLM GGUF via HTTP API with automatic server management