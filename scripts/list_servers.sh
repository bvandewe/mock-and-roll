#!/usr/bin/env bash

# Script to list running vManage API mock servers
# This script detects running servers and provides management information

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root to ensure relative paths work correctly
cd "$PROJECT_ROOT"

echo "🔍 Scanning for running vManage API Mock Servers..."
echo ""

# Function to check if a port is the vManage API server
check_vmanage_server() {
    local port=$1
    local pid=$2
    
    # Try to get a response from the server
    local response=$(curl -s --connect-timeout 2 http://localhost:$port/ 2>/dev/null || echo "")
    
    # Check if it's our mock server based on the response
    if [[ "$response" == *"Mock server is running"* ]]; then
        return 0  # It's our server
    else
        return 1  # Not our server
    fi
}

# Function to get process command line
get_process_info() {
    local pid=$1
    ps -p $pid -o pid,ppid,command --no-headers 2>/dev/null || echo "Process not found"
}

# Read configured port from file if it exists
DEFAULT_PORT="8001"
if [ -f ".VMANAGE_API_PORT" ]; then
    CONFIGURED_PORT=$(cat .VMANAGE_API_PORT | tr -d '[:space:]')
    echo "📁 Configured port from .VMANAGE_API_PORT: $CONFIGURED_PORT"
else
    CONFIGURED_PORT="$DEFAULT_PORT"
    echo "📁 Using default port: $DEFAULT_PORT"
fi
echo ""

# Check common ports for vManage API servers
PORTS_TO_CHECK=("$CONFIGURED_PORT" "8000" "8001" "8080" "8081" "3000" "5000")
FOUND_SERVERS=()

echo "🌐 Checking common ports for vManage API servers..."
for port in "${PORTS_TO_CHECK[@]}"; do
    # Get PIDs using this port
    PIDS=$(lsof -ti:$port 2>/dev/null || echo "")
    
    if [ -n "$PIDS" ]; then
        for pid in $PIDS; do
            # Check if it's our vManage server
            if check_vmanage_server $port $pid; then
                FOUND_SERVERS+=("$port:$pid")
                echo "✅ Found vManage API server on port $port (PID: $pid)"
                
                # Get process details
                PROCESS_INFO=$(get_process_info $pid)
                echo "   Process: $PROCESS_INFO"
                echo "   URL: http://localhost:$port"
                echo "   Docs: http://localhost:$port/docs"
                echo ""
            else
                echo "ℹ️  Port $port is in use by PID $pid (not vManage API server)"
            fi
        done
    fi
done

# Summary
echo "📊 Summary:"
if [ ${#FOUND_SERVERS[@]} -eq 0 ]; then
    echo "   No vManage API Mock Servers found running"
    echo ""
    echo "💡 To start a server:"
    echo "   ./start_vmanage_api.sh"
else
    echo "   Found ${#FOUND_SERVERS[@]} vManage API Mock Server(s) running:"
    for server in "${FOUND_SERVERS[@]}"; do
        port=$(echo $server | cut -d: -f1)
        pid=$(echo $server | cut -d: -f2)
        echo "   - Port $port (PID: $pid)"
    done
    echo ""
    echo "🛑 To stop servers:"
    echo "   ./stop_vmanage_api.sh                    # Stop server on configured port"
    for server in "${FOUND_SERVERS[@]}"; do
        pid=$(echo $server | cut -d: -f2)
        echo "   ./stop_vmanage_api.sh $pid            # Stop server with PID $pid"
    done
fi

echo ""
echo "🔧 Management commands:"
echo "   ./start_vmanage_api.sh    # Start new server"
echo "   ./stop_vmanage_api.sh     # Stop server"
echo "   ./list_servers.sh         # Show this list"
echo "   ./setup_environment.sh    # Setup Poetry environment"
