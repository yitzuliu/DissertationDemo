"""
Query Processor for Instant Response System

This module handles intelligent parsing and routing of user queries
for the instant response whiteboard mechanism.
"""

import re
import time
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

class QueryType(Enum):
    """Types of user queries"""
    CURRENT_STEP = "current_step"
    NEXT_STEP = "next_step"
    REQUIRED_TOOLS = "required_tools"
    COMPLETION_STATUS = "completion_status"
    PROGRESS_OVERVIEW = "progress_overview"
    HELP = "help"
    UNKNOWN = "unknown"

@dataclass
class QueryResult:
    """Result of query processing"""
    query_type: QueryType
    response_text: str
    processing_time_ms: float
    confidence: float
    raw_query: str

class QueryProcessor:
    """
    Intelligent query processor for instant response system.
    
    Provides fast, template-based responses to user queries about current state.
    """
    
    def __init__(self):
        """Initialize query processor with keyword patterns"""
        # Define keyword patterns for each query type (English only)
        self.query_patterns = {
            QueryType.CURRENT_STEP: [
                r'where am i|current step|what step|which step|my step|current.*step',
                r'current|now|present|location|position'
            ],
            QueryType.NEXT_STEP: [
                r'next step|what.*next|following|after.*this|then.*what|next.*step',
                r'next|following|subsequent|after|then'
            ],
            QueryType.REQUIRED_TOOLS: [
                r'tools?|equipment|what.*tools|what.*need|what.*do.*step|tools.*needed|required.*tools',
                r'what.*should.*do|how.*do.*this|what.*required|what.*equipment|what.*materials'
            ],
            QueryType.COMPLETION_STATUS: [
                r'progress|status|done|finished|complete|how.*much|percent|percentage',
                r'completed|finished|done|over|remaining|left'
            ],
            QueryType.PROGRESS_OVERVIEW: [
                r'overall|summary|overview|progress.*overview|status.*overview|big.*picture',
                r'give.*overview|show.*progress|current.*status|what.*progress|total.*progress'
            ],
            QueryType.HELP: [
                r'help|how.*to|how.*do|instruction|guide|what.*do.*this|how.*step',
                r'explain|describe|tell.*me.*about|show.*me.*how|assist|support'
            ]
        }
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify user query based on keyword patterns"""
        query_lower = query.lower().strip()
        
        # Check each query type
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return query_type
        
        return QueryType.UNKNOWN
    
    def _generate_response(self, query_type: QueryType, state_data: Optional[Dict[str, Any]]) -> str:
        """Generate formatted response based on query type and current state"""
        
        if not state_data:
            return "No active state. Please start a task first."
        
        task_id = state_data.get('task_id', 'unknown')
        step_index = state_data.get('step_index', 0)
        confidence = state_data.get('confidence', 0.0)
        
        if query_type == QueryType.CURRENT_STEP:
            # Get detailed step information from matched_step
            step_details = self._get_step_details(state_data)
            if step_details:
                return f"You are currently on step {step_index} of task '{task_id}' (confidence: {confidence:.2f})\n\nStep: {step_details['title']}\nDescription: {step_details['description']}"
            else:
                return f"You are currently on step {step_index} of task '{task_id}' (confidence: {confidence:.2f})"
        
        elif query_type == QueryType.NEXT_STEP:
            next_step = step_index + 1
            return f"Next step is step {next_step}. Please complete the current step {step_index} first."
        
        elif query_type == QueryType.REQUIRED_TOOLS:
            # Get detailed tool information from matched_step
            step_details = self._get_step_details(state_data)
            if step_details and step_details.get('tools'):
                tools_list = ", ".join(step_details['tools'])
                return f"Step {step_index} requires the following tools:\n{tools_list}\n\nStep: {step_details['title']}\nDescription: {step_details['description']}"
            else:
                return f"Step {step_index} may require specific tools. Please refer to the task description for detailed tool requirements."
        
        elif query_type == QueryType.COMPLETION_STATUS:
            progress_percent = min(step_index * 10, 100)  # Simple progress estimation
            step_details = self._get_step_details(state_data)
            if step_details:
                return f"Current progress: Step {step_index} (approximately {progress_percent}% complete, confidence: {confidence:.2f})\n\nStep: {step_details['title']}\nEstimated duration: {step_details['estimated_duration']}"
            else:
                return f"Current progress: Step {step_index} (approximately {progress_percent}% complete, confidence: {confidence:.2f})"
        
        elif query_type == QueryType.PROGRESS_OVERVIEW:
            step_details = self._get_step_details(state_data)
            if step_details:
                return f"Task '{task_id}' in progress, currently on step {step_index}, system confidence {confidence:.2f}\n\nCurrent step: {step_details['title']}\nDescription: {step_details['description']}"
            else:
                return f"Task '{task_id}' in progress, currently on step {step_index}, system confidence {confidence:.2f}"
        
        elif query_type == QueryType.HELP:
            step_details = self._get_step_details(state_data)
            if step_details:
                tools_list = ", ".join(step_details['tools']) if step_details['tools'] else "No specific tools listed"
                safety_notes = "\n".join([f"- {note}" for note in step_details['safety_notes']]) if step_details['safety_notes'] else "No specific safety notes"
                
                return f"You are currently on step {step_index} of task '{task_id}'.\n\nStep: {step_details['title']}\nDescription: {step_details['description']}\nRequired tools: {tools_list}\nEstimated duration: {step_details['estimated_duration']}\nSafety notes:\n{safety_notes}"
            else:
                return f"You are currently on step {step_index} of task '{task_id}'. For detailed instructions, please refer to the task guide."
        
        else:  # UNKNOWN
            return f"Sorry, I don't understand your question. You are currently on step {step_index} of task '{task_id}'. You can ask: Where am I? What's next? What tools do I need?"
    
    def process_query(self, query: str, current_state: Optional[Dict[str, Any]]) -> QueryResult:
        """
        Process user query and generate instant response.
        
        Args:
            query: User's natural language query
            current_state: Current state data from State Tracker
            
        Returns:
            QueryResult with response and metadata
        """
        start_time = time.time()
        
        # Classify query
        query_type = self._classify_query(query)
        
        # Generate response
        response_text = self._generate_response(query_type, current_state)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Simple confidence based on pattern matching
        confidence = 0.9 if query_type != QueryType.UNKNOWN else 0.3
        
        return QueryResult(
            query_type=query_type,
            response_text=response_text,
            processing_time_ms=processing_time,
            confidence=confidence,
            raw_query=query
        )
    
    def _get_step_details(self, state_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract detailed step information from state data
        
        Args:
            state_data: Current state data from State Tracker
            
        Returns:
            Dictionary with step details or None if not available
        """
        if not state_data or not state_data.get('matched_step'):
            return None
        
        matched_step = state_data['matched_step']
        
        # Extract information from MatchResult structure
        step_details = {
            'title': matched_step.get('step_title', ''),
            'description': matched_step.get('step_description', ''),
            'tools': matched_step.get('tools_needed', []),
            'completion_indicators': matched_step.get('completion_indicators', []),
            'visual_cues': matched_step.get('visual_cues', []),
            'estimated_duration': matched_step.get('estimated_duration', ''),
            'safety_notes': matched_step.get('safety_notes', [])
        }
        
        return step_details
    
    def get_supported_queries(self) -> List[str]:
        """Get list of example supported queries (English only)"""
        return [
            "Where am I?",
            "What is the current step?", 
            "What's next?",
            "What tools do I need?",
            "What should I do in this step?",
            "How do I do this step?",
            "What's my progress?",
            "Give me an overview",
            "Help me with this step",
            "What's the status?",
            "How much is done?",
            "What equipment is required?"
        ]