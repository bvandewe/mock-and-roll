#!/usr/bin/env bash

# Script to stop vManage API mock server
# Usage: ./stop_vmanage_api.sh [PID]

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
    # Find process by port
    echo "🔍 Finding server process on port $PORT..."
    PID=$(lsof -ti:$PORT)
    
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
