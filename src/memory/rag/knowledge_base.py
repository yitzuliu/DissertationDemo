"""
RAG Knowledge Base Implementation

Main RAG system that combines task knowledge loading with vector search capabilities.
This serves as the primary interface for the memory system's long-term knowledge storage.
"""

from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
from .task_loader import TaskKnowledgeLoader, TaskKnowledge
from .vector_search import VectorSearchEngine, MatchResult
from .validation import validate_task_file

logger = logging.getLogger(__name__)


class RAGKnowledgeBase:
    """
    Main RAG Knowledge Base for the memory system
    
    This class provides the primary interface for:
    1. Loading and managing task knowledge
    2. Performing semantic search on task steps
    3. Matching VLM observations to task steps
    4. Caching and performance optimization
    """
    
    def __init__(self, 
                 tasks_directory: str = "data/tasks",
                 model_name: str = "all-MiniLM-L6-v2",
                 cache_dir: str = "cache/embeddings"):
        """
        Initialize the RAG Knowledge Base
        
        Args:
            tasks_directory: Directory containing task YAML files
            model_name: Sentence transformer model for embeddings
            cache_dir: Directory for caching embeddings
        """
        self.tasks_directory = Path(tasks_directory)
        
        # Initialize components
        self.task_loader = TaskKnowledgeLoader(self.tasks_directory)
        self.vector_engine = VectorSearchEngine(model_name, cache_dir)
        
        # Track loaded tasks
        self.loaded_tasks: Dict[str, TaskKnowledge] = {}
        self.is_initialized = False
        
        logger.info(f"RAG Knowledge Base initialized with tasks directory: {tasks_directory}")
    
    def initialize(self, precompute_embeddings: bool = True) -> None:
        """
        Initialize the knowledge base by loading all tasks
        
        Args:
            precompute_embeddings: Whether to precompute embeddings during initialization
        """
        logger.info("Initializing RAG Knowledge Base...")
        
        try:
            # Load all tasks from directory
            self.loaded_tasks = self.task_loader.load_all_tasks()
            
            if not self.loaded_tasks:
                logger.warning("No tasks loaded from directory")
                return
            
            # Add tasks to vector search engine
            for task_name, task in self.loaded_tasks.items():
                self.vector_engine.add_task_knowledge(task)
            
            # Optionally precompute embeddings
            if precompute_embeddings:
                self.vector_engine.precompute_all_embeddings()
            
            self.is_initialized = True
            logger.info(f"RAG Knowledge Base initialized with {len(self.loaded_tasks)} tasks")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Knowledge Base: {str(e)}")
            raise
    
    def find_matching_step(self, observation: str, task_name: str = None) -> MatchResult:
        """
        Find the best matching task step for a VLM observation
        
        This is the main method used by the State Tracker to match
        VLM observations to task steps.
        
        Args:
            observation: VLM observation text
            task_name: Optional specific task to search in
            
        Returns:
            MatchResult with the best matching step
        """
        if not self.is_initialized:
            raise RuntimeError("RAG Knowledge Base not initialized. Call initialize() first.")
        
        if not observation or not observation.strip():
            logger.warning("Empty observation provided to find_matching_step")
            return self._create_no_match_result()
        
        try:
            # Get best match from vector search
            matches = self.vector_engine.find_best_match(
                observation=observation,
                task_name=task_name,
                top_k=1
            )
            
            if matches:
                best_match = matches[0]
                logger.debug(f"Found match: step {best_match.step_id} with similarity {best_match.similarity:.3f}")
                return best_match
            else:
                logger.warning(f"No matches found for observation: {observation[:50]}...")
                return self._create_no_match_result()
                
        except Exception as e:
            logger.error(f"Error in find_matching_step: {str(e)}")
            return self._create_no_match_result()
    
    def find_multiple_matches(self, 
                            observation: str, 
                            top_k: int = 3,
                            task_name: str = None) -> List[MatchResult]:
        """
        Find multiple matching task steps for a VLM observation
        
        Args:
            observation: VLM observation text
            top_k: Number of top matches to return
            task_name: Optional specific task to search in
            
        Returns:
            List of MatchResult objects sorted by similarity
        """
        if not self.is_initialized:
            raise RuntimeError("RAG Knowledge Base not initialized. Call initialize() first.")
        
        try:
            matches = self.vector_engine.find_best_match(
                observation=observation,
                task_name=task_name,
                top_k=top_k
            )
            
            logger.debug(f"Found {len(matches)} matches for observation")
            return matches
            
        except Exception as e:
            logger.error(f"Error in find_multiple_matches: {str(e)}")
            return []
    
    def get_step_details(self, task_name: str, step_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific step
        
        Args:
            task_name: Name of the task
            step_id: ID of the step
            
        Returns:
            Dictionary with step details or None if not found
        """
        if task_name not in self.loaded_tasks:
            return None
        
        task = self.loaded_tasks[task_name]
        step = task.get_step(step_id)
        
        if not step:
            return None
        
        return {
            "step_id": step.step_id,
            "title": step.title,
            "task_description": step.task_description,
            "tools_needed": step.tools_needed,
            "completion_indicators": step.completion_indicators,
            "visual_cues": step.visual_cues,
            "estimated_duration": step.estimated_duration,
            "safety_notes": step.safety_notes
        }
    
    def get_next_step_info(self, task_name: str, current_step_id: int) -> Optional[Dict[str, Any]]:
        """
        Get information about the next step in a task
        
        Args:
            task_name: Name of the task
            current_step_id: Current step ID
            
        Returns:
            Dictionary with next step details or None if not found
        """
        return self.get_step_details(task_name, current_step_id + 1)
    
    def get_task_summary(self, task_name: str) -> Optional[Dict[str, Any]]:
        """
        Get summary information about a task
        
        Args:
            task_name: Name of the task
            
        Returns:
            Dictionary with task summary or None if not found
        """
        if task_name not in self.loaded_tasks:
            return None
        
        return self.task_loader.get_task_summary(task_name)
    
    def get_all_tasks(self) -> List[str]:
        """
        Get list of all loaded task names
        
        Returns:
            List of task names
        """
        return list(self.loaded_tasks.keys())
    
    def reload_task(self, task_name: str) -> bool:
        """
        Reload a specific task from file
        
        Args:
            task_name: Name of the task to reload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear from cache first
            if task_name in self.loaded_tasks:
                del self.loaded_tasks[task_name]
            
            # Reload from file
            task = self.task_loader.load_task(task_name)
            if task:
                self.loaded_tasks[task_name] = task
                self.vector_engine.add_task_knowledge(task)
                logger.info(f"Successfully reloaded task: {task_name}")
                return True
            else:
                logger.error(f"Failed to reload task: {task_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error reloading task {task_name}: {str(e)}")
            return False
    
    def add_new_task(self, task_file_path: str) -> bool:
        """
        Add a new task from a YAML file
        
        Args:
            task_file_path: Path to the task YAML file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate the task file first
            if not validate_task_file(task_file_path):
                logger.error(f"Task file validation failed: {task_file_path}")
                return False
            
            # Load the task
            task = self.task_loader.load_task_from_file(task_file_path)
            if not task:
                logger.error(f"Failed to load task from file: {task_file_path}")
                return False
            
            # Add to knowledge base
            self.loaded_tasks[task.task_name] = task
            self.vector_engine.add_task_knowledge(task)
            
            logger.info(f"Successfully added new task: {task.task_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding new task from {task_file_path}: {str(e)}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics
        
        Returns:
            Dictionary with system performance and usage statistics
        """
        stats = {
            "knowledge_base": {
                "total_tasks": len(self.loaded_tasks),
                "total_steps": sum(len(task.steps) for task in self.loaded_tasks.values()),
                "is_initialized": self.is_initialized,
                "tasks_directory": str(self.tasks_directory)
            },
            "vector_engine": self.vector_engine.get_performance_stats(),
            "task_loader": self.task_loader.get_performance_stats()
        }
        
        return stats
    
    def _create_no_match_result(self) -> MatchResult:
        """
        Create a MatchResult for when no match is found
        
        Returns:
            MatchResult with zero similarity and empty data
        """
        return MatchResult(
            step_id=0,
            task_description="No matching step found",
            tools_needed=[],
            completion_indicators=[],
            visual_cues=[],
            similarity=0.0,
            confidence_level="none",
            matched_cues=[],
            task_name=""
        )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the knowledge base
        
        Returns:
            Dictionary with health status information
        """
        health = {
            "status": "healthy",
            "issues": [],
            "warnings": []
        }
        
        try:
            # Check initialization
            if not self.is_initialized:
                health["issues"].append("Knowledge base not initialized")
                health["status"] = "unhealthy"
            
            # Check if tasks are loaded
            if not self.loaded_tasks:
                health["issues"].append("No tasks loaded")
                health["status"] = "unhealthy"
            
            # Check vector engine
            vector_stats = self.vector_engine.get_performance_stats()
            if vector_stats["loaded_tasks"] == 0:
                health["issues"].append("No tasks in vector engine")
                health["status"] = "unhealthy"
            
            # Check for missing embeddings
            for task_name in self.loaded_tasks:
                if task_name not in self.vector_engine.task_embeddings:
                    health["warnings"].append(f"Missing embeddings for task: {task_name}")
            
            # Performance warnings
            if vector_stats["cache_hit_rate"] < 0.5 and vector_stats["total_searches"] > 10:
                health["warnings"].append("Low cache hit rate detected")
            
            if health["warnings"] and health["status"] == "healthy":
                health["status"] = "warning"
                
        except Exception as e:
            health["status"] = "error"
            health["issues"].append(f"Health check failed: {str(e)}")
        
        return health
    
    def clear_all_caches(self) -> None:
        """
        Clear all caches in the system
        """
        self.vector_engine.clear_cache()
        self.task_loader.clear_cache()
        logger.info("All caches cleared")
    
    def __repr__(self) -> str:
        return (f"RAGKnowledgeBase(tasks={len(self.loaded_tasks)}, "
                f"initialized={self.is_initialized})")