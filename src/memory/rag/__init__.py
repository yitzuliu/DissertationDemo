"""
RAG (Retrieval-Augmented Generation) Long-term Memory Module

This module implements the knowledge repository for structured task information.
It serves as the "knowledge manual" containing task steps, tools, completion indicators,
and visual cues for intelligent semantic matching.
"""

try:
    from .knowledge_base import RAGKnowledgeBase
    from .task_loader import TaskKnowledgeLoader, TaskKnowledge, TaskStep
    from .vector_search import ChromaVectorSearchEngine, MatchResult
    from .vector_optimizer import VectorOptimizer
    from .validation import TaskKnowledgeValidator, validate_task_file
    from .performance_tester import PerformanceTester
    from .task_models import TaskStep, TaskKnowledge, MatchResult
except ImportError:
    # Handle standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from src.memory.rag.knowledge_base import RAGKnowledgeBase
    from src.memory.rag.task_loader import TaskKnowledgeLoader, TaskKnowledge, TaskStep
    from src.memory.rag.vector_search import ChromaVectorSearchEngine, MatchResult
    from src.memory.rag.vector_optimizer import VectorOptimizer
    from src.memory.rag.validation import TaskKnowledgeValidator, validate_task_file
    from src.memory.rag.performance_tester import PerformanceTester
    from src.memory.rag.task_models import TaskStep, TaskKnowledge, MatchResult

__all__ = [
    'RAGKnowledgeBase',
    'TaskKnowledgeLoader',
    'TaskKnowledge',
    'TaskStep',
    'ChromaVectorSearchEngine',
    'MatchResult',
    'VectorOptimizer',
    'TaskKnowledgeValidator',
    'validate_task_file',
    'PerformanceTester',
    'TaskStep',
    'TaskKnowledge',
    'MatchResult'
]