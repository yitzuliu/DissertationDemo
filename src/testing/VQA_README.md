# 🎯 VQA 2.0 Testing Framework

A comprehensive Visual Question Answering testing framework using real COCO dataset images and VQA 2.0 questions.

## 📊 **Quick Summary**

### **Supported Models**
- **SmolVLM2-500M-Video-Instruct**: MLX optimized for Apple Silicon (M1/M2/M3)
- **SmolVLM-500M-Instruct**: Fast and reliable transformers model
- **Moondream2**: Vision-only model with excellent image quality
- **LLaVA-v1.6-Mistral-7B-MLX**: Creative writing with MLX optimization
- **Phi-3.5-Vision-Instruct**: Educational applications with MLX optimization

### **Test Environment**
- **Dataset**: VQA 2.0 + COCO val2014 images
- **Images**: 20 real COCO images (IDs: 139, 285, 632, 724, 776, 785, 802, 872, 885, 1000, 1268, 1296, 1353, 1584, 1818, 2006, 2149, 2153, 2157, 2261)
- **Questions**: Real VQA 2.0 questions with annotations
- **Evaluation**: VQA accuracy + simple accuracy metrics

## 🚀 **Quick Start**

```bash
# Basic test (20 questions, all models)
python vqa_test.py

# Test specific model
python vqa_test.py --questions 10 --models moondream2

# Test multiple models
python vqa_test.py --questions 15 --models moondream2 smolvlm_instruct

# Verbose output
python vqa_test.py --questions 5 --verbose
```

## 📋 **Command Line Options**

```bash
python vqa_test.py [OPTIONS]

Options:
  --questions INTEGER     Number of questions (1-20, default: 20)
  --models [model_list]   Models to test (default: all models)
  --verbose              Show detailed output
  --save-results         Save results to JSON (default: True)
  --help                 Show help message
```

## 📊 **Result Format**

Each test generates a JSON file with complete question-image mapping:

```json
{
  "test_metadata": {
    "test_date": "2025-07-18 22:21:26",
    "test_mode": "coco",
    "num_questions": 20,
    "framework_version": "unified_v1.1"
  },
  "results": {
    "moondream2": {
      "accuracy": 0.6,
      "vqa_accuracy": 0.72,
      "question_results": [
        {
          "question_id": 100187002,
          "image_id": 100187,
          "image_filename": "COCO_val2014_000000100187.jpg",
          "question": "Is it daytime?",
          "model_answer": "Yes",
          "ground_truth": "no",
          "is_correct": false,
          "vqa_accuracy": 0.0,
          "inference_time": 4.23
        }
      ]
    }
  }
}
```

## 🎯 **Key Features**

- **Real Data**: Official VQA 2.0 dataset + COCO images
- **Multiple Models**: Support for 5 different VLM models
- **Complete Mapping**: Full question-image correspondence
- **Auto Download**: Automatic data and image downloading
- **Memory Efficient**: Automatic model cleanup
- **Detailed Results**: Comprehensive accuracy analysis

## 📁 **File Structure**

```
src/testing/
├── vqa_framework.py      # Core VQA framework
├── vqa_test.py          # Command-line interface
├── VQA_README.md        # This documentation
├── VQA_RESULT_FORMAT.md # Result format details
├── results/             # Test results (JSON files)
└── testing_material/    # VQA data and COCO images
    └── vqa2/
        └── images/
            └── val2014_sample/  # COCO image files
```

## 📈 **Expected Performance**

Based on previous test results:
- **SmolVLM2-500M-Video**: ~66% VQA accuracy, fastest MLX inference
- **SmolVLM-500M-Instruct**: ~64% VQA accuracy, balanced performance  
- **Moondream2**: ~56% VQA accuracy, fastest overall inference
- **LLaVA-MLX**: ~34% VQA accuracy, creative responses
- **Phi-3.5-Vision**: ~60% VQA accuracy, detailed explanations

## 🔍 **Troubleshooting**

1. **Network Issues**: First run requires downloading data
2. **Memory Issues**: Use smaller models (moondream2)
3. **Model Loading**: Check model ID and network connection
4. **Image Download**: Framework creates placeholder if download fails

## 🎯 **Recommendations**

- **Quick Testing**: Use `smolvlm_v2_instruct` (MLX optimized, best accuracy)
- **Comprehensive Testing**: Use `smolvlm_instruct` (balanced performance)
- **Speed Testing**: Use `moondream2` (fastest inference)
- **⚠️ Avoid**: `llava_mlx` (state issues), `phi35_vision` (slow inference)

---

**Framework Version**: unified_v1.1  
**Last Updated**: July 18, 2025
