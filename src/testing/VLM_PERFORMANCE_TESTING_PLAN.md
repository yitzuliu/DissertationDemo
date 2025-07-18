# VLM Performance Testing Plan

## 📊 **Quick Summary** (2025-07-18)

### 🏆 **Performance Rankings**
| Rank | Model | Load Time | Inference | Vision | Text | Context | Status |
|------|-------|-----------|-----------|--------|------|---------|--------|
| 🥇 | **SmolVLM-500M-Instruct** | 3.81s | 6.51s | ✅ 100% | ✅ 100% | ⚠️ 33% | ✅ Reliable |
| 🥈 | **LLaVA-v1.6-Mistral-7B-MLX** | 3.04s | 8.57s | ✅ 100% | ✅ 100% | ⚠️ 20% | ⚠️ State Issues |
| 🥉 | **SmolVLM2-500M-Video** | 4.71s | 6.61s | ✅ 100% | ✅ 100% | ❌ 10% | ✅ Reliable |
| 4️⃣ | **Moondream2** | 5.56s | 6.61s | ✅ 100% | ❌ 0% | ❌ 0% | ✅ Vision-Only |
| 5️⃣ | **Phi-3.5-Vision-Instruct** | 3.01s | 32.79s | ✅ 100% | ✅ 100% | ❌ 0% | ❌ Multiple Issues |

### 🎯 **Key Findings**
- **Vision Tasks**: All 5 models successful (100% success rate)
- **Pure Text**: 4/5 models support (80% success rate)
- **Context Understanding**: Limited capabilities as expected
- **MLX Optimization**: Critical for Apple Silicon performance

## 🎯 **Testing Objectives**

### **Core Capabilities Tested**
1. **Vision-Language Tasks**: Image description and analysis
2. **Pure Text Processing**: Knowledge Q&A, explanations, creative writing
3. **Context Understanding**: Conversation memory across multiple turns
4. **Technical Reliability**: Memory management, error handling

### **Test Environment**
- **Hardware**: MacBook Air M3 (16GB RAM)
- **Images**: 3 test images (photographic + synthetic)
- **Parameters**: Unified `max_new_tokens=100, do_sample=false`

## 🧠 **Context Understanding Test**

### **Methodology**
1. **Image Description**: Show image with detailed prompt
2. **Context Questions** (without re-showing image):
   - "What were the most prominent colors?"
   - "Were there any people visible?"
   - "Summarize the main scene in one sentence"

### **Results Analysis**
- **Expected Outcome**: Limited context understanding (confirmed)
- **Best Performer**: SmolVLM-500M-Instruct (~33% success)
- **Architectural Limitation**: Most local VLM models lack conversation memory

## 🎯 **Test Models**

| Model | HuggingFace ID | Framework | Special Requirements |
|-------|----------------|-----------|---------------------|
| **SmolVLM2-500M-Video** | `HuggingFaceTB/SmolVLM2-500M-Video-Instruct` | Transformers | None |
| **SmolVLM-500M-Instruct** | `HuggingFaceTB/SmolVLM-500M-Instruct` | Transformers | None |
| **Moondream2** | `vikhyatk/moondream2` | Transformers | Special API |
| **LLaVA-v1.6-Mistral-7B-MLX** | `mlx-community/llava-v1.6-mistral-7b-4bit` | MLX | `pip install mlx-vlm` |
| **Phi-3.5-Vision-Instruct** | `lokinfey/Phi-3.5-vision-mlx-int4` | MLX | `pip install mlx-vlm` |

## 📊 **Test Configuration**

### **Unified Test Conditions**
- **Image Preprocessing**: Max 1024px, aspect ratio preserved
- **Prompt**: "Describe what you see in this image in detail."
- **Generation**: `max_new_tokens=100, do_sample=false`
- **Image Format**: Local images with unified preprocessing

### **Test Images**
- **Location**: `src/testing/testing_material/images/`
- **Support**: JPG, JPEG, PNG, BMP
- **Processing**: Automatic multi-image detection and testing

## 🛠️ **Implementation**

### **File Structure**
```
src/testing/
├── VLM_PERFORMANCE_TESTING_PLAN.md
├── vlm_tester.py                    # Main testing program
├── vlm_context_tester.py            # Context understanding tests
├── testing_material/images/         # Test images
└── results/                         # JSON result files
```

### **Memory Management**
- **Sequential Loading**: One model at a time
- **Complete Cleanup**: `del model, gc.collect(), torch.mps.empty_cache()`
- **Timeout Settings**: 60s (small), 180s (large models)

### **Known Issues & Solutions**
- **LLaVA-MLX**: Synthetic image processing bug → Exclusion list implemented
- **Phi-3.5-Vision**: MLX required for Apple Silicon → 98% speed improvement
- **Moondream2**: Special API required → Cannot unify parameters

## 📊 **Result Format**

### **JSON Structure**
```json
{
  "test_timestamp": "2025-07-18 17:05:26",
  "system_info": {
    "device": "MacBook Air M3",
    "memory": "16GB"
  },
  "models": {
    "model_name": {
      "load_time": 3.81,
      "memory_diff": 0.39,
      "successful_inferences": 3,
      "avg_inference_time": 6.51,
      "images": {
        "image_name.jpg": {
          "inference_time": 6.51,
          "response": "Image description...",
          "error": null
        }
      }
    }
  }
}
```

## 🚀 **Usage Instructions**

### **Quick Commands**
```bash
# Activate environment
source ../../ai_vision_env/bin/activate

# Install MLX (required for Apple Silicon)
pip install mlx-vlm

# Run tests
python vlm_tester.py                    # Full performance test
python vlm_tester.py "Model Name"       # Single model test
python vlm_context_tester.py            # Context understanding test
```

### **Test Features**
- **Automatic Multi-Image**: Detects all images in directory
- **Pure Text Testing**: 3 standardized prompts per model
- **Context Understanding**: Conversation flow testing
- **Result Files**: Timestamped JSON with intermediate saves

### **Result Files**
- **Performance**: `test_results_YYYYMMDD_HHMMSS.json`
- **Context**: `context_understanding_test_results_YYYYMMDD_HHMMSS.json`
- **Single Model**: `test_results_single_[Model].json`

## 🎯 **Key Discoveries**

### **Performance Highlights**
- **Fastest Loading**: LLaVA-MLX (3.04s)
- **Fastest Inference**: Moondream2 (6.61s avg)
- **Best Text Model**: SmolVLM-500M-Instruct (1.72s avg)
- **Most Reliable**: SmolVLM series

### **Technical Insights**
- **MLX Breakthrough**: 98%+ speed improvement on Apple Silicon
- **Pure Text Surprise**: 80% of VLM models support text-only tasks
- **Context Reality**: Limited capabilities confirm architectural constraints
- **Memory Efficiency**: MLX models use memory more efficiently

### **Recommendations**
- **General Use**: SmolVLM-500M-Instruct (balanced performance)
- **Fast Q&A**: SmolVLM-500M-Instruct (ultra-fast text)
- **Creative Writing**: LLaVA-MLX (poetic responses)
- **Educational**: Phi-3.5-Vision (detailed explanations)
- **Vision-Only**: Moondream2 (excellent image quality)
- **Avoid**: LLaVA-MLX (state issues), Phi-3.5-Vision (technical problems)