"""
Decision Engine for VLM Fallback System

Determines when to use VLM fallback based on state tracker confidence
and other contextual factors.
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class DecisionContext:
    """Context information for fallback decision"""
    query: str
    state_data: Optional[Dict]
    confidence: float
    query_type: str
    has_current_step: bool
    decision_reason: str
    should_use_fallback: bool
    timestamp: datetime

class DecisionEngine:
    """
    Intelligent decision engine that determines when to use VLM fallback.
    
    Core Logic:
    1. No state data → Use VLM fallback
    2. Confidence < threshold → Use VLM fallback  
    3. Query type unknown → Use VLM fallback
    4. No current step → Use VLM fallback
    5. Otherwise → Use template response
    """
    
    def __init__(self, confidence_threshold: float = 0.40):
        """
        Initialize decision engine.
        
        Args:
            confidence_threshold: Minimum confidence to use template response
        """
        self.confidence_threshold = confidence_threshold
        self.decision_count = 0
        self.fallback_count = 0
        
        logger.info(f"DecisionEngine initialized with confidence threshold: {confidence_threshold}")
    
    def should_use_vlm_fallback(self, query: str, state_data: Optional[Dict]) -> bool:
        """
        Main decision method - determines if VLM fallback should be used.
        
        Args:
            query: User query string
            state_data: Current state tracker data
            
        Returns:
            bool: True if should use VLM fallback, False for template response
        """
        self.decision_count += 1
        
        # Create decision context
        context = self._create_decision_context(query, state_data)
        
        # Log decision for monitoring
        self._log_decision(context)
        
        if context.should_use_fallback:
            self.fallback_count += 1
            
        return context.should_use_fallback
    
    def _create_decision_context(self, query: str, state_data: Optional[Dict]) -> DecisionContext:
        """Create comprehensive decision context"""
        
        # Extract state information
        confidence = 0.0
        query_type = "UNKNOWN"
        has_current_step = False
        
        if state_data:
            confidence = state_data.get('confidence', 0.0)
            query_type = state_data.get('query_type', 'UNKNOWN')
            has_current_step = bool(state_data.get('current_step'))
        
        # Decision logic
        should_use_fallback, reason = self._make_decision(
            query, state_data, confidence, query_type, has_current_step
        )
        
        return DecisionContext(
            query=query,
            state_data=state_data,
            confidence=confidence,
            query_type=query_type,
            has_current_step=has_current_step,
            decision_reason=reason,
            should_use_fallback=should_use_fallback,
            timestamp=datetime.now()
        )
    
    def _make_decision(self, query: str, state_data: Optional[Dict], 
                      confidence: float, query_type: str, has_current_step: bool) -> tuple[bool, str]:
        """
        Core decision logic with detailed reasoning.
        
        Returns:
            tuple: (should_use_fallback, reason)
        """
        
        # Condition 1: No state data
        if not state_data:
            return True, "No state data available"
        
        # Condition 2: Confidence too low
        if confidence < self.confidence_threshold:
            return True, f"Confidence too low: {confidence:.3f} < {self.confidence_threshold}"
        
        # Condition 3: Query type unknown
        if query_type == 'UNKNOWN':
            return True, "Query type unknown"
        
        # Condition 4: No current step
        if not has_current_step:
            return True, "No current step available"
        
        # Default: Use template response
        return False, f"Template response: confidence={confidence:.3f}, type={query_type}"
    
    def _log_decision(self, context: DecisionContext):
        """Log decision for monitoring and debugging"""
        
        log_level = logging.INFO if context.should_use_fallback else logging.DEBUG
        
        logger.log(log_level, 
            f"Decision #{self.decision_count}: "
            f"{'VLM_FALLBACK' if context.should_use_fallback else 'TEMPLATE'} - "
            f"{context.decision_reason} "
            f"(query: '{context.query[:50]}{'...' if len(context.query) > 50 else ''}')"
        )
    
    def get_statistics(self) -> Dict:
        """Get decision engine statistics"""
        fallback_rate = (self.fallback_count / self.decision_count * 100) if self.decision_count > 0 else 0
        
        return {
            "total_decisions": self.decision_count,
            "fallback_decisions": self.fallback_count,
            "template_decisions": self.decision_count - self.fallback_count,
            "fallback_rate_percent": round(fallback_rate, 2),
            "confidence_threshold": self.confidence_threshold
        }
    
    def reset_statistics(self):
        """Reset decision statistics"""
        self.decision_count = 0
        self.fallback_count = 0
        logger.info("Decision engine statistics reset")
    
    def update_threshold(self, new_threshold: float):
        """Update confidence threshold"""
        old_threshold = self.confidence_threshold
        self.confidence_threshold = new_threshold
        logger.info(f"Confidence threshold updated: {old_threshold} → {new_threshold}")