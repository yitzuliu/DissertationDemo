#!/usr/bin/env python3
"""
Stage 3.1 Quick Verification Test

Quick verification of basic service communication functionality
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path

def test_backend_basic():
    """Basic backend service test"""
    print("🚀 Stage 3.1 Quick Verification Test")
    print("=" * 50)
    
    # 1. Test backend service startup
    print("📋 1. Testing backend service startup...")
    
    backend_dir = Path(__file__).parent.parent.parent / "src" / "backend"
    
    try:
        # Start backend service
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ Waiting for service to start...")
        time.sleep(8)
        
        if process.poll() is None:
            print("✅ Backend service started successfully")
            
            # 2. Test health check
            print("\n📋 2. Testing health check endpoint...")
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Health check passed")
                    print(f"   Response: {response.json()}")
                else:
                    print(f"❌ Health check failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ Health check connection failed: {e}")
            
            # 3. Test status endpoint
            print("\n📋 3. Testing status endpoint...")
            try:
                response = requests.get("http://127.0.0.1:8000/status", timeout=5)
                if response.status_code == 200:
                    print("✅ Status endpoint normal")
                    data = response.json()
                    print(f"   Status: {data.get('status', 'Unknown')}")
                else:
                    print(f"❌ Status endpoint failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ Status endpoint connection failed: {e}")
            
            # 4. Test State Tracker endpoint
            print("\n📋 4. Testing State Tracker endpoint...")
            try:
                response = requests.get("http://127.0.0.1:8000/api/v1/state", timeout=5)
                if response.status_code == 200:
                    print("✅ State Tracker endpoint normal")
                    data = response.json()
                    print(f"   Current step: {data.get('current_step', 'None')}")
                else:
                    print(f"❌ State Tracker endpoint failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ State Tracker endpoint connection failed: {e}")
            
            # 5. Test VLM text processing
            print("\n📋 5. Testing VLM text processing...")
            try:
                test_data = {"vlm_text": "User is preparing coffee equipment, coffee beans and grinder on table"}
                response = requests.post("http://127.0.0.1:8000/api/v1/state/process", 
                                       json=test_data, timeout=10)
                if response.status_code == 200:
                    print("✅ VLM text processing successful")
                    data = response.json()
                    print(f"   Processing result: Step {data.get('current_step', 'Unknown')}")
                else:
                    print(f"❌ VLM text processing failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ VLM text processing connection failed: {e}")
            
            # 6. Test user query
            print("\n📋 6. Testing user query...")
            try:
                query_data = {"query": "What step am I on now?"}
                response = requests.post("http://127.0.0.1:8000/api/v1/state/query", 
                                       json=query_data, timeout=10)
                if response.status_code == 200:
                    print("✅ User query processing successful")
                    data = response.json()
                    print(f"   Query response: {data.get('response', 'No response')[:100]}...")
                else:
                    print(f"❌ User query processing failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ User query processing connection failed: {e}")
            
        else:
            print("❌ Backend service startup failed")
            stdout, stderr = process.communicate()
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
        
        # Clean up process
        if process.poll() is None:
            process.terminate()
            process.wait()
        
        print("\n" + "=" * 50)
        print("🎯 Stage 3.1 quick verification completed")
        print("If most of the above tests pass, service communication is basically normal")
        print("Can proceed with complete Stage 3.1 testing")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    test_backend_basic()