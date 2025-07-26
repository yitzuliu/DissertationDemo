"""
Task Knowledge Data Models

Defines the data structures for storing and managing task knowledge in the RAG system.
These models represent the structured knowledge repository that contains task steps,
tools, completion indicators, and visual cues.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class TaskStep:
    """
    Represents a single step in a task with all associated information.
    
    This is the core data structure that contains everything needed to identify
    and guide users through a specific task step.
    """
    step_id: int
    task_description: str
    tools_needed: List[str] = field(default_factory=list)
    completion_indicators: List[str] = field(default_factory=list)
    visual_cues: List[str] = field(default_factory=list)
    estimated_duration: Optional[str] = None
    safety_notes: List[str] = field(default_factory=list)
    embedding: Optional[np.ndarray] = None
    
    def __post_init__(self):
        """Validate the task step data after initialization."""
        if self.step_id < 1:
            raise ValueError("step_id must be positive")
        if not self.task_description.strip():
            raise ValueError("task_description cannot be empty")
        if not self.visual_cues:
            raise ValueError("visual_cues cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TaskStep to dictionary for serialization."""
        return {
            "step_id": self.step_id,
            "task_description": self.task_description,
            "tools_needed": self.tools_needed,
            "completion_indicators": self.completion_indicators,
            "visual_cues": self.visual_cues,
            "estimated_duration": self.estimated_duration,
            "safety_notes": self.safety_notes,
            # Note: embedding is not serialized as it's computed at runtime
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskStep':
        """Create TaskStep from dictionary data."""
        return cls(
            step_id=data["step_id"],
            task_description=data["task_description"],
            tools_needed=data.get("tools_needed", []),
            completion_indicators=data.get("completion_indicators", []),
            visual_cues=data.get("visual_cues", []),
            estimated_duration=data.get("estimated_duration"),
            safety_notes=data.get("safety_notes", [])
        )


@dataclass
class TaskKnowledge:
    """
    Represents complete knowledge for a specific task.
    
    Contains all steps and metadata for a task like "brewing coffee".
    """
    task_name: str
    task_description: str
    total_steps: int
    steps: List[TaskStep] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    difficulty_level: str = "medium"  # easy, medium, hard
    estimated_total_time: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate task knowledge after initialization."""
        if not self.task_name.strip():
            raise ValueError("task_name cannot be empty")
        if self.total_steps != len(self.steps):
            raise ValueError("total_steps must match the number of steps")
        if self.difficulty_level not in ["easy", "medium", "hard"]:
            raise ValueError("difficulty_level must be easy, medium, or hard")
    
    def get_step(self, step_id: int) -> Optional[TaskStep]:
        """Get a specific step by its ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_next_step(self, current_step_id: int) -> Optional[TaskStep]:
        """Get the next step after the current one."""
        return self.get_step(current_step_id + 1)
    
    def get_previous_step(self, current_step_id: int) -> Optional[TaskStep]:
        """Get the previous step before the current one."""
        return self.get_step(current_step_id - 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TaskKnowledge to dictionary for serialization."""
        return {
            "task_name": self.task_name,
            "task_description": self.task_description,
            "total_steps": self.total_steps,
            "steps": [step.to_dict() for step in self.steps],
            "prerequisites": self.prerequisites,
            "difficulty_level": self.difficulty_level,
            "estimated_total_time": self.estimated_total_time,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskKnowledge':
        """Create TaskKnowledge from dictionary data."""
        steps = [TaskStep.from_dict(step_data) for step_data in data.get("steps", [])]
        
        return cls(
            task_name=data["task_name"],
            task_description=data["task_description"],
            total_steps=data["total_steps"],
            steps=steps,
            prerequisites=data.get("prerequisites", []),
            difficulty_level=data.get("difficulty_level", "medium"),
            estimated_total_time=data.get("estimated_total_time"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )


@dataclass
class MatchResult:
    """
    Represents the result of matching a VLM observation to a task step.
    
    This is returned by the RAG system when finding the best matching step
    for a given VLM observation.
    """
    step_id: int
    task_description: str
    tools_needed: List[str]
    completion_indicators: List[str]
    visual_cues: List[str]
    similarity: float
    confidence_level: str  # "high", "medium", "low", "none"
    matched_cues: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate match result after initialization."""
        if not 0.0 <= self.similarity <= 1.0:
            raise ValueError("similarity must be between 0.0 and 1.0")
        if self.confidence_level not in ["high", "medium", "low", "none"]:
            raise ValueError("confidence_level must be high, medium, low, or none")
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high confidence match."""
        return self.confidence_level == "high"
    
    @property
    def is_reliable(self) -> bool:
        """Check if this match is reliable enough for state updates."""
        return self.confidence_level in ["high", "medium"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert MatchResult to dictionary."""
        return {
            "step_id": self.step_id,
            "task_description": self.task_description,
            "tools_needed": self.tools_needed,
            "completion_indicators": self.completion_indicators,
            "visual_cues": self.visual_cues,
            "similarity": self.similarity,
            "confidence_level": self.confidence_level,
            "matched_cues": self.matched_cues,
            "timestamp": self.timestamp.isoformat()
        }