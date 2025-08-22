#!/usr/bin/env bash

# Generic Mock Server Start Script
# This script allows you to start the server with different configuration sets
# 
# Usage:
#   ./start_server.sh                    # Interactive config selection
#   ./start_server.sh vmanage            # Start with vmanage config
#   ./start_server.sh basic              # Start with basic config
#   ./start_server.sh persistence        # Start with persistence config
#   ./start_server.sh custom-folder      # Start with custom config folder
#   ./start_server.sh --help             # Show help

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root to ensure relative paths work correctly
cd "$PROJECT_ROOT"

# Source server state management functions
source "$SCRIPT_DIR/server_state.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8000"
CONFIG_BASE="configs"

# Function to show help
show_help() {
    cat << EOF
🚀 Mock Server Configuration Launcher

USAGE:
    $0 [CONFIG_NAME] [OPTIONS]

ARGUMENTS:
    CONFIG_NAME     Configuration set to use (optional, interactive if not provided)

OPTIONS:
    --port PORT     Server port (default: from config or 8000)
    --host HOST     Server host (default: 0.0.0.0)
    --help, -h      Show this help message

AVAILABLE CONFIGURATIONS:
EOF

    # List available configurations
    if [ -d "$CONFIG_BASE" ]; then
        for config_dir in "$CONFIG_BASE"/*; do
            if [ -d "$config_dir" ]; then
                config_name=$(basename "$config_dir")
                description=""
                
                # Try to get description from README or detect type
                if [ -f "$config_dir/README.md" ]; then
                    description=$(head -n 3 "$config_dir/README.md" | grep -v "^#" | grep -v "^$" | head -n 1 | sed 's/^[*-] *//')
                else
                    # Detect configuration type based on content
                    if [ -f "$config_dir/endpoints.json" ]; then
                        endpoint_count=$(grep -o '"path"' "$config_dir/endpoints.json" | wc -l | tr -d ' ')
                        description="Mock API with $endpoint_count endpoints"
                    fi
                fi
                
                printf "    %-15s %s\n" "$config_name" "$description"
            fi
        done
    else
        echo "    (No configurations found in $CONFIG_BASE/)"
    fi

    cat << EOF

EXAMPLES:
    $0                          # Interactive selection
    $0 vmanage                  # Start with vManage SD-WAN API config
    $0 basic                    # Start with basic REST API config
    $0 persistence              # Start with Redis persistence config
    $0 --port 8001 vmanage      # Start vManage config on port 8001

NOTES:
    - Configuration files are loaded from: $CONFIG_BASE/[CONFIG_NAME]/
    - Required files: api.json, auth.json, endpoints.json
    - Server will run at: http://HOST:PORT
    - Interactive docs available at: http://HOST:PORT/docs
EOF
}

# Function to list available configurations
list_configs() {
    local configs=()
    if [ -d "$CONFIG_BASE" ]; then
        for config_dir in "$CONFIG_BASE"/*; do
            if [ -d "$config_dir" ]; then
                configs+=("$(basename "$config_dir")")
            fi
        done
    fi
    printf '%s\n' "${configs[@]}"
}

# Function to validate configuration
validate_config() {
    local config_path="$1"
    local config_name="$2"
    
    if [ ! -d "$config_path" ]; then
        echo -e "${RED}❌ Error: Configuration '$config_name' not found at '$config_path'${NC}"
        echo -e "${YELLOW}💡 Available configurations:${NC}"
        list_configs | sed 's/^/   - /'
        return 1
    fi

    # Check for required config files
    local required_files=("api.json" "auth.json" "endpoints.json")
    for file in "${required_files[@]}"; do
        if [ ! -f "$config_path/$file" ]; then
            echo -e "${RED}❌ Error: Required file '$file' not found in '$config_path'${NC}"
            echo -e "${YELLOW}💡 Required files: ${required_files[*]}${NC}"
            return 1
        fi
    done
    
    # Validate JSON files
    for file in "${required_files[@]}"; do
        if ! python3 -m json.tool "$config_path/$file" >/dev/null 2>&1; then
            echo -e "${RED}❌ Error: Invalid JSON in '$config_path/$file'${NC}"
            return 1
        fi
    done
    
    return 0
}

# Function for interactive configuration selection
interactive_selection() {
    echo -e "${CYAN}🔧 Interactive Configuration Selection${NC}" >&2
    echo "" >&2
    
    local configs=($(list_configs))
    if [ ${#configs[@]} -eq 0 ]; then
        echo -e "${RED}❌ No configurations found in '$CONFIG_BASE'${NC}" >&2
        exit 1
    fi
    
    echo -e "${BLUE}Available configurations:${NC}" >&2
    for i in "${!configs[@]}"; do
        local config_name="${configs[$i]}"
        local config_path="$CONFIG_BASE/$config_name"
        local description=""
        
        # Get description
        if [ -f "$config_path/README.md" ]; then
            description=$(head -n 5 "$config_path/README.md" | grep -v "^#" | grep -v "^$" | head -n 1 | sed 's/^[*-] *//')
        else
            if [ -f "$config_path/endpoints.json" ]; then
                endpoint_count=$(grep -o '"path"' "$config_path/endpoints.json" 2>/dev/null | wc -l | tr -d ' ')
                description="Mock API with $endpoint_count endpoints"
            fi
        fi
        
        printf "${YELLOW}%2d)${NC} %-15s %s\n" $((i+1)) "$config_name" "$description" >&2
    done
    
    echo "" >&2
    echo -ne "${CYAN}Select configuration (1-${#configs[@]}): ${NC}" >&2
    read choice
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#configs[@]} ]; then
        selected_config="${configs[$((choice-1))]}"
        echo -e "${GREEN}✅ Selected: $selected_config${NC}" >&2
        echo "$selected_config"
    else
        echo -e "${RED}❌ Invalid selection${NC}" >&2
        exit 1
    fi
}

# Parse command line arguments
CONFIG_NAME=""
HOST="$DEFAULT_HOST"
PORT=""

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
        --host)
            HOST="$2"
            shift 2
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
                echo -e "${RED}❌ Multiple configuration names specified${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

# If no config specified, use interactive selection
if [ -z "$CONFIG_NAME" ]; then
    CONFIG_NAME=$(interactive_selection)
fi

# Set configuration path
CONFIG_PATH="$CONFIG_BASE/$CONFIG_NAME"

# Validate configuration
if ! validate_config "$CONFIG_PATH" "$CONFIG_NAME"; then
    exit 1
fi

# Read port from server state or use default
if [ -z "$PORT" ]; then
    # Check if there's an existing server for this config
    existing_port=$(get_port_for_config "$CONFIG_NAME")
    if [ -n "$existing_port" ]; then
        PORT="$existing_port"
        echo -e "${BLUE}📁 Found existing server for $CONFIG_NAME on port: $PORT${NC}"
        echo -e "${YELLOW}⚠️  A server with this configuration is already tracked. Use 'stop' first or specify a different port.${NC}"
        exit 1
    else
        PORT="$DEFAULT_PORT"
        echo -e "${BLUE}📁 Using default port: $PORT${NC}"
    fi
fi

# Validate port
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo -e "${RED}❌ Error: Invalid port number '$PORT'. Must be between 1-65535${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🚀 Starting Mock Server with '$CONFIG_NAME' configuration...${NC}"
echo -e "${BLUE}📂 Config folder: $CONFIG_PATH${NC}"
echo -e "${BLUE}🌐 Host: $HOST${NC}"
echo -e "${BLUE}🔌 Port: $PORT${NC}"
echo ""

echo -e "${GREEN}✅ Configuration files found${NC}"

# Check Python environment
echo -e "${BLUE}🔧 Checking Python environment...${NC}"

# Check if we're in a Poetry environment
if command -v poetry >/dev/null 2>&1; then
    echo -e "${BLUE}📝 Configuring Poetry for local virtual environment...${NC}"
    poetry config virtualenvs.in-project true
    
    echo -e "${BLUE}📦 Installing/updating dependencies with Poetry...${NC}"
    POETRY_VERSION=$(poetry --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
    echo -e "${BLUE}📝 Detected Poetry version: $POETRY_VERSION${NC}"
    
    # Handle Poetry version differences
    if [[ "$POETRY_VERSION" =~ ^[0-1]\. ]] || [[ "$POETRY_VERSION" =~ ^2\.0\. ]]; then
        echo -e "${BLUE}📝 Using Poetry 1.x/2.0.x syntax${NC}"
        poetry install --no-dev 2>/dev/null || poetry install --only=main
    else
        echo -e "${BLUE}📝 Using Poetry 2.1.x+ syntax with package-mode${NC}"
        poetry install --only=main
    fi
    
    echo -e "${GREEN}✅ Poetry environment ready${NC}"
    echo ""
    echo -e "${BLUE}🔄 Starting server using Poetry...${NC}"
    
    # Start the server with Poetry
    CONFIG_FOLDER="$CONFIG_PATH" poetry run python -m uvicorn src.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload &
    
    SERVER_PID=$!
    
else
    echo -e "${BLUE}🔄 Starting server using system Python...${NC}"
    
    # Start the server directly
    CONFIG_FOLDER="$CONFIG_PATH" python -m uvicorn src.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload &
    
    SERVER_PID=$!
fi

# Give the server a moment to start
sleep 3

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null; then
    # Add server to state management
    add_server "$CONFIG_NAME" "$PORT" "$SERVER_PID" "$HOST"
    
    echo -e "${GREEN}✅ Server started successfully!${NC}"
    echo ""
    echo -e "${GREEN}📊 Server Information:${NC}"
    echo -e "${BLUE}   Configuration: $CONFIG_NAME${NC}"
    echo -e "${BLUE}   Process ID: $SERVER_PID${NC}"
    echo -e "${BLUE}   Access the API at: http://$HOST:$PORT${NC}"
    echo -e "${BLUE}   Interactive docs: http://$HOST:$PORT/docs${NC}"
    echo -e "${BLUE}   OpenAPI schema: http://$HOST:$PORT/openapi.json${NC}"
    echo ""
    echo -e "${YELLOW}🛑 To stop the server, run:${NC}"
    echo -e "${CYAN}   kill $SERVER_PID${NC}"
    echo -e "${CYAN}   OR use: ./run.sh stop${NC}"
    echo -e "${CYAN}   OR use: ./run.sh stop --pid $SERVER_PID${NC}"
    echo ""
    echo -e "${BLUE}💡 To check if the server is still running:${NC}"
    echo -e "${CYAN}   ps -p $SERVER_PID${NC}"
    echo ""
else
    echo -e "${RED}❌ Failed to start server${NC}"
    exit 1
fi

# Test server response
echo -e "${BLUE}🔍 Testing server response...${NC}"
if curl -s --connect-timeout 3 "http://$HOST:$PORT/" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is responding to HTTP requests${NC}"
else
    echo -e "${YELLOW}⚠️  Server may still be starting up...${NC}"
fi

echo -e "${GREEN}🎉 Server startup complete!${NC}"
echo -e "${BLUE}🌐 Using config folder: $CONFIG_PATH${NC}"
