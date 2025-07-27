#!/usr/bin/env python3
"""
Enhanced Logging Test
Test the enhanced logging functionality for VLM responses, RAG matching, and State Tracker
"""

import requests
import time
import json
import sys
from pathlib import Path

def test_enhanced_logging():
    """Test enhanced logging functionality"""
    print("🧪 Testing Enhanced Logging Functionality")
    print("=" * 50)
    
    # Test data - simulate VLM responses for different steps
    test_cases = [
        {
            "name": "Step 1 - Coffee Preparation",
            "text": "I can see coffee beans being prepared. The user is measuring coffee beans and getting ready to grind them. This appears to be the first step of coffee making.",
            "expected_task": "coffee_making",
            "expected_step": 1
        },
        {
            "name": "Step 2 - Coffee Brewing", 
            "text": "The coffee is now brewing. I can see hot water being poured over the coffee grounds. The coffee maker is actively brewing the coffee.",
            "expected_task": "coffee_making",
            "expected_step": 2
        },
        {
            "name": "Step 3 - Coffee Completion",
            "text": "The coffee brewing is complete. I can see a finished cup of coffee. The coffee making process appears to be finished.",
            "expected_task": "coffee_making", 
            "expected_step": 3
        }
    ]
    
    backend_url = "http://localhost:8000"
    
    # Check if backend is running
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not responding")
            return False
        print("✅ Backend is running")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔄 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Send test VLM response to State Tracker
            response = requests.post(
                f"{backend_url}/api/v1/state/process",
                json={"text": test_case["text"]},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API Response: {result}")
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        # Wait between tests
        time.sleep(2)
    
    print(f"\n📋 Test completed. Check logs for detailed information:")
    print(f"   Log file: logs/app_{time.strftime('%Y%m%d')}.log")
    
    return True

if __name__ == "__main__":
    test_enhanced_logging() 