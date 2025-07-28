#!/usr/bin/env python3
"""
Memory monitoring utilities for VLM testing
"""

import gc
import time
import psutil
import torch
from typing import Optional

class MemoryMonitor:
    """Memory monitoring and cleanup utilities"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = self.get_memory_gb()
    
    def get_memory_gb(self) -> float:
        """Get current memory usage in GB"""
        return self.process.memory_info().rss / (1024 ** 3)
    
    def get_memory_info(self) -> dict:
        """Get detailed memory information"""
        memory_info = self.process.memory_info()
        return {
            "rss_gb": memory_info.rss / (1024 ** 3),
            "vms_gb": memory_info.vms / (1024 ** 3),
            "percent": self.process.memory_percent(),
            "available_gb": psutil.virtual_memory().available / (1024 ** 3)
        }
    
    def print_memory_status(self, label: str = ""):
        """Print current memory status"""
        info = self.get_memory_info()
        prefix = f"[{label}] " if label else ""
        print(f"📊 {prefix}Memory: {info['rss_gb']:.2f}GB RSS, "
              f"{info['percent']:.1f}% used, "
              f"{info['available_gb']:.2f}GB available")
    
    def force_cleanup(self, model_name: Optional[str] = None):
        """Force comprehensive memory cleanup"""
        print(f"🧹 Force cleanup for {model_name or 'unknown model'}...")
        
        # Multiple garbage collection cycles
        for i in range(3):
            gc.collect()
            time.sleep(0.5)
        
        # Clear PyTorch caches
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
            print("  🔧 MPS cache cleared")
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("  🔧 CUDA cache cleared")
        
        # MLX-specific cleanup
        try:
            import mlx.core as mx
            mx.eval(mx.zeros((1, 1)))
            
            # Try to clear MLX Metal cache if available
            try:
                mx.metal.clear_cache()
                print("  🔧 MLX Metal cache cleared")
            except AttributeError:
                pass  # Older MLX versions
                
            print("  🔧 MLX memory cleared")
        except ImportError:
            pass  # MLX not available
        except Exception as e:
            print(f"  ⚠️ MLX cleanup warning: {e}")
        
        # Final cleanup cycle
        gc.collect()
        time.sleep(1)
        
        print("✅ Force cleanup completed")
    
    def check_memory_pressure(self, threshold_gb: float = 12.0) -> bool:
        """Check if memory usage is approaching dangerous levels"""
        current_memory = self.get_memory_gb()
        if current_memory > threshold_gb:
            print(f"⚠️ Memory pressure detected: {current_memory:.2f}GB > {threshold_gb}GB")
            return True
        return False
    
    def memory_safe_operation(self, operation_name: str, threshold_gb: float = 12.0):
        """Context manager for memory-safe operations"""
        return MemorySafeContext(self, operation_name, threshold_gb)

class MemorySafeContext:
    """Context manager for memory-safe operations"""
    
    def __init__(self, monitor: MemoryMonitor, operation_name: str, threshold_gb: float):
        self.monitor = monitor
        self.operation_name = operation_name
        self.threshold_gb = threshold_gb
        self.start_memory = None
    
    def __enter__(self):
        self.start_memory = self.monitor.get_memory_gb()
        self.monitor.print_memory_status(f"Before {self.operation_name}")
        
        # Check if we should cleanup before starting
        if self.monitor.check_memory_pressure(self.threshold_gb):
            self.monitor.force_cleanup(self.operation_name)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_memory = self.monitor.get_memory_gb()
        memory_diff = end_memory - self.start_memory
        
        self.monitor.print_memory_status(f"After {self.operation_name}")
        print(f"📈 Memory change: {memory_diff:+.2f}GB")
        
        # Force cleanup if memory increased significantly
        if memory_diff > 2.0:  # More than 2GB increase
            print(f"⚠️ Large memory increase detected, forcing cleanup...")
            self.monitor.force_cleanup(self.operation_name)
            final_memory = self.monitor.get_memory_gb()
            print(f"📉 Memory after cleanup: {final_memory:.2f}GB")

# Global memory monitor instance
memory_monitor = MemoryMonitor()