# VQA 2.0 Test Results Analysis

## 📊 **Executive Summary** (2025-07-28 21:48:39)

### 🏆 **Performance Rankings**
| Model                | Correct | Simple Accuracy | VQA Accuracy | Avg Time (s) |
|----------------------|---------|-----------------|--------------|--------------|
| **moondream2**       | 12/20   | **60.0%**       | **52.5%**    | 7.16         |
| smolvlm_v2_instruct  | 12/20   | 60.0%           | 51.5%        | 5.48         |
| smolvlm_instruct     | 8/20    | 40.0%           | 39.5%        | **1.17**     |
| phi35_vision         | 8/20    | 40.0%           | 42.5%        | 6.86         |
| llava_mlx            | 5/20    | 25.0%           | 27.0%        | 9.79         |

### **Key Insights**
- **moondream2** achieves the highest overall accuracy (60.0%)
- **smolvlm_instruct** is the fastest with 1.17s avg inference
- **llava_mlx** continues to show poor performance with batch inference issues
- **phi35_vision** shows reduced performance compared to previous tests
- All models show room for improvement, especially on complex reasoning questions

---

## **🧪 Test Configuration**
- **Dataset:** VQA 2.0 COCO val2014 (20 questions)
- **Test Date:** July 28, 2025 21:48:39
- **Framework:** vqa2_enhanced_v1.2
- **Hardware:** MacBook Air M3 (16GB RAM)

---

## **Detailed Results**

### **Per-Model Performance**
| Model                | Correct | Simple Accuracy | VQA Accuracy | Avg Inference (s) |
|----------------------|---------|-----------------|--------------|-------------------|
| **moondream2**       | 12/20   | **60.0%**       | **52.5%**    | 7.16              |
| smolvlm_v2_instruct  | 12/20   | 60.0%           | 51.5%        | 5.48              |
| smolvlm_instruct     | 8/20    | 40.0%           | 39.5%        | **1.17**          |
| phi35_vision         | 8/20    | 40.0%           | 42.5%        | 6.86              |
| llava_mlx            | 5/20    | 25.0%           | 27.0%        | 9.79              |

### **Per-Question-Type Breakdown**
- **Yes/No Questions:** moondream2 excels with excellent performance
- **Color Questions:** moondream2 and smolvlm_v2_instruct lead
- **Count Questions:** moondream2 shows best performance
- **What Questions:** smolvlm_instruct and moondream2 perform best

---

## **Key Findings**
- **moondream2** achieves the highest overall accuracy (60.0%)
- **smolvlm_instruct** is the fastest with 1.17s avg inference
- **llava_mlx** continues to show poor performance with batch inference issues
- **phi35_vision** shows reduced performance compared to previous tests
- All models show room for improvement, especially on complex reasoning questions

## **Recommendations**
- **For production VQA:** Use moondream2 for best overall performance
- **For speed-critical applications:** Use smolvlm_instruct (fastest inference)
- **For VQA-specific tasks:** Use moondream2 for highest VQA accuracy
- **For research and development:** Use smolvlm_v2_instruct for balanced performance
- **Avoid:** llava_mlx for latency-sensitive or high-accuracy tasks

---

**Test Date:** 2025-07-28 21:48:39  
**Framework Version:** vqa2_enhanced_v1.2  
**Dataset:** VQA 2.0 COCO val2014 (20 questions)  
**Environment:** MacBook Air M3 (16GB RAM)
