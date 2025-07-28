# AI Manual Assistant - VLM Performance Test Results

**Latest VQA 2.0 Test Results** | **Hardware**: MacBook Air M3 (16GB RAM) | **Test Framework**: VQA 2.0 Standard Evaluation

This document summarizes the comprehensive performance testing of all Vision-Language Models integrated into the AI Manual Assistant system.

## 🏆 Performance Rankings (VQA 2.0 Results)

### Overall Performance Summary

| **Model** | **VQA Accuracy** | **Avg Inference Time** | **Memory Usage** | **Status** | **Recommendation** |
|-----------|:----------------:|:----------------------:|:----------------:|:----------:|:------------------:|
| **Moondream2** | 🥇 **52.5%** | 7.16s | 🏆 **0.10GB** | ✅ Active | **Best Overall** |
| **SmolVLM2-500M-Video-Instruct** | 🥈 **51.5%** | 5.48s | 2.08GB | ✅ Active | **Fast & Accurate** |
| **SmolVLM-500M-Instruct** | **39.5%** | 🏆 **1.17s** | 1.58GB | ✅ Active | **Fastest** |
| **Phi-3.5-Vision (MLX)** | **42.5%** | 6.86s | 1.53GB | ✅ Active | **Balanced** |
| **LLaVA-v1.6 (MLX)** | ⚠️ **27.0%** | 9.79s | 1.16GB | 🔧 Issues | **Not Recommended** |

## 📊 Detailed Test Results

### VQA 2.0 Testing Framework
- **Dataset**: Real COCO images with VQA 2.0 questions
- **Test Scenarios**: 10, 15, and 20 question batches
- **Evaluation Metrics**: VQA accuracy, simple accuracy, inference time, memory usage
- **Hardware**: MacBook Air M3, 16GB unified memory

### Model Performance Analysis

#### 🥇 Moondream2 (Best Overall)
- **VQA Accuracy**: 52.5% (highest among all models)
- **Simple Accuracy**: 60.0% (12/20 correct responses)
- **Avg Inference Time**: 7.16s (balanced performance)
- **Memory Usage**: 0.10GB (lowest)
- **Load Time**: ~5.34s
- **Strengths**: Best accuracy, lowest memory usage, stable performance
- **Use Cases**: Production environments, tasks requiring high accuracy

#### 🥈 SmolVLM2-500M-Video-Instruct (Fast & Accurate)
- **VQA Accuracy**: 51.5% (second highest)
- **Simple Accuracy**: 60.0% (12/20 correct responses)
- **Avg Inference Time**: 5.48s (fast and accurate)
- **Memory Usage**: 2.08GB
- **Load Time**: ~1.02s
- **Strengths**: Good accuracy/speed balance, video capabilities, stable performance
- **Use Cases**: General-purpose analysis, video processing

#### 🏆 SmolVLM-500M-Instruct (Fastest)
- **VQA Accuracy**: 39.5%
- **Simple Accuracy**: 40.0% (8/20 correct responses)
- **Avg Inference Time**: 1.17s (fastest among all models)
- **Memory Usage**: 1.58GB (efficient)
- **Load Time**: ~2.04s
- **Strengths**: Fastest inference, reliable, low memory usage
- **Use Cases**: Speed-critical applications, real-time processing

#### 🥉 Phi-3.5-Vision (MLX) (Balanced)
- **VQA Accuracy**: 42.5% (good accuracy)
- **Simple Accuracy**: 40.0% (8/20 correct responses)
- **Avg Inference Time**: 6.86s (balanced)
- **Memory Usage**: 1.53GB
- **Load Time**: ~1.52s (fast loading)
- **Strengths**: Balanced performance, MLX optimization
- **Use Cases**: General analysis tasks, balanced workloads

#### ⚠️ LLaVA-v1.6 (MLX) (Underperforming)
- **VQA Accuracy**: 27.0% (significant performance degradation)
- **Simple Accuracy**: 25.0% (5/20 correct responses)
- **Avg Inference Time**: 9.79s (slow)
- **Memory Usage**: 1.16GB
- **Load Time**: ~2.17s
- **Issues**: Batch inference issues, poor performance, unreliable
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
1. **Primary**: Moondream2 (best overall performance)
2. **Backup**: SmolVLM2-500M-Video-Instruct (fast & accurate)
3. **Avoid**: LLaVA-MLX (performance issues)

### Speed-Critical Applications
1. **Primary**: SmolVLM-500M-Instruct (1.17s inference, fastest)
2. **Alternative**: SmolVLM2-500M-Video-Instruct (5.48s inference, good accuracy)

### Resource-Constrained Environments
1. **Primary**: Moondream2 (0.10GB memory usage)
2. **Alternative**: SmolVLM (1.58GB memory usage)

### High-Accuracy Requirements
1. **Primary**: Moondream2 (52.5% VQA accuracy)
2. **Alternative**: SmolVLM2-500M-Video-Instruct (51.5% VQA accuracy)

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
- **Moondream2** provides the best balance of accuracy and speed
- **SmolVLM** excels in speed-critical scenarios (fastest inference)
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