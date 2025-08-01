"""
SmolVLM2 models package
"""

# Import the model classes
from .smolvlm2_500m_video import SmolVLM2Model
from .smolvlm2_500m_video_optimized import OptimizedSmolVLM2Model

__all__ = ['SmolVLM2Model', 'OptimizedSmolVLM2Model'] 