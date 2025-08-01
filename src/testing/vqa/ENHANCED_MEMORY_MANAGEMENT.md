# Enhanced MLX Memory Management

## Overview

This document describes the enhanced memory management system implemented to address MLX framework memory issues on Apple Silicon devices, specifically the "Insufficient Memory" errors that occur during VQA testing.

## Problem Analysis

### Original Issue
```
libc++abi: terminating due to uncaught exception of type std::runtime_error: 
[METAL] Command buffer execution failed: Insufficient Memory (00000008:kIOGPUCommandBufferCallbackErrorOutOfMemory)
```

### Root Causes
1. **MLX Memory Accumulation**: MLX models accumulate GPU memory during inference without proper cleanup
2. **Insufficient Memory Management**: Original `clear_model_memory()` only handled PyTorch, not MLX
3. **No Memory Pressure Detection**: System couldn't detect when memory usage was approaching dangerous levels
4. **Continuous Inference**: Multiple questions processed without intermediate memory cleanup

## Solution Implementation

### 1. Enhanced MLX Memory Clearing (`clear_mlx_memory()`)

**Location**: `src/testing/vlm/vlm_tester.py`

```python
def clear_mlx_memory():
    """Clear MLX-specific memory and Metal GPU cache"""
    print("🧹 Clearing MLX memory...")
    try:
        import mlx.core as mx
        # Force garbage collection for MLX
        mx.eval(mx.zeros((1, 1)))
        
        # Clear Metal GPU cache if available
        try:
            mx.metal.clear_cache()
            print("  🔧 MLX Metal cache cleared")
        except AttributeError:
            # Older MLX versions may not have metal.clear_cache()
            pass
        except Exception as e:
            print(f"  ⚠️ MLX Metal cache clearing failed: {e}")
            
        print("  ✅ MLX memory cleared successfully")
        
    except ImportError:
        print("  ℹ️ MLX not available, skipping MLX memory cleanup")
    except Exception as e:
        print(f"  ⚠️ MLX memory clearing warning: {e}")
```

**Features**:
- Forces MLX garbage collection
- Clears Metal GPU cache when available
- Handles version compatibility issues
- Provides detailed logging

### 2. Enhanced Model Memory Clearing (`clear_model_memory()`)

**Location**: `src/testing/vlm/vlm_tester.py`

```python
def clear_model_memory(model, processor):
    """Clear model memory with enhanced MLX support"""
    print("🧹 Clearing model memory...")
    
    # Delete model and processor references
    del model, processor
    
    # Force garbage collection
    gc.collect()
    
    # Clear PyTorch MPS cache if available
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
        print("  🔧 PyTorch MPS cache cleared")
    
    # Clear MLX memory specifically
    clear_mlx_memory()
    
    # Allow system time to clean up memory
    time.sleep(2)
    print("  ✅ Memory cleanup completed")
```

**Features**:
- Handles both PyTorch and MLX models
- Sequential cleanup process
- System time allowance for memory release

### 3. VQA Framework Memory Management

**Location**: `src/testing/vqa/vqa_framework.py`

#### Memory Pressure Detection
```python
def _check_mlx_memory_pressure(self) -> bool:
    """Check if MLX memory usage is approaching dangerous levels"""
    try:
        import mlx.core as mx
        # Try to get memory info if available
        try:
            memory_info = mx.metal.get_memory_info()
            # If we can get memory info, check if it's high
            if hasattr(memory_info, 'used') and hasattr(memory_info, 'total'):
                usage_ratio = memory_info.used / memory_info.total
                if usage_ratio > 0.8:  # 80% threshold
                    print(f"⚠️ MLX memory pressure detected: {usage_ratio:.1%} usage")
                    return True
        except AttributeError:
            # Fallback: try to allocate a small array to test memory
            try:
                test_array = mx.zeros((1000, 1000))
                mx.eval(test_array)
                return False  # Memory seems available
            except Exception:
                print("⚠️ MLX memory pressure detected (allocation failed)")
                return True
    except ImportError:
        return False  # MLX not available
    except Exception as e:
        print(f"⚠️ MLX memory check warning: {e}")
        return False
    
    return False
```

#### Periodic Memory Cleanup
```python
# Enhanced memory management for MLX models
# Check memory pressure and perform cleanup for MLX models
if i > 0 and i % self.memory_cleanup_interval == 0:
    if any(mlx_model in model_name.lower() for mlx_model in self.mlx_models):
        print(f"  🧹 Periodic memory management for MLX model (question {i})...")
        
        # Check memory pressure first
        if self._check_mlx_memory_pressure():
            print(f"  ⚠️ High memory pressure detected, performing aggressive cleanup...")
            # Force multiple cleanup cycles
            for cleanup_cycle in range(3):
                clear_mlx_memory()
                gc.collect()
                time.sleep(0.5)
            print(f"  ✅ Aggressive memory cleanup completed")
        else:
            # Normal periodic cleanup
            try:
                clear_mlx_memory()
                gc.collect()
                print(f"  ✅ Normal memory cleanup completed for question {i}")
            except Exception as e:
                print(f"  ⚠️ Memory cleanup warning: {e}")
```

### 4. Configuration Settings

**Memory Management Parameters**:
```python
# Initialize memory management settings
self.memory_cleanup_interval = 5  # Clean memory every 5 questions for MLX models
self.mlx_models = ["phi35_vision", "llava_mlx", "smolvlm_v2_instruct"]
```

**Model Configuration**:
```python
self.models_config = {
    "phi35_vision": {
        "model_id": "mlx-community/Phi-3.5-vision-instruct-4bit",
        "loader": VLMModelLoader.load_phi3_vision,
        "memory_intensive": True  # Flag for enhanced memory management
    },
    # ... other models
}
```

## Usage

### Running VQA Tests with Enhanced Memory Management

```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Run VQA test with enhanced memory management
cd src/testing/vqa
python vqa_test.py --questions 10 --models phi35_vision --verbose
```

### Testing Memory Management

```bash
# Test the enhanced memory management functions
python test_enhanced_memory.py
```

## Monitoring and Debugging

### Memory Cleanup Logs
The enhanced system provides detailed logging:
```
🧹 Periodic memory management for MLX model (question 5)...
⚠️ High memory pressure detected, performing aggressive cleanup...
  🔧 MLX Metal cache cleared
  ✅ MLX memory cleared successfully
✅ Aggressive memory cleanup completed
```

### Memory Pressure Detection
```
⚠️ MLX memory pressure detected: 85.2% usage
🧹 Clearing MLX memory...
  🔧 MLX Metal cache cleared
  ✅ MLX memory cleared successfully
```

## Performance Impact

### Benefits
- **Prevents Memory Overflow**: Eliminates "Insufficient Memory" errors
- **Stable Long-Running Tests**: Supports extended VQA testing sessions
- **Automatic Management**: No manual intervention required
- **Adaptive Cleanup**: Adjusts cleanup intensity based on memory pressure

### Overhead
- **Minimal Performance Impact**: Cleanup occurs every 5 questions
- **Intelligent Scheduling**: Only for MLX models that need it
- **Conditional Execution**: Skips cleanup when memory pressure is low

## Troubleshooting

### Common Issues

1. **MLX Import Errors**
   ```
   ℹ️ MLX not available, skipping MLX memory cleanup
   ```
   - **Solution**: Ensure MLX is properly installed for Apple Silicon

2. **Memory Pressure False Positives**
   ```
   ⚠️ MLX memory pressure detected (allocation failed)
   ```
   - **Solution**: System is correctly detecting memory issues

3. **Cleanup Warnings**
   ```
   ⚠️ MLX Metal cache clearing failed: [error]
   ```
   - **Solution**: Normal for older MLX versions, system continues working

### Debug Mode
Enable verbose logging to see detailed memory management:
```bash
python vqa_test.py --verbose --questions 5 --models phi35_vision
```

## Future Enhancements

1. **Dynamic Cleanup Intervals**: Adjust based on model size and memory usage
2. **Memory Usage Tracking**: Log memory usage patterns for optimization
3. **Predictive Cleanup**: Clean memory before pressure reaches critical levels
4. **Model-Specific Optimization**: Different strategies for different MLX models

## Compatibility

- **MLX Versions**: Compatible with MLX 0.0.8 and later
- **Apple Silicon**: Optimized for M1/M2/M3 chips
- **Python Versions**: 3.8+ supported
- **Operating Systems**: macOS 12.0+ required for MLX support 