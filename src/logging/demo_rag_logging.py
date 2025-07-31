#!/usr/bin/env python3
"""
RAG Logging Demo

Demonstrates complete logging functionality for RAG matching process.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from log_manager import get_log_manager
from memory.rag.knowledge_base import RAGKnowledgeBase
from state_tracker.state_tracker import get_state_tracker


async def demonstrate_rag_logging():
    """Demonstrate RAG logging functionality"""
    print("=== RAG Logging Demo ===\n")
    
    # Get log manager
    log_manager = get_log_manager()
    
    # Generate observation ID
    observation_id = log_manager.generate_observation_id()
    print(f"Generated observation ID: {observation_id}")
    
    # Initialize RAG knowledge base
    print("\n1. Initializing RAG knowledge base...")
    rag_kb = RAGKnowledgeBase()
    try:
        rag_kb.initialize(precompute_embeddings=False)
        print("✓ RAG knowledge base initialization successful")
    except Exception as e:
        print(f"⚠ RAG knowledge base initialization failed: {e}")
        return
    
    # Test different VLM observations
    test_observations = [
        "I can see a red power button on the coffee machine",
        "The user is pouring coffee beans into the grinder",
        "Water in the kettle is heating up, thermometer shows 85 degrees",
        "Coffee is dripping into the cup, color is very dark",
        "The user is cleaning the coffee machine filter"
    ]
    
    print(f"\n2. Testing {len(test_observations)} VLM observations...")
    
    for i, observation in enumerate(test_observations, 1):
        print(f"\n--- Test {i}: {observation} ---")
        
        # Generate new observation ID for each test
        obs_id = log_manager.generate_observation_id()
        
        # Test RAG knowledge base directly
        print("Testing RAG knowledge base matching directly...")
        match_result = rag_kb.find_matching_step(
            observation=observation,
            observation_id=obs_id
        )
        
        if match_result and match_result.similarity > 0:
            print(f"✓ Match result: {match_result.task_name}:step_{match_result.step_id}")
            print(f"  Similarity: {match_result.similarity:.3f}")
            print(f"  Confidence: {match_result.confidence_level}")
            print(f"  Step description: {match_result.task_description[:100]}...")
        else:
            print("⚠ No match result found")
        
        # Test through state tracker
        print("Testing through state tracker...")
        state_tracker = get_state_tracker()
        
        try:
            state_updated = await state_tracker.process_vlm_response(
                vlm_text=observation,
                observation_id=obs_id
            )
            print(f"✓ State tracker processing completed, state updated: {state_updated}")
        except Exception as e:
            print(f"⚠ State tracker processing failed: {e}")
    
    print(f"\n3. Checking log files...")
    
    # Check log files
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"Found {len(log_files)} log files:")
        
        for log_file in log_files:
            print(f"  - {log_file.name}")
            
            # Check for RAG-related entries
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                rag_matching_count = content.count("RAG_MATCHING")
                rag_result_count = content.count("RAG_RESULT")
                
                if rag_matching_count > 0 or rag_result_count > 0:
                    print(f"    RAG_MATCHING: {rag_matching_count} entries")
                    print(f"    RAG_RESULT: {rag_result_count} entries")
                    
                    # Show recent RAG entries
                    lines = content.split('\n')
                    rag_lines = [line for line in lines if 'RAG_' in line]
                    
                    if rag_lines:
                        print("    Recent RAG log entries:")
                        for line in rag_lines[-3:]:  # Show last 3 entries
                            print(f"      {line}")
                            
            except Exception as e:
                print(f"    Failed to read log file: {e}")
    else:
        print("Log directory not found")
    
    print(f"\n=== RAG Logging Demo Completed ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_rag_logging())