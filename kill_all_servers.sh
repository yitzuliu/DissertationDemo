#!/bin/bash
# Quick script to kill all AI Manual Assistant servers

echo "🧹 Killing all AI Manual Assistant servers..."

# Kill processes on specific ports
for port in 5500 8000 8080; do
    echo "🔍 Checking port $port..."
    pids=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "💀 Killing processes on port $port: $pids"
        echo $pids | xargs kill -9 2>/dev/null
    else
        echo "✅ Port $port is already free"
    fi
done

# Kill common Python server processes
echo "🔍 Looking for Python server processes..."
pkill -f "python.*main.py" 2>/dev/null
pkill -f "python.*run_.*py" 2>/dev/null  
pkill -f "python.*http.server" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
pkill -f "flask" 2>/dev/null

echo "✅ Cleanup complete!"
