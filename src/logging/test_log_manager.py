#!/usr/bin/env python3
"""
LogManager Test Script

Used to verify LogManager basic functionality
"""

import os
import sys
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from log_manager import LogManager, get_log_manager


def test_log_manager():
    """Test LogManager basic functionality"""
    print("Starting LogManager test...")
    
    # Initialize log manager
    log_manager = LogManager("test_logs")
    
    # Test unique ID generation
    print("\n1. Testing unique ID generation:")
    obs_id = log_manager.generate_observation_id()
    query_id = log_manager.generate_query_id()
    req_id = log_manager.generate_request_id()
    state_id = log_manager.generate_state_update_id()
    flow_id = log_manager.generate_flow_id()
    
    print(f"  observation_id: {obs_id}")
    print(f"  query_id: {query_id}")
    print(f"  request_id: {req_id}")
    print(f"  state_update_id: {state_id}")
    print(f"  flow_id: {flow_id}")
    
    # Test system logging
    print("\n2. Testing system log recording:")
    log_manager.log_system_start("sys_001", "localhost", 8000, "smolvlm")
    log_manager.log_memory_usage("sys_001", "22.1MB")
    log_manager.log_endpoint_call(req_id, "POST", "/v1/chat/completions", 200, 2.31)
    print("  System log recording completed")
    
    # Test visual logging
    print("\n3. Testing visual log recording:")
    log_manager.log_eyes_capture(obs_id, req_id, "MacBook FaceTime HD", 
                                "1920x1080", 0.9, "JPEG", "1.2MB")
    log_manager.log_eyes_prompt(obs_id, "Describe the steps for making coffee...", 48)
    log_manager.log_rag_matching(obs_id, "There are coffee filters and drip coffee maker on the table.", 
                               ["step1", "step2", "step3"], [0.82, 0.65, 0.12])
    log_manager.log_rag_result(obs_id, "step2", "Rinse the filter paper", 0.82)
    log_manager.log_state_tracker(obs_id, state_id, 0.82, "UPDATE", 
                                {"task": "brewing_coffee", "step": 2})
    print("  Visual log recording completed")
    
    # Test user query logging
    print("\n4. Testing user query logging:")
    log_manager.log_user_query(query_id, req_id, "What tools do I need?", "en", obs_id)
    log_manager.log_query_classify(query_id, "required_tools", 0.95)
    log_manager.log_query_process(query_id, {"task": "brewing_coffee", "step": 2})
    log_manager.log_query_response(query_id, "You need: filter paper, drip coffee maker, hot water, cup.", 1.2)
    print("  User query log recording completed")
    
    # Test flow tracking logging
    print("\n5. Testing flow tracking logging:")
    log_manager.log_flow_start(flow_id, "EYES_OBSERVATION")
    log_manager.log_flow_step(flow_id, "image_capture", observation_id=obs_id)
    log_manager.log_flow_step(flow_id, "backend_transfer", request_id=req_id)
    log_manager.log_flow_step(flow_id, "user_query", query_id=query_id)
    log_manager.log_flow_end(flow_id, "SUCCESS", 5.0)
    print("  Flow tracking log recording completed")
    
    # Check log files
    print("\n6. Checking generated log files:")
    today = datetime.now().strftime("%Y%m%d")
    log_files = [
        f"test_logs/system_{today}.log",
        f"test_logs/visual_{today}.log", 
        f"test_logs/user_{today}.log",
        f"test_logs/flow_tracking_{today}.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"  {log_file}: {len(lines)} lines")
        else:
            print(f"  {log_file}: File does not exist")
    
    # Cleanup
    log_manager.close_all_loggers()
    print("\nTest completed!")


if __name__ == "__main__":
    test_log_manager()