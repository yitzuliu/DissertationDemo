"""
State Tracker Core System

This module implements the core State Tracker that receives VLM text output
and matches it with RAG knowledge base to track current task state.

Part of the continuous state awareness loop:
C: State Tracker receives VLM text
D: Match with RAG knowledge base  
E: Store structured results
F: Update current state
"""

import logging
import re
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

# Import existing RAG system
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from memory.rag.knowledge_base import RAGKnowledgeBase

logger = logging.getLogger(__name__)

@dataclass
class StateRecord:
    """Structured record for state tracking"""
    timestamp: datetime
    vlm_text: str
    matched_step: Optional[Dict[str, Any]]
    confidence: float
    task_id: Optional[str]
    step_index: Optional[int]

class StateTracker:
    """
    Core State Tracker system that processes VLM output and maintains task state.
    
    This class implements the continuous state awareness loop by:
    1. Receiving VLM text output
    2. Cleaning and normalizing the text
    3. Matching with RAG knowledge base
    4. Updating current state
    """
    
    def __init__(self):
        """Initialize State Tracker with RAG knowledge base"""
        self.rag_kb = RAGKnowledgeBase()
        self.rag_kb.initialize(precompute_embeddings=True)
        self.current_state: Optional[StateRecord] = None
        self.confidence_threshold = 0.7
        self.state_history: List[StateRecord] = []
        self.max_history_size = 10  # Basic sliding window
        
        logger.info("State Tracker initialized")
    
    def clean_vlm_text(self, vlm_text: str) -> str:
        """
        Clean and standardize VLM text output.
        
        Handles:
        - Empty or None input
        - Garbled text
        - Special characters
        - Excessive whitespace
        
        Args:
            vlm_text: Raw VLM text output
            
        Returns:
            Cleaned and normalized text
        """
        if not vlm_text or not isinstance(vlm_text, str):
            return ""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', vlm_text.strip())
        
        # Remove common VLM artifacts
        cleaned = re.sub(r'[^\w\s\.,!?-]', '', cleaned)
        
        # Handle empty result after cleaning
        if len(cleaned.strip()) < 3:
            logger.warning(f"VLM text too short after cleaning: '{cleaned}'")
            return ""
        
        return cleaned
    
    async def process_vlm_response(self, vlm_text: str) -> bool:
        """
        Process VLM response and update state.
        
        This is the main entry point for the continuous state awareness loop.
        
        Args:
            vlm_text: Raw VLM text output from /v1/chat/completions
            
        Returns:
            True if state was updated, False otherwise
        """
        try:
            # Step 1: Clean VLM text
            cleaned_text = self.clean_vlm_text(vlm_text)
            if not cleaned_text:
                logger.warning("Empty VLM text after cleaning, skipping")
                return False
            
            # Step 2: Match with RAG knowledge base
            match_result = self.rag_kb.find_matching_step(cleaned_text)
            
            if not match_result:
                logger.info("No match found in RAG knowledge base")
                return False
            
            # Step 3: Create state record
            state_record = StateRecord(
                timestamp=datetime.now(),
                vlm_text=cleaned_text,
                matched_step=match_result.to_dict() if hasattr(match_result, 'to_dict') else vars(match_result),
                confidence=match_result.similarity,
                task_id=match_result.task_name,
                step_index=match_result.step_id
            )
            
            # Step 4: Update state if confidence is sufficient
            if state_record.confidence >= self.confidence_threshold:
                self.current_state = state_record
                logger.info(f"State updated: task={state_record.task_id}, step={state_record.step_index}, confidence={state_record.confidence:.2f}")
                
                # Add to history (basic sliding window)
                self.state_history.append(state_record)
                if len(self.state_history) > self.max_history_size:
                    self.state_history.pop(0)
                
                return True
            else:
                logger.info(f"Confidence too low ({state_record.confidence:.2f}), keeping current state")
                return False
                
        except Exception as e:
            logger.error(f"Error processing VLM response: {e}")
            return False
    
    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """
        Get current state information.
        
        Returns:
            Current state as dictionary or None if no state
        """
        if not self.current_state:
            return None
        
        return {
            'timestamp': self.current_state.timestamp.isoformat(),
            'task_id': self.current_state.task_id,
            'step_index': self.current_state.step_index,
            'confidence': self.current_state.confidence,
            'matched_step': self.current_state.matched_step,
            'vlm_text': self.current_state.vlm_text
        }
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get summary of state tracker status.
        
        Returns:
            Summary information about state tracker
        """
        return {
            'has_current_state': self.current_state is not None,
            'history_size': len(self.state_history),
            'confidence_threshold': self.confidence_threshold,
            'current_state': self.get_current_state()
        }

# Global state tracker instance
_state_tracker_instance: Optional[StateTracker] = None

def get_state_tracker() -> StateTracker:
    """Get or create global state tracker instance"""
    global _state_tracker_instance
    if _state_tracker_instance is None:
        _state_tracker_instance = StateTracker()
    return _state_tracker_instance