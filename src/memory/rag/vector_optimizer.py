"""
Vector Optimization Module for RAG System

This module provides advanced vector optimization features including:
1. Precomputed embeddings management
2. Vector cache optimization
3. Fast retrieval mechanisms
4. Vector update and maintenance interfaces
"""

import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import pickle
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
try:
    from .task_loader import TaskKnowledge, TaskStep
    from .vector_search import ChromaVectorSearchEngine
except ImportError:
    # Handle standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from src.memory.rag.task_loader import TaskKnowledge, TaskStep
    from src.memory.rag.vector_search import ChromaVectorSearchEngine

logger = logging.getLogger(__name__)


@dataclass
class VectorCacheStats:
    """Statistics for vector cache performance"""
    total_embeddings: int
    cache_hits: int
    cache_misses: int
    last_updated: str
    precompute_time: float
    average_search_time: float
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_requests = self.cache_hits + self.cache_misses
        return self.cache_hits / max(1, total_requests)


class VectorOptimizer:
    """
    Advanced vector optimization system for RAG
    
    Provides precomputation, caching, and performance optimization
    for vector embeddings and search operations.
    """
    
    def __init__(self, 
                 vector_engine: ChromaVectorSearchEngine,
                 cache_dir: str = "cache/vector_optimizer",
                 enable_precompute: bool = True):
        """
        Initialize the vector optimizer
        
        Args:
            vector_engine: ChromaDB vector search engine to optimize
            cache_dir: Directory for optimization cache files
            enable_precompute: Whether to enable precomputation
        """
        self.vector_engine = vector_engine
        self.cache_dir = Path(cache_dir)
        self.enable_precompute = enable_precompute
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache management
        self.embedding_cache: Dict[str, Any] = {}
        self.cache_metadata: Dict[str, Dict] = {}
        
        # Performance tracking
        self.stats = VectorCacheStats(
            total_embeddings=0,
            cache_hits=0,
            cache_misses=0,
            last_updated="",
            precompute_time=0.0,
            average_search_time=0.0
        )
        
        # Thread safety
        self._cache_lock = threading.RLock()
        
        logger.info(f"Vector optimizer initialized with cache dir: {cache_dir}")
    
    def precompute_all_embeddings(self, task_knowledge_dict: Dict[str, TaskKnowledge]) -> bool:
        """
        Precompute embeddings for all tasks during system startup
        
        Args:
            task_knowledge_dict: Dictionary of task knowledge objects
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enable_precompute:
            logger.info("Precomputation disabled, skipping...")
            return True
        
        logger.info("Starting precomputation of all embeddings...")
        start_time = time.time()
        
        try:
            total_steps = sum(len(task.steps) for task in task_knowledge_dict.values())
            processed_steps = 0
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit precomputation tasks
                future_to_task = {}
                
                for task_name, task in task_knowledge_dict.items():
                    future = executor.submit(self._precompute_task_embeddings, task_name, task)
                    future_to_task[future] = task_name
                
                # Process completed tasks
                for future in as_completed(future_to_task):
                    task_name = future_to_task[future]
                    try:
                        step_count = future.result()
                        processed_steps += step_count
                        logger.debug(f"Precomputed embeddings for task: {task_name} ({step_count} steps)")
                    except Exception as e:
                        logger.error(f"Failed to precompute embeddings for task {task_name}: {str(e)}")
            
            # Update statistics
            precompute_time = time.time() - start_time
            self.stats.total_embeddings = processed_steps
            self.stats.precompute_time = precompute_time
            self.stats.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Save cache metadata
            self._save_cache_metadata()
            
            logger.info(f"Precomputation completed in {precompute_time:.2f}s for {processed_steps} embeddings")
            return True
            
        except Exception as e:
            logger.error(f"Precomputation failed: {str(e)}")
            return False
    
    def _precompute_task_embeddings(self, task_name: str, task: TaskKnowledge) -> int:
        """
        Precompute embeddings for a single task
        
        Args:
            task_name: Name of the task
            task: TaskKnowledge object
            
        Returns:
            Number of steps processed
        """
        with self._cache_lock:
            # Check if already cached
            cache_key = f"{task_name}_embeddings"
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            if cache_file.exists():
                # Load from cache
                try:
                    with open(cache_file, 'rb') as f:
                        cached_embeddings = pickle.load(f)
                    
                    self.embedding_cache[cache_key] = cached_embeddings
                    self.cache_metadata[cache_key] = {
                        "task_name": task_name,
                        "step_count": len(task.steps),
                        "cached_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "cache_file": str(cache_file)
                    }
                    
                    logger.debug(f"Loaded cached embeddings for {task_name}")
                    return len(task.steps)
                    
                except Exception as e:
                    logger.warning(f"Failed to load cached embeddings for {task_name}: {str(e)}")
            
            # Generate new embeddings
            embeddings = {}
            documents = []
            
            for step in task.steps:
                # Create combined text for embedding (same as vector_search.py)
                combined_text = self._create_step_text_for_embedding(step)
                documents.append(combined_text)
            
            # Generate embeddings in batch
            if documents:
                batch_embeddings = self.vector_engine.model.encode(
                    documents, 
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                
                # Store embeddings with step IDs
                for i, step in enumerate(task.steps):
                    embeddings[step.step_id] = batch_embeddings[i]
            
            # Cache the embeddings in memory
            self.embedding_cache[cache_key] = embeddings
            
            logger.debug(f"Cached {len(embeddings)} embeddings for {task_name} in memory")
            
            # Save to disk
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(embeddings, f)
                
                self.cache_metadata[cache_key] = {
                    "task_name": task_name,
                    "step_count": len(task.steps),
                    "cached_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "cache_file": str(cache_file)
                }
                
            except Exception as e:
                logger.warning(f"Failed to save embeddings cache for {task_name}: {str(e)}")
            
            return len(task.steps)
    
    def _create_step_text_for_embedding(self, step: TaskStep) -> str:
        """
        Create combined text from step information for embedding generation
        (Same logic as in vector_search.py)
        """
        components = [
            step.task_description,
            step.title,
            " ".join(step.visual_cues),
            " ".join(step.tools_needed),
            " ".join(step.completion_indicators)
        ]
        
        combined = " ".join(components)
        return combined.strip()
    
    def get_cached_embedding(self, task_name: str, step_id: int) -> Optional[Any]:
        """
        Retrieve cached embedding for a specific step
        
        Args:
            task_name: Name of the task
            step_id: ID of the step
            
        Returns:
            Cached embedding or None if not found
        """
        with self._cache_lock:
            cache_key = f"{task_name}_embeddings"
            
            # Check memory cache first
            if cache_key in self.embedding_cache:
                embeddings = self.embedding_cache[cache_key]
                if step_id in embeddings:
                    self.stats.cache_hits += 1
                    return embeddings[step_id]
            
            # Try to load from disk cache
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        embeddings = pickle.load(f)
                    
                    # Store in memory cache
                    self.embedding_cache[cache_key] = embeddings
                    
                    if step_id in embeddings:
                        self.stats.cache_hits += 1
                        return embeddings[step_id]
                        
                except Exception as e:
                    logger.warning(f"Failed to load cached embeddings: {str(e)}")
            
            self.stats.cache_misses += 1
            return None
    
    def update_task_embeddings(self, task_name: str, task: TaskKnowledge) -> bool:
        """
        Update embeddings for a specific task
        
        Args:
            task_name: Name of the task to update
            task: Updated TaskKnowledge object
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Updating embeddings for task: {task_name}")
        
        try:
            # Remove old cache
            self.invalidate_task_cache(task_name)
            
            # Precompute new embeddings
            step_count = self._precompute_task_embeddings(task_name, task)
            
            # Update ChromaDB as well
            self.vector_engine.add_task_knowledge(task)
            
            logger.info(f"Successfully updated embeddings for {task_name} ({step_count} steps)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update embeddings for {task_name}: {str(e)}")
            return False
    
    def invalidate_task_cache(self, task_name: str) -> None:
        """
        Invalidate cache for a specific task
        
        Args:
            task_name: Name of the task to invalidate
        """
        with self._cache_lock:
            cache_key = f"{task_name}_embeddings"
            
            # Remove from memory cache
            if cache_key in self.embedding_cache:
                del self.embedding_cache[cache_key]
            
            if cache_key in self.cache_metadata:
                del self.cache_metadata[cache_key]
            
            # Remove cache file
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    logger.debug(f"Removed cache file for {task_name}")
                except Exception as e:
                    logger.warning(f"Failed to remove cache file for {task_name}: {str(e)}")
    
    def clear_all_cache(self) -> None:
        """
        Clear all cached embeddings
        """
        logger.info("Clearing all vector cache...")
        
        with self._cache_lock:
            # Clear memory cache
            self.embedding_cache.clear()
            self.cache_metadata.clear()
            
            # Remove cache files
            try:
                for cache_file in self.cache_dir.glob("*.pkl"):
                    cache_file.unlink()
                
                # Reset statistics
                self.stats = VectorCacheStats(
                    total_embeddings=0,
                    cache_hits=0,
                    cache_misses=0,
                    last_updated="",
                    precompute_time=0.0,
                    average_search_time=0.0
                )
                
                logger.info("All vector cache cleared")
                
            except Exception as e:
                logger.error(f"Failed to clear cache files: {str(e)}")
    
    def _save_cache_metadata(self) -> None:
        """
        Save cache metadata to disk
        """
        metadata_file = self.cache_dir / "cache_metadata.json"
        
        try:
            metadata = {
                "stats": asdict(self.stats),
                "cache_info": self.cache_metadata
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to save cache metadata: {str(e)}")
    
    def load_cache_metadata(self) -> bool:
        """
        Load cache metadata from disk
        
        Returns:
            True if successful, False otherwise
        """
        metadata_file = self.cache_dir / "cache_metadata.json"
        
        if not metadata_file.exists():
            return False
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Restore statistics
            stats_data = metadata.get("stats", {})
            self.stats = VectorCacheStats(**stats_data)
            
            # Restore cache metadata
            self.cache_metadata = metadata.get("cache_info", {})
            
            logger.info("Cache metadata loaded successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load cache metadata: {str(e)}")
            return False
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive optimization statistics
        
        Returns:
            Dictionary with optimization metrics
        """
        return {
            "cache_stats": asdict(self.stats),
            "memory_cache_size": len(self.embedding_cache),
            "cached_tasks": len(self.cache_metadata),
            "cache_directory": str(self.cache_dir),
            "precompute_enabled": self.enable_precompute,
            "cache_files": len(list(self.cache_dir.glob("*.pkl")))
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the vector optimizer
        
        Returns:
            Dictionary with health status
        """
        health = {
            "status": "healthy",
            "issues": [],
            "warnings": []
        }
        
        try:
            # Check cache directory
            if not self.cache_dir.exists():
                health["issues"].append("Cache directory does not exist")
                health["status"] = "unhealthy"
            
            # Check cache consistency
            memory_cache_count = len(self.embedding_cache)
            file_cache_count = len(list(self.cache_dir.glob("*.pkl")))
            
            if memory_cache_count != file_cache_count:
                health["warnings"].append(f"Cache inconsistency: memory={memory_cache_count}, files={file_cache_count}")
            
            # Check hit rate
            if self.stats.hit_rate < 0.5 and (self.stats.cache_hits + self.stats.cache_misses) > 10:
                health["warnings"].append(f"Low cache hit rate: {self.stats.hit_rate:.1%}")
            
            if health["warnings"] and health["status"] == "healthy":
                health["status"] = "warning"
                
        except Exception as e:
            health["status"] = "error"
            health["issues"].append(f"Health check failed: {str(e)}")
        
        return health
    
    def __repr__(self) -> str:
        return (f"VectorOptimizer(cached_tasks={len(self.cache_metadata)}, "
                f"hit_rate={self.stats.hit_rate:.1%})")