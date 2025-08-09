"""
Test Recent Observation Aware Fallback

This test suite validates the recent observation aware fallback functionality
that prevents stale template responses during scene transitions.
"""

import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path for imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from state_tracker.state_tracker import StateTracker, ConfidenceLevel, RecentObservationStatus
from state_tracker.query_processor import QueryProcessor, QueryType


class TestRecentObservationFallback(unittest.TestCase):
    """Test cases for recent observation aware fallback functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.state_tracker = StateTracker()
        self.query_processor = QueryProcessor()
        
        # Mock VLM fallback to avoid actual VLM calls during testing
        self.query_processor.enhanced_vlm_fallback = Mock()
        self.query_processor.vlm_fallback = Mock()
    
    def test_get_recent_observation_status_no_state(self):
        """Test status when no current state exists"""
        status = self.state_tracker.get_recent_observation_status()
        
        self.assertIsNone(status.seconds_since_last_update)
        self.assertEqual(status.last_observation_confidence_level, ConfidenceLevel.LOW)
        self.assertEqual(status.consecutive_low_count, 0)
        self.assertFalse(status.fallback_recommended)
    
    def test_get_recent_observation_status_fresh_state(self):
        """Test status with recent HIGH confidence update"""
        # Create a recent state with HIGH confidence
        from state_tracker.state_tracker import StateRecord
        recent_time = datetime.now() - timedelta(seconds=5)
        
        self.state_tracker.current_state = StateRecord(
            timestamp=recent_time,
            vlm_text="User is grinding coffee beans",
            matched_step={"title": "Grind coffee beans", "description": "Grind the coffee beans"},
            confidence=0.75,
            task_id="coffee_brewing",
            step_index=3
        )
        
        # Add a recent HIGH confidence observation
        from state_tracker.state_tracker import ProcessingMetrics, ActionType
        self.state_tracker.processing_metrics.append(ProcessingMetrics(
            timestamp=datetime.now() - timedelta(seconds=2),
            vlm_input="User is grinding coffee beans",
            confidence_score=0.75,
            processing_time_ms=150.0,
            confidence_level=ConfidenceLevel.HIGH,
            action_taken=ActionType.UPDATE,
            matched_task="coffee_brewing",
            matched_step=3,
            consecutive_low_count=0
        ))
        
        status = self.state_tracker.get_recent_observation_status()
        
        self.assertIsNotNone(status.seconds_since_last_update)
        self.assertLess(status.seconds_since_last_update, 10.0)  # Should be recent
        self.assertEqual(status.last_observation_confidence_level, ConfidenceLevel.HIGH)
        self.assertFalse(status.fallback_recommended)
    
    def test_get_recent_observation_status_stale_state(self):
        """Test status with old state and recent LOW observations"""
        # Create an old state
        from state_tracker.state_tracker import StateRecord
        old_time = datetime.now() - timedelta(seconds=30)
        
        self.state_tracker.current_state = StateRecord(
            timestamp=old_time,
            vlm_text="User is grinding coffee beans",
            matched_step={"title": "Grind coffee beans", "description": "Grind the coffee beans"},
            confidence=0.75,
            task_id="coffee_brewing",
            step_index=3
        )
        
        # Add a recent LOW confidence observation
        from state_tracker.state_tracker import ProcessingMetrics, ActionType
        self.state_tracker.processing_metrics.append(ProcessingMetrics(
            timestamp=datetime.now() - timedelta(seconds=5),
            vlm_input="I see something on the counter",
            confidence_score=0.25,
            processing_time_ms=150.0,
            confidence_level=ConfidenceLevel.LOW,
            action_taken=ActionType.OBSERVE,
            matched_task=None,
            matched_step=None,
            consecutive_low_count=2
        ))
        
        status = self.state_tracker.get_recent_observation_status()
        
        self.assertIsNotNone(status.seconds_since_last_update)
        self.assertGreater(status.seconds_since_last_update, 15.0)  # Should be old
        self.assertEqual(status.last_observation_confidence_level, ConfidenceLevel.LOW)
        self.assertTrue(status.fallback_recommended)
    
    def test_fallback_decision_with_recent_low_observations(self):
        """Test fallback when recent observations are LOW"""
        # Set up state tracker with recent LOW observations
        from state_tracker.state_tracker import StateRecord, ProcessingMetrics, ActionType
        
        self.state_tracker.current_state = StateRecord(
            timestamp=datetime.now() - timedelta(seconds=10),
            vlm_text="User is grinding coffee beans",
            matched_step={"title": "Grind coffee beans", "description": "Grind the coffee beans"},
            confidence=0.75,
            task_id="coffee_brewing",
            step_index=3
        )
        
        self.state_tracker.processing_metrics.append(ProcessingMetrics(
            timestamp=datetime.now() - timedelta(seconds=2),
            vlm_input="I see something on the counter",
            confidence_score=0.25,
            processing_time_ms=150.0,
            confidence_level=ConfidenceLevel.LOW,
            action_taken=ActionType.OBSERVE,
            matched_task=None,
            matched_step=None,
            consecutive_low_count=1
        ))
        
        # Test fallback decision
        should_fallback = self.query_processor._should_use_vlm_fallback(
            QueryType.CURRENT_STEP,
            self.state_tracker.get_current_state(),
            0.9,  # High confidence query
            self.state_tracker
        )
        
        self.assertTrue(should_fallback)
    
    def test_fallback_decision_with_fresh_high_confidence(self):
        """Test no fallback with recent HIGH confidence"""
        # Set up state tracker with recent HIGH observations
        from state_tracker.state_tracker import StateRecord, ProcessingMetrics, ActionType
        
        self.state_tracker.current_state = StateRecord(
            timestamp=datetime.now() - timedelta(seconds=5),
            vlm_text="User is grinding coffee beans",
            matched_step={"title": "Grind coffee beans", "description": "Grind the coffee beans"},
            confidence=0.75,
            task_id="coffee_brewing",
            step_index=3
        )
        
        self.state_tracker.processing_metrics.append(ProcessingMetrics(
            timestamp=datetime.now() - timedelta(seconds=2),
            vlm_input="User is grinding coffee beans",
            confidence_score=0.75,
            processing_time_ms=150.0,
            confidence_level=ConfidenceLevel.HIGH,
            action_taken=ActionType.UPDATE,
            matched_task="coffee_brewing",
            matched_step=3,
            consecutive_low_count=0
        ))
        
        # Test fallback decision
        should_fallback = self.query_processor._should_use_vlm_fallback(
            QueryType.CURRENT_STEP,
            self.state_tracker.get_current_state(),
            0.9,  # High confidence query
            self.state_tracker
        )
        
        self.assertFalse(should_fallback)
    
    def test_fallback_decision_error_handling(self):
        """Test graceful error handling in fallback decision"""
        # Test with None state tracker
        should_fallback = self.query_processor._should_use_vlm_fallback(
            QueryType.CURRENT_STEP,
            {"task_id": "test", "step_index": 1},
            0.9,
            None  # No state tracker
        )
        
        # Should not fallback when state tracker is None
        self.assertFalse(should_fallback)
    
    def test_consecutive_low_threshold(self):
        """Test fallback triggered by consecutive low observations"""
        # Set up state tracker with consecutive low observations
        from state_tracker.state_tracker import StateRecord, ProcessingMetrics, ActionType
        
        self.state_tracker.current_state = StateRecord(
            timestamp=datetime.now() - timedelta(seconds=5),
            vlm_text="User is grinding coffee beans",
            matched_step={"title": "Grind coffee beans", "description": "Grind the coffee beans"},
            confidence=0.75,
            task_id="coffee_brewing",
            step_index=3
        )
        
        # Set consecutive low count to trigger threshold
        self.state_tracker.consecutive_low_count = 3
        
        # Add a recent MEDIUM confidence observation
        self.state_tracker.processing_metrics.append(ProcessingMetrics(
            timestamp=datetime.now() - timedelta(seconds=2),
            vlm_input="I see some objects",
            confidence_score=0.5,
            processing_time_ms=150.0,
            confidence_level=ConfidenceLevel.MEDIUM,
            action_taken=ActionType.OBSERVE,
            matched_task=None,
            matched_step=None,
            consecutive_low_count=3
        ))
        
        status = self.state_tracker.get_recent_observation_status()
        self.assertTrue(status.fallback_recommended)


if __name__ == '__main__':
    unittest.main()
