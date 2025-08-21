#!/usr/bin/env bash

# Script to list running mock API servers
# This script detects running servers and provides management information

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root to ensure relative paths work correctly
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Scanning for running Mock API Servers...${NC}"
echo ""

# Function to check if a port is our mock server
check_mock_server() {
    local port=$1
    local pid=$2
    
    # First check if it's a Python process with our expected command pattern
    local cmd=$(get_process_command $pid)
    if [[ ! "$cmd" == *"python"* ]] || [[ ! "$cmd" == *"run_server.py"* && ! "$cmd" == *"uvicorn"* && ! "$cmd" == *"main:app"* ]]; then
        return 1  # Not a Python process or not our server pattern
    fi
    
    # Try a quick HTTP check (with shorter timeout for Alpine)
    if command -v curl >/dev/null 2>&1; then
        local response=$(timeout 3 curl -s --connect-timeout 1 --max-time 2 http://localhost:$port/ 2>/dev/null || echo "")
        if [[ "$response" == *"Mock server is running"* ]] || [[ "$response" == *"message"* ]] || [[ "$response" == *"detail"* ]]; then
            return 0  # It's our server
        fi
    fi
    
    # Fallback: if it's a Python process with the right pattern, assume it's ours
    if [[ "$cmd" == *"run_server.py"* ]] || [[ "$cmd" == *"main:app"* ]]; then
        return 0
    fi
    
    return 1  # Not our server
}

# Function to get process command line (cross-platform)
get_process_command() {
    local pid=$1
    
    # Try different ps formats for cross-platform compatibility
    if ps -p $pid -o command= >/dev/null 2>&1; then
        # macOS format
        ps -p $pid -o command= 2>/dev/null | head -1
    elif ps -p $pid -o command --no-headers >/dev/null 2>&1; then
        # Linux format
        ps -p $pid -o command --no-headers 2>/dev/null | head -1
    else
        # Fallback
        ps -p $pid 2>/dev/null | tail -1 | awk '{for(i=5;i<=NF;i++) printf "%s ", $i; print ""}'
    fi
}

# Function to get config name from port file
get_config_from_port_file() {
    local port=$1
    for port_file in .*_API_PORT; do
        if [ -f "$port_file" ] && [ "$(cat "$port_file" | tr -d '[:space:]')" = "$port" ]; then
            # Extract config name from port file name
            echo "$port_file" | sed 's/^\.\(.*\)_API_PORT$/\1/' | tr '[:upper:]' '[:lower:]'
            return 0
        fi
    done
    echo "unknown"
}

# Read all configured ports from port files
echo -e "${YELLOW}📁 Checking configured servers:${NC}"
found_configs=false
for port_file in .*_API_PORT; do
    if [ -f "$port_file" ]; then
        port=$(cat "$port_file" | tr -d '[:space:]')
        config_name=$(echo "$port_file" | sed 's/^\.\(.*\)_API_PORT$/\1/' | tr '[:upper:]' '[:lower:]')
        echo -e "   ${CYAN}$config_name${NC}: port $port (from $port_file)"
        found_configs=true
    fi
done

if [ "$found_configs" = false ]; then
    echo "   No active configuration port files found"
fi
echo ""

# Check common ports for mock API servers
PORTS_TO_CHECK=("8000" "8001" "8080" "8081" "3000" "5000")

# Add configured ports to check list
for port_file in .*_API_PORT; do
    if [ -f "$port_file" ]; then
        port=$(cat "$port_file" | tr -d '[:space:]')
        PORTS_TO_CHECK+=("$port")
    fi
done

# Remove duplicates
PORTS_TO_CHECK=($(printf "%s\n" "${PORTS_TO_CHECK[@]}" | sort -u))

FOUND_SERVERS=()

echo -e "${YELLOW}🌐 Checking ports for running mock API servers...${NC}"

# More efficient approach: find Python processes that match our pattern first
PYTHON_PROCESSES=$(ps aux | grep -E "(run_server\.py|uvicorn.*(main:app|src\.main))" | grep -v grep | awk '{print $2}' || echo "")

if [ -n "$PYTHON_PROCESSES" ]; then
    for pid in $PYTHON_PROCESSES; do
        # Get the port from the command line
        cmd=$(get_process_command $pid)
        
        # Debug: show what process we found (only in verbose mode)
        if [ "${DEBUG:-}" = "1" ]; then
            echo "   Debug: Found process $pid: $cmd"
        fi
        
        # Extract port from command line
        port=""
        if [[ "$cmd" == *"--port "* ]]; then
            port=$(echo "$cmd" | sed -n 's/.*--port \([0-9]*\).*/\1/p')
        elif [[ "$cmd" == *"--port="* ]]; then
            port=$(echo "$cmd" | sed -n 's/.*--port=\([0-9]*\).*/\1/p')
        elif [[ "$cmd" == *":8"* ]]; then
            # Look for uvicorn format like "0.0.0.0:8000" or ":8000"
            port=$(echo "$cmd" | sed -n 's/.*:\([0-9][0-9]*\).*/\1/p')
        fi
        
        # Debug: show extracted port
        if [ "${DEBUG:-}" = "1" ]; then
            echo "   Debug: Extracted port: '$port'"
        fi
        
        # If we found a port, check if it's accessible
        if [ -n "$port" ]; then
            # Get config name if available
            config_name=$(get_config_from_port_file $port)
            if [ -z "$config_name" ]; then
                # Try to guess config from command line
                if [[ "$cmd" == *"configs/basic"* ]]; then
                    config_name="basic"
                elif [[ "$cmd" == *"configs/vmanage"* ]] || [[ "$cmd" == *"vmanage-api"* ]]; then
                    config_name="vmanage"
                elif [[ "$cmd" == *"configs/persistence"* ]]; then
                    config_name="persistence"
                else
                    config_name="unknown"
                fi
            fi
            
            FOUND_SERVERS+=("$port:$pid:$config_name")
            echo -e "✅ Found mock API server on port $port (PID: $pid) - Config: ${CYAN}$config_name${NC}"
            
            # Get process details
            echo "   Process: $cmd"
            echo "   URL: http://localhost:$port"
            echo "   Docs: http://localhost:$port/docs"
            echo ""
        else
            echo -e "⚠️  Found Python process (PID: $pid) but couldn't extract port"
            echo "   Command: $cmd"
            echo ""
        fi
    done
else
    echo "   No Python mock API processes found"
fi

# Also check port files for comparison
for port_file in .*_API_PORT; do
    if [ -f "$port_file" ]; then
        port=$(cat "$port_file" | tr -d '[:space:]')
        
        # Check if we already found this port
        found_in_processes=false
        for server in "${FOUND_SERVERS[@]}"; do
            server_port=$(echo $server | cut -d: -f1)
            if [ "$server_port" = "$port" ]; then
                found_in_processes=true
                break
            fi
        done
        
        # If not found in processes but port file exists, it might be stale
        if [ "$found_in_processes" = false ]; then
            echo -e "⚠️  Port file $port_file exists (port $port) but no running process found"
            echo "   This may be a stale port file from a previous session"
            echo ""
        fi
    fi
done

# Summary
echo -e "${GREEN}📊 Summary:${NC}"
if [ ${#FOUND_SERVERS[@]} -eq 0 ]; then
    echo "   No Mock API Servers found running"
    echo ""
    echo -e "${YELLOW}💡 To start a server:${NC}"
    echo "   ./scripts/start_server.sh                 # Interactive selection"
    echo "   ./scripts/start_server.sh basic           # Start basic config"
    echo "   ./scripts/start_server.sh vmanage         # Start vmanage config"
else
    echo "   Found ${#FOUND_SERVERS[@]} Mock API Server(s) running:"
    for server in "${FOUND_SERVERS[@]}"; do
        port=$(echo $server | cut -d: -f1)
        pid=$(echo $server | cut -d: -f2)
        config=$(echo $server | cut -d: -f3)
        echo -e "   - Port $port (PID: $pid) - Config: ${CYAN}$config${NC}"
    done
    echo ""
    echo -e "${YELLOW}🛑 To stop servers:${NC}"
    echo "   ./scripts/stop_server.sh                  # Auto-detect or interactive"
    echo "   ./scripts/stop_server.sh --all            # Stop all servers"
    for server in "${FOUND_SERVERS[@]}"; do
        pid=$(echo $server | cut -d: -f2)
        config=$(echo $server | cut -d: -f3)
        echo "   ./scripts/stop_server.sh --pid $pid      # Stop server with PID $pid"
    done
fi

echo ""
echo -e "${YELLOW}🔧 Management commands:${NC}"
echo "   ./run.sh start                                 # Start new server (interactive)"
echo "   ./run.sh stop                                  # Stop servers"
echo "   ./run.sh list                                  # Show this list"
echo "   ./run.sh help                                  # Show all available commands"
