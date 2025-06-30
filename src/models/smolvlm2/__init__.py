"""
SmolVLM2 models package
"""

# Import the model classes
from .SmolVLM2-500M-Video-Instruct.project_workspace.smolvlm2_500_model import SmolVLM2Model
from .SmolVLM2-500M-Video-Instruct.project_workspace.smolvlm2_500_model_optimized import OptimizedSmolVLM2Model

__all__ = ['SmolVLM2Model', 'OptimizedSmolVLM2Model'] 