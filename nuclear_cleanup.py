#!/usr/bin/env python3
"""
Nuclear cleanup option - kills ALL Python processes
⚠️ WARNING: This will kill ALL Python processes on your system!
Only use if you're sure no other important Python processes are running.
"""

import subprocess
import sys

def nuclear_cleanup():
    """Kill ALL Python processes - use with extreme caution!"""
    print("☢️ NUCLEAR CLEANUP MODE")
    print("⚠️ WARNING: This will kill ALL Python processes on your system!")
    print("This includes:")
    print("   • All Python scripts")
    print("   • All Python servers") 
    print("   • Any other Python applications")
    
    response = input("\n❓ Are you absolutely sure? Type 'YES' to continue: ")
    if response != 'YES':
        print("🛑 Nuclear cleanup cancelled")
        return
    
    print("💀 Killing all Python processes...")
    
    try:
        # Kill all Python processes
        subprocess.run(['pkill', '-f', 'python'], check=False)
        subprocess.run(['pkill', '-f', 'Python'], check=False)
        
        print("☢️ Nuclear cleanup complete!")
        print("All Python processes have been terminated.")
        
    except Exception as e:
        print(f"❌ Nuclear cleanup failed: {e}")

if __name__ == "__main__":
    nuclear_cleanup()
