#!/usr/bin/env python3
"""
AI Manual Assistant - Project Startup Script

This script helps you start the complete project with proper sequence.

Usage:
python start_project.py                    # Start with default model (smolvlm)
python start_project.py --model moondream2_optimized  # Start with specific model
python start_project.py --help            # Show help
"""

import argparse
import subprocess
import sys
import time
import os
from pathlib import Path

class ProjectStarter:
    """Project startup manager"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = []
    
    def print_banner(self):
        """Print startup banner"""
        print("🚀 AI Manual Assistant - Project Startup")
        print("=" * 60)
        print("This script will start the complete project in the correct order:")
        print("1. 🤖 Model Server (Port 8080)")
        print("2. 🔧 Backend Server (Port 8000)")  
        print("3. 🌐 Frontend Server (Port 5500)")
        print("=" * 60)
    
    def start_model(self, model_name: str = "smolvlm"):
        """Start model server"""
        print(f"🤖 Step 1: Starting Model Server ({model_name})...")
        print("⏳ This may take a few minutes to load the model...")
        
        cmd = [
            sys.executable, 
            "src/models/model_launcher_en.py", 
            "--model", model_name
        ]
        
        print(f"💻 Command: {' '.join(cmd)}")
        print("📋 Instructions:")
        print("   - Wait for 'Model server launched successfully!' message")
        print("   - Keep this terminal open")
        print("   - Open a new terminal for the next step")
        print()
        
        try:
            process = subprocess.Popen(cmd, cwd=self.project_root)
            self.processes.append(("Model Server", process))
            
            # Wait a bit to see if it starts successfully
            time.sleep(3)
            if process.poll() is not None:
                print("❌ Model server failed to start")
                return False
            
            print("✅ Model server starting... (check the output above)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start model server: {e}")
            return False
    
    def start_backend(self):
        """Start backend server"""
        print("🔧 Step 2: Starting Backend Server...")
        print("📋 Instructions:")
        print("   - Open a NEW terminal")
        print("   - Run the following command:")
        print(f"   cd {self.project_root}")
        print("   python src/backend/main.py")
        print()
        print("⏳ Waiting for you to start the backend...")
        input("Press Enter after you've started the backend server...")
    
    def start_frontend(self):
        """Start frontend server"""
        print("🌐 Step 3: Starting Frontend Server...")
        print("📋 Instructions:")
        print("   - Open another NEW terminal")
        print("   - Run the following commands:")
        print(f"   cd {self.project_root}")
        print("   cd src/frontend && python -m http.server 5500")
        print()
        print("⏳ Waiting for you to start the frontend...")
        input("Press Enter after you've started the frontend server...")
    
    def show_final_info(self):
        """Show final information"""
        print("🎉 Project Startup Complete!")
        print("=" * 60)
        print("📊 Service URLs:")
        print("   🤖 Model Server:   http://localhost:8080")
        print("   🔧 Backend Server: http://localhost:8000") 
        print("   🌐 Frontend App:   http://localhost:5500")
        print()
        print("🔍 Health Checks:")
        print("   curl http://localhost:8080/health  # Model health")
        print("   curl http://localhost:8000/health  # Backend health")
        print()
        print("📋 Usage:")
        print("   1. Open http://localhost:5500 in your browser")
        print("   2. Allow camera access when prompted")
        print("   3. Start using the AI Manual Assistant!")
        print()
        print("🛑 To stop all servers:")
        print("   - Press Ctrl+C in each terminal")
        print("=" * 60)
    
    def start_project(self, model_name: str = "smolvlm"):
        """Start the complete project"""
        self.print_banner()
        
        # Step 1: Start model
        if not self.start_model(model_name):
            print("❌ Failed to start model server")
            return False
        
        # Step 2: Start backend
        self.start_backend()
        
        # Step 3: Start frontend
        self.start_frontend()
        
        # Show final info
        self.show_final_info()
        
        return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="AI Manual Assistant - Project Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Models:
  smolvlm                      - Default model (recommended)
  moondream2_optimized         - Fastest model
  smolvlm2_500m_video_optimized - Best performance
  phi3_vision_optimized        - Detailed analysis

Examples:
  python start_project.py                           # Use default model
  python start_project.py --model moondream2_optimized  # Use specific model
        """
    )
    
    parser.add_argument('--model', '-m', default='smolvlm', 
                       help='Model to use (default: smolvlm)')
    
    args = parser.parse_args()
    
    starter = ProjectStarter()
    success = starter.start_project(args.model)
    
    if success:
        print("✅ Project startup completed successfully!")
    else:
        print("❌ Project startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()