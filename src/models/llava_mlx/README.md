# LLaVA MLX Model

A high-performance multimodal vision-language model optimized for Apple Silicon using MLX framework with INT4 quantization for efficient inference.

**⚠️ CRITICAL STATUS UPDATE**: LLaVA-MLX has significant performance issues and is NOT recommended for production use. See performance analysis below.

## 🎯 Model Overview

LLaVA MLX provides state-of-the-art vision-language understanding capabilities with Apple Silicon optimization. This implementation uses the MLX framework for superior performance on M1/M2/M3 chips with quantized weights for memory efficiency.

**Latest Performance Status (2025-08-01):**
- **VQA Accuracy**: 21.0% (critical performance issue)
- **Simple Accuracy**: 20.0% (critical performance issue)
- **Average Inference Time**: 19.02s (improved from 24.15s with enhanced memory management)
- **Load Time**: 2.01s
- **Memory Usage**: -1.47GB (memory efficient but performance poor)

## ⚠️ Critical Performance Issues

### **🚨 Production Recommendation: AVOID**
LLaVA-MLX has critical performance issues that make it unsuitable for production use:

1. **Extremely Slow Inference**: 19.02s average (5-6x slower than other models)
2. **Poor Accuracy**: Only 20.0% simple accuracy, 21.0% VQA accuracy
3. **Batch Processing Issues**: Model state corruption after first inference
4. **Repetitive Responses**: Verbose, repetitive responses with self-questioning loops
5. **Technical Errors**: "input operand has more dimensions than allowed by the axis remapping"

### **Enhanced Memory Management Results**
- **✅ Successfully Implemented**: Periodic memory cleanup, adaptive pressure detection
- **Performance Improvement**: Inference time improved from 24.15s to 19.02s (21% improvement)
- **Memory Stability**: No memory errors during testing
- **Workaround**: Model reloading required for each image (implemented)

## ⚠️ Requirements

### Hardware Requirements
- **Apple Silicon (M1/M2/M3) REQUIRED** - This model will not run on Intel or other architectures
- **Minimum 16GB RAM** recommended for stable operation
- **macOS Monterey 12.0+** for optimal MLX performance

### Software Requirements
- **MLX-VLM package** - Core MLX vision-language model support
- **MLX Framework** - Apple's machine learning framework
- **Python 3.9+** - Required for MLX compatibility

## 📁 File Structure

### Core Implementation
- **`run_llava_mlx.py`** - Flask server with OpenAI-compatible API endpoints
- **`llava_mlx_model.py`** - Core model class with MLX inference optimization and enhanced memory management
- **`src/config/model_configs/llava_mlx.json`** - Complete model configuration

### Documentation
- **`README.md`** - This comprehensive guide
- **Testing logs** - Available in `../../logs/` directory

## 🚀 Quick Start

### 1. Installation

```bash
# Activate your virtual environment
source ai_vision_env/bin/activate

# Install MLX-VLM and dependencies
pip install mlx-vlm>=0.0.9
pip install mlx>=0.11.0

# Install Flask for the server
pip install Flask>=2.3.0
pip install Pillow>=9.0.0
```

### 2. Verify MLX Installation

```bash
# Test MLX availability
python -c "import mlx.core as mx; print('MLX available:', mx.default_device())"

# Test MLX-VLM installation
python -c "import mlx_vlm; print('MLX-VLM version:', mlx_vlm.__version__)"
```

### 3. Start the Server

```bash
# Navigate to LLaVA MLX directory
cd src/models/llava_mlx

# Run the server
python run_llava_mlx.py
```

The server will start on **port 8080** by default.

### 4. Verify Server Status

```bash
# Health check
curl http://localhost:8080/health

# Expected response: {"status": "healthy", "model": "LLaVA-MLX", ...}
```

## ⚙️ Configuration

### Model Configuration
Located at: `src/config/model_configs/llava_mlx.json`

Key configuration options:
```json
{
  "model_name": "LLaVA-MLX",
  "model_id": "mlx-community/llava-v1.6-mistral-7b-4bit",
  "device": "mps",
  "quantization": "int4",
  "max_tokens": 150,
  "image_processing": {
    "max_size": 1024,
    "min_size": 224,
    "format": "RGB",
    "quality": 95
  },
  "enhanced_memory_management": {
    "periodic_cleanup": true,
    "cleanup_interval": 1,
    "adaptive_pressure_detection": true
  }
}
```

## 🔍 Performance Analysis

### **Latest Test Results (2025-08-01)**

**VQA 2.0 Performance (20 Questions - COCO val2014):**
- **VQA Accuracy**: 21.0% (lowest among all models)
- **Simple Accuracy**: 20.0% (4/20 correct)
- **Average Inference Time**: 19.02s (improved from 24.15s)
- **Load Time**: 2.01s
- **Memory Usage**: -1.47GB (memory efficient)

**Context Understanding Performance:**
- **Context Understanding**: 0% (universal failure across all models)
- **Failure Type**: Hallucinated responses
- **Specific Issues**: Claims "white and black" for all images, generic template responses

### **Performance Comparison**

| Model | VQA Accuracy | Simple Accuracy | Avg Time | Status |
|-------|:------------:|:---------------:|:--------:|:------:|
| **Moondream2** | 🥇 **62.5%** | 🥇 **65.0%** | 7.80s | 🥇 **Best Overall** |
| **SmolVLM2** | 🥈 57.5% | 🥈 60.0% | 6.45s | 🥈 **Balanced** |
| **Phi-3.5-Vision** | 🥉 35.0% | 35.0% | 8.71s | 🥉 **Detailed** |
| **SmolVLM** | 36.0% | 35.0% | ⚡ **0.34s** | ⚡ **Fastest** |
| **LLaVA-MLX** | ⚠️ 21.0% | ⚠️ 20.0% | 🐌 19.02s | 🚫 **Critical Issues** |

### **Critical Issues Identified**

1. **Extremely Slow Inference**: 19.02s average (5-6x slower than other models)
2. **Poor Accuracy**: Only 20.0% simple accuracy, 21.0% VQA accuracy
3. **Batch Processing Failures**: Model state corruption after first inference
4. **Repetitive Response Loops**: "Is it morning? Yes. Is it afternoon? No..." patterns
5. **Technical Errors**: "input operand has more dimensions than allowed by the axis remapping"
6. **Context Understanding**: 0% capability (hallucinated responses)

## 🔧 Enhanced Memory Management

### **Successfully Implemented Features**
- **Periodic Memory Cleanup**: Every inference for MLX models
- **Adaptive Memory Pressure Detection**: Aggressive cleanup when memory usage >80%
- **MLX-Specific Memory Clearing**: `clear_mlx_memory()` function with Metal GPU cache clearing
- **Memory Monitoring**: Real-time memory pressure detection and response

### **Performance Improvements**
- **Inference Time**: Improved from 24.15s to 19.02s (21% improvement)
- **Memory Stability**: No memory errors during testing
- **Model Reloading**: Automatic model reloading after each inference to prevent state corruption

## 🚫 Production Recommendations

### **❌ NOT Recommended for Any Production Use**

**Critical Issues:**
- Very slow inference (19.02s)
- Poor accuracy (20.0% simple, 21.0% VQA)
- Technical problems with batch processing
- Repetitive response loops
- Model state corruption issues

### **Alternative Recommendations**

**For High Accuracy:**
- **Use Moondream2** (65.0% accuracy, 7.80s inference)

**For Real-Time Applications:**
- **Use SmolVLM-GGUF** (0.34s inference, 35.0% accuracy)

**For Balanced Performance:**
- **Use SmolVLM2-MLX** (60.0% accuracy, 6.45s inference)

## 🔍 Testing and Validation

### Test Results Summary
Based on comprehensive testing (see `../../logs/` for detailed results):

- **❌ VQA Performance**: Critical performance issues (21.0% accuracy)
- **❌ Inference Speed**: Extremely slow (19.02s average)
- **❌ Context Understanding**: 0% capability (hallucinated responses)
- **✅ Memory Management**: Enhanced memory management successfully implemented
- **⚠️ Technical Issues**: Batch processing failures, state corruption

### Performance Benchmarks (Updated 2025-08-01)
- **Average Inference Time**: 19.02s (improved from 24.15s)
- **VQA Accuracy**: 21.0% (critical issue)
- **Simple Accuracy**: 20.0% (critical issue)
- **Load Time**: 2.01s
- **Memory Usage**: -1.47GB (memory efficient)
- **Success Rate**: 20% on VQA questions, 0% on context understanding

## 🔧 Advanced Configuration

### Enhanced Memory Management
```json
{
  "enhanced_memory_management": {
    "periodic_cleanup": true,
    "cleanup_interval": 1,
    "adaptive_pressure_detection": true,
    "mlx_memory_clearing": true,
    "model_reloading": true
  }
}
```

### Memory Optimization
```json
{
  "mlx_config": {
    "memory_pool_size": "8GB",
    "cache_size": 512,
    "batch_size": 1
  }
}
```

### Image Processing Tuning
```json
{
  "image_processing": {
    "max_size": 768,
    "preprocessing_quality": "high",
    "maintain_aspect_ratio": true,
    "padding_color": [255, 255, 255]
  }
}
```

## 📚 Additional Resources

- **[MLX-VLM Documentation](https://github.com/Blaizzy/mlx-vlm)** - Official MLX-VLM documentation
- **[LLaVA Project](https://llava-vl.github.io/)** - Original LLaVA research project
- **[MLX Framework](https://ml-explore.github.io/mlx/)** - Apple's MLX machine learning framework
- **[Model Card](https://huggingface.co/mlx-community/llava-v1.6-mistral-7b-4bit)** - Hugging Face model documentation
- **[System Architecture](../../docs/ARCHITECTURE.md)** - Overall system design
- **[Performance Benchmarks](../../logs/)** - Detailed testing results
- **[VQA Analysis Report](../../testing/reports/vqa_analysis.md)** - VQA 2.0 analysis
- **[Model Performance Guide](../../testing/reports/model_performance_guide.md)** - Production recommendations

---

**Status**: 🚫 **Critical Issues** | **Recommended**: ❌ **NOT for Production** | **Last Updated**: 2025-08-01

**⚠️ Performance Crisis**: LLaVA-MLX has critical performance issues (19.02s inference, 20.0% accuracy) and is NOT recommended for any use case. Enhanced memory management provides 21% improvement but doesn't solve core performance problems.

**Production Alternatives:**
- **High Accuracy**: Use Moondream2 (65.0% accuracy, 7.80s inference)
- **Real-Time**: Use SmolVLM-GGUF (0.34s inference, 35.0% accuracy)
- **Balanced**: Use SmolVLM2-MLX (60.0% accuracy, 6.45s inference)