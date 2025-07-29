# VLM Model Loading Reference Guide

## 📊 **Quick Summary** (2025-07-29)

### **Comprehensive Performance Overview**
| Model | Vision | Pure Text | VQA Acc | Simple Acc | Avg Inference (s) | Load Time (s) | Memory Diff (GB) | Status |
|-------|--------|-----------|---------|------------|-------------------|---------------|------------------|--------|
| **Moondream2** | ✅ | ❌ | **63.0%** | **65.0%** | 5.82 | 16.61 | -0.09 | 🥇 **Best Overall** |
| SmolVLM2-500M-Video-Instruct | ✅ | ✅ | 56.5% | 60.0% | 6.50 | 1.48 | 0.13 | 🥈 **Balanced** |
| SmolVLM-500M-Instruct (GGUF) | ✅ | ✅ | 39.5% | 35.0% | **0.27** | 4.05 | 0.001 | ⚡ **Fastest** |
| Phi-3.5-Vision-Instruct | ✅ | ✅ | 49.5% | 35.0% | 5.06 | 1.71 | 0.05 | 🥉 **Fast** |
| LLaVA-v1.6-Mistral-7B-MLX | ✅ | ✅ | 28.5% | 20.0% | 25.37 | 6.07 | -0.48 | ⚠️ **Critical Issues** |

---

## **Model Loading Methods & Performance Details**

### **🥇 Moondream2** - **Best Overall Performance**
```python
model_id = "vikhyatk/moondream2"
# Load time: 16.61s | Avg Inference: 5.82s | Memory Diff: -0.09GB
# VQA Accuracy: 63.0% | Simple Accuracy: 65.0%
# Features: Highest accuracy, excellent yes/no questions, vision-only
# Strengths: Object recognition, spatial reasoning, color identification
# Limitations: Cannot process text-only input, slower loading
```

### **🥈 SmolVLM2-500M-Video-Instruct** - **Balanced Performance**
```python
model_id = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"
# Load time: 1.48s | Avg Inference: 6.50s | Memory Diff: 0.13GB
# VQA Accuracy: 56.5% | Simple Accuracy: 60.0%
# Features: Best balance of speed and accuracy, supports text-only
# Strengths: Color perception, object identification, fast loading
# Context Issues: Provides generic responses without image context
```

### **⚡ SmolVLM-500M-Instruct (GGUF)** - **Fastest Inference**
```python
# Unified GGUF approach via HTTP API (Production Ready)
model_id = "ggml-org/SmolVLM-500M-Instruct-GGUF"
api_endpoint = "http://localhost:8080/v1/chat/completions"
# Load time: 4.05s | Avg Inference: 0.27s | Memory Diff: 0.001GB
# VQA Accuracy: 39.5% | Simple Accuracy: 35.0%
# Features: Extremely fast inference, automatic server management, unified API
# Strengths: Real-time applications, minimal memory usage
# Trade-offs: Lower accuracy for extreme speed
```

### **🥉 Phi-3.5-Vision-Instruct** - **Fast with Good VQA**
```python
model_id = "mlx-community/Phi-3.5-vision-instruct-4bit"
# Load time: 1.71s | Avg Inference: 5.06s | Memory Diff: 0.05GB
# VQA Accuracy: 49.5% | Simple Accuracy: 35.0%
# Features: Good VQA performance despite lower simple accuracy
# Strengths: Detailed responses, spatial reasoning
# Context Issues: Returns empty responses for text-only context questions
```

### **⚠️ LLaVA-v1.6-Mistral-7B-MLX** - **Critical Performance Issues**
```python
model_id = "mlx-community/llava-v1.6-mistral-7b-4bit"
# Load time: 6.07s | Avg Inference: 25.37s | Memory Diff: -0.48GB
# VQA Accuracy: 28.5% | Simple Accuracy: 20.0%
# Critical Issues: Extremely slow, poor accuracy, batch inference problems
# Problems: State corruption, repetitive responses, requires model reloading
# Status: NOT RECOMMENDED for production use
```

---

## **🎯 Production Recommendations**

### **For High-Accuracy VQA Applications**
**🥇 Use: Moondream2**
- Highest VQA accuracy (63.0%) and simple accuracy (65.0%)
- Excellent for yes/no questions (77.8% accuracy)
- Best object recognition and spatial reasoning
- Reasonable inference time (5.82s)
- **Trade-off:** Vision-only, cannot process text-only input

### **For Real-Time Applications**
**⚡ Use: SmolVLM-500M-Instruct (GGUF)**
- Fastest inference (0.27s) - 20x faster than others
- Production-ready with unified API and automatic server management
- Minimal memory usage (0.001GB diff)
- **Trade-off:** Lower accuracy (35.0% simple, 39.5% VQA)

### **For Balanced Performance**
**🥈 Use: SmolVLM2-500M-Video-Instruct**
- Good accuracy (60.0% simple, 56.5% VQA)
- Reasonable speed (6.50s)
- Best color perception (75.0% accuracy)
- Supports both vision and text-only input
- **Best overall balance** of speed, accuracy, and features

### **For Development/Testing**
**🥉 Use: Phi-3.5-Vision-Instruct**
- Good VQA performance (49.5%) despite lower simple accuracy
- Fast inference (5.06s) and loading (1.71s)
- Detailed responses for analysis
- **Trade-off:** Context understanding issues

### **❌ Avoid for Production**
**⚠️ LLaVA-v1.6-Mistral-7B-MLX**
- Extremely slow (25.37s inference)
- Poor accuracy (20.0% simple, 28.5% VQA)
- Critical batch inference issues
- Requires model reloading between images
- **Not suitable for any production use case**

---

## **🚨 Critical Issues & Limitations**

### **Context Understanding Crisis**
**⚠️ ALL MODELS HAVE 0% TRUE CONTEXT UNDERSTANDING**
- **Phi-3.5 & LLaVA-MLX:** Return empty responses to context questions
- **Moondream2:** Explicitly states cannot answer without image
- **SmolVLM models:** Provide hallucinated responses (claim "red, white, blue" for all images)
- **Implication:** Multi-turn conversations require external memory systems

### **LLaVA-MLX Specific Issues**
- **Batch Processing:** Model state corruption after first inference
- **Performance:** 5x slower than other models (25.37s vs ~5-6s)
- **Accuracy:** Lowest performance across all metrics
- **Responses:** Verbose, repetitive, often incorrect
- **Technical Error:** "input operand has more dimensions than allowed by the axis remapping"
- **Workaround:** Model reloading required for each image (implemented)

### **Universal Challenges**
- **Text Reading:** All models struggle with text in images (0% success on "PED XING" sign)
- **Counting Tasks:** Poor performance across all models (0-50% accuracy)
- **Color Perception:** Frequent errors (white vs. gray, blue vs. green)
- **Context Retention:** No model can maintain conversation context

## **Recent Test Results** (2025-07-29)
- ✅ **Comprehensive VQA 2.0 Testing**: 20-question evaluation with COCO val2014 dataset
- ✅ **Context Understanding Assessment**: Multi-turn conversation capability testing
- ✅ **Performance Benchmarking**: Load time, inference speed, memory usage analysis
- ✅ **Issue Identification**: Critical problems with LLaVA-MLX and context understanding
- ✅ **Production Readiness**: SmolVLM GGUF unified API with automatic server management
- ✅ **Accuracy Improvements**: Moondream2 now achieves 65.0% simple accuracy
- ✅ **Speed Optimization**: SmolVLM GGUF achieves 0.27s inference time

## **Performance Rankings** (Updated 2025-07-29)

### **🏆 Overall Performance Rankings**
1. **🥇 Moondream2:** 65.0% simple, 63.0% VQA, 5.82s inference
2. **🥈 SmolVLM2-MLX:** 60.0% simple, 56.5% VQA, 6.50s inference  
3. **🥉 Phi-3.5-MLX:** 35.0% simple, 49.5% VQA, 5.06s inference
4. **⚡ SmolVLM GGUF:** 35.0% simple, 39.5% VQA, 0.27s inference
5. **⚠️ LLaVA-MLX:** 20.0% simple, 28.5% VQA, 25.37s inference

### **⚡ Speed Rankings**
1. **SmolVLM GGUF:** 0.27s (fastest by 20x)
2. **Phi-3.5-MLX:** 5.06s
3. **Moondream2:** 5.82s
4. **SmolVLM2-MLX:** 6.50s
5. **LLaVA-MLX:** 25.37s (critical performance issue)

### **🎯 Accuracy Rankings (VQA 2.0)**
1. **Moondream2:** 63.0% VQA accuracy
2. **SmolVLM2-MLX:** 56.5% VQA accuracy
3. **Phi-3.5-MLX:** 49.5% VQA accuracy
4. **SmolVLM GGUF:** 39.5% VQA accuracy
5. **LLaVA-MLX:** 28.5% VQA accuracy

### **📊 Question Type Performance**
- **Yes/No Questions:** Moondream2 (77.8%) > SmolVLM2 (55.6%) > Others (~44%)
- **Color Questions:** SmolVLM2 (75.0%) > Moondream2 (50.0%) > Others (25%)
- **Counting Questions:** Moondream2 (50.0%) > All others (0.0%)
- **Text Reading:** All models perform poorly (0% success rate)

---

## **Test Environment & Specifications**

### **Hardware Configuration**
- **Device:** MacBook Air M3
- **Memory:** 16GB RAM
- **MPS Available:** Yes
- **Torch Version:** 2.7.1
- **Python Version:** 3.13.3

### **Test Datasets**
- **VQA 2.0:** COCO val2014 (20 questions)
- **Context Understanding:** 3 test images with forensic-level prompts
- **Basic Performance:** 3 diverse test images

### **Evaluation Metrics**
- **VQA Accuracy:** VQA 2.0 standard scoring
- **Simple Accuracy:** Binary correct/incorrect
- **Inference Time:** Average response generation time
- **Load Time:** Model initialization time
- **Memory Usage:** RAM consumption difference

---

**Last Updated:** 2025-07-29 12:06:28  
**Test Environment:** MacBook Air M3 (16GB RAM, MPS available)  
**Unified Architecture:** SmolVLM GGUF via HTTP API with automatic server management  
**Comprehensive Testing:** VQA 2.0, Context Understanding, Performance Benchmarking