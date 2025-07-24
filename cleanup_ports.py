#!/usr/bin/env python3
"""
Port Cleanup Utility for AI Manual Assistant

This script helps clean up all ports used by the system:
- Port 5500: Frontend server
- Port 8000: Backend server  
- Port 8080: Model server
- Any other related processes
"""

import os
import sys
import signal
import subprocess
import time
import socket
from pathlib import Path

# System ports used by AI Manual Assistant
SYSTEM_PORTS = [5500, 8000, 8080]
COMMON_PORTS = [3000, 3001, 5000, 5001, 7000, 7001, 8001, 8081, 9000, 9001]

def check_port_availability(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0
    except Exception as e:
        print(f"⚠️ Port check error for {port}: {e}")
        return False

def find_processes_on_port(port):
    """Find all processes using the specified port"""
    try:
        # Use lsof to find processes
        result = subprocess.run(
            ['lsof', '-i', f':{port}', '-t'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            return [int(pid) for pid in pids if pid.isdigit()]
        return []
        
    except subprocess.TimeoutExpired:
        print(f"⚠️ lsof command timed out for port {port}")
        return []
    except FileNotFoundError:
        print("⚠️ lsof command not found - trying alternative method...")
        return find_processes_alternative(port)
    except Exception as e:
        print(f"⚠️ Error finding process on port {port}: {e}")
        return []

def find_processes_alternative(port):
    """Alternative method to find processes using netstat"""
    try:
        result = subprocess.run(
            ['netstat', '-tulnp'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        pids = []
        for line in result.stdout.split('\n'):
            if f':{port}' in line:
                parts = line.split()
                if len(parts) > 6:
                    pid_info = parts[6]
                    if '/' in pid_info:
                        pid = pid_info.split('/')[0]
                        if pid.isdigit():
                            pids.append(int(pid))
        
        return pids
        
    except Exception as e:
        print(f"⚠️ Alternative process finding failed for port {port}: {e}")
        return []

def get_process_info(pid):
    """Get process information"""
    try:
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'pid,ppid,cmd'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                return lines[1].strip()
        return f"PID {pid} (unknown command)"
        
    except Exception as e:
        return f"PID {pid} (info unavailable: {e})"

def kill_process(pid, force=False):
    """Kill a process by PID"""
    try:
        if not force:
            # Try graceful termination first
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            
            # Check if process still exists
            try:
                os.kill(pid, 0)  # This doesn't kill, just checks if process exists
                print(f"⚠️ Process {pid} still running, using force kill...")
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                print(f"✅ Process {pid} terminated gracefully")
                return True
        else:
            os.kill(pid, signal.SIGKILL)
            print(f"💀 Force killed process {pid}")
        
        time.sleep(1)
        return True
        
    except ProcessLookupError:
        print(f"✅ Process {pid} already terminated")
        return True
    except PermissionError:
        print(f"❌ Permission denied to kill process {pid}")
        return False
    except Exception as e:
        print(f"❌ Error killing process {pid}: {e}")
        return False

def cleanup_port(port, force=False):
    """Clean up a specific port"""
    print(f"\n🔍 Checking port {port}...")
    
    if check_port_availability(port):
        print(f"✅ Port {port} is already available")
        return True
    
    print(f"🔄 Port {port} is in use, finding processes...")
    pids = find_processes_on_port(port)
    
    if not pids:
        print(f"⚠️ No processes found on port {port}, but port appears busy")
        return False
    
    print(f"🎯 Found {len(pids)} process(es) on port {port}:")
    
    for pid in pids:
        process_info = get_process_info(pid)
        print(f"   • {process_info}")
    
    # Ask for confirmation unless force mode
    if not force:
        response = input(f"\n❓ Kill {len(pids)} process(es) on port {port}? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print(f"⏭️ Skipping port {port}")
            return False
    
    # Kill processes
    success = True
    for pid in pids:
        if not kill_process(pid, force):
            success = False
    
    # Verify port is now available
    time.sleep(1)
    if check_port_availability(port):
        print(f"✅ Port {port} is now available")
        return True
    else:
        print(f"❌ Port {port} is still busy after cleanup")
        return False

def find_python_processes():
    """Find Python processes that might be related to the system"""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        python_processes = []
        for line in result.stdout.split('\n'):
            if 'python' in line.lower() and any(keyword in line for keyword in [
                'main.py', 'run_', 'server', 'flask', 'fastapi', 'uvicorn', 'http.server'
            ]):
                parts = line.split()
                if len(parts) > 1 and parts[1].isdigit():
                    pid = int(parts[1])
                    python_processes.append((pid, line))
        
        return python_processes
        
    except Exception as e:
        print(f"⚠️ Error finding Python processes: {e}")
        return []

def cleanup_related_processes(force=False):
    """Clean up Python processes that might be related to the system"""
    print(f"\n🔍 Looking for related Python processes...")
    
    processes = find_python_processes()
    
    if not processes:
        print("✅ No related Python processes found")
        return True
    
    print(f"🎯 Found {len(processes)} potentially related process(es):")
    for pid, info in processes:
        # Show a shortened version of the command
        cmd_part = ' '.join(info.split()[10:15])  # Show some of the command
        print(f"   • PID {pid}: {cmd_part}...")
    
    if not force:
        response = input(f"\n❓ Kill {len(processes)} related process(es)? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("⏭️ Skipping related processes")
            return False
    
    success = True
    for pid, info in processes:
        if not kill_process(pid, force):
            success = False
    
    return success

def main():
    """Main cleanup function"""
    print("🧹 AI Manual Assistant - Port Cleanup Utility")
    print("=" * 55)
    print("This will clean up ports used by the system:")
    print("   • Port 5500: Frontend server")
    print("   • Port 8000: Backend server")
    print("   • Port 8080: Model server")
    print("=" * 55)
    
    # Parse command line arguments
    force_mode = '--force' in sys.argv or '-f' in sys.argv
    all_ports = '--all' in sys.argv or '-a' in sys.argv
    help_requested = '--help' in sys.argv or '-h' in sys.argv
    
    if help_requested:
        print("\nUsage:")
        print("  python cleanup_ports.py [options]")
        print("\nOptions:")
        print("  --force, -f    Force kill without confirmation")
        print("  --all, -a      Also check common development ports")
        print("  --help, -h     Show this help message")
        print("\nExamples:")
        print("  python cleanup_ports.py          # Interactive cleanup")
        print("  python cleanup_ports.py --force  # Force cleanup without prompts")
        print("  python cleanup_ports.py --all    # Include additional ports")
        return
    
    if force_mode:
        print("⚠️ FORCE MODE: Will kill processes without confirmation")
    
    # Determine which ports to clean
    ports_to_clean = SYSTEM_PORTS.copy()
    if all_ports:
        ports_to_clean.extend(COMMON_PORTS)
        print(f"🔍 Checking {len(ports_to_clean)} ports...")
    
    print()
    
    # Clean up system ports
    success_count = 0
    for port in ports_to_clean:
        if cleanup_port(port, force_mode):
            success_count += 1
    
    # Clean up related processes
    cleanup_related_processes(force_mode)
    
    # Final summary
    print(f"\n📊 Summary:")
    print(f"   • {success_count}/{len(ports_to_clean)} ports cleaned successfully")
    
    # Verify all main system ports are now available
    print(f"\n🔍 Final verification:")
    all_clear = True
    for port in SYSTEM_PORTS:
        if check_port_availability(port):
            print(f"   ✅ Port {port}: Available")
        else:
            print(f"   ❌ Port {port}: Still busy")
            all_clear = False
    
    if all_clear:
        print(f"\n🎉 All system ports are now available!")
        print(f"You can now start the AI Manual Assistant normally.")
    else:
        print(f"\n⚠️ Some ports are still busy. You may need to:")
        print(f"   • Restart your computer")
        print(f"   • Use Activity Monitor to find remaining processes")
        print(f"   • Run with --force flag")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n🛑 Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
