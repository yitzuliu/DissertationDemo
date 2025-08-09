"""
Task Knowledge Loader Module

This module provides functionality to load and manage task knowledge from YAML files.
It includes caching, validation, and easy access to task information for the RAG system.
"""

from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path
from dataclasses import dataclass
from .validation import TaskKnowledgeValidator, TaskValidationError


@dataclass
class TaskStep:
    """Represents a single step in a task"""
    step_id: int
    title: str
    task_description: str
    tools_needed: List[str]
    completion_indicators: List[str]
    visual_cues: List[str]
    estimated_duration: str
    safety_notes: Optional[List[str]] = None
    
    def __post_init__(self):
        """Ensure safety_notes is always a list"""
        if self.safety_notes is None:
            self.safety_notes = []


@dataclass
class TaskKnowledge:
    """Represents complete task knowledge"""
    task_name: str
    display_name: str
    description: str
    steps: List[TaskStep]
    estimated_total_duration: Optional[str] = None
    difficulty_level: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    global_safety_notes: Optional[List[str]] = None
    task_completion_indicators: Optional[List[str]] = None
    
    def __post_init__(self):
        """Ensure optional fields have default values"""
        if self.metadata is None:
            self.metadata = {}
        if self.global_safety_notes is None:
            self.global_safety_notes = []
        if self.task_completion_indicators is None:
            self.task_completion_indicators = []
    
    def get_step(self, step_id: int) -> Optional[TaskStep]:
        """Get a specific step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_total_steps(self) -> int:
        """Get the total number of steps"""
        return len(self.steps)
    
    def get_all_visual_cues(self) -> List[str]:
        """Get all visual cues from all steps"""
        all_cues = []
        for step in self.steps:
            all_cues.extend(step.visual_cues)
        return list(set(all_cues))  # Remove duplicates
    
    def get_all_tools(self) -> List[str]:
        """Get all tools needed across all steps"""
        all_tools = []
        for step in self.steps:
            all_tools.extend(step.tools_needed)
        return list(set(all_tools))  # Remove duplicates


class TaskKnowledgeLoader:
    """Loads and manages task knowledge from YAML files"""
    
    def __init__(self, tasks_directory: Path = None):
        """
        Initialize the task loader
        
        Args:
            tasks_directory: Directory containing task YAML files
        """
        if tasks_directory is None:
            tasks_directory = Path("data/tasks")
        
        self.tasks_directory = Path(tasks_directory)
        self.validator = TaskKnowledgeValidator()
        self._task_cache: Dict[str, TaskKnowledge] = {}
        self._loaded_files: Dict[str, Path] = {}
    
    def load_task(self, task_name: str, file_path: Optional[Path] = None) -> TaskKnowledge:
        """
        Load a task from YAML file
        
        Args:
            task_name: Name of the task to load
            file_path: Optional specific file path (if not provided, will look in tasks_directory)
            
        Returns:
            TaskKnowledge object
            
        Raises:
            TaskValidationError: If the task file is invalid
            FileNotFoundError: If the task file is not found
        """
        # Check cache first
        if task_name in self._task_cache:
            return self._task_cache[task_name]
        
        # Determine file path
        if file_path is None:
            file_path = self.tasks_directory / f"{task_name}.yaml"
        
        # Validate file
        is_valid, errors = self.validator.validate_task_file(file_path)
        if not is_valid:
            raise TaskValidationError(f"Task validation failed for {task_name}: {errors}")
        
        # Load YAML data
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                task_data = yaml.safe_load(file)
        except Exception as e:
            raise TaskValidationError(f"Failed to load task file {file_path}: {str(e)}")
        
        # Convert to TaskKnowledge object
        task_knowledge = self._convert_to_task_knowledge(task_data)
        
        # Cache the result
        self._task_cache[task_name] = task_knowledge
        self._loaded_files[task_name] = file_path
        
        return task_knowledge
    
    def _convert_to_task_knowledge(self, task_data: Dict[str, Any]) -> TaskKnowledge:
        """Convert raw YAML data to TaskKnowledge object"""
        
        # Convert steps
        steps = []
        for step_data in task_data['steps']:
            step = TaskStep(
                step_id=step_data['step_id'],
                title=step_data['title'],
                task_description=step_data['task_description'],
                tools_needed=step_data['tools_needed'],
                completion_indicators=step_data['completion_indicators'],
                visual_cues=step_data['visual_cues'],
                estimated_duration=step_data['estimated_duration'],
                safety_notes=step_data.get('safety_notes', [])
            )
            steps.append(step)
        
        # Create TaskKnowledge object
        task_knowledge = TaskKnowledge(
            task_name=task_data['task_name'],
            display_name=task_data['display_name'],
            description=task_data['description'],
            steps=steps,
            estimated_total_duration=task_data.get('estimated_total_duration'),
            difficulty_level=task_data.get('difficulty_level'),
            metadata=task_data.get('metadata', {}),
            global_safety_notes=task_data.get('global_safety_notes', []),
            task_completion_indicators=task_data.get('task_completion_indicators', [])
        )
        
        return task_knowledge
    
    def load_all_tasks(self) -> Dict[str, TaskKnowledge]:
        """
        Load all task files from the tasks directory
        
        Returns:
            Dictionary mapping task names to TaskKnowledge objects
        """
        if not self.tasks_directory.exists():
            raise FileNotFoundError(f"Tasks directory not found: {self.tasks_directory}")
        
        tasks = {}
        yaml_files = list(self.tasks_directory.glob("*.yaml")) + list(self.tasks_directory.glob("*.yml"))
        
        for file_path in yaml_files:
            task_name = file_path.stem
            try:
                task_knowledge = self.load_task(task_name, file_path)
                tasks[task_name] = task_knowledge
                print(f"Successfully loaded task: {task_name}")
            except Exception as e:
                print(f"Failed to load task {task_name}: {str(e)}")
                continue
        
        return tasks
    
    def get_task_summary(self, task_name: str) -> Dict[str, Any]:
        """
        Get a summary of a loaded task
        
        Args:
            task_name: Name of the task
            
        Returns:
            Dictionary with task summary information
        """
        if task_name not in self._task_cache:
            raise ValueError(f"Task {task_name} not loaded. Call load_task() first.")
        
        task = self._task_cache[task_name]
        
        return {
            "task_name": task.task_name,
            "display_name": task.display_name,
            "description": task.description,
            "total_steps": task.get_total_steps(),
            "estimated_duration": task.estimated_total_duration,
            "difficulty": task.difficulty_level,
            "total_tools": len(task.get_all_tools()),
            "total_visual_cues": len(task.get_all_visual_cues()),
            "file_path": str(self._loaded_files.get(task_name, "Unknown"))
        }
    
    def clear_cache(self):
        """Clear the task cache"""
        self._task_cache.clear()
        self._loaded_files.clear()
    
    def is_task_loaded(self, task_name: str) -> bool:
        """Check if a task is already loaded in cache"""
        return task_name in self._task_cache
    
    def get_loaded_tasks(self) -> List[str]:
        """Get list of currently loaded task names"""
        return list(self._task_cache.keys())
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the task loader
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            "cached_tasks": len(self._task_cache),
            "tasks_directory": str(self.tasks_directory),
            "cache_enabled": True,
            "loaded_files": len(self._loaded_files)
        }


# Convenience functions
def load_coffee_brewing_task() -> TaskKnowledge:
    """Load the coffee brewing task specifically"""
    loader = TaskKnowledgeLoader()
    return loader.load_task("brewing_coffee")


def create_task_loader(tasks_directory: str = "data/tasks") -> TaskKnowledgeLoader:
    """Create a task loader with specified directory"""
    return TaskKnowledgeLoader(Path(tasks_directory))