# VLM Model Performance Guide

## 📊 **Quick Summary** (2025-07-29)

### **Comprehensive Performance Overview**
| Model | Vision | Pure Text | VQA Acc | Simple Acc | Avg Inference (s) | Load Time (s) | Memory Diff (GB) | Status |
|-------|--------|-----------|---------|------------|-------------------|---------------|------------------|--------|
| **Moondream2** | ✅ | ❌ | **62.5%** | **65.0%** | 8.35 | 16.61 | -0.09 | 🥇 **Best Overall** |
| SmolVLM2-500M-Video-Instruct | ✅ | ✅ | 52.5% | 55.0% | 8.41 | 1.48 | 0.13 | 🥈 **Balanced** |
| SmolVLM-500M-Instruct (GGUF) | ✅ | ✅ | 36.0% | 35.0% | **0.39** | 4.05 | 0.001 | ⚡ **Fastest** |
| Phi-3.5-Vision-Instruct | ✅ | ✅ | 35.0% | 35.0% | 5.29 | 1.71 | 0.05 | 🥉 **Fast** |
| LLaVA-v1.6-Mistral-7B-MLX | ✅ | ✅ | 21.0% | 20.0% | 24.15 | 6.07 | -0.48 | ⚠️ **Critical Issues** |

---

## **Model Loading Methods & Performance Details**

### **🥇 Moondream2** - **Best Overall Performance**
```python
model_id = "vikhyatk/moondream2"
# Load time: 16.61s | Avg Inference: 8.35s | Memory Diff: -0.09GB
# VQA Accuracy: 62.5% | Simple Accuracy: 65.0%
# Features: Highest accuracy, excellent yes/no questions, vision-only
# Strengths: Object recognition, spatial reasoning, color identification
# Limitations: Cannot process text-only input, slower loading
```

### **🥈 SmolVLM2-500M-Video-Instruct** - **Balanced Performance**
```python
model_id = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"
# Load time: 1.48s | Avg Inference: 8.41s | Memory Diff: 0.13GB
# VQA Accuracy: 52.5% | Simple Accuracy: 55.0%
# Features: Best balance of speed and accuracy, supports text-only
# Strengths: Color perception, object identification, fast loading
# Context Issues: Provides generic responses without image context
```

### **⚡ SmolVLM-500M-Instruct (GGUF)** - **Fastest Inference**
```python
# Unified GGUF approach via HTTP API (Production Ready)
model_id = "ggml-org/SmolVLM-500M-Instruct-GGUF"
api_endpoint = "http://localhost:8080/v1/chat/completions"
# Load time: 4.05s | Avg Inference: 0.39s | Memory Diff: 0.001GB
# VQA Accuracy: 36.0% | Simple Accuracy: 35.0%
# Features: Extremely fast inference, automatic server management, unified API
# Strengths: Real-time applications, minimal memory usage
# Trade-offs: Lower accuracy for extreme speed
```

### **🥉 Phi-3.5-Vision-Instruct** - **Fast with Good VQA**
```python
model_id = "mlx-community/Phi-3.5-vision-instruct-4bit"
# Load time: 1.71s | Avg Inference: 5.29s | Memory Diff: 0.05GB
# VQA Accuracy: 35.0% | Simple Accuracy: 35.0%
# Features: Good VQA performance despite lower simple accuracy
# Strengths: Detailed responses, spatial reasoning
# Context Issues: Returns empty responses for text-only context questions
```

### **⚠️ LLaVA-v1.6-Mistral-7B-MLX** - **Critical Performance Issues**
```python
model_id = "mlx-community/llava-v1.6-mistral-7b-4bit"
# Load time: 6.07s | Avg Inference: 24.15s | Memory Diff: -0.48GB
# VQA Accuracy: 21.0% | Simple Accuracy: 20.0%
# Critical Issues: Extremely slow, poor accuracy, batch inference problems
# Problems: State corruption, repetitive responses, requires model reloading
# Status: NOT RECOMMENDED for production use
```

---

## **🎯 Production Recommendations**

### **For High-Accuracy VQA Applications**
**🥇 Use: Moondream2**
- Highest VQA accuracy (62.5%) and simple accuracy (65.0%)
- Excellent for yes/no questions and object recognition
- Best overall performance consistency
- Reasonable inference time (8.35s)
- **Trade-off:** Vision-only, cannot process text-only input

### **For Real-Time Applications**
**⚡ Use: SmolVLM-500M-Instruct (GGUF)**
- Fastest inference (0.39s) - 20x faster than others
- Production-ready with unified API and automatic server management
- Minimal memory usage (0.001GB diff)
- **Trade-off:** Lower accuracy (35.0% simple, 36.0% VQA)

### **For Balanced Performance**
**🥈 Use: SmolVLM2-500M-Video-Instruct**
- Good accuracy (55.0% simple, 52.5% VQA)
- Reasonable speed (8.41s)
- Best color perception among all models
- Supports both vision and text-only input
- **Good balance** of speed, accuracy, and features

### **For Development/Testing**
**🥉 Use: Phi-3.5-Vision-Instruct**
- Consistent VQA and simple accuracy (35.0% both)
- Fast inference (5.29s) and loading (1.71s)
- Detailed responses for analysis
- **Trade-off:** Context understanding issues

### **❌ Avoid for Production**
**⚠️ LLaVA-v1.6-Mistral-7B-MLX**
- Extremely slow (24.15s inference)
- Poor accuracy (20.0% simple, 21.0% VQA)
- Critical batch inference issues with repetitive response loops
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
- **Performance:** 5x slower than other models (24.15s vs ~5-6s)
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
- ✅ **Speed Optimization**: SmolVLM GGUF achieves 0.39s inference time

## **Performance Rankings** (Updated 2025-07-29)

### **🏆 Overall Performance Rankings**
1. **🥇 Moondream2:** 65.0% simple, 62.5% VQA, 8.35s inference
2. **🥈 SmolVLM2-MLX:** 55.0% simple, 52.5% VQA, 8.41s inference  
3. **🥉 Phi-3.5-MLX:** 35.0% simple, 35.0% VQA, 5.29s inference
4. **⚡ SmolVLM GGUF:** 35.0% simple, 36.0% VQA, 0.39s inference
5. **⚠️ LLaVA-MLX:** 20.0% simple, 21.0% VQA, 24.15s inference

### **⚡ Speed Rankings**
1. **SmolVLM GGUF:** 0.39s (fastest by 20x)
2. **Phi-3.5-MLX:** 5.29s
3. **Moondream2:** 8.35s
4. **SmolVLM2-MLX:** 8.41s
5. **LLaVA-MLX:** 24.15s (critical performance issue)

### **🎯 Accuracy Rankings (VQA 2.0)**
1. **Moondream2:** 62.5% VQA accuracy
2. **SmolVLM2-MLX:** 52.5% VQA accuracy
3. **SmolVLM GGUF:** 36.0% VQA accuracy
4. **Phi-3.5-MLX:** 35.0% VQA accuracy
5. **LLaVA-MLX:** 21.0% VQA accuracy

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

**Last Updated:** 2025-07-29 13:12:58  
**Test Environment:** MacBook Air M3 (16GB RAM, MPS available)  
**Unified Architecture:** SmolVLM GGUF via HTTP API with automatic server management  
**Comprehensive Testing:** VQA 2.0, Context Understanding, Performance Benchmarking