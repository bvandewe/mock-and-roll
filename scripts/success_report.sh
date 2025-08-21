#!/usr/bin/env bash

# Successful Requests Report Script for Mock Server
# This script searches logs for successful requests and generates a report
# 
# Usage:
#   ./success_report.sh                          # All successful requests
#   ./success_report.sh /dataservice/device      # Successful requests for specific endpoint
#   ./success_report.sh --status 201,202         # Custom success status codes
#   ./success_report.sh --help                   # Show help

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root to ensure relative paths work correctly
cd "$PROJECT_ROOT"

# Default configuration
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8000"
DEFAULT_LINES="10000"
DEFAULT_API_KEY="system-admin-key-123"
DEFAULT_SUCCESS_CODES="200,201,202,204"

# Read port from .VMANAGE_API_PORT file if it exists
if [ -f ".VMANAGE_API_PORT" ]; then
    PORT=$(cat .VMANAGE_API_PORT | tr -d '[:space:]')
else
    PORT="$DEFAULT_PORT"
fi

# Configuration
HOST="$DEFAULT_HOST"
LINES="$DEFAULT_LINES"
API_KEY="$DEFAULT_API_KEY"
SUCCESS_CODES="$DEFAULT_SUCCESS_CODES"
ENDPOINT_FILTER=""
OUTPUT_FORMAT="summary"  # summary, detailed, json

# Function to show help
show_help() {
    cat << EOF
📊 Mock Server Successful Requests Report

Usage:
    $0 [OPTIONS] [ENDPOINT_PATH]

Options:
    --host HOST         Server host (default: $DEFAULT_HOST)
    --port PORT         Server port (default: from .VMANAGE_API_PORT or $DEFAULT_PORT)
    --lines LINES       Number of log lines to fetch (default: $DEFAULT_LINES)
    --api-key KEY       API key for authentication (default: $DEFAULT_API_KEY)
    --status CODES      Success status codes (default: $DEFAULT_SUCCESS_CODES)
    --format FORMAT     Output format: summary, detailed, json (default: summary)
    --help              Show this help message

Arguments:
    ENDPOINT_PATH       Filter for specific endpoint path (optional)
                       (e.g., /dataservice/device, /j_security_check)

Examples:
    $0                                      # All successful requests (summary)
    $0 /dataservice/device                 # Successful requests for device endpoint
    $0 --status 200,201 /api/users         # Only 200/201 responses for users
    $0 --format detailed                   # Detailed report with request info
    $0 --format json > report.json         # JSON output for processing
    $0 --lines 5000 /logout                # Check last 5000 lines for logout
    
The script analyzes RESPONSE log entries for successful HTTP status codes.
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
        --status)
            SUCCESS_CODES="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
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

# Validate arguments
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "❌ Error: Invalid port number '$PORT'. Must be between 1-65535"
    exit 1
fi

if ! [[ "$LINES" =~ ^[0-9]+$ ]] || [ "$LINES" -lt 1 ]; then
    echo "❌ Error: Invalid lines number '$LINES'. Must be a positive integer"
    exit 1
fi

if [[ ! "$OUTPUT_FORMAT" =~ ^(summary|detailed|json)$ ]]; then
    echo "❌ Error: Invalid format '$OUTPUT_FORMAT'. Must be: summary, detailed, or json"
    exit 1
fi

# Build the API URL
API_URL="http://$HOST:$PORT/system/logging/logs?lines=$LINES"

if [ "$OUTPUT_FORMAT" != "json" ]; then
    echo "📊 Mock Server Success Report"
    echo "🌐 Server: http://$HOST:$PORT"
    echo "📊 Analyzing: $LINES lines"
    echo "✅ Success codes: $SUCCESS_CODES"
    if [ -n "$ENDPOINT_FILTER" ]; then
        echo "🔍 Filtering for endpoint: $ENDPOINT_FILTER"
    fi
    echo ""
fi

# Fetch logs from the server
if [ "$OUTPUT_FORMAT" != "json" ]; then
    echo "📥 Fetching logs..."
fi

if ! LOG_RESPONSE=$(curl -s -X 'GET' \
    "$API_URL" \
    -H 'accept: application/json' \
    -H "X-API-Key: $API_KEY" 2>/dev/null); then
    echo "❌ Failed to fetch logs from server"
    echo "   Make sure the server is running on http://$HOST:$PORT"
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
    exit 1
fi

if [ -z "$LOGS" ]; then
    echo "📭 No logs available"
    exit 0
fi

# Create regex pattern for success codes
SUCCESS_PATTERN=$(echo "$SUCCESS_CODES" | sed 's/,/\\|/g')

# Filter for RESPONSE entries with success codes
if [ -n "$ENDPOINT_FILTER" ]; then
    SUCCESSFUL_RESPONSES=$(echo "$LOGS" | grep -E "RESPONSE: ($SUCCESS_PATTERN) for [A-Z]+ [^[:space:]]*$ENDPOINT_FILTER" || true)
else
    SUCCESSFUL_RESPONSES=$(echo "$LOGS" | grep -E "RESPONSE: ($SUCCESS_PATTERN) for [A-Z]+" || true)
fi

if [ -z "$SUCCESSFUL_RESPONSES" ]; then
    if [ "$OUTPUT_FORMAT" = "json" ]; then
        echo '{"total_successful_requests": 0, "requests": [], "summary": {}}'
    else
        echo "📭 No successful requests found"
        if [ -n "$ENDPOINT_FILTER" ]; then
            echo "   for endpoint: $ENDPOINT_FILTER"
        fi
        echo "   with status codes: $SUCCESS_CODES"
    fi
    exit 0
fi

# Process the successful responses
declare -A endpoint_counts
declare -A method_counts  
declare -A status_counts
declare -a request_details

while IFS= read -r line; do
    if [[ "$line" =~ RESPONSE:\ ([0-9]+)\ for\ ([A-Z]+)\ ([^[:space:]]+) ]]; then
        status_code="${BASH_REMATCH[1]}"
        method="${BASH_REMATCH[2]}"
        endpoint="${BASH_REMATCH[3]}"
        
        # Extract timestamp
        timestamp=$(echo "$line" | grep -o '^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9]' || echo "Unknown")
        
        # Extract request ID
        request_id=$(echo "$line" | grep -o '\[[a-f0-9]*\]' | tr -d '[]' || echo "unknown")
        
        # Extract time taken
        time_taken=$(echo "$line" | grep -o 'Time: [0-9.]*s' | sed 's/Time: //' | sed 's/s//' || echo "0")
        
        # Count statistics
        endpoint_counts["$endpoint"]=$((${endpoint_counts["$endpoint"]} + 1))
        method_counts["$method"]=$((${method_counts["$method"]} + 1))
        status_counts["$status_code"]=$((${status_counts["$status_code"]} + 1))
        
        # Store request details
        request_details+=("$timestamp|$request_id|$method|$endpoint|$status_code|$time_taken")
    fi
done <<< "$SUCCESSFUL_RESPONSES"

# Generate output based on format
case "$OUTPUT_FORMAT" in
    "json")
        echo "{"
        echo "  \"total_successful_requests\": ${#request_details[@]},"
        echo "  \"success_codes_filter\": \"$SUCCESS_CODES\","
        if [ -n "$ENDPOINT_FILTER" ]; then
            echo "  \"endpoint_filter\": \"$ENDPOINT_FILTER\","
        fi
        echo "  \"requests\": ["
        
        for i in "${!request_details[@]}"; do
            IFS='|' read -r timestamp request_id method endpoint status_code time_taken <<< "${request_details[$i]}"
            echo "    {"
            echo "      \"timestamp\": \"$timestamp\","
            echo "      \"request_id\": \"$request_id\","
            echo "      \"method\": \"$method\","
            echo "      \"endpoint\": \"$endpoint\","
            echo "      \"status_code\": $status_code,"
            echo "      \"response_time\": \"${time_taken}s\""
            if [ $i -lt $((${#request_details[@]} - 1)) ]; then
                echo "    },"
            else
                echo "    }"
            fi
        done
        
        echo "  ],"
        echo "  \"summary\": {"
        echo "    \"by_endpoint\": {"
        first=true
        for endpoint in "${!endpoint_counts[@]}"; do
            if [ "$first" = true ]; then
                first=false
            else
                echo ","
            fi
            echo -n "      \"$endpoint\": ${endpoint_counts[$endpoint]}"
        done
        echo ""
        echo "    },"
        echo "    \"by_method\": {"
        first=true
        for method in "${!method_counts[@]}"; do
            if [ "$first" = true ]; then
                first=false
            else
                echo ","
            fi
            echo -n "      \"$method\": ${method_counts[$method]}"
        done
        echo ""
        echo "    },"
        echo "    \"by_status_code\": {"
        first=true
        for status in "${!status_counts[@]}"; do
            if [ "$first" = true ]; then
                first=false
            else
                echo ","
            fi
            echo -n "      \"$status\": ${status_counts[$status]}"
        done
        echo ""
        echo "    }"
        echo "  }"
        echo "}"
        ;;
        
    "detailed")
        echo "📊 Successful Requests Report"
        echo "=" | tr '=' '=' | head -c 60
        echo ""
        echo "✅ Total successful requests: ${#request_details[@]}"
        echo ""
        
        echo "📋 Request Details:"
        echo "-------------------"
        printf "%-20s %-10s %-8s %-30s %-6s %-8s\n" "Timestamp" "Request ID" "Method" "Endpoint" "Status" "Time"
        echo "=" | tr '=' '-' | head -c 80
        echo ""
        
        for detail in "${request_details[@]}"; do
            IFS='|' read -r timestamp request_id method endpoint status_code time_taken <<< "$detail"
            printf "%-20s %-10s %-8s %-30s %-6s %-8s\n" \
                "${timestamp:11:8}" \
                "${request_id:0:8}" \
                "$method" \
                "${endpoint:0:28}" \
                "$status_code" \
                "${time_taken}s"
        done
        
        echo ""
        echo "📈 Summary by Endpoint:"
        echo "-----------------------"
        for endpoint in "${!endpoint_counts[@]}"; do
            printf "  %-40s : %d requests\n" "$endpoint" "${endpoint_counts[$endpoint]}"
        done | sort -k3 -nr
        
        echo ""
        echo "📊 Summary by Method:"
        echo "---------------------"
        for method in "${!method_counts[@]}"; do
            printf "  %-10s : %d requests\n" "$method" "${method_counts[$method]}"
        done | sort -k3 -nr
        
        echo ""
        echo "📊 Summary by Status Code:"
        echo "--------------------------"
        for status in "${!status_counts[@]}"; do
            printf "  %-10s : %d requests\n" "$status" "${status_counts[$status]}"
        done | sort -k1 -n
        ;;
        
    "summary")
        echo "📊 Successful Requests Summary"
        echo "=" | tr '=' '=' | head -c 50
        echo ""
        echo "✅ Total successful requests: ${#request_details[@]}"
        echo ""
        
        echo "🎯 Top Endpoints:"
        for endpoint in "${!endpoint_counts[@]}"; do
            printf "  %-35s : %d\n" "$endpoint" "${endpoint_counts[$endpoint]}"
        done | sort -k3 -nr | head -10
        
        echo ""
        echo "🔧 Methods Used:"
        for method in "${!method_counts[@]}"; do
            printf "  %-8s : %d requests\n" "$method" "${method_counts[$method]}"
        done | sort -k3 -nr
        
        echo ""
        echo "📈 Status Codes:"
        for status in "${!status_counts[@]}"; do
            printf "  %-8s : %d requests\n" "$status" "${status_counts[$status]}"
        done | sort -k1 -n
        
        echo ""
        echo "💡 Use --format detailed for full request details"
        echo "💡 Use --format json for machine-readable output"
        ;;
esac

if [ "$OUTPUT_FORMAT" != "json" ]; then
    echo ""
    echo "✅ Report complete!"
fi
