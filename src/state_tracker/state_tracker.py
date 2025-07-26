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
from enum import Enum

# Import existing RAG system
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from memory.rag.knowledge_base import RAGKnowledgeBase

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Confidence level enumeration"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM" 
    LOW = "LOW"

class ActionType(Enum):
    """Action type enumeration"""
    UPDATE = "UPDATE"
    OBSERVE = "OBSERVE"
    IGNORE = "IGNORE"

@dataclass
class StateRecord:
    """Structured record for state tracking"""
    timestamp: datetime
    vlm_text: str
    matched_step: Optional[Dict[str, Any]]
    confidence: float
    task_id: Optional[str]
    step_index: Optional[int]

@dataclass
class OptimizedStateRecord:
    """Memory-optimized state record for sliding window"""
    timestamp: datetime
    confidence: float
    task_id: str
    step_index: int
    
    def get_memory_size(self) -> int:
        """Calculate approximate memory size in bytes"""
        # datetime: ~56 bytes, float: 24 bytes, str: ~50 bytes each, int: 28 bytes
        return 56 + 24 + len(self.task_id) * 2 + 28 + 50  # Approximate

@dataclass
class MemoryStats:
    """Memory usage statistics"""
    total_records: int
    memory_usage_bytes: int
    cleanup_count: int
    max_size_reached: int
    avg_record_size: float

@dataclass
class ProcessingMetrics:
    """Quantifiable metrics for each VLM processing"""
    timestamp: datetime
    vlm_input: str  # First 100 chars
    confidence_score: float
    processing_time_ms: float
    confidence_level: ConfidenceLevel
    action_taken: ActionType
    matched_task: Optional[str]
    matched_step: Optional[int]
    consecutive_low_count: int

class StateTracker:
    """
    Enhanced State Tracker with intelligent matching and fault tolerance.
    
    Implements multi-tier confidence thresholds and conservative update strategies.
    """
    
    def __init__(self):
        """Initialize State Tracker with sliding window memory management"""
        self.rag_kb = RAGKnowledgeBase()
        self.rag_kb.initialize(precompute_embeddings=True)
        self.current_state: Optional[StateRecord] = None
        
        # Multi-tier confidence thresholds
        self.high_confidence_threshold = 0.70
        self.medium_confidence_threshold = 0.40
        
        # Legacy state tracking (for compatibility)
        self.state_history: List[StateRecord] = []
        self.max_history_size = 10
        
        # Optimized sliding window
        self.sliding_window: List[OptimizedStateRecord] = []
        self.max_window_size = 50
        self.memory_limit_bytes = 1024 * 1024  # 1MB limit
        
        # Memory management stats
        self.cleanup_count = 0
        self.max_size_reached = 0
        self.failure_count = 0  # VLM failures (not stored in window)
        
        # Fault tolerance tracking
        self.consecutive_low_count = 0
        self.max_consecutive_low = 5
        
        # Metrics tracking
        self.processing_metrics: List[ProcessingMetrics] = []
        self.max_metrics_size = 100
        
        # Query processor for instant response
        from .query_processor import QueryProcessor
        self.query_processor = QueryProcessor()
        
        logger.info("Enhanced State Tracker initialized with sliding window memory management and instant response")
    
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
    
    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine confidence level based on thresholds"""
        if confidence >= self.high_confidence_threshold:
            return ConfidenceLevel.HIGH
        elif confidence >= self.medium_confidence_threshold:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _should_update_state(self, confidence: float, confidence_level: ConfidenceLevel) -> bool:
        """Conservative state update strategy"""
        if confidence_level == ConfidenceLevel.HIGH:
            return True
        elif confidence_level == ConfidenceLevel.MEDIUM:
            # Medium confidence: check consistency with recent history
            if len(self.state_history) > 0:
                recent_state = self.state_history[-1]
                # Simple consistency check - could be enhanced
                return confidence > recent_state.confidence * 0.8
            return True
        else:
            # Low confidence: no update
            return False
    
    def _handle_consecutive_low_matches(self):
        """Handle consecutive low confidence matches"""
        if self.consecutive_low_count >= self.max_consecutive_low:
            logger.warning(f"Detected {self.consecutive_low_count} consecutive low matches - system may need adjustment")
            # Could implement adaptive threshold adjustment here
            self.consecutive_low_count = 0  # Reset counter
    
    def _add_to_sliding_window(self, state_record: StateRecord):
        """Add optimized record to sliding window with memory management"""
        # Create optimized record (no VLM text, minimal data)
        optimized_record = OptimizedStateRecord(
            timestamp=state_record.timestamp,
            confidence=state_record.confidence,
            task_id=state_record.task_id,
            step_index=state_record.step_index
        )
        
        # Add to sliding window
        self.sliding_window.append(optimized_record)
        
        # Check if cleanup is needed
        self._cleanup_sliding_window()
        
        # Update max size reached
        current_size = len(self.sliding_window)
        if current_size > self.max_size_reached:
            self.max_size_reached = current_size
    
    def _cleanup_sliding_window(self):
        """Automatic cleanup of oldest records"""
        # Size-based cleanup
        if len(self.sliding_window) > self.max_window_size:
            removed_count = len(self.sliding_window) - self.max_window_size
            self.sliding_window = self.sliding_window[-self.max_window_size:]
            self.cleanup_count += removed_count
            logger.info(f"Cleaned up {removed_count} old records from sliding window")
        
        # Memory-based cleanup (if needed)
        current_memory = self._calculate_memory_usage()
        if current_memory > self.memory_limit_bytes:
            # Remove 20% of oldest records
            remove_count = max(1, len(self.sliding_window) // 5)
            self.sliding_window = self.sliding_window[remove_count:]
            self.cleanup_count += remove_count
            logger.warning(f"Memory limit exceeded, cleaned up {remove_count} records")
    
    def _calculate_memory_usage(self) -> int:
        """Calculate current memory usage of sliding window"""
        return sum(record.get_memory_size() for record in self.sliding_window)
    
    def _check_state_consistency(self, new_task_id: str, new_step_index: int) -> bool:
        """Check state consistency based on sliding window history"""
        if not self.sliding_window:
            return True  # No history to check against
        
        # Get recent records from same task
        recent_records = [r for r in self.sliding_window[-5:] if r.task_id == new_task_id]
        
        if not recent_records:
            return True  # Different task, no consistency check needed
        
        # Simple step jump detection
        last_step = recent_records[-1].step_index
        step_diff = abs(new_step_index - last_step)
        
        # Allow reasonable step progression (max jump of 3 steps)
        # But allow going back to earlier steps (user might restart)
        if step_diff > 3 and new_step_index > last_step:
            logger.warning(f"Large forward step jump detected: {last_step} -> {new_step_index}")
            return False
        
        return True
    
    def _record_vlm_failure(self, reason: str):
        """Record VLM failure without occupying window space"""
        self.failure_count += 1
        logger.info(f"VLM failure recorded: {reason} (total failures: {self.failure_count})")
    
    def _record_metrics(self, vlm_text: str, confidence: float, processing_time: float, 
                       confidence_level: ConfidenceLevel, action: ActionType,
                       matched_task: Optional[str], matched_step: Optional[int]):
        """Record quantifiable metrics"""
        metrics = ProcessingMetrics(
            timestamp=datetime.now(),
            vlm_input=vlm_text[:100],  # First 100 chars
            confidence_score=confidence,
            processing_time_ms=processing_time,
            confidence_level=confidence_level,
            action_taken=action,
            matched_task=matched_task,
            matched_step=matched_step,
            consecutive_low_count=self.consecutive_low_count
        )
        
        self.processing_metrics.append(metrics)
        if len(self.processing_metrics) > self.max_metrics_size:
            self.processing_metrics.pop(0)
    
    async def process_vlm_response(self, vlm_text: str) -> bool:
        """
        Enhanced VLM response processing with intelligent matching and fault tolerance.
        
        Args:
            vlm_text: Raw VLM text output from /v1/chat/completions
            
        Returns:
            True if state was updated, False otherwise
        """
        start_time = time.time()
        
        try:
            # Step 1: Clean VLM text
            cleaned_text = self.clean_vlm_text(vlm_text)
            if not cleaned_text:
                self._record_vlm_failure("Empty text after cleaning")
                processing_time = (time.time() - start_time) * 1000
                self._record_metrics(vlm_text, 0.0, processing_time, ConfidenceLevel.LOW, ActionType.IGNORE, None, None)
                return False
            
            # Step 2: Match with RAG knowledge base
            match_result = self.rag_kb.find_matching_step(cleaned_text)
            
            if not match_result:
                self._record_vlm_failure("No RAG match found")
                processing_time = (time.time() - start_time) * 1000
                self._record_metrics(cleaned_text, 0.0, processing_time, ConfidenceLevel.LOW, ActionType.IGNORE, None, None)
                return False
            
            # Step 3: Determine confidence level and action
            confidence = match_result.similarity
            confidence_level = self._determine_confidence_level(confidence)
            should_update = self._should_update_state(confidence, confidence_level)
            
            # Step 4: Take action based on confidence level
            action_taken = ActionType.IGNORE
            state_updated = False
            
            if should_update:
                # Check state consistency before update
                consistency_ok = self._check_state_consistency(match_result.task_name, match_result.step_id)
                
                if consistency_ok:
                    # Create and update state record
                    state_record = StateRecord(
                        timestamp=datetime.now(),
                        vlm_text=cleaned_text,
                        matched_step=vars(match_result),
                        confidence=confidence,
                        task_id=match_result.task_name,
                        step_index=match_result.step_id
                    )
                    
                    self.current_state = state_record
                    
                    # Add to legacy history (for compatibility)
                    self.state_history.append(state_record)
                    if len(self.state_history) > self.max_history_size:
                        self.state_history.pop(0)
                    
                    # Add to optimized sliding window
                    self._add_to_sliding_window(state_record)
                    
                    action_taken = ActionType.UPDATE
                    state_updated = True
                    self.consecutive_low_count = 0  # Reset on successful update
                    
                    logger.info(f"State updated: task={state_record.task_id}, step={state_record.step_index}, confidence={confidence:.2f}, level={confidence_level.value}")
                else:
                    # Consistency check failed
                    action_taken = ActionType.OBSERVE
                    logger.warning(f"State consistency check failed - observing instead of updating")
                
            elif confidence_level == ConfidenceLevel.MEDIUM:
                action_taken = ActionType.OBSERVE
                logger.info(f"Medium confidence ({confidence:.2f}) - observing without update")
                
            else:
                # Low confidence
                action_taken = ActionType.IGNORE
                self.consecutive_low_count += 1
                logger.info(f"Low confidence ({confidence:.2f}) - ignoring (consecutive: {self.consecutive_low_count})")
                
                # Handle consecutive low matches
                self._handle_consecutive_low_matches()
            
            # Step 5: Record metrics
            processing_time = (time.time() - start_time) * 1000
            self._record_metrics(
                cleaned_text, confidence, processing_time, confidence_level, action_taken,
                match_result.task_name, match_result.step_id
            )
            
            return state_updated
                
        except Exception as e:
            logger.error(f"Error processing VLM response: {e}")
            processing_time = (time.time() - start_time) * 1000
            self._record_metrics(vlm_text, 0.0, processing_time, ConfidenceLevel.LOW, ActionType.IGNORE, None, None)
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
    
    def get_processing_metrics(self) -> List[Dict[str, Any]]:
        """Get quantifiable processing metrics"""
        return [
            {
                'timestamp': m.timestamp.isoformat(),
                'vlm_input': m.vlm_input,
                'confidence_score': m.confidence_score,
                'processing_time_ms': m.processing_time_ms,
                'confidence_level': m.confidence_level.value,
                'action_taken': m.action_taken.value,
                'matched_task': m.matched_task,
                'matched_step': m.matched_step,
                'consecutive_low_count': m.consecutive_low_count
            }
            for m in self.processing_metrics
        ]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary statistics of processing metrics"""
        if not self.processing_metrics:
            return {'total_processed': 0}
        
        confidence_scores = [m.confidence_score for m in self.processing_metrics]
        processing_times = [m.processing_time_ms for m in self.processing_metrics]
        
        # Count actions
        action_counts = {}
        confidence_level_counts = {}
        for m in self.processing_metrics:
            action_counts[m.action_taken.value] = action_counts.get(m.action_taken.value, 0) + 1
            confidence_level_counts[m.confidence_level.value] = confidence_level_counts.get(m.confidence_level.value, 0) + 1
        
        return {
            'total_processed': len(self.processing_metrics),
            'avg_confidence': sum(confidence_scores) / len(confidence_scores),
            'max_confidence': max(confidence_scores),
            'min_confidence': min(confidence_scores),
            'avg_processing_time_ms': sum(processing_times) / len(processing_times),
            'max_processing_time_ms': max(processing_times),
            'min_processing_time_ms': min(processing_times),
            'action_distribution': action_counts,
            'confidence_level_distribution': confidence_level_counts,
            'consecutive_low_count': self.consecutive_low_count
        }
    
    def get_memory_stats(self) -> MemoryStats:
        """Get detailed memory usage statistics"""
        total_records = len(self.sliding_window)
        memory_usage = self._calculate_memory_usage()
        avg_size = memory_usage / total_records if total_records > 0 else 0
        
        return MemoryStats(
            total_records=total_records,
            memory_usage_bytes=memory_usage,
            cleanup_count=self.cleanup_count,
            max_size_reached=self.max_size_reached,
            avg_record_size=avg_size
        )
    
    def get_sliding_window_data(self) -> List[Dict[str, Any]]:
        """Get sliding window data for analysis"""
        return [
            {
                'timestamp': record.timestamp.isoformat(),
                'confidence': record.confidence,
                'task_id': record.task_id,
                'step_index': record.step_index
            }
            for record in self.sliding_window
        ]
    
    def get_state_history_analysis(self) -> Dict[str, Any]:
        """Analyze state history patterns"""
        if not self.sliding_window:
            return {'pattern_analysis': 'No data available'}
        
        # Task distribution
        task_counts = {}
        step_counts = {}
        confidence_levels = {'high': 0, 'medium': 0, 'low': 0}
        
        for record in self.sliding_window:
            # Count tasks
            task_counts[record.task_id] = task_counts.get(record.task_id, 0) + 1
            
            # Count steps
            step_key = f"{record.task_id}:{record.step_index}"
            step_counts[step_key] = step_counts.get(step_key, 0) + 1
            
            # Count confidence levels
            if record.confidence >= self.high_confidence_threshold:
                confidence_levels['high'] += 1
            elif record.confidence >= self.medium_confidence_threshold:
                confidence_levels['medium'] += 1
            else:
                confidence_levels['low'] += 1
        
        return {
            'task_distribution': task_counts,
            'step_distribution': step_counts,
            'confidence_distribution': confidence_levels,
            'total_records': len(self.sliding_window),
            'time_span_minutes': (
                (self.sliding_window[-1].timestamp - self.sliding_window[0].timestamp).total_seconds() / 60
                if len(self.sliding_window) > 1 else 0
            )
        }
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive state tracker summary with memory management.
        
        Returns:
            Summary information about state tracker
        """
        memory_stats = self.get_memory_stats()
        
        return {
            'has_current_state': self.current_state is not None,
            'history_size': len(self.state_history),
            'sliding_window_size': len(self.sliding_window),
            'high_confidence_threshold': self.high_confidence_threshold,
            'medium_confidence_threshold': self.medium_confidence_threshold,
            'current_state': self.get_current_state(),
            'metrics_summary': self.get_metrics_summary(),
            'memory_stats': {
                'total_records': memory_stats.total_records,
                'memory_usage_bytes': memory_stats.memory_usage_bytes,
                'memory_usage_mb': memory_stats.memory_usage_bytes / (1024 * 1024),
                'cleanup_count': memory_stats.cleanup_count,
                'max_size_reached': memory_stats.max_size_reached,
                'avg_record_size_bytes': memory_stats.avg_record_size,
                'memory_limit_mb': self.memory_limit_bytes / (1024 * 1024),
                'failure_count': self.failure_count
            }
        }
    
    def process_instant_query(self, query: str):
        """
        Process user query for instant response (< 20ms target).
        
        This implements the instant response loop:
        G: User query -> H: State Tracker direct response -> I: Return state info
        
        Args:
            query: User's natural language query
            
        Returns:
            QueryResult with formatted response
        """
        from .query_processor import QueryResult
        
        # Get current state (fast memory read)
        current_state = self.get_current_state()
        
        # Process query with query processor
        result = self.query_processor.process_query(query, current_state)
        
        logger.info(f"Instant query processed: '{query}' -> {result.query_type.value} in {result.processing_time_ms:.1f}ms")
        
        return result
    
    def get_query_capabilities(self) -> Dict[str, Any]:
        """Get information about query processing capabilities"""
        return {
            'supported_query_types': [qt.value for qt in self.query_processor.query_patterns.keys()],
            'example_queries': self.query_processor.get_supported_queries(),
            'response_time_target_ms': 20,
            'current_state_available': self.current_state is not None
        }

# Global state tracker instance
_state_tracker_instance: Optional[StateTracker] = None

def get_state_tracker() -> StateTracker:
    """Get or create global state tracker instance"""
    global _state_tracker_instance
    if _state_tracker_instance is None:
        _state_tracker_instance = StateTracker()
    return _state_tracker_instance