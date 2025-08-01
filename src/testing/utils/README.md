# Testing Utilities

This directory contains essential utilities for VLM testing and system monitoring, providing memory management and performance optimization tools.

*Last Updated: August 1, 2025*

---

## Overview

The Testing Utilities module provides comprehensive memory monitoring and management capabilities for VLM testing environments. It ensures optimal performance and prevents memory-related issues during intensive model testing operations.

---

## Architecture

### Core Components

- **MemoryMonitor**: Primary memory monitoring and cleanup utility
- **MemorySafeContext**: Context manager for memory-safe operations
- **Global Instance**: Pre-configured memory monitor for immediate use

### Key Features

- **Real-time Memory Tracking**: Monitor RSS, VMS, and percentage usage
- **Multi-Platform Cache Clearing**: Support for PyTorch, MLX, CUDA, and MPS
- **Automatic Cleanup**: Intelligent memory pressure detection and cleanup
- **Context Management**: Safe operation execution with automatic cleanup
- **Performance Optimization**: Comprehensive garbage collection cycles

---

## Core Components

### MemoryMonitor Class

**Purpose**: Central memory monitoring and management utility

**Key Methods**:
- `get_memory_gb()`: Get current memory usage in GB
- `get_memory_info()`: Get detailed memory information
- `print_memory_status()`: Display formatted memory status
- `force_cleanup()`: Comprehensive memory cleanup
- `check_memory_pressure()`: Detect memory pressure conditions
- `memory_safe_operation()`: Create memory-safe context

**Features**:
- Cross-platform memory monitoring (Linux, macOS, Windows)
- Multi-framework cache clearing (PyTorch, MLX, CUDA, MPS)
- Intelligent cleanup strategies
- Real-time memory pressure detection

### MemorySafeContext Class

**Purpose**: Context manager for memory-safe operations

**Usage**:
```python
with memory_monitor.memory_safe_operation("model_inference", threshold_gb=12.0):
    # Your memory-intensive operation here
    result = model.predict(input_data)
```

**Features**:
- Automatic pre-operation cleanup
- Memory change tracking
- Post-operation cleanup on large increases
- Detailed memory reporting

---

## Performance Characteristics

### Memory Monitoring
- **Accuracy**: Real-time system memory tracking
- **Overhead**: Minimal (< 1% CPU usage)
- **Frequency**: On-demand or continuous monitoring
- **Precision**: GB-level precision with percentage tracking

### Cleanup Operations
- **Comprehensive**: Multi-framework cache clearing
- **Safe**: Non-destructive cleanup operations
- **Efficient**: Optimized cleanup cycles
- **Adaptive**: Platform-specific optimizations

### Context Management
- **Automatic**: Pre and post-operation cleanup
- **Intelligent**: Threshold-based cleanup decisions
- **Transparent**: Detailed operation reporting
- **Safe**: Exception-safe context management

---

## Usage

### Basic Memory Monitoring

```python
from src.testing.utils.memory_monitor import memory_monitor

# Get current memory usage
memory_gb = memory_monitor.get_memory_gb()
print(f"Current memory: {memory_gb:.2f}GB")

# Get detailed memory information
info = memory_monitor.get_memory_info()
print(f"RSS: {info['rss_gb']:.2f}GB, VMS: {info['vms_gb']:.2f}GB")
```

### Memory Status Display

```python
# Print formatted memory status
memory_monitor.print_memory_status("Before Model Load")
# Output: 📊 [Before Model Load] Memory: 2.45GB RSS, 15.3% used, 13.55GB available
```

### Force Cleanup

```python
# Comprehensive memory cleanup
memory_monitor.force_cleanup("model_switch")
# Clears: PyTorch, MLX, CUDA, MPS caches + garbage collection
```

### Memory-Safe Operations

```python
# Safe operation execution
with memory_monitor.memory_safe_operation("large_inference", threshold_gb=12.0):
    # Automatic cleanup before operation
    result = model.predict(large_dataset)
    # Automatic cleanup after operation if needed
```

### Memory Pressure Detection

```python
# Check for memory pressure
if memory_monitor.check_memory_pressure(threshold_gb=12.0):
    print("⚠️ Memory pressure detected!")
    memory_monitor.force_cleanup("pressure_relief")
```

---

## Integration

### With VLM Testing

```python
from src.testing.utils.memory_monitor import memory_monitor

def test_model_performance():
    with memory_monitor.memory_safe_operation("model_testing"):
        # Load model
        model = load_vlm_model()
        
        # Run inference
        for batch in test_data:
            result = model.predict(batch)
            
        # Automatic cleanup ensures next test starts clean
```

### With Model Switching

```python
def switch_models(model_name):
    # Cleanup before loading new model
    memory_monitor.force_cleanup(f"switch_to_{model_name}")
    
    # Load new model
    new_model = load_model(model_name)
    
    # Verify memory status
    memory_monitor.print_memory_status(f"After {model_name} load")
```

### With Batch Processing

```python
def process_large_batch(batch_data):
    with memory_monitor.memory_safe_operation("batch_processing", threshold_gb=10.0):
        results = []
        for item in batch_data:
            result = process_item(item)
            results.append(result)
        return results
```

---

## Monitoring

### Memory Metrics

- **RSS (Resident Set Size)**: Physical memory usage
- **VMS (Virtual Memory Size)**: Virtual memory allocation
- **Memory Percentage**: System memory utilization
- **Available Memory**: Free system memory

### Performance Indicators

- **Memory Pressure**: Threshold-based pressure detection
- **Memory Growth**: Operation-specific memory changes
- **Cleanup Effectiveness**: Pre/post cleanup memory levels
- **Cache Efficiency**: Framework-specific cache utilization

### Logging and Reporting

- **Real-time Status**: Live memory status updates
- **Operation Tracking**: Memory changes per operation
- **Cleanup Logging**: Detailed cleanup operation logs
- **Performance Metrics**: Memory efficiency statistics

---

## Configuration

### Memory Thresholds

```python
# Default thresholds
DEFAULT_MEMORY_THRESHOLD = 12.0  # GB
DEFAULT_CLEANUP_THRESHOLD = 2.0  # GB increase

# Custom thresholds
memory_monitor.check_memory_pressure(threshold_gb=8.0)
```

### Cleanup Strategies

```python
# Comprehensive cleanup (default)
memory_monitor.force_cleanup("operation_name")

# Platform-specific cleanup
if torch.cuda.is_available():
    torch.cuda.empty_cache()
if torch.backends.mps.is_available():
    torch.mps.empty_cache()
```

### Context Management

```python
# Custom context parameters
with memory_monitor.memory_safe_operation(
    operation_name="custom_operation",
    threshold_gb=10.0
):
    # Operation with custom memory threshold
    pass
```

---

## Troubleshooting

### Common Issues

**High Memory Usage**
```python
# Force comprehensive cleanup
memory_monitor.force_cleanup("emergency_cleanup")

# Check memory pressure
if memory_monitor.check_memory_pressure(threshold_gb=8.0):
    print("⚠️ Consider reducing batch size or model complexity")
```

**Cache Not Clearing**
```python
# Manual cache clearing
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    
import mlx.core as mx
mx.eval(mx.zeros((1, 1)))
```

**Memory Leaks**
```python
# Monitor memory growth
with memory_monitor.memory_safe_operation("leak_detection"):
    # Suspected leaky operation
    pass
# Check memory change in output
```

### Performance Optimization

**Batch Size Optimization**
```python
# Monitor memory during batch processing
with memory_monitor.memory_safe_operation("batch_optimization"):
    for batch_size in [1, 2, 4, 8, 16]:
        memory_monitor.print_memory_status(f"Batch size {batch_size}")
        # Test with different batch sizes
```

**Model Loading Optimization**
```python
# Clean memory before loading large models
memory_monitor.force_cleanup("pre_model_load")
model = load_large_model()
memory_monitor.print_memory_status("Post model load")
```

---

## API Reference

### MemoryMonitor

#### Methods

**`get_memory_gb() -> float`**
- Returns current memory usage in GB
- **Returns**: Memory usage as float

**`get_memory_info() -> dict`**
- Returns detailed memory information
- **Returns**: Dictionary with rss_gb, vms_gb, percent, available_gb

**`print_memory_status(label: str = "")`**
- Prints formatted memory status
- **Parameters**: label - Optional operation label

**`force_cleanup(model_name: Optional[str] = None)`**
- Performs comprehensive memory cleanup
- **Parameters**: model_name - Optional model identifier

**`check_memory_pressure(threshold_gb: float = 12.0) -> bool`**
- Checks for memory pressure conditions
- **Parameters**: threshold_gb - Memory threshold in GB
- **Returns**: True if pressure detected

**`memory_safe_operation(operation_name: str, threshold_gb: float = 12.0)`**
- Creates memory-safe context manager
- **Parameters**: operation_name - Operation identifier, threshold_gb - Memory threshold
- **Returns**: MemorySafeContext instance

### MemorySafeContext

#### Context Manager Methods

**`__enter__()`**
- Initializes context and performs pre-operation cleanup
- **Returns**: Self instance

**`__exit__(exc_type, exc_val, exc_tb)`**
- Performs post-operation cleanup and reporting
- **Parameters**: Exception information (if any)

---

## Contribution Guidelines

### Code Standards

- **Documentation**: All methods must have docstrings
- **Type Hints**: Use type hints for all function parameters
- **Error Handling**: Implement comprehensive exception handling
- **Testing**: Include unit tests for all utilities

### Performance Requirements

- **Memory Overhead**: Keep monitoring overhead < 1%
- **Response Time**: Memory queries should complete < 10ms
- **Cleanup Efficiency**: Cleanup should reduce memory by > 50%
- **Cross-Platform**: Support Linux, macOS, and Windows

### Testing Guidelines

- **Memory Tests**: Test with various memory pressure scenarios
- **Platform Tests**: Test on different operating systems
- **Framework Tests**: Test with different ML frameworks
- **Integration Tests**: Test with VLM testing workflows

---

## Related Documentation

- [VLM Testing Framework](../README.md)
- [Memory Management Best Practices](../../memory/README.md)
- [Performance Optimization Guide](../../../docs/VLM_SYSTEM_GUIDE.md)
- [System Monitoring Tools](../../../docs/RAG_SYSTEM_OPERATION_GUIDE.md) 