"""
AI Manual Assistant Memory System

A dual-loop memory architecture for intelligent task progress tracking:
1. Unconscious Loop: VLM observation → State Tracker → RAG matching → State update
2. Instant Response Loop: User query → State reading → Direct response

This system implements Dialogue State Tracking (DST) framework with VLM fault tolerance.
"""

__version__ = "1.0.0"
__author__ = "AI Manual Assistant Team"