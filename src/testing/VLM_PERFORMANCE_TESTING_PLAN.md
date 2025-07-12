# VLM Performance Testing Plan

## 🎯 **Testing Summary** (Latest Update)
> ✅ **Testing Complete**: 5 models tested. 4 fully successful, 1 partially successful.  
> 🏆 **MLX Optimization Success**: Phi-3.5-Vision performance transformed from failure to the top performer.  
> ⚠️ **LLaVA-MLX Limitation**: New MLX version of LLaVA is fast, but fails on specific image types.  
> ⚡ **Fastest Loading**: Phi-3.5-Vision-Instruct (1.79s)  
> 💨 **Fastest Inference**: Moondream2 (avg 5.41s)  
> 📸 **Multi-Image Testing**: Latest run successfully tested 3 different images.  

## 📋 Testing Objectives

Comprehensive testing of 5 vision-language models, recording basic performance metrics and response results. Using MacBook Air M3 (16GB) environment, supporting single or multiple image testing.

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
> 📅 **Latest Test**: 2025-07-12 08:47:39 (`test_results_20250712_085010.json`)  
> 📸 **Test Images**: 3 images (`IMG_0119.JPG` - photo, `test_image.jpg`, `test_image.png` - synthetic)

### ✅ **Fully Successful Models (4/5)** 🎉
| Rank | Model | Load Time | Avg Inference | Memory Usage | Success Rate |
|------|-------|-----------|---------------|--------------|--------------|
| 🥇 | **Phi-3.5-Vision-Instruct** | **1.79s** | 10.88s | +0.20GB | 100% (3/3) |
| 🥈 | **Moondream2** | 4.91s | **5.41s** | -1.24GB | 100% (3/3) |
| 🥉 | **SmolVLM-500M-Instruct** | 3.52s | 10.71s | +0.48GB | 100% (3/3) |
| 4️⃣ | **SmolVLM2-500M-Video** | 2.58s | 12.37s | +0.08GB | 100% (3/3) |
*Note: Negative memory usage is likely a measurement artifact due to garbage collection.*

### ⚠️ **Partially Successful Models (1/5)**
| Model | Load Time | Avg Inference (Success) | Memory Usage | Success Rate | Details |
|-------|-----------|-------------------------|--------------|--------------|---------|
| **LLaVA-v1.6-Mistral-7B-MLX** | 2.76s | 5.86s | -0.20GB | 33% (1/3) | Fails on synthetic images, works on photographic images. |

### 🏆 **MLX Optimization Success Story** 
**Phi-3.5-Vision's Amazing Transformation**:
- **Before (Transformers)**: 135s+ loading timeout → 100% failure
- **Now (MLX)**: 1.79s fastest loading → 100% success 
- **Improvement**: Loading speed improved **~99%**, from unusable to **top performance**

### 📝 **Key Findings**
1. **🚀 MLX Framework Breakthrough**: Revolutionary VLM performance improvement on Apple Silicon.
2. **⚡ Fastest Loading**: Phi-3.5-Vision-Instruct (1.79s) surpasses all models.
3. **💨 Fastest Inference**: Moondream2 (avg 5.41s) leads in average inference speed.
4. **💾 Memory Efficiency**: MLX models appear to use memory more efficiently, though precise measurement is complex.
5. **📊 Overall Success Rate**: High reliability, with 80% (4/5) of models being fully successful across all test images.
6. **⚙️ Model-Specific Failures**: The LLaVA-MLX model shows that even with framework optimizations, models can have specific data-dependent failure modes that require targeted testing to uncover.

## ✅ Usage Instructions

### 🚀 **Basic Test Commands**
1. **Single Model Test**: `python vlm_tester.py "Model Name"`
   - Example: `python vlm_tester.py "Phi-3.5-Vision-Instruct"`
2. **Full Test**: `python vlm_tester.py`
3. **View Results**: Check JSON files in `results/` directory

### 📸 **Multi-Image Test Support**
- **Automatic Multi-Image Testing**: Program automatically detects all images in `testing_material/images/`
- **Result Format**: Each image independently recorded in JSON `images` field
- **Statistics**: Automatically calculates total inference time, success/failure counts, average inference time

### 📊 **Result Files**
- **Main Results**: `test_results_YYYYMMDD_HHMMSS.json`
- **Single Model Results**: `test_results_single_[Model Name].json`
- **Intermediate Results**: `test_results_intermediate_[Model Name].json` (prevents test interruption)

### ⚠️ **Pre-usage Preparation**
1. **Activate Virtual Environment**: `source ../../ai_vision_env/bin/activate` (from testing directory)
2. **Install MLX-VLM** (Required for Apple Silicon): `pip install mlx-vlm`
   - ⚠️ **Critical for Phi-3.5-Vision**: Without MLX, this model will completely fail (timeout)
   - 🚀 **Performance Impact**: MLX provides 98%+ speed improvement on M1/M2/M3
3. **Prepare Test Images**: Place images in `testing_material/images/` directory 