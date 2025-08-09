#!/usr/bin/env python3
"""
System Startup Script

This script helps you start all the necessary components for testing:
1. Backend server (src/backend/main.py)
2. VLM server (src/models/smolvlm/run_smolvlm.py)
3. Run tests
4. Open frontend

Usage:
    python start_system.py --all          # Start everything
    python start_system.py --backend      # Start only backend
    python start_system.py --vlm          # Start only VLM
    python start_system.py --test         # Run tests only
"""

import subprocess
import sys
import os
import time
import signal
import webbrowser
from pathlib import Path
import argparse
import threading
import requests

class SystemManager:
    """Manage system components"""
    
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        self.backend_url = "http://localhost:8000"
        self.vlm_url = "http://localhost:8080"
    
    def start_backend(self):
        """Start backend server"""
        print("🚀 Starting Backend Server...")
        
        backend_dir = self.base_dir / "src" / "backend"
        if not backend_dir.exists():
            print("❌ Backend directory not found!")
            return None
        
        try:
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_dir,
                env={**os.environ, "PYTHONPATH": str(self.base_dir / "src")}
            )
            
            self.processes.append(("Backend", process))
            print(f"✅ Backend server started (PID: {process.pid})")
            return process
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return None
    
    def start_vlm(self):
        """Start VLM server"""
        print("🤖 Starting VLM Server...")
        
        vlm_dir = self.base_dir / "src" / "models" / "smolvlm"
        if not vlm_dir.exists():
            print("❌ VLM directory not found!")
            return None
        
        try:
            process = subprocess.Popen(
                [sys.executable, "run_smolvlm.py"],
                cwd=vlm_dir
            )
            
            self.processes.append(("VLM", process))
            print(f"✅ VLM server started (PID: {process.pid})")
            return process
            
        except Exception as e:
            print(f"❌ Failed to start VLM: {e}")
            return None
    
    def wait_for_service(self, url, name, timeout=30):
        """Wait for service to be ready"""
        print(f"⏳ Waiting for {name} at {url}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name} is ready!")
                    return True
            except:
                pass
            time.sleep(1)
        
        print(f"❌ {name} not ready after {timeout}s")
        return False
    
    def run_tests(self):
        """Run core component tests"""
        print("🧪 Running Core Component Tests...")
        
        test_script = self.base_dir / "archive" / "tests" / "experimental" / "test_core_components.py"
        if not test_script.exists():
            print("❌ Test script not found!")
            return False
        
        try:
            # Set environment
            env = {**os.environ, "PYTHONPATH": str(self.base_dir / "src")}
            
            # Run tests
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=self.base_dir,
                env=env,
                input="\\n",  # Auto-press Enter
                text=True,
                capture_output=False
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Failed to run tests: {e}")
            return False
    
    def open_frontend(self):
        """Open frontend in browser"""
        frontend_file = self.base_dir / "src" / "frontend" / "index.html"
        
        if frontend_file.exists():
            print("🌐 Opening frontend in browser...")
            try:
                webbrowser.open(f"file://{frontend_file.absolute()}")
                print("✅ Frontend opened!")
            except Exception as e:
                print(f"❌ Failed to open frontend: {e}")
                print(f"📁 Please manually open: {frontend_file}")
        else:
            print("❌ Frontend file not found!")
    
    def stop_all(self):
        """Stop all processes"""
        print("🛑 Stopping all services...")
        
        for name, process in self.processes:
            try:
                print(f"   Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"   Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"   Error stopping {name}: {e}")
        
        self.processes.clear()
        print("✅ All services stopped")
    
    def start_all(self, run_tests=True, open_browser=True):
        """Start all components"""
        print("🚀 Starting Complete System...")
        print("=" * 50)
        
        try:
            # Start backend
            backend_process = self.start_backend()
            if not backend_process:
                return False
            
            # Wait for backend
            if not self.wait_for_service(self.backend_url, "Backend", 15):
                return False
            
            # Start VLM
            vlm_process = self.start_vlm()
            if not vlm_process:
                print("⚠️ VLM server failed to start, continuing without it...")
            else:
                # Wait for VLM (longer timeout for model loading)
                self.wait_for_service(self.vlm_url, "VLM", 60)
            
            print("\n✅ System startup complete!")
            
            # Run tests if requested
            if run_tests:
                print("\n" + "=" * 50)
                time.sleep(2)  # Give services a moment to stabilize
                test_success = self.run_tests()
                
                if test_success:
                    print("\n🎉 All tests passed!")
                else:
                    print("\n⚠️ Some tests failed, but system is running")
            
            # Open frontend if requested
            if open_browser:
                print("\n" + "=" * 50)
                time.sleep(1)
                self.open_frontend()
            
            # Keep running
            print("\n" + "=" * 50)
            print("🎯 System is running!")
            print("📡 Backend: http://localhost:8000")
            print("🤖 VLM: http://localhost:8080")
            print("🌐 Frontend: Open src/frontend/index.html")
            print("\n🛑 Press Ctrl+C to stop all services")
            
            # Wait for interrupt
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⚠️ Shutdown requested...")
            
            return True
            
        except Exception as e:
            print(f"❌ System startup failed: {e}")
            return False
        finally:
            self.stop_all()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="System Startup Manager")
    parser.add_argument("--all", action="store_true", help="Start all components")
    parser.add_argument("--backend", action="store_true", help="Start only backend")
    parser.add_argument("--vlm", action="store_true", help="Start only VLM")
    parser.add_argument("--test", action="store_true", help="Run tests only")
    parser.add_argument("--no-tests", action="store_true", help="Skip tests")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    
    args = parser.parse_args()
    
    manager = SystemManager()
    
    try:
        if args.test:
            # Run tests only
            success = manager.run_tests()
            sys.exit(0 if success else 1)
        
        elif args.backend:
            # Start backend only
            print("🚀 Starting Backend Only...")
            process = manager.start_backend()
            if process:
                manager.wait_for_service(manager.backend_url, "Backend")
                print("🛑 Press Ctrl+C to stop")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\\n⚠️ Stopping backend...")
                    manager.stop_all()
        
        elif args.vlm:
            # Start VLM only
            print("🤖 Starting VLM Only...")
            process = manager.start_vlm()
            if process:
                manager.wait_for_service(manager.vlm_url, "VLM", 60)
                print("🛑 Press Ctrl+C to stop")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\\n⚠️ Stopping VLM...")
                    manager.stop_all()
        
        elif args.all or len(sys.argv) == 1:
            # Start everything (default)
            success = manager.start_all(
                run_tests=not args.no_tests,
                open_browser=not args.no_browser
            )
            sys.exit(0 if success else 1)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\\n⚠️ Interrupted by user")
        manager.stop_all()
        sys.exit(1)
    except Exception as e:
        print(f"💥 Error: {e}")
        manager.stop_all()
        sys.exit(1)

if __name__ == "__main__":
    main()