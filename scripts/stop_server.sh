#!/usr/bin/env bash

# Generic Mock Server Stop Script
# This script can stop servers started with different configurations
# 
# Usage:
#   ./stop_server.sh                     # Interactive selection or auto-detect
#   ./stop_server.sh vmanage             # Stop server using vmanage config port
#   ./stop_server.sh basic               # Stop server using basic config port
#   ./stop_server.sh --port 8001         # Stop server on specific port
#   ./stop_server.sh --pid 12345         # Stop specific process ID
#   ./stop_server.sh --help              # Show help

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root to ensure relative paths work correctly
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to show help
show_help() {
    cat << EOF
🛑 Mock Server Stop Script

USAGE:
    $0 [CONFIG_NAME] [OPTIONS]

ARGUMENTS:
    CONFIG_NAME     Configuration set name (optional, auto-detect if not provided)

OPTIONS:
    --port PORT     Stop server on specific port
    --pid PID       Stop specific process ID
    --all           Stop all mock server processes
    --help, -h      Show this help message

EXAMPLES:
    $0                          # Interactive selection or auto-detect
    $0 vmanage                  # Stop server using vmanage config
    $0 --port 8001              # Stop server on port 8001
    $0 --pid 12345              # Stop specific process
    $0 --all                    # Stop all mock servers

NOTES:
    - Script will look for port files: .[CONFIG_NAME]_API_PORT
    - Auto-detection tries common port files and running processes
    - Graceful shutdown is attempted first, then force kill if needed
EOF
}

# Function to find port from config name
get_port_from_config() {
    local config_name="$1"
    # Convert to uppercase for bash 3.x compatibility
    local config_name_upper=$(echo "$config_name" | tr '[:lower:]' '[:upper:]')
    local port_file=".${config_name_upper}_API_PORT"
    
    if [ -f "$port_file" ]; then
        cat "$port_file" | tr -d '[:space:]'
    else
        echo ""
    fi
}

# Function to find running mock server processes
find_mock_servers() {
    # Look for uvicorn processes with our main module
    ps aux | grep -E "(uvicorn.*src\.main:app|python.*uvicorn.*src\.main)" | grep -v grep || true
}

# Function to find process by port (cross-platform)
find_process_by_port() {
    local port="$1"
    
    # Try lsof first (more reliable)
    if command -v lsof >/dev/null 2>&1; then
        # Get the first (parent) process using the port
        lsof -ti:$port 2>/dev/null | head -1 || true
    else
        # Fallback to netstat
        if command -v netstat >/dev/null 2>&1; then
            netstat -tulpn 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1 || true
        fi
    fi
}

# Function to stop process gracefully
stop_process() {
    local pid="$1"
    local config_name="$2"
    
    if [ -z "$pid" ]; then
        echo -e "${YELLOW}⚠️  No process ID provided${NC}"
        return 1
    fi
    
    if ! ps -p "$pid" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Process $pid is not running${NC}"
        return 1
    fi
    
    echo -e "${BLUE}⏹️  Stopping process $pid...${NC}"
    
    # Try graceful shutdown first
    if kill -TERM "$pid" 2>/dev/null; then
        echo -e "${BLUE}📤 Sent SIGTERM signal to process $pid${NC}"
        
        # Wait up to 10 seconds for graceful shutdown
        local count=0
        while [ $count -lt 10 ] && ps -p "$pid" >/dev/null 2>&1; do
            sleep 1
            count=$((count + 1))
            printf "."
        done
        echo ""
        
        # Check if process stopped
        if ! ps -p "$pid" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Process $pid stopped gracefully${NC}"
        else
            echo -e "${YELLOW}⚠️  Process $pid didn't stop gracefully, force killing...${NC}"
            kill -KILL "$pid" 2>/dev/null || true
            sleep 1
            if ! ps -p "$pid" >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Process $pid force killed${NC}"
            else
                echo -e "${RED}❌ Failed to stop process $pid${NC}"
                return 1
            fi
        fi
    else
        echo -e "${RED}❌ Failed to send signal to process $pid${NC}"
        return 1
    fi
    
    # Clean up port file if config name provided
    if [ -n "$config_name" ]; then
        # Convert to uppercase for bash 3.x compatibility
        local config_name_upper=$(echo "$config_name" | tr '[:lower:]' '[:upper:]')
        local port_file=".${config_name_upper}_API_PORT"
        if [ -f "$port_file" ]; then
            rm -f "$port_file"
            echo -e "${BLUE}🗑️  Removed port file: $port_file${NC}"
        fi
    fi
    
    return 0
}

# Function to list available configurations
list_configs() {
    local configs=()
    if [ -d "configs" ]; then
        for config_dir in configs/*; do
            if [ -d "$config_dir" ]; then
                configs+=("$(basename "$config_dir")")
            fi
        done
    fi
    printf '%s\n' "${configs[@]}"
}

# Function to auto-detect running servers
auto_detect_servers() {
    echo -e "${BLUE}🔍 Auto-detecting running mock servers...${NC}"
    
    # Check port files first
    local found_servers=()
    for config in $(list_configs); do
        local port=$(get_port_from_config "$config")
        if [ -n "$port" ]; then
            local pid=$(find_process_by_port "$port")
            if [ -n "$pid" ]; then
                found_servers+=("$config:$port:$pid")
                echo -e "${YELLOW}📍 Found $config server: PID $pid on port $port${NC}"
            fi
        fi
    done
    
    # Also check for any uvicorn processes
    local running_processes=$(find_mock_servers)
    if [ -n "$running_processes" ]; then
        echo -e "${BLUE}🔍 Running mock server processes:${NC}"
        echo "$running_processes" | while read -r line; do
            local pid=$(echo "$line" | awk '{print $2}')
            echo -e "${YELLOW}📍 Process: $pid${NC}"
            found_servers+=("unknown:unknown:$pid")
        done
    fi
    
    if [ ${#found_servers[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No running mock servers found${NC}"
        return 1
    fi
    
    printf '%s\n' "${found_servers[@]}"
}

# Function for interactive server selection
interactive_selection() {
    echo -e "${CYAN}🔧 Interactive Server Selection${NC}"
    echo ""
    
    local servers=($(auto_detect_servers))
    if [ ${#servers[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No running servers found${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Running servers:${NC}"
    for i in "${!servers[@]}"; do
        local server_info="${servers[$i]}"
        local config=$(echo "$server_info" | cut -d':' -f1)
        local port=$(echo "$server_info" | cut -d':' -f2)
        local pid=$(echo "$server_info" | cut -d':' -f3)
        
        printf "${YELLOW}%2d)${NC} Config: %-10s Port: %-5s PID: %s\n" $((i+1)) "$config" "$port" "$pid"
    done
    
    echo ""
    read -p "$(echo -e ${CYAN}"Select server to stop (1-${#servers[@]}): "${NC})" choice
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#servers[@]} ]; then
        local selected="${servers[$((choice-1))]}"
        local config=$(echo "$selected" | cut -d':' -f1)
        local pid=$(echo "$selected" | cut -d':' -f3)
        echo -e "${GREEN}✅ Selected: $config (PID: $pid)${NC}"
        echo "$config:$pid"
    else
        echo -e "${RED}❌ Invalid selection${NC}"
        return 1
    fi
}

# Parse command line arguments
CONFIG_NAME=""
PORT=""
PID=""
STOP_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --pid)
            PID="$2"
            shift 2
            ;;
        --all)
            STOP_ALL=true
            shift
            ;;
        -*)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            if [ -z "$CONFIG_NAME" ]; then
                CONFIG_NAME="$1"
            else
                echo -e "${RED}❌ Multiple arguments specified${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

echo -e "${BLUE}🛑 Mock Server Stop Script${NC}"
echo ""

# Handle --all option
if [ "$STOP_ALL" = true ]; then
    echo -e "${YELLOW}🛑 Stopping all mock server processes...${NC}"
    all_processes=$(find_mock_servers)
    if [ -n "$all_processes" ]; then
        echo "$all_processes" | while read -r line; do
            pid=$(echo "$line" | awk '{print $2}')
            stop_process "$pid" ""
        done
        
        # Clean up all port files
        for port_file in .*.PORT; do
            if [ -f "$port_file" ]; then
                rm -f "$port_file"
                echo -e "${BLUE}🗑️  Removed $port_file${NC}"
            fi
        done 2>/dev/null || true
        
        echo -e "${GREEN}✅ All mock servers stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  No running mock servers found${NC}"
    fi
    exit 0
fi

# Handle specific PID
if [ -n "$PID" ]; then
    stop_process "$PID" ""
    exit $?
fi

# Handle specific port
if [ -n "$PORT" ]; then
    echo -e "${BLUE}🔍 Finding process on port $PORT...${NC}"
    pid=$(find_process_by_port "$PORT")
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}📍 Found process: $pid${NC}"
        stop_process "$pid" ""
    else
        echo -e "${YELLOW}⚠️  No process found on port $PORT${NC}"
        exit 1
    fi
    exit $?
fi

# Handle config name
if [ -n "$CONFIG_NAME" ]; then
    port=$(get_port_from_config "$CONFIG_NAME")
    if [ -n "$port" ]; then
        # Convert to uppercase for bash 3.x compatibility  
        config_name_upper=$(echo "$CONFIG_NAME" | tr '[:lower:]' '[:upper:]')
        echo -e "${BLUE}📁 Port read from .${config_name_upper}_API_PORT file: $port${NC}"
        pid=$(find_process_by_port "$port")
        if [ -n "$pid" ]; then
            echo -e "${YELLOW}📍 Found server process: $pid${NC}"
            stop_process "$pid" "$CONFIG_NAME"
        else
            echo -e "${YELLOW}⚠️  No process found on port $port for config '$CONFIG_NAME'${NC}"
            echo -e "${BLUE}🔍 Checking for any running mock servers...${NC}"
            auto_detect_servers
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  No port file found for config '$CONFIG_NAME'${NC}"
        echo -e "${BLUE}🔍 Available configurations:${NC}"
        list_configs | sed 's/^/   - /'
        exit 1
    fi
    exit $?
fi

# No arguments provided - try auto-detection or interactive selection
detected=$(auto_detect_servers)
if [ $? -eq 0 ]; then
    server_count=$(echo "$detected" | wc -l | tr -d ' ')
    
    if [ "$server_count" -eq 1 ]; then
        # Single server found, stop it automatically
        server_info="$detected"
        config=$(echo "$server_info" | cut -d':' -f1)
        pid=$(echo "$server_info" | cut -d':' -f3)
        echo -e "${GREEN}✅ Auto-detected single server: $config (PID: $pid)${NC}"
        stop_process "$pid" "$config"
    else
        # Multiple servers found, show interactive selection
        selection=$(interactive_selection)
        if [ $? -eq 0 ]; then
            config=$(echo "$selection" | cut -d':' -f1)
            pid=$(echo "$selection" | cut -d':' -f2)
            stop_process "$pid" "$config"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  No running mock servers found${NC}"
    exit 1
fi
