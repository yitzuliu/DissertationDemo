# VLM Model Loading Reference Guide

## 📊 **Quick Summary** (2025-07-20)

### **Capability Overview**
| Model | Vision | Pure Text | Context | VQA Accuracy | Simple Accuracy | Framework | Status |
|-------|--------|-----------|---------|--------------|-----------------|-----------|--------|
| **SmolVLM2-500M-Video-MLX** | ✅ 100% | ✅ 100% | ❌ 10% | 51.5% | **60.0%** | MLX | ✅ **Best Overall** |
| **SmolVLM-500M-Instruct** | ✅ 100% | ✅ 100% | ⚠️ 33% | **52.5%** | 55.0% | Transformers | ✅ **Best VQA** |
| **Moondream2** | ✅ 100% | ❌ 0% | ❌ 0% | 53.0% | **60.0%** | Transformers | ✅ **Vision-Only** |
| **LLaVA-v1.6-Mistral-7B-MLX** | ✅ 100% | ✅ 100% | ⚠️ 20% | 27.0% | 25.0% | MLX | ⚠️ **State Issues** |
| **Phi-3.5-Vision-Instruct-MLX** | ✅ 100% | ✅ 100% | ⚠️ 25% | 52.0% | 50.0% | MLX | ✅ **Balanced** |

### **Performance Rankings**
| Rank | Model | Load Time | Inference | VQA Acc | Simple Acc | Context | Status |
|------|-------|-----------|-----------|---------|------------|---------|--------|
| 🥇 | **SmolVLM2-MLX** | 0.38s | 4.23s | 51.5% | **60.0%** | ❌ 10% | ✅ **Fastest** |
| 🥈 | **Moondream2** | 4.96s | 3.89s | 53.0% | **60.0%** | ❌ 0% | ✅ **Best Vision** |
| 🥉 | **SmolVLM** | 3.37s | 6.09s | **52.5%** | 55.0% | ⚠️ 33% | ✅ **Best VQA** |
| 4️⃣ | **Phi-3.5-MLX** | 1.55s | 9.64s | 52.0% | 50.0% | ⚠️ 25% | ✅ **Balanced** |
| 5️⃣ | **LLaVA-MLX** | 2.61s | 15.09s | 27.0% | 25.0% | ⚠️ 20% | ⚠️ **Slow** |

---

## **🔧 Model Loading Methods**

### **1. SmolVLM2-500M-Video-Instruct-MLX** ⭐ **RECOMMENDED**
```python
# Best overall performance - Fast, accurate, MLX optimized
model_id = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"
# Load time: 0.38s | Inference: 4.23s | VQA: 51.5% | Simple: 60.0%
```

### **2. SmolVLM-500M-Instruct** 🏆 **BEST VQA**
```python
# Best VQA accuracy - Transformers framework
model_id = "HuggingFaceTB/SmolVLM-500M-Instruct"
# Load time: 3.37s | Inference: 6.09s | VQA: 52.5% | Simple: 55.0%
```

### **3. Moondream2** 👁️ **VISION-ONLY**
```python
# Vision-only model - No text capability
model_id = "vikhyatk/moondream2"
# Load time: 4.96s | Inference: 3.89s | VQA: 53.0% | Simple: 60.0%
```

### **4. LLaVA-v1.6-Mistral-7B-MLX** ⚠️ **STATE ISSUES**
```python
# Large model with state bugs - Requires reloading
model_id = "mlx-community/llava-v1.6-mistral-7b-4bit"
# Load time: 2.61s | Inference: 15.09s | VQA: 27.0% | Simple: 25.0%
```

### **5. Phi-3.5-Vision-Instruct-MLX** ⚖️ **BALANCED**
```python
# Balanced performance - Good all-around
model_id = "mlx-community/Phi-3.5-vision-instruct-4bit"
# Load time: 1.55s | Inference: 9.64s | VQA: 52.0% | Simple: 50.0%
```

---

## **📈 Detailed Performance Analysis**

### **VQA 2.0 COCO Dataset Results (20 Questions)**
| Model | Correct | Accuracy | VQA Accuracy | Avg Time | Grade |
|-------|---------|----------|--------------|----------|-------|
| **SmolVLM2-MLX** | 12/20 | **60.0%** | 51.5% | 4.23s | 🥇 **A** |
| **Moondream2** | 12/20 | **60.0%** | 53.0% | 3.89s | 🥈 **A** |
| **SmolVLM** | 11/20 | 55.0% | **52.5%** | 6.09s | 🥉 **B+** |
| **Phi-3.5-MLX** | 10/20 | 50.0% | 52.0% | 9.64s | **B** |
| **LLaVA-MLX** | 5/20 | 25.0% | 27.0% | 15.09s | **D** |

### **Context Understanding Capability**
| Model | Success Rate | Context Accuracy | Status |
|-------|--------------|------------------|--------|
| **SmolVLM2-MLX** | 100% | **10%** | ❌ **Poor Context** |
| **SmolVLM** | 100% | **33%** | ⚠️ **Limited Context** |
| **LLaVA-MLX** | 100% | **20%** | ⚠️ **Poor Context** |
| **Phi-3.5-MLX** | 100% | **25%** | ⚠️ **Limited Context** |

### **Text-Only Capability**
| Model | Success Rate | Status |
|-------|--------------|--------|
| **SmolVLM2-MLX** | **100%** | ✅ **Full Support** |
| **SmolVLM** | **100%** | ✅ **Full Support** |
| **LLaVA-MLX** | **100%** | ✅ **Full Support** |
| **Phi-3.5-MLX** | **100%** | ✅ **Full Support** |
| **Moondream2** | **0%** | ❌ **No Support** |

---

## **🎯 Recommendations**

### **For Production Use:**
1. **SmolVLM2-MLX** - Best overall performance, fastest inference
2. **SmolVLM** - Best VQA accuracy, reliable text support
3. **Moondream2** - Best vision-only performance

### **For Development/Testing:**
1. **Phi-3.5-MLX** - Balanced performance, good for experimentation
2. **LLaVA-MLX** - Large model, but has state issues

### **For Specific Use Cases:**
- **VQA Tasks**: SmolVLM (52.5% VQA accuracy)
- **Speed Critical**: SmolVLM2-MLX (4.23s avg inference)
- **Vision-Only**: Moondream2 (60.0% simple accuracy)
- **Text + Vision**: SmolVLM2-MLX (100% text success rate)

---

## **⚠️ Known Issues**

### **LLaVA-MLX State Bugs**
- Model state becomes corrupted after multiple inferences
- Requires model reloading between evaluations
- Fixed in VQA framework with reload strategy

### **Moondream2 Text Limitations**
- Cannot process text-only prompts
- Vision-only model by design
- Not suitable for pure text tasks

### **Context Understanding**
- All models show poor context retention
- SmolVLM has best context accuracy (33%)
- Significant limitation for conversation tasks

---

## **🔄 Framework Compatibility**

### **VQA Framework**
- ✅ All models supported
- ✅ Unified evaluation metrics
- ✅ COCO dataset integration
- ✅ MLX subprocess handling

### **Performance Testing**
- ✅ Load time measurement
- ✅ Memory usage tracking
- ✅ Text-only capability testing
- ✅ Vision capability validation

### **Context Testing**
- ✅ Conversation flow testing
- ✅ Context retention evaluation
- ✅ Forensic-level detail testing

---

**Last Updated:** 2025-07-20  
**Test Environment:** MacBook Air M3 (16GB RAM)  
**Framework Version:** vqa2_enhanced_v1.2