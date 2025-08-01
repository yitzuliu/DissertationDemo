#!/usr/bin/env python3
"""
SmolVLM Server Launcher (Refactored)

Launch SmolVLM model server using the unified server manager.
This version uses the shared server management interface for better consistency.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from server_manager import SmolVLMServerManager

def main():
    """Main function for launching SmolVLM server."""
    print("🎯 SmolVLM Server Launcher (Refactored)")
    print("=" * 50)
    
    # Create server manager with default settings
    server_manager = SmolVLMServerManager()
    
    try:
        # Start server with verbose output
        if server_manager.start(verbose=True):
            print("\n✅ Server started successfully!")
            print("📡 Server is ready for requests")
            print("🛑 Press Ctrl+C to stop server")
            
            # Keep the server running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Received stop signal...")
        else:
            print("❌ Failed to start server")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Received stop signal...")
    finally:
        server_manager.stop()
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 