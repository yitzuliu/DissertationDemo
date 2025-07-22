# AI Manual Assistant - Testing Framework

This directory contains the comprehensive testing infrastructure for the AI Manual Assistant project, including VQA 2.0 evaluation, performance benchmarking, and model comparison tools.

## 🏗️ Current Testing Directory Structure

```
src/testing/
├── vqa/                          # VQA 2.0 Testing Framework
│   ├── vqa_framework.py         # Core VQA testing infrastructure
│   ├── vqa_test.py              # Test runner and execution
│   └── vqa_README.md            # VQA testing documentation
├── vlm/                          # Vision-Language Model Tests
│   ├── vlm_tester.py            # Model performance testing
│   ├── vlm_context_tester.py    # Context understanding tests
│   └── vlm_README.md            # VLM testing documentation
├── rag/                          # RAG Testing (Planned)
│   ├── rag_module.py            # RAG testing module
│   └── README.md                # RAG testing documentation
├── results/                      # Test Outputs and Logs
│   ├── test_results_*.json      # Raw test results
│   ├── context_understanding_*.json  # Context test results
│   └── vqa2_results_*.json      # VQA 2.0 test results
├── reports/                      # Test Reports and Analysis
│   ├── vqa_test_result.md       # VQA test analysis
│   ├── context_understanding_test_results_summary.md
│   └── model_active.md          # Active model status
├── materials/                    # Test Materials and Datasets
│   ├── vqa2/                    # VQA 2.0 dataset
│   └── images/                  # Additional test images
└── __pycache__/                 # Python cache (auto-generated)
```

## 🎯 VQA 2.0 Testing Framework

### Overview
The VQA 2.0 testing framework provides standardized evaluation of Vision-Language Models using real COCO dataset images and questions.

### Key Features
- **Standardized Evaluation**: VQA 2.0 compliant assessment
- **Multiple Test Sizes**: 5, 10, 15, 20 question batches
- **Performance Metrics**: VQA accuracy, simple accuracy, inference time, memory usage
- **Model Comparison**: Side-by-side performance analysis
- **Detailed Reporting**: Comprehensive test results and time analysis

### Running VQA Tests

```bash
# Quick test (10 questions) - Recommended for development
python src/testing/vqa/vqa_test.py --questions 10 --models smolvlm2

# Standard test (15 questions) - Balanced evaluation
python src/testing/vqa/vqa_test.py --questions 15 --models smolvlm2

# Comprehensive test (20 questions) - Full evaluation
python src/testing/vqa/vqa_test.py --questions 20 --models smolvlm2

# Compare multiple models
python src/testing/vqa/vqa_test.py --questions 10 --models smolvlm2 smolvlm moondream2
```

### Latest Test Results Summary

**VQA 2.0 Results (10 Questions):**

| Model | VQA Accuracy | Avg Time | Memory | Status |
|-------|:------------:|:--------:|:------:|:------:|
| **SmolVLM2** | 🥇 66.0% | 6.61s | 2.08GB | ✅ Best |
| **SmolVLM** | 🥈 64.0% | 5.98s | 1.58GB | ✅ Excellent |
| **Moondream2** | 56.0% | 🏆 4.06s | 🏆 0.10GB | ✅ Fastest |
| **Phi-3.5-Vision** | 60.0% | 13.61s | 1.53GB | ✅ Detailed |
| **LLaVA-MLX** | ⚠️ 34.0% | 17.86s | 1.16GB | 🔧 Issues |

## 🔧 VLM Performance Testing

### Model Performance Tests
- **Load Time Measurement**: Model initialization benchmarks
- **Inference Speed**: Response time analysis
- **Memory Usage**: Resource consumption tracking
- **Accuracy Assessment**: Response quality evaluation

### Context Understanding Tests
- **Temporal Reasoning**: Multi-frame understanding
- **Object Tracking**: Consistency across frames
- **Activity Recognition**: Task understanding capabilities
- **Progress Monitoring**: Step-by-step guidance evaluation

### Running Performance Tests

```bash
# Basic performance test
python src/testing/vlm/vlm_tester.py --model smolvlm2

# Context understanding test
python src/testing/vlm/vlm_context_tester.py --model smolvlm2 --frames 10
```

## 📊 Test Materials and Datasets

### VQA 2.0 Dataset
- **Questions**: Real VQA 2.0 questions from COCO dataset
- **Images**: Corresponding COCO images
- **Ground Truth**: Expected answers for accuracy calculation
- **Metadata**: Question types, difficulty levels, categories

### Custom Test Images
- **Synthetic Images**: Computer-generated test cases
- **Real-world Scenarios**: Cooking, repair, assembly tasks
- **Edge Cases**: Challenging scenarios for model evaluation
- **Performance Benchmarks**: Standardized test images

## 📈 Results and Reporting

### Test Results Storage
- **Raw Results**: JSON format with detailed metrics (`results/`)
- **Performance Logs**: Timing and resource usage data
- **Error Logs**: Failed test cases and error analysis
- **Comparison Reports**: Side-by-side model comparisons (`reports/`)

### Available Reports
- **VQA Test Results**: `reports/vqa_test_result.md`
- **Context Understanding**: `reports/context_understanding_test_results_summary.md`
- **Model Status**: `reports/model_active.md`

## 📋 TODO: Future Testing Enhancements

### Planned Testing Features
- [ ] **RAG Testing Framework** - Comprehensive RAG evaluation
- [ ] **State Tracker Testing** - Memory and context evaluation
- [ ] **Multi-modal Testing** - Audio and sensor integration tests
- [ ] **Real-time Performance** - Live system performance monitoring

### Testing Infrastructure Improvements
- [ ] **Automated Test Generation** - AI-generated test cases
- [ ] **Performance Regression Detection** - Automated performance monitoring
- [ ] **Test Result Visualization** - Interactive performance dashboards
- [ ] **Distributed Testing** - Multi-machine test execution

### Advanced Evaluation Metrics
- [ ] **User Experience Metrics** - Task completion success rates
- [ ] **Context Coherence** - Multi-turn conversation evaluation
- [ ] **Safety Assessment** - Harmful content detection
- [ ] **Bias Evaluation** - Fairness and bias testing

## 🛠️ Testing Best Practices

### Test Development Guidelines
1. **Reproducible Tests**: Use fixed random seeds and standardized datasets
2. **Comprehensive Coverage**: Test all supported models and configurations
3. **Performance Baselines**: Establish and maintain performance benchmarks
4. **Error Handling**: Robust error handling and recovery mechanisms

### Test Execution Guidelines
1. **Clean Environment**: Fresh model loading for each test
2. **Resource Monitoring**: Track memory and CPU usage
3. **Result Validation**: Verify test results and data integrity
4. **Documentation**: Document test procedures and findings

### Maintenance Guidelines
1. **Regular Updates**: Keep datasets and benchmarks current
2. **Performance Tracking**: Monitor performance trends over time
3. **Test Cleanup**: Remove obsolete tests and data (`__pycache__/` cleanup)
4. **Documentation Updates**: Keep testing documentation current

## 📚 Additional Resources

- **[VQA 2.0 Documentation](./vqa/vqa_README.md)** - Detailed VQA testing guide
- **[VLM Testing Documentation](./vlm/vlm_README.md)** - VLM testing procedures
- **[Model Comparison Guide](../../docs/MODEL_COMPARISON.md)** - Performance analysis
- **[Test Results Summary](../../TEST_RESULTS_SUMMARY.md)** - Latest benchmarks
- **[System Architecture](../../docs/ARCHITECTURE.md)** - Overall system design

---

**For specific testing procedures, see the README files in each subdirectory.**

**Last Updated**: January 2025  
**Test Framework**: VQA 2.0 Standard Evaluation  
**Hardware**: MacBook Air M3, 16GB RAM 