# VQA (Visual Question Answering) Testing Framework

*Last Updated: August 1, 2025 - Enhanced Memory Management & Results Saving*

## 📊 **Quick Summary** (Latest Results)

### 🏆 **VQA 2.0 COCO Results (20 Questions)**
| Rank | Model | Correct | Simple Accuracy | VQA Accuracy | Avg Time | Status |
|------|-------|---------|-----------------|--------------|----------|--------|
| 🥇 | **Moondream2** | 13/20 | **65.0%** | **62.5%** | 8.35s | ✅ **Best Overall** |
| 🥈 | **SmolVLM2-Instruct** | 11/20 | **55.0%** | 52.5% | 8.41s | ✅ **Fast & Accurate** |
| 🥉 | **Phi-3.5-Vision** | 7/20 | 35.0% | 35.0% | 5.29s | ✅ **Balanced** |
| 4️⃣ | **SmolVLM-Instruct** | 7/20 | 35.0% | 36.0% | 🏆 **0.39s** | ✅ **Fastest** |
| 5️⃣ | **LLaVA-MLX** | 4/20 | 20.0% | 21.0% | 24.15s | ⚠️ **Poor** |

---

## **🎯 Overview**

The VQA (Visual Question Answering) testing framework evaluates Vision-Language Models (VLMs) using the standard VQA 2.0 evaluation protocol on the COCO dataset. This framework provides comprehensive accuracy assessment and performance benchmarking for VLM models with enhanced evaluation logic.

### **Key Features**
- **Standard VQA 2.0 Evaluation:** Uses official COCO val2014 dataset
- **Enhanced Accuracy Metrics:** Simple accuracy and improved VQA accuracy with partial scoring
- **Performance Tracking:** Inference time and memory usage monitoring
- **Model Comparison:** Side-by-side evaluation of different models
- **Detailed Results:** Question-level analysis with ground truth comparison
- **Question Type Analysis:** Categorized evaluation by question types

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
├── vqa/
│   ├── vqa_test.py              # Main VQA testing script
│   ├── vqa_framework.py         # Core VQA evaluation framework
│   ├── test_results_saving.py   # Results saving verification script
│   ├── test_enhanced_memory.py  # Enhanced memory management test
│   ├── ENHANCED_MEMORY_MANAGEMENT.md  # Memory management documentation
│   ├── RESULTS_SAVING_UPDATE.md # Results saving documentation
│   ├── __init__.py              # Python package marker
│   └── README.md                # This documentation
├── materials/
│   ├── vqa2/
│   │   ├── images/              # COCO images
│   │   ├── questions.json       # VQA questions
│   │   └── annotations.json     # Ground truth answers
│   └── images/                  # (other test images, if any)
├── results/                     # Test results output (json)
│   ├── vqa2_results_coco_*.json # Complete test results
│   └── vqa2_results_single_*.json # Single model test results
├── reports/                     # Human-written reports/analysis
└── ...
```

---

## **🚀 Usage**

### **Quick Start**
```bash
# Run VQA test with all models (20 questions)
python vqa_test.py --questions 20

# Run with specific model
python vqa_test.py --questions 20 --models phi35_vision

# Run with multiple specific models
python vqa_test.py --questions 20 --models phi35_vision moondream2

# Run with verbose output
python vqa_test.py --questions 20 --models phi35_vision --verbose
```

### **Command Line Options**
```bash
python vqa_test.py [OPTIONS]

Options:
  --questions INTEGER      Number of test questions (default: 20, max 20)
  --models TEXT [TEXT ...] Models to test (choices: phi35_vision, llava_mlx, 
                          smolvlm_v2_instruct, smolvlm_instruct, moondream2)
  --verbose               Show detailed output
  --save-results          Save test results (default: True)
  --help                  Show help message
```

### **Available Models**
- `moondream2` - Moondream2 (Best Overall: 65.0%)
- `smolvlm_v2_instruct` - SmolVLM2-500M-Video-Instruct (Fast & Accurate: 55.0%)
- `smolvlm_instruct` - SmolVLM-500M-Instruct (Fastest: 0.39s)
- `phi35_vision` - Phi-3.5-Vision-Instruct (Balanced: 35.0%)
- `llava_mlx` - LLaVA-v1.6-Mistral-7B-MLX (Poor: 20.0%)

---

## **📊 Evaluation Metrics & Logic**

### **Simple Accuracy**
- **Definition:** Exact string match between model answer and ground truth
- **Calculation:** `correct_answers / total_questions`
- **Example:** Model answers "yes" for ground truth "yes" = 100% accuracy

### **Enhanced VQA Accuracy Logic**

#### **Yes/No Questions**
For yes/no questions, the framework uses a sophisticated scoring system:

```python
# Yes/No Keywords Detection
yes_keywords = ['yes', 'yeah', 'yep', 'correct', 'true', 'right', 'sure', 'okay']
no_keywords = ['no', 'nope', 'not', 'false', 'wrong', 'incorrect', 'negative']

# Scoring Logic
if gt_yes and model_yes and not model_no:
    return 1.0  # Correct yes answer
elif gt_no and model_no and not model_yes:
    return 1.0  # Correct no answer
elif gt_yes and model_no and not model_yes:
    return 0.0  # Wrong no answer (should be yes)
elif gt_no and model_yes and not model_no:
    return 0.0  # Wrong yes answer (should be no)
else:
    # Ambiguous responses get partial credit
    if model_yes and model_no:
        return 0.1  # Both yes/no keywords present
    elif not model_yes and not model_no:
        return 0.2  # No clear yes/no keywords
    else:
        return 0.3  # Some indication but unclear
```

#### **Non-Yes/No Questions**
For other question types, the framework uses a hierarchical matching system:

```python
# 1. Exact match (highest score)
if gt_answer_lower == prediction_lower:
    return 1.0

# 2. Word-level matching (high score)
gt_words = set(gt_answer_lower.split())
pred_words = set(prediction_lower.split())
common_words = gt_words.intersection(pred_words)
word_overlap = len(common_words) / len(gt_words)

if word_overlap >= 1.0:
    return 0.9  # All ground truth words present
elif word_overlap >= 0.7:
    return 0.7  # Most ground truth words present
elif word_overlap >= 0.3:
    return 0.3  # Some ground truth words present

# 3. Substring matching (lower score)
if gt_answer_lower in prediction_lower:
    return 0.5

# 4. No match
return 0.0
```

#### **Answer Preprocessing**
All answers undergo comprehensive preprocessing:

```python
def _preprocess_answer(self, answer: str) -> str:
    # Convert to lowercase
    answer = answer.lower().strip()
    
    # Remove all punctuation marks
    answer = re.sub(r'[^\w\s]', ' ', answer)
    
    # Handle contractions
    answer = answer.replace("'t", " not")
    answer = answer.replace("'re", " are")
    answer = answer.replace("'s", " is")
    answer = answer.replace("'ve", " have")
    answer = answer.replace("'ll", " will")
    answer = answer.replace("'d", " would")
    answer = answer.replace("n't", " not")
    answer = answer.replace("i'm", "i am")
    answer = answer.replace("it's", "it is")
    answer = answer.replace("don't", "do not")
    answer = answer.replace("can't", "cannot")
    answer = answer.replace("won't", "will not")
    
    # Number normalization
    number_mapping = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
        'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
        'eighteen': '18', 'nineteen': '19', 'twenty': '20'
    }
    
    for word, digit in number_mapping.items():
        answer = re.sub(r'\b' + word + r'\b', digit, answer)
    
    return answer
```

### **Performance Metrics**
- **Inference Time:** Average seconds per question
- **Memory Usage:** RAM consumption during testing
- **Success Rate:** Percentage of successful inferences

---

## **🔍 Detailed Results Analysis**

### **Comprehensive Model Performance Table**

| Model | Total Questions | Correct Answers | Simple Accuracy | VQA Accuracy | Avg Inference Time | Performance Grade |
|-------|-----------------|-----------------|-----------------|--------------|-------------------|-------------------|
| **Moondream2** | 20 | 13 | 65.0% | 62.5% | 8.35s | 🥇 **Best Overall** |
| **SmolVLM2-Instruct** | 20 | 11 | 55.0% | 52.5% | 8.41s | 🥈 **Fast & Accurate** |
| **Phi-3.5-Vision** | 20 | 7 | 35.0% | 35.0% | 5.29s | 🥉 **Balanced** |
| **SmolVLM-Instruct** | 20 | 7 | 35.0% | 36.0% | 0.39s | 🏆 **Fastest** |
| **LLaVA-MLX** | 20 | 4 | 20.0% | 21.0% | 24.15s | ⚠️ **Poor** |

### **Question Type Analysis**

#### **Yes/No Questions (7 questions)**

| Question ID | Question | Ground Truth | Phi-3.5 | LLaVA-MLX | SmolVLM2 | SmolVLM | Moondream2 |
|-------------|----------|--------------|---------|-----------|----------|----------|------------|
| 100187002 | Is it daytime? | no | ✅ | ❌ | ❌ | ❌ | ❌ |
| 278161005 | Is there another bus behind this one? | no | ❌ | ✅ | ❌ | ❌ | ✅ |
| 134483004 | Is the light on? | yes | ❌ | ✅ | ❌ | ❌ | ❌ |
| 117869005 | Is this a zoo? | yes | ❌ | ❌ | ✅ | ✅ | ✅ |
| 248767004 | Do pedestrians have the right of way? | yes | ✅ | ❌ | ❌ | ✅ | ✅ |
| 223174004 | Is the zebra grazing? | no | ❌ | ❌ | ✅ | ✅ | ✅ |
| 4396000 | Is the bear wearing shoes? | no | ❌ | ✅ | ✅ | ✅ | ✅ |

**Analysis:** Yes/No questions show variable performance across models. Moondream2 performs best with 5/7 correct answers, while Phi-3.5-Vision and LLaVA-MLX each get 2/7 correct.

#### **Color Questions (6 questions)**

| Question ID | Question | Ground Truth | Phi-3.5 | LLaVA-MLX | SmolVLM2 | SmolVLM | Moondream2 |
|-------------|----------|--------------|---------|-----------|----------|----------|------------|
| 32364003 | What color is her dress? | gray | ❌ | ❌ | ❌ | ❌ | ❌ |
| 413522004 | What color jacket is the person wearing? | green | ❌ | ❌ | ✅ | ✅ | ✅ |
| 248069002 | What color shoes is the girl wearing? | red | ✅ | ❌ | ✅ | ❌ | ✅ |
| 346214001 | What color is the seahorse? | yellow and orange | ❌ | ❌ | ✅ | ❌ | ❌ |
| 455506003 | What color is the disk? | green | ✅ | ❌ | ✅ | ❌ | ✅ |
| 376667002 | What color are the stripes? | white | ❌ | ✅ | ✅ | ❌ | ❌ |

**Analysis:** Color recognition is challenging for all models. SmolVLM2-Instruct performs best with 4/6 correct answers, followed by Moondream2 with 3/6 correct answers.

#### **Count Questions (2 questions)**

| Question ID | Question | Ground Truth | Phi-3.5 | LLaVA-MLX | SmolVLM2 | SmolVLM | Moondream2 |
|-------------|----------|--------------|---------|-----------|----------|----------|------------|
| 297944003 | How many shrubs are in the yard? | 0 | ❌ | ❌ | ❌ | ❌ | ❌ |
| 499727001 | How many kites have legs? | 3 | ❌ | ❌ | ❌ | ❌ | ✅ |

**Analysis:** Counting questions are particularly challenging. Only Moondream2 correctly answered 1/2 questions, while all other models failed on both.

#### **Other Questions (5 questions)**

| Question ID | Question | Ground Truth | Phi-3.5 | LLaVA-MLX | SmolVLM2 | SmolVLM | Moondream2 |
|-------------|----------|--------------|---------|-----------|----------|----------|------------|
| 302260000 | What holiday is the dog's hat for? | christmas | ✅ | ❌ | ✅ | ✅ | ✅ |
| 145824000 | Is the skier going up or down? | up | ✅ | ❌ | ✅ | ❌ | ✅ |
| 143450001 | What is stuck in the cake? | flag | ✅ | ❌ | ✅ | ✅ | ✅ |
| 397303002 | What is the man making? | ties | ❌ | ❌ | ❌ | ❌ | ✅ |
| 406647002 | What does the yellow sign say? | ped xing | ❌ | ❌ | ❌ | ❌ | ❌ |

**Analysis:** Object identification and text recognition questions show mixed results. Moondream2 performs best with 4/5 correct answers, while Phi-3.5-Vision and SmolVLM2-Instruct each get 3/5 correct.

### **Model Performance Breakdown**

#### **1. Moondream2** 🥇 **Best Overall**
- **Simple Accuracy:** 65.0% (13/20 correct)
- **VQA Accuracy:** 62.5%
- **Avg Inference:** 8.35s
- **Strengths:** Best overall accuracy, excellent VQA performance, strong on complex questions
- **Weaknesses:** Slower inference than some competitors
- **Best Question Types:** Yes/No questions, object identification, counting

#### **2. SmolVLM2-Instruct** 🥈 **Fast & Accurate**
- **Simple Accuracy:** 55.0% (11/20 correct)
- **VQA Accuracy:** 52.5%
- **Avg Inference:** 8.41s
- **Strengths:** Good overall accuracy, balanced performance, MLX optimized
- **Weaknesses:** Lower accuracy than Moondream2, struggles with counting
- **Best Question Types:** Color recognition, object identification

#### **3. Phi-3.5-Vision** 🥉 **Balanced**
- **Simple Accuracy:** 35.0% (7/20 correct)
- **VQA Accuracy:** 35.0%
- **Avg Inference:** 5.29s
- **Strengths:** Balanced performance, reasonable speed
- **Weaknesses:** Lower accuracy than top performers
- **Best Question Types:** Basic object identification

#### **4. SmolVLM-Instruct** 🏆 **Fastest**
- **Simple Accuracy:** 35.0% (7/20 correct)
- **VQA Accuracy:** 36.0%
- **Avg Inference:** 0.39s (fastest)
- **Strengths:** Fastest inference, reliable text support, stable
- **Weaknesses:** Lower accuracy than top performers
- **Best Question Types:** Basic questions, speed-critical applications

#### **5. LLaVA-MLX** ⚠️ **Poor Performance**
- **Simple Accuracy:** 20.0% (4/20 correct)
- **VQA Accuracy:** 21.0%
- **Avg Inference:** 24.15s (slowest)
- **Strengths:** Large model capacity
- **Weaknesses:** Poor accuracy, slow inference, batch inference issues
- **Best Question Types:** None (consistently poor performance)

---

## **📁 Result Files**

### **Output Format**
```json
{
  "experiment_metadata": {
    "test_date": "2025-07-29 13:12:58",
    "test_mode": "coco",
    "num_questions": 20,
    "framework_version": "vqa2_enhanced_v1.2",
    "evaluation_method": "VQA 2.0 Standard",
    "dataset": "COCO val2014",
    "generation_params": {
      "max_new_tokens": 100,
      "do_sample": false
    }
  },
  "hardware_configuration": {
    "device": "MacBook Air M3",
    "memory": "16GB",
    "mps_available": true,
    "torch_version": "2.7.1",
    "python_version": "3.13.3"
  },
  "model_configuration": {
    "models_tested": [
      "phi35_vision",
      "llava_mlx",
      "smolvlm_v2_instruct",
      "smolvlm_instruct",
      "moondream2"
    ],
    "model_loader": "VLMModelLoader from vlm_tester.py",
    "unified_parameters": true,
    "image_preprocessing": "Resize to max 1024px, LANCZOS"
  },
  "results": {
    "model_name": {
      "model_id": "model_identifier",
      "total_questions": 20,
      "correct_answers": 13,
      "accuracy": 0.65,
      "vqa_accuracy": 0.625,
      "avg_inference_time": 8.35,
      "question_results": [...]
    }
  }
}
```

### **File Naming Convention**
- **Complete Tests:** `results/vqa2_results_coco_YYYYMMDD_HHMMSS.json`
- **Single Model Tests:** `results/vqa2_results_single_{model_name}_YYYYMMDD_HHMMSS.json`
- **Examples:**
  - `vqa2_results_coco_20250801_191939.json` (complete test)
  - `vqa2_results_single_phi35_vision_20250801_192204.json` (single model)

---

## **🔧 Framework Architecture**

### **Core Components**

#### **VQAFramework Class**
- **Data Loading:** COCO dataset and sample data management
- **Model Evaluation:** Unified evaluation across different models
- **Enhanced Accuracy Calculation:** Simple and improved VQA accuracy computation
- **Result Management:** JSON output generation with detailed metadata
- **Enhanced Memory Management:** MLX-specific memory cleanup and monitoring
- **Results Saving:** Consistent file naming for both single model and complete tests

#### **Model Integration**
- **Unified Interface:** Consistent API across different model types
- **MLX Support:** Subprocess handling for MLX-optimized models
- **Error Handling:** Timeout and error recovery mechanisms
- **Memory Management:** Efficient model loading and cleanup

### **Evaluation Process**
1. **Data Preparation:** Load questions and ground truth answers
2. **Model Loading:** Initialize model with appropriate framework
3. **Question Processing:** Generate answers for each question with periodic memory cleanup
4. **Enhanced Accuracy Calculation:** Compare answers with ground truth using improved logic
5. **Result Compilation:** Generate comprehensive JSON report with detailed analysis
6. **Results Saving:** Save to `results/` directory with consistent naming convention

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

### **Enhanced Memory Management**
- **Problem:** MLX models can cause `[METAL] Command buffer execution failed: Insufficient Memory` errors
- **Solution:** Enhanced MLX memory management with periodic cleanup and adaptive memory pressure detection
- **Implementation:** 
  - Periodic cleanup every 5 questions for MLX models
  - Adaptive aggressive cleanup when memory pressure is high
  - MLX-specific memory clearing with `clear_mlx_memory()` function
- **Impact:** Stable performance without memory overflow errors

### **VQA Accuracy Calculation**
- **Problem:** Previous logic had inconsistencies in ground truth handling
- **Solution:** Enhanced logic with hierarchical matching and improved preprocessing
- **Impact:** More accurate and consistent evaluation results

---

## **🎯 Best Practices**

### **Model Selection**
- **Best Overall Performance:** Use Moondream2 (65.0% accuracy)
- **Speed-Critical Tasks:** Use SmolVLM-Instruct (0.39s avg inference)
- **VQA-Critical Tasks:** Use Moondream2 (62.5% VQA accuracy)
- **Vision-Only Tasks:** Use Moondream2 (65.0% simple accuracy)
- **Balanced Performance:** Use SmolVLM2-Instruct (55.0% accuracy, 8.41s)
- **Avoid:** LLaVA-MLX for accuracy-critical applications

### **Testing Configuration**
- **Question Count:** 20 questions for reliable evaluation
- **Timeout Settings:** 60s for small models, 180s for large models
- **Memory Management:** Enhanced MLX memory management with periodic cleanup
- **Result Validation:** Always verify ground truth accuracy
- **Results Saving:** All results automatically saved to `results/` directory

### **Performance Optimization**
- **MLX Models:** Use for Apple Silicon optimization with enhanced memory management
- **Batch Processing:** Not supported (sequential processing required)
- **Caching:** Results cached in JSON format for analysis
- **Parallel Testing:** Not recommended due to memory constraints
- **Memory Cleanup:** Periodic cleanup every 5 questions for MLX models

---

## **📈 Performance Comparison**

### **Speed Rankings**
1. **SmolVLM-Instruct:** 0.39s avg inference
2. **Phi-3.5-Vision:** 5.29s avg inference
3. **Moondream2:** 8.35s avg inference
4. **SmolVLM2-Instruct:** 8.41s avg inference
5. **LLaVA-MLX:** 24.15s avg inference

### **Accuracy Rankings**
1. **Moondream2:** 65.0% simple accuracy, 62.5% VQA accuracy
2. **SmolVLM2-Instruct:** 55.0% simple accuracy, 52.5% VQA accuracy
3. **Phi-3.5-Vision:** 35.0% simple accuracy, 35.0% VQA accuracy
4. **SmolVLM-Instruct:** 35.0% simple accuracy, 36.0% VQA accuracy
5. **LLaVA-MLX:** 20.0% simple accuracy, 21.0% VQA accuracy

### **Overall Rankings**
1. **Moondream2:** Best overall (accurate + balanced speed)
2. **SmolVLM2-Instruct:** Fast & accurate
3. **SmolVLM-Instruct:** Fastest inference
4. **Phi-3.5-Vision:** Balanced performance
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
- **VQA Results:** `vqa2_results_*.json`
- **Performance Data:** `test_results_*.json`
- **Context Data:** `context_understanding_test_results_*.json`
- **Memory Management:** `ENHANCED_MEMORY_MANAGEMENT.md`
- **Results Saving:** `RESULTS_SAVING_UPDATE.md`

### **Testing & Verification**
- **Results Saving Test:** `test_results_saving.py` - Verifies individual model results are properly saved
- **Memory Management Test:** `test_enhanced_memory.py` - Tests enhanced MLX memory management
- **Test Coverage:** Single model saving, complete test saving, results directory structure validation

### **Usage Examples**
```bash
# Test single model with results saved to results/ directory
python vqa_test.py --questions 10 --models phi35_vision --verbose

# Test multiple models with complete results
python vqa_test.py --questions 20 --models phi35_vision moondream2

# Run verification tests
python test_results_saving.py
python test_enhanced_memory.py
```

---

**Framework Version:** vqa2_enhanced_v1.2  
**Test Environment:** MacBook Air M3 (16GB RAM, MPS available)  
**Latest Test Results:** vqa2_results_coco_20250801_191939.json (Complete Test) + Individual Model Results

## **Recent Updates**

### **Enhanced Memory Management** (August 1, 2025)
- ✅ Implemented enhanced MLX memory management to prevent `[METAL] Command buffer execution failed: Insufficient Memory` errors
- ✅ Added periodic memory cleanup every 5 questions for MLX models
- ✅ Implemented adaptive memory pressure detection and aggressive cleanup
- ✅ Added `clear_mlx_memory()` function for MLX-specific memory clearing
- ✅ Integrated with `vlm_tester.py` and `vlm_context_tester.py` for consistency

### **Improved Results Saving** (August 1, 2025)
- ✅ Fixed individual model results saving to `results/` directory
- ✅ Implemented consistent file naming convention for single model tests
- ✅ Added timestamp-based filenames to prevent overwriting
- ✅ Enhanced save logic with proper suffix handling
- ✅ All results now saved with format: `vqa2_results_single_{model}_{timestamp}.json`

### **Other Notes**
- All references to `testing_material/` have been updated to `materials/`.
- All references to result files are now in `results/`.
- All scripts are now in the `vqa/` subfolder.
- Enhanced VQA accuracy calculation logic implemented.
- This README reflects the latest test results and framework updates.
- All performance metrics verified against source JSON data.
