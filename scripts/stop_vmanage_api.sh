#!/usr/bin/env bash

# Script to stop vManage API mock server
# Usage: ./stop_vmanage_api.sh [PID]

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root to ensure relative paths work correctly
cd "$PROJECT_ROOT"

# Read port from .VMANAGE_API_PORT file if it exists, otherwise use default
if [ -f ".VMANAGE_API_PORT" ]; then
    PORT=$(cat .VMANAGE_API_PORT | tr -d '[:space:]')
    echo "📁 Port read from .VMANAGE_API_PORT file: $PORT"
else
    PORT="8001"
    echo "📁 Using default port (no .VMANAGE_API_PORT file found): $PORT"
fi

# Validate port is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "❌ Error: Invalid port number '$PORT'. Must be between 1-65535"
    exit 1
fi

echo "🛑 Stopping vManage API Mock Server..."

if [ $# -eq 1 ]; then
    # PID provided as argument
    PID=$1
    echo "📍 Using provided PID: $PID"
else
    # Find process by port using Alpine/BusyBox compatible method
    echo "🔍 Finding server process on port $PORT..."
    
    # Try multiple methods to find the process using the port
    PID=""
    
    # Method 1: Use netstat if available
    if command -v netstat >/dev/null 2>&1; then
        PID=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1 | head -1)
    fi
    
    # Method 2: Use ss if available (more modern)
    if [ -z "$PID" ] && command -v ss >/dev/null 2>&1; then
        PID=$(ss -tlnp | grep ":$PORT " | sed 's/.*pid=\([0-9]*\).*/\1/' | head -1)
    fi
    
    # Method 3: Use ps and grep for Python processes
    if [ -z "$PID" ]; then
        PID=$(ps aux | grep "python.*run_server.py.*--port $PORT" | grep -v grep | awk '{print $2}' | head -1)
    fi
    
    # Method 4: Look for any Python process with the port in command line
    if [ -z "$PID" ]; then
        PID=$(ps aux | grep "python.*$PORT" | grep -v grep | awk '{print $2}' | head -1)
    fi
    
    if [ -z "$PID" ]; then
        echo "❌ No server found running on port $PORT"
        exit 1
    fi
    
    echo "📍 Found server process: $PID"
fi

# Check if process exists
if ! ps -p $PID > /dev/null 2>&1; then
    echo "❌ Process $PID is not running"
    exit 1
fi

# Kill the process
echo "⏹️  Stopping process $PID..."
kill $PID

# Wait a moment and check if it stopped
sleep 2

if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Process still running, forcing termination..."
    kill -9 $PID
    sleep 1
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ Failed to stop process $PID"
        exit 1
    fi
fi

echo "✅ Server stopped successfully!"
echo "   Process $PID has been terminated"
