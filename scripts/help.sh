#!/usr/bin/env bash

# Mock Server Scripts Help
# This script lists all available scripts and their purposes

set -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPTS_DIR")"

echo "🛠️  Mock Server - Available Scripts"
echo "=" | tr '=' '=' | head -c 60
echo ""
echo "📁 Location: $SCRIPTS_DIR"
echo ""

# Function to get script description from comments
get_script_description() {
    local script_file="$1"
    local description=""
    
    # Look for description in comments (lines starting with # that contain description text)
    description=$(grep -E "^#.*([Ss]cript|[Dd]escription|[Pp]urpose)" "$script_file" 2>/dev/null | head -1 | sed 's/^#[[:space:]]*//' || echo "")
    
    # If no description found, try to extract from the filename or first meaningful comment
    if [ -z "$description" ]; then
        description=$(grep -E "^#[[:space:]]*[A-Z]" "$script_file" 2>/dev/null | head -1 | sed 's/^#[[:space:]]*//' || echo "")
    fi
    
    # If still no description, provide a generic one based on filename
    if [ -z "$description" ]; then
        case "$script_file" in
            *start*) description="Start the mock server" ;;
            *stop*) description="Stop the mock server" ;;
            *test*) description="Test script" ;;
            *setup*) description="Setup script" ;;
            *get_logs*) description="Fetch and filter server logs" ;;
            *kill*) description="Kill server processes" ;;
            *list*) description="List server information" ;;
            *alpine*) description="Alpine Linux setup" ;;
            *) description="Utility script" ;;
        esac
    fi
    
    echo "$description"
}

# Main scripts (server operations)
echo "🚀 Server Operations:"
echo "--------------------"

if [ -f "$SCRIPTS_DIR/start_vmanage_api.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/start_vmanage_api.sh")
    echo "  ./scripts/start_vmanage_api.sh    - $desc"
fi

if [ -f "$SCRIPTS_DIR/stop_vmanage_api.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/stop_vmanage_api.sh")
    echo "  ./scripts/stop_vmanage_api.sh     - $desc"
fi

if [ -f "$SCRIPTS_DIR/kill_all_servers.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/kill_all_servers.sh")
    echo "  ./scripts/kill_all_servers.sh     - $desc"
fi

if [ -f "$SCRIPTS_DIR/list_servers.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/list_servers.sh")
    echo "  ./scripts/list_servers.sh         - $desc"
fi

echo ""

# Monitoring and debugging
echo "📊 Monitoring & Debugging:"
echo "---------------------------"

if [ -f "$SCRIPTS_DIR/get_logs.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/get_logs.sh")
    echo "  ./scripts/get_logs.sh             - $desc"
    echo "    Examples:"
    echo "      ./scripts/get_logs.sh                     # All recent logs"
    echo "      ./scripts/get_logs.sh /dataservice/device # Filter by endpoint"
    echo "      ./scripts/get_logs.sh --lines 500 /logout # Custom line count"
fi

if [ -f "$SCRIPTS_DIR/test_vmanage_api.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/test_vmanage_api.sh")
    echo "  ./scripts/test_vmanage_api.sh     - $desc"
fi

echo ""

# Setup and environment
echo "⚙️  Setup & Environment:"
echo "------------------------"

if [ -f "$SCRIPTS_DIR/setup_environment.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/setup_environment.sh")
    echo "  ./scripts/setup_environment.sh    - $desc"
fi

if [ -f "$SCRIPTS_DIR/setup_alpine.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/setup_alpine.sh")
    echo "  ./scripts/setup_alpine.sh         - $desc"
fi

echo ""

# All other scripts
echo "🔧 Other Utilities:"
echo "-------------------"

for script in "$SCRIPTS_DIR"/*.sh; do
    if [ -f "$script" ]; then
        script_name=$(basename "$script")
        
        # Skip scripts already listed above
        case "$script_name" in
            "help.sh"|"start_vmanage_api.sh"|"stop_vmanage_api.sh"|"kill_all_servers.sh"|"list_servers.sh"|"get_logs.sh"|"test_vmanage_api.sh"|"setup_environment.sh"|"setup_alpine.sh")
                continue
                ;;
        esac
        
        desc=$(get_script_description "$script")
        printf "  ./scripts/%-25s - %s\n" "$script_name" "$desc"
    fi
done

echo ""
echo "💡 Quick Start:"
echo "---------------"
echo "  1. Start server:    ./scripts/start_vmanage_api.sh"
echo "  2. Check logs:      ./scripts/get_logs.sh"
echo "  3. Stop server:     ./scripts/stop_vmanage_api.sh"
echo ""
echo "📖 For detailed help on any script, run:"
echo "  ./scripts/SCRIPT_NAME --help"
echo ""
echo "🌐 Server will be available at: http://0.0.0.0:8000"
echo "📚 API Documentation: http://0.0.0.0:8000/docs"
