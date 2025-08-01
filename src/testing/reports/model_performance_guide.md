# VLM Model Performance Guide

## 📊 **Quick Summary** (2025-08-01)

### **Comprehensive Performance Overview**
| Model | Vision | Pure Text | VQA Acc | Simple Acc | Avg Inference (s) | Load Time (s) | Memory Diff (GB) | Status |
|-------|--------|-----------|---------|------------|-------------------|---------------|------------------|--------|
| **Moondream2** | ✅ | ❌ | **62.5%** | **65.0%** | 7.80 | 5.99 | -0.52 | 🥇 **Best Overall** |
| SmolVLM2-500M-Video-Instruct | ✅ | ✅ | 57.5% | 60.0% | 6.45 | 0.69 | 1.03 | 🥈 **Balanced** |
| SmolVLM-500M-Instruct (GGUF) | ✅ | ✅ | 36.0% | 35.0% | **0.34** | 2.03 | 0.001 | ⚡ **Fastest** |
| Phi-3.5-Vision-Instruct | ✅ | ✅ | 35.0% | 35.0% | 8.71 | 4.16 | 2.58 | 🥉 **Detailed** |
| LLaVA-v1.6-Mistral-7B-MLX | ✅ | ✅ | 21.0% | 20.0% | 19.02 | 2.01 | -1.47 | ⚠️ **Critical Issues** |

---

## **Model Loading Methods & Performance Details**

### **🥇 Moondream2** - **Best Overall Performance**
```python
model_id = "vikhyatk/moondream2"
# Load time: 5.99s | Avg Inference: 7.80s | Memory Diff: -0.52GB
# VQA Accuracy: 62.5% | Simple Accuracy: 65.0%
# Features: Highest accuracy, excellent yes/no questions, vision-only
# Strengths: Object recognition, spatial reasoning, color identification, counting tasks
# Limitations: Cannot process text-only input, slower loading
# Enhanced Memory Management: Stable performance with periodic cleanup
```

### **🥈 SmolVLM2-500M-Video-Instruct** - **Balanced Performance**
```python
model_id = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"
# Load time: 0.69s | Avg Inference: 6.45s | Memory Diff: 1.03GB
# VQA Accuracy: 57.5% | Simple Accuracy: 60.0% - IMPROVED
# Features: Best balance of speed and accuracy, supports text-only
# Strengths: Color perception, object identification, fast loading, context understanding
# Context Issues: Provides generic responses without image context
# Enhanced Memory Management: Improved performance with better memory handling
```

### **⚡ SmolVLM-500M-Instruct (GGUF)** - **Fastest Inference**
```python
# Unified GGUF approach via HTTP API (Production Ready)
model_id = "ggml-org/SmolVLM-500M-Instruct-GGUF"
api_endpoint = "http://localhost:8080/v1/chat/completions"
# Load time: 2.03s | Avg Inference: 0.34s | Memory Diff: 0.001GB
# VQA Accuracy: 36.0% | Simple Accuracy: 35.0%
# Features: Extremely fast inference, automatic server management, unified API
# Strengths: Real-time applications, minimal memory usage, enhanced memory management
# Trade-offs: Lower accuracy for extreme speed
```

### **🥉 Phi-3.5-Vision-Instruct** - **Detailed with Enhanced Memory**
```python
model_id = "mlx-community/Phi-3.5-vision-instruct-4bit"
# Load time: 4.16s | Avg Inference: 8.71s | Memory Diff: 2.58GB
# VQA Accuracy: 35.0% | Simple Accuracy: 35.0%
# Features: Good VQA performance despite lower simple accuracy, enhanced MLX memory management
# Strengths: Detailed responses, spatial reasoning, stable memory performance
# Context Issues: Returns empty responses for text-only context questions
# Enhanced Memory Management: Periodic cleanup prevents memory errors
```

### **⚠️ LLaVA-v1.6-Mistral-7B-MLX** - **Critical Performance Issues**
```python
model_id = "mlx-community/llava-v1.6-mistral-7b-4bit"
# Load time: 2.01s | Avg Inference: 19.02s | Memory Diff: -1.47GB
# VQA Accuracy: 21.0% | Simple Accuracy: 20.0%
# Critical Issues: Very slow, poor accuracy, batch inference problems
# Problems: State corruption, repetitive responses, requires model reloading
# Enhanced Memory Management: Improved from 24.15s to 19.02s (21% improvement)
# Status: NOT RECOMMENDED for production use
```

---

## **🎯 Production Recommendations**

### **For High-Accuracy Applications**
**🥇 Use: Moondream2**
- Highest VQA accuracy (62.5%) and simple accuracy (65.0%)
- Excellent for yes/no questions and object recognition
- Best overall performance consistency
- Reasonable inference time (7.80s)
- Enhanced memory management ensures stability
- **Trade-off:** Vision-only, cannot process text-only input

### **For Real-Time Applications**
**⚡ Use: SmolVLM-500M-Instruct (GGUF)**
- Fastest inference (0.34s) - 20x faster than others
- Production-ready with unified API and automatic server management
- Minimal memory usage (0.001GB diff)
- Enhanced memory management for stability
- **Trade-off:** Lower accuracy (35.0% simple, 36.0% VQA)

### **For Balanced Performance**
**🥈 Use: SmolVLM2-500M-Video-Instruct**
- Good accuracy (60.0% simple, 57.5% VQA) - **IMPROVED**
- Reasonable speed (6.45s) - **IMPROVED**
- Best color perception among all models
- Supports both vision and text-only input
- Enhanced memory management for better performance
- **Good balance** of speed, accuracy, and features

### **For Development/Testing**
**🥉 Use: Phi-3.5-Vision-Instruct**
- Consistent VQA and simple accuracy (35.0% both)
- Fast loading (4.16s) with detailed responses
- Enhanced MLX memory management prevents errors
- **Trade-off:** Context understanding issues, slower inference (8.71s)

### **❌ Avoid for Production**
**⚠️ LLaVA-v1.6-Mistral-7B-MLX**
- Very slow (19.02s inference) - improved but still critical
- Poor accuracy (20.0% simple, 21.0% VQA)
- Critical batch inference issues with repetitive response loops
- Requires model reloading between images
- Enhanced memory management helps but doesn't solve core issues
- **Not suitable for any production use case**

---

## **🚨 Critical Issues & Limitations**

### **Context Understanding Crisis**
**⚠️ ALL MODELS HAVE 0% TRUE CONTEXT UNDERSTANDING**
- **Phi-3.5:** Returns empty responses to context questions
- **LLaVA-MLX:** Provides hallucinated responses (claims "white and black" for all images)
- **Moondream2:** Explicitly states cannot answer without image
- **SmolVLM models:** Provide hallucinated responses (claim "red, white, blue" for all images)
- **Implication:** Multi-turn conversations require external memory systems

### **LLaVA-MLX Specific Issues (Improved but Still Critical)**
- **Batch Processing:** Model state corruption after first inference
- **Performance:** 5x slower than other models (19.02s vs ~6-8s)
- **Accuracy:** Lowest performance across all metrics
- **Responses:** Verbose, repetitive, often incorrect
- **Technical Error:** "input operand has more dimensions than allowed by the axis remapping"
- **Enhanced Memory Management:** Improved inference time from 24.15s to 19.02s (21% improvement)
- **Workaround:** Model reloading required for each image (implemented)

### **Universal Challenges**
- **Text Reading:** All models struggle with text in images (0% success on "PED XING" sign)
- **Counting Tasks:** Poor performance across all models (0-50% accuracy)
- **Color Perception:** Frequent errors (white vs. gray, blue vs. green)
- **Context Retention:** No model can maintain conversation context

---

## **Enhanced Memory Management Results**

### **✅ Successfully Implemented Features**
- **Periodic Memory Cleanup:** Every 5 questions for MLX models
- **Adaptive Memory Pressure Detection:** Aggressive cleanup when memory usage >80%
- **MLX-Specific Memory Clearing:** `clear_mlx_memory()` function with Metal GPU cache clearing
- **Memory Monitoring:** Real-time memory pressure detection and response

### **Performance Improvements**
- **LLaVA-MLX:** Inference time improved from 24.15s to 19.02s (21% improvement)
- **Phi-3.5-Vision:** Stable performance with enhanced memory management
- **SmolVLM2:** Improved accuracy and speed with better memory handling
- **SmolVLM GGUF:** Improved speed from 0.39s to 0.34s
- **No Memory Errors:** Successfully prevented `[METAL] Command buffer execution failed: Insufficient Memory` errors

---

## **Performance Rankings** (Updated 2025-08-01)

### **🏆 Overall Performance Rankings**
1. **🥇 Moondream2:** 65.0% simple, 62.5% VQA, 7.80s inference
2. **🥈 SmolVLM2-MLX:** 60.0% simple, 57.5% VQA, 6.45s inference - **IMPROVED**
3. **🥉 Phi-3.5-MLX:** 35.0% simple, 35.0% VQA, 8.71s inference
4. **⚡ SmolVLM GGUF:** 35.0% simple, 36.0% VQA, 0.34s inference - **IMPROVED**
5. **⚠️ LLaVA-MLX:** 20.0% simple, 21.0% VQA, 19.02s inference - **IMPROVED**

### **⚡ Speed Rankings**
1. **SmolVLM GGUF:** 0.34s (fastest by 20x) - **IMPROVED**
2. **Moondream2:** 7.80s - **IMPROVED**
3. **SmolVLM2-MLX:** 6.45s - **IMPROVED**
4. **Phi-3.5-MLX:** 8.71s
5. **LLaVA-MLX:** 19.02s (critical performance issue) - **IMPROVED**

### **🎯 Accuracy Rankings**
1. **Moondream2:** 62.5% VQA accuracy, 65.0% simple accuracy
2. **SmolVLM2-MLX:** 57.5% VQA accuracy, 60.0% simple accuracy - **IMPROVED**
3. **SmolVLM GGUF:** 36.0% VQA accuracy, 35.0% simple accuracy
4. **Phi-3.5-MLX:** 35.0% VQA accuracy, 35.0% simple accuracy
5. **LLaVA-MLX:** 21.0% VQA accuracy, 20.0% simple accuracy

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

**Last Updated:** 2025-08-01 19:48:55  
**Test Environment:** MacBook Air M3 (16GB RAM, MPS available)  
**Unified Architecture:** SmolVLM GGUF via HTTP API with automatic server management  
**Enhanced Features:** MLX memory management, periodic cleanup, adaptive pressure detection  
**Comprehensive Testing:** VQA 2.0, Context Understanding, Performance Benchmarking