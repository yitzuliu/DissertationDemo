"""
RAG Vector Search Engine with ChromaDB

Implements high-speed semantic vector search for task knowledge matching.
This module provides the core functionality to match VLM observations
to task steps using ChromaDB for efficient vector storage and retrieval.
"""

import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path
import time
import uuid
from .task_loader import TaskKnowledge, TaskStep

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """
    Result of matching a VLM observation to a task step
    
    This contains all information needed by the State Tracker
    to update the current state.
    """
    step_id: int
    task_description: str
    tools_needed: List[str]
    completion_indicators: List[str]
    visual_cues: List[str]
    estimated_duration: str
    safety_notes: List[str]
    similarity: float
    confidence_level: str  # "high", "medium", "low", "none"
    matched_cues: List[str]
    task_name: str
    
    # Additional properties for State Tracker compatibility
    @property
    def step_title(self) -> str:
        """Get step title from task description"""
        return self.task_description.split('.')[0] if self.task_description else ""
    
    @property
    def step_description(self) -> str:
        """Get step description"""
        return self.task_description
    
    def __post_init__(self):
        """Determine confidence level based on similarity score"""
        if self.similarity >= 0.7:
            self.confidence_level = "high"
        elif self.similarity >= 0.5:
            self.confidence_level = "medium"
        elif self.similarity >= 0.35:
            self.confidence_level = "low"
        else:
            self.confidence_level = "none"
    
    @property
    def is_reliable(self) -> bool:
        """Check if this match is reliable enough for state updates"""
        return self.confidence_level in ["high", "medium"]
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high confidence match"""
        return self.confidence_level == "high"


class ChromaVectorSearchEngine:
    """
    High-speed semantic vector search engine using ChromaDB
    
    This class handles:
    1. ChromaDB collection management
    2. Embedding generation and storage
    3. Vector similarity search
    4. Fast retrieval of best matching steps
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 persist_directory: str = "cache/chromadb",
                 collection_name: str = "task_knowledge"):
        """
        Initialize the ChromaDB vector search engine
        
        Args:
            model_name: Name of the sentence transformer model to use
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the ChromaDB collection
        """
        self.model_name = model_name
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        
        # Create persist directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB with persist directory: {persist_directory}")
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Load the sentence transformer model
        logger.info(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        # Storage for task knowledge
        self.task_knowledge: Dict[str, TaskKnowledge] = {}
        
        # Performance tracking
        self.search_count = 0
        self.total_search_time = 0.0
    
    def add_task_knowledge(self, task: TaskKnowledge) -> None:
        """
        Add task knowledge and store embeddings in ChromaDB
        
        Args:
            task: TaskKnowledge object to add
        """
        logger.info(f"Adding task knowledge to ChromaDB: {task.task_name}")
        
        self.task_knowledge[task.task_name] = task
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for step in task.steps:
            # Create combined text for embedding
            combined_text = self._create_step_text_for_embedding(step)
            documents.append(combined_text)
            
            # Create metadata
            metadata = {
                "task_name": task.task_name,
                "step_id": step.step_id,
                "title": step.title,
                "task_description": step.task_description,
                "tools_needed": ",".join(step.tools_needed),
                "completion_indicators": ",".join(step.completion_indicators),
                "visual_cues": ",".join(step.visual_cues),
                "estimated_duration": step.estimated_duration,
                "safety_notes": ",".join(step.safety_notes)
            }
            metadatas.append(metadata)
            
            # Create unique ID
            doc_id = f"{task.task_name}_step_{step.step_id}"
            ids.append(doc_id)
        
        # Generate embeddings and add to collection (optimized)
        embeddings = self.model.encode(documents, show_progress_bar=False)
        if hasattr(embeddings, 'tolist'):
            embeddings = embeddings.tolist()
        else:
            embeddings = embeddings
        
        # Add to ChromaDB collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} steps to ChromaDB for task: {task.task_name}")
    
    def _create_step_text_for_embedding(self, step: TaskStep) -> str:
        """
        Create combined text from step information for embedding generation
        
        Args:
            step: TaskStep object
            
        Returns:
            Combined text string optimized for semantic matching
        """
        # Combine different aspects of the step with appropriate weighting
        components = [
            step.task_description,  # Primary description
            step.title,  # Step title
            " ".join(step.visual_cues),  # Visual cues (important for VLM matching)
            " ".join(step.tools_needed),  # Tools
            " ".join(step.completion_indicators)  # Completion indicators
        ]
        
        # Join with spaces and clean up
        combined = " ".join(components)
        return combined.strip()
    
    def find_best_match(self, 
                       observation: str, 
                       task_name: str = None,
                       top_k: int = 1) -> List[MatchResult]:
        """
        Find the best matching task step(s) for a VLM observation using ChromaDB
        
        Args:
            observation: VLM observation text
            task_name: Optional specific task to search in
            top_k: Number of top matches to return
            
        Returns:
            List of MatchResult objects sorted by similarity
        """
        start_time = time.time()
        self.search_count += 1
        
        if not observation or not observation.strip():
            logger.warning("Empty observation provided to find_best_match")
            return []
        
        try:
            # Generate embedding for the observation (optimized for single query)
            query_embedding = self.model.encode(observation, show_progress_bar=False)
            
            # Prepare query filters
            where_filter = None
            if task_name:
                where_filter = {"task_name": task_name}
            
            # Query ChromaDB with optimized parameters
            if hasattr(query_embedding, 'tolist'):
                query_emb = query_embedding.tolist()
            else:
                query_emb = query_embedding
                
            results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=top_k,
                where=where_filter,
                include=["metadatas", "distances"]
            )
            
            # Convert results to MatchResult objects
            matches = []
            
            if results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    # ChromaDB returns distances, convert to similarity (1 - distance)
                    distance = results["distances"][0][i]
                    similarity = max(0.0, 1.0 - distance)
                    
                    # Parse metadata back to lists
                    tools_needed = metadata["tools_needed"].split(",") if metadata["tools_needed"] else []
                    completion_indicators = metadata["completion_indicators"].split(",") if metadata["completion_indicators"] else []
                    visual_cues = metadata["visual_cues"].split(",") if metadata["visual_cues"] else []
                    safety_notes = metadata["safety_notes"].split(",") if metadata["safety_notes"] else []
                    
                    # Find matched visual cues
                    matched_cues = self._find_matched_cues(observation, visual_cues)
                    
                    match_result = MatchResult(
                        step_id=int(metadata["step_id"]),
                        task_description=metadata["task_description"],
                        tools_needed=tools_needed,
                        completion_indicators=completion_indicators,
                        visual_cues=visual_cues,
                        estimated_duration=metadata.get("estimated_duration", ""),
                        safety_notes=safety_notes,
                        similarity=similarity,
                        confidence_level="",  # Will be set in __post_init__
                        matched_cues=matched_cues,
                        task_name=metadata["task_name"]
                    )
                    
                    matches.append(match_result)
            
            # Track performance
            search_time = time.time() - start_time
            self.total_search_time += search_time
            
            logger.debug(f"ChromaDB search completed in {search_time*1000:.1f}ms, found {len(matches)} matches")
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in ChromaDB search: {str(e)}")
            return []
    
    def _find_matched_cues(self, observation: str, visual_cues: List[str]) -> List[str]:
        """
        Find which visual cues might have contributed to the match
        
        Args:
            observation: VLM observation text
            visual_cues: List of visual cues for the step
            
        Returns:
            List of visual cues that appear to match the observation
        """
        observation_lower = observation.lower()
        matched = []
        
        for cue in visual_cues:
            if not cue:  # Skip empty cues
                continue
                
            # Simple keyword matching (can be improved with more sophisticated NLP)
            cue_words = cue.lower().replace('_', ' ').split()
            
            for word in cue_words:
                if len(word) > 3 and word in observation_lower:
                    matched.append(cue)
                    break
        
        return matched
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the search engine
        
        Returns:
            Dictionary with performance metrics
        """
        avg_search_time = (self.total_search_time / max(1, self.search_count)) * 1000
        
        # Get collection stats
        collection_count = self.collection.count()
        
        return {
            "total_searches": self.search_count,
            "total_search_time_ms": self.total_search_time * 1000,
            "avg_search_time_ms": avg_search_time,
            "loaded_tasks": len(self.task_knowledge),
            "total_documents": collection_count,
            "model_name": self.model_name,
            "collection_name": self.collection_name,
            "performance_target_met": avg_search_time < 10.0
        }
    
    def clear_collection(self) -> None:
        """
        Clear all data from the ChromaDB collection
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.task_knowledge.clear()
            logger.info("ChromaDB collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
    
    def reload_all_tasks(self) -> None:
        """
        Reload all tasks into ChromaDB
        This can be called when task data is updated
        """
        logger.info("Reloading all tasks into ChromaDB...")
        
        # Clear existing data
        self.clear_collection()
        
        # Re-add all tasks
        for task_name, task in self.task_knowledge.items():
            self.add_task_knowledge(task)
        
        logger.info(f"Reloaded {len(self.task_knowledge)} tasks into ChromaDB")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the vector search engine
        
        Returns:
            Dictionary with health status information
        """
        health = {
            "status": "healthy",
            "issues": [],
            "warnings": []
        }
        
        try:
            # Check ChromaDB connection
            collection_count = self.collection.count()
            
            # Check if collection has data
            if collection_count == 0:
                health["warnings"].append("ChromaDB collection is empty")
            
            # Check performance
            stats = self.get_performance_stats()
            if stats["avg_search_time_ms"] > 10.0 and self.search_count > 5:
                health["warnings"].append(f"Average search time ({stats['avg_search_time_ms']:.1f}ms) exceeds 10ms target")
            
            # Check model loading
            if not hasattr(self.model, 'encode'):
                health["issues"].append("Sentence transformer model not properly loaded")
                health["status"] = "unhealthy"
            
            if health["warnings"] and health["status"] == "healthy":
                health["status"] = "warning"
                
        except Exception as e:
            health["status"] = "error"
            health["issues"].append(f"Health check failed: {str(e)}")
        
        return health
    
    def __repr__(self) -> str:
        return (f"ChromaVectorSearchEngine(model={self.model_name}, "
                f"collection={self.collection_name}, "
                f"documents={self.collection.count()})")