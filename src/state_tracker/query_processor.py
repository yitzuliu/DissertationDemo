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

# Import VLM Fallback System
try:
    from vlm_fallback.fallback_processor import VLMFallbackProcessor
    VLM_FALLBACK_AVAILABLE = True
except ImportError:
    VLM_FALLBACK_AVAILABLE = False

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
        # Initialize VLM Fallback System
        self.vlm_fallback = None
        if VLM_FALLBACK_AVAILABLE:
            try:
                self.vlm_fallback = VLMFallbackProcessor()
            except Exception as e:
                print(f"Warning: VLM Fallback initialization failed: {e}")
        
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
                r'what.*required|what.*equipment|what.*materials'
            ],
            QueryType.COMPLETION_STATUS: [
                r'progress|status|done|finished|complete|percent|percentage',
                r'completed|finished|done|remaining|left|how.*much.*done'
            ],
            QueryType.PROGRESS_OVERVIEW: [
                r'overall|summary|overview|big.*picture|give.*overview|show.*progress',
                r'total.*progress|full.*overview|complete.*overview|entire.*progress'
            ],
            QueryType.HELP: [
                r'help|how.*to|how.*do|instruction|guide|what.*do.*this|how.*step',
                r'explain|describe|tell.*me.*about|show.*me.*how|assist|support'
            ]
        }
    
    def _classify_query(self, query: str, query_id: str = None, log_manager = None) -> QueryType:
        """Classify user query based on keyword patterns with improved accuracy"""
        query_lower = query.lower().strip()
        
        # 記錄分類開始
        if query_id and log_manager:
            log_manager.log_query_classify_start(query_id, query)
        
        # Define priority order for query types (more specific first)
        priority_order = [
            QueryType.CURRENT_STEP,
            QueryType.NEXT_STEP,
            QueryType.REQUIRED_TOOLS,
            QueryType.COMPLETION_STATUS,  # Move completion_status before help
            QueryType.PROGRESS_OVERVIEW,
            QueryType.HELP
        ]
        
        # Check each query type in priority order
        for query_type in priority_order:
            patterns = self.query_patterns.get(query_type, [])
            for pattern in patterns:
                # 記錄模式檢查過程
                if query_id and log_manager:
                    log_manager.log_query_pattern_check(query_id, pattern, query_type.value)
                
                if re.search(pattern, query_lower):
                    # 記錄模式匹配成功
                    if query_id and log_manager:
                        log_manager.log_query_pattern_match(query_id, query_type.value, pattern)
                        # 記錄分類最終結果
                        log_manager.log_query_classify_result(query_id, query_type.value, 0.9)
                    return query_type
        
        # 記錄分類結果（未找到匹配）
        if query_id and log_manager:
            log_manager.log_query_classify_result(query_id, QueryType.UNKNOWN.value, 0.3)
        
        return QueryType.UNKNOWN
    
    def _generate_response(self, query_type: QueryType, state_data: Optional[Dict[str, Any]]) -> str:
        """Generate formatted response based on query type and current state"""
        
        try:
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
                    tools = step_details['tools']
                    if isinstance(tools, list) and tools:
                        tools_list = ", ".join(tools)
                        return f"Step {step_index} requires the following tools:\n{tools_list}\n\nStep: {step_details['title']}\nDescription: {step_details['description']}"
                    else:
                        return f"Step {step_index} may require specific tools. Please refer to the task description for detailed tool requirements."
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
                    # Handle tools list safely
                    tools = step_details.get('tools', [])
                    if isinstance(tools, list) and tools:
                        tools_list = ", ".join(tools)
                    else:
                        tools_list = "No specific tools listed"
                    
                    # Handle safety notes safely
                    safety_notes = step_details.get('safety_notes', [])
                    if isinstance(safety_notes, list) and safety_notes:
                        safety_notes_text = "\n".join([f"- {note}" for note in safety_notes])
                    else:
                        safety_notes_text = "No specific safety notes"
                    
                    return f"You are currently on step {step_index} of task '{task_id}'.\n\nStep: {step_details['title']}\nDescription: {step_details['description']}\nRequired tools: {tools_list}\nEstimated duration: {step_details['estimated_duration']}\nSafety notes:\n{safety_notes_text}"
                else:
                    return f"You are currently on step {step_index} of task '{task_id}'. For detailed instructions, please refer to the task guide."
            
            else:  # UNKNOWN
                return f"Sorry, I don't understand your question. You are currently on step {step_index} of task '{task_id}'. You can ask: Where am I? What's next? What tools do I need?"
        
        except Exception as e:
            # Fallback response in case of any error
            return f"Sorry, I encountered an error while processing your query. You are currently on step {step_index} of task '{task_id}'."
    
    def _get_response_type(self, query_type: QueryType, state_data: Optional[Dict[str, Any]]) -> str:
        """Determine response type for logging"""
        if not state_data:
            return "no_state_message"
        
        if query_type == QueryType.CURRENT_STEP:
            return "current_step_info"
        elif query_type == QueryType.NEXT_STEP:
            return "next_step_info"
        elif query_type == QueryType.REQUIRED_TOOLS:
            return "tools_info"
        elif query_type == QueryType.COMPLETION_STATUS:
            return "completion_info"
        elif query_type == QueryType.PROGRESS_OVERVIEW:
            return "progress_overview"
        elif query_type == QueryType.HELP:
            return "help_info"
        else:
            return "unknown_response"
    
    def process_query(self, query: str, current_state: Optional[Dict[str, Any]], 
                     query_id: str = None, log_manager = None) -> QueryResult:
        """
        Process user query and generate instant response.
        
        Args:
            query: User's natural language query
            current_state: Current state data from State Tracker
            query_id: Optional query ID for logging
            log_manager: Optional log manager for detailed logging
            
        Returns:
            QueryResult with response and metadata
        """
        try:
            start_time = time.time()
            
            # 記錄處理開始
            if query_id and log_manager:
                state_keys = list(current_state.keys()) if current_state else []
                log_manager.log_query_process_start(query_id, query, state_keys)
            
            # Classify query with detailed logging
            query_type = self._classify_query(query, query_id, log_manager)
            
            # 記錄狀態查找
            if query_id and log_manager:
                state_found = bool(current_state)
                state_info = {
                    'has_task_id': 'task_id' in (current_state or {}),
                    'has_step_index': 'step_index' in (current_state or {}),
                    'state_keys': list((current_state or {}).keys())
                }
                log_manager.log_query_state_lookup(query_id, state_found, state_info)
            
            # Calculate confidence based on query complexity and state availability
            confidence = self._calculate_confidence(query_type, current_state, query)
            
            # Check if VLM fallback should be used
            should_use_fallback = self._should_use_vlm_fallback(query_type, current_state, confidence)
            
            # Debug logging
            print(f"DEBUG: Query='{query}', Type={query_type}, Confidence={confidence}, Should_fallback={should_use_fallback}, VLM_available={bool(self.vlm_fallback)}")
            
            if should_use_fallback and self.vlm_fallback:
                try:
                    # Use VLM fallback system - create a simple synchronous wrapper
                    import asyncio
                    import threading
                    
                    def run_fallback_sync():
                        """Run VLM fallback in a separate thread with its own event loop"""
                        try:
                            # Create new event loop for this thread
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            # Run the async function
                            if asyncio.iscoroutinefunction(self.vlm_fallback.process_query_with_fallback):
                                result = loop.run_until_complete(self.vlm_fallback.process_query_with_fallback(query, current_state))
                            else:
                                result = self.vlm_fallback.process_query_with_fallback(query, current_state)
                            
                            return result
                        except Exception as e:
                            print(f"VLM fallback thread error: {e}")
                            return None
                        finally:
                            loop.close()
                    
                    # Run in separate thread to avoid event loop conflicts
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_fallback_sync)
                        try:
                            fallback_result = future.result(timeout=30)  # 30 second timeout
                        except concurrent.futures.TimeoutError:
                            print("VLM fallback timeout")
                            fallback_result = None
                    
                    if fallback_result:
                        # Calculate processing time
                        processing_time = (time.time() - start_time) * 1000
                        
                        # 記錄處理完成
                        if query_id and log_manager:
                            log_manager.log_query_process_complete(query_id, processing_time)
                        
                        return QueryResult(
                            query_type=query_type,
                            response_text=fallback_result["response_text"],
                            processing_time_ms=processing_time,
                            confidence=fallback_result["confidence"],
                            raw_query=query
                        )
                except Exception as e:
                    # If VLM fallback fails, continue with template response
                    print(f"VLM fallback failed: {e}")
            
            # Generate template response
            response_text = self._generate_response(query_type, current_state)
            
            # 記錄回應生成
            if query_id and log_manager:
                response_type = self._get_response_type(query_type, current_state)
                log_manager.log_query_response_generate(query_id, response_type, len(response_text))
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # 記錄處理完成
            if query_id and log_manager:
                log_manager.log_query_process_complete(query_id, processing_time)
            
            return QueryResult(
                query_type=query_type,
                response_text=response_text,
                processing_time_ms=processing_time,
                confidence=confidence,
                raw_query=query
            )
        except Exception as e:
            # Return a fallback response in case of any error
            return QueryResult(
                query_type=QueryType.UNKNOWN,
                response_text=f"Sorry, I encountered an error processing your query: {str(e)}",
                processing_time_ms=0.0,
                confidence=0.0,
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
        try:
            if not state_data or not state_data.get('matched_step'):
                return None
            
            matched_step = state_data['matched_step']
            
            # Extract information from MatchResult structure with safe defaults
            step_details = {
                'title': matched_step.get('step_title', ''),
                'description': matched_step.get('step_description', ''),
                'tools': matched_step.get('tools_needed', []),
                'completion_indicators': matched_step.get('completion_indicators', []),
                'visual_cues': matched_step.get('visual_cues', []),
                'estimated_duration': matched_step.get('estimated_duration', ''),
                'safety_notes': matched_step.get('safety_notes', [])
            }
            
            # Ensure lists are actually lists
            for key in ['tools', 'completion_indicators', 'visual_cues', 'safety_notes']:
                if not isinstance(step_details[key], list):
                    step_details[key] = []
            
            # Ensure strings are actually strings
            for key in ['title', 'description', 'estimated_duration']:
                if not isinstance(step_details[key], str):
                    step_details[key] = str(step_details[key]) if step_details[key] is not None else ''
            
            return step_details
        except Exception as e:
            # Return None if any error occurs
            return None
    
    def _should_use_vlm_fallback(self, query_type: QueryType, current_state: Optional[Dict[str, Any]], confidence: float) -> bool:
        """
        Determine if VLM fallback should be used based on decision criteria
        
        Args:
            query_type: Classified query type
            current_state: Current state data
            confidence: Confidence score from classification
            
        Returns:
            True if VLM fallback should be used
        """
        if not self.vlm_fallback:
            return False
        
        # Use VLM fallback if:
        # 1. No state data available
        if not current_state:
            return True
        
        # 2. Low confidence in query classification
        if confidence < 0.40:
            return True
        
        # 3. Unknown query type
        if query_type == QueryType.UNKNOWN:
            return True
        
        # 4. No current step information
        if not current_state.get('step_index') and not current_state.get('matched_step'):
            return True
        
        return False
    
    def _calculate_confidence(self, query_type: QueryType, current_state: Optional[Dict[str, Any]], query: str) -> float:
        """
        Calculate confidence score based on multiple factors
        
        Args:
            query_type: Classified query type
            current_state: Current state data
            query: Original query text
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = 0.9 if query_type != QueryType.UNKNOWN else 0.1
        
        # Reduce confidence if no state data
        if not current_state:
            base_confidence *= 0.3  # Significant reduction
        
        # Reduce confidence for complex queries that might need VLM
        complex_keywords = [
            'meaning', 'explain', 'why', 'how does', 'what is', 'tell me about',
            'philosophy', 'consciousness', 'artificial intelligence', 'quantum',
            'weather', 'today', 'tomorrow', 'news', 'current events'
        ]
        
        query_lower = query.lower()
        complex_matches = sum(1 for keyword in complex_keywords if keyword in query_lower)
        
        if complex_matches > 0:
            # More complex queries get lower confidence
            complexity_factor = max(0.2, 1.0 - (complex_matches * 0.3))
            base_confidence *= complexity_factor
        
        # Ensure confidence is within bounds
        return max(0.1, min(0.9, base_confidence))
    
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