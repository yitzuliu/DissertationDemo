# VQA 2.0 Analysis Report

## 📊 **Executive Summary** (2025-07-29 13:12:58)

### 🏆 **Performance Rankings**
| Model                | Correct | Simple Accuracy | VQA Accuracy | Avg Time (s) | Status |
|----------------------|---------|-----------------|--------------|--------------|--------|
| **moondream2**       | 13/20   | **65.0%**       | **62.5%**    | 8.35         | 🥇 **Best Overall** |
| smolvlm_v2_instruct  | 11/20   | 55.0%           | 52.5%        | 8.41         | 🥈 **Balanced** |
| phi35_vision         | 7/20    | 35.0%           | 35.0%        | 5.29         | 🥉 **Fast** |
| smolvlm_instruct     | 7/20    | 35.0%           | 36.0%        | **0.39**     | ⚡ **Fastest** |
| llava_mlx            | 4/20    | 20.0%           | 21.0%        | 24.15        | ⚠️ **Issues** |

### **Key Insights**
- **moondream2** maintains the highest simple accuracy (65.0%) with stable performance
- **smolvlm_instruct** remains the fastest with 0.39s avg inference time
- **llava_mlx** continues to show severe performance issues with 24.15s avg inference
- **Performance consistency** observed across multiple test runs with minor variations
- **VQA accuracy decline** noted across all models compared to previous test run

---

## **🧪 Test Configuration**
- **Dataset:** VQA 2.0 COCO val2014 (20 questions)
- **Test Date:** July 29, 2025 13:12:58
- **Framework:** vqa2_enhanced_v1.2
- **Hardware:** MacBook Air M3 (16GB RAM, MPS available)
- **Generation Parameters:** max_new_tokens=100, do_sample=false

---

## **Detailed Model Performance Analysis**

### **moondream2** - 🥇 **Best Overall Performance**
- **Simple Accuracy:** 65.0% (13/20 correct)
- **VQA Accuracy:** 62.5%
- **Avg Inference Time:** 8.35s
- **Strengths:** Excellent at yes/no questions, object recognition, spatial reasoning
- **Notable Successes:** Zoo identification, Christmas hat, green jacket, red shoes, kite counting (3/3 correct), pedestrian right-of-way
- **Issues:** Text reading challenges ("Pull Zone" vs "PED XING"), some color perception (seahorse: "yellow and red" vs "yellow and orange", stripes: "pink" vs "white")

### **smolvlm_v2_instruct** - 🥈 **Balanced Performance**
- **Simple Accuracy:** 55.0% (11/20 correct)
- **VQA Accuracy:** 52.5%
- **Avg Inference Time:** 8.41s
- **Strengths:** Good at object identification, color recognition, detailed reasoning
- **Notable Successes:** Zoo identification, Christmas recognition, green jacket, red shoes, flag identification, white stripes
- **Issues:** Frequent uncertainty responses ("image does not provide information"), text reading challenges ("PED KING" vs "PED XING")

### **phi35_vision** - 🥉 **Fast Performance**
- **Simple Accuracy:** 35.0% (7/20 correct)
- **VQA Accuracy:** 35.0%
- **Avg Inference Time:** 5.29s
- **Strengths:** Detailed responses, good at specific object identification
- **Notable Successes:** Christmas identification, skier direction, pedestrian right-of-way, flag identification, green disk, red shoes
- **Issues:** Significant color perception problems, counting errors ("all kites have legs" vs 3), text reading difficulties ("FLOODING" vs "PED XING")

### **smolvlm_instruct** - ⚡ **Fastest Inference**
- **Simple Accuracy:** 35.0% (7/20 correct)
- **VQA Accuracy:** 36.0%
- **Avg Inference Time:** 0.39s (fastest by far)
- **Strengths:** Extremely fast inference, good at basic object recognition
- **Notable Successes:** Zoo identification, Christmas recognition, green jacket, pedestrian rights, flag identification, zebra behavior
- **Issues:** Color perception problems (white vs gray, black vs red/green), counting errors, text reading failures

### **llava_mlx** - ⚠️ **Significant Performance Issues**
- **Simple Accuracy:** 20.0% (4/20 correct)
- **VQA Accuracy:** 21.0%
- **Avg Inference Time:** 24.15s (slowest)
- **Critical Issues:** 
  - Extremely slow inference (24+ seconds)
  - Repetitive and verbose responses with self-questioning loops
  - Poor accuracy across all question types
  - Batch inference problems causing state corruption
- **Notable Failures:** Verbose repetitive responses ("Is it morning? Yes. Is it afternoon? No..." pattern), complete misidentification of objects

---

## **Question Type Analysis**

### **Yes/No Questions Performance**
| Model | Correct | Total | Accuracy |
|-------|---------|-------|----------|
| moondream2 | 7/9 | 9 | 77.8% |
| smolvlm_v2_instruct | 5/9 | 9 | 55.6% |
| phi35_vision | 4/9 | 9 | 44.4% |
| smolvlm_instruct | 4/9 | 9 | 44.4% |
| llava_mlx | 3/9 | 9 | 33.3% |

### **Color Questions Performance**
| Model | Correct | Total | Accuracy |
|-------|---------|-------|----------|
| moondream2 | 2/4 | 4 | 50.0% |
| smolvlm_v2_instruct | 3/4 | 4 | 75.0% |
| phi35_vision | 1/4 | 4 | 25.0% |
| smolvlm_instruct | 1/4 | 4 | 25.0% |
| llava_mlx | 1/4 | 4 | 25.0% |

### **Counting Questions Performance**
| Model | Correct | Total | Accuracy |
|-------|---------|-------|----------|
| moondream2 | 1/2 | 2 | 50.0% |
| smolvlm_v2_instruct | 0/2 | 2 | 0.0% |
| phi35_vision | 0/2 | 2 | 0.0% |
| smolvlm_instruct | 0/2 | 2 | 0.0% |
| llava_mlx | 0/2 | 2 | 0.0% |

---

## **Critical Issues Identified**

### **1. LLaVA-MLX Performance Crisis**
- **Inference Time:** 24.15s average (4-6x slower than others)
- **Accuracy:** Only 20.0% simple accuracy, 21.0% VQA accuracy
- **Response Quality:** Verbose, repetitive, often incorrect with self-questioning loops
- **Technical Issues:** Batch inference problems, state corruption, repetitive response patterns
- **Example Issue:** "Is it morning? Yes. Is it afternoon? No. Is it evening? No..." endless loops
- **Recommendation:** ❌ **Not suitable for production use**

### **2. Color Perception Challenges**
- All models struggle with accurate color identification
- Common errors: white vs. gray, blue vs. green, yellow vs. orange
- **Best performer:** smolvlm_v2_instruct (75.0% color accuracy)

### **3. Counting and Numerical Reasoning**
- All models perform poorly on counting tasks (0-50% accuracy)
- Specific challenge: "How many kites have legs?" - only moondream2 got correct answer (3)
- **Recommendation:** Avoid counting-dependent applications

### **4. Text Reading in Images**
- Universal challenge across all models
- Yellow sign reading: All models failed to read "PED XING" correctly
- Various incorrect interpretations: "FLOODING", "Caution: Children at Play", "PED KING", "Stop"

---

## **Performance Recommendations**

### **🥇 For Production VQA Applications**
**Use: moondream2**
- Highest accuracy (65.0%)
- Best VQA performance (62.5%)
- Reasonable inference time (8.35s)
- Most reliable for yes/no questions and object recognition

### **⚡ For Speed-Critical Applications**
**Use: smolvlm_instruct**
- Fastest inference (0.39s)
- Acceptable accuracy for basic tasks
- Good for real-time applications
- Trade-off: Lower accuracy for extreme speed

### **🎯 For Balanced Performance**
**Use: smolvlm_v2_instruct**
- Good accuracy (55.0%)
- Reasonable speed (8.41s)
- Best color perception
- Reliable for general-purpose VQA with detailed reasoning

### **🚫 Avoid for Production**
**Avoid: llava_mlx**
- Extremely slow (24.15s)
- Poor accuracy (20.0%)
- Technical issues with batch processing and repetitive response loops
- Not suitable for any production use case

---

## **Technical Specifications**

### **Hardware Configuration**
- **Device:** MacBook Air M3
- **Memory:** 16GB RAM
- **MPS Available:** Yes
- **Torch Version:** 2.7.1
- **Python Version:** 3.13.3

### **Test Parameters**
- **Max New Tokens:** 100
- **Sampling:** Disabled (do_sample=false)
- **Image Preprocessing:** Resize to max 1024px, LANCZOS
- **Unified Parameters:** Yes (consistent across all models)

### **Model Configurations**
- **phi35_vision:** mlx-community/Phi-3.5-vision-instruct-4bit
- **llava_mlx:** mlx-community/llava-v1.6-mistral-7b-4bit  
- **smolvlm_v2_instruct:** mlx-community/SmolVLM2-500M-Video-Instruct-mlx
- **smolvlm_instruct:** ggml-org/SmolVLM-500M-Instruct-GGUF
- **moondream2:** vikhyatk/moondream2

---

**Test Date:** 2025-07-29 13:12:58  
**Framework Version:** vqa2_enhanced_v1.2  
**Dataset:** VQA 2.0 COCO val2014 (20 questions)  
**Environment:** MacBook Air M3 (16GB RAM, MPS available)  
**Evaluation Method:** VQA 2.0 Standard with unified parameters  
**Performance Consistency:** Results show stable performance across multiple test runs with minor variations