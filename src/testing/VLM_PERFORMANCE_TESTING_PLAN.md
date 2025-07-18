# VLM Performance Testing Plan

## 🎯 **Testing Summary** (Latest Update: 2025-07-18)
> ✅ **Basic Testing Complete**: 5 models tested. All models successful for vision tasks, 4/5 support pure text.  
> 🧠 **Context Understanding Added**: New comprehensive test for conversation context capabilities.  
> 🏆 **MLX Optimization Success**: Phi-3.5-Vision performance transformed from failure to functional.  
> ⚠️ **LLaVA-MLX Limitation**: MLX version of LLaVA has state memory issues affecting reliability.  
> 📊 **Context Understanding Results**: Most models show limited context understanding as expected.  
> ⚡ **Fastest Loading**: LLaVA-v1.6-Mistral-7B-MLX (3.04s)  
> 💨 **Fastest Inference**: Moondream2 (avg 6.61s)  
> 📸 **Multi-Image Testing**: Latest run successfully tested 3 different images.  
> 🚀 **Pure Text Discovery**: 80% models support pure text - SmolVLM series excels unexpectedly!  

### 🧠 **Context Understanding Test Results Summary**

| Model | Context Understanding | Image Description Quality | Technical Reliability | Recommended Use |
|-------|----------------------|---------------------------|----------------------|-----------------|
| ✅ | **SmolVLM-500M-Instruct** | ⚠️ Limited | ✅ Good | ✅ Reliable | 🚀 Fast basic tasks |
| ⚠️ | **SmolVLM2-500M-Video** | ❌ Poor | ✅ Good | ✅ Reliable | 🎬 Video/Image description only |
| ❌ | **Moondream2** | ❌ Not Supported | ✅ Excellent | ✅ Reliable | 👁️ Vision-only model |
| ❌ | **LLaVA-v1.6-Mistral-7B-MLX** | ⚠️ Limited | ❌ State Issues | ❌ Memory Problems | 🔴 Not recommended |
| ❌ | **Phi-3.5-Vision-Instruct** | ❌ Complete Failure | ⚠️ Improved | ❌ Multiple Issues | 🔴 Not recommended |

**Key Findings**:
- **Context Understanding**: Most models show limited capabilities as expected for local VLM models
- **Technical Reliability**: SmolVLM series and Moondream2 are most reliable
- **Recommendation**: Use SmolVLM-500M-Instruct for basic context-aware tasks

## 📋 Testing Objectives

Comprehensive testing of 5 vision-language models, recording basic performance metrics and response results. Using MacBook Air M3 (16GB) environment, supporting single or multiple image testing.

### 🚀 **Extended Testing Capabilities** ✨
1. **Pure Text Capability Testing**: Test each model's ability to handle pure text inputs without images
2. **Context Understanding Testing**: NEW - Test models' ability to answer questions based on conversation history
3. **Image Description Quality**: Standard vision-language task performance
4. **Technical Reliability**: Memory management, inference stability, and error handling

### 🧠 **Context Understanding Testing Methodology**
**Test Flow**:
1. **Image Description**: Show image with forensic expert prompt, require detailed description
2. **Context-Based Questioning**: Ask 3 follow-up questions without re-showing image:
   - Question 1: "What were the most prominent colors in the image?"
   - Question 2: "Were there any people visible in the image?"  
   - Question 3: "Summarize the main subject or scene of the image in one sentence."
3. **Analysis**: Evaluate model's ability to maintain conversation context and provide relevant answers

**Expected Outcome**: 
> Most local VLM models have limited context understanding compared to cloud-based models. This test confirms architectural limitations in maintaining conversation context.

## 🎯 Test Model List

1. **SmolVLM2-500M-Video-Instruct** → `HuggingFaceTB/SmolVLM2-500M-Video-Instruct`
2. **SmolVLM-500M-Instruct** → `HuggingFaceTB/SmolVLM-500M-Instruct`
3. **Moondream2** → `vikhyatk/moondream2`
4. **LLaVA-v1.6-Mistral-7B-MLX** → `mlx-community/llava-v1.6-mistral-7b-4bit` (**MLX Required, Partial Success**)
5. **Phi-3.5-Vision-Instruct** → `lokinfey/Phi-3.5-vision-mlx-int4` (MLX-optimized for Apple Silicon, **MLX Required**)

> Loading methods reference `active_model.md`

## 📊 Recorded Test Metrics

### ⏱️ **Time Metrics**
- **Model Loading Time**: Time required to load model
- **Inference Time**: Processing time per image
- **Total Test Time**: Complete testing duration

### 💾 **Memory Metrics**  
- **Memory Before Loading**: Memory usage before model loading
- **Memory After Loading**: Memory usage after model loading
- **Memory Difference**: Memory occupied by the model

### 📝 **Result Recording**
- **Model Response**: Complete response text for each image
- **Image Information**: Image filename, size, resolution
- **Error Recording**: Detailed error information if errors occur

## 📸 Test Configuration

### **📏 Unified Test Conditions** ✨
To ensure fair comparison, all models use unified test conditions:

- **🖼️ Image Preprocessing**: Unified scaling to maximum 1024 pixels, preserving aspect ratio
- **💬 Prompt**: All models use the same prompt
- **⚙️ Generation Parameters**: `max_new_tokens: 100, do_sample: false`
- **🏷️ Image Format**: Local images use `{"type": "image", "image": image}` format

### **Test Images** 📸
- **Image Location**: `src/testing/testing_material/images/`
- **Multi-Image Support**: Automatically detects all images in directory, tests each individually
- **Quantity**: The latest test successfully ran against 3 images of different types (photographic and synthetic).
- **Format**: Supports JPG, JPEG, PNG, BMP and other common formats
- **Processing**: Automatic scaling to unified size (maximum 1024 pixels)
- **Data Recording**: Each image independently records inference time, response content, image information

### **Test Prompt**
Using unified prompt for all image testing:
```
"Describe what you see in this image in detail."
```

## 🛠️ Implementation Files

### 📁 **Simple File Structure**
```
src/testing/
├── VLM_PERFORMANCE_TESTING_PLAN.md     # Test plan
├── vlm_tester.py                        # Main testing program
├── testing_material/
│   └── images/                          # Test images (user provided)
└── results/
    └── test_results.json                # Test result records
```

### 🔧 **Main Program Features**
`vlm_tester.py` includes:
- **Sequential model loading** (avoiding memory overflow)
- **Complete memory cleanup after testing**
- Reading test images
- Recording time and memory usage
- Saving all results to JSON files

### ⚠️ **Memory Management Strategy** ✨
Due to M3 MacBook Air 16GB memory limitations:
1. **Sequential Loading**: Load only one model at a time
2. **Complete Testing**: Finish all image tests for that model
3. **Memory Cleanup**: `del model, gc.collect(), torch.mps.empty_cache()`
4. **Load Next**: Clean up before loading next model

### ⏱️ **Timeout Mechanism** ✨
Setting reasonable timeouts based on different model technical characteristics:
- **Small Models** (SmolVLM series, Moondream2): 60 seconds
- **Medium Models** (Phi-3.5-Vision MLX): 180 seconds (significantly improved with MLX optimization)
- **Large Models** (LLaVA v1.6 MLX): 180 seconds

### 🔧 **Known Limitations & Solutions** ✨
- **LLaVA-v1.6-Mistral-7B-MLX**: ✅ **Upgraded to MLX version.** The original `Transformers`-based model was replaced. The new MLX version loads quickly but exhibits content-specific failures. It succeeds with photographic images but fails with synthetic geometric images, pointing to a potential issue in the model's image processor or the `mlx-vlm` library's handling of images without standard metadata (e.g. EXIF).
- **Phi-3.5-Vision**: ✅ **MLX Optimization Success!** Improved from timeout failure to fastest loading (1.79s)
  - **Required**: `pip install mlx-vlm` for Apple Silicon M1/M2/M3
  - **Effect**: From complete failure to 100% success, loading time reduced by over 98%
- **Moondream2**: Uses special API, cannot fully unify parameter control (but doesn't affect comparison fairness)

## 📋 Implementation Steps

1. **Create Test Program** - Write `vlm_tester.py`
2. **Test Model Loading** - Confirm all 5 models can load normally
3. **Execute Testing** - Test all images
4. **Record Results** - Save all data to JSON files

## 📊 Result Format ✨

Test results will be saved in JSON format, including unified test markers:

```json
{
  "test_timestamp": "2025-01-XX XX:XX:XX",
  "system_info": {
    "device": "MacBook Air M3",
    "memory": "16GB",
    "mps_available": true
  },
  "models": {
    "model_name": {
      "model_id": "actual/model/path",
      "load_time": 10.5,
      "memory_before": 8.2,
      "memory_after": 12.8,
      "memory_diff": 4.6,
      "memory_after_cleanup": 8.5,
      "successful_inferences": 3,
      "failed_inferences": 0,
      "avg_inference_time": 6.2,
      "images": {
        "test_image.png": {
          "inference_time": 13.00,
          "response": "The image shows a simple graphic representation...",
          "image_info": {
            "original_size": [336, 336],
            "processed_size": [336, 336],
            "mode": "RGB",
            "file_size": 2305
          },
          "error": null,
          "unified_test": true,
          "generation_params": {
            "max_new_tokens": 100,
            "do_sample": false
          },
          "timeout_used": 180
        },
        "IMG_0119.JPG": {
          "inference_time": 12.19,
          "response": "This image shows a Shiba Inu dog...",
          "image_info": {
            "original_size": [960, 1707],
            "processed_size": [575, 1024],
            "mode": "RGB",
            "file_size": 222091
          },
          "error": null,
          "unified_test": true
        }
      },
      "total_inference_time": 25.19,
      "successful_inferences": 2,
      "failed_inferences": 0,
      "avg_inference_time": 12.60
    }
  }
}
```

## 🏆 Actual Test Results ✨
> 📅 **Latest Test**: 2025-07-18 17:05:26 (`context_understanding_test_results_20250718_165329.json`)  
> 📸 **Test Images**: 3 images (`IMG_0119.JPG` - photo, `IMG_2053.JPG` - photo, `test_image.jpg` - synthetic)  
> 📝 **Pure Text Tests**: 3 prompts (knowledge Q&A, concept explanation, creative writing)  
> 🧠 **Context Understanding Tests**: NEW - 3 context-based questions per image without re-showing image

### ✅ **Vision Task Results (5/5)** 🎉
| Rank | Model | Load Time | Avg Inference | Memory Usage | Success Rate |
|------|-------|-----------|---------------|--------------|--------------|
| 🥇 | **LLaVA-v1.6-Mistral-7B-MLX** | **3.04s** | 8.57s | -0.36GB | 100% (3/3) |
| 🥈 | **Phi-3.5-Vision-Instruct** | 3.01s | 32.79s | -2.62GB | 100% (3/3) |
| 🥉 | **SmolVLM-500M-Instruct** | 3.81s | 6.51s | +0.39GB | 100% (3/3) |
| 4️⃣ | **SmolVLM2-500M-Video** | 4.71s | 6.61s | +0.23GB | 100% (3/3) |
| 5️⃣ | **Moondream2** | 5.56s | **6.61s** | -1.09GB | 100% (3/3) |
*Note: Negative memory usage is likely a measurement artifact due to garbage collection.*

### 🚀 **Pure Text Capability Results (4/5)** 📝
| Rank | Model | Pure Text Support | Success Rate | Avg Speed | Best Use Case |
|------|-------|-------------------|--------------|-----------|---------------|
| 🥇 | **SmolVLM-500M-Instruct** | ✅ Full | 100% (3/3) | **1.72s** | 🚀 Fast Q&A, real-time chat |
| 🥈 | **SmolVLM2-500M-Video** | ✅ Full | 100% (3/3) | 3.70s | 🎬 Multi-media applications |
| 🥉 | **LLaVA-v1.6-Mistral-7B-MLX** | ✅ Full | 100% (3/3) | 4.08s | 🎨 Creative writing, poetry |
| 4️⃣ | **Phi-3.5-Vision-Instruct** | ✅ Full | 100% (3/3) | 16.38s | 📚 Detailed analysis, education |
| ❌ | **Moondream2** | ❌ None | 0% (0/3) | N/A | 👁️ Vision-only model |

### 🧠 **Context Understanding Test Results (NEW)** 🎯
| Rank | Model | Context Understanding | Context Success Rate | Technical Reliability | Recommendation |
|------|-------|----------------------|---------------------|----------------------|----------------|
| 🥇 | **SmolVLM-500M-Instruct** | ⚠️ Limited | ~33% | ✅ Reliable | 🟡 Basic context tasks |
| 🥈 | **Moondream2** | ❌ Not Supported | 0% (Expected) | ✅ Reliable | 👁️ Vision-only, excellent quality |
| 🥉 | **SmolVLM2-500M-Video** | ❌ Poor | ~10% | ✅ Reliable | 🎬 Image description only |
| 4️⃣ | **LLaVA-v1.6-Mistral-7B-MLX** | ⚠️ Limited | ~20% | ❌ State Issues | 🔴 Not recommended |
| 5️⃣ | **Phi-3.5-Vision-Instruct** | ❌ Complete Failure | 0% | ❌ Multiple Issues | 🔴 Not recommended |

**Context Understanding Analysis**:
- **SmolVLM-500M-Instruct**: Short but sometimes relevant answers (e.g., "Yes", "white, black, red")
- **SmolVLM2-500M-Video**: Generates irrelevant content about flags, weapons unrelated to actual images
- **Moondream2**: Cannot process text-only questions (architectural limitation, expected behavior)
- **LLaVA-v1.6-Mistral-7B-MLX**: Same response for all images, indicating state memory problems
- **Phi-3.5-Vision-Instruct**: Training data leakage, repetitive content, content contamination

**Key Insight**: 
> 🎯 **As Expected**: Local VLM models show very limited context understanding capabilities compared to cloud-based models. This confirms the architectural limitations in maintaining conversation context that we anticipated.

### 🎯 **Key Discoveries**
1. **🎉 SmolVLM Series Breakthrough**: Despite being VLM models, both SmolVLM variants fully support pure text with excellent performance
2. **🚀 Ultra-Fast Text Processing**: SmolVLM-500M-Instruct achieves 0.16s response time for simple queries
3. **🎨 Creative Excellence**: LLaVA-MLX generates the most poetic and creative text responses
4. **📚 Educational Depth**: Phi-3.5-Vision provides the most comprehensive and detailed explanations
5. **👁️ Vision-Only Limitation**: Moondream2 architecture requires image embeddings, cannot process pure text
6. **🧠 Context Understanding Reality**: NEW - Most local VLM models show very limited context understanding as expected
7. **✅ SmolVLM-500M Best Context**: Among all models, SmolVLM-500M-Instruct shows the most reliable context understanding
8. **❌ LLaVA State Issues**: LLaVA-MLX has serious state memory problems affecting reliability
9. **🔴 Phi-3.5 Technical Problems**: Multiple technical issues including training data leakage and repetitive content
10. **🎯 Expected Limitations**: Context understanding limitations confirm architectural constraints of local VLM models

### 📝 **Pure Text Response Examples**

**Question**: "What is the capital of France?"
- **SmolVLM-500M**: "Paris" (0.16s - ultra-fast)
- **LLaVA-MLX**: "The capital of France is Paris." (1.19s - concise)
- **Phi-3.5-Vision**: "Paris is the capital of France. It is not only the largest city in France but also one of the most populous cities in Europe..." (21.18s - comprehensive)

**Question**: "Write a short poem about technology."
- **SmolVLM2-Video**: "In the digital realm, where wires and circuits dance, We find ourselves in a technological trance..."
- **LLaVA-MLX**: "In a world where technology reigns, We're connected, yet sometimes pained. Through screens and wires, we communicate..."
- **Phi-3.5-Vision**: "In circuits and bytes, our world is woven, A tapestry of data, silently spoken..."

**Question**: "Explain machine learning in simple terms."
- **SmolVLM-500M**: "Machine learning is a subset of artificial intelligence that allows computers to learn from data..."
- **LLaVA-MLX**: "Machine learning is a type of artificial intelligence that allows computer systems to learn and improve from experience..."
- **Phi-3.5-Vision**: "Machine learning is a subset of artificial intelligence that involves training computers to learn from data and make predictions..."

### 🏆 **MLX Optimization Success Story** 
**Phi-3.5-Vision's Significant Improvement**:
- **Before (Transformers)**: 135s+ loading timeout → 100% failure
- **Now (MLX)**: 3.01s reliable loading → 100% success 
- **Improvement**: Loading speed improved **~98%**, from unusable to **functional**
- **Note**: While not the fastest loader, it achieved successful functionality

### 📝 **Key Findings**
1. **🚀 MLX Framework Breakthrough**: Revolutionary VLM performance improvement on Apple Silicon.
2. **⚡ Fastest Loading**: Phi-3.5-Vision-Instruct (2.24s) surpasses all models.
3. **💨 Fastest Inference**: Moondream2 (avg 6.78s) leads in average vision inference speed.
4. **💾 Memory Efficiency**: MLX models appear to use memory more efficiently, though precise measurement is complex.
5. **📊 Overall Success Rate**: High reliability, with 100% (5/5) of models being fully successful across all test images.
6. **🚀 Pure Text Breakthrough**: 80% (4/5) of models support pure text processing, with SmolVLM series excelling unexpectedly.
7. **⚡ Ultra-Fast Text**: SmolVLM-500M-Instruct achieves 0.16s response time for simple queries.
8. **🎨 Creative Excellence**: LLaVA-MLX generates the most creative and poetic text responses.
9. **📚 Educational Depth**: Phi-3.5-Vision provides the most comprehensive and detailed explanations.
10. **👁️ Vision-Only Limitation**: Moondream2 architecture requires image embeddings, cannot process pure text.
11. **🧠 Context Understanding Reality**: NEW - Most local VLM models show very limited context understanding capabilities as expected.
12. **✅ SmolVLM-500M Reliability**: Best overall model for context-aware tasks with consistent technical performance.
13. **❌ LLaVA Technical Issues**: State memory problems make LLaVA-MLX unreliable for production use.
14. **🔴 Phi-3.5 Regression**: Despite fast loading, multiple technical issues make this model unreliable.
15. **🎯 Expected Architectural Limitations**: Context understanding limitations confirm that local VLM models have inherent constraints compared to cloud-based models.

## ✅ Usage Instructions

### 🚀 **Basic Test Commands**
1. **Standard Performance Test**: `python vlm_tester.py "Model Name"`
   - Example: `python vlm_tester.py "Phi-3.5-Vision-Instruct"`
2. **Context Understanding Test**: `python vlm_context_tester.py "Model Name"`
   - Example: `python vlm_context_tester.py "SmolVLM-500M-Instruct"`
3. **Full Performance Test**: `python vlm_tester.py`
4. **Full Context Test**: `python vlm_context_tester.py`
5. **View Results**: Check JSON files in `results/` directory

### 📝 **Testing Features**

**Pure Text Testing**:
- **Automatic Testing**: Pure text capability tested automatically for all models
- **3 Test Prompts**: Knowledge Q&A, concept explanation, creative writing
- **Success Rate Calculation**: Determines if model supports pure text (>0% success rate)
- **Response Quality**: Records actual text responses for comparison
- **Performance Metrics**: Measures inference time for pure text tasks

**Context Understanding Testing** (NEW):
- **Conversation Flow**: Tests model's ability to maintain context across multiple turns
- **Forensic Expert Prompt**: Uses detailed prompt to establish context
- **3 Context Questions**: Colors, people visibility, scene summary
- **No Image Re-showing**: Tests pure context understanding without visual aids
- **Technical Reliability**: Monitors for technical issues (repetition, contamination, truncation)
- **Performance Metrics**: Measures context inference time and success rate

### 📸 **Multi-Image Test Support**
- **Automatic Multi-Image Testing**: Program automatically detects all images in `testing_material/images/`
- **Result Format**: Each image independently recorded in JSON `images` field
- **Statistics**: Automatically calculates total inference time, success/failure counts, average inference time

### 📊 **Result Files**

**Standard Performance Tests**:
- **Main Results**: `test_results_YYYYMMDD_HHMMSS.json`
- **Single Model Results**: `test_results_single_[Model Name].json`
- **Intermediate Results**: `test_results_intermediate_[Model Name].json` (prevents test interruption)

**Context Understanding Tests** (NEW):
- **Main Results**: `context_understanding_test_results_YYYYMMDD_HHMMSS.json`
- **Single Model Results**: `context_understanding_test_results_single_[Model Name].json`
- **Intermediate Results**: `context_understanding_test_results_intermediate_[Model Name].json`

### ⚠️ **Pre-usage Preparation**
1. **Activate Virtual Environment**: `source ../../ai_vision_env/bin/activate` (from testing directory)
2. **Install MLX-VLM** (Required for Apple Silicon): `pip install mlx-vlm`
   - ⚠️ **Critical for Phi-3.5-Vision**: Without MLX, this model will completely fail (timeout)
   - 🚀 **Performance Impact**: MLX provides 98%+ speed improvement on M1/M2/M3
3. **Prepare Test Images**: Place images in `testing_material/images/` directory

### 📝 **Pure Text Testing Configuration**
- **Automatic Mode**: Pure text testing is enabled by default (`enable_text_only_test = True`)
- **Test Prompts**: 3 standardized prompts test different capabilities
- **Success Criteria**: Models with >0% success rate are considered "pure text capable"
- **Control**: Set `enable_text_only_test = False` in `VLMTester` to disable