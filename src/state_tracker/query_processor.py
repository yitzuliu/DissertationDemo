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
    from vlm_fallback.enhanced_fallback_processor import EnhancedVLMFallbackProcessor
    VLM_FALLBACK_AVAILABLE = True
    ENHANCED_FALLBACK_AVAILABLE = True
except ImportError:
    VLM_FALLBACK_AVAILABLE = False
    ENHANCED_FALLBACK_AVAILABLE = False

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
        # Initialize Enhanced VLM Fallback (with image support)
        self.enhanced_vlm_fallback = None
        self.vlm_fallback = None  # Initialize vlm_fallback attribute
        
        if ENHANCED_FALLBACK_AVAILABLE:
            try:
                # Load config and pass to EnhancedVLMFallbackProcessor
                from vlm_fallback.config import VLMFallbackConfig
                config = VLMFallbackConfig.from_file('src/config/vlm_fallback_config.json')
                self.enhanced_vlm_fallback = EnhancedVLMFallbackProcessor(config)
                print("Enhanced VLM Fallback initialized successfully with config")
            except Exception as e:
                print(f"Warning: Enhanced VLM Fallback initialization failed: {e}")
                # Fallback to default config if file loading fails
                try:
                    self.enhanced_vlm_fallback = EnhancedVLMFallbackProcessor()
                    print("Enhanced VLM Fallback initialized with default config")
                except Exception as e2:
                    print(f"Warning: Enhanced VLM Fallback initialization with default config also failed: {e2}")
        
        # Initialize Standard VLM Fallback (always try as backup)
        if VLM_FALLBACK_AVAILABLE:
            try:
                self.vlm_fallback = VLMFallbackProcessor()
                print("Standard VLM Fallback initialized successfully")
            except Exception as e:
                print(f"Warning: Standard VLM Fallback initialization failed: {e}")
        
        # Log final initialization status
        print(f"VLM Fallback Status: Enhanced={bool(self.enhanced_vlm_fallback)}, Standard={bool(self.vlm_fallback)}")
        
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
        
        # First check for clearly non-task-related queries
        non_task_indicators = [
            'meaning of life', 'joke', 'weather', 'tokyo', 'quantum physics',
            'perfect cup of coffee', 'programming', 'artificial intelligence',
            'philosophy', 'consciousness', 'news', 'current events'
        ]
        
        if any(indicator in query_lower for indicator in non_task_indicators):
            if query_id and log_manager:
                log_manager.log_query_classify_result(query_id, QueryType.UNKNOWN.value, 0.1)
            return QueryType.UNKNOWN
        
        # Check each query type in priority order
        for query_type in priority_order:
            patterns = self.query_patterns.get(query_type, [])
            for pattern in patterns:
                # 記錄模式檢查過程
                if query_id and log_manager:
                    log_manager.log_query_pattern_check(query_id, pattern, query_type.value)
                
                if re.search(pattern, query_lower):
                    # Additional validation for HELP classification
                    if query_type == QueryType.HELP:
                        # Don't classify general questions as HELP if they're not task-related
                        general_question_patterns = [
                            'what is', 'tell me about', 'explain', 'how do i make',
                            'what\'s the weather', 'meaning of'
                        ]
                        if any(gp in query_lower for gp in general_question_patterns):
                            continue  # Skip this match, continue checking
                    
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
                     query_id: str = None, log_manager = None, state_tracker = None) -> QueryResult:
        """
        Enhanced query processing with recent observation awareness.
        
        Args:
            query: User's natural language query
            current_state: Current state data from State Tracker
            query_id: Optional query ID for logging
            log_manager: Optional log manager for detailed logging
            state_tracker: Optional state tracker instance for recent observation check
            
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
            
            # Enhanced fallback decision with recent observation awareness
            should_use_fallback = self._should_use_vlm_fallback(query_type, current_state, confidence, state_tracker)
            
            # Debug logging
            print(f"DEBUG: Query='{query}', Type={query_type}, Confidence={confidence}, Should_fallback={should_use_fallback}, Enhanced_VLM_available={bool(self.enhanced_vlm_fallback)}, VLM_available={bool(self.vlm_fallback)}")
            
            # Priority: Use Enhanced VLM Fallback (with image support)
            if should_use_fallback and self.enhanced_vlm_fallback:
                try:
                    # Simplified VLM Fallback: Direct query to VLM
                    print(f"DEBUG: Using Enhanced VLM Fallback for query: '{query}' (Type: {query_type}, Confidence: {confidence})")
                    
                    # Get current image and send query directly to VLM
                    current_image = None
                    if state_tracker:
                        current_image = state_tracker.get_last_processed_image()
                    
                    # Direct VLM query - let VLM handle all analysis
                    # Use asyncio to run the async method
                    import asyncio
                    try:
                        # Try to get existing event loop
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is running, create a task
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(asyncio.run, self.simple_enhanced_vlm_fallback(query, current_image))
                                fallback_result = future.result(timeout=30)
                        else:
                            # If no loop is running, use asyncio.run
                            fallback_result = asyncio.run(self.simple_enhanced_vlm_fallback(query, current_image))
                    except RuntimeError:
                        # If there's no event loop, create one
                        fallback_result = asyncio.run(self.simple_enhanced_vlm_fallback(query, current_image))
                    
                    if fallback_result:
                        # Calculate processing time
                        processing_time = (time.time() - start_time) * 1000
                        
                        # Log processing completion
                        if query_id and log_manager:
                            log_manager.log_query_process_complete(query_id, processing_time)
                        
                        return QueryResult(
                            query_type=query_type,  # Use calculated query_type
                            response_text=fallback_result["response_text"],
                            processing_time_ms=processing_time,
                            confidence=fallback_result.get("confidence", confidence),  # Use VLM confidence or calculated confidence
                            raw_query=query
                        )
                except Exception as e:
                    # If Enhanced VLM fallback fails, continue with standard fallback
                    print(f"Enhanced VLM fallback failed: {e}")
            
            # Fallback to standard VLM Fallback (text-only)
            if should_use_fallback and self.vlm_fallback:
                try:
                    # Simplified VLM Fallback: Direct query to VLM
                    print(f"DEBUG: Using Standard VLM Fallback for query: '{query}' (Type: {query_type}, Confidence: {confidence})")
                    
                    # Direct VLM query - let VLM handle all analysis
                    # Use asyncio to run the async method
                    import asyncio
                    try:
                        # Try to get existing event loop
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is running, create a task
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(asyncio.run, self.simple_vlm_fallback(query))
                                fallback_result = future.result(timeout=30)
                        else:
                            # If no loop is running, use asyncio.run
                            fallback_result = asyncio.run(self.simple_vlm_fallback(query))
                    except RuntimeError:
                        # If there's no event loop, create one
                        fallback_result = asyncio.run(self.simple_vlm_fallback(query))
                    
                    if fallback_result:
                        # Calculate processing time
                        processing_time = (time.time() - start_time) * 1000
                        
                        return QueryResult(
                            query_type=query_type,  # Use calculated query_type
                            response_text=fallback_result["response_text"],
                            processing_time_ms=processing_time,
                            confidence=fallback_result.get("confidence", confidence),  # Use VLM confidence or calculated confidence
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
    
    def _should_use_vlm_fallback(self, query_type: QueryType, current_state: Optional[Dict[str, Any]], 
                                confidence: float, state_tracker=None) -> bool:
        """
        Enhanced fallback decision with recent observation awareness.
        
        Args:
            query_type: Classified query type
            current_state: Current state data
            confidence: Classification confidence
            state_tracker: Optional state tracker instance for recent observation check
            
        Returns:
            True if VLM fallback should be used
        """
        # Check if any VLM fallback system is available
        if not (self.enhanced_vlm_fallback or self.vlm_fallback):
            print(f"DEBUG: No VLM fallback available - enhanced: {bool(self.enhanced_vlm_fallback)}, standard: {bool(self.vlm_fallback)}")
            return False
        
        # Use VLM fallback if:
        # 1. No state data available
        if not current_state:
            print(f"DEBUG: Using VLM fallback - no state data")
            return True
        
        # 2. Low confidence in query classification
        if confidence < 0.40:
            print(f"DEBUG: Using VLM fallback - low confidence ({confidence} < 0.40)")
            return True
        
        # 3. Unknown query type
        if query_type == QueryType.UNKNOWN:
            print(f"DEBUG: Using VLM fallback - unknown query type")
            return True
        
        # 4. No current step information
        if not current_state.get('step_index') and not current_state.get('matched_step'):
            print(f"DEBUG: Using VLM fallback - no step information")
            return True
        
        # NEW: Recent observation aware fallback
        if state_tracker and self._should_fallback_due_to_recent_observations(state_tracker):
            print(f"DEBUG: Using VLM fallback - recent observations suggest fallback")
            return True
        
        print(f"DEBUG: Not using VLM fallback - confidence: {confidence}, type: {query_type}, state: {bool(current_state)}")
        return False

    def _should_fallback_due_to_recent_observations(self, state_tracker, 
                                                   fallback_ttl_seconds: float = 15.0) -> bool:
        """
        Check if fallback should be used based on recent observations.
        
        Args:
            state_tracker: State tracker instance
            fallback_ttl_seconds: TTL threshold for stale state detection
            
        Returns:
            True if recent observations suggest fallback is needed
        """
        try:
            status = state_tracker.get_recent_observation_status(fallback_ttl_seconds)
            return status.fallback_recommended
        except Exception as e:
            print(f"Warning: Error checking recent observation status: {e}")
            return False  # Default to existing behavior on error

    async def simple_enhanced_vlm_fallback(self, query: str, current_image: bytes = None):
        """
        Simplified Enhanced VLM Fallback - Direct query to VLM
        
        Args:
            query: User query
            current_image: Current image data (optional)
            
        Returns:
            VLM response or None if failed
        """
        try:
            # Direct query to Enhanced VLM Fallback
            if current_image:
                # Use image-based fallback
                result = await self.enhanced_vlm_fallback.process_query_with_image_fallback(
                    query, {"image": current_image}
                )
            else:
                # Use text-only fallback
                result = await self.enhanced_vlm_fallback.process_query_with_fallback(
                    query, {}
                )
            
            return result
        except Exception as e:
            print(f"Enhanced VLM Fallback error: {e}")
            return None

    async def simple_vlm_fallback(self, query: str):
        """
        Simplified Standard VLM Fallback - Direct query to VLM
        
        Args:
            query: User query
            
        Returns:
            VLM response or None if failed
        """
        try:
            # Direct query to Standard VLM Fallback
            result = await self.vlm_fallback.process_query_with_fallback(query, {})
            return result
        except Exception as e:
            print(f"Standard VLM Fallback error: {e}")
            return None
    
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
        
        # Reduce confidence if no state data - this is critical for fallback triggering
        if not current_state:
            # For task-related queries without state, confidence should be very low
            if query_type in [QueryType.CURRENT_STEP, QueryType.NEXT_STEP, 
                             QueryType.REQUIRED_TOOLS, QueryType.COMPLETION_STATUS, 
                             QueryType.PROGRESS_OVERVIEW]:
                base_confidence = 0.2  # Very low confidence for task queries without state
            else:
                base_confidence *= 0.3  # Significant reduction for other queries
        
        # Additional reduction for state-dependent queries even with state
        state_dependent_queries = ['what am i doing', 'where am i', 'current status', 'my status']
        if any(phrase in query.lower() for phrase in state_dependent_queries):
            if not current_state or not current_state.get('task_id'):
                base_confidence = 0.15  # Force low confidence for these queries without proper state
        
        # Reduce confidence for complex queries that might need VLM
        complex_keywords = [
            'meaning', 'explain', 'why', 'how does', 'what is', 'tell me about',
            'philosophy', 'consciousness', 'artificial intelligence', 'quantum',
            'weather', 'today', 'tomorrow', 'news', 'current events', 'joke',
            'perfect', 'tokyo', 'physics', 'life', 'programming'
        ]
        
        query_lower = query.lower()
        complex_matches = sum(1 for keyword in complex_keywords if keyword in query_lower)
        
        if complex_matches > 0:
            # More complex queries get lower confidence
            complexity_factor = max(0.15, 1.0 - (complex_matches * 0.4))
            base_confidence *= complexity_factor
        
        # Additional reduction for questions that don't match standard patterns
        question_indicators = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        has_question_word = any(word in query_lower for word in question_indicators)
        
        if has_question_word and query_type == QueryType.UNKNOWN:
            base_confidence *= 0.5  # Further reduce for unknown questions
        
        # Reduce confidence for queries about general topics (not task-specific)
        general_topics = ['coffee', 'weather', 'joke', 'meaning of life', 'quantum', 'tokyo']
        if any(topic in query_lower for topic in general_topics):
            base_confidence *= 0.3
        
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