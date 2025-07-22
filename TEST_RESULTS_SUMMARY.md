# AI Manual Assistant - VLM Performance Test Results

**Latest VQA 2.0 Test Results** | **Hardware**: MacBook Air M3 (16GB RAM) | **Test Framework**: VQA 2.0 Standard Evaluation

This document summarizes the comprehensive performance testing of all Vision-Language Models integrated into the AI Manual Assistant system.

## 🏆 Performance Rankings (VQA 2.0 Results)

### Overall Performance Summary

| **Model** | **VQA Accuracy** | **Avg Inference Time** | **Memory Usage** | **Status** | **Recommendation** |
|-----------|:----------------:|:----------------------:|:----------------:|:----------:|:------------------:|
| **SmolVLM2-500M-Video-Instruct** | 🥇 **66.0%** | 6.61s | 2.08GB | ✅ Active | **Best Overall** |
| **SmolVLM-500M-Instruct** | 🥈 **64.0%** | 5.98s | 1.58GB | ✅ Active | **Excellent Alternative** |
| **Phi-3.5-Vision (MLX)** | 🥉 **60.0%** | 13.61s | 1.53GB | ✅ Active | **High Accuracy** |
| **Moondream2** | **56.0%** | 🏆 **4.06s** | 🏆 **0.10GB** | ✅ Active | **Speed Champion** |
| **LLaVA-v1.6 (MLX)** | ⚠️ **34.0%** | 17.86s | 1.16GB | 🔧 Issues | **Not Recommended** |

## 📊 Detailed Test Results

### VQA 2.0 Testing Framework
- **Dataset**: Real COCO images with VQA 2.0 questions
- **Test Scenarios**: 10, 15, and 20 question batches
- **Evaluation Metrics**: VQA accuracy, simple accuracy, inference time, memory usage
- **Hardware**: MacBook Air M3, 16GB unified memory

### Model Performance Analysis

#### 🥇 SmolVLM2-500M-Video-Instruct (Best Overall)
- **VQA Accuracy**: 66.0% (highest among all models)
- **Simple Accuracy**: 70.0% (7/10 correct responses)
- **Avg Inference Time**: 6.61s (balanced performance)
- **Memory Usage**: 2.08GB
- **Load Time**: ~2.32s
- **Strengths**: Best accuracy/speed balance, video capabilities, stable performance
- **Use Cases**: Production environments, tasks requiring high accuracy

#### 🥈 SmolVLM-500M-Instruct (Excellent Alternative)
- **VQA Accuracy**: 64.0% (second highest)
- **Simple Accuracy**: 60.0% (6/10 correct responses)
- **Avg Inference Time**: 5.98s (fast and stable)
- **Memory Usage**: 1.58GB (efficient)
- **Load Time**: ~4.40s
- **Strengths**: Reliable, low memory usage, consistent performance
- **Use Cases**: General-purpose analysis, resource-constrained environments

#### 🏆 Moondream2 (Speed Champion)
- **VQA Accuracy**: 56.0% (good for lightweight model)
- **Simple Accuracy**: 60.0% (6/10 correct responses)
- **Avg Inference Time**: 4.06s (fastest among all models)
- **Memory Usage**: 0.10GB (lowest resource usage)
- **Load Time**: ~5.15s
- **Strengths**: Fastest inference, minimal memory usage, highly stable
- **Use Cases**: Speed-critical applications, real-time processing

#### 🥉 Phi-3.5-Vision (MLX) (High Accuracy)
- **VQA Accuracy**: 60.0% (good accuracy)
- **Simple Accuracy**: 60.0% (6/10 correct responses)
- **Avg Inference Time**: 13.61s (slower but detailed)
- **Memory Usage**: 1.53GB
- **Load Time**: ~1.94s (fastest loading)
- **Strengths**: Detailed analysis, strong reasoning, MLX optimization
- **Use Cases**: Detailed analysis tasks, offline processing

#### ⚠️ LLaVA-v1.6 (MLX) (Underperforming)
- **VQA Accuracy**: 34.0% (significant performance degradation)
- **Simple Accuracy**: 30.0% (3/10 correct responses)
- **Avg Inference Time**: 17.86s (slow due to reloading overhead)
- **Memory Usage**: 1.16GB
- **Load Time**: ~2.77s
- **Issues**: Model reloading required for each image, state management problems
- **Status**: Functional but not recommended due to performance issues

## 📈 Performance Trends and Analysis

### Time Analysis by Test Size

#### 10 Questions Test (Recommended for Quick Evaluation)
- **Moondream2**: ~41 seconds total (fastest)
- **SmolVLM**: ~60 seconds total (balanced)
- **SmolVLM2**: ~66 seconds total (best accuracy)

#### 15 Questions Test (Standard Evaluation)
- **Moondream2**: ~55 seconds total, 56-60% accuracy
- **SmolVLM**: ~90 seconds total, 49-64% accuracy
- **SmolVLM2**: ~98 seconds total, 58-66% accuracy

#### 20 Questions Test (Comprehensive Evaluation)
- **Moondream2**: ~74 seconds total, 56-60% accuracy
- **SmolVLM2**: ~130 seconds total, 58-66% accuracy

### Memory Usage Patterns
- **Moondream2**: Minimal memory footprint (0.10GB)
- **SmolVLM**: Efficient usage (1.58GB)
- **Phi-3.5-Vision**: Moderate usage (1.53GB)
- **SmolVLM2**: Higher usage but justified by performance (2.08GB)
- **LLaVA-MLX**: Moderate usage but poor performance (1.16GB)

## 🎯 Recommendations by Use Case

### Production Deployment
1. **Primary**: SmolVLM2-500M-Video-Instruct (best overall performance)
2. **Backup**: SmolVLM-500M-Instruct (excellent reliability)
3. **Avoid**: LLaVA-MLX (performance issues)

### Speed-Critical Applications
1. **Primary**: Moondream2 (4.06s inference, minimal resources)
2. **Alternative**: SmolVLM (5.98s inference, good accuracy)

### Resource-Constrained Environments
1. **Primary**: Moondream2 (0.10GB memory usage)
2. **Alternative**: SmolVLM (1.58GB memory usage)

### High-Accuracy Requirements
1. **Primary**: SmolVLM2 (66.0% VQA accuracy)
2. **Alternative**: SmolVLM (64.0% VQA accuracy)

## 🔧 Testing Infrastructure

### VQA 2.0 Framework Location
- **Framework**: `src/testing/vqa/vqa_framework.py`
- **Test Runner**: `src/testing/vqa/vqa_test.py`
- **Results**: `src/testing/results/`
- **Materials**: `src/testing/materials/vqa2/`

### Running Performance Tests
```bash
# Quick test (10 questions)
python src/testing/vqa/vqa_test.py --questions 10 --models smolvlm2

# Standard test (15 questions)
python src/testing/vqa/vqa_test.py --questions 15 --models smolvlm2

# Comprehensive test (20 questions)
python src/testing/vqa/vqa_test.py --questions 20 --models smolvlm2

# Compare multiple models
python src/testing/vqa/vqa_test.py --questions 10 --models smolvlm2 smolvlm moondream2
```

## 📋 Key Takeaways

### Performance Insights
- **SmolVLM2** provides the best balance of accuracy and speed
- **Moondream2** excels in speed-critical scenarios
- **MLX optimization** is essential for Apple Silicon performance
- **Model reloading** significantly impacts performance (LLaVA issue)

### Reliability Findings
- Most models show consistent performance across test runs
- **LLaVA-MLX** has known issues with state management
- **Synthetic image processing** remains challenging for some models
- **Real-world camera applications** perform better than synthetic tests

### Resource Management
- Memory usage varies significantly between models (0.10GB - 2.08GB)
- **Apple Silicon unified memory** enables efficient model switching
- **Single model operation** recommended due to memory constraints

---

**Test Framework**: VQA 2.0 Standard Evaluation  
**Last Updated**: January 2025  
**Hardware**: MacBook Air M3, 16GB RAM  
**For detailed results**: See `src/testing/results/` directory 