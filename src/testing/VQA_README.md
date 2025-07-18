# 🎯 VQA 2.0 Testing Framework

A comprehensive Visual Question Answering testing framework using real COCO dataset images and VQA 2.0 questions.

## 🚀 Quick Start

```bash
# Basic test with default settings (20 questions, all models)
python vqa_test.py

# Test with specific parameters
python vqa_test.py --questions 10 --models moondream2

# Test multiple models
python vqa_test.py --questions 15 --models moondream2 smolvlm_instruct

# Verbose output with question-image mapping
python vqa_test.py --questions 5 --verbose
```

## 📊 Supported Models

- `moondream2` - Lightweight, fastest (recommended for testing)
- `smolvlm_instruct` - 500M parameters, balanced performance
- `smolvlm_v2_instruct` - Video-optimized version
- `llava_mlx` - 7B model, larger but good performance
- `phi35_vision` - Microsoft model

## 🖼️ COCO Dataset

The framework automatically uses 20 real COCO val2014 images:
- **Image IDs**: 139, 285, 632, 724, 776, 785, 802, 872, 885, 1000, 1268, 1296, 1353, 1584, 1818, 2006, 2149, 2153, 2157, 2261
- **Storage**: `testing_material/vqa2/images/val2014_sample/`
- **Format**: `COCO_val2014_000000000139.jpg` (12-digit zero-padded)

## 📋 Result Format

Each test generates a JSON file with complete question-image mapping:

```json
{
  "test_metadata": {
    "test_date": "2025-07-18 22:21:26",
    "test_mode": "coco",
    "num_questions": 20,
    "framework_version": "unified_v1.1",
    "image_reference_note": "Each question's image_id corresponds to image_filename, image files are located in testing_material/vqa2/images/val2014_sample/ directory"
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

## 🎯 Key Features

- **Real Data**: Uses official VQA 2.0 dataset and COCO images
- **Multiple Models**: Support for 5 different VLM models
- **Complete Mapping**: Full question-image correspondence tracking
- **Auto Download**: Automatic VQA data and COCO image downloading
- **Memory Efficient**: Automatic model memory cleanup
- **Detailed Results**: Comprehensive accuracy and timing analysis

## 📁 File Structure

```
src/testing/
├── vqa_framework.py      # Core VQA framework
├── vqa_test.py          # Command-line interface
├── VQA_RESULT_FORMAT.md # Result format documentation
├── results/             # Test results (JSON files)
└── testing_material/    # VQA data and COCO images
    └── vqa2/
        └── images/
            └── val2014_sample/  # COCO image files
```

## 🔧 Command Line Options

```bash
python vqa_test.py [OPTIONS]

Options:
  --questions INTEGER     Number of questions to test (1-20, default: 20)
  --models [model_list]   Models to test (default: all models)
  --verbose              Show detailed output with question-image mapping
  --save-results         Save results to JSON file (default: True)
  --help                 Show help message
```

## 📈 Expected Performance

Based on previous test results:
- **Moondream2**: ~60-80% VQA accuracy, fastest inference
- **SmolVLM**: ~60-70% VQA accuracy, balanced performance  
- **LLaVA**: ~50-70% VQA accuracy, larger model but stable

## 🔍 Troubleshooting

1. **Network Issues**: First run requires downloading data
2. **Memory Issues**: Use smaller models (moondream2)
3. **Model Loading**: Check model ID and network connection
4. **Image Download**: Framework creates placeholder if download fails

---

**Framework Version**: unified_v1.1  
**Last Updated**: July 18, 2025
