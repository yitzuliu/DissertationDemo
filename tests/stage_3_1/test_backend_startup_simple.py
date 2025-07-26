#!/usr/bin/env python3
"""
Simplified Backend Service Startup Test

Used for quick verification of whether backend service can start normally
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

def test_backend_startup():
    """Test backend service startup"""
    print("🚀 Testing backend service startup...")
    
    # Set working directory
    project_root = Path(__file__).parent.parent.parent
    backend_dir = project_root / "src" / "backend"
    
    print(f"📁 Backend directory: {backend_dir}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if main.py exists
    main_py = backend_dir / "main.py"
    if not main_py.exists():
        print(f"❌ main.py doesn't exist: {main_py}")
        return False
    
    print(f"✅ Found main.py: {main_py}")
    
    # Try import test
    try:
        print("🔍 Testing Python import...")
        
        # Add paths
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(backend_dir))
        
        # Try import
        os.chdir(backend_dir)
        
        # Test basic import
        import main
        print("✅ Successfully imported main module")
        
        # Check app object
        if hasattr(main, 'app'):
            print("✅ Found FastAPI app object")
        else:
            print("❌ FastAPI app object not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_direct_uvicorn():
    """Test direct uvicorn startup"""
    print("\n🚀 Testing direct uvicorn startup...")
    
    try:
        # Switch to backend directory
        backend_dir = Path(__file__).parent.parent.parent / "src" / "backend"
        os.chdir(backend_dir)
        
        print(f"📁 Current directory: {os.getcwd()}")
        
        # Start uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000",
            "--log-level", "info"
        ]
        
        print(f"🔧 Executing command: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for startup
        print("⏳ Waiting for service to start...")
        time.sleep(10)
        
        # Check process status
        if process.poll() is None:
            print("✅ Service process is running")
            
            # Test connection
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Health check passed")
                    print(f"📄 Response: {response.json()}")
                    
                    # Terminate process
                    process.terminate()
                    process.wait()
                    return True
                else:
                    print(f"❌ Health check failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ Connection test failed: {e}")
        else:
            print("❌ Service process has exited")
            stdout, stderr = process.communicate()
            print(f"📄 stdout: {stdout}")
            print(f"📄 stderr: {stderr}")
        
        # Clean up process
        if process.poll() is None:
            process.terminate()
            process.wait()
        
        return False
        
    except Exception as e:
        print(f"❌ uvicorn startup test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Stage 3.1 - Backend Service Startup Diagnosis")
    print("=" * 50)
    
    # Test 1: Python import
    import_success = test_backend_startup()
    
    # Test 2: Direct uvicorn startup
    if import_success:
        uvicorn_success = test_direct_uvicorn()
        
        if uvicorn_success:
            print("\n✅ Backend service startup test successful")
            print("🎯 Can continue with complete Stage 3.1 tests")
            return True
        else:
            print("\n❌ uvicorn startup failed")
    else:
        print("\n❌ Python import failed")
    
    print("\n🔧 Suggestions:")
    print("1. Confirm all dependencies are installed")
    print("2. Check Python path configuration")
    print("3. Verify backend/utils modules")
    print("4. Check state_tracker module")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)