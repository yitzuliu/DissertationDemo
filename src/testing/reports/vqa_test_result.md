# VQA 2.0 Test Results Analysis

## 📊 **Executive Summary** (2025-07-22)

### 🏆 **Performance Rankings**
| Model | Correct | Simple Accuracy | VQA Accuracy | Avg Time (s) |
|-------|---------|-----------------|--------------|--------------|
| smolvlm_v2_instruct | 12/20 | 60.0% | 51.5% | 5.67 |
| moondream2 | 13/20 | 65.0% | 57.5% | 5.42 |
| smolvlm_instruct | 11/20 | 55.0% | 52.5% | 6.12 |
| phi35_vision | 10/20 | 50.0% | 52.0% | 13.23 |
| llava_mlx | 5/20 | 25.0% | 27.0% | 23.19 |

### **Key Insights**
- **Best Overall:** moondream2 (highest simple and VQA accuracy)
- **Best VQA:** smolvlm_instruct (52.5% VQA accuracy)
- **Best Vision:** moondream2 (65.0% simple accuracy)
- **Worst Performance:** llava_mlx (25.0% simple accuracy, slowest)

---

## **🧪 Test Configuration**
- **Dataset:** VQA 2.0 COCO val2014 (20 questions)
- **Test Date:** July 22, 2025 10:46:54
- **Framework:** vqa2_enhanced_v1.2
- **Hardware:** MacBook Air M3 (16GB RAM)

---

## **Detailed Results**

### **Per-Model Performance**
| Model | Correct | Simple Accuracy | VQA Accuracy | Avg Inference (s) |
|-------|---------|-----------------|--------------|-------------------|
| smolvlm_v2_instruct | 12/20 | 60.0% | 51.5% | 5.67 |
| moondream2 | 13/20 | 65.0% | 57.5% | 5.42 |
| smolvlm_instruct | 11/20 | 55.0% | 52.5% | 6.12 |
| phi35_vision | 10/20 | 50.0% | 52.0% | 13.23 |
| llava_mlx | 5/20 | 25.0% | 27.0% | 23.19 |

### **Per-Question-Type Breakdown**
- (See JSON for detailed per-question results. For brevity, only summary is shown here.)
- **Yes/No:** All models perform best on yes/no questions.
- **Color:** Moderate performance, with moondream2 and smolvlm_v2_instruct leading.
- **Count:** moondream2 and phi35_vision excel at count questions.
- **What:** smolvlm_instruct and moondream2 perform best.

---

## **Key Findings**
- moondream2 achieves the highest overall accuracy and VQA accuracy.
- smolvlm_instruct is the best for VQA-specific tasks.
- llava_mlx is the slowest and least accurate.
- All models show room for improvement, especially on color and count questions.

## **Recommendations**
- For production VQA, use moondream2 or smolvlm_instruct.
- For speed, moondream2 is fastest among top performers.
- For research, phi35_vision offers balanced performance but is slower.
- Avoid llava_mlx for latency-sensitive or high-accuracy tasks.

---

**Test Date:** 2025-07-22 10:46:54  
**Framework Version:** vqa2_enhanced_v1.2  
**Dataset:** VQA 2.0 COCO val2014 (20 questions)  
**Environment:** MacBook Air M3 (16GB RAM)
