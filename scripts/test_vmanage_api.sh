#!/bin/bash

# test_vmanage_api.sh - Quick test script for vManage API Mock Server
# Usage: ./test_vmanage_api.sh [port]

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
NC='\033[0m' # No Color

# Default port
DEFAULT_PORT=8000

# Get port from argument or .VMANAGE_API_PORT file or use default
if [ $# -eq 1 ]; then
    PORT=$1
elif [ -f ".VMANAGE_API_PORT" ]; then
    PORT=$(cat .VMANAGE_API_PORT)
    echo -e "${BLUE}📁 Using port from .VMANAGE_API_PORT file: ${PORT}${NC}"
else
    PORT=$DEFAULT_PORT
    echo -e "${YELLOW}⚠️  No port specified, using default: ${PORT}${NC}"
fi

BASE_URL="http://localhost:${PORT}"

echo -e "${BLUE}🧪 Testing vManage API Mock Server on port ${PORT}...${NC}\n"

# Test 1: Basic server health check
echo -e "${BLUE}1️⃣  Testing server health...${NC}"
if response=$(curl -s --max-time 5 "${BASE_URL}/"); then
    if echo "$response" | grep -q "Mock server is running"; then
        echo -e "   ${GREEN}✅ Server is running${NC}"
        echo -e "   ${GREEN}📝 Response: ${response}${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Server responded but with unexpected content${NC}"
        echo -e "   ${YELLOW}📝 Response: ${response}${NC}"
    fi
else
    echo -e "   ${RED}❌ Server is not responding${NC}"
    echo -e "   ${RED}💡 Try starting the server with: ./start_vmanage_api.sh${NC}"
    exit 1
fi

# Test 2: OpenAPI documentation
echo -e "\n${BLUE}2️⃣  Testing OpenAPI documentation...${NC}"
if curl -s --max-time 5 "${BASE_URL}/docs" > /dev/null; then
    echo -e "   ${GREEN}✅ Swagger UI is accessible${NC}"
    echo -e "   ${GREEN}🌐 URL: ${BASE_URL}/docs${NC}"
else
    echo -e "   ${RED}❌ Swagger UI is not accessible${NC}"
fi

# Test 3: OpenAPI JSON schema
echo -e "\n${BLUE}3️⃣  Testing OpenAPI schema...${NC}"
if openapi_response=$(curl -s --max-time 5 "${BASE_URL}/openapi.json"); then
    if echo "$openapi_response" | grep -q "openapi"; then
        echo -e "   ${GREEN}✅ OpenAPI schema is available${NC}"
        # Extract API title and version with Alpine-compatible commands
        title=$(echo "$openapi_response" | awk -F'"title":"' '{if (NF>1) print $2}' | awk -F'"' '{print $1}' | head -1)
        version=$(echo "$openapi_response" | awk -F'"version":"' '{if (NF>1) print $2}' | awk -F'"' '{print $1}' | head -1)
        
        # Fallback to "Unknown" if extraction failed
        [ -z "$title" ] && title="Unknown"
        [ -z "$version" ] && version="Unknown"
        
        echo -e "   ${GREEN}📋 API Title: ${title}${NC}"
        echo -e "   ${GREEN}🏷️  Version: ${version}${NC}"
    else
        echo -e "   ${YELLOW}⚠️  OpenAPI schema has unexpected format${NC}"
    fi
else
    echo -e "   ${RED}❌ OpenAPI schema is not accessible${NC}"
fi

# Function to get system API key from auth.json
get_system_api_key() {
    local config_folder="tests/configs/vmanage-api"
    if [ -d "$config_folder" ]; then
        local auth_file="$config_folder/auth.json"
    else
        local auth_file="config/auth.json"
    fi
    
    if [ -f "$auth_file" ]; then
        # Extract the first valid system API key from auth.json
        # More compatible approach for Alpine/BusyBox
        local api_key=$(awk '
        /system_api_key/ { in_system=1 }
        in_system && /valid_keys/ { in_keys=1; next }
        in_system && in_keys && /"[^"]*"/ { 
            gsub(/[",[:space:]]/, "")
            if ($0 != "" && $0 != "[" && $0 != "]") {
                print $0
                exit
            }
        }
        in_system && /}/ { in_system=0; in_keys=0 }
        ' "$auth_file")
        echo "$api_key"
    else
        echo ""
    fi
}

# Test 4: System endpoints (cache management)
echo -e "\n${BLUE}4️⃣  Testing system cache endpoint...${NC}"
SYSTEM_API_KEY=$(get_system_api_key)

if [ -n "$SYSTEM_API_KEY" ]; then
    echo -e "   ${BLUE}🔑 Using system API key: ${SYSTEM_API_KEY:0:10}...${NC}"
    if cache_response=$(curl -s --max-time 5 -H "X-API-Key: $SYSTEM_API_KEY" "${BASE_URL}/system/cache/status"); then
        if echo "$cache_response" | grep -q '"status"'; then
            echo -e "   ${GREEN}✅ System cache endpoint is accessible with authentication${NC}"
            echo -e "   ${GREEN}🔧 URL: ${BASE_URL}/system/cache/status${NC}"
            echo -e "   ${GREEN}📝 Response: ${cache_response}${NC}"
        else
            echo -e "   ${YELLOW}⚠️  System cache endpoint responded with unexpected content${NC}"
            echo -e "   ${YELLOW}📝 Response: ${cache_response}${NC}"
        fi
    else
        echo -e "   ${RED}❌ System cache endpoint failed even with authentication${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  No system API key found in auth.json${NC}"
    echo -e "   ${YELLOW}💡 Check authentication setup in config/auth.json${NC}"
fi

# Test 5: System logs endpoint
echo -e "\n${BLUE}5️⃣  Testing system logs endpoint...${NC}"
if [ -n "$SYSTEM_API_KEY" ]; then
    if logs_response=$(curl -s --max-time 5 -H "X-API-Key: $SYSTEM_API_KEY" "${BASE_URL}/system/logging/logs?lines=5"); then
        if echo "$logs_response" | grep -q '"status"'; then
            echo -e "   ${GREEN}✅ System logs endpoint is accessible with authentication${NC}"
            echo -e "   ${GREEN}🔧 URL: ${BASE_URL}/system/logging/logs${NC}"
            
            # Extract log count and sample from response with Alpine-compatible commands
            log_count=$(echo "$logs_response" | awk -F'"returned_lines":' '{if (NF>1) print $2}' | awk -F',' '{print $1}' | head -1)
            [ -z "$log_count" ] && log_count="0"
            echo -e "   ${GREEN}📊 Retrieved log entries: ${log_count}${NC}"
            
            # Show first log entry if available
            if [ "$log_count" -gt 0 ] 2>/dev/null; then
                # Extract first log entry in a more portable way
                first_log=$(echo "$logs_response" | awk -F'"logs":\\[' '{if (NF>1) print $2}' | awk -F'"' '{print $2}' | head -1)
                if [ -n "$first_log" ] && [ ${#first_log} -gt 0 ]; then
                    # Truncate long log lines for display
                    if [ ${#first_log} -gt 80 ]; then
                        echo -e "   ${GREEN}📝 Sample log: ${first_log:0:80}...${NC}"
                    else
                        echo -e "   ${GREEN}📝 Sample log: ${first_log}${NC}"
                    fi
                fi
            else
                echo -e "   ${BLUE}ℹ️  No log entries found (log file may be empty)${NC}"
            fi
        else
            echo -e "   ${YELLOW}⚠️  System logs endpoint responded with unexpected content${NC}"
            echo -e "   ${YELLOW}📝 Response: ${logs_response}${NC}"
        fi
    else
        echo -e "   ${RED}❌ System logs endpoint failed even with authentication${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  No system API key found - skipping logs test${NC}"
fi

# # Test 5: Check for common API endpoints
# echo -e "\n${BLUE}5️⃣  Checking API endpoint availability...${NC}"
# endpoints=("/api/v1/devices" "/api/v1/templates" "/api/v1/policies")
# available_endpoints=0

# for endpoint in "${endpoints[@]}"; do
#     if curl -s --max-time 3 "${BASE_URL}${endpoint}" > /dev/null 2>&1; then
#         echo -e "   ${GREEN}✅ ${endpoint}${NC}"
#         ((available_endpoints++))
#     else
#         echo -e "   ${YELLOW}⚠️  ${endpoint} (may require auth)${NC}"
#     fi
# done

# Summary
echo -e "\n${BLUE}📊 Test Summary:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🌐 Server URL: ${BASE_URL}${NC}"
echo -e "${GREEN}📚 Documentation: ${BASE_URL}/docs${NC}"
echo -e "${GREEN}🔧 System cache: ${BASE_URL}/system/cache/status${NC}"
echo -e "${GREEN}� System logs: ${BASE_URL}/system/logging/logs${NC}"
if [ -n "$SYSTEM_API_KEY" ]; then
    echo -e "${GREEN}🔑 System API key: Available (${SYSTEM_API_KEY:0:10}...)${NC}"
else
    echo -e "${YELLOW}⚠️  System API key: Not found in auth.json${NC}"
fi

# Check if server process is running
echo -e "\n${BLUE}🔍 Process Information:${NC}"
if pids=$(lsof -ti :${PORT} 2>/dev/null); then
    echo -e "${GREEN}📍 Server PIDs: ${pids}${NC}"
    for pid in $pids; do
        if ps_info=$(ps -p $pid -o pid,command --no-headers 2>/dev/null); then
            echo -e "   ${GREEN}🔧 Process: ${ps_info}${NC}"
        fi
    done
else
    echo -e "${YELLOW}⚠️  No process found listening on port ${PORT}${NC}"
fi

echo -e "\n${GREEN}🎉 Test completed!${NC}"

# Exit with appropriate code - server is working if we got this far
echo -e "${GREEN}✨ Server appears to be working correctly${NC}"
exit 0
