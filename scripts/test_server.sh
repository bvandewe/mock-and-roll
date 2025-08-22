#!/usr/bin/env bash

# API Test Script Wrapper
# Tests the system logging endpoint using the system API key

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Default values
DEFAULT_HOST="localhost"
DEFAULT_CONFIG="configs/basic"

show_help() {
    cat << EOF
🧪 Mock Server API Test

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --port PORT     Server port (required)
    --host HOST     Server host (default: localhost)
    --config CONFIG Configuration directory (default: configs/basic)
    --api-key KEY   System API key (auto-detected from config if not provided)
    --help          Show this help

DESCRIPTION:
    Tests the GET /system/logging/logs endpoint using system API key authentication.
    The system API key is automatically extracted from the auth.json file in the
    specified configuration directory.

EXAMPLES:
    $0 --port 8000                           # Test basic config on port 8000
    $0 --port 8080 --config configs/vmanage  # Test vmanage config on port 8080
    $0 --port 8000 --api-key custom-key-123  # Use specific API key

ENDPOINTS TESTED:
    GET /system/logging/logs   - Get recent log entries (requires system auth)

EOF
}

# Parse arguments
HOST="$DEFAULT_HOST"
PORT=""
CONFIG="$DEFAULT_CONFIG"
API_KEY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --config)
            CONFIG="$2"
            shift 2
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$PORT" ]; then
    echo -e "${RED}❌ Error: --port is required${NC}"
    echo ""
    show_help
    exit 1
fi

# Validate port
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo -e "${RED}❌ Error: Invalid port number '$PORT'. Must be between 1-65535${NC}"
    exit 1
fi

# Validate config directory
if [ ! -d "$CONFIG" ]; then
    echo -e "${RED}❌ Error: Configuration directory '$CONFIG' not found${NC}"
    exit 1
fi

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: python3 is required but not found${NC}"
    exit 1
fi

# Check if requests module is available
if ! python3 -c "import requests" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Warning: 'requests' module not found. Installing...${NC}"
    
    # Try to install requests
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install requests
    elif command -v pip >/dev/null 2>&1; then
        pip install requests
    else
        echo -e "${RED}❌ Error: pip not found. Please install the 'requests' module manually:${NC}"
        echo "    pip3 install requests"
        exit 1
    fi
    
    # Verify installation
    if ! python3 -c "import requests" >/dev/null 2>&1; then
        echo -e "${RED}❌ Error: Failed to install 'requests' module${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 'requests' module installed successfully${NC}"
fi

echo -e "${BLUE}🧪 Mock Server API Test${NC}"
echo -e "${BLUE}======================${NC}"
echo -e "${CYAN}📍 Host: $HOST${NC}"
echo -e "${CYAN}🔌 Port: $PORT${NC}"
echo -e "${CYAN}📁 Config: $CONFIG${NC}"
echo ""

# Build Python command arguments
PYTHON_ARGS=(
    "--host" "$HOST"
    "--port" "$PORT"
    "--config" "$CONFIG"
)

if [ -n "$API_KEY" ]; then
    PYTHON_ARGS+=("--api-key" "$API_KEY")
fi

# Run the Python test script
python3 "$SCRIPT_DIR/test_api.py" "${PYTHON_ARGS[@]}"
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}🎉 API test completed successfully!${NC}"
else
    echo -e "${RED}💥 API test failed!${NC}"
fi

exit $exit_code
