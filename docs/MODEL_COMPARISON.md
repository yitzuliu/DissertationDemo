# Vision-Language Models Comparison Guide

This document provides a comprehensive comparison of all Vision-Language Models (VLMs) integrated into the AI Manual Assistant system, including the latest VQA 2.0 test results.

**Key Finding**: For this project, which runs on Apple Silicon, models optimized with the **MLX framework** are not just faster—they are essential. Standard transformer-based implementations of large models like LLaVA and Phi-3 were too slow to be usable, while their MLX counterparts are highly performant.

## Quick Reference Table (Updated with VQA 2.0 Results)

| Model | Type | VQA Accuracy (10題) | Avg Inference Time | Memory Usage | Status |
|-----------------------------|-----------------|---------------------|-------------------|--------------|--------|
| **SmolVLM2-500M-Video-Instruct** | Balanced | 🏆 66.0% | 6.61s | 2.08GB | ✅ **Best Overall** |
| **SmolVLM-500M-Instruct** | Balanced | 64.0% | 5.98s | 1.58GB | ✅ Excellent |
| **Phi-3.5-Vision (MLX)** | High-Accuracy | 60.0% | 13.61s | 1.53GB | ✅ Good |
| **Moondream2** | Lightweight | 56.0% | 🏆 4.06s | 0.10GB | ✅ Fastest |
| **LLaVA-v1.6 (MLX)** | Conversational | ⚠️ 34.0% | 17.86s | 1.16GB | 🔧 Underperforming |

---

## Detailed Model Analysis

### 1. SmolVLM2-500M-Video-Instruct (🏆 Best Overall)

The top-performing model in our latest VQA 2.0 tests, providing the best balance of accuracy and speed.

**Key Strengths:**
- **Highest VQA Accuracy**: 66.0% in 10-question tests
- **Excellent Balance**: Good speed (6.61s) with high accuracy
- **Stable Performance**: Very consistent inference times
- **Video Capabilities**: Can process video segments for temporal understanding

**VQA 2.0 Performance:**
- **Simple Accuracy**: 70.0% (7/10 correct)
- **VQA Accuracy**: 66.0%
- **Avg Inference Time**: 6.61s
- **Memory Usage**: 2.08GB

**Ideal Use Cases:**
- Production environments requiring reliable performance
- Tasks requiring both accuracy and reasonable speed
- Video analysis and temporal understanding

**Technical Specifications:**
- **Model ID**: `HuggingFaceTB/SmolVLM2-500M-Video-Instruct`
- **Load Time**: ~2.32s
- **Avg. Inference Time**: 6.61s
- **Memory Usage**: 2.08GB

### 2. SmolVLM-500M-Instruct (Excellent Alternative)

A reliable workhorse model with very good performance and stability.

**Key Strengths:**
- **High VQA Accuracy**: 64.0% in 10-question tests
- **Fast and Stable**: 5.98s average inference time
- **Low Memory Usage**: Only 1.58GB
- **Consistent Performance**: Very reliable across different scenarios

**VQA 2.0 Performance:**
- **Simple Accuracy**: 60.0% (6/10 correct)
- **VQA Accuracy**: 64.0%
- **Avg Inference Time**: 5.98s
- **Memory Usage**: 1.58GB

**Ideal Use Cases:**
- General-purpose visual analysis
- Resource-constrained environments
- When reliability is more important than maximum accuracy

**Technical Specifications:**
- **Model ID**: `HuggingFaceTB/SmolVLM-500M-Instruct`
- **Load Time**: ~4.40s
- **Avg. Inference Time**: 5.98s
- **Memory Usage**: 1.58GB

### 3. Moondream2 (🏆 Speed Champion)

The fastest model in our tests, ideal for speed-critical applications.

**Key Strengths:**
- **Fastest Inference**: 4.06s average (fastest among all models)
- **Very Low Memory**: Only 0.10GB memory usage
- **Good Accuracy**: 56.0% VQA accuracy despite being lightweight
- **Highly Stable**: Most consistent performance across tests

**VQA 2.0 Performance:**
- **Simple Accuracy**: 60.0% (6/10 correct)
- **VQA Accuracy**: 56.0%
- **Avg Inference Time**: 4.06s
- **Memory Usage**: 0.10GB

**Ideal Use Cases:**
- Applications where speed is the absolute priority
- Environments with very tight resource constraints
- Real-time applications requiring quick responses

**Technical Specifications:**
- **Model ID**: `vikhyatk/moondream2`
- **Load Time**: ~5.15s
- **Avg. Inference Time**: 4.06s
- **Memory Usage**: 0.10GB

### 4. Phi-3.5-Vision (MLX-Optimized) (High Accuracy)

A high-accuracy model that excels in detailed analysis but is slower than alternatives.

**Key Strengths:**
- **Good Accuracy**: 60.0% VQA accuracy
- **Detailed Analysis**: Provides comprehensive descriptions
- **Strong Reasoning**: Good at complex scene understanding
- **MLX Performance**: Optimized for Apple Silicon

**Limitations:**
- **Slow Inference**: 13.61s average (slower than alternatives)
- **Time Variability**: Inconsistent performance (11.79s - 14.75s)

**VQA 2.0 Performance:**
- **Simple Accuracy**: 60.0% (6/10 correct)
- **VQA Accuracy**: 60.0%
- **Avg Inference Time**: 13.61s
- **Memory Usage**: 1.53GB

**Ideal Use Cases:**
- Tasks requiring detailed analysis
- When accuracy is more important than speed
- Offline processing scenarios

**Technical Specifications (MLX Version):**
- **Model ID**: `mlx-community/Phi-3.5-vision-instruct-4bit`
- **Quantization**: 4-bit (INT4)
- **Load Time**: ~1.94s
- **Avg. Inference Time**: 13.61s

### 5. LLaVA-v1.6 (MLX-Optimized) (⚠️ Underperforming)

A conversational model that has shown significant performance degradation in recent tests.

**Key Strengths:**
- **Conversational Ability**: Designed for multi-turn dialogue
- **Fast Loading**: 2.77s load time
- **MLX Optimization**: Optimized for Apple Silicon

**Major Limitations:**
- **Performance Degradation**: VQA accuracy dropped from 56% to 34%
- **Model Reloading Issues**: Requires reloading for each image, causing overhead
- **Inconsistent Performance**: Unstable due to state management issues

**VQA 2.0 Performance:**
- **Simple Accuracy**: 30.0% (3/10 correct)
- **VQA Accuracy**: 34.0%
- **Avg Inference Time**: 17.86s
- **Memory Usage**: 1.16GB

**Known Issues:**
- **State Bug**: Model requires reloading for each image to avoid inference failures
- **Performance Impact**: Reloading overhead significantly reduces accuracy
- **Synthetic Image Failures**: Still fails on computer-generated images

**Current Status**: ⚠️ **Functional but not recommended** due to performance issues

**Technical Specifications (MLX Version):**
- **Model ID**: `mlx-community/llava-v1.6-mistral-7b-4bit`
- **Quantization**: 4-bit
- **Load Time**: ~2.77s
- **Avg. Inference Time**: 17.86s

### 6. YOLOv8 (Specialized Object Detection)

A specialized tool for object detection, not a general-purpose VLM.

**Key Strengths:**
- **Real-time Speed**: Can detect objects in video streams with very low latency
- **High Accuracy for Detection**: Excellent at identifying the location of known objects
- **Very Low Resource Requirements**

**Limitations:**
- **Detection Only**: Cannot describe scenes, answer questions, or understand context
- **Fixed Classes**: Can only identify objects from its training data (e.g., the 80 classes in the COCO dataset)

**Ideal Use Cases:**
- As a preliminary step to identify objects before passing them to a VLM
- For tasks where only the location of specific items is needed (e.g., counting objects, tracking tools)

## Performance Recommendations

### For Production Use
1. **Primary Choice**: SmolVLM2-500M-Video-Instruct (best accuracy/speed balance)
2. **Backup Option**: SmolVLM-500M-Instruct (excellent alternative)
3. **Speed Option**: Moondream2 (fastest inference)
4. **⚠️ Avoid**: LLaVA-MLX (underperforming due to reloading overhead)

### For Different Scenarios

#### Quick Testing (10 Questions)
- **Recommended**: Moondream2 (~41 seconds, 56.0% accuracy)

#### Standard Testing (15 Questions)
- **Recommended**: SmolVLM2-500M-Video-Instruct (~98 seconds, 58-66% accuracy)

#### Comprehensive Testing (20 Questions)
- **Speed Priority**: Moondream2 (~74 seconds, 56-60% accuracy)
- **Balance**: SmolVLM2-500M-Video-Instruct (~130 seconds, 58-66% accuracy)

## Testing Methodology

Our VQA 2.0 testing framework evaluates models on:
- **Real COCO Dataset**: Using actual VQA 2.0 questions and images
- **Standardized Evaluation**: VQA 2.0 compliant assessment
- **Performance Metrics**: Both simple accuracy and VQA accuracy
- **Time Analysis**: Comprehensive inference time measurement
- **Memory Usage**: Resource consumption tracking

For detailed test results and time analysis, see `src/testing/vqa_test_result.md`.

---

**Last Updated**: January 2025  
**Test Framework**: VQA 2.0 Standard Evaluation  
**Hardware**: MacBook Air M3, 16GB RAM

For the latest detailed test results and comprehensive performance analysis, see [Test Results Summary](../TEST_RESULTS_SUMMARY.md).
