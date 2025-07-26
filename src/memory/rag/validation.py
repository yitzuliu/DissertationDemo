"""
Task Knowledge Validation Module

This module provides validation functions for task knowledge data structures.
It ensures that task YAML files conform to the expected schema and contain
all required fields for proper system operation.
"""

from typing import Dict, List, Any, Optional, Tuple
import yaml
from pathlib import Path


class TaskValidationError(Exception):
    """Custom exception for task validation errors"""
    pass


class TaskKnowledgeValidator:
    """Validator for task knowledge YAML files"""
    
    # Required fields for the main task structure
    REQUIRED_TASK_FIELDS = {
        'task_name': str,
        'display_name': str,
        'description': str,
        'steps': list
    }
    
    # Required fields for each step
    REQUIRED_STEP_FIELDS = {
        'step_id': int,
        'title': str,
        'task_description': str,
        'tools_needed': list,
        'completion_indicators': list,
        'visual_cues': list,
        'estimated_duration': str
    }
    
    # Optional fields that can be present
    OPTIONAL_TASK_FIELDS = {
        'estimated_total_duration': str,
        'difficulty_level': str,
        'metadata': dict,
        'global_safety_notes': list,
        'task_completion_indicators': list
    }
    
    OPTIONAL_STEP_FIELDS = {
        'safety_notes': list
    }
    
    def __init__(self):
        """Initialize the validator"""
        self.validation_errors: List[str] = []
    
    def validate_task_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a task knowledge YAML file
        
        Args:
            file_path: Path to the YAML file to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.validation_errors = []
        
        try:
            # Load YAML file
            with open(file_path, 'r', encoding='utf-8') as file:
                task_data = yaml.safe_load(file)
            
            if not isinstance(task_data, dict):
                self.validation_errors.append("Task file must contain a dictionary at root level")
                return False, self.validation_errors
            
            # Validate main task structure
            self._validate_task_structure(task_data)
            
            # Validate steps
            if 'steps' in task_data:
                self._validate_steps(task_data['steps'])
            
            return len(self.validation_errors) == 0, self.validation_errors
            
        except yaml.YAMLError as e:
            self.validation_errors.append(f"YAML parsing error: {str(e)}")
            return False, self.validation_errors
        except FileNotFoundError:
            self.validation_errors.append(f"Task file not found: {file_path}")
            return False, self.validation_errors
        except Exception as e:
            self.validation_errors.append(f"Unexpected error: {str(e)}")
            return False, self.validation_errors
    
    def _validate_task_structure(self, task_data: Dict[str, Any]) -> None:
        """Validate the main task structure"""
        
        # Check required fields
        for field_name, expected_type in self.REQUIRED_TASK_FIELDS.items():
            if field_name not in task_data:
                self.validation_errors.append(f"Missing required field: {field_name}")
                continue
            
            if not isinstance(task_data[field_name], expected_type):
                self.validation_errors.append(
                    f"Field '{field_name}' must be of type {expected_type.__name__}, "
                    f"got {type(task_data[field_name]).__name__}"
                )
        
        # Validate task_name format (should be snake_case)
        if 'task_name' in task_data:
            task_name = task_data['task_name']
            if not isinstance(task_name, str) or not task_name.replace('_', '').isalnum():
                self.validation_errors.append(
                    "task_name should be in snake_case format (letters, numbers, underscores only)"
                )
        
        # Check for unknown fields (warn but don't fail)
        known_fields = set(self.REQUIRED_TASK_FIELDS.keys()) | set(self.OPTIONAL_TASK_FIELDS.keys())
        unknown_fields = set(task_data.keys()) - known_fields
        if unknown_fields:
            print(f"Warning: Unknown fields found: {unknown_fields}")
    
    def _validate_steps(self, steps: List[Dict[str, Any]]) -> None:
        """Validate the steps array"""
        
        if not isinstance(steps, list):
            self.validation_errors.append("Steps must be a list")
            return
        
        if len(steps) == 0:
            self.validation_errors.append("Task must have at least one step")
            return
        
        step_ids = set()
        
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                self.validation_errors.append(f"Step {i+1} must be a dictionary")
                continue
            
            # Validate required step fields
            for field_name, expected_type in self.REQUIRED_STEP_FIELDS.items():
                if field_name not in step:
                    self.validation_errors.append(f"Step {i+1}: Missing required field '{field_name}'")
                    continue
                
                if not isinstance(step[field_name], expected_type):
                    self.validation_errors.append(
                        f"Step {i+1}: Field '{field_name}' must be of type {expected_type.__name__}, "
                        f"got {type(step[field_name]).__name__}"
                    )
            
            # Validate step_id uniqueness and sequence
            if 'step_id' in step:
                step_id = step['step_id']
                if step_id in step_ids:
                    self.validation_errors.append(f"Duplicate step_id: {step_id}")
                step_ids.add(step_id)
                
                if step_id != i + 1:
                    self.validation_errors.append(
                        f"Step {i+1}: step_id should be {i+1}, got {step_id}"
                    )
            
            # Validate list fields are not empty
            list_fields = ['tools_needed', 'completion_indicators', 'visual_cues']
            for field_name in list_fields:
                if field_name in step and isinstance(step[field_name], list):
                    if len(step[field_name]) == 0:
                        self.validation_errors.append(
                            f"Step {i+1}: {field_name} should not be empty"
                        )
                    
                    # Check that all items in lists are strings
                    for item in step[field_name]:
                        if not isinstance(item, str):
                            self.validation_errors.append(
                                f"Step {i+1}: All items in {field_name} must be strings"
                            )
                            break
    
    def validate_task_data(self, task_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate task data dictionary directly (for testing)
        
        Args:
            task_data: Task data dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.validation_errors = []
        
        if not isinstance(task_data, dict):
            self.validation_errors.append("Task data must be a dictionary")
            return False, self.validation_errors
        
        self._validate_task_structure(task_data)
        
        if 'steps' in task_data:
            self._validate_steps(task_data['steps'])
        
        return len(self.validation_errors) == 0, self.validation_errors


def validate_task_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate a task file
    
    Args:
        file_path: Path to the task YAML file
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = TaskKnowledgeValidator()
    return validator.validate_task_file(file_path)


def validate_task_data(task_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate task data
    
    Args:
        task_data: Task data dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = TaskKnowledgeValidator()
    return validator.validate_task_data(task_data)