"""
Text Processing Utilities for State Tracker

This module provides utilities for cleaning and normalizing VLM text output
to handle various edge cases and ensure consistent processing.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VLMTextProcessor:
    """Utility class for processing VLM text output"""
    
    @staticmethod
    def is_valid_text(text: str) -> bool:
        """
        Check if text is valid for processing.
        
        Args:
            text: Input text to validate
            
        Returns:
            True if text is valid, False otherwise
        """
        if not text or not isinstance(text, str):
            return False
        
        # Check minimum length
        if len(text.strip()) < 3:
            return False
        
        # Check if text is mostly non-alphabetic (likely garbled)
        alpha_chars = sum(1 for c in text if c.isalpha())
        if alpha_chars / len(text) < 0.3:
            return False
        
        return True
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize VLM text.
        
        Args:
            text: Raw VLM text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove control characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s\.,!?;:()\-\'\"]+', '', cleaned)
        
        # Remove excessive punctuation
        cleaned = re.sub(r'[.]{3,}', '...', cleaned)
        cleaned = re.sub(r'[!]{2,}', '!', cleaned)
        cleaned = re.sub(r'[?]{2,}', '?', cleaned)
        
        return cleaned.strip()
    
    @staticmethod
    def extract_key_phrases(text: str) -> list:
        """
        Extract key phrases from VLM text for better matching.
        
        Args:
            text: Cleaned VLM text
            
        Returns:
            List of key phrases
        """
        if not text:
            return []
        
        # Simple keyword extraction
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        words = text.lower().split()
        key_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_words[:10]  # Return top 10 key words
    
    @staticmethod
    def detect_anomalies(text: str) -> list:
        """
        Detect potential anomalies in VLM text.
        
        Args:
            text: VLM text to analyze
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        if not text:
            anomalies.append("empty_text")
            return anomalies
        
        # Check for repeated characters
        if re.search(r'(.)\1{5,}', text):
            anomalies.append("repeated_characters")
        
        # Check for excessive special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            anomalies.append("excessive_special_chars")
        
        # Check for very short text
        if len(text.strip()) < 5:
            anomalies.append("too_short")
        
        # Check for very long text (might be concatenated responses)
        if len(text) > 1000:
            anomalies.append("too_long")
        
        return anomalies