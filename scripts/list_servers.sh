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
for port in "${PORTS_TO_CHECK[@]}"; do
    # Get PIDs using this port
    PIDS=$(lsof -ti:$port 2>/dev/null || echo "")
    
    if [ -n "$PIDS" ]; then
        for pid in $PIDS; do
            # Check if it's our mock server
            if check_mock_server $port $pid; then
                config_name=$(get_config_from_port_file $port)
                FOUND_SERVERS+=("$port:$pid:$config_name")
                echo -e "✅ Found mock API server on port $port (PID: $pid) - Config: ${CYAN}$config_name${NC}"
                
                # Get process details
                PROCESS_INFO=$(get_process_info $pid)
                echo "   Process: $PROCESS_INFO"
                echo "   URL: http://localhost:$port"
                echo "   Docs: http://localhost:$port/docs"
                echo ""
            else
                echo -e "ℹ️  Port $port is in use by PID $pid (not our mock API server)"
            fi
        done
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
echo "   ./scripts/start_server.sh                     # Start new server"
echo "   ./scripts/help.sh                             # Show all available scripts"
echo "   ./scripts/config_help.sh                      # Configuration guide"
echo "   ./stop_vmanage_api.sh     # Stop server"
echo "   ./list_servers.sh         # Show this list"
echo "   ./setup_environment.sh    # Setup Poetry environment"
