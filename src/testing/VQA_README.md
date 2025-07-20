# VQA (Visual Question Answering) Testing Framework

## 📊 **Quick Summary** (2025-07-20)

### 🏆 **VQA 2.0 COCO Results (20 Questions)**
| Rank | Model | Correct | Simple Accuracy | VQA Accuracy | Avg Time | Status |
|------|-------|---------|-----------------|--------------|----------|--------|
| 🥇 | **SmolVLM2-MLX** | 12/20 | **60.0%** | 51.5% | 4.23s | ✅ **Best Overall** |
| 🥈 | **Moondream2** | 12/20 | **60.0%** | 53.0% | 3.89s | ✅ **Best Vision** |
| 🥉 | **SmolVLM** | 11/20 | 55.0% | **52.5%** | 6.09s | ✅ **Best VQA** |
| 4️⃣ | **Phi-3.5-MLX** | 10/20 | 50.0% | 52.0% | 9.64s | ✅ **Balanced** |
| 5️⃣ | **LLaVA-MLX** | 5/20 | 25.0% | 27.0% | 15.09s | ⚠️ **Poor** |

---

## **🎯 Overview**

The VQA (Visual Question Answering) testing framework evaluates Vision-Language Models (VLMs) using the standard VQA 2.0 evaluation protocol on the COCO dataset. This framework provides comprehensive accuracy assessment and performance benchmarking for VLM models.

### **Key Features**
- **Standard VQA 2.0 Evaluation:** Uses official COCO val2014 dataset
- **Multiple Accuracy Metrics:** Simple accuracy and VQA accuracy
- **Performance Tracking:** Inference time and memory usage
- **Model Comparison:** Side-by-side evaluation of different models
- **Detailed Results:** Question-level analysis with ground truth comparison

---

## **🔧 Installation & Setup**

### **Prerequisites**
```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Install required packages
pip install torch torchvision
pip install transformers pillow
pip install mlx-vlm  # For MLX models
```

### **Directory Structure**
```
src/testing/
├── vqa_test.py              # Main VQA testing script
├── vqa_framework.py         # Core VQA evaluation framework
├── testing_material/
│   ├── images/              # Test images
│   └── vqa2/                # VQA dataset
│       ├── images/          # COCO images
│       ├── questions.json   # VQA questions
│       └── annotations.json # Ground truth answers
└── results/                 # Test results output
```

---

## **🚀 Usage**

### **Quick Start**
```bash
# Run VQA test with all models (20 questions)
python vqa_test.py --mode coco --num_questions 20

# Run with specific model
python vqa_test.py --mode coco --model smolvlm_instruct --num_questions 20

# Run with sample data (for testing)
python vqa_test.py --mode sample --num_questions 10
```

### **Command Line Options**
```bash
python vqa_test.py [OPTIONS]

Options:
  --mode TEXT              Test mode: 'coco' or 'sample' [default: coco]
  --num_questions INTEGER  Number of questions to test [default: 20]
  --model TEXT             Specific model to test
  --verbose                Enable verbose output
  --help                   Show help message
```

### **Available Models**
- `smolvlm_instruct` - SmolVLM-500M-Instruct (Best VQA: 52.5%)
- `smolvlm_v2_instruct` - SmolVLM2-500M-Video-MLX (Best Overall: 60.0%)
- `moondream2` - Moondream2 (Best Vision: 60.0%)
- `llava_mlx` - LLaVA-v1.6-Mistral-7B-MLX (Poor: 27.0%)
- `phi35_vision` - Phi-3.5-Vision-Instruct-MLX (Balanced: 52.0%)

---

## **📊 Evaluation Metrics**

### **Simple Accuracy**
- **Definition:** Exact string match between model answer and ground truth
- **Calculation:** `correct_answers / total_questions`
- **Example:** Model answers "yes" for ground truth "yes" = 100% accuracy

### **VQA Accuracy**
- **Definition:** Standard VQA 2.0 evaluation protocol
- **Calculation:** Uses multiple acceptable answers and partial credit
- **Example:** Ground truth ["red", "red color"] accepts both answers

### **Performance Metrics**
- **Inference Time:** Average seconds per question
- **Memory Usage:** RAM consumption during testing
- **Success Rate:** Percentage of successful inferences

---

## **🔍 Detailed Results Analysis**

### **Model Performance Breakdown**

#### **1. SmolVLM2-500M-Video-MLX** 🥇 **Best Overall**
- **Simple Accuracy:** 60.0% (12/20 correct)
- **VQA Accuracy:** 51.5%
- **Avg Inference:** 4.23s (fastest)
- **Strengths:** Fastest inference, good overall accuracy
- **Weaknesses:** Lower VQA accuracy than some competitors

#### **2. Moondream2** 🥈 **Best Vision**
- **Simple Accuracy:** 60.0% (12/20 correct)
- **VQA Accuracy:** 53.0%
- **Avg Inference:** 3.89s
- **Strengths:** Best VQA accuracy, fast inference
- **Weaknesses:** No text-only capability

#### **3. SmolVLM-500M-Instruct** 🥉 **Best VQA**
- **Simple Accuracy:** 55.0% (11/20 correct)
- **VQA Accuracy:** 52.5% (best among all models)
- **Avg Inference:** 6.09s
- **Strengths:** Best VQA accuracy, reliable text support
- **Weaknesses:** Slower inference than MLX models

#### **4. Phi-3.5-Vision-Instruct-MLX** ✅ **Balanced**
- **Simple Accuracy:** 50.0% (10/20 correct)
- **VQA Accuracy:** 52.0%
- **Avg Inference:** 9.64s
- **Strengths:** Balanced performance, good MLX optimization
- **Weaknesses:** Slower inference, moderate accuracy

#### **5. LLaVA-v1.6-Mistral-7B-MLX** ⚠️ **Poor Performance**
- **Simple Accuracy:** 25.0% (5/20 correct)
- **VQA Accuracy:** 27.0%
- **Avg Inference:** 15.09s (slowest)
- **Strengths:** Large model capacity
- **Weaknesses:** Poor accuracy, slow inference, state issues

### **Question Type Analysis**

#### **Yes/No Questions (7 questions)**
- **Best:** SmolVLM2-MLX and Moondream2 (tied)
- **Performance:** Generally good across all models
- **Example:** "Is it daytime?" → Ground truth: "no"

#### **Color Questions (6 questions)**
- **Best:** SmolVLM2-MLX
- **Performance:** Variable, some models struggle with color accuracy
- **Example:** "What color is her dress?" → Ground truth: "gray"

#### **Count Questions (2 questions)**
- **Best:** Moondream2
- **Performance:** Challenging for all models
- **Example:** "How many kites have legs?" → Ground truth: "3"

#### **What Questions (3 questions)**
- **Best:** SmolVLM
- **Performance:** Good across most models
- **Example:** "What holiday is the dog's hat for?" → Ground truth: "christmas"

---

## **📁 Result Files**

### **Output Format**
```json
{
  "experiment_metadata": {
    "test_date": "2025-07-20 12:33:25",
    "test_mode": "coco",
    "num_questions": 20,
    "framework_version": "vqa2_enhanced_v1.2"
  },
  "results": {
    "model_name": {
      "model_id": "model_identifier",
      "total_questions": 20,
      "correct_answers": 12,
      "accuracy": 0.6,
      "vqa_accuracy": 0.515,
      "avg_inference_time": 4.23,
      "question_results": [...]
    }
  }
}
```

### **File Naming Convention**
- **COCO Tests:** `vqa2_results_coco_YYYYMMDD_HHMMSS.json`
- **Sample Tests:** `vqa2_results_sample_YYYYMMDD_HHMMSS.json`
- **Single Model:** `vqa2_results_[model]_YYYYMMDD_HHMMSS.json`

---

## **🔧 Framework Architecture**

### **Core Components**

#### **VQAFramework Class**
- **Data Loading:** COCO dataset and sample data management
- **Model Evaluation:** Unified evaluation across different models
- **Accuracy Calculation:** Simple and VQA accuracy computation
- **Result Management:** JSON output generation

#### **Model Integration**
- **Unified Interface:** Consistent API across different model types
- **MLX Support:** Subprocess handling for MLX-optimized models
- **Error Handling:** Timeout and error recovery mechanisms
- **Memory Management:** Efficient model loading and cleanup

### **Evaluation Process**
1. **Data Preparation:** Load questions and ground truth answers
2. **Model Loading:** Initialize model with appropriate framework
3. **Question Processing:** Generate answers for each question
4. **Accuracy Calculation:** Compare answers with ground truth
5. **Result Compilation:** Generate comprehensive JSON report

---

## **⚠️ Known Issues & Solutions**

### **LLaVA-MLX State Issues**
- **Problem:** Model state corruption after multiple inferences
- **Solution:** Model reloading between evaluations (implemented in framework)
- **Impact:** Slower testing but ensures accuracy

### **Moondream2 Text Limitation**
- **Problem:** Cannot process text-only prompts
- **Solution:** Vision-only testing (no text capability testing)
- **Impact:** Limited to image-based questions

### **Memory Management**
- **Problem:** Large models consume significant RAM
- **Solution:** Sequential testing with cleanup between models
- **Impact:** Slower overall testing but stable performance

---

## **🎯 Best Practices**

### **Model Selection**
- **VQA-Critical Tasks:** Use SmolVLM (52.5% VQA accuracy)
- **Speed-Critical Tasks:** Use SmolVLM2-MLX (4.23s avg inference)
- **Vision-Only Tasks:** Use Moondream2 (60.0% simple accuracy)
- **Avoid:** LLaVA-MLX for accuracy-critical applications

### **Testing Configuration**
- **Question Count:** 20 questions for reliable evaluation
- **Timeout Settings:** 60s for small models, 180s for large models
- **Memory Management:** Test one model at a time
- **Result Validation:** Always verify ground truth accuracy

### **Performance Optimization**
- **MLX Models:** Use for Apple Silicon optimization
- **Batch Processing:** Not supported (sequential processing required)
- **Caching:** Results cached in JSON format for analysis
- **Parallel Testing:** Not recommended due to memory constraints

---

## **📈 Performance Comparison**

### **Speed Rankings**
1. **SmolVLM2-MLX:** 4.23s avg inference
2. **Moondream2:** 3.89s avg inference
3. **SmolVLM:** 6.09s avg inference
4. **Phi-3.5-MLX:** 9.64s avg inference
5. **LLaVA-MLX:** 15.09s avg inference

### **Accuracy Rankings**
1. **SmolVLM:** 52.5% VQA accuracy
2. **Moondream2:** 53.0% VQA accuracy
3. **Phi-3.5-MLX:** 52.0% VQA accuracy
4. **SmolVLM2-MLX:** 51.5% VQA accuracy
5. **LLaVA-MLX:** 27.0% VQA accuracy

### **Overall Rankings**
1. **SmolVLM2-MLX:** Best overall (fast + accurate)
2. **Moondream2:** Best vision performance
3. **SmolVLM:** Best VQA accuracy
4. **Phi-3.5-MLX:** Balanced performance
5. **LLaVA-MLX:** Poor performance

---

## **🔄 Integration with Other Frameworks**

### **Performance Testing**
- **Compatible:** Works with `vlm_tester.py` for performance benchmarking
- **Data Sharing:** Uses same model configurations and test images
- **Result Correlation:** VQA accuracy correlates with overall model quality

### **Context Testing**
- **Independent:** VQA testing is separate from context understanding
- **Different Metrics:** VQA focuses on accuracy, context focuses on memory
- **Complementary:** Both provide different insights into model capabilities

---

## **📚 Additional Resources**

### **Documentation**
- **VQA 2.0 Paper:** [Visual Question Answering v2.0](https://arxiv.org/abs/1612.00837)
- **COCO Dataset:** [Common Objects in Context](https://cocodataset.org/)
- **Framework Code:** `vqa_framework.py` for detailed implementation

### **Related Files**
- **Model Configurations:** `src/config/model_configs/`
- **Test Results:** `src/testing/results/`
- **Performance Data:** `test_results_*.json`
- **Context Data:** `context_understanding_test_results_*.json`

---

**Last Updated:** 2025-07-20  
**Framework Version:** vqa2_enhanced_v1.2  
**Test Environment:** MacBook Air M3 (16GB RAM)
