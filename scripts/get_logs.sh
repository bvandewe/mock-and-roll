#!/usr/bin/env bash

# Log Fetcher and Filter Script for Mock Server
# This script pulls logs from the server and optionally filters by endpoint path
# 
# Usage:
#   ./get_logs.sh                           # Get all logs (last 10000 lines)
#   ./get_logs.sh /dataservice/device       # Filter logs for specific endpoint
#   ./get_logs.sh --lines 500 /api/users    # Get 500 lines and filter
#   ./get_logs.sh --help                    # Show help

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root to ensure relative paths work correctly
cd "$PROJECT_ROOT"

# Source server state management functions
source "$SCRIPT_DIR/server_state.sh"

# Default configuration
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8000"
DEFAULT_LINES="10000"
DEFAULT_API_KEY="system-admin-key-123"

# Try to find a running server to get port from
cleanup_dead_processes
all_servers=$(get_all_servers)
first_server_port=$(echo "$all_servers" | python3 -c "
import json
import sys
try:
    servers = json.load(sys.stdin)
    if servers:
        print(servers[0].get('port', ''))
except:
    pass
")

if [ -n "$first_server_port" ]; then
    PORT="$first_server_port"
else
    PORT="$DEFAULT_PORT"
fi

# Configuration
HOST="$DEFAULT_HOST"
LINES="$DEFAULT_LINES"
API_KEY="$DEFAULT_API_KEY"
ENDPOINT_FILTER=""

# Function to show help
show_help() {
    cat << EOF
📋 Mock Server Log Fetcher and Filter

Usage:
    $0 [OPTIONS] [ENDPOINT_PATH]

Options:
    --host HOST         Server host (default: $DEFAULT_HOST)
    --port PORT         Server port (default: auto-detect from running servers or $DEFAULT_PORT)
    --lines LINES       Number of log lines to fetch (default: $DEFAULT_LINES)
    --api-key KEY       API key for authentication (default: $DEFAULT_API_KEY)
    --help              Show this help message

Arguments:
    ENDPOINT_PATH       Filter logs for requests to this endpoint path
                       (e.g., /dataservice/device, /j_security_check)

Examples:
    $0                                    # Get all recent logs
    $0 /dataservice/device               # Filter for device endpoint logs
    $0 --lines 500 /j_security_check     # Get 500 lines, filter for login
    $0 --port 8001 /logout               # Use different port and filter
    
The script will show both REQUEST and RESPONSE log entries for the filtered endpoint.
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --lines)
            LINES="$2"
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
        -*)
            echo "❌ Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            if [ -z "$ENDPOINT_FILTER" ]; then
                ENDPOINT_FILTER="$1"
            else
                echo "❌ Multiple endpoint paths specified. Use only one."
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate numeric arguments
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "❌ Error: Invalid port number '$PORT'. Must be between 1-65535"
    exit 1
fi

if ! [[ "$LINES" =~ ^[0-9]+$ ]] || [ "$LINES" -lt 1 ]; then
    echo "❌ Error: Invalid lines number '$LINES'. Must be a positive integer"
    exit 1
fi

# Build the API URL
API_URL="http://$HOST:$PORT/system/logging/logs?lines=$LINES"

echo "📋 Mock Server Log Fetcher"
echo "🌐 Server: http://$HOST:$PORT"
echo "📊 Fetching: $LINES lines"
if [ -n "$ENDPOINT_FILTER" ]; then
    echo "🔍 Filtering for endpoint: $ENDPOINT_FILTER"
fi
echo ""

# Fetch logs from the server
echo "📥 Fetching logs..."
if ! LOG_RESPONSE=$(curl -s -X 'GET' \
    "$API_URL" \
    -H 'accept: application/json' \
    -H "X-API-Key: $API_KEY" 2>/dev/null); then
    echo "❌ Failed to fetch logs from server"
    echo "   Make sure the server is running on http://$HOST:$PORT"
    echo "   and the API key is correct"
    exit 1
fi

# Check if response is valid JSON
if ! echo "$LOG_RESPONSE" | jq . >/dev/null 2>&1; then
    echo "❌ Invalid JSON response from server:"
    echo "$LOG_RESPONSE"
    exit 1
fi

# Extract logs from JSON response
if ! LOGS=$(echo "$LOG_RESPONSE" | jq -r '.data.logs[]?' 2>/dev/null); then
    echo "❌ No logs found in server response"
    echo "Response was: $LOG_RESPONSE"
    exit 1
fi

if [ -z "$LOGS" ]; then
    echo "📭 No logs available"
    exit 0
fi

# Filter logs if endpoint path is specified
if [ -n "$ENDPOINT_FILTER" ]; then
    echo "🔍 Filtering logs for endpoint: $ENDPOINT_FILTER"
    echo "=" | tr '=' '-' | head -c 80
    echo ""
    
    # Filter for both REQUEST and RESPONSE entries containing the endpoint
    FILTERED_LOGS=$(echo "$LOGS" | grep -E "(REQUEST|RESPONSE).*$ENDPOINT_FILTER" || true)
    
    if [ -z "$FILTERED_LOGS" ]; then
        echo "📭 No log entries found for endpoint: $ENDPOINT_FILTER"
        echo ""
        echo "💡 Available endpoints in recent logs:"
        echo "$LOGS" | grep -o 'REQUEST: [A-Z]* [^[:space:]]*' | sed 's/REQUEST: [A-Z]* //' | sort -u | head -10
        exit 0
    fi
    
    # Count matches
    MATCH_COUNT=$(echo "$FILTERED_LOGS" | wc -l | tr -d '[:space:]')
    echo "✅ Found $MATCH_COUNT log entries for endpoint: $ENDPOINT_FILTER"
    echo ""
    
    # Display filtered logs with some context
    echo "$LOGS" | grep -E -A2 -B1 "(REQUEST|RESPONSE).*$ENDPOINT_FILTER" | \
        sed 's/^--$/\n---\n/' | \
        grep -v '^--$'
        
else
    echo "📄 All recent logs:"
    echo "=" | tr '=' '-' | head -c 80
    echo ""
    echo "$LOGS"
fi

echo ""
echo "✅ Log fetch complete!"

# Show summary
TOTAL_LINES=$(echo "$LOGS" | wc -l | tr -d '[:space:]')
echo "📊 Summary:"
echo "   Total log lines: $TOTAL_LINES"
if [ -n "$ENDPOINT_FILTER" ]; then
    FILTERED_LINES=$(echo "$FILTERED_LOGS" | wc -l | tr -d '[:space:]' 2>/dev/null || echo "0")
    echo "   Filtered lines: $FILTERED_LINES"
fi
echo "   Server: http://$HOST:$PORT"
