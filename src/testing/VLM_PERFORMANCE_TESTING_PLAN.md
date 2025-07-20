# VLM Performance Testing Plan

## 📊 **Quick Summary** (2025-07-20)

### 🏆 **Performance Rankings**
| Rank | Model | Load Time | Inference | Vision | Text | Context | VQA Accuracy | Simple Accuracy | Status |
|------|-------|-----------|-----------|--------|------|---------|--------------|-----------------|--------|
| 🥇 | **SmolVLM2-500M-Video-MLX** | 0.38s | 4.23s | ✅ 100% | ✅ 100% | ❌ 10% | 51.5% | **60.0%** | ✅ **Best Overall** |
| 🥈 | **SmolVLM-500M-Instruct** | 3.37s | 6.09s | ✅ 100% | ✅ 100% | ⚠️ 33% | **52.5%** | 55.0% | ✅ **Best VQA** |
| 🥉 | **Moondream2** | 4.96s | 3.89s | ✅ 100% | ❌ 0% | ❌ 0% | 53.0% | **60.0%** | ✅ **Best Vision** |
| 4️⃣ | **Phi-3.5-Vision-Instruct-MLX** | 1.55s | 9.64s | ✅ 100% | ✅ 100% | ⚠️ 25% | 52.0% | 50.0% | ✅ **Balanced** |
| 5️⃣ | **LLaVA-v1.6-Mistral-7B-MLX** | 2.61s | 15.09s | ✅ 100% | ✅ 100% | ⚠️ 20% | 27.0% | 25.0% | ⚠️ **Slow** |

---

## **🎯 Testing Objectives**

### **Primary Goals**
1. **Performance Benchmarking:** Measure load time, inference speed, and memory usage
2. **Accuracy Evaluation:** Assess VQA and simple accuracy on COCO dataset
3. **Capability Testing:** Validate vision, text, and context understanding
4. **Framework Compatibility:** Test MLX vs Transformers performance
5. **Real-world Validation:** Use actual images and questions

### **Secondary Goals**
1. **Memory Efficiency:** Monitor RAM usage and cleanup effectiveness
2. **Error Handling:** Test timeout and error recovery mechanisms
3. **Consistency:** Verify reproducible results across multiple runs
4. **Scalability:** Assess performance with different image sizes and complexities

---

## **🧪 Testing Framework**

### **Test Environment**
- **Hardware:** MacBook Air M3 (16GB RAM)
- **OS:** macOS 14.5.0
- **Python:** 3.13.3
- **Frameworks:** PyTorch 2.7.1, MLX, Transformers
- **Virtual Environment:** ai_vision_env

### **Test Images**
1. **IMG_0119.JPG:** Shiba Inu dog on tiled floor (960x1707)
2. **IMG_2053.JPG:** Person holding passport (3088x2316)
3. **test_image.jpg:** Geometric diagram (336x336)

### **Test Prompts**
- **Vision:** "Describe what you see in this image in detail."
- **Text:** "What is the capital of France?", "Explain machine learning", "Write a poem about technology"
- **VQA:** 20 COCO val2014 questions with ground truth answers

---

## **📋 Test Categories**

### **1. Performance Testing** (`vlm_tester.py`)
- **Load Time Measurement:** Time to load model into memory
- **Inference Speed:** Average time per image/text prompt
- **Memory Usage:** RAM consumption before/after loading
- **Text-Only Capability:** Pure text processing without images

### **2. VQA Testing** (`vqa_test.py`)
- **COCO Dataset:** 20 questions from VQA 2.0 validation set
- **Accuracy Metrics:** Simple accuracy and VQA accuracy
- **Ground Truth:** Standard VQA 2.0 evaluation protocol
- **Performance Tracking:** Inference time per question

### **3. Context Understanding** (`vlm_context_tester.py`)
- **Conversation Flow:** Multi-turn dialogue testing
- **Context Retention:** Ability to reference previous descriptions
- **Forensic Testing:** Detailed image analysis with follow-up questions
- **Memory Assessment:** Conversation context preservation

---

## **🔧 Model Configurations**

### **SmolVLM2-500M-Video-Instruct-MLX**
```python
model_id = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"
framework = "MLX"
load_time = 0.38s
avg_inference = 4.23s
vqa_accuracy = 51.5%
simple_accuracy = 60.0%
context_accuracy = 10%
```

### **SmolVLM-500M-Instruct**
```python
model_id = "HuggingFaceTB/SmolVLM-500M-Instruct"
framework = "Transformers"
load_time = 3.37s
avg_inference = 6.09s
vqa_accuracy = 52.5%
simple_accuracy = 55.0%
context_accuracy = 33%
```

### **Moondream2**
```python
model_id = "vikhyatk/moondream2"
framework = "Transformers"
load_time = 4.96s
avg_inference = 3.89s
vqa_accuracy = 53.0%
simple_accuracy = 60.0%
context_accuracy = 0% (not supported)
```

### **LLaVA-v1.6-Mistral-7B-MLX**
```python
model_id = "mlx-community/llava-v1.6-mistral-7b-4bit"
framework = "MLX"
load_time = 2.61s
avg_inference = 15.09s
vqa_accuracy = 27.0%
simple_accuracy = 25.0%
context_accuracy = 20%
```

### **Phi-3.5-Vision-Instruct-MLX**
```python
model_id = "mlx-community/Phi-3.5-vision-instruct-4bit"
framework = "MLX"
load_time = 1.55s
avg_inference = 9.64s
vqa_accuracy = 52.0%
simple_accuracy = 50.0%
context_accuracy = 25%
```

---

## **📊 Detailed Results**

### **Performance Metrics Summary**
| Model | Load Time | Vision Inference | Text Inference | Memory Usage | Vision Success | Text Success |
|-------|-----------|------------------|----------------|--------------|----------------|--------------|
| **SmolVLM2-MLX** | 0.38s | 5.71s | 5.37s | 1.04GB | 3/3 | 3/3 |
| **SmolVLM** | 3.37s | 10.40s | 1.72s | 1.87GB | 3/3 | 3/3 |
| **Moondream2** | 4.96s | 6.47s | N/A | -1.74GB | 3/3 | 0/3 |
| **LLaVA-MLX** | 2.61s | 12.56s | 4.08s | 0.17GB | 3/3 | 3/3 |
| **Phi-3.5-MLX** | 1.55s | 12.44s | 5.30s | 0.29GB | 3/3 | 3/3 |

### **VQA 2.0 COCO Results (20 Questions)**
| Model | Correct Answers | Simple Accuracy | VQA Accuracy | Avg Time | Grade |
|-------|----------------|-----------------|--------------|----------|-------|
| **SmolVLM2-MLX** | 12/20 | **60.0%** | 51.5% | 4.23s | 🥇 **A** |
| **Moondream2** | 12/20 | **60.0%** | 53.0% | 3.89s | 🥈 **A** |
| **SmolVLM** | 11/20 | 55.0% | **52.5%** | 6.09s | 🥉 **B+** |
| **Phi-3.5-MLX** | 10/20 | 50.0% | 52.0% | 9.64s | **B** |
| **LLaVA-MLX** | 5/20 | 25.0% | 27.0% | 15.09s | **D** |

### **Context Understanding Results**
| Model | Success Rate | Context Accuracy | Avg Inference | Status |
|-------|--------------|------------------|---------------|--------|
| **SmolVLM** | 100% | **33%** | 6.09s | 🏆 **Best Context** |
| **Phi-3.5-MLX** | 100% | **25%** | 9.64s | 🥈 **Good Context** |
| **LLaVA-MLX** | 100% | **20%** | 15.09s | 🥉 **Limited Context** |
| **SmolVLM2-MLX** | 100% | **10%** | 4.23s | ❌ **Poor Context** |

---

## **🎯 Key Findings**

### **Performance Insights**
1. **Fastest Overall:** SmolVLM2-MLX (0.38s load, 4.23s inference)
2. **Best VQA:** SmolVLM (52.5% VQA accuracy)
3. **Best Vision:** Moondream2 (60.0% simple accuracy)
4. **Best Context:** SmolVLM (33% context accuracy)
5. **Slowest:** LLaVA-MLX (15.09s inference)

### **Framework Comparison**
- **MLX Models:** Faster loading, optimized for Apple Silicon
- **Transformers Models:** More reliable, better text support
- **Memory Efficiency:** Moondream2 shows memory optimization
- **State Issues:** LLaVA-MLX requires reloading between tests

### **Capability Analysis**
- **Vision Processing:** All models achieve 100% success rate
- **Text Processing:** Moondream2 cannot process text-only prompts
- **Context Understanding:** All models show significant limitations
- **VQA Performance:** Wide range from 27% to 53%

---

## **⚠️ Known Issues**

### **Technical Issues**
1. **LLaVA State Bugs:** Model state corruption requires reloading
2. **Moondream2 Text Limitation:** Cannot process text-only prompts
3. **Context Understanding:** Universal poor performance across all models
4. **Memory Management:** Some models show memory leaks

### **Performance Issues**
1. **LLaVA Slow Inference:** 15.09s average (3x slower than others)
2. **VQA Accuracy Gap:** 26% difference between best and worst
3. **Context Retention:** Maximum 33% accuracy (SmolVLM)

---

## **🔧 Testing Procedures**

### **Performance Testing**
```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Run performance tests
python vlm_tester.py

# Expected output: test_results_YYYYMMDD_HHMMSS.json
```

### **VQA Testing**
```bash
# Run VQA tests with COCO dataset
python vqa_test.py --mode coco --num_questions 20

# Expected output: vqa2_results_coco_YYYYMMDD_HHMMSS.json
```

### **Context Testing**
```bash
# Run context understanding tests
python vlm_context_tester.py

# Expected output: context_understanding_test_results_YYYYMMDD_HHMMSS.json
```

---

## **📈 Evaluation Metrics**

### **Performance Metrics**
- **Load Time:** Seconds to load model into memory
- **Inference Time:** Average seconds per image/text prompt
- **Memory Usage:** RAM consumption in GB
- **Success Rate:** Percentage of successful inferences

### **Accuracy Metrics**
- **Simple Accuracy:** Exact match with ground truth
- **VQA Accuracy:** Standard VQA 2.0 evaluation protocol
- **Context Accuracy:** Ability to reference previous descriptions

### **Quality Metrics**
- **Response Quality:** Relevance and coherence of responses
- **Error Rate:** Percentage of failed or timeout responses
- **Consistency:** Reproducibility across multiple runs

---

## **🎯 Recommendations**

### **For Production Use**
1. **SmolVLM2-MLX:** Best overall performance, fastest inference
2. **SmolVLM:** Best VQA accuracy, reliable text support
3. **Moondream2:** Best vision-only performance

### **For Development**
1. **Phi-3.5-MLX:** Balanced performance, good for experimentation
2. **LLaVA-MLX:** Large model, but has state issues

### **For Specific Use Cases**
- **VQA Tasks:** SmolVLM (52.5% VQA accuracy)
- **Speed Critical:** SmolVLM2-MLX (4.23s avg inference)
- **Vision-Only:** Moondream2 (60.0% simple accuracy)
- **Text + Vision:** SmolVLM2-MLX (100% text success rate)

---

## **🔄 Framework Integration**

### **VQA Framework**
- ✅ Unified evaluation metrics
- ✅ COCO dataset integration
- ✅ MLX subprocess handling
- ✅ Model reloading strategies

### **Performance Framework**
- ✅ Load time measurement
- ✅ Memory usage tracking
- ✅ Text-only capability testing
- ✅ Vision capability validation

### **Context Framework**
- ✅ Conversation flow testing
- ✅ Context retention evaluation
- ✅ Forensic-level detail testing

---

**Last Updated:** 2025-07-20  
**Test Environment:** MacBook Air M3 (16GB RAM)  
**Framework Version:** vqa2_enhanced_v1.2