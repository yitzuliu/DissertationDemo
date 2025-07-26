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
        # Define keyword patterns for each query type
        self.query_patterns = {
            QueryType.CURRENT_STEP: [
                r'我在哪|現在哪|當前|where am i|current step|現在在|在哪個步驟',
                r'目前|現況|狀況|current|now'
            ],
            QueryType.NEXT_STEP: [
                r'下一步|接下來|然後|next step|next|what\'s next|下個步驟',
                r'接著|之後|後續|following'
            ],
            QueryType.REQUIRED_TOOLS: [
                r'需要什麼|工具|準備|tools|equipment|需要的|要用什麼',
                r'材料|用具|器具|需求'
            ],
            QueryType.COMPLETION_STATUS: [
                r'完成了嗎|進度|狀態|progress|status|done|finished|完成',
                r'做完了|結束了|好了嗎'
            ],
            QueryType.PROGRESS_OVERVIEW: [
                r'整體|全部|總共|overall|summary|概況|總進度',
                r'全體|整個流程|所有步驟'
            ],
            QueryType.HELP: [
                r'怎麼做|說明|幫助|help|how to|指導|教學',
                r'方法|步驟說明|詳細|instruction'
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
            return "目前沒有活動狀態。請先開始一個任務。"
        
        task_id = state_data.get('task_id', 'unknown')
        step_index = state_data.get('step_index', 0)
        confidence = state_data.get('confidence', 0.0)
        
        if query_type == QueryType.CURRENT_STEP:
            return f"您現在在「{task_id}」任務的第{step_index}步 (信心度: {confidence:.2f})"
        
        elif query_type == QueryType.NEXT_STEP:
            next_step = step_index + 1
            return f"下一步是第{next_step}步。建議先完成當前第{step_index}步。"
        
        elif query_type == QueryType.REQUIRED_TOOLS:
            return f"第{step_index}步可能需要相關工具。請參考任務說明獲取詳細工具清單。"
        
        elif query_type == QueryType.COMPLETION_STATUS:
            progress_percent = min(step_index * 10, 100)  # Simple progress estimation
            return f"當前進度：第{step_index}步 (約{progress_percent}%完成，信心度: {confidence:.2f})"
        
        elif query_type == QueryType.PROGRESS_OVERVIEW:
            return f"任務「{task_id}」進行中，目前在第{step_index}步，系統信心度{confidence:.2f}"
        
        elif query_type == QueryType.HELP:
            return f"您正在進行「{task_id}」的第{step_index}步。如需詳細說明，請查看任務指南。"
        
        else:  # UNKNOWN
            return f"抱歉，我不太理解您的問題。您目前在「{task_id}」的第{step_index}步。您可以問：我在哪？下一步？需要什麼工具？"
    
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
    
    def get_supported_queries(self) -> List[str]:
        """Get list of example supported queries"""
        return [
            "我在哪個步驟？",
            "下一步是什麼？",
            "需要什麼工具？",
            "完成了嗎？",
            "整體進度如何？",
            "怎麼做這個步驟？",
            "current step",
            "next step",
            "tools needed",
            "progress status"
        ]