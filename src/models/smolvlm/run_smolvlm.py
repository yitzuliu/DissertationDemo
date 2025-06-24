#!/usr/bin/env python3
"""
SmolVLM Server Launcher
Launch SmolVLM model server (powered by llama-server)
"""

import subprocess
import sys
import time
import signal
import os

class SmolVLMServer:
    def __init__(self):
        self.process = None
        self.model_name = "ggml-org/SmolVLM-500M-Instruct-GGUF"
        self.port = 8080
        
    def start_server(self):
        """Start SmolVLM server"""
        cmd = [
            "llama-server",
            "-hf", self.model_name,
            "-ngl", "99",
            "--port", str(self.port)
        ]
        
        print("🚀 Starting SmolVLM server...")
        print(f"📦 Model: {self.model_name}")
        print(f"🌐 Port: {self.port}")
        print(f"💻 Command: {' '.join(cmd)}")
        print("-" * 50)
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor output
            if self.process.stdout:
                for line in iter(self.process.stdout.readline, ''):
                    print(line.rstrip())
                    
                    # Check if server started successfully
                    if "HTTP server listening" in line or "Server listening" in line:
                        print(f"\n✅ SmolVLM server running at http://localhost:{self.port}")
                        print("📡 API endpoint: /v1/chat/completions")
                        print("🛑 Press Ctrl+C to stop server")
                    
        except FileNotFoundError:
            print("❌ Error: 'llama-server' command not found")
            print("Please ensure llama.cpp is properly installed and added to PATH")
            return False
        except KeyboardInterrupt:
            print("\n🛑 Received stop signal...")
            self.stop_server()
            return True
        except Exception as e:
            print(f"❌ Startup failed: {e}")
            return False
            
    def stop_server(self):
        """Stop server"""
        if self.process:
            print("🔄 Stopping SmolVLM server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print("✅ SmolVLM server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force stopping server...")
                self.process.kill()
                self.process.wait()
                print("✅ SmolVLM server force stopped")

def signal_handler(signum, frame):
    """Handle system signals"""
    print("\n🛑 Received stop signal, shutting down server...")
    sys.exit(0)

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🎯 SmolVLM Server Launcher")
    print("=" * 50)
    
    server = SmolVLMServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        server.stop_server()
    finally:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 