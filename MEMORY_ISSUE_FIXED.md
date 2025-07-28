# Phi-3.5-Vision-Instruct Memory Issue Fix

## Problem Description

The Phi-3.5-Vision-Instruct model was experiencing MLX GPU memory exhaustion on MacBook Air M3 (16GB), causing crashes with the error:
```
[METAL] Command buffer execution failed: Insufficient Memory (00000008:kIOGPUCommandBufferCallbackErrorOutOfMemory)
```

## Root Cause Analysis

1. **MLX GPU Memory Pressure**: The MLX framework was running out of Metal GPU memory during model loading or inference
2. **Insufficient Memory Cleanup**: Previous cleanup routines weren't properly clearing MLX-specific memory caches
3. **No Fallback Mechanism**: When MLX failed due to memory issues, there was no graceful fallback to CPU-based inference

## Implemented Fixes

### 1. Enhanced Model Loading (`load_phi3_vision`)

**Before:**
```python
model, processor = load(model_id, trust_remote_code=True)
```

**After:**
```python
# Memory protection before loading
gc.collect()
torch.mps.empty_cache()
import mlx.core as mx
mx.eval(mx.zeros((1, 1)))

try:
    model, processor = load(model_id, trust_remote_code=True)
    model._is_mlx_model = True  # Mark for special handling
except RuntimeError as e:
    if "Insufficient Memory" in str(e):
        # Graceful fallback to CPU-based transformers
        fallback_to_transformers()
```

### 2. Enhanced Memory Cleanup (`clear_model_memory`)

**Before:**
```python
del model, processor
gc.collect()
torch.mps.empty_cache()
```

**After:**
```python
# Enhanced MLX cleanup BEFORE deleting model
if hasattr(model, '_is_mlx_model'):
    import mlx.core as mx
    mx.eval(mx.zeros((1, 1)))
    try:
        mx.metal.clear_cache()  # Clear MLX Metal cache
    except AttributeError:
        pass
    
    # Multiple garbage collection cycles
    for i in range(3):
        gc.collect()
        time.sleep(1)

del model, processor
gc.collect()
torch.mps.empty_cache()

# Extended cleanup for memory-intensive models
if "Phi-3.5" in model_name:
    for i in range(2):
        gc.collect()
        torch.mps.empty_cache()
        time.sleep(2)
```

### 3. Memory-Safe Inference

**Before:**
```python
response = generate(model, processor, prompt, image=image_path, ...)
```

**After:**
```python
# Clear MLX cache before inference
import mlx.core as mx
mx.eval(mx.zeros((1, 1)))

try:
    response = generate(model, processor, prompt, image=image_path, ...)
except RuntimeError as e:
    if "Insufficient Memory" in str(e):
        raise Exception(f"MLX GPU memory exhausted: {e}")
```

### 4. Memory Monitoring Utilities

Added `src/testing/utils/memory_monitor.py` with:
- Real-time memory usage tracking
- Memory pressure detection
- Context managers for memory-safe operations
- Comprehensive cleanup utilities

## Testing

### Test Script: `test_phi35_memory_fix.py`

```bash
python test_phi35_memory_fix.py
```

This script:
1. Tests model loading with memory protection
2. Verifies proper model marking (MLX vs fallback)
3. Tests simple inference
4. Validates memory cleanup effectiveness

### Expected Behavior

1. **Successful MLX Loading**: If sufficient GPU memory is available, the model loads as MLX
2. **Graceful Fallback**: If MLX fails due to memory, automatically falls back to CPU-based transformers
3. **Proper Cleanup**: Memory is properly released after model use
4. **No Crashes**: No more `kIOGPUCommandBufferCallbackErrorOutOfMemory` errors

## Usage in VLM Tester

The fixes are automatically applied when running:

```bash
# Test single model
python src/testing/vlm/vlm_tester.py "Phi-3.5-Vision-Instruct"

# Test all models
python src/testing/vlm/vlm_tester.py

# Context understanding tests
python src/testing/vlm/vlm_context_tester.py "Phi-3.5-Vision-Instruct"
```

## Memory Recommendations

For MacBook Air M3 (16GB):
- **Optimal**: Close other applications before running VLM tests
- **Memory Threshold**: Tests will trigger cleanup if memory usage exceeds 12GB
- **Sequential Testing**: Models are tested one at a time with cleanup between each
- **Fallback Strategy**: CPU-based inference is used when GPU memory is insufficient

## Files Modified

1. `src/testing/vlm/vlm_tester.py`
   - Enhanced `load_phi3_vision()` method
   - Improved `clear_model_memory()` function
   - Memory-safe inference in `test_single_image()`

2. `src/testing/vlm/vlm_context_tester.py`
   - Same fixes applied for context understanding tests
   - Enhanced conversation history management

3. `src/testing/utils/memory_monitor.py` (NEW)
   - Memory monitoring utilities
   - Context managers for safe operations

4. `test_phi35_memory_fix.py` (NEW)
   - Verification script for the fixes

## Future Improvements

1. **Dynamic Memory Allocation**: Adjust model parameters based on available memory
2. **Model Quantization**: Use lower precision models when memory is limited
3. **Streaming Inference**: Process large images in chunks
4. **Memory Pool Management**: Pre-allocate and reuse memory buffers

The fixes ensure robust operation of Phi-3.5-Vision-Instruct on memory-constrained systems while maintaining optimal performance when resources are available.